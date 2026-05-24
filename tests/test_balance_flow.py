import pytest
from unittest.mock import AsyncMock, MagicMock
from src.flows.balance import build_balance_reply


def make_registry(members):
    registry = MagicMock()
    registry.all.return_value = members
    return registry


def make_client(balances: dict):
    client = MagicMock()
    client.get_balance.side_effect = lambda name: balances[name]
    return client


def test_balance_reply_formats_correctly():
    client = make_client({"محمود": 280, "خالد": 560})
    message = build_balance_reply(member_name="محمود", client=client)
    assert "محمود" in message
    assert "280" in message


def test_balance_reply_for_member_with_two_shares():
    client = make_client({"خالد": 560})
    message = build_balance_reply(member_name="خالد", client=client)
    assert "خالد" in message
    assert "560" in message


def test_balance_reply_calls_client_with_correct_name():
    client = make_client({"محمود": 280})
    build_balance_reply(member_name="محمود", client=client)
    client.get_balance.assert_called_once_with("محمود")
