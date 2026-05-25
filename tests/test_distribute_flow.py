import pytest
from unittest.mock import AsyncMock, MagicMock
from src.flows.distribute import build_distribute_confirmation, DistributeContext, MemberSelect, AmountModal


def test_distribute_confirmation_includes_month_member_and_amount():
    msg = build_distribute_confirmation(month="07/2026", member_name="خالد", amount=440)
    assert "07/2026" in msg
    assert "خالد" in msg
    assert "440" in msg


def make_distribute_context():
    registry = MagicMock()
    registry.all.return_value = [{"name": "خالد"}]
    return DistributeContext(registry=registry, dist_row=4, month="11/2026")


@pytest.mark.asyncio
async def test_member_select_sends_amount_modal():
    ctx = make_distribute_context()
    select = MemberSelect(ctx)
    select._values = ["خالد"]

    interaction = MagicMock()
    interaction.response.send_modal = AsyncMock()

    await select.callback(interaction)

    interaction.response.send_modal.assert_called_once()
    modal = interaction.response.send_modal.call_args.args[0]
    assert isinstance(modal, AmountModal)
