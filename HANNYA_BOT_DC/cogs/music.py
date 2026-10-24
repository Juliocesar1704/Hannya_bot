# cogs/music.py
import asyncio
import logging
import time
import urllib.request
import json
import re
from collections import deque
import discord
from discord import app_commands
from discord.ext import commands
import yt_dlp
import imageio_ffmpeg

logger = logging.getLogger("HannyaMusic")

# Localiza automaticamente o executável do FFmpeg instalado pelo imageio-ffmpeg
FFMPEG_PATH = imageio_ffmpeg.get_ffmpeg_exe()

YTDL_OPTIONS = {
    'format': 'bestaudio/best',
    'extractaudio': True,
    'audioformat': 'mp3',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'ytsearch',
    'source_address': '0.0.0.0',
}

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn',
}

ytdl = yt_dlp.YoutubeDL(YTDL_OPTIONS)


def extract_spotify_metadata(url: str) -> dict | None:
    """Extrai nomes das faixas de playlists, álbuns ou músicas do Spotify sem necessidade de API keys."""
    clean = url.split("?")[0].strip()
    match = re.search(r"spotify\.com/(track|playlist|album)/([a-zA-Z0-9]+)", clean)
    if not match:
        return None

    item_type, item_id = match.groups()
    embed_url = f"https://open.spotify.com/embed/{item_type}/{item_id}"
    req = urllib.request.Request(
        embed_url,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode("utf-8")

        m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html)
        if not m:
            return None

        data = json.loads(m.group(1))
        props = data.get("props", {}).get("pageProps", {})
        entity = props.get("state", {}).get("data", {}).get("entity", {})
        title = entity.get("title", "Mídia do Spotify")

        if item_type == "track":
            artist = entity.get("subtitle", "")
            return {
                "type": "track",
                "title": title,
                "tracks": [f"{title} {artist}".strip()]
            }
        else:
            track_list = entity.get("trackList", [])
            tracks = []
            for t in track_list:
                t_title = t.get("title", "")
                t_artist = t.get("subtitle", "")
                if t_title:
                    tracks.append(f"{t_title} {t_artist}".strip())
            return {
                "type": item_type,
                "title": title,
                "tracks": tracks
            }
    except Exception as e:
        logger.error(f"Erro ao extrair dados do Spotify: {e}")
        return None


class GuildMusicPlayer:
    """Controlador de fila e reprodução para cada servidor."""

    def __init__(self, bot: commands.Bot, guild_id: int):
        self.bot = bot
        self.guild_id = guild_id
        self.queue = deque()
        self.current = None
        self.is_looping = False
        self.text_channel = None

    def get_voice_client(self) -> discord.VoiceClient | None:
        guild = self.bot.get_guild(self.guild_id)
        if guild:
            return guild.voice_client
        return None

    async def resolve_track(self, raw_track: dict) -> dict | None:
        """Resolve uma busca em stream de áudio real do YouTube sob demanda."""
        loop = asyncio.get_event_loop()
        query = raw_track["query"]
        try:
            busca_query = query if (query.startswith("http://") or query.startswith("https://")) else f"ytsearch:{query}"
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(busca_query, download=False))
            if "entries" in data and data["entries"]:
                info = data["entries"][0]
            else:
                info = data

            dur_segundos = info.get("duration") or 0
            dur_formatada = time.strftime("%H:%M:%S", time.gmtime(dur_segundos)) if dur_segundos >= 3600 else time.strftime("%M:%S", time.gmtime(dur_segundos))

            return {
                "title": info.get("title", raw_track.get("title", query)),
                "stream_url": info.get("url"),
                "webpage_url": info.get("webpage_url", query),
                "duration": dur_formatada,
                "thumbnail": info.get("thumbnail"),
                "requester": raw_track["requester"],
                "is_resolved": True
            }
        except Exception as e:
            logger.error(f"Erro ao resolver faixa '{query}': {e}")
            return None

    async def play_next(self):
        vc = self.get_voice_client()
        if not vc or not vc.is_connected():
            return

        if self.is_looping and self.current:
            track = self.current
        elif self.queue:
            raw_track = self.queue.popleft()
            if not raw_track.get("is_resolved", True):
                track = await self.resolve_track(raw_track)
                if not track:
                    # Se falhar uma música da playlist, pula para a próxima automaticamente
                    await self.play_next()
                    return
            else:
                track = raw_track
            self.current = track
        else:
            self.current = None
            if self.text_channel:
                try:
                    await self.text_channel.send("🏮 A fila de reprodução terminou. Ficarei por aqui aguardando novos sons!")
                except discord.HTTPException:
                    pass
            return

        def after_playing(error):
            if error:
                logger.error(f"Erro na reprodução: {error}")
            coro = self.play_next()
            asyncio.run_coroutine_threadsafe(coro, self.bot.loop)

        try:
            source = discord.FFmpegPCMAudio(track["stream_url"], executable=FFMPEG_PATH, **FFMPEG_OPTIONS)
            vc.play(source, after=after_playing)

            if self.text_channel and not self.is_looping:
                embed = discord.Embed(
                    title="🎶 Tocando Agora",
                    description=f"[{track['title']}]({track['webpage_url']})",
                    color=discord.Color.red()
                )
                if track.get("thumbnail"):
                    embed.set_thumbnail(url=track["thumbnail"])
                embed.add_field(name="⏱️ Duração", value=f"`{track['duration']}`", inline=True)
                embed.add_field(name="👤 Solicitado por", value=track['requester'].mention, inline=True)
                await self.text_channel.send(embed=embed)
        except Exception as e:
            logger.error(f"Falha ao iniciar áudio: {e}")
            if self.text_channel:
                await self.text_channel.send(f"❌ Não foi possível reproduzir `{track['title']}`: {e}")
            await self.play_next()


class Music(commands.Cog):
    """Módulo completo de música e voz para a Hannya com suporte a YouTube e Spotify."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.players: dict[int, GuildMusicPlayer] = {}

    def get_player(self, guild_id: int) -> GuildMusicPlayer:
        if guild_id not in self.players:
            self.players[guild_id] = GuildMusicPlayer(self.bot, guild_id)
        return self.players[guild_id]

    async def _ensure_voice(self, interaction: discord.Interaction) -> discord.VoiceClient | None:
        """Garante que o bot esteja conectado ao canal de voz do usuário."""
        if not interaction.user.voice or not interaction.user.voice.channel:
            await interaction.followup.send("❌ Você precisa estar conectado a um canal de voz para tocar música!", ephemeral=True)
            return None

        channel = interaction.user.voice.channel
        vc = interaction.guild.voice_client

        if vc:
            if vc.channel.id != channel.id:
                await vc.move_to(channel)
            return vc
        else:
            try:
                return await channel.connect()
            except Exception as e:
                await interaction.followup.send(f"❌ Erro ao conectar ao canal de voz: {e}", ephemeral=True)
                return None

    # ============================================================
    # /tocar
    # ============================================================
    @app_commands.command(name="tocar", description="Toca uma música ou playlist (suporta YouTube, Spotify e busca por nome).")
    @app_commands.describe(busca="Nome da música, link do YouTube ou link de Playlist/Música do Spotify")
    async def tocar(self, interaction: discord.Interaction, busca: str):
        await interaction.response.defer()

        vc = await self._ensure_voice(interaction)
        if not vc:
            return

        player = self.get_player(interaction.guild_id)
        player.text_channel = interaction.channel
        loop = asyncio.get_event_loop()

        # ========================================================
        # 1. TRATAMENTO DE LINKS DO SPOTIFY (PLAYLIST, ÁLBUM OU FAIXA)
        # ========================================================
        if "spotify.com" in busca:
            await interaction.followup.send("🟢 Lendo dados do Spotify... aguarde um instante!")
            spotify_data = await loop.run_in_executor(None, lambda: extract_spotify_metadata(busca))

            if not spotify_data or not spotify_data.get("tracks"):
                await interaction.channel.send("❌ Não foi possível carregar as músicas deste link do Spotify. Verifique se a playlist/música é pública.")
                return

            tipo = spotify_data["type"]
            titulo_spotify = spotify_data["title"]
            lista_faixas = spotify_data["tracks"]

            # Adiciona as faixas na fila como buscas sob demanda
            for nome_musica in lista_faixas:
                player.queue.append({
                    "title": nome_musica,
                    "query": nome_musica,
                    "requester": interaction.user,
                    "is_resolved": False
                })

            embed = discord.Embed(
                title=f"🟢 Spotify: {tipo.capitalize()} Carregada!",
                description=f"**[{titulo_spotify}]({busca})**",
                color=discord.Color.green()
            )
            embed.add_field(name="Total de Músicas", value=f"`{len(lista_faixas)}` faixas", inline=True)
            embed.add_field(name="Posição Inicial na Fila", value=f"`#{len(player.queue) - len(lista_faixas) + 1}`", inline=True)
            embed.set_footer(text=f"Adicionado por {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)
            await interaction.channel.send(embed=embed)

            # Se não estiver tocando nada, inicia imediatamente
            if not vc.is_playing() and not vc.is_paused():
                await player.play_next()
            return

        # ========================================================
        # 2. BUSCA NORMAL (YOUTUBE OU LINK DIRETO)
        # ========================================================
        try:
            busca_query = busca if (busca.startswith("http://") or busca.startswith("https://")) else f"ytsearch:{busca}"
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(busca_query, download=False))
        except Exception as e:
            await interaction.followup.send(f"❌ Erro ao buscar música no YouTube: `{e}`")
            return

        if "entries" in data:
            if not data["entries"]:
                await interaction.followup.send("⚠️ Nenhum resultado encontrado para a sua busca.", ephemeral=True)
                return
            info = data["entries"][0]
        else:
            info = data

        dur_segundos = info.get("duration") or 0
        dur_formatada = time.strftime("%H:%M:%S", time.gmtime(dur_segundos)) if dur_segundos >= 3600 else time.strftime("%M:%S", time.gmtime(dur_segundos))

        track = {
            "title": info.get("title", "Faixa Desconhecida"),
            "stream_url": info.get("url"),
            "webpage_url": info.get("webpage_url", busca),
            "duration": dur_formatada,
            "thumbnail": info.get("thumbnail"),
            "requester": interaction.user,
            "is_resolved": True
        }

        if vc.is_playing() or vc.is_paused():
            player.queue.append(track)
            embed = discord.Embed(
                title="📥 Adicionado à Fila",
                description=f"[{track['title']}]({track['webpage_url']})",
                color=discord.Color.blue()
            )
            if track["thumbnail"]:
                embed.set_thumbnail(url=track["thumbnail"])
            embed.add_field(name="Posição na Fila", value=f"`#{len(player.queue)}`", inline=True)
            embed.add_field(name="Duração", value=f"`{track['duration']}`", inline=True)
            await interaction.followup.send(embed=embed)
        else:
            player.queue.append(track)
            await interaction.followup.send(f"🎶 Preparando: **{track['title']}**...")
            await player.play_next()

    # ============================================================
    # /loop
    # ============================================================
    @app_commands.command(name="loop", description="Ativa ou desativa a repetição contínua da música atual.")
    async def loop(self, interaction: discord.Interaction):
        player = self.get_player(interaction.guild_id)
        if not player.current:
            await interaction.response.send_message("⚠️ Nenhuma música tocando no momento.", ephemeral=True)
            return

        player.is_looping = not player.is_looping
        status = "ativada 🔂" if player.is_looping else "desativada ➡️"
        await interaction.response.send_message(f"🔁 Repetição da música atual foi **{status}**!")

    # ============================================================
    # /pular
    # ============================================================
    @app_commands.command(name="pular", description="Pula a música que está tocando no momento.")
    async def pular(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        if not vc or not vc.is_playing():
            await interaction.response.send_message("⚠️ Não há nenhuma música tocando no momento.", ephemeral=True)
            return

        player = self.get_player(interaction.guild_id)
        player.is_looping = False
        vc.stop()
        await interaction.response.send_message("⏭️ A música atual foi pulada!")

    # ============================================================
    # /pausar
    # ============================================================
    @app_commands.command(name="pausar", description="Pausa a música atual.")
    async def pausar(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        if not vc or not vc.is_playing():
            await interaction.response.send_message("⚠️ Nenhuma música está tocando para pausar.", ephemeral=True)
            return

        vc.pause()
        await interaction.response.send_message("⏸️ Música pausada!")

    # ============================================================
    # /continuar
    # ============================================================
    @app_commands.command(name="continuar", description="Retoma a música pausada.")
    async def continuar(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        if not vc or not vc.is_paused():
            await interaction.response.send_message("⚠️ A música não está pausada.", ephemeral=True)
            return

        vc.resume()
        await interaction.response.send_message("▶️ Música retomada!")

    # ============================================================
    # /parar
    # ============================================================
    @app_commands.command(name="parar", description="Para a música, esvazia a fila e desconecta a Hannya do canal.")
    async def parar(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        player = self.get_player(interaction.guild_id)
        player.queue.clear()
        player.current = None
        player.is_looping = False

        if vc:
            await vc.disconnect()
            await interaction.response.send_message("🛑 Reprodução interrompida e Hannya desconectada do canal de voz.")
        else:
            await interaction.response.send_message("⚠️ A Hannya não está conectada a nenhum canal de voz.", ephemeral=True)

    # ============================================================
    # /fila
    # ============================================================
    @app_commands.command(name="fila", description="Mostra as músicas que estão na fila de reprodução.")
    async def fila(self, interaction: discord.Interaction):
        player = self.get_player(interaction.guild_id)

        if not player.current and not player.queue:
            await interaction.response.send_message("📭 A fila de reprodução está vazia no momento.", ephemeral=True)
            return

        embed = discord.Embed(
            title="📜 Fila de Reprodução — Hannya",
            color=discord.Color.red()
        )

        if player.current:
            dur = player.current.get('duration', 'Ao vivo')
            url = player.current.get('webpage_url', '#')
            embed.add_field(
                name="🔊 Tocando Agora",
                value=f"[{player.current['title']}]({url}) | `{dur}` (Pedido por {player.current['requester'].mention})",
                inline=False
            )

        if player.queue:
            itens = []
            for i, t in enumerate(list(player.queue)[:15], start=1):
                nome = t.get('title', 'Faixa')
                dur = t.get('duration', 'Spotify/Fila')
                itens.append(f"`{i}.` **{nome}** — `{dur}`")
            
            resto = len(player.queue) - 15
            if resto > 0:
                itens.append(f"\n*...e mais `{resto}` música(s) na fila.*")

            embed.add_field(name=f"⏳ Próximas Faixas ({len(player.queue)})", value="\n".join(itens), inline=False)

        await interaction.response.send_message(embed=embed)

    # ============================================================
    # /tocando
    # ============================================================
    @app_commands.command(name="tocando", description="Exibe detalhes completos sobre a faixa em reprodução.")
    async def tocando(self, interaction: discord.Interaction):
        player = self.get_player(interaction.guild_id)
        if not player.current:
            await interaction.response.send_message("⚠️ Nenhuma faixa sendo reproduzida no momento.", ephemeral=True)
            return

        t = player.current
        embed = discord.Embed(
            title="🎵 Faixa em Reprodução",
            description=f"**[{t['title']}]({t.get('webpage_url', '#')})**",
            color=discord.Color.red()
        )
        if t.get("thumbnail"):
            embed.set_thumbnail(url=t["thumbnail"])
        embed.add_field(name="⏱️ Duração", value=f"`{t.get('duration', 'Indefinido')}`", inline=True)
        embed.add_field(name="👤 Pedido por", value=t["requester"].mention, inline=True)
        embed.add_field(name="🔁 Repetição", value="Ativada" if player.is_looping else "Desativada", inline=True)
        await interaction.response.send_message(embed=embed)

    # ============================================================
    # /conectar & /desconectar
    # ============================================================
    @app_commands.command(name="conectar", description="Conecta a Hannya ao canal de voz onde você está.")
    async def conectar(self, interaction: discord.Interaction):
        if not interaction.user.voice or not interaction.user.voice.channel:
            await interaction.response.send_message("❌ Você precisa estar em um canal de voz!", ephemeral=True)
            return

        ch = interaction.user.voice.channel
        vc = interaction.guild.voice_client
        if vc:
            await vc.move_to(ch)
        else:
            await ch.connect()
        await interaction.response.send_message(f"🎧 Hannya conectada ao canal **{ch.name}**!")

    @app_commands.command(name="desconectar", description="Desconecta a Hannya do canal de voz.")
    async def desconectar(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        if vc:
            await vc.disconnect()
            await interaction.response.send_message("👋 Desconectada do canal de voz.")
        else:
            await interaction.response.send_message("⚠️ Não estou conectada a nenhum canal de voz.", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Music(bot))
