from uuid import uuid4

from .agents import OutreachDraftingAgent, QualificationAgent, ResearchAgent
from .models import SupervisedLeadResult
from .router import ModelRouter
from ..models import LeadInput
from ..policy import evaluate_policy


class RevenueOpsSupervisor:
    """Coordinates AI recommendations while preserving deterministic authorization."""

    def __init__(self, router: ModelRouter) -> None:
        self.router = router
        self.research_agent = ResearchAgent(router)
        self.qualification_agent = QualificationAgent(router)
        self.outreach_agent = OutreachDraftingAgent(router)

    def evaluate(
        self,
        lead: LeadInput,
        *,
        enrichment_context: dict | None = None,
        correlation_id: str | None = None,
    ) -> SupervisedLeadResult:
        correlation_id = correlation_id or f"corr_{uuid4().hex}"
        research, research_trace = self.research_agent.run(
            lead,
            enrichment_context=enrichment_context,
            correlation_id=correlation_id,
        )
        recommendation, qualification_trace = self.qualification_agent.run(
            lead,
            research,
            correlation_id=correlation_id,
        )
        qualification = recommendation.to_domain()
        policy = evaluate_policy(lead, qualification)
        traces = [research_trace, qualification_trace]
        outreach = None

        if policy.authorized_for_outreach:
            outreach, outreach_trace = self.outreach_agent.run(
                lead,
                research,
                qualification,
                policy,
                correlation_id=correlation_id,
            )
            traces.append(outreach_trace)

        return SupervisedLeadResult(
            lead=lead,
            research=research,
            qualification=qualification,
            qualification_rationale=recommendation.rationale,
            policy=policy,
            outreach=outreach,
            traces=traces,
        )
