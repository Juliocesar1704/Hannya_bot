<p align="center">
  <img src="../assets/hannya_banner_hd.png" alt="Hannya NetWatch Banner" width="100%">
</p>

# 📡 Hannya NetWatch — Telegram Bot

> *“A máscara não esconde as falhas. Ela vigia cada pacote que atravessa a rede.”*

O **Hannya NetWatch** é o módulo do Projeto Hannya desenvolvido sob medida para **estudantes e profissionais de Redes de Computadores e Infraestrutura**. Ele transforma seu Telegram em um centro de operações de rede (NOC) de bolso, permitindo diagnosticar conexões, calcular sub-redes e receber alertas imediatos quando seus servidores ficarem fora do ar.

---

## ⚙️ Principais Funcionalidades

### 🚨 1. Monitoramento Contínuo com Alertas em Tempo Real
- **Sentinela em Background:** O bot verifica automaticamente a cada 60 segundos a saúde de todos os seus hosts cadastrados.
- **Alertas Instantâneos no Privado:** Se um servidor, site ou porta parar de responder, você recebe uma notificação de emergência imediata no Telegram.
- **Notificação de Recuperação:** Quando o host volta a responder, a Hannya avisa que a conexão foi restabelecida com a latência atual.
- **Painel Visual Interativo:** Comando `/status` com contadores de hosts `🟢 ONLINE` e `🔴 OFFLINE` e botão de recarregar em tempo real.

### 🔍 2. Ferramentas Diagnósticas de Rede
- **`/ping <host>`**: Mede latência (RTT) e perda de pacotes via ICMP de forma assíncrona.
- **`/portscan <host>`**: Varre as principais portas TCP (SSH, Web, MySQL, RDP, Minecraft, etc.) e identifica serviços abertos.
- **`/dns <domínio> [tipo]`**: Consulta registros DNS (`A`, `AAAA`, `MX`, `TXT`, `NS`, `CNAME`).
- **`/cert <domínio>`**: Checa a validade de certificados SSL/TLS, autoridade emissora e dias restantes antes de expirar.
- **`/myip`**: Consulta o endereço IP público de saída do bot com geolocalização e provedor/ASN.

### 🧮 3. Calculadora de Sub-redes IPv4 / IPv6
- **`/subnet <ip/cidr>`**:
  - Máscara de sub-rede decimal (`255.255.255.192`) e wildcard (`0.0.0.63`)
  - Endereço de rede e broadcast
  - Primeiro e último host utilizável
  - Total de máquinas válidas utilizáveis
  - Classe do IP e escopo (Privado RFC 1918, Público ou Loopback)

### 🖥️ 4. Telemetria do Servidor
- **`/server`**: Gráficos e métricas de hardware da máquina hospedeira em tempo real:
  - Uso de CPU (%) e contagem de núcleos
  - Consumo de Memória RAM usada vs livre
  - Armazenamento em disco
  - **Tráfego de rede nas interfaces** (upload/download e pacotes trafegados)

---

## 💡 Guia Rápido de Comandos

| Comando | Descrição |
|---|---|
| `/start` | Abre o menu principal interativo com botões rápidos |
| `/status` | Exibe o painel visual de saúde de todos os hosts monitorados |
| `/monitorar add <host>` | Cadastra um IP, site ou porta para monitoramento contínuo |
| `/monitorar list` | Lista todos os hosts cadastrados e seus respectivos IDs |
| `/monitorar remove <id>` | Remove um host do monitoramento |
| `/ping <host>` | Teste de latência ICMP (ex: `/ping 8.8.8.8`) |
| `/portscan <host>` | Varredura de portas abertas em um servidor |
| `/subnet <ip/cidr>` | Cálculo de sub-redes (ex: `/subnet 192.168.1.10/26`) |
| `/dns <domínio> [tipo]` | Consulta registros DNS (ex: `/dns google.com MX`) |
| `/cert <domínio>` | Auditoria de certificado SSL/TLS (ex: `/cert github.com`) |
| `/server` | Telemetria de CPU, RAM, Disco e tráfego de rede |
| `/myip` | Exibe o IP público do bot e dados do provedor |
| `/ajuda` | Manual completo de comandos e sintaxe |

---

## 🛠️ Tecnologias Utilizadas

- **Python 3.10+**
- **aiogram 3.x** *(Framework moderno assíncrono para a API do Telegram)*
- **dnspython** *(Consultas DNS de precisão)*
- **psutil** *(Telemetria de sistema e placas de rede)*
- **ipaddress** *(Biblioteca padrão de cálculo de redes)*
- **SQLite** *(Persistência local leve para hosts monitorados)*

---

## 🚀 Como Executar

1. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
2. Configure suas variáveis de ambiente no arquivo `.env`:
   ```env
   TELEGRAM_BOT_TOKEN=seu_token_aqui
   CHECK_INTERVAL_SECONDS=60
   ```
3. Inicie o bot:
   ```bash
   python main.py
   ```
