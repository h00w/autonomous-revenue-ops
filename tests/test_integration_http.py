import httpx
import pytest

from src.integrations.errors import IntegrationError, IntegrationErrorKind
from src.integrations.http import BoundedHttpClient


def client_for(status: int, *, headers=None, payload=None):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            status,
            headers=headers or {},
            json=payload if payload is not None else {"message": "provider error"},
            request=request,
        )

    return httpx.Client(transport=httpx.MockTransport(handler))


@pytest.mark.parametrize(
    ("status", "kind", "retryable"),
    [
        (400, IntegrationErrorKind.VALIDATION, False),
        (401, IntegrationErrorKind.AUTHENTICATION, False),
        (403, IntegrationErrorKind.AUTHORIZATION, False),
        (404, IntegrationErrorKind.NOT_FOUND, False),
        (409, IntegrationErrorKind.CONFLICT, False),
        (429, IntegrationErrorKind.RATE_LIMIT, True),
        (500, IntegrationErrorKind.PROVIDER, True),
        (503, IntegrationErrorKind.PROVIDER, True),
    ],
)
def test_http_statuses_are_normalized(status, kind, retryable):
    bounded = BoundedHttpClient("test-provider", client=client_for(status))
    with pytest.raises(IntegrationError) as caught:
        bounded.request("GET", "https://provider.example/resource")
    assert caught.value.kind == kind
    assert caught.value.retryable is retryable
    assert caught.value.status_code == status


def test_retry_after_is_preserved_for_rate_limit():
    bounded = BoundedHttpClient(
        "test-provider",
        client=client_for(429, headers={"Retry-After": "12"}),
    )
    with pytest.raises(IntegrationError) as caught:
        bounded.request("GET", "https://provider.example/resource")
    assert caught.value.retry_after_seconds == 12.0


def test_timeout_is_normalized():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("synthetic timeout", request=request)

    client = httpx.Client(transport=httpx.MockTransport(handler))
    bounded = BoundedHttpClient("test-provider", client=client)
    with pytest.raises(IntegrationError) as caught:
        bounded.request("GET", "https://provider.example/resource")
    assert caught.value.kind == IntegrationErrorKind.TIMEOUT
    assert caught.value.retryable is True
