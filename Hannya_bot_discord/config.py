# config.py
import os

# Token do bot (use variável de ambiente)
TOKEN = os.getenv("DISCORD_TOKEN", "SEU_TOKEN_AQUI")  # substitua se quiser testar localmente

# IDs de canais
LOG_CHANNEL_ID = 123456789012345678  # substitua pelo ID real
WELCOME_CHANNEL_ID = 123456789012345678

# Prefixo
COMMAND_PREFIX = "/"
