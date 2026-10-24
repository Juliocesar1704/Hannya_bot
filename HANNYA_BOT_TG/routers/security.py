# routers/security.py
from aiogram import Router, types
from aiogram.filters import Command
from services.network import audit_http_headers, check_dnsbl_blacklist, check_dnssec

router = Router()


# ============================================================
# /headers (AUDITORIA DE CABEÇALHOS HTTP / OWASP)
# ============================================================
@router.message(Command("headers", "security"))
async def cmd_headers(message: types.Message):
    partes = message.text.strip().split()
    if len(partes) < 2:
        await message.answer("⚠️ Uso: `/headers <url_ou_site>`\nEx: `/headers https://google.com` ou `/headers github.com`", parse_mode="Markdown")
        return

    alvo = partes[1].strip()
    status_msg = await message.answer(f"🛡️ Auditando cabeçalhos de segurança HTTP em `{alvo}`...", parse_mode="Markdown")

    res = await audit_http_headers(alvo)

    if not res.get("success"):
        await status_msg.edit_text(f"❌ Falha na auditoria: `{res.get('error')}`", parse_mode="Markdown")
        return

    grade = res["grade"]
    score = res["score"]
    grade_emoji = "🏆" if "A" in grade else ("🟡" if grade in ["B", "C"] else "🔴")

    linhas = [
        f"🛡️ **Auditoria de Cabeçalhos HTTP — {res['url']}**\n",
        f"Nota de Segurança: {grade_emoji} **{grade}** (`{score}/100 pontos`)",
        "----------------------------------------"
    ]

    for name, passed, details in res["checks"]:
        icon = "✅" if passed else "❌"
        linhas.append(f"{icon} **{name}**\n   └ _{details}_")

    linhas.append("\n*Recomendações baseadas nas diretrizes OWASP Secure Headers.*")
    await status_msg.edit_text("\n".join(linhas), parse_mode="Markdown")


# ============================================================
# /blacklist (CONSULTA DE REPUTAÇÃO DNSBL)
# ============================================================
@router.message(Command("blacklist", "dnsbl"))
async def cmd_blacklist(message: types.Message):
    partes = message.text.strip().split()
    if len(partes) < 2:
        await message.answer("⚠️ Uso: `/blacklist <endereco_ipv4>`\nEx: `/blacklist 1.1.1.1` ou `/blacklist 200.147.3.157`", parse_mode="Markdown")
        return

    ip_alvo = partes[1].strip()
    status_msg = await message.answer(f"🔎 Consultando reputação do IP `{ip_alvo}` em 5 listas DNSBL globais...", parse_mode="Markdown")

    res = await check_dnsbl_blacklist(ip_alvo)

    if res and res[0].get("server") == "Erro":
        await status_msg.edit_text(f"❌ `{res[0].get('error')}`", parse_mode="Markdown")
        return

    listed_count = sum(1 for r in res if r["listed"])
    clean_count = len(res) - listed_count

    linhas = [
        f"📋 **Reputação DNSBL — IP {ip_alvo}**\n",
        f"Status: {'🔴 **LISTADO EM BLACKLIST!**' if listed_count > 0 else '🟢 **IP LIMPO (NÃO LISTADO)**'}",
        f"Listas Limpas: `{clean_count}/{len(res)}`\n",
        "----------------------------------------"
    ]

    for r in res:
        status_str = "🔴 LISTADO (Spam/Malware)" if r["listed"] else "🟢 Limpo"
        linhas.append(f"• **{r['server']}** (`{r['host']}`): {status_str}")

    await status_msg.edit_text("\n".join(linhas), parse_mode="Markdown")


# ============================================================
# /dnssec
# ============================================================
@router.message(Command("dnssec"))
async def cmd_dnssec(message: types.Message):
    partes = message.text.strip().split()
    if len(partes) < 2:
        await message.answer("⚠️ Uso: `/dnssec <dominio>`\nEx: `/dnssec registro.br` ou `/dnssec cloudflare.com`", parse_mode="Markdown")
        return

    dominio = partes[1].strip()
    status_msg = await message.answer(f"🔐 Verificando assinaturas criptográficas DNSSEC de `{dominio}`...", parse_mode="Markdown")

    res = check_dnssec(dominio)

    key_icon = "✅ Presente" if res["has_dnskey"] else "❌ Ausente"
    ds_icon = "✅ Presente" if res["has_ds"] else "❌ Ausente"

    texto = (
        f"🔐 **Validação DNSSEC — {res['domain']}**\n\n"
        f"• **Status Geral:** {res['status']}\n"
        f"• **Chave de Assinatura (DNSKEY):** {key_icon}\n"
        f"• **Registro de Delegação (DS):** {ds_icon}\n\n"
        "O DNSSEC garante autenticidade e integridade nas respostas DNS, impedindo redirecionamentos maliciosos (DNS Spoofing)."
    )
    await status_msg.edit_text(texto, parse_mode="Markdown")
