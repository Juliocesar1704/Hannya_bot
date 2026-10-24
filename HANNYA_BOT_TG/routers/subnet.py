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


# ============================================================
# /vlsm (CÁLCULO DE SUB-REDES EM TAMANHO VARIÁVEL)
# ============================================================
@router.message(Command("vlsm"))
async def cmd_vlsm(message: types.Message):
    from services.network import calculate_vlsm

    partes = message.text.strip().split()
    if len(partes) < 3:
        texto = (
            "🧮 **Calculadora VLSM (Variable Length Subnet Mask)**\n\n"
            "Divide um bloco de rede de acordo com os requisitos de hosts de cada departamento.\n\n"
            "**Como usar:**\n"
            "`/vlsm <bloco_base> <qtd_hosts_separados_por_virgula>`\n\n"
            "**Exemplos:**\n"
            "• `/vlsm 192.168.0.0/24 60,30,14,2,2`\n"
            "• `/vlsm 10.0.0.0/22 LAN_A=120,LAN_B=50,WIFI=30,WAN1=2,WAN2=2`"
        )
        await message.answer(texto, parse_mode="Markdown")
        return

    base_cidr = partes[1].strip()
    reqs_str = partes[2].strip()

    requirements = []
    for idx, item in enumerate(reqs_str.split(",")):
        item = item.strip()
        if not item:
            continue
        if "=" in item:
            nome, count_str = item.split("=", 1)
        else:
            nome = f"Sub-rede {chr(65 + idx)}"
            count_str = item

        if not count_str.isdigit():
            await message.answer(f"⚠️ Valor de hosts inválido: `{count_str}`.", parse_mode="Markdown")
            return
        requirements.append((nome, int(count_str)))

    try:
        resultado = calculate_vlsm(base_cidr, requirements)
    except Exception as e:
        await message.answer(f"❌ **Erro no cálculo VLSM:** `{e}`", parse_mode="Markdown")
        return

    linhas = [
        f"📊 **Resultado do Planejamento VLSM — {resultado['base_network']}**\n",
        f"• Capacidade Total: `{resultado['total_addresses']}` IPs",
        f"• IPs Alocados: `{resultado['used_addresses']}` | Livres: `{resultado['free_addresses']}`\n",
        "----------------------------------------"
    ]

    for s in resultado["subnets"]:
        linhas.append(
            f"🏷️ **{s['name']}** (Solicitados: `{s['needed_hosts']}` | Úteis: `{s['usable_hosts']}`)\n"
            f"├ **CIDR:** `{s['cidr']}`\n"
            f"├ **Máscara:** `{s['netmask']}` (Wildcard: `{s['wildcard']}`)\n"
            f"├ **Faixa Útil:** `{s['first_host']}` até `{s['last_host']}`\n"
            f"└ **Broadcast:** `{s['broadcast']}`\n"
        )

    await message.answer("\n".join(linhas), parse_mode="Markdown")


# ============================================================
# /cisco (GERADOR DE CONFIGURAÇÃO CISCO CCNA)
# ============================================================
@router.message(Command("cisco"))
async def cmd_cisco(message: types.Message):
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from services.network import generate_cisco_config

    partes = message.text.strip().split()
    if len(partes) >= 2:
        tipo = partes[1].lower()
        config_text = generate_cisco_config(tipo)
        await message.answer(f"```cisco\n{config_text}\n```", parse_mode="Markdown")
        return

    builder = InlineKeyboardBuilder()
    builder.button(text="🏷️ VLAN & Trunk", callback_data="cisco:vlan")
    builder.button(text="🚦 Router-on-a-stick", callback_data="cisco:stick")
    builder.button(text="🌐 Roteamento OSPF", callback_data="cisco:ospf")
    builder.button(text="💻 Servidor DHCP", callback_data="cisco:dhcp")
    builder.button(text="🔀 NAT / PAT Overload", callback_data="cisco:nat")
    builder.adjust(2)

    await message.answer(
        "🛠️ **Gerador de Configurações Cisco IOS (CCNA)**\n\n"
        "Selecione um dos modelos abaixo para obter os comandos prontos:",
        reply_markup=builder.as_markup()
    )


@router.callback_query(lambda c: c.data.startswith("cisco:"))
async def cb_cisco_template(callback: types.CallbackQuery):
    from services.network import generate_cisco_config
    tipo = callback.data.split(":")[1]
    config_text = generate_cisco_config(tipo)

    await callback.message.answer(
        f"📋 **Script Cisco IOS — {tipo.upper()}**\n```cisco\n{config_text}\n```",
        parse_mode="Markdown"
    )
    await callback.answer()
