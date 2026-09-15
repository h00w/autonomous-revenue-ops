from ..config import Settings, get_settings
from .providers import AnthropicStructuredProvider, GeminiStructuredProvider, OpenAIStructuredProvider
from .router import ModelRouter


def build_ai_router(settings: Settings | None = None) -> ModelRouter:
    settings = settings or get_settings()
    providers = []
    order = [name.strip().lower() for name in settings.ai_provider_order.split(",") if name.strip()]

    for name in order:
        if name == "openai" and settings.openai_api_key:
            providers.append(
                OpenAIStructuredProvider(
                    api_key=settings.openai_api_key.get_secret_value(),
                    model=settings.openai_model,
                    base_url=settings.openai_base_url,
                    timeout_seconds=settings.ai_timeout_seconds,
                )
            )
        elif name == "anthropic" and settings.anthropic_api_key:
            providers.append(
                AnthropicStructuredProvider(
                    api_key=settings.anthropic_api_key.get_secret_value(),
                    model=settings.anthropic_model,
                    base_url=settings.anthropic_base_url,
                    timeout_seconds=settings.ai_timeout_seconds,
                )
            )
        elif name == "gemini" and settings.gemini_api_key:
            providers.append(
                GeminiStructuredProvider(
                    api_key=settings.gemini_api_key.get_secret_value(),
                    model=settings.gemini_model,
                    base_url=settings.gemini_base_url,
                    timeout_seconds=settings.ai_timeout_seconds,
                )
            )

    if not providers:
        raise ValueError("No configured AI providers; set at least one ARO_*_API_KEY")
    return ModelRouter(providers)
