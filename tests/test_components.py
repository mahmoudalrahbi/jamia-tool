import pytest
from datetime import date
from unittest.mock import AsyncMock, MagicMock, patch
from src.flows.components import ManualDateModal, DatePickerView


@pytest.mark.asyncio
async def test_manual_date_modal_defaults_to_today():
    modal = ManualDateModal(on_date=AsyncMock())
    assert modal.date_input.default == date.today().strftime("%d/%m/%Y")


@pytest.mark.asyncio
async def test_manual_date_modal_rejects_invalid_date_format():
    on_date = AsyncMock()
    modal = ManualDateModal(on_date=on_date)
    modal.date_input._value = "2025-05-21"

    interaction = MagicMock()
    interaction.response.send_message = AsyncMock()

    await modal.on_submit(interaction)

    on_date.assert_not_called()
    interaction.response.send_message.assert_called_once()
    args = interaction.response.send_message.call_args
    content = args.kwargs.get("content", args.args[0] if args.args else "")
    assert "DD/MM/YYYY" in content or "صيغة" in content
    assert args.kwargs.get("ephemeral") is True


@pytest.mark.asyncio
async def test_manual_date_modal_accepts_valid_date_format():
    on_date = AsyncMock()
    modal = ManualDateModal(on_date=on_date)
    modal.date_input._value = "21/05/2025"

    interaction = MagicMock()
    interaction.response.send_message = AsyncMock()

    await modal.on_submit(interaction)

    on_date.assert_called_once_with(interaction, "21/05/2025")
    interaction.response.send_message.assert_not_called()


@pytest.mark.asyncio
async def test_date_picker_view_sends_timeout_message():
    view = DatePickerView(on_date=AsyncMock())
    view.message = AsyncMock()
    view.message.edit = AsyncMock()

    await view.on_timeout()

    view.message.edit.assert_called_once()
    kwargs = view.message.edit.call_args.kwargs
    assert "انتهت" in kwargs.get("content", "")
