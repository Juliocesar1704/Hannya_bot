import os
from pathlib import Path
from dotenv import load_dotenv

# ============================================================
# CARREGAMENTO DO .ENV
# ============================================================
# Procura o arquivo .env no diretório local ou no diretório pai
base_dir = Path(__file__).resolve().parent
env_file = base_dir / ".env"
if not env_file.exists():
    env_file = base_dir.parent / ".env"

load_dotenv(dotenv_path=env_file)

# ============================================================
# CONFIGURAÇÕES GERAIS DO BOT
# ============================================================
TOKEN = os.getenv("DISCORD_TOKEN", "COLOQUE_SEU_TOKEN_AQUI")
APPLICATION_ID = int(os.getenv("APPLICATION_ID", "0"))
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID", "0"))
WELCOME_CHANNEL_ID = int(os.getenv("WELCOME_CHANNEL_ID", "0"))