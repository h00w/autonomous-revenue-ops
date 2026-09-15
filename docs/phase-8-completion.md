# Phase 8 completion — Deployment Hardening & SLO Evidence

Phase 8 establishes a deployable, security-hardened **deployment-candidate** artifact and an evidence model for deployment health/SLOs. It does not claim production high availability or production SLO attainment.

## Verified completion gates

The final Phase 8 pull-request CI run (`34974452164`) completed successfully on the Phase 8 head.

| Gate | Evidence | Result |
| --- | --- | --- |
| Full Python regression suite | `python -m pytest -q` | **94/94 passed** |
| Deterministic policy benchmark | `evals/benchmark.py` | **6/6 (100%)** |
| Deterministic supervisor release gate | `evals/agent_release_gate.py` | **all required rates 100%; 0 policy violations** |
| Live-model harness default behavior | OpenAI / Anthropic / Gemini dry-runs | **0 external calls** |
| Prior SaaS/workflow/reliability/analytics gates | Phase 2–7 smoke checks | **all passed** |
| Static deployment hardening | `scripts/deployment_contract.py` | **passed; 0 errors; 0 network calls** |
| SQLite scaling boundary | deployment contract | **single_replica** |
| SLO target harness default behavior | `scripts/slo_probe.py` | **candidate_slo_target; 0 external calls** |
| Container image | `docker build` | **built successfully** |
| Runtime identity | Docker Config.User | **10001:10001** |
| Hardened local runtime | read-only root FS, `cap-drop ALL`, no-new-privileges, dedicated writable `/app/data` | **booted successfully** |
| Container liveness | `/health/live` | **HTTP 200 / ok** |
| Container readiness | `/health/ready` in test mode | **HTTP 200 / ok** |
| Production missing-config behavior | automated test | **HTTP 503 / degraded** |
| SQLite multi-replica behavior | automated test | **fails readiness** |

## Deployment controls delivered

- multi-stage API-only Docker image;
- non-root UID/GID `10001:10001`;
- shallow Docker liveness check;
- SIGTERM shutdown contract;
- read-only-root compatible runtime;
- writable state isolated to `/app/data` and temporary files to `/tmp`;
- all Linux capabilities dropped in Compose/Kubernetes references;
- `no-new-privileges` / `allowPrivilegeEscalation: false`;
- Kubernetes `RuntimeDefault` seccomp;
- CPU/memory requests and limits;
- liveness and readiness probes;
- required external secret reference without committed secret values;
- `replicas: 1`, `Recreate`, and `ReadWriteOnce` to match the SQLite evidence boundary;
- deployment contract validation in CI;
- SLO target/live-probe evidence classes.

## SLO evidence boundary

The default SLO configuration is explicitly labeled `candidate_slo_target`:

- liveness availability target: **99.5%**;
- readiness success target: **99.5%**;
- p95 health-probe latency target: **500 ms**.

CI runs the SLO harness without `--execute`, so no deployment is contacted and no live-SLO claim is created. Only an explicitly executed deployment probe may emit `live_deployment_probe` evidence.

## Persistence and scaling boundary

The durable workflow/replay/dead-letter state is still SQLite-backed. Phase 8 therefore validates a **single-application-replica** topology with persistent storage. This establishes container deployability and restart-safe single-host operation; it does not establish horizontally scaled application availability, multi-region durability, or shared-database failover.

Before increasing application replicas, workflow/idempotency/replay state must move to a shared transactional backend and be validated under concurrency, failover, recovery, and duplicate-delivery tests.

## What Phase 8 does not prove

Phase 8 does **not** prove:

- cloud-cluster or multi-zone high availability;
- ingress/TLS/WAF behavior;
- managed persistent-volume failover;
- autoscaling behavior;
- production error-budget performance;
- long-window production SLO attainment;
- live SaaS/provider reliability or model quality.

These remain separate evidence requirements.

## Release decision

**Phase 8 deployment hardening gates: PASS.**

The repository may now be described as a **deployment-candidate, contract-tested, hardened single-replica architecture proof**. It must not yet be described as **Production Validated**.

## Next milestone

Phase 9: public release/supply-chain proof — reproducible release metadata, SBOM/provenance evidence, release bundle integrity, security/release documentation, and recruiter-facing public proof surfaces.
