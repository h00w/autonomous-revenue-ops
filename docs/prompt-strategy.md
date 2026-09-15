# Prompt strategy and versioning

Prompts are application artifacts, not ad-hoc strings. `src/ai/prompts.py` assigns every production prompt a stable ID and semantic version. Phase 3 starts with `revenue_ops.research@1.0.0`, `revenue_ops.qualification@1.0.0`, and `revenue_ops.outreach@1.0.0`.

A prompt version changes when instructions that can affect behavior change. Cosmetic code refactors do not change prompt versions. Evaluation evidence in Phase 6 will be keyed by prompt ID/version plus provider/model so a prompt change cannot silently inherit an older quality claim.

## Untrusted-data boundary

Lead messages, CRM fields, enrichment text, and research context are serialized inside an `<untrusted_data>` block. System prompts state that these values are data rather than instructions and explicitly forbid external action or authorization. This does not claim that prompt injection is solved; it creates an inspectable control that Phase 5 security testing and Phase 6 adversarial evaluations can exercise.

## Structured output

Each agent uses a Pydantic output model. Its JSON Schema is sent to the provider's structured-output mechanism and the returned dictionary is validated locally again. A provider response that does not satisfy the local model is classified as `schema_validation` and may be routed to a configured fallback model. Refusals and authentication failures fail closed.
