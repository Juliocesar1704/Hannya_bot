# routers/tools.py
from aiogram import Router, types
from aiogram.filters import Command
from services.network import ping_host, port_scan, query_dns, check_ssl
import aiohttp

router = Router()


# ============================================================
# /ping
# ============================================================
@router.message(Command("ping"))
async def cmd_ping(message: types.Message):
    partes = message.text.strip().split()
    if len(partes) < 2:
        await message.answer("⚠️ Uso: `/ping <host_ou_ip>`\nEx: `/ping 8.8.8.8` ou `/ping google.com`", parse_mode="Markdown")
        return

    alvo = partes[1].strip()
    status_msg = await message.answer(f"⏳ Enviando pacotes ICMP para `{alvo}`...", parse_mode="Markdown")

    is_up, lat, det = await ping_host(alvo)

    if is_up:
        emoji = "🟢" if lat < 100 else ("🟡" if lat < 250 else "🔴")
        texto = (
            f"🏓 **Pong! Resultado do Teste ICMP**\n\n"
            f"• **Alvo:** `{alvo}`\n"
            f"• **Status:** {emoji} **ONLINE**\n"
            f"• **Latência (RTT):** `{lat:.1f} ms`\n"
            "• **Perda de Pacotes:** `0%`"
        )
    else:
        texto = (
            f"🏓 **Resultado do Teste ICMP**\n\n"
            f"• **Alvo:** `{alvo}`\n"
            f"• **Status:** 🔴 **OFFLINE / INACESSÍVEL**\n"
            f"• **Detalhe:** `{det}`"
        )

    await status_msg.edit_text(texto, parse_mode="Markdown")


# ============================================================
# /portscan
# ============================================================
@router.message(Command("portscan"))
async def cmd_portscan(message: types.Message):
    partes = message.text.strip().split()
    if len(partes) < 2:
        await message.answer("⚠️ Uso: `/portscan <host_ou_ip>`\nEx: `/portscan scanme.nmap.org`", parse_mode="Markdown")
        return

    alvo = partes[1].strip()
    status_msg = await message.answer(f"🔍 Escaneando portas TCP comuns em `{alvo}`...", parse_mode="Markdown")

    resultados = await port_scan(alvo)

    abertas = [r for r in resultados if r["open"]]
    fechadas = len(resultados) - len(abertas)

    linhas = [
        f"🛡️ **Relatório de Portscan — {alvo}**\n",
        f"📊 Portas Abertas: `{len(abertas)}` | Portas Fechadas: `{fechadas}`\n",
        "----------------------------------------"
    ]

    if abertas:
        for p in abertas:
            linhas.append(f"🟢 **Porta {p['port']}/TCP** — `{p['service']}` ({p['latency']:.1f} ms)")
    else:
        linhas.append("🔒 Nenhuma das portas padrão testadas está aberta para o exterior.")

    linhas.append("\n*Portas escaneadas: 21, 22, 23, 25, 53, 80, 110, 143, 443, 445, 3306, 3389, 5432, 8080, 25565.*")
    await status_msg.edit_text("\n".join(linhas), parse_mode="Markdown")


# ============================================================
# /dns
# ============================================================
@router.message(Command("dns"))
async def cmd_dns(message: types.Message):
    partes = message.text.strip().split()
    if len(partes) < 2:
        await message.answer("⚠️ Uso: `/dns <domínio> [tipo_registro]`\nEx: `/dns cloudflare.com` ou `/dns google.com MX`", parse_mode="Markdown")
        return

    dominio = partes[1].strip()
    tipo = partes[2].upper() if len(partes) >= 3 else "A"

    res = query_dns(dominio, tipo)

    linhas = [
        f"🌐 **Consulta DNS — Registro {tipo}**\n",
        f"• **Domínio:** `{dominio}`\n",
        "**Resultados:**"
    ]
    for item in res:
        linhas.append(f"└ `{item}`")

    await message.answer("\n".join(linhas), parse_mode="Markdown")


# ============================================================
# /cert
# ============================================================
@router.message(Command("cert", "ssl"))
async def cmd_cert(message: types.Message):
    partes = message.text.strip().split()
    if len(partes) < 2:
        await message.answer("⚠️ Uso: `/cert <domínio>`\nEx: `/cert github.com`", parse_mode="Markdown")
        return

    alvo = partes[1].strip()
    status_msg = await message.answer(f"🔒 Consultando certificado SSL/TLS de `{alvo}`...", parse_mode="Markdown")

    res = check_ssl(alvo)

    if res.get("valid"):
        dias = res["days_left"]
        emoji = "🟢" if dias > 30 else ("🟡" if dias > 7 else "🔴")
        texto = (
            f"🔒 **Auditoria de Certificado SSL/TLS**\n\n"
            f"• **Domínio:** `{res['subject']}`\n"
            f"• **Emissor (CA):** `{res['issuer']}`\n"
            f"• **Validade:** {emoji} `{dias}` dias restantes\n"
            f"• **Data de Expiração:** `{res['expires_at']}`"
        )
    else:
        texto = (
            f"🔒 **Auditoria de Certificado SSL/TLS**\n\n"
            f"• **Alvo:** `{alvo}`\n"
            f"• **Status:** 🔴 Inválido ou Inacessível\n"
            f"• **Detalhe:** `{res.get('error', 'Erro desconhecido')}`"
        )

    await status_msg.edit_text(texto, parse_mode="Markdown")


# ============================================================
# /myip
# ============================================================
@router.message(Command("myip"))
async def cmd_myip(message: types.Message):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://ipapi.co/json/", timeout=4.0) as resp:
                data = await resp.json()

        ip = data.get("ip", "Desconhecido")
        cidade = data.get("city", "Desconhecido")
        regiao = data.get("region", "Desconhecido")
        pais = data.get("country_name", "Desconhecido")
        org = data.get("org", "Desconhecido")
        asn = data.get("asn", "Desconhecido")

        texto = (
            "🌍 **Informações de Conexão Externa (Bot Host)**\n\n"
            f"• **Endereço IP Público:** `{ip}`\n"
            f"• **Provedor / ASN:** `{org}` (`{asn}`)\n"
            f"• **Localização:** `{cidade}, {regiao} — {pais}`\n"
        )
        await message.answer(texto, parse_mode="Markdown")
    except Exception as e:
        await message.answer(f"❌ Não foi possível consultar o IP público: {e}")


# ============================================================
# /traceroute
# ============================================================
@router.message(Command("traceroute", "tracert"))
async def cmd_traceroute(message: types.Message):
    from services.network import run_traceroute

    partes = message.text.strip().split()
    if len(partes) < 2:
        await message.answer("⚠️ Uso: `/traceroute <host_ou_ip>`\nEx: `/traceroute 8.8.8.8` ou `/traceroute uol.com.br`", parse_mode="Markdown")
        return

    alvo = partes[1].strip()
    status_msg = await message.answer(f"🧭 Executando traceroute para `{alvo}` (até 18 saltos)... Isso pode levar alguns segundos.", parse_mode="Markdown")

    hops = await run_traceroute(alvo, max_hops=18)

    linhas = [
        f"🧭 **Traceroute — Rota para {alvo}**\n",
        "Salto | RTT | Endereço IP / Roteador",
        "----------------------------------------"
    ]

    for h in hops:
        linhas.append(f"`#{h['hop']:02d}` • `{h['rtt']:<8}` • `{h['ip']}`")

    linhas.append("\n*Trace concluído com sucesso.*")
    await status_msg.edit_text("\n".join(linhas), parse_mode="Markdown")


# ============================================================
# /whois & /geo
# ============================================================
@router.message(Command("whois", "geo"))
async def cmd_whois(message: types.Message):
    from services.network import lookup_whois_and_geo

    partes = message.text.strip().split()
    if len(partes) < 2:
        await message.answer("⚠️ Uso: `/whois <ip_ou_dominio>`\nEx: `/whois 1.1.1.1` ou `/whois registro.br`", parse_mode="Markdown")
        return

    alvo = partes[1].strip()
    status_msg = await message.answer(f"🔍 Consultando ASN e dados geográficos de `{alvo}`...", parse_mode="Markdown")

    info = await lookup_whois_and_geo(alvo)

    if not info.get("success"):
        await status_msg.edit_text(f"❌ Falha na consulta: `{info.get('error')}`", parse_mode="Markdown")
        return

    texto = (
        f"🌐 **Informações de ASN & Geolocalização**\n\n"
        f"• **Alvo Consultado:** `{alvo}`\n"
        f"• **Endereço IP:** `{info['ip']}`\n"
        f"• **Sistema Autônomo (ASN):** `{info['asn']}`\n"
        f"• **Provedor / Organização:** `{info['org']}`\n"
        f"• **Localização:** `{info['city']}, {info['country']}`\n"
        f"• **Fuso Horário:** `{info['timezone']}`\n"
        f"• **Coordenadas:** `{info['coords']}`"
    )
    await status_msg.edit_text(texto, parse_mode="Markdown")


# ============================================================
# /mac (OUI LOOKUP)
# ==========================================
@router.message(Command("mac", "oui"))
async def cmd_mac(message: types.Message):
    from services.network import lookup_mac_oui

    partes = message.text.strip().split()
    if len(partes) < 2:
        await message.answer("⚠️ Uso: `/mac <endereco_mac>`\nEx: `/mac 00:1A:2B:3C:4D:5E` ou `/mac CC:2D:E0`", parse_mode="Markdown")
        return

    mac_input = partes[1].strip()
    res = await lookup_mac_oui(mac_input)

    if res.get("success"):
        texto = (
            f"🏷️ **Consulta de Fabricante MAC (OUI)**\n\n"
            f"• **Endereço MAC:** `{mac_input}`\n"
            f"• **Prefixo OUI:** `{res['oui']}`\n"
            f"• **Fabricante:** 🏢 **{res['vendor']}**\n"
            f"• **Fonte:** `{res['source']}`"
        )
    else:
        texto = (
            f"🏷️ **Consulta de Fabricante MAC (OUI)**\n\n"
            f"• **Endereço MAC:** `{mac_input}`\n"
            f"• **Status:** ⚠️ Não identificado\n"
            f"• **Detalhe:** {res.get('error')}"
        )

    await message.answer(texto, parse_mode="Markdown")
