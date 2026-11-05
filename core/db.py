"""SQLite connection, schema and migrations.

The schema is Postgres-compatible on purpose: when this moves to Supabase,
only this module changes. Nothing outside ``core`` opens a connection.
"""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager

from core import config

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    name          TEXT NOT NULL,
    email         TEXT UNIQUE,
    ui_language   TEXT NOT NULL DEFAULT 'en-IN',
    created_at    TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS lessons (
    id       TEXT PRIMARY KEY,
    subject  TEXT NOT NULL,
    grade    INTEGER NOT NULL,
    title_en TEXT NOT NULL,
    payload  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS progress (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL REFERENCES users(id),
    lesson_id   TEXT NOT NULL,
    segment_id  TEXT,
    status      TEXT NOT NULL,
    score       REAL,
    updated_at  TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(user_id, lesson_id, segment_id)
);

CREATE TABLE IF NOT EXISTS translations (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER,
    source_text TEXT NOT NULL,
    source_lang TEXT NOT NULL,
    target_lang TEXT NOT NULL,
    output_text TEXT NOT NULL,
    provider    TEXT NOT NULL,
    latency_ms  INTEGER,
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS events (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER,
    event_name  TEXT NOT NULL,
    props       TEXT,
    lang        TEXT,
    session_id  TEXT,
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_events_name_time ON events(event_name, created_at);
CREATE INDEX IF NOT EXISTS idx_events_lang ON events(lang);
CREATE INDEX IF NOT EXISTS idx_translations_pair ON translations(source_lang, target_lang);
"""


def connect() -> sqlite3.Connection:
    path = config.db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path), timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def get_conn() -> Iterator[sqlite3.Connection]:
    """Transactional connection: commits on success, always closes."""
    conn = connect()
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    """Idempotent schema creation. Safe to call on every app start."""
    with get_conn() as conn:
        conn.executescript(SCHEMA)


def ensure_local_user(ui_language: str = config.DEFAULT_LANG) -> int:
    """The single local learner used until real auth exists (Phase 5).

    Returns the user id, creating the row once and reusing it after that.
    """
    with get_conn() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO users (name, email, ui_language) VALUES (?, ?, ?)",
            ("Local learner", "local@demo.in", ui_language),
        )
        row = conn.execute(
            "SELECT id FROM users WHERE email = ?", ("local@demo.in",)
        ).fetchone()
        return int(row["id"])


def set_ui_language(user_id: int, lang: str) -> None:
    with get_conn() as conn:
        conn.execute("UPDATE users SET ui_language = ? WHERE id = ?", (lang, user_id))


def reset_db() -> None:
    """Delete the database file. Dev and tests only — never called by pages."""
    path = config.db_path()
    if path.exists():
        path.unlink()
