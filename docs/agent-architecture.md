# Phase 3 agent architecture

Phase 3 introduces model-assisted reasoning without making an LLM the authorization system.

```text
Lead + optional enrichment context
        |
        v
 Research Agent ---- typed ResearchOutput
        |
        v
 Qualification Agent ---- typed QualificationRecommendation
        |
        v
 deterministic evaluate_policy()
        |
        +---- unauthorized ----> no outreach draft
        |
        +---- authorized ------> Outreach Drafting Agent
                                  |
                                  v
                              draft only
```

## Responsibility boundary

The Research Agent synthesizes supplied evidence and uncertainty. It does not browse the web or mutate external systems. The Qualification Agent recommends bounded numeric features and evidence but cannot authorize action. `src/policy.py` remains the sole authorization decision point. The Outreach Drafting Agent refuses to run unless it receives a `PolicyResult` whose `authorized_for_outreach` field is true.

The supervisor does not write to HubSpot, Salesforce, Slack, email, or webhooks. Those Phase 2 integrations remain separate effectors so later orchestration can enforce idempotency, approval, retry, and audit policy around each side effect.

## Traceability

Each agent call records the agent name, prompt ID/version, selected provider/model, and every routing attempt. Correlation IDs flow into generation requests. Provider tokens and API keys are never included in traces.

## Evidence boundary

Phase 3 contract tests prove request shapes, typed output validation, controlled fallback, prompt versioning, and deterministic authorization. Real model capability is validated separately with `scripts/ai_provider_smoke.py --execute`; CI never requires private model credentials.
