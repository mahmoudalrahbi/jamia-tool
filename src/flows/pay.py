import discord
from discord import ui
from dataclasses import dataclass, field
from src.member_registry import MemberRegistry
from src.flows.components import DatePickerView, TimeoutView


@dataclass
class PayContext:
    registry: MemberRegistry
    member_name: str = ""
    month: str = ""
    amount: int = 0


def build_pay_confirmation(member_name: str, month: str, amount: int) -> str:
    return f"تسجيل دفعة لـ **{member_name}** — الشهر: **{month}** — المبلغ: **{amount} ريال**"


async def execute_payment(interaction: discord.Interaction, registry: MemberRegistry,
                          member_name: str, month: str, date: str, amount: int) -> None:
    registry.write_payment(member=member_name, month=month, date=date, amount=amount)
    msg = f"✅ تم تسجيل دفعة **{member_name}** — {month} — {amount} ريال"
    await interaction.response.edit_message(content=msg, view=None)


def _make_date_picker(registry: MemberRegistry, member_name: str,
                      month: str, amount: int) -> DatePickerView:
    async def on_date(interaction: discord.Interaction, date: str):
        await execute_payment(interaction, registry, member_name, month, date, amount)
    return DatePickerView(on_date)


class AmountModal(ui.Modal, title="تعديل المبلغ"):
    amount_input: ui.TextInput = ui.TextInput(
        label="المبلغ",
        placeholder="مثال: 20",
        max_length=6,
    )

    def __init__(self, ctx: PayContext):
        super().__init__()
        self._ctx = ctx
        self.amount_input.default = str(ctx.amount)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            amount = int(self.amount_input.value)
        except ValueError:
            await interaction.response.send_message("المبلغ يجب أن يكون رقمًا.", ephemeral=True)
            return
        self._ctx.amount = amount
        msg = build_pay_confirmation(self._ctx.member_name, self._ctx.month, self._ctx.amount)
        await interaction.response.edit_message(content=msg, view=ConfirmView(self._ctx))


class DuplicatePaymentView(TimeoutView):
    def __init__(self, ctx: PayContext):
        super().__init__()
        self._ctx = ctx

    @ui.button(label="نعم، استبدل", style=discord.ButtonStyle.danger)
    async def overwrite(self, interaction: discord.Interaction, button: ui.Button):
        view = _make_date_picker(
            self._ctx.registry, self._ctx.member_name, self._ctx.month, self._ctx.amount
        )
        await interaction.response.edit_message(content="اختر تاريخ الدفع:", view=view)

    @ui.button(label="إلغاء", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.edit_message(content="تم الإلغاء.", view=None)


class ConfirmView(TimeoutView):
    def __init__(self, ctx: PayContext):
        super().__init__()
        self._ctx = ctx

    @ui.button(label="تأكيد", style=discord.ButtonStyle.success)
    async def confirm(self, interaction: discord.Interaction, button: ui.Button):
        paid = self._ctx.registry.get_paid_months(self._ctx.member_name)
        if self._ctx.month in paid:
            msg = f"هذه الدفعة مسجلة مسبقاً لـ **{self._ctx.member_name}** — {self._ctx.month}. هل تريد استبدالها؟"
            await interaction.response.edit_message(content=msg, view=DuplicatePaymentView(self._ctx))
            return
        view = _make_date_picker(
            self._ctx.registry, self._ctx.member_name, self._ctx.month, self._ctx.amount
        )
        await interaction.response.edit_message(content="اختر تاريخ الدفع:", view=view)

    @ui.button(label="تعديل المبلغ", style=discord.ButtonStyle.secondary)
    async def edit_amount(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_modal(AmountModal(self._ctx))


class MonthSelect(ui.Select):
    def __init__(self, ctx: PayContext, months: list[str]):
        self._ctx = ctx
        options = [discord.SelectOption(label=m) for m in months]
        super().__init__(placeholder="اختر الشهر...", options=options)

    async def callback(self, interaction: discord.Interaction):
        self._ctx.month = self.values[0]
        msg = build_pay_confirmation(self._ctx.member_name, self._ctx.month, self._ctx.amount)
        view = ConfirmView(self._ctx)
        await interaction.response.edit_message(content=msg, view=view)


class MonthView(TimeoutView):
    def __init__(self, ctx: PayContext, months: list[str]):
        super().__init__()
        self.add_item(MonthSelect(ctx, months))


class MemberSelect(ui.Select):
    def __init__(self, ctx: PayContext):
        self._ctx = ctx
        options = [discord.SelectOption(label=m["name"]) for m in ctx.registry.all()]
        super().__init__(placeholder="اختر العضو...", options=options)

    async def callback(self, interaction: discord.Interaction):
        self._ctx.member_name = self.values[0]
        member = self._ctx.registry.get(self._ctx.member_name)
        if member is None:
            await interaction.response.edit_message(
                content="عذراً، لم يُعثر على بيانات العضو. الرجاء المحاولة مجدداً.", view=None
            )
            return
        months = self._ctx.registry.get_unpaid_months(self._ctx.member_name)

        if not months:
            await interaction.response.edit_message(
                content=f"لا توجد شهور غير مدفوعة لـ **{self._ctx.member_name}**", view=None
            )
            return

        self._ctx.amount = member["monthly_amount"]
        view = MonthView(self._ctx, months)
        await interaction.response.edit_message(content="اختر الشهر:", view=view)


class PayView(TimeoutView):
    def __init__(self, ctx: PayContext):
        super().__init__()
        self.add_item(MemberSelect(ctx))


async def start_pay(interaction: discord.Interaction, registry: MemberRegistry):
    ctx = PayContext(registry=registry)
    view = PayView(ctx)
    await interaction.response.send_message("اختر العضو:", view=view, ephemeral=True)
