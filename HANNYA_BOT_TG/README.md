<p align="center">
  <img src="../assets/hannya_banner_hd.png" alt="Hannya NetWatch Banner" width="100%">
</p>

# 📡 Hannya NetWatch — Telegram Bot

> *“A máscara não esconde as falhas. Ela vigia cada pacote que atravessa a rede.”*

O **Hannya NetWatch** é o módulo do Projeto Hannya desenvolvido sob medida para **estudantes e profissionais de Redes de Computadores e Infraestrutura**. Ele transforma seu Telegram em um centro de operações de rede (NOC) de bolso, permitindo diagnosticar conexões, calcular sub-redes e receber alertas imediatos quando seus servidores ficarem fora do ar.

---

## ⚙️ Principais Funcionalidades

### 🚨 1. Monitoramento Contínuo com Alertas em Tempo Real & Gráficos
- **Sentinela em Background:** O bot verifica automaticamente a cada 60 segundos a saúde de todos os seus hosts cadastrados.
- **Alertas Instantâneos no Privado:** Se um servidor, site ou porta parar de responder, você recebe uma notificação de emergência imediata no Telegram.
- **Gráficos Visuais de Latência (`/grafico`):** Gera um gráfico dark cyberpunk com o histórico recente de tempo de resposta gerado com `matplotlib`.
- **Botões Inline Interativos:** Na listagem `/monitorar list` ou `/status`, toque diretamente nos botões para testar na hora, gerar gráficos ou remover o nó.

### 🔍 2. Diagnósticos Avançados de Redes & Telecom
- **`/traceroute <host>`**: Rastreamento de saltos (*hops*) e tempos de resposta de cada roteador no caminho até o destino.
- **`/whois <ip/domínio>` & `/geo <ip>`**: Consulta o Sistema Autônomo (**ASN** / BGP), operadora/ISP, país, cidade e coordenadas geográficas.
- **`/mac <endereço MAC>`**: Identifica o fabricante da placa de rede através do prefixo OUI (Cisco, MikroTik, Huawei, Intel, Ubiquiti, etc.).
- **`/ping <host>`**: Mede latência (RTT) e perda de pacotes via ICMP de forma assíncrona.
- **`/portscan <host>`**: Varre portas TCP principais (SSH, Web, MySQL, RDP, Minecraft, etc.) e identifica serviços abertos.
- **`/dns <domínio> [tipo]`**: Consulta registros DNS (`A`, `AAAA`, `MX`, `TXT`, `NS`, `CNAME`).
- **`/cert <domínio>`**: Checa a validade de certificados SSL/TLS, autoridade emissora e dias restantes antes de expirar.
- **`/myip`**: Consulta o endereço IP público de saída do bot com geolocalização e provedor/ASN.

### 🧮 3. Modo Acadêmico & Cisco CCNA
- **`/subnet <ip/cidr>`**:
  - Máscara decimal e hexadecimal
  - Máscara Curinga / Wildcard (essencial para ACLs Cisco/Huawei)
  - Primeiro e último host utilizável
  - Total de máquinas válidas utilizáveis e escopo (Privado, Público, Loopback).
- **`/vlsm <bloco> <hosts>`**: Divisão otimizada de sub-redes em tamanho variável (VLSM) ordenada por demanda, calculando o melhor prefixo sem desperdício de IPs.
- **`/cisco`**: Gerador interativo de configurações Cisco IOS para colar no console (VLANs, Router-on-a-stick, OSPFv2, DHCP Server, NAT PAT Overload).

### 🛡️ 4. Segurança de Infraestrutura & Hardening
- **`/headers <url>`**: Auditoria OWASP de cabeçalhos HTTP com nota de segurança (**A+ a F**), checando HSTS, CSP, X-Frame-Options, X-Content-Type-Options e vazamento de servidor.
- **`/blacklist <ip>`**: Consulta o IP em 5 listas DNSBL globais de reputação (Spamhaus, SpamCop, Barracuda, SORBS, UCEPROTECT).
- **`/dnssec <domínio>`**: Valida se o domínio possui assinaturas criptográficas DNSKEY e DS ativas contra ataques de DNS Spoofing.

### ⚡ 5. Servidor de Webhooks para Integrações Externas
- Servidor HTTP leve embutido na porta `8088` (`POST /webhook/alert`).
- Receba alertas automáticos de ferramentas como **Zabbix**, **Grafana**, **Uptime Kuma**, **Prometheus** ou **GitHub Actions** diretamente no seu Telegram.
- Comando `/webhook` para habilitar ou desabilitar alertas no chat.

### 🖥️ 6. Telemetria do Servidor
- **`/server`**: Gráficos e métricas de hardware da máquina hospedeira em tempo real:
  - Uso de CPU (%) e contagem de núcleos
  - Consumo de Memória RAM usada vs livre
  - Armazenamento em disco
  - Tráfego de rede nas interfaces (upload/download e pacotes trafegados).

---

## 💡 Guia Rápido de Comandos

| Comando | Descrição |
|---|---|
| `/start` | Abre o menu principal interativo com botões rápidos |
| `/status` | Painel visual de saúde com botões interativos e gráficos |
| `/grafico [id]` | Gera o gráfico visual de latência do host monitorado |
| `/monitorar add <host>` | Cadastra um IP, site ou porta para monitoramento contínuo |
| `/monitorar list` | Lista todos os hosts cadastrados com botões de ação rápida |
| `/monitorar remove <id>` | Remove um host do monitoramento |
| `/ping <host>` | Teste de latência ICMP assíncrono |
| `/traceroute <host>` | Rastreamento de saltos (*hops*) na rota |
| `/whois <ip/domínio>` | Consulta ASN, ISP, operadora e geolocalização |
| `/mac <endereço MAC>` | Identifica o fabricante da placa de rede (OUI) |
| `/portscan <host>` | Varredura de portas abertas em um servidor |
| `/subnet <ip/cidr>` | Cálculo de sub-redes IPv4 / IPv6 com Wildcard |
| `/vlsm <bloco> <hosts>` | Calculadora de sub-redes em tamanho variável VLSM |
| `/cisco` | Gerador interativo de templates Cisco IOS (CCNA) |
| `/headers <url>` | Auditoria de cabeçalhos de segurança HTTP (A+ a F) |
| `/blacklist <ip>` | Consulta em 5 listas DNSBL de spam e malware |
| `/dnssec <domínio>` | Validação de chaves criptográficas DNSSEC |
| `/dns <domínio> [tipo]` | Consulta registros DNS (`A`, `MX`, `TXT`, `NS`...) |
| `/cert <domínio>` | Auditoria de certificado SSL/TLS |
| `/webhook` | Configuração de integração de webhooks externos |
| `/server` | Telemetria de CPU, RAM, Disco e tráfego de rede |
| `/myip` | Exibe o IP público do bot e dados do provedor |
| `/ajuda` | Manual completo de comandos e sintaxe |

---

## 🛠️ Tecnologias Utilizadas

- **Python 3.10+**
- **aiogram 3.x** *(Framework moderno assíncrono para a API do Telegram)*
- **matplotlib** *(Geração de gráficos de latência em tema dark)*
- **aiohttp** *(Servidor HTTP de Webhooks e requisições assíncronas)*
- **dnspython** *(Consultas DNS de precisão e validação DNSSEC/DNSBL)*
- **psutil** *(Telemetria de sistema e placas de rede)*
- **ipaddress** *(Cálculos matemáticos de rede e VLSM)*
- **SQLite** *(Persistência local leve para hosts monitorados e histórico de latência)*

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
   WEBHOOK_PORT=8088
   WEBHOOK_HOST=0.0.0.0
   ```
3. Inicie o bot:
   ```bash
   python main.py
   ```
