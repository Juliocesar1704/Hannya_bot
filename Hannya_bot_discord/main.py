# main.py
import discord
from discord.ext import commands
from config import TOKEN, COMMAND_PREFIX

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)

async def load_extensions():
    for ext in ("cogs.events", "cogs.fun", "cogs.admin"):
        await bot.load_extension(ext)

@bot.event
async def on_ready():
    print(f"✅ Bot {bot.user} conectado com sucesso!")

async def main():
    async with bot:
        await load_extensions()
        await bot.start(TOKEN)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
