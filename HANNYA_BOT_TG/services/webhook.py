# services/webhook.py
import logging
from aiohttp import web
from aiogram import Bot
from config import WEBHOOK_HOST, WEBHOOK_PORT, ADMIN_CHAT_ID
from services.db import get_webhook_subscribers

logger = logging.getLogger("HannyaWebhook")


def setup_webhook_app(bot: Bot) -> web.Application:
    """Cria a aplicação web aiohttp para receber webhooks externos."""
    app = web.Application()

    async def health_check(request: web.Request):
        return web.json_response({
            "status": "online",
            "bot": "Hannya NetWatch",
            "version": "2.0.0"
        })

    async def handle_alert(request: web.Request):
        try:
            data = await request.json()
        except Exception:
            return web.json_response({"error": "Payload JSON inválido."}, status=400)

        # Extração de campos padronizados ou flexíveis (Zabbix, Grafana, Uptime Kuma, Prometheus)
        source = data.get("source") or data.get("app") or "Alerta Externo"
        title = data.get("title") or data.get("event") or "Notificação de Infraestrutura"
        message = data.get("message") or data.get("description") or str(data)
        level = str(data.get("level") or data.get("severity") or "INFO").upper()

        if level in ["CRITICAL", "DOWN", "ERROR", "FATAL"]:
            emoji = "🔴"
            badge = "CRÍTICO"
        elif level in ["WARN", "WARNING", "HIGH"]:
            emoji = "🟡"
            badge = "ALERTA"
        elif level in ["UP", "OK", "RESOLVED", "SUCCESS"]:
            emoji = "🟢"
            badge = "RESOLVIDO"
        else:
            emoji = "ℹ️"
            badge = "INFORMAÇÃO"

        alert_text = (
            f"{emoji} <b>[WEBHOOK: {badge}]</b>\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"📡 <b>Origem:</b> <code>{source}</code>\n"
            f"📌 <b>Evento:</b> <b>{title}</b>\n"
            f"📝 <b>Detalhes:</b>\n{message}\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"⏰ <i>Recebido via Hannya NetWatch Webhook</i>"
        )

        subscribers = set(get_webhook_subscribers())
        if ADMIN_CHAT_ID and ADMIN_CHAT_ID.strip().isdigit():
            subscribers.add(int(ADMIN_CHAT_ID.strip()))

        sent_count = 0
        for chat_id in subscribers:
            try:
                await bot.send_message(chat_id=chat_id, text=alert_text, parse_mode="HTML")
                sent_count += 1
            except Exception as e:
                logger.error(f"Erro ao enviar webhook para chat {chat_id}: {e}")

        return web.json_response({
            "status": "dispatched",
            "delivered_to": sent_count,
            "subscribers": len(subscribers)
        })

    app.router.add_get("/", health_check)
    app.router.add_get("/health", health_check)
    app.router.add_post("/webhook/alert", handle_alert)

    return app


async def start_webhook_server(bot: Bot):
    """Inicia o servidor HTTP para escuta de webhooks em background."""
    app = setup_webhook_app(bot)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host=WEBHOOK_HOST, port=WEBHOOK_PORT)
    try:
        await site.start()
        logger.info(f"🌐 Servidor Webhook Hannya ouvindo em http://{WEBHOOK_HOST}:{WEBHOOK_PORT}/webhook/alert")
    except Exception as e:
        logger.error(f"Falha ao iniciar servidor webhook na porta {WEBHOOK_PORT}: {e}")
