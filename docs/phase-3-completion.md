# Phase 3 completion gates

Phase 3 is complete when the branch passes all existing Phase 0-2 regression gates plus the following checks:

- OpenAI Responses REST contract is mocked and tested.
- Anthropic Messages structured-output contract is mocked and tested.
- Gemini GenerateContent structured-output contract is mocked and tested.
- provider outputs are locally Pydantic-validated.
- routing fallback is bounded and recorded.
- authentication/refusal paths fail closed.
- Research, Qualification, and Outreach agents use versioned prompts.
- the Supervisor calls deterministic policy before outreach drafting.
- unauthorized policy outcomes cannot invoke the Outreach Drafting Agent.
- API keys remain secret configuration values.
- provider smoke harness is side-effect free unless `--execute` is explicit.
- policy benchmark remains 100%.

Live provider smoke evidence is capability validation, not a CI prerequisite. It is required before a later Production Validated claim but does not block the contract-complete Phase 3 architecture milestone.
