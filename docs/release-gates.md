# AI Release Gates

A pull request that changes agents, prompts, routing, schemas, policy, or evaluation fixtures must preserve the deterministic Phase 6 release gate.

## Required CI sequence

1. compile/import checks;
2. full Python regression suite;
3. deterministic policy benchmark;
4. deterministic multi-agent release gate;
5. existing SaaS/AI/workflow/reliability dry-run smoke gates.

The agent gate emits `agent-eval-report.json`, which CI uploads as a build artifact. The report declares `evidence_class=deterministic_contract_eval` and `live_provider_evidence=false`.

## Prompt change control

`evals/prompt_manifest.json` stores the approved prompt ID, semantic version, and SHA-256 of each system prompt. Changing prompt text without updating the manifest fails CI. A legitimate prompt change should therefore update the prompt version, manifest hash, evaluation fixtures if needed, and explain the behavioral intent in the PR.

## Failure policy

Release is blocked when any required metric falls below `evals/release_thresholds.json`, a policy violation is observed, or the prompt manifest does not match. Thresholds are data, not hidden constants, so reviewers can see when release standards change.
