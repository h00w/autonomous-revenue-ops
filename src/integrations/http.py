from __future__ import annotations

from typing import Any, Mapping, Optional

import httpx

from .errors import IntegrationError, IntegrationErrorKind


class BoundedHttpClient:
    """Thin HTTP boundary that normalizes provider failures.

    Retry policy is intentionally not implemented here in Phase 2. The caller
    receives retryability metadata; Phase 5 will add bounded retry/backoff and
    circuit-breaking without changing adapter contracts.
    """

    def __init__(
        self,
        provider: str,
        *,
        client: httpx.Client | None = None,
        timeout_seconds: float = 10.0,
    ) -> None:
        self.provider = provider
        self._owns_client = client is None
        self.client = client or httpx.Client(timeout=timeout_seconds)

    def close(self) -> None:
        if self._owns_client:
            self.client.close()

    def request(
        self,
        method: str,
        url: str,
        *,
        headers: Mapping[str, str] | None = None,
        params: Mapping[str, Any] | None = None,
        json: Any = None,
        expected_statuses: set[int] | None = None,
    ) -> httpx.Response:
        try:
            response = self.client.request(
                method,
                url,
                headers=headers,
                params=params,
                json=json,
            )
        except httpx.TimeoutException as exc:
            raise IntegrationError(
                provider=self.provider,
                kind=IntegrationErrorKind.TIMEOUT,
                message=f"{self.provider} request timed out",
                retryable=True,
                details=str(exc),
            ) from exc
        except httpx.NetworkError as exc:
            raise IntegrationError(
                provider=self.provider,
                kind=IntegrationErrorKind.NETWORK,
                message=f"{self.provider} network failure",
                retryable=True,
                details=str(exc),
            ) from exc
        except httpx.HTTPError as exc:
            raise IntegrationError(
                provider=self.provider,
                kind=IntegrationErrorKind.UNKNOWN,
                message=f"{self.provider} HTTP client failure",
                retryable=False,
                details=str(exc),
            ) from exc

        if expected_statuses is not None and response.status_code in expected_statuses:
            return response
        if expected_statuses is None and response.is_success:
            return response
        if expected_statuses is not None and response.is_success:
            return response

        raise self._from_response(response)

    def request_json(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        response = self.request(*args, **kwargs)
        if not response.content:
            return {}
        try:
            payload = response.json()
        except ValueError as exc:
            raise IntegrationError(
                provider=self.provider,
                kind=IntegrationErrorKind.PROVIDER,
                message=f"{self.provider} returned non-JSON content",
                retryable=False,
                status_code=response.status_code,
                details=response.text[:1000],
            ) from exc
        if isinstance(payload, dict):
            return payload
        return {"data": payload}

    def _from_response(self, response: httpx.Response) -> IntegrationError:
        status = response.status_code
        kind = IntegrationErrorKind.UNKNOWN
        retryable = False
        if status == 400 or status == 422:
            kind = IntegrationErrorKind.VALIDATION
        elif status == 401:
            kind = IntegrationErrorKind.AUTHENTICATION
        elif status == 403:
            kind = IntegrationErrorKind.AUTHORIZATION
        elif status == 404:
            kind = IntegrationErrorKind.NOT_FOUND
        elif status == 409:
            kind = IntegrationErrorKind.CONFLICT
        elif status == 429:
            kind = IntegrationErrorKind.RATE_LIMIT
            retryable = True
        elif status >= 500:
            kind = IntegrationErrorKind.PROVIDER
            retryable = True

        retry_after: Optional[float] = None
        raw_retry_after = response.headers.get("Retry-After")
        if raw_retry_after:
            try:
                retry_after = float(raw_retry_after)
            except ValueError:
                retry_after = None

        details: Any
        try:
            details = response.json()
        except ValueError:
            details = response.text[:1000]

        return IntegrationError(
            provider=self.provider,
            kind=kind,
            message=f"{self.provider} request failed with HTTP {status}",
            retryable=retryable,
            status_code=status,
            retry_after_seconds=retry_after,
            details=details,
        )
