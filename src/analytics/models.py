from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field


class OperationalSnapshot(BaseModel):
    evidence_class: Literal["measured_runtime"] = "measured_runtime"
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    source_run_count: int = Field(ge=0)
    status_counts: dict[str, int]
    decision_counts: dict[str, int]
    authorized_run_count: int = Field(ge=0)
    completed_with_receipt_count: int = Field(ge=0)
    recovered_run_count: int = Field(ge=0)
    completion_rate: float = Field(ge=0.0, le=1.0)
    failure_rate: float = Field(ge=0.0, le=1.0)
    human_review_rate: float = Field(ge=0.0, le=1.0)
    research_more_rate: float = Field(ge=0.0, le=1.0)
    authorization_rate: float = Field(ge=0.0, le=1.0)
    recovery_rate: float = Field(ge=0.0, le=1.0)
    execution_receipt_rate: float = Field(ge=0.0, le=1.0)
    average_recorded_lifecycle_seconds: float = Field(ge=0.0)
    p95_recorded_lifecycle_seconds: float = Field(ge=0.0)


class BusinessImpactScenario(BaseModel):
    evidence_class: Literal["scenario_input"] = "scenario_input"
    workflows_per_month: int = Field(ge=0)
    manual_minutes_per_workflow: float = Field(ge=0.0)
    automation_rate: float = Field(ge=0.0, le=1.0)
    loaded_hourly_cost: float = Field(ge=0.0)
    automation_cost_per_automated_workflow: float = Field(ge=0.0)
    currency: str = Field(default="USD", min_length=3, max_length=8)


class BusinessImpactProjection(BaseModel):
    evidence_class: Literal["scenario_projection"] = "scenario_projection"
    currency: str
    workflows_per_month: int
    automated_workflows: float
    manual_workflows_remaining: float
    manual_hours_baseline: float
    manual_hours_remaining: float
    hours_avoided: float
    capacity_value: float
    automation_operating_cost: float
    net_capacity_value: float
    assumptions: list[str]
