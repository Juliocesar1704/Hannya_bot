# cogs/events.py
import random
import discord
from discord.ext import commands
from datetime import datetime
from config import LOG_CHANNEL_ID, WELCOME_CHANNEL_ID


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ===============================
    #      COMANDO !ajuda
    # ===============================
    @commands.command(name="ajuda")
    async def ajuda_command(self, ctx):
        """Exibe todos os comandos organizados por categorias"""

        embed = discord.Embed(
            title="📘 Centro de Ajuda",
            description="Lista de comandos disponíveis:",
            color=discord.Color.blue()
        )

        # PEGAR TODOS OS COGS E COMANDOS
        for cog_name, cog in self.bot.cogs.items():

            comandos = [
                f"`!{cmd.name}` - {cmd.help or 'Sem descrição'}"
                for cmd in cog.get_commands() if not cmd.hidden
            ]

            if comandos:
                embed.add_field(
                    name=f"📂 {cog_name}",
                    value="\n".join(comandos),
                    inline=False
                )

        # COMANDOS SEM COG
        sem_cog = [
            f"`!{cmd.name}` - {cmd.help or 'Sem descrição'}"
            for cmd in self.bot.commands
            if not cmd.cog_name and not cmd.hidden
        ]

        if sem_cog:
            embed.add_field(
                name="📂 Outros",
                value="\n".join(sem_cog),
                inline=False
            )

        embed.set_footer(
            text=f"Pedido por {ctx.author}",
            icon_url=ctx.author.avatar
        )

        await ctx.send(embed=embed)

    # ===============================
    # EVENTO: Novo membro entrou
    # ===============================
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        canal_boas_vindas = self.bot.get_channel(WELCOME_CHANNEL_ID)
        canal_log = self.bot.get_channel(LOG_CHANNEL_ID)

        cargo_novato = discord.utils.get(member.guild.roles, name="Novato")
        if cargo_novato:
            await member.add_roles(cargo_novato)

        cumprimentos = [
            f"👋 Bem-vindo(a), {member.mention}! Aproveite seu tempo aqui!",
            f"🌟 Olá {member.mention}! Que tal se apresentar no chat?",
            f"🎉 {member.mention} acabou de chegar! Dêem boas-vindas!"
        ]

        embed = discord.Embed(
            title=random.choice(["👋 Olá!", "🎈 Bem-vindo!", "🌸 Seja bem-vindo!"]),
            description=random.choice(cumprimentos),
            color=discord.Color.green(),
            timestamp=datetime.utcnow()
        )

        if member.avatar:
            embed.set_thumbnail(url=member.avatar.url)

        embed.set_footer(text=f"Entrou em: {member.guild.name}")

        if canal_boas_vindas:
            await canal_boas_vindas.send(embed=embed)

        if canal_log:
            await canal_log.send(f"✅ **{member}** entrou no servidor.")

        # Mensagem privada
        try:
            embed_dm = discord.Embed(
                title="🎉 Seja bem-vindo(a)!",
                description=(
                    f"Olá, {member.name}!\n\n"
                    f"Você entrou no servidor **{member.guild.name}**.\n"
                    "• Leia as regras\n"
                    "• Apresente-se no canal apropriado\n"
                    "• Use `!ajuda` para ver os comandos\n\n"
                    "Bom divertimento! 🎈"
                ),
                color=discord.Color.blurple()
            )
            await member.send(embed=embed_dm)
        except discord.Forbidden:
            pass

    # ===============================
    # EVENTO: Membro saiu
    # ===============================
    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        canal_log = self.bot.get_channel(LOG_CHANNEL_ID)
        despedidas = [
            f"😢 {member} nos deixou. Até mais!",
            f"👋 Adeus {member}! Esperamos te ver de volta!",
            f"💔 {member} saiu do servidor. Saudades!"
        ]
        if canal_log:
            await canal_log.send(random.choice(despedidas))

    # ===============================
    # EVENTO: Atualização do membro
    # ===============================
    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        canal_log = self.bot.get_channel(LOG_CHANNEL_ID)

        jogo_antes = [a.name for a in (before.activities or []) if isinstance(a, discord.Game)]
        jogo_depois = [a.name for a in (after.activities or []) if isinstance(a, discord.Game)]

        if jogo_depois and jogo_depois != jogo_antes:
            if canal_log:
                await canal_log.send(
                    f"🎮 {after.display_name} começou a jogar **{jogo_depois[0]}**!"
                )


# ===============================
# SETUP DO COG
# ===============================
async def setup(bot):
    await bot.add_cog(Events(bot))