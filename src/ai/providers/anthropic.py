from typing import Any

import httpx

from ..errors import AIProviderError, AIProviderErrorKind
from ..models import StructuredGenerationRequest, StructuredGenerationResult
from .common import ai_http_client, call_json, parse_json_text


class AnthropicStructuredProvider:
    provider = "anthropic"

    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        base_url: str = "https://api.anthropic.com",
        anthropic_version: str = "2023-06-01",
        client: httpx.Client | None = None,
        timeout_seconds: float = 30.0,
    ) -> None:
        self.model = model
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.anthropic_version = anthropic_version
        self.http = ai_http_client(self.provider, client=client, timeout_seconds=timeout_seconds)

    def close(self) -> None:
        self.http.close()

    def generate_structured(self, request: StructuredGenerationRequest) -> StructuredGenerationResult:
        payload, latency_ms = call_json(
            self.http,
            "POST",
            f"{self.base_url}/v1/messages",
            headers={
                "x-api-key": self.api_key,
                "anthropic-version": self.anthropic_version,
                "content-type": "application/json",
            },
            json={
                "model": self.model,
                "max_tokens": request.max_output_tokens,
                "system": request.system_prompt,
                "messages": [{"role": "user", "content": request.user_prompt}],
                "output_config": {
                    "format": {
                        "type": "json_schema",
                        "schema": request.json_schema,
                    }
                },
            },
        )
        text = self._extract_text(payload)
        usage = payload.get("usage") or {}
        return StructuredGenerationResult(
            provider=self.provider,
            model=self.model,
            data=parse_json_text(self.provider, text),
            request_id=payload.get("id"),
            input_tokens=usage.get("input_tokens"),
            output_tokens=usage.get("output_tokens"),
            latency_ms=latency_ms,
        )

    def _extract_text(self, payload: dict[str, Any]) -> str:
        texts: list[str] = []
        for block in payload.get("content", []):
            if block.get("type") == "text" and isinstance(block.get("text"), str):
                texts.append(block["text"])
            elif block.get("type") == "refusal":
                raise AIProviderError(
                    provider=self.provider,
                    kind=AIProviderErrorKind.REFUSAL,
                    message="Anthropic refused the structured generation request",
                    retryable=False,
                    details=block,
                )
        if texts:
            return "".join(texts)
        raise AIProviderError(
            provider=self.provider,
            kind=AIProviderErrorKind.INVALID_RESPONSE,
            message="Anthropic response contained no text content",
            retryable=True,
            details=payload,
        )
