# routers/subnet.py
from aiogram import Router, types
from aiogram.filters import Command
from services.network import calculate_subnet

router = Router()


@router.message(Command("subnet", "ip", "calc"))
async def cmd_subnet(message: types.Message):
    partes = message.text.strip().split()
    if len(partes) < 2:
        texto = (
            "🧮 **Calculadora de Sub-redes IPv4 / IPv6**\n\n"
            "Digite o endereço IP acompanhado do prefixo CIDR (`/X`).\n\n"
            "**Exemplos práticos:**\n"
            "• `/subnet 192.168.1.50/26`\n"
            "• `/subnet 10.0.0.0/19`\n"
            "• `/subnet 172.16.50.12/28`\n"
            "• `/subnet 2001:db8::/64`"
        )
        await message.answer(texto, parse_mode="Markdown")
        return

    entrada = partes[1].strip()

    try:
        dados = calculate_subnet(entrada)
    except Exception as e:
        await message.answer(f"❌ **Entrada inválida:** `{e}`\nVerifique o formato, ex: `192.168.1.0/24`", parse_mode="Markdown")
        return

    if dados["version"] == "IPv4":
        texto = (
            f"🧮 **Cálculo de Sub-rede — {dados['cidr']}**\n\n"
            f"• **Endereço de Rede:** `{dados['network']}`\n"
            f"• **Máscara de Sub-rede:** `{dados['netmask']}`\n"
            f"• **Máscara Curinga (Wildcard):** `{dados['wildcard']}`\n"
            f"• **Endereço de Broadcast:** `{dados['broadcast']}`\n\n"
            "👥 **Faixa de Hosts Utilizáveis:**\n"
            f"• **Primeiro Host:** `{dados['first_host']}`\n"
            f"• **Último Host:** `{dados['last_host']}`\n"
            f"• **Total de Hosts Válidos:** `{dados['usable_hosts']:,}` máquinas\n"
            f"• **Total de Endereços:** `{dados['total_addresses']:,}`\n\n"
            "🏷️ **Classificação:**\n"
            f"• **Classe do IP:** `{dados['class']}`\n"
            f"• **Escopo:** `{dados['type']}`"
        )
    else:
        texto = (
            f"🧮 **Cálculo de Sub-rede IPv6 — {dados['cidr']}**\n\n"
            f"• **Prefixo:** `/{dados['prefix']}`\n"
            f"• **Rede:** `{dados['network']}`\n"
            f"• **Total de Endereços:** `{dados['total_addresses']}`\n"
            f"• **Tipo:** `{dados['type']}`"
        )

    await message.answer(texto, parse_mode="Markdown")
