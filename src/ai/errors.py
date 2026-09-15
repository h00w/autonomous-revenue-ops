from enum import Enum
from typing import Any, Optional


class AIProviderErrorKind(str, Enum):
    AUTHENTICATION = "authentication"
    RATE_LIMIT = "rate_limit"
    TIMEOUT = "timeout"
    NETWORK = "network"
    PROVIDER = "provider"
    REFUSAL = "refusal"
    INVALID_RESPONSE = "invalid_response"
    SCHEMA_VALIDATION = "schema_validation"


class AIProviderError(RuntimeError):
    def __init__(
        self,
        *,
        provider: str,
        kind: AIProviderErrorKind,
        message: str,
        retryable: bool,
        status_code: Optional[int] = None,
        details: Any = None,
    ) -> None:
        super().__init__(message)
        self.provider = provider
        self.kind = kind
        self.retryable = retryable
        self.status_code = status_code
        self.details = details

    def as_dict(self) -> dict[str, Any]:
        return {
            "provider": self.provider,
            "kind": self.kind.value,
            "message": str(self),
            "retryable": self.retryable,
            "status_code": self.status_code,
            "details": self.details,
        }
