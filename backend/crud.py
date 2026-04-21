from .database import get_conn
from .models import UserOut, SkillTotalOut, WeakWordOut, NiveauProgressOut, DashboardOut


# ── Users ──────────────────────────────────────────────────────────────────

def create_user(name: str, avatar: str = '🧒', niveau: str = '4-6') -> UserOut | None:
    with get_conn() as conn:
        conn.execute(
            'INSERT OR IGNORE INTO users (name, avatar, niveau) VALUES (?, ?, ?)',
            (name, avatar, niveau),
        )
    return get_user_by_name(name)


def get_users() -> list[UserOut]:
    with get_conn() as conn:
        rows = conn.execute('SELECT * FROM users ORDER BY name').fetchall()
    return [UserOut(**dict(r)) for r in rows]


def get_user(user_id: int) -> UserOut | None:
    with get_conn() as conn:
        row = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    return UserOut(**dict(row)) if row else None


def get_user_by_name(name: str) -> UserOut | None:
    with get_conn() as conn:
        row = conn.execute('SELECT * FROM users WHERE name = ?', (name,)).fetchone()
    return UserOut(**dict(row)) if row else None


# ── Scores ─────────────────────────────────────────────────────────────────

def post_score(user_id: int, word: str, skill: str, correct: bool,
               niveau: str, session_id: int | None = None):
    c = 1 if correct else 0
    with get_conn() as conn:
        conn.execute(
            'INSERT INTO word_scores (user_id, session_id, word, skill, correct, niveau) '
            'VALUES (?, ?, ?, ?, ?, ?)',
            (user_id, session_id, word, skill, c, niveau),
        )
        conn.execute('''
            INSERT INTO skill_totals (user_id, skill, niveau, correct_total, wrong_total, streak)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id, skill, niveau) DO UPDATE SET
                correct_total = correct_total + excluded.correct_total,
                wrong_total   = wrong_total   + excluded.wrong_total,
                streak        = CASE
                    WHEN excluded.correct_total > 0 THEN streak + 1
                    ELSE 0
                END
        ''', (user_id, skill, niveau, c, 1 - c, c))


# ── Sessies ────────────────────────────────────────────────────────────────

def start_session(user_id: int) -> int:
    with get_conn() as conn:
        cur = conn.execute('INSERT INTO sessions (user_id) VALUES (?)', (user_id,))
        return cur.lastrowid


def end_session(session_id: int, exercises_done: int):
    with get_conn() as conn:
        conn.execute(
            "UPDATE sessions SET ended_at = datetime('now'), exercises_done = ? WHERE id = ?",
            (exercises_done, session_id),
        )


# ── Dashboard ──────────────────────────────────────────────────────────────

def get_weaknesses(user_id: int, limit: int = 10) -> list[WeakWordOut]:
    with get_conn() as conn:
        rows = conn.execute('''
            SELECT word, skill, COUNT(*) as wrong_total, niveau
            FROM word_scores WHERE user_id = ? AND correct = 0
            GROUP BY word, skill
            ORDER BY wrong_total DESC
            LIMIT ?
        ''', (user_id, limit)).fetchall()
    return [WeakWordOut(**dict(r)) for r in rows]


def get_dashboard(user_id: int) -> DashboardOut | None:
    user = get_user(user_id)
    if not user:
        return None

    with get_conn() as conn:
        st_rows = conn.execute('''
            SELECT skill, niveau, correct_total, wrong_total, streak
            FROM skill_totals WHERE user_id = ?
            ORDER BY skill, niveau
        ''', (user_id,)).fetchall()

        ww_rows = conn.execute('''
            SELECT word, skill, COUNT(*) as wrong_total, niveau
            FROM word_scores WHERE user_id = ? AND correct = 0
            GROUP BY word, skill
            ORDER BY wrong_total DESC
            LIMIT 10
        ''', (user_id,)).fetchall()

        np_rows = conn.execute('''
            SELECT niveau,
                   SUM(correct_total) as correct,
                   SUM(correct_total + wrong_total) as total
            FROM skill_totals WHERE user_id = ?
            GROUP BY niveau
        ''', (user_id,)).fetchall()

        totals = conn.execute('''
            SELECT SUM(correct_total) as tc, SUM(correct_total + wrong_total) as ta
            FROM skill_totals WHERE user_id = ?
        ''', (user_id,)).fetchone()

    skill_totals = [
        SkillTotalOut(
            skill=r['skill'], niveau=r['niveau'],
            correct_total=r['correct_total'], wrong_total=r['wrong_total'],
            streak=r['streak'],
            ratio=round(r['correct_total'] / max(r['correct_total'] + r['wrong_total'], 1), 2),
        ) for r in st_rows
    ]

    weak_words = [WeakWordOut(**dict(r)) for r in ww_rows]

    niveau_progress = [
        NiveauProgressOut(
            niveau=r['niveau'],
            correct=r['correct'] or 0,
            total=r['total'] or 0,
            ratio=round((r['correct'] or 0) / max(r['total'] or 1, 1), 2),
        ) for r in np_rows
    ]

    return DashboardOut(
        user=user,
        skill_totals=skill_totals,
        weak_words=weak_words,
        niveau_progress=niveau_progress,
        total_correct=totals['tc'] or 0,
        total_attempts=totals['ta'] or 0,
    )
