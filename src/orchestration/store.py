import json
import sqlite3
import time
from pathlib import Path
from threading import RLock
from typing import Optional, Protocol, runtime_checkable

from .models import WorkflowRun, WorkflowRunStatus


@runtime_checkable
class WorkflowRunStore(Protocol):
    def create(self, run: WorkflowRun) -> tuple[WorkflowRun, bool]: ...
    def get(self, run_id: str) -> Optional[WorkflowRun]: ...
    def save(self, run: WorkflowRun) -> WorkflowRun: ...
    def acquire_lease(self, run_id: str, owner: str, ttl_seconds: int, *, now: float | None = None) -> bool: ...
    def release_lease(self, run_id: str, owner: str) -> None: ...
    def list_recoverable(self) -> list[WorkflowRun]: ...


class InMemoryWorkflowRunStore:
    """Thread-safe process-local store retained for tests and local demos."""

    def __init__(self) -> None:
        self._lock = RLock()
        self._runs: dict[str, WorkflowRun] = {}
        self._idempotency_index: dict[str, str] = {}
        self._leases: dict[str, tuple[str, float]] = {}

    def create(self, run: WorkflowRun) -> tuple[WorkflowRun, bool]:
        with self._lock:
            existing_id = self._idempotency_index.get(run.idempotency_key)
            if existing_id is not None:
                return self._runs[existing_id].model_copy(deep=True), True
            self._runs[run.run_id] = run.model_copy(deep=True)
            self._idempotency_index[run.idempotency_key] = run.run_id
            return run.model_copy(deep=True), False

    def get(self, run_id: str) -> Optional[WorkflowRun]:
        with self._lock:
            run = self._runs.get(run_id)
            return run.model_copy(deep=True) if run is not None else None

    def save(self, run: WorkflowRun) -> WorkflowRun:
        with self._lock:
            if run.run_id not in self._runs:
                raise KeyError(run.run_id)
            self._runs[run.run_id] = run.model_copy(deep=True)
            return run.model_copy(deep=True)

    def acquire_lease(self, run_id: str, owner: str, ttl_seconds: int, *, now: float | None = None) -> bool:
        with self._lock:
            if run_id not in self._runs:
                raise KeyError(run_id)
            current = now if now is not None else time.time()
            lease = self._leases.get(run_id)
            if lease is not None and lease[0] != owner and lease[1] > current:
                return False
            self._leases[run_id] = (owner, current + ttl_seconds)
            return True

    def release_lease(self, run_id: str, owner: str) -> None:
        with self._lock:
            lease = self._leases.get(run_id)
            if lease is not None and lease[0] == owner:
                self._leases.pop(run_id, None)

    def list_recoverable(self) -> list[WorkflowRun]:
        with self._lock:
            return [
                run.model_copy(deep=True)
                for run in self._runs.values()
                if run.status == WorkflowRunStatus.RUNNING
            ]


class SQLiteWorkflowRunStore:
    """Restart-safe single-node workflow store with optimistic revisions and leases.

    SQLite is intentionally the Phase 5 durability boundary. It survives process
    restarts and provides transactional idempotency/lease semantics on one host,
    but it is not presented as a multi-region or horizontally scaled database.
    """

    def __init__(self, path: str) -> None:
        self.path = path
        db_path = Path(path)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS workflow_runs (
                    run_id TEXT PRIMARY KEY,
                    idempotency_key TEXT NOT NULL UNIQUE,
                    payload TEXT NOT NULL,
                    revision INTEGER NOT NULL,
                    lease_owner TEXT,
                    lease_expires_at REAL
                )
                """
            )

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path, timeout=10.0)
        conn.row_factory = sqlite3.Row
        return conn

    @staticmethod
    def _encode(run: WorkflowRun) -> str:
        return run.model_dump_json()

    @staticmethod
    def _decode(payload: str) -> WorkflowRun:
        return WorkflowRun.model_validate_json(payload)

    def create(self, run: WorkflowRun) -> tuple[WorkflowRun, bool]:
        with self._connect() as conn:
            try:
                conn.execute(
                    "INSERT INTO workflow_runs(run_id,idempotency_key,payload,revision) VALUES(?,?,?,?)",
                    (run.run_id, run.idempotency_key, self._encode(run), run.revision),
                )
                return run.model_copy(deep=True), False
            except sqlite3.IntegrityError:
                row = conn.execute(
                    "SELECT payload FROM workflow_runs WHERE idempotency_key=?",
                    (run.idempotency_key,),
                ).fetchone()
                if row is None:
                    raise
                return self._decode(row["payload"]), True

    def get(self, run_id: str) -> Optional[WorkflowRun]:
        with self._connect() as conn:
            row = conn.execute("SELECT payload FROM workflow_runs WHERE run_id=?", (run_id,)).fetchone()
            return self._decode(row["payload"]) if row is not None else None

    def save(self, run: WorkflowRun) -> WorkflowRun:
        expected_previous = max(run.revision - 1, 0)
        with self._connect() as conn:
            conn.execute("BEGIN IMMEDIATE")
            row = conn.execute("SELECT revision FROM workflow_runs WHERE run_id=?", (run.run_id,)).fetchone()
            if row is None:
                raise KeyError(run.run_id)
            if int(row["revision"]) != expected_previous:
                raise RuntimeError(
                    f"Workflow revision conflict for {run.run_id}: expected {expected_previous}, found {row['revision']}"
                )
            conn.execute(
                "UPDATE workflow_runs SET payload=?, revision=? WHERE run_id=?",
                (self._encode(run), run.revision, run.run_id),
            )
        return run.model_copy(deep=True)

    def acquire_lease(self, run_id: str, owner: str, ttl_seconds: int, *, now: float | None = None) -> bool:
        current = now if now is not None else time.time()
        expires = current + ttl_seconds
        with self._connect() as conn:
            conn.execute("BEGIN IMMEDIATE")
            row = conn.execute(
                "SELECT lease_owner, lease_expires_at FROM workflow_runs WHERE run_id=?", (run_id,)
            ).fetchone()
            if row is None:
                raise KeyError(run_id)
            lease_owner = row["lease_owner"]
            lease_expires_at = row["lease_expires_at"]
            if lease_owner and lease_owner != owner and lease_expires_at is not None and lease_expires_at > current:
                return False
            conn.execute(
                "UPDATE workflow_runs SET lease_owner=?, lease_expires_at=? WHERE run_id=?",
                (owner, expires, run_id),
            )
            return True

    def release_lease(self, run_id: str, owner: str) -> None:
        with self._connect() as conn:
            conn.execute(
                "UPDATE workflow_runs SET lease_owner=NULL, lease_expires_at=NULL WHERE run_id=? AND lease_owner=?",
                (run_id, owner),
            )

    def list_recoverable(self) -> list[WorkflowRun]:
        with self._connect() as conn:
            rows = conn.execute("SELECT payload FROM workflow_runs").fetchall()
        return [
            run
            for row in rows
            if (run := self._decode(row["payload"])).status == WorkflowRunStatus.RUNNING
        ]
