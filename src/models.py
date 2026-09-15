from datetime import datetime, timezone
from enum import Enum
from typing import Any, List, Optional

from pydantic import BaseModel, EmailStr, Field


class Decision(str, Enum):
    AUTO_ROUTE = "AUTO_ROUTE"
    HUMAN_REVIEW = "HUMAN_REVIEW"
    RESEARCH_MORE = "RESEARCH_MORE"
    NURTURE = "NURTURE"
    BLOCK = "BLOCK"


class LeadInput(BaseModel):
    lead_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    email: EmailStr
    company: str = Field(min_length=1)
    role: Optional[str] = None
    source: str = "website"
    message: str = ""
    consent_to_contact: bool = True


class Qualification(BaseModel):
    score: int = Field(ge=0, le=100)
    confidence: float = Field(ge=0.0, le=1.0)
    icp_fit: int = Field(ge=0, le=100)
    intent: int = Field(ge=0, le=100)
    urgency: int = Field(ge=0, le=100)
    risk_flags: List[str] = Field(default_factory=list)
    evidence: List[str] = Field(default_factory=list)


class PolicyResult(BaseModel):
    decision: Decision
    authorized_for_outreach: bool
    reason: str
    next_action: str


class LeadEvaluationRequest(BaseModel):
    lead: LeadInput
    qualification: Qualification


class EventEnvelope(BaseModel):
    event_id: str
    event_type: str
    event_version: str = "1.0"
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    correlation_id: str
    idempotency_key: str
    source: str = "revenue-ops-api"
    payload: dict[str, Any] = Field(default_factory=dict)


class WorkflowTrace(BaseModel):
    event_id: str
    correlation_id: str
    lead: LeadInput
    qualification: Qualification
    policy: PolicyResult


class WorkflowResponse(BaseModel):
    event: EventEnvelope
    policy: PolicyResult
    replayed: bool = False


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    environment: str
    checks: dict[str, str] = Field(default_factory=dict)
