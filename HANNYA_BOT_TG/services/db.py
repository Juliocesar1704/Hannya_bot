# services/db.py
import sqlite3
from pathlib import Path
from datetime import datetime, timezone

DB_DIR = Path(__file__).resolve().parent.parent / "data"
DB_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DB_DIR / "tg_netwatch.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Cria a tabela de hosts monitorados caso não exista."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS monitored_hosts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER NOT NULL,
                host TEXT NOT NULL,
                port INTEGER,
                check_type TEXT NOT NULL,
                name TEXT,
                is_active INTEGER DEFAULT 1,
                last_status TEXT DEFAULT 'UNKNOWN',
                last_latency_ms REAL DEFAULT 0.0,
                last_checked TEXT,
                fail_count INTEGER DEFAULT 0
            )
        """)
        conn.commit()


def add_host(chat_id: int, host: str, check_type: str = "PING", port: int = None, name: str = None) -> int:
    """Cadastra um novo host para monitoramento."""
    now_str = datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M:%S")
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO monitored_hosts (chat_id, host, port, check_type, name, is_active, last_status, last_checked)
            VALUES (?, ?, ?, ?, ?, 1, 'UNKNOWN', ?)
        """, (chat_id, host.strip(), port, check_type.upper(), name or host.strip(), now_str))
        conn.commit()
        return cursor.lastrowid


def get_user_hosts(chat_id: int) -> list[sqlite3.Row]:
    """Retorna todos os hosts cadastrados por um usuário/chat específico."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM monitored_hosts
            WHERE chat_id = ?
            ORDER BY id ASC
        """, (chat_id,))
        return cursor.fetchall()


def delete_host(host_id: int, chat_id: int) -> bool:
    """Remove um host do monitoramento."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM monitored_hosts
            WHERE id = ? AND chat_id = ?
        """, (host_id, chat_id))
        conn.commit()
        return cursor.rowcount > 0


def get_all_active_hosts() -> list[sqlite3.Row]:
    """Retorna todos os hosts ativos para a tarefa em background checar."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM monitored_hosts
            WHERE is_active = 1
        """)
        return cursor.fetchall()


def update_host_result(host_id: int, status: str, latency_ms: float, fail_count: int):
    """Atualiza o resultado da última checagem de um host."""
    now_str = datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M:%S")
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE monitored_hosts
            SET last_status = ?, last_latency_ms = ?, fail_count = ?, last_checked = ?
            WHERE id = ?
        """, (status, round(latency_ms, 2), fail_count, now_str, host_id))
        conn.commit()


# Inicializa as tabelas na importação
init_db()
