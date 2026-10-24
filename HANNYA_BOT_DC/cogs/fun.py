# cogs/fun.py
import random
import discord
from discord import app_commands
from discord.ext import commands


class Fun(commands.Cog):
    """Comandos Slash de entretenimento, sorteios e interação social."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # ============================================================
    # /ping
    # ============================================================
    @app_commands.command(name="ping", description="Mostra a latência atual da Hannya com a API do Discord.")
    async def ping(self, interaction: discord.Interaction):
        latency = round(self.bot.latency * 1000)
        color = (
            discord.Color.green() if latency < 150 
            else discord.Color.orange() if latency < 300 
            else discord.Color.red()
        )

        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"Latência da API: `{latency} ms`",
            color=color
        )
        await interaction.response.send_message(embed=embed)

    # ============================================================
    # /ola
    # ============================================================
    @app_commands.command(name="ola", description="Envia uma saudação personalizada e amigável da Hannya.")
    async def ola(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"Olá, {interaction.user.mention}! 🌸 A Hannya está aqui para servir ao Refúgio de Atlas.")

    # ============================================================
    # /dado
    # ============================================================
    @app_commands.command(name="dado", description="Rola um dado com a quantidade de lados informada.")
    @app_commands.describe(lados="Número de faces do dado (padrão: 6)")
    async def dado(self, interaction: discord.Interaction, lados: int = 6):
        if lados < 2:
            await interaction.response.send_message("⚠️ O dado precisa ter pelo menos 2 lados.", ephemeral=True)
            return

        resultado = random.randint(1, lados)
        await interaction.response.send_message(f"🎲 {interaction.user.mention} rolou um dado de **{lados} lados**: tirou **{resultado}**!")

    # ============================================================
    # /moeda
    # ============================================================
    @app_commands.command(name="moeda", description="Joga uma moeda para cima (Cara ou Coroa).")
    async def moeda(self, interaction: discord.Interaction):
        resultado = random.choice(["Cara 🪙", "Coroa 🪙"])
        await interaction.response.send_message(f"🪙 A moeda girou no ar e caiu em: **{resultado}**!")

    # ============================================================
    # /piada
    # ============================================================
    @app_commands.command(name="piada", description="Conta uma piada aleatória de tecnologia ou do dia a dia.")
    async def piada(self, interaction: discord.Interaction):
        piadas = [
            "Por que o computador foi ao médico? Porque estava com um vírus! 💻🤒",
            "O que o zero disse para o oito? Que cinto legal! 🎩",
            "Por que o Dev terminou com o banco de dados? Relacionamento complicado. 😅",
            "Como o Discord se despede? Falou no canal! 📡",
            "Por que o JavaScript terminou com o CSS? Porque tinha problemas de estilo. 😎",
            "O que um firewall disse para o outro? Bloqueando ou liberando? 🔥",
            "Por que os programadores adoram o Halloween? Porque é dia de quebrar tudo! 🎃",
            "Como o computador pega um resfriado? Ele abre muitas abas! 🤧",
            "Por que os bytes não vão à escola? Porque já sabem ler e escrever! 💾",
            "Qual é o animal mais tecnológico? O mouse! 🐭💻",
            "Por que o Python não briga com ninguém? Porque ele resolve tudo com 'import peace'. 🐍✌️",
            "O que o programador pediu no restaurante? Um byte para comer. 🍽️",
            "Por que os algoritmos nunca ficam doentes? Porque eles têm boas funções! 🏥"
        ]
        await interaction.response.send_message(random.choice(piadas))

    # ============================================================
    # /8ball
    # ============================================================
    @app_commands.command(name="8ball", description="Faz uma pergunta à esfera mística da Hannya.")
    @app_commands.describe(pergunta="Qual pergunta deseja fazer à sabedoria das sombras?")
    async def _8ball(self, interaction: discord.Interaction, pergunta: str):
        respostas = [
            "🔮 Com certeza!", "🔮 Provavelmente sim.", "🔮 Não conte com isso...",
            "🔮 É incerto no momento.", "🔮 Pode apostar!", "🔮 Me pergunte mais tarde.",
            "🔮 Melhor não responder agora.", "🔮 Sinais apontam que sim.",
            "🔮 As estrelas dizem que sim.", "🔮 Acho que não.", "🔮 Definitivamente!",
            "🔮 Não mesmo.", "🔮 Sem dúvida!", "🔮 Meu palpite é sim.", "🔮 Difícil dizer agora."
        ]
        await interaction.response.send_message(f"💬 **Pergunta:** {pergunta}\n✨ **Resposta:** {random.choice(respostas)}")

    # ============================================================
    # /hug
    # ============================================================
    @app_commands.command(name="hug", description="Envia um abraço carinhoso com GIF para um membro.")
    @app_commands.describe(membro="Quem receberá o seu abraço?")
    async def hug(self, interaction: discord.Interaction, membro: discord.Member):
        gifs = [
            "https://media.giphy.com/media/l2QDM9Jnim1YVILXa/giphy.gif",
            "https://media.giphy.com/media/od5H3PmEG5EVq/giphy.gif",
            "https://media.giphy.com/media/143v0Z4767T15e/giphy.gif",
            "https://media.giphy.com/media/wnsgren9NtITS/giphy.gif",
            "https://media.giphy.com/media/11cB1sJt4f1c3G/giphy.gif"
        ]
        await interaction.response.send_message(f"{interaction.user.mention} deu um forte abraço em {membro.mention}! 🤗\n{random.choice(gifs)}")

    # ============================================================
    # /kiss
    # ============================================================
    @app_commands.command(name="kiss", description="Envia um beijo amigável com GIF para um membro.")
    @app_commands.describe(membro="Quem receberá o seu beijo?")
    async def kiss(self, interaction: discord.Interaction, membro: discord.Member):
        gifs = [
            "https://media.giphy.com/media/G3va31oEEnIkM/giphy.gif",
            "https://media.giphy.com/media/bGm9FuBCGg4SY/giphy.gif",
            "https://media.giphy.com/media/FqBTvSNjNzeZG/giphy.gif",
            "https://media.giphy.com/media/ZQN9TsG70eEgQ/giphy.gif",
            "https://media.giphy.com/media/3ZnBrkqoaI2hq/giphy.gif"
        ]
        await interaction.response.send_message(f"{interaction.user.mention} enviou um beijo para {membro.mention}! 😘\n{random.choice(gifs)}")

    # ============================================================
    # /fortune
    # ============================================================
    @app_commands.command(name="fortune", description="Abre um biscoito da sorte com mensagens inspiradoras.")
    async def fortune(self, interaction: discord.Interaction):
        mensagens = [
            "🌟 Hoje é um ótimo dia para começar algo novo!",
            "💡 Uma surpresa agradável está a caminho.",
            "🍀 A sorte está do seu lado hoje.",
            "🔥 Cuidado com decisões impulsivas!",
            "🎯 Concentre-se nos seus objetivos, o sucesso vem!",
            "😄 Sorria, coisas boas vão acontecer.",
            "💫 O universo conspira a seu favor.",
            "🪄 Grandes mudanças estão chegando!",
            "🌞 Aproveite cada momento do dia.",
            "🧩 Algo inesperado vai se encaixar perfeitamente."
        ]
        await interaction.response.send_message(f"🥠 **Seu biscoito da sorte revela:**\n> *\"{random.choice(mensagens)}\"*")

    # ============================================================
    # /meme
    # ============================================================
    @app_commands.command(name="meme", description="Envia uma imagem aleatória de meme.")
    async def meme(self, interaction: discord.Interaction):
        memes = [
            "https://i.imgflip.com/5p2n2b.jpg",
            "https://i.imgflip.com/5p2n4t.jpg",
            "https://i.imgflip.com/5p2n6w.jpg",
            "https://i.imgflip.com/5p2n9y.jpg",
            "https://i.imgflip.com/5p2nbh.jpg",
            "https://i.imgflip.com/5p2ndm.jpg",
            "https://i.imgflip.com/5p2nfg.jpg",
            "https://i.imgflip.com/5p2nh1.jpg"
        ]
        await interaction.response.send_message(random.choice(memes))

    # ============================================================
    # /numero
    # ============================================================
    @app_commands.command(name="numero", description="Sorteia um número aleatório entre os limites definidos.")
    @app_commands.describe(minimo="Valor mínimo (padrão: 1)", maximo="Valor máximo (padrão: 100)")
    async def numero(self, interaction: discord.Interaction, minimo: int = 1, maximo: int = 100):
        if minimo > maximo:
            await interaction.response.send_message("⚠️ O valor mínimo não pode ser maior do que o valor máximo.", ephemeral=True)
            return

        resultado = random.randint(minimo, maximo)
        await interaction.response.send_message(f"🎲 Sorteio realizado entre `{minimo}` e `{maximo}`: **{resultado}**!")


async def setup(bot: commands.Bot):
    await bot.add_cog(Fun(bot))
