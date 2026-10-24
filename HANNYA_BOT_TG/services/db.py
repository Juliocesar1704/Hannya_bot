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
    """Cria as tabelas do banco de dados caso não existam."""
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
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ping_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                host_id INTEGER NOT NULL,
                timestamp TEXT NOT NULL,
                latency_ms REAL NOT NULL,
                status TEXT NOT NULL,
                FOREIGN KEY (host_id) REFERENCES monitored_hosts(id) ON DELETE CASCADE
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS webhook_subscribers (
                chat_id INTEGER PRIMARY KEY,
                created_at TEXT NOT NULL
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


def get_host(host_id: int) -> sqlite3.Row | None:
    """Busca um host específico por ID."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM monitored_hosts WHERE id = ?", (host_id,))
        return cursor.fetchone()


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
        cursor.execute("DELETE FROM ping_history WHERE host_id = ?", (host_id,))
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
    """Atualiza o resultado da última checagem de um host e grava histórico."""
    now = datetime.now(timezone.utc)
    now_str = now.strftime("%d/%m/%Y %H:%M:%S")
    time_short = now.strftime("%H:%M")
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE monitored_hosts
            SET last_status = ?, last_latency_ms = ?, fail_count = ?, last_checked = ?
            WHERE id = ?
        """, (status, round(latency_ms, 2), fail_count, now_str, host_id))
        cursor.execute("""
            INSERT INTO ping_history (host_id, timestamp, latency_ms, status)
            VALUES (?, ?, ?, ?)
        """, (host_id, time_short, round(latency_ms, 2), status))
        # Mantém histórico limitado aos últimos 60 registros por host
        cursor.execute("""
            DELETE FROM ping_history
            WHERE id NOT IN (
                SELECT id FROM ping_history WHERE host_id = ? ORDER BY id DESC LIMIT 60
            ) AND host_id = ?
        """, (host_id, host_id))
        conn.commit()


def get_host_history(host_id: int, limit: int = 30) -> list[sqlite3.Row]:
    """Retorna o histórico recente de latência para gerar gráfico."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT timestamp, latency_ms, status FROM ping_history
            WHERE host_id = ?
            ORDER BY id ASC
            LIMIT ?
        """, (host_id, limit))
        return cursor.fetchall()


def register_webhook_subscriber(chat_id: int) -> bool:
    """Inscreve um chat para receber alertas de Webhooks externos."""
    now_str = datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M:%S")
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO webhook_subscribers (chat_id, created_at)
            VALUES (?, ?)
        """, (chat_id, now_str))
        conn.commit()
        return True


def unregister_webhook_subscriber(chat_id: int) -> bool:
    """Remove a inscrição de um chat para alertas de Webhooks."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM webhook_subscribers WHERE chat_id = ?", (chat_id,))
        conn.commit()
        return cursor.rowcount > 0


def get_webhook_subscribers() -> list[int]:
    """Retorna a lista de chat_ids que devem receber alertas de Webhook."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT chat_id FROM webhook_subscribers")
        return [row["chat_id"] for row in cursor.fetchall()]


# Inicializa as tabelas na importação
init_db()
