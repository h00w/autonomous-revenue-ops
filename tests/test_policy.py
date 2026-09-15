from src.models import Decision, LeadInput, Qualification
from src.policy import evaluate_policy


def lead(consent=True):
    return LeadInput(
        lead_id="lead_test",
        name="Jane Doe",
        email="jane@example.com",
        company="Example AB",
        role="VP Engineering",
        consent_to_contact=consent,
    )


def q(score=87, confidence=0.91, risk_flags=None):
    return Qualification(
        score=score,
        confidence=confidence,
        icp_fit=90,
        intent=82,
        urgency=70,
        risk_flags=risk_flags or [],
        evidence=["synthetic test evidence"],
    )


def test_auto_route_high_quality_lead():
    result = evaluate_policy(lead(), q())
    assert result.decision == Decision.AUTO_ROUTE
    assert result.authorized_for_outreach is True


def test_medium_score_requires_human_review():
    result = evaluate_policy(lead(), q(score=70, confidence=0.90))
    assert result.decision == Decision.HUMAN_REVIEW
    assert result.authorized_for_outreach is False


def test_low_confidence_requests_more_research():
    result = evaluate_policy(lead(), q(score=90, confidence=0.60))
    assert result.decision == Decision.RESEARCH_MORE


def test_risk_flags_override_high_score():
    result = evaluate_policy(lead(), q(score=95, confidence=0.99, risk_flags=["regulated_data"]))
    assert result.decision == Decision.HUMAN_REVIEW
    assert result.authorized_for_outreach is False


def test_no_consent_blocks_outreach():
    result = evaluate_policy(lead(consent=False), q())
    assert result.decision == Decision.BLOCK
    assert result.authorized_for_outreach is False


def test_low_score_enters_nurture():
    result = evaluate_policy(lead(), q(score=45, confidence=0.90))
    assert result.decision == Decision.NURTURE
    assert result.authorized_for_outreach is True
