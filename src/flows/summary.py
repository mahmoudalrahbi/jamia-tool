import discord
from src.member_registry import MemberRegistry


def build_summary_message(registry: MemberRegistry) -> str:
    members = registry.all()

    total_collected = sum(registry.get_balance(m["name"]) for m in members)
    dist_months = registry.get_distributed_months()
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


async def start_summary(interaction: discord.Interaction, registry: MemberRegistry):
    msg = build_summary_message(registry)
    await interaction.response.send_message(msg, ephemeral=True)
