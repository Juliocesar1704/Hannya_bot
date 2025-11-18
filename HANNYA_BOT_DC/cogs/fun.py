# cogs/fun.py
import random
import discord
import logging
from discord.ext import commands
from cogs.utils import safe_send

class Fun(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    # ============================
    # !ola
    # ============================
    @commands.command(name="ola", help="Envia uma saudação simpática da Hannya para o usuário.")
    async def ola(self, ctx):
        await ctx.send("Olá! 🌸 A Hannya está aqui para te ajudar")

    # ================================
    # !ping - Mostra a latência do bot
    # ================================
    @commands.command(name="ping", help="Mostra a latência do bot.")
    async def ping(self, ctx):
        latency = round(self.bot.latency * 1000)
        color = (
            discord.Color.green() if latency < 150 
            else discord.Color.orange() if latency < 300 
            else discord.Color.red()
        )

        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"Latência: `{latency} ms`",
            color=color
        )

        await ctx.send(embed=embed)

    # ================================
    # !dado - Rola um dado customizável
    # ================================
    @commands.command(name="dado", help="Rola um dado de N lados (padrão: 6).")
    async def dado(self, ctx, lados: int = 6):
        if lados < 2:
            await ctx.send("⚠️ O dado precisa ter pelo menos 2 lados.")
            return

        resultado = random.randint(1, lados)
        await ctx.send(f"🎲 Você rolou um dado de {lados} lados: **{resultado}**!")

    # ================================
    # !moeda - Joga uma moeda
    # ================================
    @commands.command(name="moeda", help="Joga uma moeda.")
    async def moeda(self, ctx):
        resultado = random.choice(["Cara 🪙", "Coroa 🪙"])
        await ctx.send(f"A moeda caiu em: **{resultado}**!")

    # ================================
    # !piada - Conta uma piada
    # ================================
    @commands.command(name="piada", help="Conta uma piada aleatória.")
    async def piada(self, ctx):
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
        await ctx.send(random.choice(piadas))

    # ================================
    # !8ball - Pergunta mística
    # ================================
    @commands.command(name="8ball", help="Responde perguntas de forma mística.")
    async def _8ball(self, ctx, *, pergunta: str):
        respostas = [
            "🔮 Com certeza!", "🔮 Provavelmente sim.", "🔮 Não conte com isso...",
            "🔮 É incerto no momento.", "🔮 Pode apostar!", "🔮 Me pergunte mais tarde.",
            "🔮 Melhor não responder agora.", "🔮 Sinais apontam que sim.",
            "🔮 As estrelas dizem que sim.", "🔮 Acho que não.", "🔮 Definitivamente!",
            "🔮 Não mesmo.", "🔮 Sem dúvida!", "🔮 Meu palpite é sim.", "🔮 Difícil dizer agora."
        ]
        await ctx.send(f"**Pergunta:** {pergunta}\n**Resposta:** {random.choice(respostas)}")

    # ================================
    # !hug - Abraço virtual
    # ================================
    @commands.command(name="hug", help="Envia um abraço virtual para alguém.")
    async def hug(self, ctx, membro: discord.Member):
        gifs = [
            "https://media.giphy.com/media/l2QDM9Jnim1YVILXa/giphy.gif",
            "https://media.giphy.com/media/od5H3PmEG5EVq/giphy.gif",
            "https://media.giphy.com/media/143v0Z4767T15e/giphy.gif",
            "https://media.giphy.com/media/wnsgren9NtITS/giphy.gif",
            "https://media.giphy.com/media/11cB1sJt4f1c3G/giphy.gif"
        ]
        await ctx.send(f"{ctx.author.mention} deu um abraço em {membro.mention} 🤗\n{random.choice(gifs)}")

    # ================================
    # !kiss - Beijo virtual
    # ================================
    @commands.command(name="kiss", help="Envia um beijo virtual para alguém.")
    async def kiss(self, ctx, membro: discord.Member):
        gifs = [
            "https://media.giphy.com/media/G3va31oEEnIkM/giphy.gif",
            "https://media.giphy.com/media/bGm9FuBCGg4SY/giphy.gif",
            "https://media.giphy.com/media/FqBTvSNjNzeZG/giphy.gif",
            "https://media.giphy.com/media/ZQN9TsG70eEgQ/giphy.gif",
            "https://media.giphy.com/media/3ZnBrkqoaI2hq/giphy.gif"
        ]
        await ctx.send(f"{ctx.author.mention} deu um beijo em {membro.mention} 😘\n{random.choice(gifs)}")

    # ================================
    # !fortune - Biscoito da sorte
    # ================================
    @commands.command(name="fortune", help="Receba uma frase de sorte.")
    async def fortune(self, ctx):
        mensagens = [
            "🌟 Hoje é um ótimo dia para começar algo novo!",
            "💡 Uma surpresa agradável está a caminho.",
            "🍀 A sorte está do seu lado hoje.",
            "🔥 Cuidado com decisões impulsivas!",
            "🎯 Concentre-se nos seus objetivos, sucesso vem!",
            "😄 Sorria, coisas boas vão acontecer.",
            "💫 O universo conspira a seu favor.",
            "🪄 Grandes mudanças estão chegando!",
            "🌞 Aproveite cada momento do dia.",
            "🧩 Algo inesperado vai se encaixar perfeitamente."
        ]
        await ctx.send(random.choice(mensagens))

    # ================================
    # !meme - Meme aleatório
    # ================================
    @commands.command(name="meme", help="Envia um meme aleatório.")
    async def meme(self, ctx):
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
        await ctx.send(random.choice(memes))

    # ================================
    # !roll_number - Número aleatório
    # ================================
    @commands.command(name="roll_number", help="Sorteia um número entre mínimo e máximo.")
    async def roll_number(self, ctx, min: int, max: int):
        if min > max:
            await ctx.send("⚠️ O número mínimo não pode ser maior que o máximo.")
            return
        
        resultado = random.randint(min, max)
        await ctx.send(f"🎲 Número sorteado entre {min} e {max}: **{resultado}**")

# ================================
# SETUP
# ================================
async def setup(bot: commands.Bot):
    await bot.add_cog(Fun(bot))
    logging.info("✔ Cog 'Fun' registrada com prefix commands!")
