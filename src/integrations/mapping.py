from typing import Any

from ..models import LeadInput
from .models import CRMLeadRecord


def split_person_name(name: str) -> tuple[str, str]:
    """Split a display name without inventing missing identity data.

    A single-token name is kept as the required last name and leaves first name
    empty, which is compatible with both HubSpot contacts and Salesforce Leads.
    """

    parts = [part for part in name.strip().split() if part]
    if not parts:
        raise ValueError("Lead name must not be blank")
    if len(parts) == 1:
        return "", parts[0]
    return " ".join(parts[:-1]), parts[-1]


def lead_input_to_crm_record(
    lead: LeadInput,
    *,
    owner_id: str | None = None,
    attributes: dict[str, Any] | None = None,
) -> CRMLeadRecord:
    first_name, last_name = split_person_name(lead.name)
    return CRMLeadRecord(
        external_key=lead.lead_id,
        email=lead.email,
        first_name=first_name,
        last_name=last_name,
        company=lead.company,
        title=lead.role,
        source=lead.source,
        owner_id=owner_id,
        attributes=attributes or {},
    )
