import sqlite3
from pathlib import Path
from logging_config import logger
DB_PATH = Path("channels.db")


def get_connection():
    conn = sqlite3.connect("../admin_bot/channels.db")
    conn.row_factory = sqlite3.Row
    return conn


def get_active_channels():
    with get_connection() as conn:
        cursor = conn.execute("SELECT * FROM channels WHERE forwarding_enabled = 1")
        return [dict(row) for row in cursor.fetchall()]


def set_channel_enabled(chat_id: int, enabled: int):
    with get_connection() as conn:
        print("Обновление канала:", chat_id, enabled)
        cursor = conn.execute("UPDATE channels SET forwarding_enabled = ? WHERE chat_id = ?",
                              (int(enabled), str(chat_id)))
        conn.commit()
        print("Обновлено строк:", cursor.rowcount)


def ensure_channel_exists(chat_id: str, title: str, forwarding_enabled: int = 1):
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR IGNORE INTO channels (chat_id, title, forwarding_enabled)
            VALUES (?, ?, ?)
        """, (chat_id, title, forwarding_enabled))

        conn.commit()


def save_channels_to_db(channels):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS channels (
                chat_id INTEGER PRIMARY KEY,
                title TEXT,
                forwarding_enabled INTEGER DEFAULT 0
            )
        """)

        for channel in channels:
            cursor.execute("""
                INSERT OR IGNORE INTO channels (chat_id, title, forwarding_enabled)
                VALUES (?, ?, 0)
            """, (channel['id'], channel['title']))

        conn.commit()
        logger.info('Список каналов обновлён')