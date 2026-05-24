from unittest.mock import MagicMock
from src.flows.balance import build_balance_reply


def make_registry(balances: dict):
    registry = MagicMock()
    registry.get_balance.side_effect = lambda name: balances[name]
    return registry


def test_balance_reply_formats_correctly():
    registry = make_registry({"محمود": 280, "خالد": 560})
    message = build_balance_reply(member_name="محمود", registry=registry)
    assert "محمود" in message
    assert "280" in message


def test_balance_reply_for_member_with_two_shares():
    registry = make_registry({"خالد": 560})
    message = build_balance_reply(member_name="خالد", registry=registry)
    assert "خالد" in message
    assert "560" in message


def test_balance_reply_calls_registry_with_correct_name():
    registry = make_registry({"محمود": 280})
    build_balance_reply(member_name="محمود", registry=registry)
    registry.get_balance.assert_called_once_with("محمود")
