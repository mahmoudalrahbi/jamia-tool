import discord
from discord import ui
from src.sheets_client import SheetsClient
from src.member_registry import MemberRegistry
from src.flows.components import DatePickerView


# ── Edit Payment ──────────────────────────────────────────────────────────────

def _make_payment_date_picker(client: SheetsClient, member_name: str,
                               month: str, amount: int) -> DatePickerView:
    async def on_date(interaction: discord.Interaction, date: str):
        client.write_payment(member=member_name, month=month, date=date, amount=amount)
        msg = f"✅ تم تعديل دفعة **{member_name}** — {month} — {amount} ريال"
        await interaction.response.edit_message(content=msg, view=None)
    return DatePickerView(on_date)


class EditPaymentAmountModal(ui.Modal, title="تعديل المبلغ"):
    amount_input: ui.TextInput = ui.TextInput(label="المبلغ", max_length=6)

    def __init__(self, client: SheetsClient, member_name: str,
                 month: str, current_amount: int):
        super().__init__()
        self._client = client
        self._member_name = member_name
        self._month = month
        self.amount_input.default = str(current_amount)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            amount = int(self.amount_input.value)
        except ValueError:
            await interaction.response.send_message("المبلغ يجب أن يكون رقمًا.", ephemeral=True)
            return
        view = _make_payment_date_picker(self._client, self._member_name, self._month, amount)
        await interaction.response.edit_message(content="اختر تاريخ الدفع:", view=view)


class EditPaymentMonthSelect(ui.Select):
    def __init__(self, client: SheetsClient, member_name: str, months: list[str]):
        self._client = client
        self._member_name = member_name
        options = [discord.SelectOption(label=m) for m in months]
        super().__init__(placeholder="اختر الشهر...", options=options)

    async def callback(self, interaction: discord.Interaction):
        month = self.values[0]
        payment = self._client.get_payment(self._member_name, month)
        modal = EditPaymentAmountModal(
            self._client, self._member_name, month, payment["amount"]
        )
        await interaction.response.send_modal(modal)


class EditPaymentMonthView(ui.View):
    def __init__(self, client: SheetsClient, member_name: str, months: list[str]):
        super().__init__()
        self.add_item(EditPaymentMonthSelect(client, member_name, months))


class EditPaymentMemberSelect(ui.Select):
    def __init__(self, registry: MemberRegistry, client: SheetsClient):
        self._registry = registry
        self._client = client
        options = [discord.SelectOption(label=m["name"]) for m in registry.all()]
        super().__init__(placeholder="اختر العضو...", options=options)

    async def callback(self, interaction: discord.Interaction):
        member_name = self.values[0]
        months = self._client.get_paid_months(member_name)
        if not months:
            await interaction.response.edit_message(
                content=f"لا توجد دفعات مسجلة لـ **{member_name}**", view=None
            )
            return
        view = EditPaymentMonthView(self._client, member_name, months)
        await interaction.response.edit_message(content="اختر الشهر:", view=view)


class EditPaymentMemberView(ui.View):
    def __init__(self, registry: MemberRegistry, client: SheetsClient):
        super().__init__()
        self.add_item(EditPaymentMemberSelect(registry, client))


# ── Edit Distribution ─────────────────────────────────────────────────────────

class EditDistributionModal(ui.Modal, title="تعديل التوزيع"):
    member_input: ui.TextInput = ui.TextInput(label="المستفيد", max_length=50)
    amount_input: ui.TextInput = ui.TextInput(label="المبلغ", max_length=6)

    def __init__(self, client: SheetsClient, dist_row: int, month: str,
                 current_member: str, current_amount: int):
        super().__init__()
        self._client = client
        self._dist_row = dist_row
        self._month = month
        self.member_input.default = current_member
        self.amount_input.default = str(current_amount) if current_amount else ""

    async def on_submit(self, interaction: discord.Interaction):
        try:
            amount = int(self.amount_input.value)
        except ValueError:
            await interaction.response.send_message("المبلغ يجب أن يكون رقمًا.", ephemeral=True)
            return
        self._client.write_distribution(
            row=self._dist_row,
            member=self.member_input.value,
            amount=amount,
        )
        msg = f"✅ تم تعديل توزيع {self._month} — {self.member_input.value} — {amount} ريال"
        await interaction.response.edit_message(content=msg, view=None)


class EditDistributionMonthSelect(ui.Select):
    def __init__(self, client: SheetsClient, dist_months: list[dict]):
        self._client = client
        self._dist_months = {d["month"]: d for d in dist_months}
        options = [discord.SelectOption(label=d["month"]) for d in dist_months]
        super().__init__(placeholder="اختر الشهر...", options=options)

    async def callback(self, interaction: discord.Interaction):
        d = self._dist_months[self.values[0]]
        modal = EditDistributionModal(
            self._client, d["row"], d["month"], d["member"], d["amount"]
        )
        await interaction.response.send_modal(modal)


class EditDistributionMonthView(ui.View):
    def __init__(self, client: SheetsClient, dist_months: list[dict]):
        super().__init__()
        self.add_item(EditDistributionMonthSelect(client, dist_months))


# ── Entry Point ───────────────────────────────────────────────────────────────

class EditTypeView(ui.View):
    def __init__(self, registry: MemberRegistry, client: SheetsClient):
        super().__init__()
        self._registry = registry
        self._client = client

    @ui.button(label="تعديل دفعة", style=discord.ButtonStyle.primary)
    async def edit_payment(self, interaction: discord.Interaction, button: ui.Button):
        view = EditPaymentMemberView(self._registry, self._client)
        await interaction.response.edit_message(content="اختر العضو:", view=view)

    @ui.button(label="تعديل توزيع", style=discord.ButtonStyle.secondary)
    async def edit_distribution(self, interaction: discord.Interaction, button: ui.Button):
        dist_months = self._client.get_distributed_months()
        if not dist_months:
            await interaction.response.edit_message(
                content="لا توجد توزيعات مسجلة بعد.", view=None
            )
            return
        view = EditDistributionMonthView(self._client, dist_months)
        await interaction.response.edit_message(content="اختر الشهر:", view=view)


async def start_edit(interaction: discord.Interaction,
                     registry: MemberRegistry, client: SheetsClient):
    view = EditTypeView(registry, client)
    await interaction.response.send_message("ماذا تريد أن تعدّل؟", view=view, ephemeral=True)
