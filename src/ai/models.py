from typing import Any, Optional

from pydantic import BaseModel, Field

from ..models import LeadInput, PolicyResult, Qualification


class ProviderAttempt(BaseModel):
    provider: str
    model: str
    success: bool
    error_kind: Optional[str] = None
    retryable: Optional[bool] = None


class StructuredGenerationRequest(BaseModel):
    system_prompt: str = Field(min_length=1)
    user_prompt: str = Field(min_length=1)
    schema_name: str = Field(min_length=1)
    json_schema: dict[str, Any]
    prompt_id: str = Field(min_length=1)
    prompt_version: str = Field(min_length=1)
    correlation_id: Optional[str] = None
    max_output_tokens: int = Field(default=1200, ge=64, le=32768)


class StructuredGenerationResult(BaseModel):
    provider: str
    model: str
    data: dict[str, Any]
    request_id: Optional[str] = None
    input_tokens: Optional[int] = Field(default=None, ge=0)
    output_tokens: Optional[int] = Field(default=None, ge=0)
    latency_ms: Optional[float] = Field(default=None, ge=0)
    routing_attempts: list[ProviderAttempt] = Field(default_factory=list)


class ResearchOutput(BaseModel):
    summary: str
    evidence: list[str]
    open_questions: list[str]
    risk_flags: list[str]
    confidence: float = Field(ge=0.0, le=1.0)


class QualificationRecommendation(BaseModel):
    score: int = Field(ge=0, le=100)
    confidence: float = Field(ge=0.0, le=1.0)
    icp_fit: int = Field(ge=0, le=100)
    intent: int = Field(ge=0, le=100)
    urgency: int = Field(ge=0, le=100)
    risk_flags: list[str]
    evidence: list[str]
    rationale: str

    def to_domain(self) -> Qualification:
        return Qualification(
            score=self.score,
            confidence=self.confidence,
            icp_fit=self.icp_fit,
            intent=self.intent,
            urgency=self.urgency,
            risk_flags=self.risk_flags,
            evidence=self.evidence,
        )


class OutreachDraftOutput(BaseModel):
    subject: str
    body: str
    personalization_points: list[str]
    compliance_notes: list[str]


class AgentTrace(BaseModel):
    agent: str
    prompt_id: str
    prompt_version: str
    provider: str
    model: str
    routing_attempts: list[ProviderAttempt] = Field(default_factory=list)


class SupervisedLeadResult(BaseModel):
    lead: LeadInput
    research: ResearchOutput
    qualification: Qualification
    qualification_rationale: str
    policy: PolicyResult
    outreach: Optional[OutreachDraftOutput] = None
    traces: list[AgentTrace] = Field(default_factory=list)
