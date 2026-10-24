# cogs/db.py
import sqlite3
import os
from pathlib import Path
from datetime import datetime, timezone

# Garante que a pasta data/ exista
DB_DIR = Path(__file__).resolve().parent.parent / "data"
DB_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DB_DIR / "hannya.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Inicializa as tabelas do banco de dados SQLite."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS warns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                moderator_id INTEGER NOT NULL,
                reason TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        conn.commit()


def add_warn(guild_id: int, user_id: int, moderator_id: int, reason: str) -> int:
    """Registra uma advertência e retorna o ID gerado."""
    now_str = datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M:%S")
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO warns (guild_id, user_id, moderator_id, reason, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (guild_id, user_id, moderator_id, reason, now_str))
        conn.commit()
        return cursor.lastrowid


def get_warns(guild_id: int, user_id: int) -> list[sqlite3.Row]:
    """Retorna a lista de advertências ativas de um usuário no servidor."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, moderator_id, reason, created_at
            FROM warns
            WHERE guild_id = ? AND user_id = ?
            ORDER BY id ASC
        """, (guild_id, user_id))
        return cursor.fetchall()


def remove_warn(warn_id: int, guild_id: int) -> bool:
    """Remove uma advertência específica pelo ID."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM warns
            WHERE id = ? AND guild_id = ?
        """, (warn_id, guild_id))
        conn.commit()
        return cursor.rowcount > 0


def clear_warns(guild_id: int, user_id: int) -> int:
    """Limpa todas as advertências de um usuário."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM warns
            WHERE guild_id = ? AND user_id = ?
        """, (guild_id, user_id))
        conn.commit()
        return cursor.rowcount


# Inicializa o banco na importação
init_db()
