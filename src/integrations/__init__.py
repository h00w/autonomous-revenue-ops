"""Bounded external integration adapters for Autonomous Revenue Ops."""

from .errors import IntegrationError, IntegrationErrorKind
from .models import CRMLeadRecord, CRMUpsertResult, EmailMessage, NotificationResult

__all__ = [
    "CRMLeadRecord",
    "CRMUpsertResult",
    "EmailMessage",
    "IntegrationError",
    "IntegrationErrorKind",
    "NotificationResult",
]
