from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Request

from ..security.auth import require_workflow_api_key
from .models import (
    ExecutionClaimRequest,
    ExecutionReceipt,
    HumanApproval,
    RecoveryRequest,
    ResearchResumeRequest,
    StartLeadWorkflowRequest,
    WorkflowRun,
    WorkflowRunResponse,
)
from .runtime import get_workflow_orchestrator

router = APIRouter(prefix="/v1/workflows", tags=["workflows"])


def _orchestrator():
    try:
        return get_workflow_orchestrator()
    except ValueError as exc:
        raise HTTPException(status_code=503, detail="Workflow AI runtime is not configured; configure at least one dedicated AI provider key.") from exc


def _run_or_404(run_id: str) -> WorkflowRun:
    try:
        return _orchestrator().get(run_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Workflow run not found") from exc


@router.post("/leads", response_model=WorkflowRunResponse, dependencies=[Depends(require_workflow_api_key)])
def start_lead_workflow(body: StartLeadWorkflowRequest, request: Request, idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None) -> WorkflowRunResponse:
    return _orchestrator().start(body, correlation_id=request.state.correlation_id, idempotency_key=idempotency_key)


@router.get("/runs/{run_id}", response_model=WorkflowRun, dependencies=[Depends(require_workflow_api_key)])
def get_workflow_run(run_id: str) -> WorkflowRun:
    return _run_or_404(run_id)


@router.post("/runs/{run_id}/approval", response_model=WorkflowRun, dependencies=[Depends(require_workflow_api_key)])
def approve_workflow(run_id: str, body: HumanApproval) -> WorkflowRun:
    _run_or_404(run_id)
    try:
        return _orchestrator().approve(run_id, body)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/runs/{run_id}/resume-research", response_model=WorkflowRun, dependencies=[Depends(require_workflow_api_key)])
def resume_workflow_research(run_id: str, body: ResearchResumeRequest) -> WorkflowRun:
    _run_or_404(run_id)
    try:
        return _orchestrator().resume_research(run_id, body)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/runs/{run_id}/claim", response_model=WorkflowRun, dependencies=[Depends(require_workflow_api_key)])
def claim_workflow_execution(run_id: str, body: ExecutionClaimRequest) -> WorkflowRun:
    _run_or_404(run_id)
    try:
        return _orchestrator().claim_execution(run_id, body)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/runs/{run_id}/complete", response_model=WorkflowRun, dependencies=[Depends(require_workflow_api_key)])
def complete_workflow_execution(run_id: str, body: ExecutionReceipt) -> WorkflowRun:
    _run_or_404(run_id)
    try:
        return _orchestrator().complete_execution(run_id, body)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/recover", response_model=list[WorkflowRun], dependencies=[Depends(require_workflow_api_key)])
def recover_stalled_workflows(body: RecoveryRequest) -> list[WorkflowRun]:
    return _orchestrator().recover_stalled(body)
