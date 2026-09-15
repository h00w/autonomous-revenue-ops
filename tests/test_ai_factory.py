from src.ai.factory import build_ai_router
from src.config import Settings


def test_factory_uses_only_configured_providers_in_explicit_order():
    settings = Settings(
        _env_file=None,
        ai_provider_order="anthropic,openai,gemini",
        openai_api_key="openai-secret",
        anthropic_api_key="anthropic-secret",
        gemini_api_key=None,
    )
    router = build_ai_router(settings)
    try:
        assert [provider.provider for provider in router.providers] == ["anthropic", "openai"]
    finally:
        router.close()


def test_secret_values_are_masked_in_settings_repr():
    settings = Settings(_env_file=None, openai_api_key="super-secret-value")
    assert "super-secret-value" not in repr(settings)
