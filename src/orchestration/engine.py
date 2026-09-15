import hashlib
import json
from datetime import datetime, timedelta, timezone
from typing import Protocol
from uuid import uuid4

from ..ai.models import SupervisedLeadResult
from ..models import Decision, LeadInput
from .models import (
    ExecutionClaim,
    ExecutionClaimRequest,
    ExecutionReceipt,
    HumanApproval,
    RecoveryRequest,
    ResearchResumeRequest,
    StartLeadWorkflowRequest,
    WorkflowHistoryEntry,
    WorkflowRun,
    WorkflowRunResponse,
    WorkflowRunStatus,
)
from .store import WorkflowRunStore


class LeadWorkflowEvaluator(Protocol):
    def evaluate(
        self,
        lead: LeadInput,
        *,
        enrichment_context: dict | None = None,
        correlation_id: str | None = None,
    ) -> SupervisedLeadResult: ...


class WorkflowOrchestrator:
    """Explicit state machine around governed evaluation and bounded execution."""

    def __init__(self, evaluator: LeadWorkflowEvaluator, store: WorkflowRunStore) -> None:
        self.evaluator = evaluator
        self.store = store

    def start(
        self,
        request: StartLeadWorkflowRequest,
        *,
        correlation_id: str | None = None,
        idempotency_key: str | None = None,
    ) -> WorkflowRunResponse:
        correlation_id = correlation_id or f"corr_{uuid4().hex}"
        idempotency_key = idempotency_key or self._derive_idempotency_key(request)
        run = WorkflowRun(
            run_id=f"run_{uuid4().hex}",
            correlation_id=correlation_id,
            idempotency_key=idempotency_key,
            status=WorkflowRunStatus.RECEIVED,
            lead=request.lead,
            enrichment_context=request.enrichment_context,
            history=[WorkflowHistoryEntry(sequence=1, status=WorkflowRunStatus.RECEIVED, note="Workflow request accepted.")],
        )
        run, replayed = self.store.create(run)
        if replayed:
            return WorkflowRunResponse(run=run, replayed=True)
        run = self._transition(run, WorkflowRunStatus.RUNNING, "Governed evaluation started.")
        self.store.save(run)
        return WorkflowRunResponse(run=self._evaluate(run, request.enrichment_context), replayed=False)

    def get(self, run_id: str) -> WorkflowRun:
        run = self.store.get(run_id)
        if run is None:
            raise KeyError(run_id)
        return run

    def approve(self, run_id: str, approval: HumanApproval) -> WorkflowRun:
        run = self.get(run_id)
        if run.status != WorkflowRunStatus.WAITING_HUMAN_REVIEW:
            raise ValueError("Workflow is not waiting for human review")
        run.human_approval = approval
        run.execution_authorized = approval.approved
        if approval.approved:
            return self._persist_transition(run, WorkflowRunStatus.READY_FOR_EXECUTION, f"Human approval granted by {approval.reviewer}.")
        return self._persist_transition(run, WorkflowRunStatus.COMPLETED, f"Human approval denied by {approval.reviewer}; no external execution authorized.")

    def resume_research(self, run_id: str, request: ResearchResumeRequest) -> WorkflowRun:
        run = self.get(run_id)
        if run.status != WorkflowRunStatus.WAITING_RESEARCH:
            raise ValueError("Workflow is not waiting for additional research")
        run.enrichment_context.update(request.enrichment_context)
        run = self._transition(run, WorkflowRunStatus.RUNNING, "Additional evidence supplied; evaluation resumed.")
        self.store.save(run)
        return self._evaluate(run, run.enrichment_context)

    def claim_execution(self, run_id: str, request: ExecutionClaimRequest) -> WorkflowRun:
        run = self.get(run_id)
        if run.status != WorkflowRunStatus.READY_FOR_EXECUTION or not run.execution_authorized:
            raise ValueError("Workflow is not ready and authorized for execution")
        if not self.store.acquire_lease(run_id, request.owner, request.ttl_seconds):
            raise ValueError("Workflow execution is already leased by another executor")
        run.execution_claim = ExecutionClaim(
            owner=request.owner,
            expires_at=datetime.now(timezone.utc) + timedelta(seconds=request.ttl_seconds),
        )
        return self._persist_transition(run, WorkflowRunStatus.READY_FOR_EXECUTION, f"Execution leased to {request.owner}.")

    def complete_execution(self, run_id: str, receipt: ExecutionReceipt) -> WorkflowRun:
        run = self.get(run_id)
        if run.status == WorkflowRunStatus.COMPLETED and run.execution_receipt is not None:
            if run.execution_receipt == receipt:
                return run
            raise ValueError("Workflow is already completed with a different execution receipt")
        if run.status != WorkflowRunStatus.READY_FOR_EXECUTION:
            raise ValueError("Workflow is not ready for execution")
        if not run.execution_authorized:
            raise ValueError("Workflow execution is not authorized")
        if run.execution_claim is not None and receipt.claim_id != run.execution_claim.claim_id:
            raise ValueError("Execution receipt does not match the active execution claim")
        run.execution_receipt = receipt
        completed = self._persist_transition(run, WorkflowRunStatus.COMPLETED, f"External execution recorded by {receipt.executor}.")
        if run.execution_claim is not None:
            self.store.release_lease(run_id, run.execution_claim.owner)
        return completed

    def recover_stalled(self, request: RecoveryRequest) -> list[WorkflowRun]:
        recovered: list[WorkflowRun] = []
        for run in self.store.list_recoverable()[: request.max_runs]:
            if not self.store.acquire_lease(run.run_id, request.owner, request.lease_ttl_seconds):
                continue
            try:
                latest = self.get(run.run_id)
                if latest.status != WorkflowRunStatus.RUNNING:
                    continue
                latest.recovery_attempts += 1
                latest = self._transition(latest, WorkflowRunStatus.RUNNING, f"Recovery attempt {latest.recovery_attempts} acquired by {request.owner}.")
                self.store.save(latest)
                recovered.append(self._evaluate(latest, latest.enrichment_context))
            finally:
                self.store.release_lease(run.run_id, request.owner)
        return recovered

    def _evaluate(self, run: WorkflowRun, enrichment_context: dict) -> WorkflowRun:
        try:
            result = self.evaluator.evaluate(run.lead, enrichment_context=enrichment_context, correlation_id=run.correlation_id)
        except Exception as exc:
            run.error = {"type": exc.__class__.__name__, "message": str(exc)[:500]}
            return self._persist_transition(run, WorkflowRunStatus.FAILED, "Governed evaluation failed.")
        run.result = result
        run.error = None
        decision = result.policy.decision
        run.execution_authorized = bool(result.policy.authorized_for_outreach)
        if decision == Decision.HUMAN_REVIEW:
            run.execution_authorized = False
            return self._persist_transition(run, WorkflowRunStatus.WAITING_HUMAN_REVIEW, "Deterministic policy requires human review.")
        if decision == Decision.RESEARCH_MORE:
            run.execution_authorized = False
            return self._persist_transition(run, WorkflowRunStatus.WAITING_RESEARCH, "Deterministic policy requires additional evidence.")
        if decision == Decision.BLOCK:
            run.execution_authorized = False
            return self._persist_transition(run, WorkflowRunStatus.COMPLETED, "Deterministic policy blocked external execution.")
        return self._persist_transition(run, WorkflowRunStatus.READY_FOR_EXECUTION, "Deterministic policy authorized the next bounded execution stage.")

    def _persist_transition(self, run: WorkflowRun, status: WorkflowRunStatus, note: str) -> WorkflowRun:
        run = self._transition(run, status, note)
        return self.store.save(run)

    @staticmethod
    def _transition(run: WorkflowRun, status: WorkflowRunStatus, note: str) -> WorkflowRun:
        run.status = status
        run.updated_at = datetime.now(timezone.utc)
        run.revision += 1
        run.history.append(WorkflowHistoryEntry(sequence=len(run.history) + 1, status=status, note=note))
        return run

    @staticmethod
    def _derive_idempotency_key(request: StartLeadWorkflowRequest) -> str:
        canonical = json.dumps(request.model_dump(mode="json"), sort_keys=True, separators=(",", ":"))
        return "wf_" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()
