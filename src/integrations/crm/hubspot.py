from __future__ import annotations

from typing import Iterable, Optional

import httpx

from ..http import BoundedHttpClient
from ..models import CRMLeadRecord, CRMUpsertResult


class HubSpotCRMAdapter:
    """HubSpot CRM v3 contact adapter.

    Business leads are represented as HubSpot contacts. Only stable default
    contact fields plus explicitly allow-listed custom fields are written.
    """

    provider = "hubspot"

    def __init__(
        self,
        access_token: str,
        *,
        base_url: str = "https://api.hubapi.com",
        client: httpx.Client | None = None,
        allowed_custom_properties: Iterable[str] = (),
    ) -> None:
        if not access_token:
            raise ValueError("HubSpot access token is required")
        self.base_url = base_url.rstrip("/")
        self.allowed_custom_properties = set(allowed_custom_properties)
        self.http = BoundedHttpClient(self.provider, client=client)
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

    def close(self) -> None:
        self.http.close()

    def find_by_email(self, email: str) -> Optional[CRMUpsertResult]:
        payload = {
            "filterGroups": [
                {
                    "filters": [
                        {
                            "propertyName": "email",
                            "operator": "EQ",
                            "value": email,
                        }
                    ]
                }
            ],
            "properties": [
                "email",
                "firstname",
                "lastname",
                "company",
                "jobtitle",
                "hubspot_owner_id",
            ],
            "limit": 1,
        }
        data = self.http.request_json(
            "POST",
            f"{self.base_url}/crm/v3/objects/contacts/search",
            headers=self.headers,
            json=payload,
            expected_statuses={200},
        )
        results = data.get("results") or []
        if not results:
            return None
        record = results[0]
        return CRMUpsertResult(
            provider=self.provider,
            record_id=str(record["id"]),
            created=False,
            updated=False,
            raw=record,
        )

    def upsert_lead(self, lead: CRMLeadRecord) -> CRMUpsertResult:
        existing = self.find_by_email(str(lead.email))
        properties = self._properties(lead)
        if existing is None:
            data = self.http.request_json(
                "POST",
                f"{self.base_url}/crm/v3/objects/contacts",
                headers=self.headers,
                json={"properties": properties},
                expected_statuses={200, 201},
            )
            return CRMUpsertResult(
                provider=self.provider,
                record_id=str(data["id"]),
                created=True,
                updated=False,
                raw=data,
            )

        data = self.http.request_json(
            "PATCH",
            f"{self.base_url}/crm/v3/objects/contacts/{existing.record_id}",
            headers=self.headers,
            json={"properties": properties},
            expected_statuses={200},
        )
        return CRMUpsertResult(
            provider=self.provider,
            record_id=existing.record_id,
            created=False,
            updated=True,
            raw=data,
        )

    def update_owner(self, record_id: str, owner_id: str) -> CRMUpsertResult:
        data = self.http.request_json(
            "PATCH",
            f"{self.base_url}/crm/v3/objects/contacts/{record_id}",
            headers=self.headers,
            json={"properties": {"hubspot_owner_id": owner_id}},
            expected_statuses={200},
        )
        return CRMUpsertResult(
            provider=self.provider,
            record_id=record_id,
            created=False,
            updated=True,
            raw=data,
        )

    def _properties(self, lead: CRMLeadRecord) -> dict[str, str]:
        properties: dict[str, str] = {
            "email": str(lead.email),
            "firstname": lead.first_name,
            "lastname": lead.last_name,
            "company": lead.company,
        }
        if lead.title:
            properties["jobtitle"] = lead.title
        if lead.owner_id:
            properties["hubspot_owner_id"] = lead.owner_id
        for key in self.allowed_custom_properties:
            value = lead.attributes.get(key)
            if value is not None:
                properties[key] = str(value)
        return {key: value for key, value in properties.items() if value != ""}
