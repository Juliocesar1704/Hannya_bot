# routers/general.py
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.button(text="📊 Meus Monitores", callback_data="menu_monitors")
    builder.button(text="🧮 Calculadora de Sub-rede", callback_data="menu_subnet")
    builder.button(text="🔍 Ferramentas de Rede", callback_data="menu_tools")
    builder.button(text="🖥️ Status da Máquina", callback_data="menu_system")
    builder.adjust(2)

    texto = (
        "👺 **Hannya NetWatch — Sentinela de Redes** 📡\n\n"
        "Olá, operador! Sou a guardiã das suas conexões e monitoramento de infraestrutura.\n\n"
        "Aqui você pode gerenciar a saúde dos seus servidores, calcular sub-redes IPv4/IPv6, "
        "realizar varreduras de portas e diagnosticar redes em tempo real pelo celular.\n\n"
        "💡 *Dica:* Digite `/ajuda` para ver o manual completo de comandos ou clique nos botões abaixo:"
    )
    await message.answer(texto, parse_mode="Markdown", reply_markup=builder.as_markup())


@router.message(Command("ajuda", "help"))
async def cmd_help(message: types.Message):
    texto = (
        "📘 **Manual de Comandos — Hannya NetWatch**\n\n"
        "🚨 **Monitoramento Contínuo & Alertas:**\n"
        "• `/monitorar add <ip/host/url>` — Adiciona um host para vigiar\n"
        "• `/status` — Painel visual de saúde de todos os seus hosts\n"
        "• `/monitorar list` — Lista todos os seus hosts e IDs\n"
        "• `/monitorar remove <id>` — Para de monitorar um host\n\n"
        "🔍 **Diagnóstico de Conexão:**\n"
        "• `/ping <host>` — Mede latência e perda de pacotes\n"
        "• `/portscan <host>` — Varre as principais portas TCP (SSH, Web, DB, etc.)\n"
        "• `/dns <domínio> [tipo]` — Consulta DNS (A, AAAA, MX, TXT, NS)\n"
        "• `/cert <domínio>` — Checa validade e emissor do certificado SSL/TLS\n"
        "• `/myip` — Exibe o IP público do bot e dados do provedor\n\n"
        "🧮 **Estudos & Sub-redes:**\n"
        "• `/subnet <ip/cidr>` — Cálculo completo de sub-rede IPv4/IPv6\n"
        "*(Ex: `/subnet 192.168.1.50/26` ou `/subnet 10.0.0.0/19`)*\n\n"
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
            "• Para adicionar um IP: `/monitorar add 1.1.1.1`\n"
            "• Para adicionar um Site: `/monitorar add https://google.com`\n"
            "• Para ver o painel: `/status`",
            parse_mode="Markdown"
        )
    elif action == "subnet":
        await callback.message.answer(
            "🧮 **Calculadora de Sub-rede:**\n\n"
            "Digite `/subnet` seguido de um endereço com barra de prefixo (CIDR):\n\n"
            "Exemplo:\n"
            "`/subnet 192.168.1.100/26`\n"
            "`/subnet 10.20.0.0/19`",
            parse_mode="Markdown"
        )
    elif action == "tools":
        await callback.message.answer(
            "🔍 **Ferramentas Rápidas:**\n\n"
            "• `/ping 8.8.8.8`\n"
            "• `/portscan scanme.nmap.org`\n"
            "• `/dns github.com MX`\n"
            "• `/cert google.com`",
            parse_mode="Markdown"
        )
    elif action == "system":
        await callback.message.answer(
            "🖥️ Digite `/server` para obter a telemetria do hardware e consumo de rede em tempo real.",
            parse_mode="Markdown"
        )

    await callback.answer()
