from scripts.deployment_contract import validate


def test_reference_deployment_contract_is_hardened():
    assert validate() == []
