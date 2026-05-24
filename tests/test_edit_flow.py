import pytest
from unittest.mock import AsyncMock, MagicMock
from src.flows.edit import (
    EditPaymentContext, EditDistributionContext,
    EditPaymentMemberSelect, EditPaymentMonthView,
    EditDistributionMonthSelect, EditDistributionModal,
    EditPaymentAmountModal,
)


@pytest.mark.asyncio
async def test_edit_distribution_month_select_opens_modal_with_prefilled_values():
    client = MagicMock()
    dist_months = [{"month": "05/2025", "row": 2, "member": "محمود", "amount": 440, "method": "حجز"}]
    ctx = EditDistributionContext(client=client)
    select = EditDistributionMonthSelect(ctx, dist_months=dist_months)
    select._values = ["05/2025"]

    interaction = MagicMock()
    interaction.response.send_modal = AsyncMock()

    await select.callback(interaction)

    interaction.response.send_modal.assert_called_once()
    modal = interaction.response.send_modal.call_args.args[0]
    assert isinstance(modal, EditDistributionModal)
    assert modal._ctx.month == "05/2025"
    assert modal._ctx.current_member == "محمود"
    assert modal._ctx.current_amount == 440
    assert modal._ctx.dist_row == 2
    assert modal._ctx.current_method == "حجز"


@pytest.mark.asyncio
async def test_edit_distribution_modal_preserves_method_on_submit():
    client = MagicMock()
    client.write_distribution = MagicMock()
    ctx = EditDistributionContext(
        client=client, dist_row=3, month="05/2025",
        current_member="محمود", current_amount=440, current_method="حجز",
    )
    modal = EditDistributionModal(ctx)
    modal.member_input._value = "محمود"
    modal.amount_input._value = "440"

    interaction = MagicMock()
    interaction.response.edit_message = AsyncMock()

    await modal.on_submit(interaction)

    client.write_distribution.assert_called_once_with(
        row=3, member="محمود", amount=440, method="حجز"
    )


@pytest.mark.asyncio
async def test_edit_distribution_modal_shows_zero_amount_as_string():
    client = MagicMock()
    ctx = EditDistributionContext(client=client, current_amount=0)
    modal = EditDistributionModal(ctx)
    assert modal.amount_input.default == "0"


def make_payment_ctx(paid_months=None):
    client = MagicMock()
    registry = MagicMock()
    registry.all.return_value = [{"name": "محمود"}]
    registry.get_paid_months.return_value = paid_months if paid_months is not None else ["04/2025"]
    return EditPaymentContext(client=client, registry=registry)


@pytest.mark.asyncio
async def test_edit_payment_member_select_shows_no_payments_message_when_none_recorded():
    ctx = make_payment_ctx(paid_months=[])
    select = EditPaymentMemberSelect(ctx)
    select._values = ["محمود"]

    interaction = MagicMock()
    interaction.response.edit_message = AsyncMock()

    await select.callback(interaction)

    kwargs = interaction.response.edit_message.call_args.kwargs
    assert "لا توجد دفعات" in kwargs["content"]
    assert kwargs["view"] is None


@pytest.mark.asyncio
async def test_edit_payment_member_select_shows_month_picker_when_member_has_paid_months():
    ctx = make_payment_ctx(paid_months=["04/2025"])
    select = EditPaymentMemberSelect(ctx)
    select._values = ["محمود"]

    interaction = MagicMock()
    interaction.response.edit_message = AsyncMock()

    await select.callback(interaction)

    kwargs = interaction.response.edit_message.call_args.kwargs
    assert kwargs["content"] == "اختر الشهر:"
    assert isinstance(kwargs["view"], EditPaymentMonthView)
