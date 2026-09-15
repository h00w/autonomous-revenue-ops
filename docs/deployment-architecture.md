# Deployment architecture — Phase 8

Phase 8 turns the repository into a deployment-candidate artifact without overstating its current evidence.

## Runtime container

The production API image is built from `requirements-api.txt`, not the reviewer/CI dependency set. The runtime image:

- runs as UID/GID `10001:10001`;
- has a shallow liveness `HEALTHCHECK`;
- writes durable state only under `/app/data`;
- supports a read-only root filesystem with writable `/app/data` and `/tmp` mounts;
- does not copy tests, local `.env` files, Git metadata, or runtime SQLite files into the image;
- handles `SIGTERM` through Uvicorn for orchestrator-controlled shutdown.

## SQLite deployment boundary

The Phase 5 store is restart-safe SQLite, so the Kubernetes reference deployment deliberately uses:

- `replicas: 1`;
- `strategy: Recreate`;
- one `ReadWriteOnce` persistent volume;
- runtime setting `ARO_DEPLOYMENT_REPLICA_COUNT=1`.

`/health/ready` fails when SQLite is configured with more than one application replica. This is a safety boundary, not a scalability claim. Horizontal replicas require a later migration to a shared transactional persistence layer.

## Kubernetes security posture

The reference pod uses `runAsNonRoot`, fixed UID/GID 10001, `RuntimeDefault` seccomp, `allowPrivilegeEscalation: false`, a read-only root filesystem, and drops all Linux capabilities. CPU/memory requests and limits are explicit. Secrets are referenced through `autonomous-revenue-ops-secrets`; no Kubernetes `Secret` object containing values is stored in this repository.

## Production readiness

Liveness answers whether the HTTP process is alive and intentionally stays shallow. Production readiness additionally requires:

- workflow API authentication configured;
- webhook HMAC signing secret configured;
- at least one AI provider key configured;
- writable SQLite storage;
- exactly one application replica when SQLite is active.

A failed readiness contract returns HTTP `503`, allowing Kubernetes to remove the pod from service without creating a liveness restart loop.

## Evidence boundary

CI builds and boots the container under read-only-root, dropped-capability and no-new-privileges controls. The Kubernetes manifests are contract-validated statically. This proves buildability and local container runtime behavior; it does **not** prove cloud-cluster availability, autoscaling, managed storage behavior, ingress/TLS, or live production SLO attainment.
