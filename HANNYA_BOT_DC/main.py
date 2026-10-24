import os
import sys
import time
import asyncio
import logging
from pathlib import Path

# Garante que o diretório atual de HANNYA_BOT_DC esteja no sys.path
current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

import discord
from discord import app_commands
from discord.ext import commands
from config import TOKEN

# ============================================================
# LOGGING ESTRUTURADO
# ============================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("HannyaBot")

# ============================================================
# INTENTS
# ============================================================
intents = discord.Intents.default()
intents.members = True
intents.message_content = True  # Para auditoria, anti-spam e anti-convites

# ============================================================
# BOT CONFIG (FOCO EM COMANDOS SLASH NATIVOS)
# ============================================================
bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    help_command=None
)

# ============================================================
# LISTA DE COGS
# ============================================================
COGS = (
    "cogs.events",
    "cogs.fun",
    "cogs.admin",
    "cogs.info",
    "cogs.music",
)

# ============================================================
# CARREGAMENTO DE EXTENSÕES (COGS)
# ============================================================
async def load_extensions():
    logger.info("🧩 Carregando módulos...")
    for ext in COGS:
        try:
            start = time.time()
            await bot.load_extension(ext)
            elapsed = (time.time() - start) * 1000
            logger.info(f"✔ Cog carregada com sucesso: {ext} ({elapsed:.1f} ms)")
        except Exception as e:
            logger.error(f"❌ Erro ao carregar extensão {ext}: {e}", exc_info=True)

# ============================================================
# TRATAMENTO DE ERROS DOS COMANDOS SLASH
# ============================================================
@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        perms = ", ".join(error.missing_permissions)
        msg = f"🚫 Você não tem permissão para usar este comando. Permissão necessária: `{perms}`."
    elif isinstance(error, app_commands.BotMissingPermissions):
        perms = ", ".join(error.missing_permissions)
        msg = f"⚠️ A Hannya não possui as permissões necessárias no servidor: `{perms}`."
    elif isinstance(error, app_commands.CommandOnCooldown):
        msg = f"⏳ Aguarde mais `{error.retry_after:.1f}` segundos para usar este comando novamente."
    else:
        logger.error(f"Erro no comando Slash '{interaction.command.name if interaction.command else 'desconhecido'}': {error}", exc_info=True)
        msg = f"❌ Ocorreu um erro ao processar o comando: `{error}`"

    try:
        if interaction.response.is_done():
            await interaction.followup.send(msg, ephemeral=True)
        else:
            await interaction.response.send_message(msg, ephemeral=True)
    except discord.HTTPException:
        pass

# ============================================================
# EVENTO ON_READY & SINCRONIZAÇÃO INSTANTÂNEA DE COMANDOS SLASH
# ============================================================
@bot.event
async def on_ready():
    logger.info(f"🤖 Bot conectado como: {bot.user} (ID: {bot.user.id})")
    logger.info("⚡ Sincronizando comandos Slash (/)...")

    # Sincroniza diretamente com cada servidor onde o bot está presente para ativação imediata
    for guild in bot.guilds:
        try:
            bot.tree.copy_global_to(guild=guild)
            synced = await bot.tree.sync(guild=guild)
            logger.info(f"✔ Sincronizados {len(synced)} comandos Slash instantaneamente com o servidor '{guild.name}'!")
        except Exception as e:
            logger.error(f"Erro ao sincronizar comandos com '{guild.name}': {e}")

    try:
        synced_global = await bot.tree.sync()
        logger.info(f"✔ Sincronizados {len(synced_global)} comandos Slash no escopo global!")
    except Exception as e:
        logger.error(f"Erro ao sincronizar globalmente: {e}")

    logger.info("🌐 Hannya Bot está pronto e operacional com comandos Slash!")

# ============================================================
# MAIN
# ============================================================
async def main():
    if not TOKEN or TOKEN == "COLOQUE_SEU_TOKEN_AQUI":
        logger.critical("❌ O token do bot não está configurado! Verifique seu arquivo .env.")
        return

    logger.info("🚀 Inicializando Hannya Bot...")
    await load_extensions()
    logger.info("🔧 Conectando à API do Discord...")
    await bot.start(TOKEN)

# ============================================================
# EXECUÇÃO
# ============================================================
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Bot encerrado manualmente.")
