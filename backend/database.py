import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / 'db' / 'papiaments.db'


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    return conn


def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with get_conn() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                name       TEXT    NOT NULL UNIQUE,
                avatar     TEXT    DEFAULT '🧒',
                niveau     TEXT    DEFAULT '4-6',
                created_at TEXT    DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS sessions (
                id             INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id        INTEGER NOT NULL REFERENCES users(id),
                started_at     TEXT    DEFAULT (datetime('now')),
                ended_at       TEXT,
                exercises_done INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS word_scores (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id    INTEGER NOT NULL REFERENCES users(id),
                session_id INTEGER REFERENCES sessions(id),
                word       TEXT    NOT NULL,
                skill      TEXT    NOT NULL CHECK(skill IN ('lezen','schrijven','spreken')),
                correct    INTEGER NOT NULL CHECK(correct IN (0,1)),
                niveau     TEXT    NOT NULL,
                last_seen  TEXT    DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS skill_totals (
                user_id       INTEGER NOT NULL REFERENCES users(id),
                skill         TEXT    NOT NULL CHECK(skill IN ('lezen','schrijven','spreken')),
                niveau        TEXT    NOT NULL,
                correct_total INTEGER DEFAULT 0,
                wrong_total   INTEGER DEFAULT 0,
                streak        INTEGER DEFAULT 0,
                PRIMARY KEY (user_id, skill, niveau)
            );
        """)
