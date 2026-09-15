from threading import RLock

from ..ai.factory import build_ai_router
from ..ai.supervisor import RevenueOpsSupervisor
from ..config import get_settings
from .engine import WorkflowOrchestrator
from .store import InMemoryWorkflowRunStore

_store = InMemoryWorkflowRunStore()
_orchestrator: WorkflowOrchestrator | None = None
_lock = RLock()


def get_workflow_orchestrator() -> WorkflowOrchestrator:
    """Build the process-local Phase 4 runtime lazily.

    AI credentials are not required to import or start the API process. A start
    request needs at least one configured AI provider; status/approval routes do
    not introduce any new secret storage.
    """
    global _orchestrator
    with _lock:
        if _orchestrator is None:
            router = build_ai_router(get_settings())
            _orchestrator = WorkflowOrchestrator(RevenueOpsSupervisor(router), _store)
        return _orchestrator
