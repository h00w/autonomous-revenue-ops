from typing import Any

import httpx

from ..errors import AIProviderError, AIProviderErrorKind
from ..models import StructuredGenerationRequest, StructuredGenerationResult
from .common import ai_http_client, call_json, parse_json_text


class OpenAIStructuredProvider:
    provider = "openai"

    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        base_url: str = "https://api.openai.com",
        client: httpx.Client | None = None,
        timeout_seconds: float = 30.0,
    ) -> None:
        self.model = model
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.http = ai_http_client(self.provider, client=client, timeout_seconds=timeout_seconds)

    def close(self) -> None:
        self.http.close()

    def generate_structured(self, request: StructuredGenerationRequest) -> StructuredGenerationResult:
        payload, latency_ms = call_json(
            self.http,
            "POST",
            f"{self.base_url}/v1/responses",
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            json={
                "model": self.model,
                "instructions": request.system_prompt,
                "input": request.user_prompt,
                "max_output_tokens": request.max_output_tokens,
                "text": {
                    "format": {
                        "type": "json_schema",
                        "name": request.schema_name,
                        "schema": request.json_schema,
                        "strict": True,
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
        if payload.get("status") == "incomplete":
            raise AIProviderError(
                provider=self.provider,
                kind=AIProviderErrorKind.INVALID_RESPONSE,
                message="OpenAI response was incomplete",
                retryable=True,
                details=payload.get("incomplete_details"),
            )
        for item in payload.get("output", []):
            if item.get("type") != "message":
                continue
            for block in item.get("content", []):
                if block.get("type") == "refusal":
                    raise AIProviderError(
                        provider=self.provider,
                        kind=AIProviderErrorKind.REFUSAL,
                        message="OpenAI refused the structured generation request",
                        retryable=False,
                        details=block.get("refusal"),
                    )
                if block.get("type") == "output_text" and isinstance(block.get("text"), str):
                    return block["text"]
        raise AIProviderError(
            provider=self.provider,
            kind=AIProviderErrorKind.INVALID_RESPONSE,
            message="OpenAI response contained no output_text block",
            retryable=True,
            details=payload,
        )
