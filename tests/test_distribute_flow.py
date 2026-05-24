import pytest
from unittest.mock import AsyncMock, MagicMock
from src.flows.distribute import build_distribute_confirmation


def test_distribute_confirmation_includes_month_member_and_amount():
    msg = build_distribute_confirmation(month="07/2026", member_name="خالد", amount=440)
    assert "07/2026" in msg
    assert "خالد" in msg
    assert "440" in msg
