import os
from pathlib import Path
from dotenv import load_dotenv

base_dir = Path(__file__).resolve().parent
env_file = base_dir / ".env"
if not env_file.exists():
    env_file = base_dir.parent / ".env"

load_dotenv(dotenv_path=env_file)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
CHECK_INTERVAL_SECONDS = int(os.getenv("CHECK_INTERVAL_SECONDS", "60"))
