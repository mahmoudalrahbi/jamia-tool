import discord
from discord import ui
from datetime import date, timedelta, datetime
from typing import Callable, Awaitable

DateCallback = Callable[[discord.Interaction, str], Awaitable[None]]

TIMEOUT_MESSAGE = "انتهت صلاحية هذه القائمة، أعد تشغيل الأمر."


class TimeoutView(ui.View):
    """Base view that sends an Arabic timeout message when the view expires."""

    async def on_timeout(self) -> None:
        if self.message:
            await self.message.edit(content=TIMEOUT_MESSAGE, view=None)


class ManualDateModal(ui.Modal, title="أدخل التاريخ"):
    date_input: ui.TextInput = ui.TextInput(
        label="التاريخ",
        placeholder="مثال: 21/05/2025",
        max_length=10,
    )

    def __init__(self, on_date: DateCallback):
        super().__init__()
        self._on_date = on_date
        self.date_input.default = date.today().strftime("%d/%m/%Y")

    async def on_submit(self, interaction: discord.Interaction):
        try:
            datetime.strptime(self.date_input.value, "%d/%m/%Y")
        except ValueError:
            await interaction.response.send_message(
                content="صيغة التاريخ غير صحيحة، استخدم: DD/MM/YYYY (مثال: 21/05/2025)",
                ephemeral=True,
            )
            return
        await self._on_date(interaction, self.date_input.value)


class DatePickerView(TimeoutView):
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
