from typing import Optional, Protocol, runtime_checkable

from ..models import CRMLeadRecord, CRMUpsertResult


@runtime_checkable
class CRMAdapter(Protocol):
    """Stable business-facing contract for CRM providers."""

    provider: str

    def find_by_email(self, email: str) -> Optional[CRMUpsertResult]: ...

    def upsert_lead(self, lead: CRMLeadRecord) -> CRMUpsertResult: ...

    def update_owner(self, record_id: str, owner_id: str) -> CRMUpsertResult: ...

    def close(self) -> None: ...
