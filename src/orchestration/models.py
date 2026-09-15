from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional
from uuid import uuid4

from pydantic import BaseModel, Field

from ..ai.models import SupervisedLeadResult
from ..models import LeadInput


class WorkflowRunStatus(str, Enum):
    RECEIVED = "RECEIVED"
    RUNNING = "RUNNING"
    WAITING_HUMAN_REVIEW = "WAITING_HUMAN_REVIEW"
    WAITING_RESEARCH = "WAITING_RESEARCH"
    READY_FOR_EXECUTION = "READY_FOR_EXECUTION"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class WorkflowHistoryEntry(BaseModel):
    sequence: int = Field(ge=1)
    status: WorkflowRunStatus
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    note: str = ""


class StartLeadWorkflowRequest(BaseModel):
    lead: LeadInput
    enrichment_context: dict[str, Any] = Field(default_factory=dict)


class ResearchResumeRequest(BaseModel):
    enrichment_context: dict[str, Any] = Field(default_factory=dict)


class HumanApproval(BaseModel):
    approved: bool
    reviewer: str = Field(min_length=1)
    note: str = ""


class ExecutionClaimRequest(BaseModel):
    owner: str = Field(min_length=1)
    ttl_seconds: int = Field(default=60, ge=5, le=3600)


class ExecutionClaim(BaseModel):
    claim_id: str = Field(default_factory=lambda: f"claim_{uuid4().hex}")
    owner: str
    expires_at: datetime


class ExecutionReceipt(BaseModel):
    executor: str = Field(min_length=1)
    external_refs: dict[str, str] = Field(default_factory=dict)
    note: str = ""
    claim_id: Optional[str] = None


class RecoveryRequest(BaseModel):
    owner: str = Field(min_length=1)
    lease_ttl_seconds: int = Field(default=60, ge=5, le=3600)
    max_runs: int = Field(default=100, ge=1, le=1000)


class WorkflowRun(BaseModel):
    run_id: str
    workflow_name: str = "lead-revenue-ops"
    workflow_version: str = "1.1.0"
    correlation_id: str
    idempotency_key: str
    status: WorkflowRunStatus
    lead: LeadInput
    enrichment_context: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    revision: int = Field(default=0, ge=0)
    recovery_attempts: int = Field(default=0, ge=0)
    result: Optional[SupervisedLeadResult] = None
    human_approval: Optional[HumanApproval] = None
    execution_authorized: bool = False
    execution_claim: Optional[ExecutionClaim] = None
    execution_receipt: Optional[ExecutionReceipt] = None
    error: Optional[dict[str, Any]] = None
    history: list[WorkflowHistoryEntry] = Field(default_factory=list)


class WorkflowRunResponse(BaseModel):
    run: WorkflowRun
    replayed: bool = False
