import discord
import gspread
from typing import Awaitable


async def handle_command_error(interaction: discord.Interaction, coro: Awaitable) -> None:
    try:
        await coro
    except gspread.exceptions.GSpreadException:
        await interaction.response.send_message(
            content="حدث خطأ أثناء الاتصال بالجداول، حاول مرة أخرى.",
            ephemeral=True,
        )
