# cogs/utils.py
import discord
import logging

logger = logging.getLogger(__name__)

async def safe_send(ctx, content=None, embed=None):
    """Envia uma mensagem de forma segura capturando exceções de permissão."""
    try:
        return await ctx.send(content=content, embed=embed)
    except discord.Forbidden:
        logger.error("O bot não tem permissão para enviar mensagens no canal.")
    except discord.HTTPException as e:
        logger.error(f"Falha ao enviar mensagem: {e}")
    return None


async def safe_reply(message: discord.Message, content=None, embed=None):
    """Responde a uma mensagem de forma segura capturando exceções."""
    try:
        return await message.reply(content=content, embed=embed)
    except discord.Forbidden:
        logger.error("O bot não tem permissão para responder no canal.")
    except Exception as e:
        logger.error(f"Erro em safe_reply(): {e}")
    return None