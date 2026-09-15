import json
import time
from typing import Any

import httpx

from ...integrations.errors import IntegrationError, IntegrationErrorKind
from ...integrations.http import BoundedHttpClient
from ..errors import AIProviderError, AIProviderErrorKind


def ai_http_client(
    provider: str,
    *,
    client: httpx.Client | None = None,
    timeout_seconds: float = 30.0,
) -> BoundedHttpClient:
    return BoundedHttpClient(
        provider,
        client=client,
        timeout_seconds=timeout_seconds,
    )


def call_json(
    http: BoundedHttpClient,
    method: str,
    url: str,
    **kwargs: Any,
) -> tuple[dict[str, Any], float]:
    started = time.perf_counter()
    try:
        payload = http.request_json(method, url, **kwargs)
    except IntegrationError as exc:
        mapping = {
            IntegrationErrorKind.AUTHENTICATION: AIProviderErrorKind.AUTHENTICATION,
            IntegrationErrorKind.AUTHORIZATION: AIProviderErrorKind.AUTHENTICATION,
            IntegrationErrorKind.RATE_LIMIT: AIProviderErrorKind.RATE_LIMIT,
            IntegrationErrorKind.TIMEOUT: AIProviderErrorKind.TIMEOUT,
            IntegrationErrorKind.NETWORK: AIProviderErrorKind.NETWORK,
            IntegrationErrorKind.PROVIDER: AIProviderErrorKind.PROVIDER,
        }
        raise AIProviderError(
            provider=exc.provider,
            kind=mapping.get(exc.kind, AIProviderErrorKind.PROVIDER),
            message=str(exc),
            retryable=exc.retryable,
            status_code=exc.status_code,
            details=exc.details,
        ) from exc
    return payload, (time.perf_counter() - started) * 1000


def parse_json_text(provider: str, text: str) -> dict[str, Any]:
    try:
        data = json.loads(text)
    except (TypeError, json.JSONDecodeError) as exc:
        raise AIProviderError(
            provider=provider,
            kind=AIProviderErrorKind.INVALID_RESPONSE,
            message=f"{provider} returned invalid structured JSON",
            retryable=False,
            details=text[:1000] if isinstance(text, str) else text,
        ) from exc
    if not isinstance(data, dict):
        raise AIProviderError(
            provider=provider,
            kind=AIProviderErrorKind.INVALID_RESPONSE,
            message=f"{provider} structured output was not an object",
            retryable=False,
            details=data,
        )
    return data
