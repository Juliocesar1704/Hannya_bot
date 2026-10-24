import asyncio
import logging
import sys
from pathlib import Path

# Adiciona o diretório atual ao sys.path para importações limpas
current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from config import TELEGRAM_BOT_TOKEN
from routers import general, monitoring, tools, subnet, system, security
from routers.monitoring import run_monitoring_worker
from services.webhook import start_webhook_server

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("HannyaTelegramBot")


async def set_bot_commands(bot: Bot):
    """Configura o menu de comandos azul nativo do Telegram."""
    commands = [
        types.BotCommand(command="start", description="Menu principal interativo"),
        types.BotCommand(command="status", description="Painel de saúde com gráficos e botões"),
        types.BotCommand(command="grafico", description="Gráfico de latência do host monitorado"),
        types.BotCommand(command="monitorar", description="Cadastrar ou gerenciar hosts vigiados"),
        types.BotCommand(command="ping", description="Latência e perda de pacotes (ICMP)"),
        types.BotCommand(command="traceroute", description="Rastreamento de saltos/hops na rota"),
        types.BotCommand(command="whois", description="ASN, ISP e geolocalização do IP"),
        types.BotCommand(command="mac", description="Identificar fabricante da placa de rede"),
        types.BotCommand(command="subnet", description="Calculadora de sub-redes IPv4/IPv6"),
        types.BotCommand(command="vlsm", description="Calculadora de sub-redes VLSM"),
        types.BotCommand(command="cisco", description="Scripts e templates Cisco IOS (CCNA)"),
        types.BotCommand(command="headers", description="Auditoria OWASP de cabeçalhos de segurança"),
        types.BotCommand(command="blacklist", description="Consulta de IP em listas DNSBL"),
        types.BotCommand(command="dns", description="Consultar registros DNS (A, MX, etc.)"),
        types.BotCommand(command="cert", description="Validade do certificado SSL/TLS"),
        types.BotCommand(command="webhook", description="Central de webhooks para Zabbix/Grafana"),
        types.BotCommand(command="server", description="Telemetria de CPU, RAM e tráfego"),
        types.BotCommand(command="ajuda", description="Manual completo de todos os recursos"),
    ]
    await bot.set_my_commands(commands)
    logger.info("✔ Menu de comandos nativo do Telegram configurado com sucesso!")


async def main():
    if not TELEGRAM_BOT_TOKEN or TELEGRAM_BOT_TOKEN == "seu_token_do_telegram_aqui":
        logger.critical("❌ O token do bot do Telegram não foi configurado no arquivo .env!")
        return

    logger.info("🚀 Inicializando Hannya NetWatch (Telegram Bot)...")

    bot = Bot(
        token=TELEGRAM_BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
    )
    dp = Dispatcher()

    # Registro de Routers
    dp.include_router(general.router)
    dp.include_router(monitoring.router)
    dp.include_router(tools.router)
    dp.include_router(subnet.router)
    dp.include_router(security.router)
    dp.include_router(system.router)

    # Configura comandos no menu do Telegram
    await set_bot_commands(bot)

    # Inicia a Sentinela de monitoramento em segundo plano
    asyncio.create_task(run_monitoring_worker(bot))

    # Inicia o Servidor de Webhooks externo em segundo plano
    asyncio.create_task(start_webhook_server(bot))

    me = await bot.get_me()
    logger.info(f"🤖 Bot conectado com sucesso como: {me.first_name} (@{me.username})")
    logger.info("📡 Escutando mensagens e monitorando hosts ativos...")

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Bot do Telegram encerrado manualmente.")
