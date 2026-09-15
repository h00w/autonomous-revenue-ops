from .models import Decision, LeadInput, PolicyResult, Qualification


def evaluate_policy(lead: LeadInput, q: Qualification) -> PolicyResult:
    if not lead.consent_to_contact:
        return PolicyResult(
            decision=Decision.BLOCK,
            authorized_for_outreach=False,
            reason="Contact consent is absent.",
            next_action="Store lead for non-contact analytics only.",
        )

    if q.risk_flags:
        return PolicyResult(
            decision=Decision.HUMAN_REVIEW,
            authorized_for_outreach=False,
            reason="Risk flags require human review before any external action.",
            next_action="Review qualification evidence and risk flags.",
        )

    if q.confidence < 0.70:
        return PolicyResult(
            decision=Decision.RESEARCH_MORE,
            authorized_for_outreach=False,
            reason="Model confidence is below the autonomous-action threshold.",
            next_action="Collect additional evidence and re-run qualification.",
        )

    if q.score >= 80 and q.confidence >= 0.85:
        return PolicyResult(
            decision=Decision.AUTO_ROUTE,
            authorized_for_outreach=True,
            reason="High qualification score and confidence satisfy autonomous routing policy.",
            next_action="Create/update CRM record, assign owner, and prepare outreach.",
        )

    if q.score >= 60:
        return PolicyResult(
            decision=Decision.HUMAN_REVIEW,
            authorized_for_outreach=False,
            reason="Lead is promising but does not satisfy the autonomous-action threshold.",
            next_action="Queue for RevOps review.",
        )

    return PolicyResult(
        decision=Decision.NURTURE,
        authorized_for_outreach=True,
        reason="Lead is valid but currently below the sales-routing threshold.",
        next_action="Place into a low-pressure nurture sequence.",
    )
