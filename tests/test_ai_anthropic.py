import json

import httpx

from src.ai.models import StructuredGenerationRequest
from src.ai.providers.anthropic import AnthropicStructuredProvider


def _request() -> StructuredGenerationRequest:
    return StructuredGenerationRequest(
        system_prompt="system",
        user_prompt="user",
        schema_name="Health",
        json_schema={"type": "object", "properties": {"ok": {"type": "boolean"}}, "required": ["ok"]},
        prompt_id="test.health",
        prompt_version="1.0.0",
    )


def test_anthropic_messages_structured_contract():
    def handler(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content)
        assert request.url.path == "/v1/messages"
        assert request.headers["x-api-key"] == "anthropic-test"
        assert request.headers["anthropic-version"] == "2023-06-01"
        assert body["system"] == "system"
        assert body["output_config"]["format"]["type"] == "json_schema"
        assert body["output_config"]["format"]["schema"]["type"] == "object"
        return httpx.Response(
            200,
            json={
                "id": "msg_123",
                "content": [{"type": "text", "text": "{\"ok\": true}"}],
                "usage": {"input_tokens": 12, "output_tokens": 5},
            },
        )

    client = httpx.Client(transport=httpx.MockTransport(handler))
    provider = AnthropicStructuredProvider(api_key="anthropic-test", model="claude-test", client=client)
    result = provider.generate_structured(_request())
    assert result.data == {"ok": True}
    assert result.request_id == "msg_123"
    assert result.input_tokens == 12
