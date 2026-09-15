import pytest
from pydantic import BaseModel

from src.ai.errors import AIProviderError, AIProviderErrorKind
from src.ai.models import StructuredGenerationRequest
from src.ai.providers.mock import StaticStructuredProvider
from src.ai.router import ModelRouter


class Output(BaseModel):
    value: int


def _request() -> StructuredGenerationRequest:
    return StructuredGenerationRequest(
        system_prompt="system",
        user_prompt="user",
        schema_name="Output",
        json_schema=Output.model_json_schema(),
        prompt_id="test.router",
        prompt_version="1.0.0",
    )


def test_router_falls_back_on_retryable_provider_failure():
    first = StaticStructuredProvider(
        model="primary",
        errors=[AIProviderError(provider="static", kind=AIProviderErrorKind.RATE_LIMIT, message="limited", retryable=True)],
    )
    second = StaticStructuredProvider([{"value": 7}], model="fallback")
    output, result = ModelRouter([first, second]).generate_typed(_request(), Output)
    assert output.value == 7
    assert [attempt.success for attempt in result.routing_attempts] == [False, True]
    assert first.calls == 1 and second.calls == 1


def test_router_falls_back_on_schema_invalid_output():
    first = StaticStructuredProvider([{"wrong": 1}], model="primary")
    second = StaticStructuredProvider([{"value": 9}], model="fallback")
    output, result = ModelRouter([first, second]).generate_typed(_request(), Output)
    assert output.value == 9
    assert result.routing_attempts[0].error_kind == "schema_validation"


def test_router_fails_closed_on_authentication_error():
    first = StaticStructuredProvider(
        model="primary",
        errors=[AIProviderError(provider="static", kind=AIProviderErrorKind.AUTHENTICATION, message="bad key", retryable=False)],
    )
    second = StaticStructuredProvider([{"value": 7}], model="fallback")
    with pytest.raises(AIProviderError) as caught:
        ModelRouter([first, second]).generate_typed(_request(), Output)
    assert caught.value.kind == AIProviderErrorKind.AUTHENTICATION
    assert second.calls == 0


def test_router_fails_closed_on_model_refusal():
    first = StaticStructuredProvider(
        model="primary",
        errors=[AIProviderError(provider="static", kind=AIProviderErrorKind.REFUSAL, message="refused", retryable=False)],
    )
    second = StaticStructuredProvider([{"value": 7}], model="fallback")
    with pytest.raises(AIProviderError) as caught:
        ModelRouter([first, second]).generate_typed(_request(), Output)
    assert caught.value.kind == AIProviderErrorKind.REFUSAL
    assert second.calls == 0
