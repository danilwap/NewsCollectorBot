import sqlite3
from pathlib import Path
from services.logging_config import logger

DB_PATH = Path("channels.db")

def init_db():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS channels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER UNIQUE,
                title TEXT,
                forwarding_enabled INTEGER DEFAULT 0
            )
        """)
        conn.commit()
        logger.info('База данных инициализирона')

def get_connection():
    conn = sqlite3.connect("channels.db")
    conn.row_factory = sqlite3.Row
    return conn


def get_active_channels():
    with get_connection() as conn:
        cursor = conn.execute("SELECT * FROM channels")
        return [dict(row) for row in cursor.fetchall()]

def set_channel_enabled(chat_id: int, enabled: int):
    with get_connection() as conn:
        print("Обновление канала:", chat_id, enabled)
        cursor = conn.execute("UPDATE channels SET forwarding_enabled = ? WHERE chat_id = ?", (int(enabled), str(chat_id)))
        conn.commit()
        print("Обновлено строк:", cursor.rowcount)

