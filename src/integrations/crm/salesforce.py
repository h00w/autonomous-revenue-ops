from __future__ import annotations

from typing import Iterable, Optional

import httpx

from ..http import BoundedHttpClient
from ..models import CRMLeadRecord, CRMUpsertResult


def _escape_soql_literal(value: str) -> str:
    return value.replace("\\", "\\\\").replace("'", "\\'")


class SalesforceCRMAdapter:
    """Salesforce REST adapter using the standard Lead sObject.

    The `latest` REST API alias is used so the adapter does not pin a stale API
    number. Production organizations can override `api_root` if they require a
    fixed version for change-control reasons.
    """

    provider = "salesforce"

    def __init__(
        self,
        instance_url: str,
        access_token: str,
        *,
        api_root: str = "/services/data/latest",
        client: httpx.Client | None = None,
        allowed_custom_fields: Iterable[str] = (),
    ) -> None:
        if not instance_url.startswith("https://"):
            raise ValueError("Salesforce instance_url must use https://")
        if not access_token:
            raise ValueError("Salesforce access token is required")
        self.instance_url = instance_url.rstrip("/")
        self.api_root = "/" + api_root.strip("/")
        self.allowed_custom_fields = set(allowed_custom_fields)
        self.http = BoundedHttpClient(self.provider, client=client)
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

    @property
    def base_url(self) -> str:
        return f"{self.instance_url}{self.api_root}"

    def close(self) -> None:
        self.http.close()

    def find_by_email(self, email: str) -> Optional[CRMUpsertResult]:
        escaped = _escape_soql_literal(email)
        query = (
            "SELECT Id, Email, FirstName, LastName, Company, Title, LeadSource, OwnerId "
            f"FROM Lead WHERE Email = '{escaped}' LIMIT 1"
        )
        data = self.http.request_json(
            "GET",
            f"{self.base_url}/query",
            headers=self.headers,
            params={"q": query},
            expected_statuses={200},
        )
        records = data.get("records") or []
        if not records:
            return None
        record = records[0]
        return CRMUpsertResult(
            provider=self.provider,
            record_id=str(record["Id"]),
            created=False,
            updated=False,
            raw=record,
        )

    def upsert_lead(self, lead: CRMLeadRecord) -> CRMUpsertResult:
        existing = self.find_by_email(str(lead.email))
        fields = self._fields(lead)
        if existing is None:
            data = self.http.request_json(
                "POST",
                f"{self.base_url}/sobjects/Lead/",
                headers=self.headers,
                json=fields,
                expected_statuses={201},
            )
            return CRMUpsertResult(
                provider=self.provider,
                record_id=str(data["id"]),
                created=True,
                updated=False,
                raw=data,
            )

        self.http.request(
            "PATCH",
            f"{self.base_url}/sobjects/Lead/{existing.record_id}",
            headers=self.headers,
            json=fields,
            expected_statuses={204},
        )
        return CRMUpsertResult(
            provider=self.provider,
            record_id=existing.record_id,
            created=False,
            updated=True,
            raw={},
        )

    def update_owner(self, record_id: str, owner_id: str) -> CRMUpsertResult:
        self.http.request(
            "PATCH",
            f"{self.base_url}/sobjects/Lead/{record_id}",
            headers=self.headers,
            json={"OwnerId": owner_id},
            expected_statuses={204},
        )
        return CRMUpsertResult(
            provider=self.provider,
            record_id=record_id,
            created=False,
            updated=True,
            raw={},
        )

    def _fields(self, lead: CRMLeadRecord) -> dict[str, object]:
        fields: dict[str, object] = {
            "Email": str(lead.email),
            "FirstName": lead.first_name,
            "LastName": lead.last_name,
            "Company": lead.company,
        }
        if lead.title:
            fields["Title"] = lead.title
        if lead.source:
            fields["LeadSource"] = lead.source
        if lead.owner_id:
            fields["OwnerId"] = lead.owner_id
        for key in self.allowed_custom_fields:
            value = lead.attributes.get(key)
            if value is not None:
                fields[key] = value
        return {key: value for key, value in fields.items() if value not in (None, "")}
