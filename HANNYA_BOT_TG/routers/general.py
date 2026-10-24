# routers/general.py
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.button(text="📊 Meus Monitores", callback_data="menu_monitors")
    builder.button(text="🧮 Sub-redes & VLSM", callback_data="menu_subnet")
    builder.button(text="🔍 Ferramentas de Rede", callback_data="menu_tools")
    builder.button(text="🛡️ Segurança & Auditoria", callback_data="menu_security")
    builder.button(text="🛠️ Cisco CCNA", callback_data="menu_cisco")
    builder.button(text="⚡ Webhooks", callback_data="menu_webhook")
    builder.button(text="🖥️ Status da Máquina", callback_data="menu_system")
    builder.adjust(2)

    texto = (
        "👺 **Hannya NetWatch — Sentinela de Redes** 📡\n\n"
        "Olá, operador! Sou a guardiã das suas conexões e monitoramento de infraestrutura.\n\n"
        "Aqui você pode gerenciar a saúde dos seus servidores, calcular sub-redes IPv4/IPv6 e VLSM, "
        "auditar segurança de sites, realizar traceroutes, portscans e receber alertas em tempo real pelo celular.\n\n"
        "💡 *Dica:* Digite `/ajuda` para ver o manual completo de comandos ou clique nos botões abaixo:"
    )
    await message.answer(texto, parse_mode="Markdown", reply_markup=builder.as_markup())


@router.message(Command("ajuda", "help"))
async def cmd_help(message: types.Message):
    texto = (
        "📘 **Manual de Comandos — Hannya NetWatch**\n\n"
        "🚨 **Monitoramento Contínuo & Alertas:**\n"
        "• `/monitorar add <ip/host/url>` — Adiciona um host para vigiar\n"
        "• `/status` — Painel visual de saúde com botões interativos\n"
        "• `/grafico <id>` — Gera gráfico visual de histórico de latência\n"
        "• `/monitorar list` — Lista todos os seus hosts com botões de ação\n"
        "• `/monitorar remove <id>` — Remove um host\n"
        "• `/webhook` — Configura alertas externos de Zabbix/Grafana/Uptime Kuma\n\n"
        "🔍 **Diagnósticos & Telecom:**\n"
        "• `/ping <host>` — Mede latência e perda de pacotes\n"
        "• `/traceroute <host>` — Rastreamento de saltos (hops) e roteadores\n"
        "• `/whois <ip/domínio>` — Consulta ASN, operadora (ISP) e geolocalização\n"
        "• `/mac <endereço MAC>` — Identifica o fabricante da placa de rede (OUI)\n"
        "• `/portscan <host>` — Varre as principais portas TCP (SSH, Web, DB, etc.)\n"
        "• `/dns <domínio> [tipo]` — Consulta registros DNS (A, AAAA, MX, TXT, NS)\n"
        "• `/cert <domínio>` — Checa validade e emissor do certificado SSL/TLS\n"
        "• `/myip` — Exibe o IP público do bot e dados do provedor\n\n"
        "🧮 **Sub-redes & Cisco CCNA:**\n"
        "• `/subnet <ip/cidr>` — Cálculo completo de sub-rede IPv4/IPv6\n"
        "• `/vlsm <bloco> <hosts>` — Divisão otimizada VLSM (ex: `/vlsm 192.168.0.0/24 60,30,10,2`)\n"
        "• `/cisco` — Gerador interativo de templates Cisco IOS (VLAN, OSPF, DHCP, NAT)\n\n"
        "🛡️ **Segurança & Auditoria:**\n"
        "• `/headers <url>` — Auditoria OWASP de cabeçalhos HTTP com nota A+ a F\n"
        "• `/blacklist <ip>` — Consulta o IP em 5 listas DNSBL de spam/malware\n"
        "• `/dnssec <domínio>` — Valida proteção criptográfica contra DNS Spoofing\n\n"
        "🖥️ **Telemetria do Servidor:**\n"
        "• `/server` — Uso de CPU, Memória, Disco e tráfego de interface\n"
    )
    await message.answer(texto, parse_mode="Markdown")


@router.message(Command("sobre"))
async def cmd_about(message: types.Message):
    texto = (
        "👺 **Sobre o Projeto Hannya NetWatch**\n\n"
        "Desenvolvido sob medida para estudantes e profissionais de **Redes de Computadores**.\n"
        "Integrado ao ecossistema multiplataforma do repositório **Hannya_bot**.\n\n"
        "• **Framework:** aiogram 3.x (Asyncio)\n"
        "• **Motor de Rede:** Python sockets, DNS Resolver & psutil\n"
        "• **Gráficos:** Matplotlib Dark Cyberpunk Engine\n"
        "• **Webhooks:** aiohttp HTTP Server embutido\n"
        "• **Segurança:** SQLite criptografado em ambiente isolado\n\n"
        "🔗 *GitHub oficial:* https://github.com/Juliocesar1704/Hannya_bot"
    )
    await message.answer(texto, parse_mode="Markdown")


@router.callback_query(lambda c: c.data.startswith("menu_"))
async def process_menu_callbacks(callback: types.CallbackQuery):
    action = callback.data.split("_")[1]

    if action == "monitors":
        await callback.message.answer(
            "📊 **Como usar o Monitoramento:**\n\n"
            "• Adicionar host: `/monitorar add 1.1.1.1`\n"
            "• Adicionar site: `/monitorar add https://google.com`\n"
            "• Ver painel: `/status`\n"
            "• Gerar gráfico: `/grafico`",
            parse_mode="Markdown"
        )
    elif action == "subnet":
        await callback.message.answer(
            "🧮 **Calculadora de Sub-rede & VLSM:**\n\n"
            "• Sub-rede fixa: `/subnet 192.168.1.100/26`\n"
            "• Divisão VLSM: `/vlsm 192.168.0.0/24 60,30,10,2,2`",
            parse_mode="Markdown"
        )
    elif action == "tools":
        await callback.message.answer(
            "🔍 **Diagnósticos de Rede:**\n\n"
            "• `/ping 8.8.8.8`\n"
            "• `/traceroute 8.8.8.8`\n"
            "• `/whois 1.1.1.1`\n"
            "• `/mac 00:1A:2B:3C:4D:5E`\n"
            "• `/portscan scanme.nmap.org`\n"
            "• `/dns google.com MX`\n"
            "• `/cert github.com`",
            parse_mode="Markdown"
        )
    elif action == "security":
        await callback.message.answer(
            "🛡️ **Segurança & Auditoria:**\n\n"
            "• `/headers https://meusite.com` — Nota de segurança HTTP\n"
            "• `/blacklist 1.1.1.1` — Verificação de DNSBL\n"
            "• `/dnssec cloudflare.com` — Checagem de DNSSEC",
            parse_mode="Markdown"
        )
    elif action == "cisco":
        await callback.message.answer(
            "🛠️ Digite `/cisco` para abrir o menu interativo de scripts para roteadores e switches.",
            parse_mode="Markdown"
        )
    elif action == "webhook":
        await callback.message.answer(
            "⚡ Digite `/webhook` para ver as instruções de integração com Zabbix, Grafana ou Uptime Kuma.",
            parse_mode="Markdown"
        )
    elif action == "system":
        await callback.message.answer(
            "🖥️ Digite `/server` para obter a telemetria do hardware e consumo de rede em tempo real.",
            parse_mode="Markdown"
        )

    await callback.answer()
