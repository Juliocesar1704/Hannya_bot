import discord
from discord.ext import commands
from cogs.utils import safe_send


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ================================
    # !say
    # ================================
    @commands.command(name="say")
    @commands.has_permissions(manage_messages=True)
    async def say(self, ctx, *, mensagem: str):
        await safe_send(ctx, "Mensagem enviada!")
        await ctx.send(mensagem)

    # ================================
    # !say_embed
    # ================================
    @commands.command(name="say_embed")
    @commands.has_permissions(manage_messages=True)
    async def say_embed(self, ctx, titulo: str, *, descricao: str):
        embed = discord.Embed(
            title=titulo,
            description=descricao,
            color=discord.Color.blue()
        )
        await safe_send(ctx, "Embed enviado!")
        await ctx.send(embed=embed)

    # ================================
    # !clear
    # ================================
    @commands.command(name="clear")
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, quantidade: int):
        await safe_send(ctx, f"🧹 Limpando `{quantidade}` mensagens...")
        await ctx.channel.purge(limit=quantidade)

    # ================================
    # !kick
    # ================================
    @commands.command(name="kick")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, membro: discord.Member, *, motivo: str = "Não informado"):
        await membro.kick(reason=motivo)
        await safe_send(ctx, f"👢 {membro} foi expulso. Motivo: {motivo}")

    # ================================
    # !ban
    # ================================
    @commands.command(name="ban")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, membro: discord.Member, *, motivo: str = "Não informado"):
        await membro.ban(reason=motivo)
        await safe_send(ctx, f"🔨 {membro} foi banido. Motivo: {motivo}")

    # ================================
    # !unban nome#tag
    # ================================
    @commands.command(name="unban")
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, usuario: str):
        banned = await ctx.guild.bans()

        nome, tag = usuario.split("#")

        for ban in banned:
            user = ban.user
            if (user.name, user.discriminator) == (nome, tag):
                await ctx.guild.unban(user)
                await safe_send(ctx, f"👍 Usuário **{usuario}** desbanido.")
                return

        await safe_send(ctx, "Usuário não encontrado.")

    # ================================
    # !mute
    # ================================
    @commands.command(name="mute")
    @commands.has_permissions(manage_roles=True)
    async def mute(self, ctx, membro: discord.Member):
        cargo = discord.utils.get(ctx.guild.roles, name="Muted")

        if not cargo:
            await safe_send(ctx, "❌ Cargo **Muted** não existe.")
            return

        await membro.add_roles(cargo)
        await safe_send(ctx, f"🔇 {membro.mention} foi mutado.")

    # ================================
    # !unmute
    # ================================
    @commands.command(name="unmute")
    @commands.has_permissions(manage_roles=True)
    async def unmute(self, ctx, membro: discord.Member):
        cargo = discord.utils.get(ctx.guild.roles, name="Muted")

        if cargo in membro.roles:
            await membro.remove_roles(cargo)
            await safe_send(ctx, f"🔊 {membro.mention} foi desmutado.")
        else:
            await safe_send(ctx, "⚠️ Esse usuário não está mutado.")

    # ================================
    # !lock
    # ================================
    @commands.command(name="lock")
    @commands.has_permissions(manage_channels=True)
    async def lock(self, ctx):
        overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = False
        await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)

        await safe_send(ctx, "🔐 Canal trancado!")

    # ================================
    # !unlock
    # ================================
    @commands.command(name="unlock")
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx):
        overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = True
        await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)

        await safe_send(ctx, "🔓 Canal destrancado!")


async def setup(bot):
    await bot.add_cog(Admin(bot))