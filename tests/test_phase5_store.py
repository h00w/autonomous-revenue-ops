import pytest

from src.models import LeadInput
from src.orchestration.models import WorkflowRun, WorkflowRunStatus
from src.orchestration.store import SQLiteWorkflowRunStore


def _run(run_id: str = "run_1", idempotency_key: str = "idem_1") -> WorkflowRun:
    return WorkflowRun(
        run_id=run_id,
        correlation_id="corr_1",
        idempotency_key=idempotency_key,
        status=WorkflowRunStatus.RECEIVED,
        lead=LeadInput(
            lead_id="lead_1",
            name="Ada Lovelace",
            email="ada@example.com",
            company="Analytical Engines AB",
            role="CTO",
            message="Interested in governed automation",
            consent_to_contact=True,
        ),
    )


def test_sqlite_store_survives_reopen_and_preserves_idempotency(tmp_path):
    path = str(tmp_path / "workflows.sqlite3")
    first = SQLiteWorkflowRunStore(path)
    created, replayed = first.create(_run())
    assert replayed is False

    reopened = SQLiteWorkflowRunStore(path)
    loaded = reopened.get(created.run_id)
    assert loaded is not None
    assert loaded.lead.email == "ada@example.com"

    replay, replayed = reopened.create(_run("run_other", "idem_1"))
    assert replayed is True
    assert replay.run_id == created.run_id


def test_sqlite_store_rejects_stale_revision(tmp_path):
    store = SQLiteWorkflowRunStore(str(tmp_path / "workflows.sqlite3"))
    store.create(_run())
    current = store.get("run_1")
    stale = store.get("run_1")
    assert current is not None and stale is not None

    current.status = WorkflowRunStatus.RUNNING
    current.revision = 1
    store.save(current)

    stale.status = WorkflowRunStatus.RUNNING
    stale.revision = 1
    with pytest.raises(RuntimeError, match="revision conflict"):
        store.save(stale)


def test_sqlite_leases_are_exclusive_and_expire(tmp_path):
    store = SQLiteWorkflowRunStore(str(tmp_path / "workflows.sqlite3"))
    store.create(_run())
    assert store.acquire_lease("run_1", "worker-a", 10, now=100.0) is True
    assert store.acquire_lease("run_1", "worker-b", 10, now=105.0) is False
    assert store.acquire_lease("run_1", "worker-b", 10, now=111.0) is True


def test_sqlite_lists_only_running_runs_as_recoverable(tmp_path):
    store = SQLiteWorkflowRunStore(str(tmp_path / "workflows.sqlite3"))
    store.create(_run("run_running", "idem_running"))
    store.create(_run("run_waiting", "idem_waiting"))
    running = store.get("run_running")
    waiting = store.get("run_waiting")
    assert running is not None and waiting is not None
    running.status = WorkflowRunStatus.RUNNING
    running.revision = 1
    waiting.status = WorkflowRunStatus.WAITING_HUMAN_REVIEW
    waiting.revision = 1
    store.save(running)
    store.save(waiting)
    assert [item.run_id for item in store.list_recoverable()] == ["run_running"]
