import discord
from discord import ui
from datetime import date, timedelta
from typing import Callable, Awaitable

DateCallback = Callable[[discord.Interaction, str], Awaitable[None]]


class ManualDateModal(ui.Modal, title="أدخل التاريخ"):
    date_input: ui.TextInput = ui.TextInput(
        label="التاريخ",
        placeholder="مثال: 21/05/2025",
        max_length=10,
    )

    def __init__(self, on_date: DateCallback):
        super().__init__()
        self._on_date = on_date

    async def on_submit(self, interaction: discord.Interaction):
        await self._on_date(interaction, self.date_input.value)


class DatePickerView(ui.View):
    """Three-button date picker: today / yesterday / manual entry."""

    def __init__(self, on_date: DateCallback):
        super().__init__()
        self._on_date = on_date

    @ui.button(label="اليوم", style=discord.ButtonStyle.success)
    async def today(self, interaction: discord.Interaction, button: ui.Button):
        await self._on_date(interaction, date.today().strftime("%d/%m/%Y"))

    @ui.button(label="أمس", style=discord.ButtonStyle.secondary)
    async def yesterday(self, interaction: discord.Interaction, button: ui.Button):
        d = date.today() - timedelta(days=1)
        await self._on_date(interaction, d.strftime("%d/%m/%Y"))

    @ui.button(label="تاريخ آخر", style=discord.ButtonStyle.secondary)
    async def other(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_modal(ManualDateModal(self._on_date))
