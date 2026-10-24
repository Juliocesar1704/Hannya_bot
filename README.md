<p align="center">
  <img src="assets/hannya_banner_hd.png" alt="Projeto Hannya Banner" width="100%">
</p>

<h1 align="center">Projeto Hannya — Bots Multiplataforma</h1>

<p align="center"><i>A máscara não esconde. Ela revela o que as palavras não dizem.</i></p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/Discord.py-2.7%2B-5865F2?style=for-the-badge&logo=discord&logoColor=white" alt="Discord.py">
  <img src="https://img.shields.io/badge/Spotify-Support-1DB954?style=for-the-badge&logo=spotify&logoColor=white" alt="Spotify">
  <img src="https://img.shields.io/badge/Status-Ativo-success?style=for-the-badge" alt="Status">
</p>

---

## 📌 Sobre o Projeto

O **Hannya** é um conjunto de bots desenvolvidos para diferentes plataformas, como **Discord**, **Telegram** e outras integrações.  

Este repositório reúne:

- 🤖 **Hannya Discord Bot**  
- 💬 **Hannya Telegram Bot**  
- 📱 Futuras integrações com outros serviços  
- 🧩 Ferramentas internas, módulos auxiliares e utilitários

---

## 🏛️ Estrutura de Pastas do Repositório

Cada bot possui sua própria pasta, organizada de forma independente:

```
HANNYA_BOTS/
├── HANNYA_BOT_DC/           # Bot para Discord (Música, Moderação, Slash Commands)
│   ├── cogs/
│   │   ├── music.py         # Reprodução de música (YouTube, Spotify, FFmpeg)
│   │   ├── fun.py           # Comandos de diversão e interação
│   │   ├── admin.py         # Moderação avançada e advertências (warns)
│   │   ├── info.py          # /userinfo e /serverinfo
│   │   ├── events.py        # Boas-vindas, status rotativo e anti-spam
│   │   ├── db.py            # Banco SQLite local
│   │   └── utils.py         # Utilitários assíncronos
│   ├── main.py              # Inicialização e sincronização dos Comandos Slash
│   └── requirements.txt
│
└── HANNYA_BOT_TG/           # Bot para Telegram (Hannya NetWatch — Redes & Monitoramento)
    ├── routers/
    │   ├── monitoring.py    # Monitoramento de Uptime com alertas automáticos
    │   ├── tools.py         # Ping, Portscan, DNS, SSL e IP público
    │   ├── subnet.py        # Calculadora de sub-redes IPv4 / IPv6
    │   ├── system.py        # Telemetria de CPU, RAM, Disco e interfaces de rede
    │   └── general.py       # Menu principal e comandos informativos
    ├── services/
    │   ├── db.py            # SQLite de hosts monitorados
    │   └── network.py       # Motor assíncrono de diagnósticos de rede
    ├── main.py              # Inicializador aiogram 3.x e sentinela em background
    └── requirements.txt
```
---

## 🧩 Filosofia do Projeto

O Hannya foi criado com três pilares:

### 🔥 **Modularidade**
Cada bot possui organização independente, podendo crescer sem quebrar outras partes.

### 👹 **Identidade**
A personalidade Hannya é mantida em todas as plataformas: enigmática, divertida e marcante.

### 🔒 **Segurança**
Tokens e dados sensíveis ficam sempre protegidos.  

---

## 🚀 Objetivos Futuros

✔ Integração com APIs externas  
✔ Painel Web para administração dos bots  
✔ Recursos avançados de logging  
🕸 Módulo de automação para servidores  
🔮 Versão "Hannya AI"  

---

## 🛠 Tecnologias

- Python 3.10+
- Discord.py / Nextcord
- Aiogram / python-telegram-bot
- Bibliotecas auxiliares diversas

---

## 💬 Contato & Contribuições

Sinta-se livre para sugerir melhorias, abrir issues e colaborar com o desenvolvimento.

---

