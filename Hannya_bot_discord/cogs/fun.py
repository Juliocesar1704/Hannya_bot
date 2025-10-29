import discord
from discord.ext import commands

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def hello(self, ctx):
        await ctx.send("Olá! 😄")

async def setup(bot):
    await bot.add_cog(Fun(bot))
