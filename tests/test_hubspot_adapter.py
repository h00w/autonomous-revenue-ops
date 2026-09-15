import json

import httpx

from src.integrations.crm.hubspot import HubSpotCRMAdapter
from src.integrations.models import CRMLeadRecord


def lead() -> CRMLeadRecord:
    return CRMLeadRecord(
        external_key="lead_001",
        email="ada@example.com",
        first_name="Ada",
        last_name="Lovelace",
        company="Analytical Engines AB",
        title="VP Revenue",
        owner_id="12345",
        attributes={"aro_score": 91, "not_allowed": "drop-me"},
    )


def test_hubspot_create_when_email_not_found():
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        assert request.headers["authorization"] == "Bearer token"
        if request.url.path.endswith("/search"):
            body = json.loads(request.content)
            assert body["filterGroups"][0]["filters"][0]["value"] == "ada@example.com"
            return httpx.Response(200, json={"results": []}, request=request)
        assert request.method == "POST"
        body = json.loads(request.content)
        props = body["properties"]
        assert props["email"] == "ada@example.com"
        assert props["firstname"] == "Ada"
        assert props["lastname"] == "Lovelace"
        assert props["company"] == "Analytical Engines AB"
        assert props["jobtitle"] == "VP Revenue"
        assert props["hubspot_owner_id"] == "12345"
        assert props["aro_score"] == "91"
        assert "not_allowed" not in props
        return httpx.Response(201, json={"id": "hs_001", "properties": props}, request=request)

    client = httpx.Client(transport=httpx.MockTransport(handler))
    adapter = HubSpotCRMAdapter(
        "token",
        client=client,
        allowed_custom_properties={"aro_score"},
    )
    result = adapter.upsert_lead(lead())

    assert result.record_id == "hs_001"
    assert result.created is True
    assert result.updated is False
    assert len(requests) == 2


def test_hubspot_updates_when_email_exists():
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/search"):
            return httpx.Response(
                200,
                json={"results": [{"id": "hs_existing", "properties": {"email": "ada@example.com"}}]},
                request=request,
            )
        assert request.method == "PATCH"
        assert request.url.path.endswith("/crm/v3/objects/contacts/hs_existing")
        return httpx.Response(200, json={"id": "hs_existing"}, request=request)

    adapter = HubSpotCRMAdapter(
        "token",
        client=httpx.Client(transport=httpx.MockTransport(handler)),
    )
    result = adapter.upsert_lead(lead())

    assert result.record_id == "hs_existing"
    assert result.created is False
    assert result.updated is True


def test_hubspot_owner_update_is_bounded_to_owner_property():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "PATCH"
        assert json.loads(request.content) == {"properties": {"hubspot_owner_id": "777"}}
        return httpx.Response(200, json={"id": "hs_001"}, request=request)

    adapter = HubSpotCRMAdapter(
        "token",
        client=httpx.Client(transport=httpx.MockTransport(handler)),
    )
    result = adapter.update_owner("hs_001", "777")
    assert result.updated is True
