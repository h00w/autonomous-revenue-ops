import json

import httpx

from src.ai.models import StructuredGenerationRequest
from src.ai.providers.gemini import GeminiStructuredProvider


def _request() -> StructuredGenerationRequest:
    return StructuredGenerationRequest(
        system_prompt="system",
        user_prompt="user",
        schema_name="Health",
        json_schema={"type": "object", "properties": {"ok": {"type": "boolean"}}, "required": ["ok"]},
        prompt_id="test.health",
        prompt_version="1.0.0",
    )


def test_gemini_generate_content_structured_contract():
    def handler(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content)
        assert request.url.path == "/v1beta/models/gemini-test:generateContent"
        assert request.headers["x-goog-api-key"] == "gemini-test-key"
        assert body["systemInstruction"]["parts"][0]["text"] == "system"
        response_format = body["generationConfig"]["responseFormat"]["text"]
        assert response_format["mimeType"] == "application/json"
        assert response_format["schema"]["type"] == "object"
        return httpx.Response(
            200,
            json={
                "responseId": "gem_123",
                "candidates": [{"content": {"parts": [{"text": "{\"ok\": true}"}]}}],
                "usageMetadata": {"promptTokenCount": 13, "candidatesTokenCount": 6},
            },
        )

    client = httpx.Client(transport=httpx.MockTransport(handler))
    provider = GeminiStructuredProvider(api_key="gemini-test-key", model="gemini-test", client=client)
    result = provider.generate_structured(_request())
    assert result.data == {"ok": True}
    assert result.request_id == "gem_123"
    assert result.output_tokens == 6
