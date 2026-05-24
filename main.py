import os
import discord
from discord import app_commands
from dotenv import load_dotenv
from src.sheets_client import SheetsClient
from src.member_registry import MemberRegistry
from src.flows.balance import start_balance

load_dotenv()

SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
CREDENTIALS = os.getenv("GOOGLE_CREDENTIALS_JSON", "credentials.json")
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

sheets = SheetsClient(sheet_id=SHEET_ID, credentials_path=CREDENTIALS)
registry = MemberRegistry(sheets)


@bot.event
async def on_ready():
    await tree.sync()
    print(f"Jamia Bot is online as {bot.user}")


@tree.command(name="balance", description="استعلم عن رصيد عضو")
async def balance(interaction: discord.Interaction):
    await start_balance(interaction, registry, sheets)


bot.run(TOKEN)
