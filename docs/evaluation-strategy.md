# Agent Evaluation Strategy

Phase 6 separates two evidence classes so deterministic CI proof is never presented as live-model quality evidence.

## 1. Deterministic contract evaluation — required CI gate

`evals/agent_release_gate.py` runs the actual `RevenueOpsSupervisor` with a deterministic structured provider and a versioned fixture dataset. It validates the architecture and governance contracts that should not vary with model sampling:

- all structured outputs validate through the production Pydantic schemas;
- expected deterministic policy decisions remain unchanged;
- outreach presence matches deterministic authorization behavior;
- no outreach is emitted when policy says it is unauthorized;
- agent trace order, provider/model identity and routing success remain coherent;
- prompt IDs and versions match the production registry;
- every model-facing user payload remains inside the `<untrusted_data>` boundary;
- the system guardrail continues to state that deterministic policy authorizes actions;
- prompt text changes require an explicit manifest update rather than silently entering a release.

The gate currently requires 100% on these contract metrics and zero policy violations. This is intentionally strict because the provider is deterministic and the assertions are software invariants.

## 2. Live-provider evaluation — opt-in evidence

`evals/live_agent_eval.py` can run the same dataset against a configured OpenAI, Anthropic, or Gemini provider only when `--execute` is supplied. CI calls this harness in dry-run mode only. Live results are evidence about a named provider/model/configuration at a point in time; they are not inferred from deterministic fixtures.

A live evaluation report should retain provider/model traces, dataset identity, date/commit, and the prompt manifest used for the run. The repository must not claim a provider quality percentage until such a live run has actually been executed and retained.

## Dataset design

`data/agent_eval_cases.jsonl` covers all five deterministic policy outcomes and includes a prompt-injection-shaped lead message. That injection case proves the software prompt-boundary contract: instruction-like lead text remains untrusted data and cannot directly mint deterministic authorization. It is not, by itself, a claim that every model resists every prompt-injection technique.

## Release criteria

Thresholds live in `evals/release_thresholds.json`. Any threshold change is therefore code-reviewed and version-controlled. The deterministic report records the dataset SHA-256 so a green gate is tied to the exact fixture set used.
