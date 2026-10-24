# cogs/info.py
import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timezone


class Info(commands.Cog):
    """Comandos informativos sobre usuários e o servidor."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # ============================================================
    # /userinfo
    # ============================================================
    @app_commands.command(name="userinfo", description="Exibe informações detalhadas sobre um usuário ou sobre você mesmo.")
    @app_commands.describe(membro="O membro do servidor a ser consultado (deixe vazio para ver o seu próprio perfil)")
    async def userinfo(self, interaction: discord.Interaction, membro: discord.Member = None):
        target: discord.Member = membro or interaction.user

        embed = discord.Embed(
            title=f"👤 Informações de {target.display_name}",
            color=target.color if target.color.value != 0 else discord.Color.red(),
            timestamp=datetime.now(timezone.utc)
        )
        embed.set_thumbnail(url=target.display_avatar.url)

        # Informações de Datas
        criado_em = target.created_at.strftime("%d/%m/%Y às %H:%M")
        entrou_em = target.joined_at.strftime("%d/%m/%Y às %H:%M") if target.joined_at else "Desconhecido"

        embed.add_field(name="🏷️ Tag / Nome", value=f"`{target.name}`", inline=True)
        embed.add_field(name="🆔 ID do Usuário", value=f"`{target.id}`", inline=True)
        embed.add_field(name="🤖 É Bot?", value="Sim" if target.bot else "Não", inline=True)

        embed.add_field(name="📅 Conta Criada em", value=criado_em, inline=True)
        embed.add_field(name="📥 Entrou no Servidor em", value=entrou_em, inline=True)
        embed.add_field(name="👑 Cargo Mais Alto", value=target.top_role.mention if target.top_role else "Nenhum", inline=True)

        # Lista de Cargos (exceto @everyone)
        cargos = [r.mention for r in target.roles if r.name != "@everyone"]
        cargos_str = ", ".join(cargos) if cargos else "Nenhum cargo atribuído"
        if len(cargos_str) > 1024:
            cargos_str = f"{len(cargos)} cargos (muitos para listar)"

        embed.add_field(name=f"🎭 Cargos ({len(cargos)})", value=cargos_str, inline=False)
        embed.set_footer(text=f"Solicitado por {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)

        await interaction.response.send_message(embed=embed)

    # ============================================================
    # /serverinfo
    # ============================================================
    @app_commands.command(name="serverinfo", description="Exibe informações e estatísticas completas sobre o servidor.")
    async def serverinfo(self, interaction: discord.Interaction):
        guild = interaction.guild
        if not guild:
            await interaction.response.send_message("❌ Este comando só pode ser utilizado dentro de um servidor.", ephemeral=True)
            return

        embed = discord.Embed(
            title=f"🏮 Informações do Servidor: {guild.name}",
            color=discord.Color.red(),
            timestamp=datetime.now(timezone.utc)
        )
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)

        # Estatísticas de Membros
        total_membros = guild.member_count or len(guild.members)
        bots = sum(1 for m in guild.members if m.bot)
        humanos = total_membros - bots

        # Canais
        texto = len(guild.text_channels)
        voz = len(guild.voice_channels)
        categorias = len(guild.categories)

        criado_em = guild.created_at.strftime("%d/%m/%Y às %H:%M")
        dono = guild.owner.mention if guild.owner else f"ID: {guild.owner_id}"

        embed.add_field(name="👑 Dono", value=dono, inline=True)
        embed.add_field(name="🆔 ID do Servidor", value=f"`{guild.id}`", inline=True)
        embed.add_field(name="📅 Criado em", value=criado_em, inline=True)

        embed.add_field(
            name="👥 Membros",
            value=f"• Total: `{total_membros}`\n• Pessoas: `{humanos}`\n• Bots: `{bots}`",
            inline=True
        )
        embed.add_field(
            name="📁 Canais",
            value=f"• Texto: `{texto}`\n• Voz: `{voz}`\n• Categorias: `{categorias}`",
            inline=True
        )
        embed.add_field(
            name="🚀 Nível de Impulso",
            value=f"Nível {guild.premium_tier} ({guild.premium_subscription_count} impulsos)",
            inline=True
        )

        embed.set_footer(text=f"Solicitado por {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)

        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Info(bot))
