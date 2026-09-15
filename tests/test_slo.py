from src.operations.slo import ProbeSample, SLOTargets, evaluate_slo


def sample(live: bool = True, ready: bool = True, latency: float = 100.0) -> ProbeSample:
    return ProbeSample(
        live_ok=live,
        ready_ok=ready,
        live_latency_ms=latency,
        ready_latency_ms=latency,
    )


def test_slo_report_passes_for_healthy_samples():
    report = evaluate_slo([sample() for _ in range(20)])
    assert report.evidence_class == "live_deployment_probe"
    assert report.availability == 1.0
    assert report.readiness == 1.0
    assert report.p95_probe_latency_ms == 100.0
    assert report.passed is True


def test_slo_report_fails_when_availability_or_latency_misses_target():
    samples = [sample() for _ in range(19)] + [sample(live=False, ready=False, latency=900.0)]
    report = evaluate_slo(samples, SLOTargets(availability_target=0.99, readiness_target=0.99, p95_probe_latency_ms_target=500.0))
    assert report.passed is False
    assert "availability_below_target" in report.failures
    assert "readiness_below_target" in report.failures
    assert "probe_latency_above_target" in report.failures


def test_empty_probe_set_never_claims_slo_success():
    report = evaluate_slo([])
    assert report.passed is False
    assert "no_samples" in report.failures
