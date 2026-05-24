import discord
from discord import ui
from src.sheets_client import SheetsClient
from src.member_registry import MemberRegistry
from src.flows.components import DatePickerView


def build_pay_confirmation(member_name: str, month: str, amount: int) -> str:
    return f"تسجيل دفعة لـ **{member_name}** — الشهر: **{month}** — المبلغ: **{amount} ريال**"


async def execute_payment(interaction: discord.Interaction, client: SheetsClient,
                          member_name: str, month: str, date: str, amount: int) -> None:
    client.write_payment(member=member_name, month=month, date=date, amount=amount)
    msg = f"✅ تم تسجيل دفعة **{member_name}** — {month} — {amount} ريال"
    await interaction.response.edit_message(content=msg, view=None)


def _make_date_picker(client: SheetsClient, member_name: str,
                      month: str, amount: int) -> DatePickerView:
    async def on_date(interaction: discord.Interaction, date: str):
        await execute_payment(interaction, client, member_name, month, date, amount)
    return DatePickerView(on_date)


class AmountModal(ui.Modal, title="تعديل المبلغ"):
    amount_input: ui.TextInput = ui.TextInput(
        label="المبلغ",
        placeholder="مثال: 20",
        max_length=6,
    )

    def __init__(self, client: SheetsClient, member_name: str,
                 month: str, default_amount: int):
        super().__init__()
        self._client = client
        self._member_name = member_name
        self._month = month
        self.amount_input.default = str(default_amount)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            amount = int(self.amount_input.value)
        except ValueError:
            await interaction.response.send_message("المبلغ يجب أن يكون رقمًا.", ephemeral=True)
            return
        view = _make_date_picker(self._client, self._member_name, self._month, amount)
        await interaction.response.edit_message(content="اختر تاريخ الدفع:", view=view)


class ConfirmView(ui.View):
    def __init__(self, client: SheetsClient, member_name: str,
                 month: str, amount: int):
        super().__init__()
        self._client = client
        self._member_name = member_name
        self._month = month
        self._amount = amount

    @ui.button(label="تأكيد", style=discord.ButtonStyle.success)
    async def confirm(self, interaction: discord.Interaction, button: ui.Button):
        view = _make_date_picker(self._client, self._member_name, self._month, self._amount)
        await interaction.response.edit_message(content="اختر تاريخ الدفع:", view=view)

    @ui.button(label="تعديل المبلغ", style=discord.ButtonStyle.secondary)
    async def edit_amount(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_modal(
            AmountModal(self._client, self._member_name, self._month, self._amount)
        )


class MonthSelect(ui.Select):
    def __init__(self, client: SheetsClient, member_name: str,
                 amount: int, months: list[str]):
        self._client = client
        self._member_name = member_name
        self._amount = amount
        options = [discord.SelectOption(label=m) for m in months]
        super().__init__(placeholder="اختر الشهر...", options=options)

    async def callback(self, interaction: discord.Interaction):
        month = self.values[0]
        msg = build_pay_confirmation(self._member_name, month, self._amount)
        view = ConfirmView(self._client, self._member_name, month, self._amount)
        await interaction.response.edit_message(content=msg, view=view)


class MonthView(ui.View):
    def __init__(self, client: SheetsClient, member_name: str,
                 amount: int, months: list[str]):
        super().__init__()
        self.add_item(MonthSelect(client, member_name, amount, months))


class MemberSelect(ui.Select):
    def __init__(self, registry: MemberRegistry, client: SheetsClient):
        self._registry = registry
        self._client = client
        options = [discord.SelectOption(label=m["name"]) for m in registry.all()]
        super().__init__(placeholder="اختر العضو...", options=options)

    async def callback(self, interaction: discord.Interaction):
        member_name = self.values[0]
        member = self._registry.get(member_name)
        months = self._client.get_unpaid_months(member_name)

        if not months:
            await interaction.response.edit_message(
                content=f"لا توجد شهور غير مدفوعة لـ **{member_name}**", view=None
            )
            return

        view = MonthView(self._client, member_name, member["monthly_amount"], months)
        await interaction.response.edit_message(content="اختر الشهر:", view=view)


class PayView(ui.View):
    def __init__(self, registry: MemberRegistry, client: SheetsClient):
        super().__init__()
        self.add_item(MemberSelect(registry, client))


async def start_pay(interaction: discord.Interaction,
                    registry: MemberRegistry, client: SheetsClient):
    view = PayView(registry, client)
    await interaction.response.send_message("اختر العضو:", view=view, ephemeral=True)
