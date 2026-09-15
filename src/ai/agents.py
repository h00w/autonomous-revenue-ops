import json
from uuid import uuid4

from .models import (
    AgentTrace,
    OutreachDraftOutput,
    QualificationRecommendation,
    ResearchOutput,
    StructuredGenerationRequest,
)
from .prompts import OUTREACH_PROMPT, QUALIFICATION_PROMPT, RESEARCH_PROMPT, PromptTemplate
from .router import ModelRouter
from .schema import strict_model_schema
from ..models import LeadInput, PolicyResult, Qualification


def _untrusted(payload: dict) -> str:
    return "<untrusted_data>\n" + json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n</untrusted_data>"


class _AgentBase:
    name: str
    prompt: PromptTemplate
    output_type: type

    def __init__(self, router: ModelRouter) -> None:
        self.router = router

    def _run(self, payload: dict, *, correlation_id: str | None = None):
        correlation_id = correlation_id or f"corr_{uuid4().hex}"
        request = StructuredGenerationRequest(
            system_prompt=self.prompt.system_prompt,
            user_prompt=_untrusted(payload),
            schema_name=self.output_type.__name__,
            json_schema=strict_model_schema(self.output_type),
            prompt_id=self.prompt.prompt_id,
            prompt_version=self.prompt.version,
            correlation_id=correlation_id,
        )
        typed, raw = self.router.generate_typed(request, self.output_type)
        trace = AgentTrace(
            agent=self.name,
            prompt_id=self.prompt.prompt_id,
            prompt_version=self.prompt.version,
            provider=raw.provider,
            model=raw.model,
            routing_attempts=raw.routing_attempts,
        )
        return typed, trace


class ResearchAgent(_AgentBase):
    name = "research"
    prompt = RESEARCH_PROMPT
    output_type = ResearchOutput

    def run(
        self,
        lead: LeadInput,
        *,
        enrichment_context: dict | None = None,
        correlation_id: str | None = None,
    ) -> tuple[ResearchOutput, AgentTrace]:
        return self._run(
            {"lead": lead.model_dump(mode="json"), "enrichment_context": enrichment_context or {}},
            correlation_id=correlation_id,
        )


class QualificationAgent(_AgentBase):
    name = "qualification"
    prompt = QUALIFICATION_PROMPT
    output_type = QualificationRecommendation

    def run(
        self,
        lead: LeadInput,
        research: ResearchOutput,
        *,
        correlation_id: str | None = None,
    ) -> tuple[QualificationRecommendation, AgentTrace]:
        return self._run(
            {"lead": lead.model_dump(mode="json"), "research": research.model_dump(mode="json")},
            correlation_id=correlation_id,
        )


class OutreachDraftingAgent(_AgentBase):
    name = "outreach"
    prompt = OUTREACH_PROMPT
    output_type = OutreachDraftOutput

    def run(
        self,
        lead: LeadInput,
        research: ResearchOutput,
        qualification: Qualification,
        policy: PolicyResult,
        *,
        correlation_id: str | None = None,
    ) -> tuple[OutreachDraftOutput, AgentTrace]:
        if not policy.authorized_for_outreach:
            raise PermissionError("Deterministic policy did not authorize outreach drafting")
        return self._run(
            {
                "policy_authorized": True,
                "lead": lead.model_dump(mode="json"),
                "research": research.model_dump(mode="json"),
                "qualification": qualification.model_dump(mode="json"),
                "policy": policy.model_dump(mode="json"),
            },
            correlation_id=correlation_id,
        )
