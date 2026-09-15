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


def get_workflow_store() -> WorkflowRunStore:
    """Return the durable workflow source of truth without requiring AI credentials."""
    global _store
    with _lock:
        if _store is None:
            _store = _build_store()
        return _store


def get_workflow_orchestrator() -> WorkflowOrchestrator:
    """Build the governed AI runtime lazily so importing the API never requires model keys."""
    global _orchestrator
    with _lock:
        if _orchestrator is None:
            router = build_ai_router(get_settings())
            _orchestrator = WorkflowOrchestrator(RevenueOpsSupervisor(router), get_workflow_store())
        return _orchestrator
