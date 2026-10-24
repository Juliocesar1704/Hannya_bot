# cogs/events.py
import re
import time
import random
from collections import defaultdict
from datetime import datetime, timezone
import discord
from discord import app_commands
from discord.ext import commands, tasks
from config import LOG_CHANNEL_ID, WELCOME_CHANNEL_ID

# Expressão regular para identificar links de convite do Discord
DISCORD_INVITE_REGEX = re.compile(
    r"(?:https?://)?(?:www\.)?(?:discord\.(?:gg|io|me|li)|discord(?:app)?\.com/invite)/[a-zA-Z0-9]+",
    re.IGNORECASE
)


class Events(commands.Cog):
    """Módulo de eventos, moderação automática, presença rotativa e ajuda."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Rastreamento de spam por usuário: {user_id: [timestamp, timestamp, ...]}
        self.user_message_times = defaultdict(list)
        self.rotate_status.start()

    def cog_unload(self):
        self.rotate_status.cancel()

    # ============================================================
    # TAREFA DE STATUS / PRESENÇA ROTATIVA (A CADA 2 MINUTOS)
    # ============================================================
    @tasks.loop(minutes=2)
    async def rotate_status(self):
        await self.bot.wait_until_ready()

        total_membros = sum(g.member_count or len(g.members) for g in self.bot.guilds)

        frases = [
            (discord.ActivityType.watching, "o Refúgio de Atlas 🏮"),
            (discord.ActivityType.listening, "seus chamados em /ajuda ✨"),
            (discord.ActivityType.playing, f"com {total_membros} almas no servidor 👹"),
            (discord.ActivityType.watching, "as sombras e a ordem 🎭"),
            (discord.ActivityType.listening, "os sussurros da máscara de Hannya 🌸"),
        ]

        tipo_atividade, texto = random.choice(frases)
        await self.bot.change_presence(
            activity=discord.Activity(type=tipo_atividade, name=texto),
            status=discord.Status.online
        )

    # ============================================================
    # COMANDO SLASH: /ajuda
    # ============================================================
    @app_commands.command(name="ajuda", description="Exibe a lista completa de todos os comandos Slash da Hannya.")
    async def ajuda(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🏮 Centro de Comandos — Hannya Bot",
            description=(
                "Todos os comandos funcionam agora exclusivamente pelo menu nativo **Slash (`/`)** do Discord.\n"
                "Comece a digitar `/` no chat para interagir com o preenchimento automático!"
            ),
            color=discord.Color.red(),
            timestamp=datetime.now(timezone.utc)
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)

        embed.add_field(
            name="🛡️ Moderação & Gestão",
            value=(
                "`/limpar` — Apaga mensagens em massa\n"
                "`/kick` — Expulsa um membro\n"
                "`/ban` — Bane um usuário\n"
                "`/unban` — Desbane por ID ou nome\n"
                "`/mute` — Silencia temporariamente (Timeout)\n"
                "`/unmute` — Remove o silêncio\n"
                "`/warn` — Aplica advertência registrada\n"
                "`/warns` — Consulta histórico de avisos\n"
                "`/unwarn` — Remove advertência por ID\n"
                "`/lock` & `/unlock` — Tranca ou destranca o canal\n"
                "`/falar` & `/anuncio` — Mensagens oficiais da Hannya"
            ),
            inline=False
        )

        embed.add_field(
            name="ℹ️ Informações",
            value=(
                "`/userinfo` — Perfil e cargos detalhados de um membro\n"
                "`/serverinfo` — Estatísticas e dados do servidor"
            ),
            inline=False
        )

        embed.add_field(
            name="🎵 Música & Voz (YouTube & Spotify)",
            value=(
                "`/tocar` — Toca uma música (YouTube, Spotify Playlist/Faixa ou busca por nome)\n"
                "`/pular` — Pula a faixa atual\n"
                "`/pausar` & `/continuar` — Pausa ou retoma o áudio\n"
                "`/loop` — Ativa ou desativa repetição da faixa\n"
                "`/parar` — Para a música e desconecta do canal\n"
                "`/fila` — Exibe as faixas da fila de reprodução\n"
                "`/tocando` — Detalhes da música em reprodução\n"
                "`/conectar` & `/desconectar` — Gerencia presença no canal de voz"
            ),
            inline=False
        )

        embed.add_field(
            name="🎭 Diversão & Interação",
            value=(
                "`/ping` — Latência com a API\n"
                "`/ola` — Saudação da Hannya\n"
                "`/dado` — Rola um dado de N lados\n"
                "`/moeda` — Joga Cara ou Coroa\n"
                "`/piada` — Piadas nerd/dev\n"
                "`/8ball` — Respostas místicas\n"
                "`/hug` & `/kiss` — Abraços e beijos virtuais\n"
                "`/fortune` — Biscoito da sorte\n"
                "`/meme` — Meme aleatório\n"
                "`/numero` — Sorteia um número"
            ),
            inline=False
        )

        embed.set_footer(text=f"Solicitado por {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed)

    # ============================================================
    # SEGURANÇA: ANTI-SPAM & ANTI-LINKS DE CONVITE
    # ============================================================
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Ignora mensagens de bots ou fora de servidores
        if message.author.bot or not message.guild:
            return

        autor: discord.Member = message.author

        # Membros com permissão de administrar ou gerenciar mensagens são isentos da auto-moderação
        if autor.guild_permissions.administrator or autor.guild_permissions.manage_messages:
            return

        canal_log = message.guild.get_channel(LOG_CHANNEL_ID)

        # 1. BLOQUEIO DE CONVITES DO DISCORD
        if DISCORD_INVITE_REGEX.search(message.content):
            try:
                await message.delete()
                aviso = await message.channel.send(
                    f"⚠️ {autor.mention}, **links de convite para outros servidores não são permitidos aqui!**",
                    delete_after=6
                )
            except discord.HTTPException:
                pass

            if canal_log:
                embed_log = discord.Embed(
                    title="🚨 Link de Convite Bloqueado",
                    description=f"**Membro:** {autor.mention} (`{autor.id}`)\n**Canal:** {message.channel.mention}\n**Conteúdo:**\n```{message.content[:800]}```",
                    color=discord.Color.red(),
                    timestamp=datetime.now(timezone.utc)
                )
                try:
                    await canal_log.send(embed=embed_log)
                except discord.HTTPException:
                    pass
            return

        # 2. DETECTOR DE SPAM RÁPIDO (FLOOD)
        agora = time.time()
        self.user_message_times[autor.id] = [
            t for t in self.user_message_times[autor.id] if agora - t < 4.0
        ]
        self.user_message_times[autor.id].append(agora)

        if len(self.user_message_times[autor.id]) >= 5:
            self.user_message_times[autor.id].clear()
            try:
                await message.delete()
                await message.channel.send(
                    f"⚠️ {autor.mention}, por favor evite enviar mensagens rápidas demais (anti-spam ativo)!",
                    delete_after=5
                )
            except discord.HTTPException:
                pass

            if canal_log:
                embed_spam = discord.Embed(
                    title="⚠️ Alerta de Anti-Spam / Flood",
                    description=f"O membro {autor.mention} (`{autor.id}`) estava enviando mensagens em velocidade excessiva no canal {message.channel.mention}.",
                    color=discord.Color.orange(),
                    timestamp=datetime.now(timezone.utc)
                )
                try:
                    await canal_log.send(embed=embed_spam)
                except discord.HTTPException:
                    pass

    # ============================================================
    # EVENTO: NOVO MEMBRO ENTROU
    # ============================================================
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        canal_boas_vindas = member.guild.get_channel(WELCOME_CHANNEL_ID)
        canal_log = member.guild.get_channel(LOG_CHANNEL_ID)

        # Atribuição opcional de cargo 'Novato'
        cargo_novato = discord.utils.get(member.guild.roles, name="Novato")
        if cargo_novato:
            try:
                await member.add_roles(cargo_novato)
            except discord.Forbidden:
                pass

        cumprimentos = [
            f"👋 Boas-vindas, {member.mention}! Que bom ter você no **{member.guild.name}**!",
            f"🌟 Olá {member.mention}! Sente-se ao redor da fogueira e aproveite sua estadia!",
            f"🎉 Uma nova alma adentrou o portal! {member.mention} acabou de chegar."
        ]

        embed = discord.Embed(
            title=random.choice(["👋 Seja Bem-vindo(a)!", "🎈 Boas-vindas ao Refúgio!", "🌸 Nova Chegada!"]),
            description=random.choice(cumprimentos),
            color=discord.Color.green(),
            timestamp=datetime.now(timezone.utc)
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"Membro #{member.guild.member_count or len(member.guild.members)}")

        if canal_boas_vindas:
            try:
                await canal_boas_vindas.send(embed=embed)
            except discord.HTTPException:
                pass

        if canal_log:
            try:
                log_embed = discord.Embed(
                    title="📥 Novo Membro",
                    description=f"**{member}** (`{member.id}`) entrou no servidor.",
                    color=discord.Color.green(),
                    timestamp=datetime.now(timezone.utc)
                )
                log_embed.set_thumbnail(url=member.display_avatar.url)
                await canal_log.send(embed=log_embed)
            except discord.HTTPException:
                pass

        # Mensagem direta ao membro
        try:
            embed_dm = discord.Embed(
                title=f"🏮 Boas-vindas ao {member.guild.name}!",
                description=(
                    f"Olá, **{member.display_name}**!\n\n"
                    "Obrigado por se juntar à nossa comunidade.\n\n"
                    "• Dê uma olhada nos canais de avisos e regras.\n"
                    "• Para conhecer todos os comandos do servidor, digite **/ajuda** no chat!\n\n"
                    "Que a sabedoria da Hannya acompanhe seus passos! 👺"
                ),
                color=discord.Color.blurple()
            )
            await member.send(embed=embed_dm)
        except (discord.Forbidden, discord.HTTPException):
            pass

    # ============================================================
    # EVENTO: MEMBRO SAIU
    # ============================================================
    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        canal_log = member.guild.get_channel(LOG_CHANNEL_ID)
        if not canal_log:
            return

        embed = discord.Embed(
            title="📤 Membro Saiu",
            description=f"**{member}** (`{member.id}`) deixou o servidor.",
            color=discord.Color.red(),
            timestamp=datetime.now(timezone.utc)
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        try:
            await canal_log.send(embed=embed)
        except discord.HTTPException:
            pass


async def setup(bot: commands.Bot):
    await bot.add_cog(Events(bot))