import httpx
import pytest
from pydantic import SecretStr

from src.config import Settings
from src.integrations.crm.hubspot import HubSpotCRMAdapter
from src.integrations.crm.salesforce import SalesforceCRMAdapter
from src.integrations.factory import build_crm_adapter
from src.integrations.mapping import lead_input_to_crm_record, split_person_name
from src.models import LeadInput


def test_name_mapping_preserves_single_token_name():
    assert split_person_name("Madonna") == ("", "Madonna")
    assert split_person_name("Ada Lovelace") == ("Ada", "Lovelace")
    assert split_person_name("Mary Jane Watson") == ("Mary Jane", "Watson")


def test_lead_input_maps_to_provider_neutral_record():
    lead = LeadInput(
        lead_id="lead_123",
        name="Ada Lovelace",
        email="ada@example.com",
        company="Analytical Engines AB",
        role="VP Revenue",
        source="partner",
    )
    record = lead_input_to_crm_record(lead, owner_id="owner_1", attributes={"score": 90})
    assert record.external_key == "lead_123"
    assert record.first_name == "Ada"
    assert record.last_name == "Lovelace"
    assert record.company == "Analytical Engines AB"
    assert record.title == "VP Revenue"
    assert record.owner_id == "owner_1"
    assert record.attributes["score"] == 90


def test_hubspot_factory_requires_secret():
    with pytest.raises(ValueError, match="HUBSPOT_ACCESS_TOKEN"):
        build_crm_adapter(Settings(environment="test"), "hubspot")


def test_salesforce_factory_requires_instance_and_secret():
    with pytest.raises(ValueError, match="SALESFORCE_INSTANCE_URL"):
        build_crm_adapter(Settings(environment="test"), "salesforce")


def test_factories_build_expected_adapter_types():
    client = httpx.Client(transport=httpx.MockTransport(lambda request: httpx.Response(200, json={}, request=request)))
    hubspot_settings = Settings(
        environment="test",
        hubspot_access_token=SecretStr("hub-token"),
        hubspot_custom_properties="aro_score, aro_segment",
    )
    hubspot = build_crm_adapter(hubspot_settings, "hubspot", client=client)
    assert isinstance(hubspot, HubSpotCRMAdapter)
    assert hubspot.allowed_custom_properties == {"aro_score", "aro_segment"}

    salesforce_settings = Settings(
        environment="test",
        salesforce_instance_url="https://example.my.salesforce.com",
        salesforce_access_token=SecretStr("sf-token"),
        salesforce_custom_fields="Lead_Score__c, Segment__c",
    )
    salesforce = build_crm_adapter(salesforce_settings, "salesforce", client=client)
    assert isinstance(salesforce, SalesforceCRMAdapter)
    assert salesforce.allowed_custom_fields == {"Lead_Score__c", "Segment__c"}


def test_secret_values_are_masked_in_settings_repr():
    settings = Settings(
        environment="test",
        hubspot_access_token=SecretStr("super-secret-token"),
    )
    assert "super-secret-token" not in repr(settings)
