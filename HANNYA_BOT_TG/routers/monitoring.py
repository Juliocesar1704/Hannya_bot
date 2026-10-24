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
        for h in hosts:
            status_emoji = "🟢" if h["last_status"] == "ONLINE" else ("🔴" if h["last_status"] == "OFFLINE" else "⚪")
            linhas.append(
                f"• `[ID #{h['id']}]` {status_emoji} **{h['name']}** (`{h['host']}`)\n"
                f"   Tipo: `{h['check_type']}` | Latência: `{h['last_latency_ms']} ms` | Checado: `{h['last_checked'] or 'Aguardando'}`"
            )

        linhas.append("\nPara remover algum host, use: `/monitorar remove <ID>`")
        await message.answer("\n".join(linhas), parse_mode="Markdown")

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
    builder.button(text="➕ Adicionar Host", callback_data="menu_monitors")

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
    builder.button(text="➕ Adicionar Host", callback_data="menu_monitors")

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
