from .base import CRMAdapter
from .hubspot import HubSpotCRMAdapter
from .salesforce import SalesforceCRMAdapter

__all__ = ["CRMAdapter", "HubSpotCRMAdapter", "SalesforceCRMAdapter"]
