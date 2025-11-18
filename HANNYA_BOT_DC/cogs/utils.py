# cogs/utils.py
import discord
import logging

# Configura logs
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


async def safe_send(ctx, content=None, embed=None):
    
    try:
        await ctx.send(content=content, embed=embed)

    except discord.Forbidden:
        logging.error("O bot não tem permissão para enviar mensagens no canal.")

    except discord.HTTPException as e:
        logging.error(f"Falha ao enviar mensagem: {e}")


async def safe_reply(message: discord.Message, content=None, embed=None):
  
    try:
        await message.reply(content=content, embed=embed)
    except Exception as e:
        logging.error(f"Erro em safe_reply(): {e}")