import os
import discord
from discord import app_commands
from dotenv import load_dotenv
from src.sheets_client import SheetsClient
from src.member_registry import MemberRegistry
from src.flows.balance import start_balance
from src.flows.pay import start_pay
from src.flows.distribute import start_distribute
from src.flows.edit import start_edit
from src.flows.summary import start_summary
from src.command_error import handle_command_error

load_dotenv()

SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
CREDENTIALS = os.getenv("GOOGLE_CREDENTIALS_JSON", "credentials.json")
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

registry = MemberRegistry(SheetsClient(sheet_id=SHEET_ID, credentials_path=CREDENTIALS))


@bot.event
async def on_ready():
    await tree.sync()
    print(f"Jamia Bot is online as {bot.user}")


@tree.command(name="balance", description="استعلم عن رصيد عضو")
async def balance(interaction: discord.Interaction):
    await handle_command_error(interaction, start_balance(interaction, registry))


@tree.command(name="pay", description="سجّل دفعة لعضو")
async def pay(interaction: discord.Interaction):
    await handle_command_error(interaction, start_pay(interaction, registry))


@tree.command(name="distribute", description="سجّل توزيع الجمعية")
async def distribute(interaction: discord.Interaction):
    await handle_command_error(interaction, start_distribute(interaction, registry))


@tree.command(name="edit", description="عدّل دفعة أو توزيع")
async def edit(interaction: discord.Interaction):
    await handle_command_error(interaction, start_edit(interaction, registry))


@tree.command(name="summary", description="ملخص الجمعية")
async def summary(interaction: discord.Interaction):
    await handle_command_error(interaction, start_summary(interaction, registry))


bot.run(TOKEN)
