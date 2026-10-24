# routers/monitoring.py
import asyncio
import logging
from aiogram import Router, types, Bot
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from services.db import add_host, get_user_hosts, delete_host, get_all_active_hosts, update_host_result
from services.network import ping_host, check_http, check_tcp_port
from config import CHECK_INTERVAL_SECONDS

logger = logging.getLogger("NetWatchMonitor")
router = Router()


# ============================================================
# /monitorar
# ============================================================
@router.message(Command("monitorar"))
async def cmd_monitor(message: types.Message):
    partes = message.text.strip().split()

    if len(partes) < 2:
        texto = (
            "📡 **Como usar o comando /monitorar:**\n\n"
            "• **Adicionar IP ou Domínio (Ping):**\n"
            "`/monitorar add 1.1.1.1` ou `/monitorar add google.com`\n\n"
            "• **Adicionar Site HTTP/HTTPS:**\n"
            "`/monitorar add https://meusite.com`\n\n"
            "• **Adicionar Porta Específica:**\n"
            "`/monitorar add 192.168.1.50 22` *(host porta)*\n\n"
            "• **Listar seus hosts cadastrados:**\n"
            "`/monitorar list` ou apenas `/status`\n\n"
            "• **Remover um host:**\n"
            "`/monitorar remove <ID>`"
        )
        await message.answer(texto, parse_mode="Markdown")
        return

    subcomando = partes[1].lower()

    if subcomando == "add":
        if len(partes) < 3:
            await message.answer("⚠️ Informe o host a ser monitorado. Ex: `/monitorar add 8.8.8.8`", parse_mode="Markdown")
            return

        alvo = partes[2].strip()
        porta = None
        check_type = "PING"

        if alvo.startswith("http://") or alvo.startswith("https://"):
            check_type = "HTTP"
        elif len(partes) >= 4 and partes[3].isdigit():
            porta = int(partes[3])
            check_type = "PORT"

        nome = partes[4] if len(partes) >= 5 else alvo

        host_id = add_host(message.chat.id, alvo, check_type=check_type, port=porta, name=nome)
        tipo_str = f"Porta TCP {porta}" if check_type == "PORT" else check_type

        await message.answer(
            f"✅ **Host cadastrado com sucesso!** (ID: `#{host_id}`)\n\n"
            f"• **Alvo:** `{alvo}`\n"
            f"• **Método de Checagem:** `{tipo_str}`\n"
            f"• **Intervalo de Verificação:** a cada `{CHECK_INTERVAL_SECONDS}s`\n\n"
            "A Hannya notificará você aqui imediatamente caso o host fique inacessível!",
            parse_mode="Markdown"
        )

    elif subcomando in ["list", "listar"]:
        hosts = get_user_hosts(message.chat.id)
        if not hosts:
            await message.answer("📭 Você ainda não cadastrou nenhum host para monitoramento. Use `/monitorar add <host>` para começar!", parse_mode="Markdown")
            return

        linhas = ["📋 **Seus Hosts Monitorados:**\n"]
        builder = InlineKeyboardBuilder()

        for h in hosts:
            status_emoji = "🟢" if h["last_status"] == "ONLINE" else ("🔴" if h["last_status"] == "OFFLINE" else "⚪")
            linhas.append(
                f"• `[#{h['id']}]` {status_emoji} **{h['name']}** (`{h['host']}`)\n"
                f"   Tipo: `{h['check_type']}` | Latência: `{h['last_latency_ms']} ms` | Checado: `{h['last_checked'] or 'Aguardando'}`"
            )
            # Botões por host
            builder.button(text=f"📊 Gráfico #{h['id']}", callback_data=f"chart:{h['id']}")
            builder.button(text=f"🔄 Testar #{h['id']}", callback_data=f"retest:{h['id']}")
            builder.button(text=f"🗑️ Excluir #{h['id']}", callback_data=f"del:{h['id']}")

        builder.adjust(3)
        linhas.append("\n_Toque nos botões abaixo para gerar gráficos, testar agora ou remover:_")
        await message.answer("\n".join(linhas), parse_mode="Markdown", reply_markup=builder.as_markup())

    elif subcomando in ["remove", "remover", "del"]:
        if len(partes) < 3 or not partes[2].isdigit():
            await message.answer("⚠️ Informe o ID numérico do host a ser removido. Ex: `/monitorar remove 1`", parse_mode="Markdown")
            return

        host_id = int(partes[2])
        removido = delete_host(host_id, message.chat.id)
        if removido:
            await message.answer(f"🗑️ O host `#{host_id}` foi removido do seu monitoramento com sucesso!", parse_mode="Markdown")
        else:
            await message.answer(f"❌ Não foi encontrado nenhum host ativo com o ID `#{host_id}` no seu perfil.", parse_mode="Markdown")


# ============================================================
# /grafico <id>
# ============================================================
@router.message(Command("grafico"))
async def cmd_grafico(message: types.Message):
    partes = message.text.strip().split()
    if len(partes) < 2 or not partes[1].isdigit():
        hosts = get_user_hosts(message.chat.id)
        if not hosts:
            await message.answer("📭 Nenhum host monitorado encontrado. Cadastre um com `/monitorar add <host>`.")
            return
        builder = InlineKeyboardBuilder()
        for h in hosts:
            builder.button(text=f"📊 {h['name']} (#{h['id']})", callback_data=f"chart:{h['id']}")
        builder.adjust(2)
        await message.answer("Selecione o host para gerar o gráfico de latência:", reply_markup=builder.as_markup())
        return

    host_id = int(partes[1])
    await send_host_chart(message, host_id)


async def send_host_chart(event_or_msg, host_id: int):
    """Gera e envia o gráfico de latência."""
    from services.db import get_host, get_host_history
    from services.network import generate_latency_chart

    host = get_host(host_id)
    if not host:
        await event_or_msg.answer("❌ Host não encontrado.")
        return

    history = get_host_history(host_id, limit=30)
    chart_bytes = generate_latency_chart(host["name"], history)

    photo = types.BufferedInputFile(chart_bytes, filename=f"latency_{host_id}.png")
    caption = (
        f"📊 **Histórico de Latência — {host['name']}**\n\n"
        f"• **Alvo:** `{host['host']}`\n"
        f"• **Última checagem:** `{host['last_latency_ms']} ms` ({host['last_status']})\n"
        f"• **Amostras no gráfico:** `{len(history)} pontos`"
    )

    if isinstance(event_or_msg, types.CallbackQuery):
        await event_or_msg.message.answer_photo(photo=photo, caption=caption, parse_mode="Markdown")
        await event_or_msg.answer()
    else:
        await event_or_msg.answer_photo(photo=photo, caption=caption, parse_mode="Markdown")


# ============================================================
# /webhook (INSCRIÇÃO E GUIA DE INTEGRAÇÃO)
# ============================================================
@router.message(Command("webhook"))
async def cmd_webhook(message: types.Message):
    from services.db import register_webhook_subscriber, unregister_webhook_subscriber, get_webhook_subscribers
    from config import WEBHOOK_HOST, WEBHOOK_PORT

    partes = message.text.strip().split()
    subscribers = get_webhook_subscribers()
    is_subscribed = message.chat.id in subscribers

    if len(partes) >= 2 and partes[1].lower() in ["toggle", "inscrever", "ativar"]:
        if is_subscribed:
            unregister_webhook_subscriber(message.chat.id)
            await message.answer("🔕 Você desativou os alertas de Webhook para este chat.")
        else:
            register_webhook_subscriber(message.chat.id)
            await message.answer("🔔 **Chat inscrito com sucesso!** Você receberá alertas externos aqui.")
        return

    status_icon = "🔔 ATIVO" if is_subscribed else "🔕 DESATIVADO"
    builder = InlineKeyboardBuilder()
    builder.button(
        text="🔕 Desativar Alertas" if is_subscribed else "🔔 Ativar Alertas neste Chat",
        callback_data="toggle_webhook"
    )

    doc_text = (
        f"⚡ **Central de Webhooks Externos — Hannya NetWatch**\n\n"
        f"Status neste chat: **{status_icon}**\n\n"
        f"Integre seus sistemas de monitoramento externos (**Zabbix**, **Grafana**, **Uptime Kuma**, **Prometheus**, **GitHub Actions** ou scripts Bash) para enviar alertas direto no Telegram.\n\n"
        f"🌐 **Endpoint HTTP do Servidor:**\n"
        f"`http://<IP_DO_BOT>:{WEBHOOK_PORT}/webhook/alert`\n\n"
        f"📥 **Formato do Payload JSON (POST):**\n"
        "```json\n"
        "{\n"
        '  "source": "Zabbix / Uptime Kuma",\n'
        '  "level": "CRITICAL",\n'
        '  "title": "Link Fibra WAN Down",\n'
        '  "message": "Interface GigabitEthernet0/1 perdeu conectividade com o gateway!"\n'
        "}\n"
        "```\n"
        f"• **Níveis suportados:** `CRITICAL`, `WARNING`, `INFO`, `RESOLVED`."
    )
    await message.answer(doc_text, parse_mode="Markdown", reply_markup=builder.as_markup())


@router.callback_query(lambda c: c.data == "toggle_webhook")
async def cb_toggle_webhook(callback: types.CallbackQuery):
    from services.db import register_webhook_subscriber, unregister_webhook_subscriber, get_webhook_subscribers

    subscribers = get_webhook_subscribers()
    if callback.message.chat.id in subscribers:
        unregister_webhook_subscriber(callback.message.chat.id)
        await callback.answer("Alertas de Webhook desativados!")
    else:
        register_webhook_subscriber(callback.message.chat.id)
        await callback.answer("Chat inscrito para receber alertas de Webhook!")
    await cmd_webhook(callback.message)


# ============================================================
# CALLBACKS INTERATIVOS DOS BOTÕES DE HOST
# ============================================================
@router.callback_query(lambda c: c.data.startswith("chart:"))
async def cb_chart(callback: types.CallbackQuery):
    host_id = int(callback.data.split(":")[1])
    await send_host_chart(callback, host_id)


@router.callback_query(lambda c: c.data.startswith("retest:"))
async def cb_retest(callback: types.CallbackQuery):
    from services.db import get_host, update_host_result
    host_id = int(callback.data.split(":")[1])
    host = get_host(host_id)
    if not host:
        await callback.answer("Host não encontrado.")
        return

    await callback.answer(f"Testando {host['name']} agora...")
    target = host["host"]
    check_type = host["check_type"]
    port = host["port"]

    if check_type == "HTTP":
        is_up, _, lat, msg = await check_http(target)
    elif check_type == "PORT" and port:
        is_up, lat = await check_tcp_port(target, port)
        msg = f"{lat:.1f} ms" if is_up else "Porta Fechada"
    else:
        is_up, lat, msg = await ping_host(target)

    status = "ONLINE" if is_up else "OFFLINE"
    update_host_result(host_id, status, lat, 0 if is_up else 1)

    emoji = "🟢" if is_up else "🔴"
    await callback.message.answer(
        f"{emoji} **Teste imediato de {host['name']}:**\n"
        f"• Status: **{status}**\n"
        f"• Latência: `{lat:.1f} ms`\n"
        f"• Detalhes: `{msg}`",
        parse_mode="Markdown"
    )


@router.callback_query(lambda c: c.data.startswith("del:"))
async def cb_del(callback: types.CallbackQuery):
    host_id = int(callback.data.split(":")[1])
    delete_host(host_id, callback.message.chat.id)
    await callback.answer(f"Host #{host_id} removido!")
    await callback.message.edit_text(f"🗑️ O host `#{host_id}` foi removido com sucesso.", parse_mode="Markdown")


# ============================================================
# /status (PAINEL VISUAL DE SAÚDE)
# ============================================================
@router.message(Command("status"))
async def cmd_status(message: types.Message):
    hosts = get_user_hosts(message.chat.id)
    if not hosts:
        await message.answer(
            "📭 Nenhum host cadastrado ainda!\nUse `/monitorar add <ip_ou_url>` para colocar seus primeiros servidores sob vigia.",
            parse_mode="Markdown"
        )
        return

    online_count = sum(1 for h in hosts if h["last_status"] == "ONLINE")
    offline_count = sum(1 for h in hosts if h["last_status"] == "OFFLINE")

    builder = InlineKeyboardBuilder()
    builder.button(text="🔄 Atualizar Painel", callback_data="refresh_status")
    for h in hosts:
        builder.button(text=f"📊 {h['name']}", callback_data=f"chart:{h['id']}")
    builder.adjust(2)

    linhas = [
        "📊 **Painel de Saúde de Infraestrutura — Hannya NetWatch**\n",
        f"🟢 Online: `{online_count}`  |  🔴 Offline: `{offline_count}`  |  Total: `{len(hosts)}`\n",
        "----------------------------------------"
    ]

    for h in hosts:
        emoji = "🟢 ONLINE" if h["last_status"] == "ONLINE" else ("🔴 OFFLINE" if h["last_status"] == "OFFLINE" else "⚪ AGUARDANDO")
        lat = f"`{h['last_latency_ms']} ms`" if h["last_status"] == "ONLINE" else "`Timeout`"
        linhas.append(
            f"**{h['name']}** — {emoji}\n"
            f"└ `{h['host']}` • {lat} • Verificado: `{h['last_checked'] or 'Aguardando'}`"
        )

    await message.answer("\n".join(linhas), parse_mode="Markdown", reply_markup=builder.as_markup())


@router.callback_query(lambda c: c.data == "refresh_status")
async def cb_refresh_status(callback: types.CallbackQuery):
    hosts = get_user_hosts(callback.message.chat.id)
    if not hosts:
        await callback.answer("Nenhum host cadastrado.")
        return

    online_count = sum(1 for h in hosts if h["last_status"] == "ONLINE")
    offline_count = sum(1 for h in hosts if h["last_status"] == "OFFLINE")

    builder = InlineKeyboardBuilder()
    builder.button(text="🔄 Atualizar Painel", callback_data="refresh_status")
    for h in hosts:
        builder.button(text=f"📊 {h['name']}", callback_data=f"chart:{h['id']}")
    builder.adjust(2)

    linhas = [
        "📊 **Painel de Saúde de Infraestrutura — Hannya NetWatch**\n",
        f"🟢 Online: `{online_count}`  |  🔴 Offline: `{offline_count}`  |  Total: `{len(hosts)}`\n",
        "----------------------------------------"
    ]

    for h in hosts:
        emoji = "🟢 ONLINE" if h["last_status"] == "ONLINE" else ("🔴 OFFLINE" if h["last_status"] == "OFFLINE" else "⚪ AGUARDANDO")
        lat = f"`{h['last_latency_ms']} ms`" if h["last_status"] == "ONLINE" else "`Timeout`"
        linhas.append(
            f"**{h['name']}** — {emoji}\n"
            f"└ `{h['host']}` • {lat} • Verificado: `{h['last_checked'] or 'Aguardando'}`"
        )

    try:
        await callback.message.edit_text("\n".join(linhas), parse_mode="Markdown", reply_markup=builder.as_markup())
        await callback.answer("Painel atualizado!")
    except Exception:
        await callback.answer("Sem alterações.")


# ============================================================
# TRABALHADOR EM SEGUNDO PLANO (MONITORAMENTO PERIÓDICO & ALERTAS)
# ============================================================
async def run_monitoring_worker(bot: Bot):
    """Loop assíncrono que verifica todos os hosts a cada intervalo e envia alertas."""
    logger.info("📡 Iniciando Sentinela de Monitoramento de Rede em background...")
    while True:
        try:
            hosts = get_all_active_hosts()
            for h in hosts:
                host_id = h["id"]
                chat_id = h["chat_id"]
                target = h["host"]
                check_type = h["check_type"]
                port = h["port"]
                nome = h["name"]
                status_anterior = h["last_status"]
                fail_count = h["fail_count"]

                is_up = False
                lat = 0.0

                if check_type == "HTTP":
                    is_up, code, lat, _ = await check_http(target)
                elif check_type == "PORT" and port:
                    is_up, lat = await check_tcp_port(target, port)
                else:
                    is_up, lat, _ = await ping_host(target)

                novo_status = "ONLINE" if is_up else "OFFLINE"

                # Detecta transição de estado para envio de alerta
                if status_anterior != "UNKNOWN" and status_anterior != novo_status:
                    if novo_status == "OFFLINE":
                        fail_count += 1
                        alerta = (
                            f"🚨 **ALERTA DE QUEDA DE REDE!** 🚨\n\n"
                            f"O host monitorado **{nome}** parou de responder!\n\n"
                            f"• **Alvo:** `{target}`\n"
                            f"• **Tipo:** `{check_type}`\n"
                            f"• **Status:** 🔴 **OFFLINE** (Inacessível)\n\n"
                            "Verifique o roteamento, firewall ou a conexão do servidor."
                        )
                        try:
                            await bot.send_message(chat_id, alerta, parse_mode="Markdown")
                        except Exception as e:
                            logger.error(f"Erro ao enviar alerta para chat {chat_id}: {e}")
                    elif novo_status == "ONLINE":
                        fail_count = 0
                        recuperado = (
                            f"✅ **HOST RECUPERADO!** ✅\n\n"
                            f"O host monitorado **{nome}** voltou a responder com sucesso!\n\n"
                            f"• **Alvo:** `{target}`\n"
                            f"• **Status:** 🟢 **ONLINE**\n"
                            f"• **Latência atual:** `{lat:.1f} ms`"
                        )
                        try:
                            await bot.send_message(chat_id, recuperado, parse_mode="Markdown")
                        except Exception as e:
                            logger.error(f"Erro ao enviar notificação de recuperação: {e}")

                update_host_result(host_id, novo_status, lat, fail_count)

        except Exception as e:
            logger.error(f"Erro no ciclo de monitoramento: {e}", exc_info=True)

        await asyncio.sleep(CHECK_INTERVAL_SECONDS)
