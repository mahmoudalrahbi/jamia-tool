import pytest
from unittest.mock import AsyncMock, MagicMock
import gspread
from src.command_error import handle_command_error


@pytest.mark.asyncio
async def test_handle_command_error_sends_arabic_message_on_gspread_error():
    interaction = MagicMock()
    interaction.response.send_message = AsyncMock()

    async def failing_command():
        raise gspread.exceptions.APIError(MagicMock())

    await handle_command_error(interaction, failing_command())

    interaction.response.send_message.assert_called_once()
    args = interaction.response.send_message.call_args
    assert "خطأ" in args.kwargs.get("content", args.args[0] if args.args else "")
    assert args.kwargs.get("ephemeral") is True


@pytest.mark.asyncio
async def test_handle_command_error_does_not_interfere_with_successful_commands():
    interaction = MagicMock()
    interaction.response.send_message = AsyncMock()

    called = []

    async def successful_command():
        called.append(True)

    await handle_command_error(interaction, successful_command())

    assert called == [True]
    interaction.response.send_message.assert_not_called()
