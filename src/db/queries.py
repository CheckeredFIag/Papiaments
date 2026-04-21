import sqlite3
from pathlib import Path
from .models import User, Score, Session
from .schema import DB_PATH


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ── Users ──────────────────────────────────────────────────────────────────

def create_user(nickname: str, avatar: str = '🧒') -> User:
    with get_conn() as conn:
        conn.execute(
            'INSERT OR IGNORE INTO users (nickname, avatar) VALUES (?, ?)',
            (nickname, avatar),
        )
    return get_user(nickname)


def get_user(nickname: str) -> User | None:
    with get_conn() as conn:
        row = conn.execute(
            'SELECT * FROM users WHERE nickname = ?', (nickname,)
        ).fetchone()
    return User(**dict(row)) if row else None


def touch_user(user_id: int):
    with get_conn() as conn:
        conn.execute(
            "UPDATE users SET last_seen = datetime('now') WHERE id = ?",
            (user_id,),
        )


# ── Scores ─────────────────────────────────────────────────────────────────

def upsert_score(score: Score):
    with get_conn() as conn:
        conn.execute('''
            INSERT INTO scores (user_id, skill, niveau, stars, correct, attempts)
            VALUES (:user_id, :skill, :niveau, :stars, :correct, :attempts)
            ON CONFLICT(user_id, skill, niveau) DO UPDATE SET
                stars      = stars    + excluded.stars,
                correct    = correct  + excluded.correct,
                attempts   = attempts + excluded.attempts,
                updated_at = datetime('now')
        ''', score.__dict__)


def get_scores(user_id: int) -> list[Score]:
    with get_conn() as conn:
        rows = conn.execute(
            'SELECT * FROM scores WHERE user_id = ? ORDER BY skill, niveau',
            (user_id,),
        ).fetchall()
    return [Score(**dict(r)) for r in rows]


# ── Sessies ────────────────────────────────────────────────────────────────

def log_session(session: Session):
    with get_conn() as conn:
        conn.execute('''
            INSERT INTO sessions (user_id, word, skill, result, heard_as)
            VALUES (:user_id, :word, :skill, :result, :heard_as)
        ''', session.__dict__)
        if session.result == 'fout':
            conn.execute('''
                INSERT INTO weak_words (user_id, word, miss_count, last_missed)
                VALUES (?, ?, 1, datetime('now'))
                ON CONFLICT(user_id, word) DO UPDATE SET
                    miss_count  = miss_count + 1,
                    last_missed = datetime('now')
            ''', (session.user_id, session.word))


def get_weak_words(user_id: int, limit: int = 5) -> list[str]:
    with get_conn() as conn:
        rows = conn.execute('''
            SELECT word FROM weak_words
            WHERE user_id = ?
            ORDER BY miss_count DESC, last_missed DESC
            LIMIT ?
        ''', (user_id, limit)).fetchall()
    return [r['word'] for r in rows]
