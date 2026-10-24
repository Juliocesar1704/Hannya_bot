<p align="center">
  <img src="../assets/hannya_banner_hd.png" alt="Hannya Discord Bot Banner" width="100%">
</p>

# 🏮 Hannya Bot

> “Mesmo uma máscara de fúria pode esconder sabedoria.”

O **Hannya Bot** é um bot para Discord inspirado nas máscaras tradicionais do teatro japonês *Noh*.  
Ele representa o equilíbrio entre o **caos e a ordem**, unindo automação, diversão e controle dentro dos servidores.  

Feito para quem quer **organizar e dar personalidade** à sua comunidade.

---

## 👹 O que é o Hannya?

A máscara **Hannya (般若)** é um símbolo clássico da cultura japonesa.  
Ela retrata uma mulher consumida por emoções intensas como raiva, ciúme e tristeza que, com o tempo, se transforma em **sabedoria e poder espiritual**.  

No contexto do bot, o Hannya reflete esse mesmo equilíbrio: **força, emoção e controle digital** dentro do Discord.

---

## ⚙️ Funcionalidades

- 🎭 **Comandos de diversão** — interações, respostas criativas e mensagens personalizadas.  
- 🛡️ **Moderação inteligente** — mantenha a ordem com comandos rápidos e seguros.  
- ⚙️ **Sistema modular (Cogs)** — o bot é dividido em módulos independentes.  
- 💬 **Integração fluida** — responde em tempo real com `discord.py` e `asyncio`.  

---

## 🚀 Adicione o Hannya ao seu servidor

Convide o bot para o seu servidor clicando no link abaixo 👇  

[✨ **Adicionar o Hannya ao Discord**](https://discord.com/oauth2/authorize?client_id=1380533833681600602) (O bot ainda não esta 100% funcional pois não consegui hospedar em nenhum lugar ainda)


---

## 💡 Comandos Slash do Hannya Bot (100% Nativos `/`)

Todos os comandos são agora executados nativamente via **Slash Commands (`/`)** com autocompletar e validação de argumentos pelo próprio Discord.

### 🎭 Diversão & Interação
| Comando | Descrição |
|----------|------------|
| `/ajuda` | Mostra o painel com todos os comandos disponíveis organizados por categorias. |
| `/ping` | Mostra a latência atual em milissegundos com a API do Discord. |
| `/ola` | Envia uma saudação amigável e personalizada da Hannya. |
| `/dado [lados]` | Rola um dado com o número de faces desejado (padrão: 6). |
| `/moeda` | Joga uma moeda para cima (Cara ou Coroa). |
| `/piada` | Conta uma piada divertida sobre tecnologia, programação ou cotidiano. |
| `/8ball [pergunta]` | Faz uma pergunta à esfera mística da Hannya. |
| `/numero [min] [max]` | Sorteia um número aleatório entre os valores informados. |
| `/hug [membro]` | Envia um abraço virtual carinhoso com GIF. |
| `/kiss [membro]` | Envia um beijo virtual amigável com GIF. |
| `/fortune` | Abre um biscoito da sorte com mensagens inspiradoras. |
| `/meme` | Envia uma imagem aleatória de meme. |

### 🎵 Música & Voz (YouTube & Spotify)
| Comando | Descrição |
|----------|------------|
| `/tocar [busca]` | Toca uma música no canal de voz (busca no YouTube, link de música, álbum ou Playlist do Spotify). |
| `/pular` | Pula a faixa atual para a próxima da fila. |
| `/pausar` | Pausa a música atual. |
| `/continuar` | Retoma a reprodução da música pausada. |
| `/loop` | Ativa ou desativa a repetição contínua da faixa atual. |
| `/parar` | Interrompe o áudio, limpa a fila e desconecta do canal de voz. |
| `/fila` | Exibe a lista das próximas faixas na fila de espera (incluindo faixas do Spotify). |
| `/tocando` | Mostra detalhes completos da música em reprodução (link, thumbnail, solicitante). |
| `/conectar` | Conecta a Hannya ao seu canal de voz atual. |
| `/desconectar` | Desconecta a Hannya do canal de voz. |

### ℹ️ Informações
| Comando | Descrição |
|----------|------------|
| `/userinfo [membro]` | Exibe perfil completo, data de criação da conta, data de entrada no servidor e lista de cargos. |
| `/serverinfo` | Exibe estatísticas completas do servidor (membros, bots, canais de texto/voz, impulsos, dono). |

### 🛡️ Moderação & Gestão
| Comando | Descrição |
|----------|------------|
| `/limpar [quantidade]` | Apaga até 100 mensagens em massa do canal atual. |
| `/warn [membro] [motivo]` | Aplica uma advertência formal registrada no banco de dados e notifica o usuário via DM. |
| `/warns [membro]` | Consulta o histórico de advertências ativas de um membro. |
| `/unwarn [aviso_id]` | Remove uma advertência do histórico utilizando o ID do aviso. |
| `/mute [membro] [tempo] [motivo]` | Silencia temporariamente um usuário utilizando o Timeout nativo do Discord (ex: `10m`, `1h`, `1d`). |
| `/unmute [membro]` | Remove o silêncio de um usuário antes do término do tempo. |
| `/kick [membro] [motivo]` | Expulsa um membro do servidor. |
| `/ban [membro] [motivo]` | Bane permanentemente um usuário do servidor. |
| `/unban [usuario_id]` | Desbane um usuário através do ID numérico ou nome. |
| `/lock` | Tranca o canal atual impedindo o envio de mensagens por membros comuns. |
| `/unlock` | Destranca o canal permitindo mensagens novamente. |
| `/falar [mensagem]` | Faz a Hannya falar uma mensagem de texto no canal. |
| `/anuncio [título] [descrição]` | Envia um anúncio formal e destacado no canal em formato Embed. |

---

## 🛡️ Recursos Automáticos de Segurança

- 🚫 **Bloqueio de Convites do Discord**: Detecta e deleta automaticamente links de convite para outros servidores enviados por membros comuns, alertando o usuário e registrando no canal de logs.
- ⚡ **Anti-Spam / Anti-Flood**: Detecta o envio excessivo de mensagens repetidas em poucos segundos, apagando e alertando o membro.
- 🎭 **Presença e Status Rotativo**: A Hannya alterna dinamicamente seu status no Discord a cada 2 minutos com frases imersivas e dados do servidor.
- 💾 **Persistência SQLite**: Histórico de advertências salvo localmente em banco de dados SQLite leve e seguro (`data/hannya.db`).

---

## ⚙️ Configuração e Execução

1. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
2. Configure o arquivo `.env` com suas credenciais:
   ```env
   DISCORD_TOKEN=seu_token_aqui
   APPLICATION_ID=1380533833681600602
   LOG_CHANNEL_ID=1406653101342986342
   WELCOME_CHANNEL_ID=990047988212727890
   ```
3. Inicie o bot:
   ```bash
   python main.py
   ```

---

## 🧩 Estrutura interna

```
HANNYA_BOT_DC/
├── cogs/
│   ├── music.py          # Comandos Slash de música, voz e fila (YouTube / FFmpeg)
│   ├── fun.py            # Comandos Slash de entretenimento
│   ├── admin.py          # Comandos Slash de moderação e advertências
│   ├── info.py           # Comandos Slash de informações (/userinfo, /serverinfo)
│   ├── events.py         # Eventos de boas-vindas, status rotativo e anti-spam
│   ├── db.py             # Gerenciamento de banco de dados SQLite (warns)
│   └── utils.py          # Funções auxiliares (safe_send, safe_reply)
├── data/                 # Banco de dados local (ignorado pelo Git)
├── main.py               # Inicialização, logging e sincronização de Slash Commands
├── config.py             # Configurações do token e canais
├── .env                  # Arquivo local com segredos (ignorado pelo Git)
├── .env.example          # Modelo de variáveis de ambiente
└── requirements.txt      # Dependências do projeto
```

Isso garante que ele possa crescer com novos módulos e atualizações sem perder estabilidade.

---

## 🧠 Tecnologias utilizadas

- **Python 3.10+**
- **discord.py**
- **python-dotenv**
- **asyncio**

---

## 💬 Contato e suporte

Caso queira reportar um bug, sugerir melhorias ou colaborar no desenvolvimento:
  
📫 **Entre em contato pelo Discord:** *https://discord.com/users/988984006672535562*
  
💻 **Repositório oficial:** (https://github.com/Juliocesar1704/Hannya_bot)

---

## 📜 Licença

Distribuído sob a licença **MIT**.  

Feito com ☕, 🧠 e um toque de cultura japonesa por Júlio César.


