from typing import Any, Optional

from pydantic import BaseModel, EmailStr, Field, HttpUrl


class CRMLeadRecord(BaseModel):
    """Provider-neutral lead/contact state sent to a CRM adapter."""

    external_key: str = Field(min_length=1)
    email: EmailStr
    first_name: str = ""
    last_name: str = Field(min_length=1)
    company: str = Field(min_length=1)
    title: Optional[str] = None
    source: Optional[str] = None
    owner_id: Optional[str] = None
    attributes: dict[str, Any] = Field(default_factory=dict)


class CRMUpsertResult(BaseModel):
    provider: str
    record_id: str
    created: bool
    updated: bool
    raw: dict[str, Any] = Field(default_factory=dict)


class NotificationResult(BaseModel):
    provider: str
    delivered: bool
    provider_message_id: Optional[str] = None
    status_code: Optional[int] = None


class EmailMessage(BaseModel):
    to: EmailStr
    subject: str = Field(min_length=1, max_length=998)
    text: str = Field(min_length=1)
    reply_to: Optional[EmailStr] = None


class OutboundWebhook(BaseModel):
    url: HttpUrl
    event_type: str = Field(min_length=1)
    payload: dict[str, Any] = Field(default_factory=dict)
    headers: dict[str, str] = Field(default_factory=dict)
