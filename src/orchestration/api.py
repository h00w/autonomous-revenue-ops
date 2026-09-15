from typing import Annotated

from fastapi import APIRouter, Header, HTTPException, Request

from .models import (
    ExecutionReceipt,
    HumanApproval,
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
        raise HTTPException(
            status_code=503,
            detail="Workflow AI runtime is not configured; configure at least one dedicated AI provider key.",
        ) from exc


def _run_or_404(run_id: str) -> WorkflowRun:
    try:
        return _orchestrator().get(run_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Workflow run not found") from exc


@router.post("/leads", response_model=WorkflowRunResponse)
def start_lead_workflow(
    body: StartLeadWorkflowRequest,
    request: Request,
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
) -> WorkflowRunResponse:
    return _orchestrator().start(
        body,
        correlation_id=request.state.correlation_id,
        idempotency_key=idempotency_key,
    )


@router.get("/runs/{run_id}", response_model=WorkflowRun)
def get_workflow_run(run_id: str) -> WorkflowRun:
    return _run_or_404(run_id)


@router.post("/runs/{run_id}/approval", response_model=WorkflowRun)
def approve_workflow(run_id: str, body: HumanApproval) -> WorkflowRun:
    _run_or_404(run_id)
    try:
        return _orchestrator().approve(run_id, body)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/runs/{run_id}/resume-research", response_model=WorkflowRun)
def resume_workflow_research(run_id: str, body: ResearchResumeRequest) -> WorkflowRun:
    _run_or_404(run_id)
    try:
        return _orchestrator().resume_research(run_id, body)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/runs/{run_id}/complete", response_model=WorkflowRun)
def complete_workflow_execution(run_id: str, body: ExecutionReceipt) -> WorkflowRun:
    _run_or_404(run_id)
    try:
        return _orchestrator().complete_execution(run_id, body)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
