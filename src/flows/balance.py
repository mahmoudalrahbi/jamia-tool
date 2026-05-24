import discord
from discord import ui
from src.member_registry import MemberRegistry


def build_balance_reply(member_name: str, registry: MemberRegistry) -> str:
    balance = registry.get_balance(member_name)
    return f"**{member_name}** — إجمالي المدفوع: **{balance} ريال**"


class MemberSelect(ui.Select):
    def __init__(self, registry: MemberRegistry):
        self._registry = registry
        options = [
            discord.SelectOption(label=m["name"]) for m in registry.all()
        ]
        super().__init__(placeholder="اختر العضو...", options=options)

    async def callback(self, interaction: discord.Interaction):
        member_name = self.values[0]
        reply = build_balance_reply(member_name, self._registry)
        await interaction.response.edit_message(content=reply, view=None)


class BalanceView(ui.View):
    def __init__(self, registry: MemberRegistry):
        super().__init__()
        self.add_item(MemberSelect(registry))


async def start_balance(interaction: discord.Interaction,
                        registry: MemberRegistry):
    view = BalanceView(registry)
    await interaction.response.send_message("اختر العضو:", view=view, ephemeral=True)
