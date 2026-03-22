import sqlite3
import random
import string
from contextlib import contextmanager
from typing import Optional

DB_PATH = "urls.db"
MAX_URLS = 500
CODE_LENGTH = 6
ALPHABET = string.ascii_letters + string.digits


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS urls (
                short_code   TEXT PRIMARY KEY,
                original_url TEXT NOT NULL,
                created_at   TEXT NOT NULL DEFAULT (datetime('now'))
            )
        """)


def _generate_code() -> str:
    return "".join(random.choices(ALPHABET, k=CODE_LENGTH))


def count_urls() -> int:
    with get_conn() as conn:
        row = conn.execute("SELECT COUNT(*) FROM urls").fetchone()
        return row[0]


def create_short_url(original_url: str) -> Optional[dict]:
    """Returns the new record, or None if the 500-URL cap is reached."""
    if count_urls() >= MAX_URLS:
        return None

    with get_conn() as conn:
        for _ in range(10):
            code = _generate_code()
            exists = conn.execute(
                "SELECT 1 FROM urls WHERE short_code = ?", (code,)
            ).fetchone()
            if not exists:
                conn.execute(
                    "INSERT INTO urls (short_code, original_url) VALUES (?, ?)",
                    (code, original_url),
                )
                row = conn.execute(
                    "SELECT * FROM urls WHERE short_code = ?", (code,)
                ).fetchone()
                return dict(row)
    return None


def get_url(short_code: str) -> Optional[dict]:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM urls WHERE short_code = ?", (short_code,)
        ).fetchone()
        return dict(row) if row else None


def list_urls() -> list:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM urls ORDER BY created_at DESC"
        ).fetchall()
        return [dict(r) for r in rows]


def delete_url(short_code: str) -> bool:
    with get_conn() as conn:
        cursor = conn.execute(
            "DELETE FROM urls WHERE short_code = ?", (short_code,)
        )
        return cursor.rowcount > 0
