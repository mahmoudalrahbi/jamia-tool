import os
from dotenv import load_dotenv
import discord

load_dotenv()

intents = discord.Intents.default()
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"Jamia Bot is online as {client.user}")

client.run(os.getenv("DISCORD_TOKEN"))
