from typing import Type, TypeVar

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
_OUTPUT_FAILURE_KINDS = {
    AIProviderErrorKind.INVALID_RESPONSE,
    AIProviderErrorKind.SCHEMA_VALIDATION,
}


class ModelRouter:
    """Ordered model router with bounded, explicit fallback semantics.

    Transport/provider failures fall back only when marked retryable. Invalid or
    schema-invalid model output may fall back once to another configured model.
    Authentication, refusal, and other non-retryable errors fail closed.
    """

    def __init__(
        self,
        providers: list[StructuredLLMProvider],
        *,
        fallback_kinds: set[AIProviderErrorKind] | None = None,
    ) -> None:
        if not providers:
            raise ValueError("At least one AI provider is required")
        self.providers = providers
        self.fallback_kinds = (
            set(_DEFAULT_FALLBACK_KINDS) if fallback_kinds is None else set(fallback_kinds)
        )

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
                eligible_kind = exc.kind in self.fallback_kinds
                safe_failure = exc.retryable or exc.kind in _OUTPUT_FAILURE_KINDS
                can_fallback = eligible_kind and safe_failure and index < len(self.providers) - 1
                if not can_fallback:
                    exc.details = {
                        "cause": exc.details,
                        "routing_attempts": [a.model_dump() for a in attempts],
                    }
                    raise

        assert last_error is not None
        raise last_error

    def close(self) -> None:
        for provider in self.providers:
            provider.close()
