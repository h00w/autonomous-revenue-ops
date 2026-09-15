# Phase 6 Completion Gates

Phase 6 is complete when multi-agent software/governance invariants are enforced by a versioned dataset-driven CI gate, while live-provider quality evidence remains explicitly separate and opt-in.

## Verified deterministic gates

- [x] Phase 0–5 regression suite remains green.
- [x] seven-case agent evaluation dataset covers all five deterministic policy outcomes.
- [x] instruction-like lead content is exercised as untrusted data.
- [x] structured-output success rate = **100%**.
- [x] deterministic policy decision accuracy = **100%**.
- [x] outreach/authorization agreement = **100%**.
- [x] agent/routing trace integrity = **100%**.
- [x] model-facing prompt-boundary integrity = **100%**.
- [x] policy violation count = **0**.
- [x] prompt ID/version/SHA-256 manifest matches the production prompt registry.
- [x] release thresholds are explicit, reviewable data in `evals/release_thresholds.json`.
- [x] deterministic report records the exact dataset SHA-256.
- [x] CI uploads `agent-eval-report.json` as build evidence.
- [x] full Python suite = **82/82 passed**.
- [x] legacy deterministic policy benchmark = **6/6 passed (100%)**.

## Live-provider evidence boundary

The OpenAI, Anthropic, and Gemini agent-evaluation harnesses are dry-run by default. In the Phase 6 CI gate each reported:

- 7 cases loaded;
- `external_calls: 0`;
- no live model quality claim.

A live-provider result becomes evidence only after an explicit `--execute` run with a dedicated API key and a retained report tied to provider/model, prompts, dataset, and commit. The deterministic CI percentages above must never be relabeled as live-model accuracy.

## Remaining proof work

Phase 7 moves from release correctness to operations evidence: run/event telemetry, funnel and intervention metrics, reliability indicators, cost/time accounting, and a business-impact model that clearly distinguishes measured values from scenarios/targets.
