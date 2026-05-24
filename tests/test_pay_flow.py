import pytest
from unittest.mock import AsyncMock, MagicMock
from src.flows.pay import build_pay_confirmation, execute_payment


def test_pay_confirmation_includes_member_month_and_amount():
    msg = build_pay_confirmation(member_name="محمود", month="يناير 2026", amount=20)
    assert "محمود" in msg
    assert "يناير 2026" in msg
    assert "20" in msg


@pytest.mark.asyncio
async def test_execute_payment_calls_write_payment_with_correct_args():
    client = MagicMock()
    interaction = MagicMock()
    interaction.response.edit_message = AsyncMock()

    await execute_payment(
        interaction=interaction,
        client=client,
        member_name="محمود",
        month="05/2025",
        date="21/05/2025",
        amount=20,
    )

    client.write_payment.assert_called_once_with(
        member="محمود",
        month="05/2025",
        date="21/05/2025",
        amount=20,
    )
