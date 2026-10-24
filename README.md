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
HANNYA_BOT_DC/
├── cogs/
│   ├── music.py          # Comandos Slash de música e voz (YouTube / Spotify / FFmpeg)
│   ├── fun.py            # Comandos Slash de diversão e interação
│   ├── admin.py          # Comandos Slash administrativos e advertências (warns)
│   ├── info.py           # Comandos Slash de informações (/userinfo, /serverinfo)
│   ├── events.py         # Eventos de boas-vindas, status rotativo e anti-spam
│   ├── db.py             # Banco de dados SQLite persistente
│   └── utils.py          # Funções auxiliares (safe_send, safe_reply)
├── main.py               # Inicialização e sincronização dos Comandos Slash
├── config.py             # Configurações com dotenv
├── .env.example          # Modelo de variáveis de ambiente
└── requirements.txt      # Dependências com suporte a voz (PyNaCl, davey, yt-dlp)

Mais em desenvolvimento ...
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

