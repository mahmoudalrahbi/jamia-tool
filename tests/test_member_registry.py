from unittest.mock import MagicMock
from src.member_registry import MemberRegistry


def make_registry(**client_attrs):
    client = MagicMock()
    client.get_members.return_value = []
    for attr, value in client_attrs.items():
        setattr(client.return_value, attr, value)
        getattr(client, attr).return_value = value
    return MemberRegistry(client), client


def test_get_unpaid_months_returns_months_from_client():
    registry, client = make_registry(get_unpaid_months=["05/2025"])
    assert registry.get_unpaid_months("محمود") == ["05/2025"]
    client.get_unpaid_months.assert_called_once_with("محمود")


def test_get_paid_months_returns_months_from_client():
    registry, client = make_registry(get_paid_months=["04/2025"])
    assert registry.get_paid_months("محمود") == ["04/2025"]
    client.get_paid_months.assert_called_once_with("محمود")


def test_get_balance_returns_total_paid_from_client():
    registry, client = make_registry(get_balance=280)
    assert registry.get_balance("محمود") == 280
    client.get_balance.assert_called_once_with("محمود")
