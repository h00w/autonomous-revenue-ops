from threading import RLock

from ..ai.factory import build_ai_router
from ..ai.supervisor import RevenueOpsSupervisor
from ..config import get_settings
from .engine import WorkflowOrchestrator
from .store import InMemoryWorkflowRunStore, SQLiteWorkflowRunStore, WorkflowRunStore

_orchestrator: WorkflowOrchestrator | None = None
_store: WorkflowRunStore | None = None
_lock = RLock()


def _build_store() -> WorkflowRunStore:
    settings = get_settings()
    if settings.workflow_store_backend == "memory":
        return InMemoryWorkflowRunStore()
    return SQLiteWorkflowRunStore(settings.workflow_db_path)


def get_workflow_orchestrator() -> WorkflowOrchestrator:
    """Build Phase 5 runtime lazily so importing the API never requires model keys."""
    global _orchestrator, _store
    with _lock:
        if _orchestrator is None:
            _store = _store or _build_store()
            router = build_ai_router(get_settings())
            _orchestrator = WorkflowOrchestrator(RevenueOpsSupervisor(router), _store)
        return _orchestrator
