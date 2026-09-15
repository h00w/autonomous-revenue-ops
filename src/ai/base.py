from typing import Protocol, runtime_checkable

from .models import StructuredGenerationRequest, StructuredGenerationResult


@runtime_checkable
class StructuredLLMProvider(Protocol):
    provider: str
    model: str

    def generate_structured(
        self, request: StructuredGenerationRequest
    ) -> StructuredGenerationResult: ...

    def close(self) -> None: ...
