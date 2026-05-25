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


def test_get_payment_returns_payment_from_client():
    payload = {"amount": 20, "date": "23/04/2025"}
    registry, client = make_registry(get_payment=payload)
    assert registry.get_payment("محمود", "04/2025") == payload
    client.get_payment.assert_called_once_with("محمود", "04/2025")


def test_get_next_distribution_returns_next_slot_from_client():
    slot = {"month": "11/2026", "row": 5}
    registry, client = make_registry(get_next_distribution=slot)
    assert registry.get_next_distribution() == slot
    client.get_next_distribution.assert_called_once_with()


def test_get_distributed_months_returns_list_from_client():
    months = [{"month": "05/2025", "row": 2, "member": "محمود", "amount": 440}]
    registry, client = make_registry(get_distributed_months=months)
    assert registry.get_distributed_months() == months
    client.get_distributed_months.assert_called_once_with()


def test_write_payment_delegates_all_args_to_client():
    registry, client = make_registry()
    registry.write_payment(member="محمود", month="05/2025", date="21/05/2025",
                           amount=20, transfer_type="تحويل")
    client.write_payment.assert_called_once_with(
        member="محمود", month="05/2025", date="21/05/2025",
        amount=20, transfer_type="تحويل",
    )


def test_write_distribution_delegates_all_args_to_client():
    registry, client = make_registry()
    registry.write_distribution(row=5, member="خالد", amount=440, method="حجز")
    client.write_distribution.assert_called_once_with(
        row=5, member="خالد", amount=440, method="حجز",
    )
