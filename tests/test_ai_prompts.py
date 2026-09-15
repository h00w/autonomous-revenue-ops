from src.ai.prompts import PROMPT_REGISTRY
from src.ai.schema import strict_model_schema
from src.ai.models import ResearchOutput


def test_prompts_are_versioned_and_unique():
    assert set(PROMPT_REGISTRY) == {
        "revenue_ops.research",
        "revenue_ops.qualification",
        "revenue_ops.outreach",
    }
    versions = [prompt.version for prompt in PROMPT_REGISTRY.values()]
    assert all(version == "1.0.0" for version in versions)
    assert all("deterministic policy" in prompt.system_prompt.lower() for prompt in PROMPT_REGISTRY.values())


def test_strict_schema_closes_object_shapes():
    schema = strict_model_schema(ResearchOutput)
    assert schema["additionalProperties"] is False
