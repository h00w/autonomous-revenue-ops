from enum import Enum
from typing import Any, Optional


class IntegrationErrorKind(str, Enum):
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    RATE_LIMIT = "rate_limit"
    NOT_FOUND = "not_found"
    VALIDATION = "validation"
    CONFLICT = "conflict"
    TIMEOUT = "timeout"
    NETWORK = "network"
    PROVIDER = "provider"
    UNKNOWN = "unknown"


class IntegrationError(RuntimeError):
    """Provider-neutral error raised by bounded integration adapters."""

    def __init__(
        self,
        *,
        provider: str,
        kind: IntegrationErrorKind,
        message: str,
        retryable: bool,
        status_code: Optional[int] = None,
        retry_after_seconds: Optional[float] = None,
        details: Any = None,
    ) -> None:
        super().__init__(message)
        self.provider = provider
        self.kind = kind
        self.retryable = retryable
        self.status_code = status_code
        self.retry_after_seconds = retry_after_seconds
        self.details = details

    def as_dict(self) -> dict[str, Any]:
        return {
            "provider": self.provider,
            "kind": self.kind.value,
            "message": str(self),
            "retryable": self.retryable,
            "status_code": self.status_code,
            "retry_after_seconds": self.retry_after_seconds,
            "details": self.details,
        }
