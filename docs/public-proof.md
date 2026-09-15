# 90-second reviewer proof path

This page is the shortest path through the repository for a recruiter, engineering leader, or technical reviewer.

## 0–15 seconds — What problem is solved?

Autonomous Revenue Ops turns inbound revenue signals into governed workflows without letting a model directly authorize business side effects. It demonstrates the difference between an AI automation demo and an engineered AI workflow system.

## 15–35 seconds — What is the architecture?

Follow the README system flow:

`authenticated input → typed contracts → AI research/qualification → deterministic policy → durable workflow state → human/research checkpoints → execution claim → bounded SaaS adapters → retry/circuit/DLQ → execution receipt → analytics`.

Key principle: **AI proposes; deterministic software authorizes.**

## 35–55 seconds — Where is the engineering proof?

- 94-test Phase 8 regression baseline before Phase 9 release tests;
- 6/6 deterministic policy benchmark;
- seven-case supervisor gate with required rates at 100% and zero policy violations;
- prompt/version/hash manifest;
- restart-safe workflow state, stale-writer protection and executor leases;
- HMAC/replay-protected webhook ingress;
- measured-runtime analytics separated from scenario projections.

## 55–75 seconds — Can it be deployed safely?

Phase 8 builds and boots the API container in CI as UID/GID 10001 with read-only root filesystem, all Linux capabilities dropped and no-new-privileges. The Kubernetes reference adds seccomp, resource bounds, liveness/readiness and external secret references. SQLite intentionally blocks a horizontal-replica claim.

## 75–90 seconds — Can the release be inspected?

Phase 9 adds a pinned runtime image base, exact runtime lock, SPDX SBOM, source/eval/deployment integrity manifest, checksums, explicit unsigned provenance metadata, and a tag-release workflow that reruns gates before publishing a GHCR image and GitHub Release evidence asset.

## Public surfaces

- Source: https://github.com/h00w/autonomous-revenue-ops
- Hugging Face Space: https://huggingface.co/spaces/h0000w/autonomous-revenue-ops
- Hugging Face dataset: https://huggingface.co/datasets/h0000w/autonomous-revenue-ops
- System/model card: https://huggingface.co/h0000w/autonomous-revenue-ops

## What is deliberately not claimed?

The repository does not yet claim Production Validated, distributed HA, live-provider model accuracy, customer ROI, or long-window production SLO attainment. Those claims require retained live evidence and remain Phase 10 work.
