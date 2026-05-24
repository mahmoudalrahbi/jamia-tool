import discord
from src.sheets_client import SheetsClient
from src.member_registry import MemberRegistry


def build_summary_message(registry: MemberRegistry, client: SheetsClient) -> str:
    members = registry.all()

    total_collected = sum(registry.get_balance(m["name"]) for m in members)
    dist_months = client.get_distributed_months()
    total_distributed = sum(d["amount"] for d in dist_months)
    remaining = total_collected - total_distributed

    lines = [
        f"**ملخص الجمعية**",
        f"مجموع الدفعات: **{total_collected} ريال**",
        f"مجموع التوزيعات: **{total_distributed} ريال**",
        f"الرصيد المتبقي: **{remaining} ريال**",
        "",
        "**حالة الأعضاء:**",
    ]

    for m in members:
        paid = registry.get_paid_months(m["name"])
        count = len(paid)
        lines.append(f"• {m['name']} — {count} دفعة")

    return "\n".join(lines)


async def start_summary(interaction: discord.Interaction,
                        registry: MemberRegistry, client: SheetsClient):
    msg = build_summary_message(registry, client)
    await interaction.response.send_message(msg, ephemeral=True)
