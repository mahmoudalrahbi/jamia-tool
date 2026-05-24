import discord
from discord import ui
from dataclasses import dataclass
from src.sheets_client import SheetsClient
from src.member_registry import MemberRegistry

DISTRIBUTION_METHODS = ["حجز", "قرعة"]


@dataclass
class DistributeContext:
    client: SheetsClient
    registry: MemberRegistry
    dist_row: int = 0
    month: str = ""
    member_name: str = ""
    amount: int = 0


def build_distribute_confirmation(month: str, member_name: str, amount: int) -> str:
    return f"تسجيل توزيع — الشهر: **{month}** — المستفيد: **{member_name}** — المبلغ: **{amount} ريال**"


class MethodSelect(ui.Select):
    def __init__(self, ctx: DistributeContext):
        self._ctx = ctx
        options = [discord.SelectOption(label=m) for m in DISTRIBUTION_METHODS]
        super().__init__(placeholder="اختر طريقة التوزيع...", options=options)

    async def callback(self, interaction: discord.Interaction):
        method = self.values[0]
        self._ctx.client.write_distribution(
            row=self._ctx.dist_row,
            member=self._ctx.member_name,
            amount=self._ctx.amount,
            method=method,
        )
        msg = f"✅ تم تسجيل التوزيع — {self._ctx.month} — {self._ctx.member_name} — {self._ctx.amount} ريال — {method}"
        await interaction.response.edit_message(content=msg, view=None)


class MethodView(ui.View):
    def __init__(self, ctx: DistributeContext):
        super().__init__()
        self.add_item(MethodSelect(ctx))


class AmountModal(ui.Modal, title="المبلغ المستلم"):
    amount_input: ui.TextInput = ui.TextInput(
        label="المبلغ",
        placeholder="مثال: 440",
        max_length=6,
    )

    def __init__(self, ctx: DistributeContext):
        super().__init__()
        self._ctx = ctx

    async def on_submit(self, interaction: discord.Interaction):
        try:
            amount = int(self.amount_input.value)
        except ValueError:
            await interaction.response.send_message("المبلغ يجب أن يكون رقمًا.", ephemeral=True)
            return
        self._ctx.amount = amount
        msg = build_distribute_confirmation(self._ctx.month, self._ctx.member_name, self._ctx.amount)
        view = MethodView(self._ctx)
        await interaction.response.edit_message(content=msg, view=view)


class MemberSelect(ui.Select):
    def __init__(self, ctx: DistributeContext):
        self._ctx = ctx
        options = [discord.SelectOption(label=m["name"]) for m in ctx.registry.all()]
        super().__init__(placeholder="اختر المستفيد...", options=options)

    async def callback(self, interaction: discord.Interaction):
        self._ctx.member_name = self.values[0]
        modal = AmountModal(self._ctx)
        await interaction.response.send_modal(modal)


class DistributeView(ui.View):
    def __init__(self, ctx: DistributeContext):
        super().__init__()
        self.add_item(MemberSelect(ctx))


async def start_distribute(interaction: discord.Interaction,
                           registry: MemberRegistry, client: SheetsClient):
    dist = client.get_next_distribution()
    ctx = DistributeContext(client=client, registry=registry,
                            dist_row=dist["row"], month=dist["month"])
    view = DistributeView(ctx)
    await interaction.response.send_message(
        f"الشهر القادم للتوزيع: **{dist['month']}**\nاختر المستفيد:",
        view=view,
        ephemeral=True,
    )
