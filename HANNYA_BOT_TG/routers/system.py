# routers/system.py
from aiogram import Router, types
from aiogram.filters import Command
from services.network import get_system_telemetry

router = Router()


@router.message(Command("server", "sistema", "hardware"))
async def cmd_server(message: types.Message):
    m = get_system_telemetry()

    cpu_bar = "█" * int(m['cpu_percent'] / 10) + "░" * (10 - int(m['cpu_percent'] / 10))
    ram_bar = "█" * int(m['ram_percent'] / 10) + "░" * (10 - int(m['ram_percent'] / 10))
    disk_bar = "█" * int(m['disk_percent'] / 10) + "░" * (10 - int(m['disk_percent'] / 10))

    texto = (
        "🖥️ **Telemetria do Servidor Host — Hannya NetWatch**\n\n"
        f"**Processador (CPU):** `{m['cpu_percent']}%` ({m['cpu_cores']} núcleos logicos)\n"
        f"`[{cpu_bar}]`\n\n"
        f"**Memória RAM:** `{m['ram_percent']}%` (`{m['ram_used']}` / `{m['ram_total']}`)\n"
        f"`[{ram_bar}]`\n\n"
        f"**Armazenamento (Disco):** `{m['disk_percent']}%` (Livre: `{m['disk_free']}`)\n"
        f"`[{disk_bar}]`\n\n"
        "🌐 **Tráfego de Rede (Interfaces de Rede):**\n"
        f"• **Enviados (Upload):** `{m['bytes_sent']}` (`{m['packets_sent']:,}` pacotes)\n"
        f"• **Recebidos (Download):** `{m['bytes_recv']}` (`{m['packets_recv']:,}` pacotes)\n\n"
        f"⏱️ **Sistema Operacional Ativo desde:**\n`{m['boot_time']}`"
    )

    await message.answer(texto, parse_mode="Markdown")
