# cogs/admin.py
import re
import asyncio
from datetime import timedelta, datetime, timezone
import discord
from discord import app_commands
from discord.ext import commands
from cogs.db import add_warn, get_warns, remove_warn
from config import LOG_CHANNEL_ID


def parse_duration(duration_str: str) -> timedelta | None:
    """Converte strings como '10m', '2h', '1d', '30s' em timedelta."""
    match = re.match(r"^(\d+)([smhd])$", duration_str.lower().strip())
    if not match:
        return None
    val, unit = match.groups()
    val = int(val)
    if unit == "s":
        return timedelta(seconds=val)
    elif unit == "m":
        return timedelta(minutes=val)
    elif unit == "h":
        return timedelta(hours=val)
    elif unit == "d":
        return timedelta(days=val)
    return None


class Admin(commands.Cog):
    """Comandos Slash de administração e moderação."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def _send_log(self, guild: discord.Guild, embed: discord.Embed):
        """Envia embed informativo para o canal de logs configurado."""
        if not LOG_CHANNEL_ID:
            return
        log_ch = guild.get_channel(LOG_CHANNEL_ID)
        if log_ch:
            try:
                await log_ch.send(embed=embed)
            except discord.HTTPException:
                pass

    # ============================================================
    # /limpar
    # ============================================================
    @app_commands.command(name="limpar", description="Apaga uma quantidade específica de mensagens do canal.")
    @app_commands.describe(quantidade="Número de mensagens a serem apagadas (1 a 100)")
    @app_commands.default_permissions(manage_messages=True)
    async def limpar(self, interaction: discord.Interaction, quantidade: int):
        if quantidade < 1 or quantidade > 100:
            await interaction.response.send_message("⚠️ A quantidade deve ser entre 1 e 100 mensagens.", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)
        deleted = await interaction.channel.purge(limit=quantidade)
        await interaction.followup.send(f"🧹 `{len(deleted)}` mensagem(ns) foram apagadas com sucesso!", ephemeral=True)

    # ============================================================
    # /falar
    # ============================================================
    @app_commands.command(name="falar", description="Faz o bot enviar uma mensagem de texto no canal.")
    @app_commands.describe(mensagem="O texto que o bot deve enviar")
    @app_commands.default_permissions(manage_messages=True)
    async def falar(self, interaction: discord.Interaction, mensagem: str):
        await interaction.channel.send(mensagem)
        await interaction.response.send_message("✅ Mensagem enviada!", ephemeral=True)

    # ============================================================
    # /anuncio
    # ============================================================
    @app_commands.command(name="anuncio", description="Envia um anúncio oficial com formatação Embed no canal.")
    @app_commands.describe(titulo="Título do anúncio", descricao="Conteúdo detalhado do comunicado")
    @app_commands.default_permissions(manage_messages=True)
    async def anuncio(self, interaction: discord.Interaction, titulo: str, descricao: str):
        embed = discord.Embed(
            title=titulo,
            description=descricao,
            color=discord.Color.red(),
            timestamp=datetime.now(timezone.utc)
        )
        embed.set_footer(text=f"Publicado por {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)
        await interaction.channel.send(embed=embed)
        await interaction.response.send_message("✅ Anúncio publicado com sucesso!", ephemeral=True)

    # ============================================================
    # /kick
    # ============================================================
    @app_commands.command(name="kick", description="Expulsa um membro do servidor.")
    @app_commands.describe(membro="O membro que será expulso", motivo="Motivo da expulsão")
    @app_commands.default_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, membro: discord.Member, motivo: str = "Não informado"):
        if membro.id == interaction.user.id:
            await interaction.response.send_message("⚠️ Você não pode expulsar a si mesmo.", ephemeral=True)
            return
        if membro.top_role >= interaction.user.top_role and interaction.user.id != interaction.guild.owner_id:
            await interaction.response.send_message("❌ Você não pode expulsar alguém com cargo igual ou superior ao seu.", ephemeral=True)
            return

        try:
            await membro.kick(reason=f"{motivo} (por {interaction.user})")
            await interaction.response.send_message(f"👢 **{membro.display_name}** foi expulso do servidor.\n📝 Motivo: `{motivo}`")

            # Log
            log_embed = discord.Embed(title="👢 Membro Expulso", color=discord.Color.orange(), timestamp=datetime.now(timezone.utc))
            log_embed.add_field(name="Membro", value=f"{membro.mention} (`{membro.id}`)", inline=True)
            log_embed.add_field(name="Moderador", value=interaction.user.mention, inline=True)
            log_embed.add_field(name="Motivo", value=motivo, inline=False)
            await self._send_log(interaction.guild, log_embed)
        except discord.Forbidden:
            await interaction.response.send_message("❌ Permissão insuficiente da Hannya para expulsar este membro.", ephemeral=True)

    # ============================================================
    # /ban
    # ============================================================
    @app_commands.command(name="ban", description="Bane permanentemente um membro do servidor.")
    @app_commands.describe(membro="O membro que será banido", motivo="Motivo do banimento")
    @app_commands.default_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, membro: discord.Member, motivo: str = "Não informado"):
        if membro.id == interaction.user.id:
            await interaction.response.send_message("⚠️ Você não pode banir a si mesmo.", ephemeral=True)
            return
        if membro.top_role >= interaction.user.top_role and interaction.user.id != interaction.guild.owner_id:
            await interaction.response.send_message("❌ Você não pode banir alguém com cargo igual ou superior ao seu.", ephemeral=True)
            return

        try:
            await membro.ban(reason=f"{motivo} (por {interaction.user})")
            await interaction.response.send_message(f"🔨 **{membro.display_name}** foi banido com sucesso.\n📝 Motivo: `{motivo}`")

            # Log
            log_embed = discord.Embed(title="🔨 Membro Banido", color=discord.Color.red(), timestamp=datetime.now(timezone.utc))
            log_embed.add_field(name="Membro", value=f"{membro.mention} (`{membro.id}`)", inline=True)
            log_embed.add_field(name="Moderador", value=interaction.user.mention, inline=True)
            log_embed.add_field(name="Motivo", value=motivo, inline=False)
            await self._send_log(interaction.guild, log_embed)
        except discord.Forbidden:
            await interaction.response.send_message("❌ Permissão insuficiente da Hannya para banir este membro.", ephemeral=True)

    # ============================================================
    # /unban
    # ============================================================
    @app_commands.command(name="unban", description="Desbane um usuário utilizando o ID numérico ou nome.")
    @app_commands.describe(usuario_id="O ID numérico ou nome de usuário da pessoa banida")
    @app_commands.default_permissions(ban_members=True)
    async def unban(self, interaction: discord.Interaction, usuario_id: str):
        usuario_limpo = usuario_id.strip().lstrip("@")
        desbanido = False

        await interaction.response.defer(ephemeral=True)
        try:
            async for ban_entry in interaction.guild.bans():
                user = ban_entry.user
                if (
                    str(user.id) == usuario_limpo
                    or user.name.lower() == usuario_limpo.lower()
                    or f"{user.name}#{user.discriminator}".lower() == usuario_limpo.lower()
                ):
                    await interaction.guild.unban(user, reason=f"Desbanido por {interaction.user}")
                    await interaction.followup.send(f"👍 O usuário **{user}** (ID: `{user.id}`) foi desbanido com sucesso!")
                    desbanido = True
                    break

            if not desbanido:
                await interaction.followup.send(f"⚠️ Usuário `{usuario_id}` não foi encontrado na lista de banidos.")
        except discord.Forbidden:
            await interaction.followup.send("❌ A Hannya não tem permissão para visualizar bans ou desbanir.")

    # ============================================================
    # /mute
    # ============================================================
    @app_commands.command(name="mute", description="Silencia temporariamente um usuário (Timeout).")
    @app_commands.describe(membro="O membro a ser silenciado", tempo="Duração (ex: 10m, 1h, 1d, 30s)", motivo="Motivo do silenciamento")
    @app_commands.default_permissions(moderate_members=True)
    async def mute(self, interaction: discord.Interaction, membro: discord.Member, tempo: str = "10m", motivo: str = "Não informado"):
        duracao = parse_duration(tempo)
        if duracao is None:
            await interaction.response.send_message("⚠️ Formato de tempo inválido. Use ex: `10m`, `1h`, `1d` ou `30s`.", ephemeral=True)
            return

        try:
            await membro.timeout(duracao, reason=f"{motivo} (por {interaction.user})")
            await interaction.response.send_message(f"🔇 {membro.mention} foi silenciado por `{tempo}`.\n📝 Motivo: `{motivo}`")

            # Log
            log_embed = discord.Embed(title="🔇 Membro Silenciado", color=discord.Color.dark_grey(), timestamp=datetime.now(timezone.utc))
            log_embed.add_field(name="Membro", value=f"{membro.mention} (`{membro.id}`)", inline=True)
            log_embed.add_field(name="Duração", value=tempo, inline=True)
            log_embed.add_field(name="Moderador", value=interaction.user.mention, inline=True)
            log_embed.add_field(name="Motivo", value=motivo, inline=False)
            await self._send_log(interaction.guild, log_embed)
        except discord.Forbidden:
            await interaction.response.send_message("❌ Permissão insuficiente da Hannya para silenciar este membro.", ephemeral=True)

    # ============================================================
    # /unmute
    # ============================================================
    @app_commands.command(name="unmute", description="Remove o silêncio de um usuário antecipadamente.")
    @app_commands.describe(membro="O membro que terá o silêncio removido")
    @app_commands.default_permissions(moderate_members=True)
    async def unmute(self, interaction: discord.Interaction, membro: discord.Member):
        try:
            await membro.timeout(None, reason=f"Desmutado por {interaction.user}")
            await interaction.response.send_message(f"🔊 O silêncio de {membro.mention} foi removido com sucesso!")
        except discord.Forbidden:
            await interaction.response.send_message("❌ Permissão insuficiente da Hannya para remover o silêncio.", ephemeral=True)

    # ============================================================
    # /warn
    # ============================================================
    @app_commands.command(name="warn", description="Aplica uma advertência formal a um membro e registra no histórico.")
    @app_commands.describe(membro="O membro advertido", motivo="Motivo detalhado da advertência")
    @app_commands.default_permissions(moderate_members=True)
    async def warn(self, interaction: discord.Interaction, membro: discord.Member, motivo: str):
        if membro.bot:
            await interaction.response.send_message("⚠️ Não é possível advertir bots.", ephemeral=True)
            return

        warn_id = add_warn(interaction.guild_id, membro.id, interaction.user.id, motivo)
        total_warns = len(get_warns(interaction.guild_id, membro.id))

        await interaction.response.send_message(
            f"⚠️ **{membro.display_name}** recebeu uma advertência (ID: `#{warn_id}`).\n"
            f"📝 **Motivo:** `{motivo}`\n"
            f"📊 **Total de Advertências:** `{total_warns}`"
        )

        # Envia DM ao usuário avisando
        try:
            dm_embed = discord.Embed(
                title=f"⚠️ Você recebeu uma advertência em {interaction.guild.name}",
                description=f"**Motivo:** {motivo}\n**Aviso ID:** #{warn_id}\n**Total de Avisos:** {total_warns}",
                color=discord.Color.yellow(),
                timestamp=datetime.now(timezone.utc)
            )
            await membro.send(embed=dm_embed)
        except (discord.Forbidden, discord.HTTPException):
            pass

        # Log
        log_embed = discord.Embed(title="⚠️ Advertência Aplicada", color=discord.Color.yellow(), timestamp=datetime.now(timezone.utc))
        log_embed.add_field(name="Membro", value=f"{membro.mention} (`{membro.id}`)", inline=True)
        log_embed.add_field(name="Moderador", value=interaction.user.mention, inline=True)
        log_embed.add_field(name="Aviso ID", value=f"#{warn_id}", inline=True)
        log_embed.add_field(name="Motivo", value=motivo, inline=False)
        await self._send_log(interaction.guild, log_embed)

    # ============================================================
    # /warns
    # ============================================================
    @app_commands.command(name="warns", description="Consulta todas as advertências registradas de um membro.")
    @app_commands.describe(membro="O membro para consultar o histórico de avisos")
    @app_commands.default_permissions(moderate_members=True)
    async def warns(self, interaction: discord.Interaction, membro: discord.Member):
        lista = get_warns(interaction.guild_id, membro.id)
        if not lista:
            await interaction.response.send_message(f"✅ **{membro.display_name}** possui um histórico limpo! Nenhuma advertência encontrada.", ephemeral=True)
            return

        embed = discord.Embed(
            title=f"📜 Histórico de Advertências — {membro.display_name}",
            description=f"Total acumulado: `{len(lista)}` advertência(s)",
            color=discord.Color.gold(),
            timestamp=datetime.now(timezone.utc)
        )
        embed.set_thumbnail(url=membro.display_avatar.url)

        for w in lista[-15:]:  # Mostra até os 15 mais recentes
            mod = interaction.guild.get_member(w["moderator_id"])
            mod_nome = mod.display_name if mod else f"ID: {w['moderator_id']}"
            embed.add_field(
                name=f"Aviso #{w['id']} — {w['created_at']}",
                value=f"**Motivo:** {w['reason']}\n**Moderador:** {mod_nome}",
                inline=False
            )

        await interaction.response.send_message(embed=embed)

    # ============================================================
    # /unwarn
    # ============================================================
    @app_commands.command(name="unwarn", description="Remove uma advertência específica pelo seu ID.")
    @app_commands.describe(aviso_id="O ID numérico da advertência a ser removida (veja em /warns)")
    @app_commands.default_permissions(moderate_members=True)
    async def unwarn(self, interaction: discord.Interaction, aviso_id: int):
        removido = remove_warn(aviso_id, interaction.guild_id)
        if removido:
            await interaction.response.send_message(f"✅ Advertência `#{aviso_id}` foi removida com sucesso do histórico!")
        else:
            await interaction.response.send_message(f"❌ Advertência `#{aviso_id}` não foi encontrada neste servidor.", ephemeral=True)

    # ============================================================
    # /lock
    # ============================================================
    @app_commands.command(name="lock", description="Tranca o canal impedindo envio de mensagens por membros comuns.")
    @app_commands.default_permissions(manage_channels=True)
    async def lock(self, interaction: discord.Interaction):
        overwrite = interaction.channel.overwrites_for(interaction.guild.default_role)
        overwrite.send_messages = False
        await interaction.channel.set_permissions(interaction.guild.default_role, overwrite=overwrite)
        await interaction.response.send_message("🔐 Este canal foi **trancado** pela moderação!")

    # ============================================================
    # /unlock
    # ============================================================
    @app_commands.command(name="unlock", description="Destranca o canal permitindo que membros comuns voltem a falar.")
    @app_commands.default_permissions(manage_channels=True)
    async def unlock(self, interaction: discord.Interaction):
        overwrite = interaction.channel.overwrites_for(interaction.guild.default_role)
        overwrite.send_messages = True
        await interaction.channel.set_permissions(interaction.guild.default_role, overwrite=overwrite)
        await interaction.response.send_message("🔓 Este canal foi **destrancado**!")


async def setup(bot: commands.Bot):
    await bot.add_cog(Admin(bot))