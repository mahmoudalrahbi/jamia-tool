import discord
from discord import ui
from src.sheets_client import SheetsClient
from src.member_registry import MemberRegistry

DISTRIBUTION_METHODS = ["حجز", "قرعة"]


def build_distribute_confirmation(month: str, member_name: str, amount: int) -> str:
    return f"تسجيل توزيع — الشهر: **{month}** — المستفيد: **{member_name}** — المبلغ: **{amount} ريال**"


class MethodSelect(ui.Select):
    def __init__(self, client: SheetsClient, dist_row: int,
                 month: str, member_name: str, amount: int):
        self._client = client
        self._dist_row = dist_row
        self._month = month
        self._member_name = member_name
        self._amount = amount
        options = [discord.SelectOption(label=m) for m in DISTRIBUTION_METHODS]
        super().__init__(placeholder="اختر طريقة التوزيع...", options=options)

    async def callback(self, interaction: discord.Interaction):
        method = self.values[0]
        self._client.write_distribution(
            row=self._dist_row,
            member=self._member_name,
            amount=self._amount,
            method=method,
        )
        msg = f"✅ تم تسجيل التوزيع — {self._month} — {self._member_name} — {self._amount} ريال — {method}"
        await interaction.response.edit_message(content=msg, view=None)


class MethodView(ui.View):
    def __init__(self, client: SheetsClient, dist_row: int,
                 month: str, member_name: str, amount: int):
        super().__init__()
        self.add_item(MethodSelect(client, dist_row, month, member_name, amount))


class AmountModal(ui.Modal, title="المبلغ المستلم"):
    amount_input: ui.TextInput = ui.TextInput(
        label="المبلغ",
        placeholder="مثال: 440",
        max_length=6,
    )

    def __init__(self, client: SheetsClient, dist_row: int,
                 month: str, member_name: str):
        super().__init__()
        self._client = client
        self._dist_row = dist_row
        self._month = month
        self._member_name = member_name

    async def on_submit(self, interaction: discord.Interaction):
        try:
            amount = int(self.amount_input.value)
        except ValueError:
            await interaction.response.send_message("المبلغ يجب أن يكون رقمًا.", ephemeral=True)
            return
        msg = build_distribute_confirmation(self._month, self._member_name, amount)
        view = MethodView(self._client, self._dist_row, self._month, self._member_name, amount)
        await interaction.response.edit_message(content=msg, view=view)


class MemberSelect(ui.Select):
    def __init__(self, registry: MemberRegistry, client: SheetsClient,
                 dist_row: int, month: str):
        self._registry = registry
        self._client = client
        self._dist_row = dist_row
        self._month = month
        options = [discord.SelectOption(label=m["name"]) for m in registry.all()]
        super().__init__(placeholder="اختر المستفيد...", options=options)

    async def callback(self, interaction: discord.Interaction):
        member_name = self.values[0]
        modal = AmountModal(self._client, self._dist_row, self._month, member_name)
        await interaction.response.send_modal(modal)


class DistributeView(ui.View):
    def __init__(self, registry: MemberRegistry, client: SheetsClient,
                 dist_row: int, month: str):
        super().__init__()
        self.add_item(MemberSelect(registry, client, dist_row, month))


async def start_distribute(interaction: discord.Interaction,
                           registry: MemberRegistry, client: SheetsClient):
    dist = client.get_next_distribution()
    view = DistributeView(registry, client, dist["row"], dist["month"])
    await interaction.response.send_message(
        f"الشهر القادم للتوزيع: **{dist['month']}**\nاختر المستفيد:",
        view=view,
        ephemeral=True,
    )
