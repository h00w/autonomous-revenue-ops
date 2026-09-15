import json

import httpx

from src.ai.models import StructuredGenerationRequest
from src.ai.providers.openai import OpenAIStructuredProvider


def _request() -> StructuredGenerationRequest:
    return StructuredGenerationRequest(
        system_prompt="system",
        user_prompt="user",
        schema_name="Health",
        json_schema={
            "type": "object",
            "properties": {"ok": {"type": "boolean"}},
            "required": ["ok"],
            "additionalProperties": False,
        },
        prompt_id="test.health",
        prompt_version="1.0.0",
    )


def test_openai_responses_api_structured_contract():
    def handler(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content)
        assert request.url.path == "/v1/responses"
        assert request.headers["authorization"] == "Bearer sk-test"
        assert body["instructions"] == "system"
        assert body["text"]["format"]["type"] == "json_schema"
        assert body["text"]["format"]["strict"] is True
        assert body["text"]["format"]["name"] == "Health"
        return httpx.Response(
            200,
            json={
                "id": "resp_123",
                "status": "completed",
                "output": [
                    {
                        "type": "message",
                        "content": [{"type": "output_text", "text": "{\"ok\": true}"}],
                    }
                ],
                "usage": {"input_tokens": 11, "output_tokens": 4},
            },
        )

    client = httpx.Client(transport=httpx.MockTransport(handler))
    provider = OpenAIStructuredProvider(api_key="sk-test", model="gpt-test", client=client)
    result = provider.generate_structured(_request())
    assert result.data == {"ok": True}
    assert result.request_id == "resp_123"
    assert result.input_tokens == 11
    assert result.output_tokens == 4
