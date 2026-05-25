import discord
from discord import ui
from dataclasses import dataclass
from src.member_registry import MemberRegistry
from src.flows.components import DatePickerView, TimeoutView


PAYMENT_METHODS = ["تحويل", "كاش"]


@dataclass
class EditPaymentContext:
    registry: MemberRegistry
    member_name: str = ""
    month: str = ""
    current_amount: int = 0
    current_date: str = ""
    new_amount: int = 0


@dataclass
class EditDistributionContext:
    registry: MemberRegistry
    dist_row: int = 0
    month: str = ""
    current_member: str = ""
    current_amount: int = 0
    current_method: str = ""


# ── Edit Payment ──────────────────────────────────────────────────────────────

def _make_payment_date_picker(registry: MemberRegistry, member_name: str,
                               month: str, amount: int) -> DatePickerView:
    async def on_date(interaction: discord.Interaction, date: str):
        registry.write_payment(member=member_name, month=month, date=date, amount=amount)
        msg = f"✅ تم تعديل دفعة **{member_name}** — {month} — {amount} ريال"
        await interaction.response.edit_message(content=msg, view=None)
    return DatePickerView(on_date)


class EditPaymentAmountModal(ui.Modal, title="تعديل المبلغ"):
    amount_input: ui.TextInput = ui.TextInput(label="المبلغ", max_length=6)

    def __init__(self, ctx: EditPaymentContext):
        super().__init__()
        self._ctx = ctx
        self.amount_input.default = str(ctx.current_amount)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            amount = int(self.amount_input.value)
        except ValueError:
            await interaction.response.send_message("المبلغ يجب أن يكون رقمًا.", ephemeral=True)
            return
        self._ctx.new_amount = amount
        view = EditPaymentMethodView(self._ctx)
        await interaction.response.edit_message(content="اختر طريقة الدفع:", view=view)


class EditPaymentMethodSelect(ui.Select):
    def __init__(self, ctx: EditPaymentContext):
        self._ctx = ctx
        options = [discord.SelectOption(label=m) for m in PAYMENT_METHODS]
        super().__init__(placeholder="اختر طريقة الدفع...", options=options)

    async def callback(self, interaction: discord.Interaction):
        method = self.values[0]
        self._ctx.registry.write_payment(
            member=self._ctx.member_name,
            month=self._ctx.month,
            date=self._ctx.current_date,
            amount=self._ctx.new_amount,
            transfer_type=method,
        )
        msg = f"✅ تم تعديل دفعة **{self._ctx.member_name}** — {self._ctx.month} — {self._ctx.new_amount} ريال — {method}"
        await interaction.response.edit_message(content=msg, view=None)


class EditPaymentMethodView(TimeoutView):
    def __init__(self, ctx: EditPaymentContext):
        super().__init__()
        self.add_item(EditPaymentMethodSelect(ctx))


class EditPaymentMonthSelect(ui.Select):
    def __init__(self, ctx: EditPaymentContext, months: list[str]):
        self._ctx = ctx
        options = [discord.SelectOption(label=m) for m in months]
        super().__init__(placeholder="اختر الشهر...", options=options)

    async def callback(self, interaction: discord.Interaction):
        self._ctx.month = self.values[0]
        payment = self._ctx.registry.get_payment(self._ctx.member_name, self._ctx.month)
        self._ctx.current_amount = payment["amount"]
        self._ctx.current_date = payment["date"]
        await interaction.response.send_modal(EditPaymentAmountModal(self._ctx))


class EditPaymentMonthView(TimeoutView):
    def __init__(self, ctx: EditPaymentContext, months: list[str]):
        super().__init__()
        self.add_item(EditPaymentMonthSelect(ctx, months))


class EditPaymentMemberSelect(ui.Select):
    def __init__(self, ctx: EditPaymentContext):
        self._ctx = ctx
        options = [discord.SelectOption(label=m["name"]) for m in ctx.registry.all()]
        super().__init__(placeholder="اختر العضو...", options=options)

    async def callback(self, interaction: discord.Interaction):
        self._ctx.member_name = self.values[0]
        months = self._ctx.registry.get_paid_months(self._ctx.member_name)
        if not months:
            await interaction.response.edit_message(
                content=f"لا توجد دفعات مسجلة لـ **{self._ctx.member_name}**", view=None
            )
            return
        view = EditPaymentMonthView(self._ctx, months)
        await interaction.response.edit_message(content="اختر الشهر:", view=view)


class EditPaymentMemberView(TimeoutView):
    def __init__(self, ctx: EditPaymentContext):
        super().__init__()
        self.add_item(EditPaymentMemberSelect(ctx))



# ── Edit Distribution ─────────────────────────────────────────────────────────

class EditDistributionModal(ui.Modal, title="تعديل التوزيع"):
    member_input: ui.TextInput = ui.TextInput(label="المستفيد", max_length=50)
    amount_input: ui.TextInput = ui.TextInput(label="المبلغ", max_length=6)

    def __init__(self, ctx: EditDistributionContext):
        super().__init__()
        self._ctx = ctx
        self.member_input.default = ctx.current_member
        self.amount_input.default = str(ctx.current_amount)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            amount = int(self.amount_input.value)
        except ValueError:
            await interaction.response.send_message("المبلغ يجب أن يكون رقمًا.", ephemeral=True)
            return
        self._ctx.registry.write_distribution(
            row=self._ctx.dist_row,
            member=self.member_input.value,
            amount=amount,
            method=self._ctx.current_method,
        )
        msg = f"✅ تم تعديل توزيع {self._ctx.month} — {self.member_input.value} — {amount} ريال"
        await interaction.response.edit_message(content=msg, view=None)


class EditDistributionMonthSelect(ui.Select):
    def __init__(self, ctx: EditDistributionContext, dist_months: list[dict]):
        self._ctx = ctx
        self._dist_months = {d["month"]: d for d in dist_months}
        options = [discord.SelectOption(label=d["month"]) for d in dist_months]
        super().__init__(placeholder="اختر الشهر...", options=options)

    async def callback(self, interaction: discord.Interaction):
        d = self._dist_months[self.values[0]]
        self._ctx.dist_row = d["row"]
        self._ctx.month = d["month"]
        self._ctx.current_member = d["member"]
        self._ctx.current_amount = d["amount"]
        self._ctx.current_method = d.get("method", "")
        await interaction.response.send_modal(EditDistributionModal(self._ctx))


class EditDistributionMonthView(TimeoutView):
    def __init__(self, ctx: EditDistributionContext, dist_months: list[dict]):
        super().__init__()
        self.add_item(EditDistributionMonthSelect(ctx, dist_months))


# ── Entry Point ───────────────────────────────────────────────────────────────

class EditTypeView(TimeoutView):
    def __init__(self, registry: MemberRegistry):
        super().__init__()
        self._registry = registry

    @ui.button(label="تعديل دفعة", style=discord.ButtonStyle.primary)
    async def edit_payment(self, interaction: discord.Interaction, button: ui.Button):
        ctx = EditPaymentContext(registry=self._registry)
        view = EditPaymentMemberView(ctx)
        await interaction.response.edit_message(content="اختر العضو:", view=view)

    @ui.button(label="تعديل توزيع", style=discord.ButtonStyle.secondary)
    async def edit_distribution(self, interaction: discord.Interaction, button: ui.Button):
        dist_months = self._registry.get_distributed_months()
        if not dist_months:
            await interaction.response.edit_message(
                content="لا توجد توزيعات مسجلة بعد.", view=None
            )
            return
        ctx = EditDistributionContext(registry=self._registry)
        view = EditDistributionMonthView(ctx, dist_months)
        await interaction.response.edit_message(content="اختر الشهر:", view=view)


async def start_edit(interaction: discord.Interaction, registry: MemberRegistry):
    view = EditTypeView(registry)
    await interaction.response.send_message("ماذا تريد أن تعدّل؟", view=view, ephemeral=True)
