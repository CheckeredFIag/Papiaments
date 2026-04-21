"""
Portaal-specifieke queries: rijkere data voor het ouder/leerkracht-dashboard.
Laadt emoji + betekenis uit data/words.csv zodat zwakke/sterke woorden
direct leesbaar zijn zonder extra join.
"""

import csv
from pathlib import Path
from .database import get_conn

_WORDS_CSV = Path(__file__).parent.parent / 'data' / 'words.csv'


def _load_word_lookup() -> dict:
    lookup: dict = {}
    try:
        with open(_WORDS_CSV, encoding='utf-8') as f:
            first = f.readline()
            if first.strip().replace(';', ''):
                f.seek(0)
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                word = row.get('papiamento_aruba', '').strip()
                if word:
                    lookup[word] = {
                        'emoji':   row.get('emoji', '📝').strip() or '📝',
                        'meaning': row.get('nederlands', '').strip(),
                    }
    except Exception:
        pass
    return lookup


WORD_LOOKUP = _load_word_lookup()


def _skill_totals(conn, user_id: int) -> dict:
    rows = conn.execute('''
        SELECT skill,
               SUM(correct_total) AS correct,
               SUM(wrong_total)   AS wrong
        FROM skill_totals WHERE user_id = ?
        GROUP BY skill
    ''', (user_id,)).fetchall()
    return {r['skill']: (r['correct'] or 0, r['wrong'] or 0) for r in rows}


def get_portaal_users() -> list[dict]:
    with get_conn() as conn:
        users = conn.execute('SELECT * FROM users ORDER BY name').fetchall()
        result = []
        for u in users:
            uid = u['id']
            sm = _skill_totals(conn, uid)

            def cv(skill):
                c, w = sm.get(skill, (0, 0))
                return c, c + w

            read_c,  read_t  = cv('lezen')
            write_c, write_t = cv('schrijven')
            speak_c, speak_t = cv('spreken')

            last = conn.execute(
                'SELECT MAX(last_seen) AS ts FROM word_scores WHERE user_id = ?',
                (uid,),
            ).fetchone()

            result.append({
                'id':    uid,
                'name':  u['name'],
                'avatar': u['avatar'],
                'niveau': u['niveau'],
                'stars':  read_c + write_c + speak_c,
                'last_active':   last['ts'] if last else None,
                'read_correct':  read_c,  'read_total':  read_t,
                'write_correct': write_c, 'write_total': write_t,
                'speak_correct': speak_c, 'speak_total': speak_t,
            })
        return result


def get_portaal_dashboard(user_id: int) -> dict | None:
    with get_conn() as conn:
        user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        if not user:
            return None

        sm = _skill_totals(conn, user_id)

        def sv(skill):
            c, w = sm.get(skill, (0, 0))
            return c, w, c + w

        read_c,  read_w,  read_t  = sv('lezen')
        write_c, write_w, write_t = sv('schrijven')
        speak_c, speak_w, speak_t = sv('spreken')

        last = conn.execute(
            'SELECT MAX(last_seen) AS ts FROM word_scores WHERE user_id = ?',
            (user_id,),
        ).fetchone()

        np_rows = conn.execute('''
            SELECT niveau,
                   SUM(correct_total)              AS correct,
                   SUM(correct_total + wrong_total) AS total
            FROM skill_totals WHERE user_id = ?
            GROUP BY niveau
        ''', (user_id,)).fetchall()
        niveau_progress = {
            r['niveau']: {'correct': r['correct'] or 0, 'total': r['total'] or 0}
            for r in np_rows
        }

        weak_rows = conn.execute('''
            SELECT word, COUNT(*) AS wrong_total
            FROM word_scores WHERE user_id = ? AND correct = 0
            GROUP BY word ORDER BY wrong_total DESC LIMIT 8
        ''', (user_id,)).fetchall()
        weaknesses = [
            {
                'word':        r['word'],
                'emoji':       WORD_LOOKUP.get(r['word'], {}).get('emoji', '📝'),
                'meaning':     WORD_LOOKUP.get(r['word'], {}).get('meaning', ''),
                'wrong_total': r['wrong_total'],
            }
            for r in weak_rows
        ]

        strong_rows = conn.execute('''
            SELECT word,
                   SUM(CASE WHEN correct = 1 THEN 1 ELSE 0 END) AS correct_total,
                   SUM(CASE WHEN correct = 0 THEN 1 ELSE 0 END) AS wrong_total
            FROM word_scores WHERE user_id = ?
            GROUP BY word
            HAVING (correct_total + wrong_total) >= 3
               AND (correct_total * 1.0 / (correct_total + wrong_total)) >= 0.75
            ORDER BY (correct_total * 1.0 / (correct_total + wrong_total)) DESC
            LIMIT 8
        ''', (user_id,)).fetchall()
        strengths = [
            {
                'word':          r['word'],
                'emoji':         WORD_LOOKUP.get(r['word'], {}).get('emoji', '📝'),
                'meaning':       WORD_LOOKUP.get(r['word'], {}).get('meaning', ''),
                'correct_total': r['correct_total'],
                'wrong_total':   r['wrong_total'],
            }
            for r in strong_rows
        ]

        return {
            'id':       user['id'],
            'name':     user['name'],
            'avatar':   user['avatar'],
            'niveau':   user['niveau'],
            'created_at': user['created_at'],
            'stars':    read_c + write_c + speak_c,
            'last_active': last['ts'] if last else None,
            'read_correct':  read_c,  'read_total':  read_t,  'read_wrong':  read_w,
            'write_correct': write_c, 'write_total': write_t, 'write_wrong': write_w,
            'speak_correct': speak_c, 'speak_total': speak_t, 'speak_wrong': speak_w,
            'weaknesses':      weaknesses,
            'strengths':       strengths,
            'niveau_progress': niveau_progress,
        }
