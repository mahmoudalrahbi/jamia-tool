import pytest
from unittest.mock import AsyncMock, MagicMock
from src.flows.pay import build_pay_confirmation, execute_payment, PayContext, MemberSelect, MonthSelect, MonthView, ConfirmView, AmountModal


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


@pytest.mark.asyncio
async def test_month_select_shows_confirmation_with_confirm_view():
    ctx = make_pay_context()
    ctx.member_name = "محمود"
    ctx.amount = 20
    select = MonthSelect(ctx, months=["05/2025"])
    select._values = ["05/2025"]

    interaction = MagicMock()
    interaction.response.edit_message = AsyncMock()

    await select.callback(interaction)

    kwargs = interaction.response.edit_message.call_args.kwargs
    assert "محمود" in kwargs["content"]
    assert "05/2025" in kwargs["content"]
    assert isinstance(kwargs["view"], ConfirmView)


@pytest.mark.asyncio
async def test_amount_modal_updates_confirmation_message_with_new_amount():
    ctx = make_pay_context()
    ctx.member_name = "محمود"
    ctx.month = "05/2025"
    ctx.amount = 20
    modal = AmountModal(ctx)
    modal.amount_input._value = "999"

    interaction = MagicMock()
    interaction.response.edit_message = AsyncMock()

    await modal.on_submit(interaction)

    interaction.response.edit_message.assert_called_once()
    kwargs = interaction.response.edit_message.call_args.kwargs
    assert "999" in kwargs["content"]
    assert isinstance(kwargs["view"], ConfirmView)


def make_pay_context(unpaid_months=None, member=None):
    client = MagicMock()
    registry = MagicMock()
    registry.all.return_value = [{"name": "محمود"}]
    registry.get.return_value = member or {"name": "محمود", "shares": 1, "monthly_amount": 20}
    registry.get_unpaid_months.return_value = unpaid_months if unpaid_months is not None else ["05/2025"]
    return PayContext(client=client, registry=registry)


@pytest.mark.asyncio
async def test_member_select_shows_error_when_registry_returns_none():
    ctx = make_pay_context()
    ctx.registry.get.return_value = None
    select = MemberSelect(ctx)
    select._values = ["محمود"]

    interaction = MagicMock()
    interaction.response.edit_message = AsyncMock()

    await select.callback(interaction)

    interaction.response.edit_message.assert_called_once()
    kwargs = interaction.response.edit_message.call_args.kwargs
    assert "عذراً" in kwargs["content"]
    assert kwargs["view"] is None


@pytest.mark.asyncio
async def test_member_select_shows_no_months_message_when_all_paid():
    ctx = make_pay_context(unpaid_months=[])
    select = MemberSelect(ctx)
    select._values = ["محمود"]

    interaction = MagicMock()
    interaction.response.edit_message = AsyncMock()

    await select.callback(interaction)

    kwargs = interaction.response.edit_message.call_args.kwargs
    assert "لا توجد شهور" in kwargs["content"]
    assert kwargs["view"] is None


@pytest.mark.asyncio
async def test_member_select_shows_month_picker_when_member_has_unpaid_months():
    ctx = make_pay_context(unpaid_months=["05/2025"])
    select = MemberSelect(ctx)
    select._values = ["محمود"]

    interaction = MagicMock()
    interaction.response.edit_message = AsyncMock()

    await select.callback(interaction)

    interaction.response.edit_message.assert_called_once()
    kwargs = interaction.response.edit_message.call_args.kwargs
    assert kwargs["content"] == "اختر الشهر:"
    assert isinstance(kwargs["view"], MonthView)
