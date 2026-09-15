# Model routing and controlled fallback

Model IDs and provider order are runtime configuration. The default Phase 3 order is OpenAI, Anthropic, Gemini, but only providers with configured API keys enter the router.

`ModelRouter` allows fallback for retryable rate-limit, timeout, network, or provider failures, and for invalid/schema-invalid structured model output. Authentication errors and refusals do not fall back. Non-retryable provider errors fail closed.

This design intentionally distinguishes model availability from business authorization. A fallback model may produce a different recommendation, but that recommendation is still validated against the same Pydantic schema and passed through the same deterministic policy layer.

## Current REST contracts

- OpenAI: Responses API with strict `text.format` JSON Schema.
- Anthropic: Messages API with `output_config.format` JSON Schema.
- Gemini: `models.generateContent` with JSON structured response format.

The repository keeps model IDs configurable because model aliases and availability change independently of application policy.

## Live validation

Run `python scripts/ai_provider_smoke.py <openai|anthropic|gemini>` for a zero-side-effect dry run. Add `--execute` only after configuring a dedicated provider key. The live smoke request asks for a tiny structured health object and performs no SaaS/CRM action.
