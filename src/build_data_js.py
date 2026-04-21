"""
Genereert docs/data.js vanuit data/words.csv.
"""

import csv
import json
import random
from datetime import date
from pathlib import Path

_ROOT      = Path(__file__).parent.parent
CSV_FILE   = _ROOT / 'data' / 'words.csv'
DATA_FILE  = _ROOT / 'docs' / 'data.js'


def load_csv() -> list[dict]:
    rows = []
    with open(CSV_FILE, encoding='utf-8') as f:
        first = f.readline()
        if first.strip().replace(';', ''):
            f.seek(0)
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            if not row.get('papiamento_aruba', '').strip():
                continue
            rows.append({
                'id':     row.get('id', '').strip(),
                'niveau': row.get('niveau', '').strip(),
                'type':   row.get('type', '').strip(),
                'emoji':  row.get('emoji', '').strip(),
                'woord':  row.get('papiamento_aruba', '').strip(),
                'nl':     row.get('nederlands', '').strip(),
            })
    return rows


def build_words(rows: list[dict]) -> list[dict]:
    seen, result = set(), []
    for row in rows:
        if row['type'] != 'woord' or row['woord'] in seen:
            continue
        seen.add(row['woord'])
        result.append({
            'word':    row['woord'],
            'emoji':   row['emoji'],
            'meaning': row['nl'],
            'niveau':  row['niveau'],
        })
    return result


def build_speak_exercises(rows: list[dict]) -> list[dict]:
    seen, result = set(), []
    for row in rows:
        if row['type'] != 'zin' or row['woord'] in seen:
            continue
        seen.add(row['woord'])
        result.append({'target': row['woord'], 'niveau': row['niveau']})
    return result


def build_read_exercises(rows: list[dict]) -> list[dict]:
    random.seed(42)
    woorden = [r for r in rows if r['type'] == 'woord']
    seen, result = set(), []
    for row in woorden:
        key = row['woord']
        if key in seen:
            continue
        seen.add(key)
        pool = [r['woord'] for r in woorden
                if r['woord'] != key and r['niveau'] == row['niveau']]
        if len(pool) < 2:
            pool = [r['woord'] for r in woorden if r['woord'] != key]
        distractors = random.sample(pool, min(2, len(pool)))
        options = distractors + [key]
        random.shuffle(options)
        result.append({
            'word':    key,
            'emoji':   row['emoji'],
            'hint':    f"Hint: {row['nl']}.",
            'options': options,
            'niveau':  row['niveau'],
        })
    return result


def build_write_exercises(rows: list[dict]) -> list[dict]:
    random.seed(42)
    extra_pool = list('abcdefghijklmnoprstuw')
    woorden = [r for r in rows if r['type'] == 'woord']
    seen, result = set(), []
    for row in woorden:
        key = row['woord']
        if key in seen:
            continue
        seen.add(key)
        base_letters = list(key.replace(' ', ''))
        extras = [c for c in extra_pool if c not in base_letters]
        distractors = random.sample(extras, min(3, len(extras)))
        letters = base_letters + distractors
        random.shuffle(letters)
        result.append({
            'word':    key,
            'hint':    f"Tip: {row['nl']}.",
            'letters': letters,
            'sample':  f"Mi ta {key}.",
            'niveau':  row['niveau'],
        })
    return result


def build_data_js():
    rows     = load_csv()
    words    = build_words(rows)
    read_ex  = build_read_exercises(rows)
    write_ex = build_write_exercises(rows)
    speak_ex = build_speak_exercises(rows)

    today   = date.today().isoformat()
    content = f"""// data.js — automatisch gegenereerd door src/build_data_js.py op {today}
// Bron: data/words.csv
// Pas dit bestand NIET handmatig aan; draai update_index.py opnieuw.

const words = {json.dumps(words, ensure_ascii=False, indent=2)};

const readExercises = {json.dumps(read_ex, ensure_ascii=False, indent=2)};

const writeExercises = {json.dumps(write_ex, ensure_ascii=False, indent=2)};

const speakExercises = {json.dumps(speak_ex, ensure_ascii=False, indent=2)};
"""
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_text(content, encoding='utf-8')
    print(f"  📄 {DATA_FILE} ({DATA_FILE.stat().st_size:,} bytes)")
    print(f"     {len(words)} woorden · {len(read_ex)} lees · "
          f"{len(write_ex)} schrijf · {len(speak_ex)} spreek")
