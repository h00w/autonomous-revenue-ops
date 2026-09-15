from typing import TypeVar, Type

from pydantic import BaseModel, ValidationError

from .base import StructuredLLMProvider
from .errors import AIProviderError, AIProviderErrorKind
from .models import ProviderAttempt, StructuredGenerationRequest, StructuredGenerationResult

T = TypeVar("T", bound=BaseModel)

_DEFAULT_FALLBACK_KINDS = {
    AIProviderErrorKind.RATE_LIMIT,
    AIProviderErrorKind.TIMEOUT,
    AIProviderErrorKind.NETWORK,
    AIProviderErrorKind.PROVIDER,
    AIProviderErrorKind.INVALID_RESPONSE,
    AIProviderErrorKind.SCHEMA_VALIDATION,
}


class ModelRouter:
    """Ordered model router with bounded, explicit fallback semantics."""

    def __init__(
        self,
        providers: list[StructuredLLMProvider],
        *,
        fallback_kinds: set[AIProviderErrorKind] | None = None,
    ) -> None:
        if not providers:
            raise ValueError("At least one AI provider is required")
        self.providers = providers
        self.fallback_kinds = fallback_kinds or set(_DEFAULT_FALLBACK_KINDS)

    def generate_typed(
        self,
        request: StructuredGenerationRequest,
        output_type: Type[T],
    ) -> tuple[T, StructuredGenerationResult]:
        attempts: list[ProviderAttempt] = []
        last_error: AIProviderError | None = None

        for index, provider in enumerate(self.providers):
            try:
                result = provider.generate_structured(request)
                try:
                    typed = output_type.model_validate(result.data)
                except ValidationError as exc:
                    raise AIProviderError(
                        provider=provider.provider,
                        kind=AIProviderErrorKind.SCHEMA_VALIDATION,
                        message=f"{provider.provider} output failed local schema validation",
                        retryable=False,
                        details=exc.errors(include_url=False),
                    ) from exc
                attempts.append(ProviderAttempt(provider=provider.provider, model=provider.model, success=True))
                result.routing_attempts = attempts
                return typed, result
            except AIProviderError as exc:
                last_error = exc
                attempts.append(
                    ProviderAttempt(
                        provider=provider.provider,
                        model=provider.model,
                        success=False,
                        error_kind=exc.kind.value,
                        retryable=exc.retryable,
                    )
                )
                can_fallback = exc.kind in self.fallback_kinds and index < len(self.providers) - 1
                if not can_fallback:
                    exc.details = {"cause": exc.details, "routing_attempts": [a.model_dump() for a in attempts]}
                    raise

        assert last_error is not None
        raise last_error

    def close(self) -> None:
        for provider in self.providers:
            provider.close()
