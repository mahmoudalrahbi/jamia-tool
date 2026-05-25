import pytest
from unittest.mock import AsyncMock, MagicMock
from src.flows.summary import build_summary_message


def make_summary_deps(members=None, paid_months=None, dist_months=None, balances=None):
    registry = MagicMock()

    members = members or [
        {"name": "محمود", "monthly_amount": 20},
        {"name": "خالد", "monthly_amount": 40},
    ]
    registry.all.return_value = members

    paid_months = paid_months or {"محمود": ["04/2025"], "خالد": ["04/2025", "05/2025"]}
    registry.get_paid_months.side_effect = lambda name: paid_months.get(name, [])

    balances = balances or {"محمود": 280, "خالد": 560}
    registry.get_balance.side_effect = lambda name: balances.get(name, 0)

    dist_months = dist_months or [
        {"month": "05/2025", "row": 2, "member": "محمود", "amount": 440},
    ]
    registry.get_distributed_months.return_value = dist_months

    return registry


def test_summary_message_includes_total_collected():
    registry = make_summary_deps()
    msg = build_summary_message(registry)
    assert "840" in msg  # 280 + 560


def test_summary_message_includes_total_distributed():
    registry = make_summary_deps()
    msg = build_summary_message(registry)
    assert "440" in msg


def test_summary_message_includes_remaining_balance():
    registry = make_summary_deps()
    msg = build_summary_message(registry)
    assert "400" in msg  # 840 - 440


def test_summary_message_includes_per_member_payment_status():
    registry = make_summary_deps()
    msg = build_summary_message(registry)
    assert "محمود" in msg
    assert "خالد" in msg
