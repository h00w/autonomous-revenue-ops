from threading import RLock
from typing import Optional, Protocol, runtime_checkable

from .models import WorkflowRun


@runtime_checkable
class WorkflowRunStore(Protocol):
    def create(self, run: WorkflowRun) -> tuple[WorkflowRun, bool]: ...
    def get(self, run_id: str) -> Optional[WorkflowRun]: ...
    def save(self, run: WorkflowRun) -> WorkflowRun: ...


class InMemoryWorkflowRunStore:
    """Thread-safe process-local run store used for the Phase 4 contract proof.

    The store intentionally exposes a stable interface so Phase 5/8 can replace
    it with durable persistence without changing workflow-engine semantics.
    """

    def __init__(self) -> None:
        self._lock = RLock()
        self._runs: dict[str, WorkflowRun] = {}
        self._idempotency_index: dict[str, str] = {}

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
