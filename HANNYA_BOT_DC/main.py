import time
import asyncio
import logging
import discord
from discord.ext import commands
from config import TOKEN

# ============================================================
# LOGGING
# ============================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)

# ============================================================
# INTENTS OTIMIZADOS
# ============================================================
intents = discord.Intents.default()
intents.members = True
intents.message_content = True  # NECESSÁRIO PARA PREFIXO

# ============================================================
# BOT CONFIG
# ============================================================
bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    help_command=None  # help custom será criado depois
)

# ============================================================
# LISTA DE COGS
# ============================================================
COGS = (
    "cogs.events",
    "cogs.fun",
    "cogs.admin",
)

# ============================================================
# FUNÇÃO PARA CARREGAR COGS
# ============================================================
async def load_extensions():
    logging.info("🧩 Carregando módulos...")
    for ext in COGS:
        try:
            start = time.time()
            await bot.load_extension(ext)
            elapsed = (time.time() - start) * 1000
            logging.info(f"✔ Cog carregada: {ext} ({elapsed:.1f} ms)")
        except Exception as e:
            logging.error(f"❌ Erro ao carregar {ext}: {e}")

# ============================================================
# EVENTO ON_READY
# ============================================================
@bot.event
async def on_ready():
    logging.info(f"🤖 Bot conectado como: {bot.user} (ID: {bot.user.id})")
    await bot.change_presence(
        activity=discord.Game(name="Usando prefixo !"),
        status=discord.Status.online
    )
    logging.info("🌐 Status atualizado e bot pronto para uso.")

# ============================================================
# MAIN
# ============================================================
async def main():
    logging.info("🚀 Inicializando bot...")
    await load_extensions()
    logging.info("🔧 Conectando ao Discord…")
    await bot.start(TOKEN)

# ============================================================
# EXECUÇÃO
# ============================================================
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("🛑 Bot encerrado manualmente.")
