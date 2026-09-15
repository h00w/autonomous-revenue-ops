from collections import deque
from typing import Iterable

from ..errors import AIProviderError
from ..models import StructuredGenerationRequest, StructuredGenerationResult


class StaticStructuredProvider:
    """Deterministic provider for tests and local architecture demonstrations."""

    provider = "static"

    def __init__(
        self,
        responses: Iterable[dict] = (),
        *,
        model: str = "static-v1",
        errors: Iterable[AIProviderError] = (),
    ) -> None:
        self.model = model
        self.responses = deque(responses)
        self.errors = deque(errors)
        self.calls = 0

    def generate_structured(self, request: StructuredGenerationRequest) -> StructuredGenerationResult:
        self.calls += 1
        if self.errors:
            raise self.errors.popleft()
        if not self.responses:
            raise RuntimeError("StaticStructuredProvider has no queued response")
        return StructuredGenerationResult(provider=self.provider, model=self.model, data=self.responses.popleft())

    def close(self) -> None:
        return None
