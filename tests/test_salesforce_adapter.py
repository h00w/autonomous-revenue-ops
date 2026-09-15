import json

import httpx

from src.integrations.crm.salesforce import SalesforceCRMAdapter
from src.integrations.models import CRMLeadRecord


def lead() -> CRMLeadRecord:
    return CRMLeadRecord(
        external_key="lead_sf_001",
        email="grace@example.com",
        first_name="Grace",
        last_name="Hopper",
        company="Compiler Systems AB",
        title="COO",
        source="Website",
        owner_id="005OWNER",
        attributes={"Lead_Score__c": 88, "Unsafe_Field__c": "drop-me"},
    )


def test_salesforce_create_when_email_not_found():
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        assert request.headers["authorization"] == "Bearer sf-token"
        if request.url.path.endswith("/query"):
            assert "/services/data/latest/query" in request.url.path
            query = request.url.params["q"]
            assert "FROM Lead" in query
            assert "grace@example.com" in query
            return httpx.Response(200, json={"totalSize": 0, "records": []}, request=request)
        assert request.method == "POST"
        assert request.url.path.endswith("/services/data/latest/sobjects/Lead/")
        body = json.loads(request.content)
        assert body["Email"] == "grace@example.com"
        assert body["FirstName"] == "Grace"
        assert body["LastName"] == "Hopper"
        assert body["Company"] == "Compiler Systems AB"
        assert body["Title"] == "COO"
        assert body["LeadSource"] == "Website"
        assert body["OwnerId"] == "005OWNER"
        assert body["Lead_Score__c"] == 88
        assert "Unsafe_Field__c" not in body
        return httpx.Response(
            201,
            json={"id": "00Q001", "success": True, "errors": []},
            request=request,
        )

    adapter = SalesforceCRMAdapter(
        "https://example.my.salesforce.com",
        "sf-token",
        client=httpx.Client(transport=httpx.MockTransport(handler)),
        allowed_custom_fields={"Lead_Score__c"},
    )
    result = adapter.upsert_lead(lead())

    assert result.record_id == "00Q001"
    assert result.created is True
    assert result.updated is False
    assert len(requests) == 2


def test_salesforce_updates_existing_lead():
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/query"):
            return httpx.Response(
                200,
                json={
                    "totalSize": 1,
                    "records": [{"Id": "00QEXIST", "Email": "grace@example.com"}],
                },
                request=request,
            )
        assert request.method == "PATCH"
        assert request.url.path.endswith("/services/data/latest/sobjects/Lead/00QEXIST")
        return httpx.Response(204, content=b"", request=request)

    adapter = SalesforceCRMAdapter(
        "https://example.my.salesforce.com",
        "sf-token",
        client=httpx.Client(transport=httpx.MockTransport(handler)),
    )
    result = adapter.upsert_lead(lead())

    assert result.record_id == "00QEXIST"
    assert result.created is False
    assert result.updated is True


def test_salesforce_owner_update_only_writes_owner_id():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "PATCH"
        assert json.loads(request.content) == {"OwnerId": "005NEW"}
        return httpx.Response(204, content=b"", request=request)

    adapter = SalesforceCRMAdapter(
        "https://example.my.salesforce.com",
        "sf-token",
        client=httpx.Client(transport=httpx.MockTransport(handler)),
    )
    result = adapter.update_owner("00Q001", "005NEW")
    assert result.updated is True


def test_salesforce_soql_email_literal_is_escaped():
    seen_query = ""

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal seen_query
        seen_query = request.url.params["q"]
        return httpx.Response(200, json={"records": []}, request=request)

    adapter = SalesforceCRMAdapter(
        "https://example.my.salesforce.com",
        "sf-token",
        client=httpx.Client(transport=httpx.MockTransport(handler)),
    )
    adapter.find_by_email("o'connor@example.com")
    assert "o\\'connor@example.com" in seen_query
