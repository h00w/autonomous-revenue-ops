from math import ceil
from typing import Literal

from pydantic import BaseModel, Field


class SLOTargets(BaseModel):
    evidence_class: Literal["candidate_slo_target"] = "candidate_slo_target"
    availability_target: float = Field(default=0.995, ge=0.0, le=1.0)
    readiness_target: float = Field(default=0.995, ge=0.0, le=1.0)
    p95_probe_latency_ms_target: float = Field(default=500.0, gt=0.0)


class ProbeSample(BaseModel):
    live_ok: bool
    ready_ok: bool
    live_latency_ms: float = Field(ge=0.0)
    ready_latency_ms: float = Field(ge=0.0)


class SLOReport(BaseModel):
    evidence_class: Literal["live_deployment_probe"] = "live_deployment_probe"
    sample_count: int
    availability: float
    readiness: float
    p95_probe_latency_ms: float
    targets: SLOTargets
    passed: bool
    failures: list[str]


def _nearest_rank_p95(values: list[float]) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = max(0, ceil(0.95 * len(ordered)) - 1)
    return ordered[index]


def evaluate_slo(samples: list[ProbeSample], targets: SLOTargets | None = None) -> SLOReport:
    targets = targets or SLOTargets()
    count = len(samples)
    availability = sum(sample.live_ok for sample in samples) / count if count else 0.0
    readiness = sum(sample.ready_ok for sample in samples) / count if count else 0.0
    p95_latency = _nearest_rank_p95(
        [max(sample.live_latency_ms, sample.ready_latency_ms) for sample in samples]
    )

    failures: list[str] = []
    if availability < targets.availability_target:
        failures.append("availability_below_target")
    if readiness < targets.readiness_target:
        failures.append("readiness_below_target")
    if p95_latency > targets.p95_probe_latency_ms_target:
        failures.append("probe_latency_above_target")
    if count == 0:
        failures.append("no_samples")

    return SLOReport(
        sample_count=count,
        availability=availability,
        readiness=readiness,
        p95_probe_latency_ms=p95_latency,
        targets=targets,
        passed=not failures,
        failures=failures,
    )
