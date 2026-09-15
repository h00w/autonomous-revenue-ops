from typing import Any
from urllib.parse import quote

import httpx

from ..errors import AIProviderError, AIProviderErrorKind
from ..models import StructuredGenerationRequest, StructuredGenerationResult
from .common import ai_http_client, call_json, parse_json_text


class GeminiStructuredProvider:
    provider = "gemini"

    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        base_url: str = "https://generativelanguage.googleapis.com",
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
        model_path = quote(self.model, safe="-._")
        payload, latency_ms = call_json(
            self.http,
            "POST",
            f"{self.base_url}/v1beta/models/{model_path}:generateContent",
            headers={"x-goog-api-key": self.api_key, "content-type": "application/json"},
            json={
                "systemInstruction": {"parts": [{"text": request.system_prompt}]},
                "contents": [{"role": "user", "parts": [{"text": request.user_prompt}]}],
                "generationConfig": {
                    "maxOutputTokens": request.max_output_tokens,
                    "responseFormat": {
                        "text": {
                            "mimeType": "application/json",
                            "schema": request.json_schema,
                        }
                    },
                },
            },
        )
        text = self._extract_text(payload)
        usage = payload.get("usageMetadata") or {}
        return StructuredGenerationResult(
            provider=self.provider,
            model=self.model,
            data=parse_json_text(self.provider, text),
            request_id=payload.get("responseId"),
            input_tokens=usage.get("promptTokenCount"),
            output_tokens=usage.get("candidatesTokenCount"),
            latency_ms=latency_ms,
        )

    def _extract_text(self, payload: dict[str, Any]) -> str:
        prompt_feedback = payload.get("promptFeedback") or {}
        if prompt_feedback.get("blockReason"):
            raise AIProviderError(
                provider=self.provider,
                kind=AIProviderErrorKind.REFUSAL,
                message="Gemini blocked the structured generation request",
                retryable=False,
                details=prompt_feedback,
            )
        candidates = payload.get("candidates") or []
        if not candidates:
            raise AIProviderError(
                provider=self.provider,
                kind=AIProviderErrorKind.INVALID_RESPONSE,
                message="Gemini response contained no candidates",
                retryable=True,
                details=payload,
            )
        parts = ((candidates[0].get("content") or {}).get("parts") or [])
        texts = [part.get("text") for part in parts if isinstance(part.get("text"), str)]
        if texts:
            return "".join(texts)
        raise AIProviderError(
            provider=self.provider,
            kind=AIProviderErrorKind.INVALID_RESPONSE,
            message="Gemini response contained no text part",
            retryable=True,
            details=candidates[0],
        )
