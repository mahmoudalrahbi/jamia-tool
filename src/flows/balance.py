import discord
from discord import ui
from src.sheets_client import SheetsClient
from src.member_registry import MemberRegistry


def build_balance_reply(member_name: str, client: SheetsClient) -> str:
    balance = client.get_balance(member_name)
    return f"**{member_name}** — إجمالي المدفوع: **{balance} ريال**"


class MemberSelect(ui.Select):
    def __init__(self, registry: MemberRegistry, client: SheetsClient):
        self._client = client
        options = [
            discord.SelectOption(label=m["name"]) for m in registry.all()
        ]
        super().__init__(placeholder="اختر العضو...", options=options)

    async def callback(self, interaction: discord.Interaction):
        member_name = self.values[0]
        reply = build_balance_reply(member_name, self._client)
        await interaction.response.edit_message(content=reply, view=None)


class BalanceView(ui.View):
    def __init__(self, registry: MemberRegistry, client: SheetsClient):
        super().__init__()
        self.add_item(MemberSelect(registry, client))


async def start_balance(interaction: discord.Interaction,
                        registry: MemberRegistry, client: SheetsClient):
    view = BalanceView(registry, client)
    await interaction.response.send_message("اختر العضو:", view=view, ephemeral=True)
