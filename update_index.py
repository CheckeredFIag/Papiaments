"""
update_index.py
Genereert docs/data.js vanuit aruba_papiamento_db_structuur.csv.
index.html laadt dit bestand via <script src="data.js"></script>.
Gebruik: python update_index.py
"""

import csv
import json
from pathlib import Path
from datetime import date

CSV_FILE  = Path('aruba_papiamento_db_structuur.csv')
DATA_FILE = Path('docs/data.js')

# ============================================================
# CSV INLEZEN
# ============================================================

def load_csv() -> list[dict]:
    rows = []
    with open(CSV_FILE, encoding='utf-8') as f:
        first = f.readline()
        # Sla de lege eerste regel over (;;;;;;;;)
        if first.strip().replace(';', ''):
            f.seek(0)   # toch inhoud → begin opnieuw
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

# ============================================================
# DATA BOUWEN
# ============================================================

def build_words(rows: list[dict]) -> list[dict]:
    """Alle unieke woorden als woordkaartjes, met niveau."""
    seen = set()
    result = []
    for row in rows:
        if row['type'] != 'woord':
            continue
        key = row['woord']
        if key in seen:
            continue
        seen.add(key)
        result.append({
            'word':    row['woord'],
            'emoji':   row['emoji'],
            'meaning': row['nl'],
            'niveau':  row['niveau'],
        })
    return result


def build_speak_exercises(rows: list[dict]) -> list[dict]:
    """Zinnen als spreekoefeningen, met niveau."""
    seen = set()
    result = []
    for row in rows:
        if row['type'] != 'zin':
            continue
        key = row['woord']
        if key in seen:
            continue
        seen.add(key)
        result.append({
            'target': row['woord'],
            'niveau': row['niveau'],
        })
    return result


def build_read_exercises(rows: list[dict]) -> list[dict]:
    """
    Leesoefeningen: voor elk woord een meerkeuzevraag.
    Afleidopties worden gekozen uit andere woorden van hetzelfde niveau.
    """
    import random
    random.seed(42)  # reproduceerbaar

    woorden = [r for r in rows if r['type'] == 'woord']
    seen = set()
    result = []

    for row in woorden:
        key = row['woord']
        if key in seen:
            continue
        seen.add(key)

        # Kies twee afleidopties uit hetzelfde niveau (of all)
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
    """
    Schrijfoefeningen: voor elk woord letters + voorbeeldzin.
    Letters = unieke letters van het woord, aangevuld met willekeurige extra's.
    """
    import random
    random.seed(42)

    extra_pool = list('abcdefghijklmnoprstuw')
    woorden = [r for r in rows if r['type'] == 'woord']
    seen = set()
    result = []

    for row in woorden:
        key = row['woord']
        if key in seen:
            continue
        seen.add(key)

        # Basisletters uit het woord (zonder spaties)
        base_letters = list(key.replace(' ', ''))
        # Voeg 2-3 willekeurige extra letters toe als afleidopties
        extras = [c for c in extra_pool if c not in base_letters]
        extra_count = min(3, len(extras))
        distractors = random.sample(extras, extra_count)
        letters = base_letters + distractors
        random.shuffle(letters)

        result.append({
            'word':    key,
            'hint':    f"Tip: {row['nl']}.",
            'letters': letters,
            'sample':  f"Mi ta {key}.",   # eenvoudige voorbeeldzin
            'niveau':  row['niveau'],
        })
    return result


# ============================================================
# DATA.JS SCHRIJVEN
# ============================================================

def write_data_js(words, read_ex, write_ex, speak_ex):
    today = date.today().isoformat()
    content = f"""// data.js — automatisch gegenereerd door update_index.py op {today}
// Bron: aruba_papiamento_db_structuur.csv
// Pas dit bestand NIET handmatig aan; draai update_index.py opnieuw.

const words = {json.dumps(words, ensure_ascii=False, indent=2)};

const readExercises = {json.dumps(read_ex, ensure_ascii=False, indent=2)};

const writeExercises = {json.dumps(write_ex, ensure_ascii=False, indent=2)};

const speakExercises = {json.dumps(speak_ex, ensure_ascii=False, indent=2)};
"""
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_text(content, encoding='utf-8')
    print(f"✅ {DATA_FILE} geschreven ({DATA_FILE.stat().st_size} bytes)")


# ============================================================
# OVERZICHT
# ============================================================

def preview(words, read_ex, write_ex, speak_ex):
    print(f"\n📊 Samenvatting:")
    print(f"  🗂️  Woordkaartjes      : {len(words)}")
    print(f"  📖 Leesoefeningen     : {len(read_ex)}")
    print(f"  ✏️  Schrijfoefeningen  : {len(write_ex)}")
    print(f"  🎤 Spreekoefeningen   : {len(speak_ex)}")

    niveaus = {}
    for w in words:
        n = w.get('niveau', '?')
        niveaus[n] = niveaus.get(n, 0) + 1
    print(f"\n  Per niveau (woorden):")
    for n, count in sorted(niveaus.items()):
        print(f"    [{n:>5}]  {count} woorden")
    print()


# ============================================================
# HOOFDPROGRAMMA
# ============================================================

if __name__ == '__main__':
    print("=" * 55)
    print("  Papiaments Leeravontuur — update_index.py")
    print("=" * 55)

    rows = load_csv()
    print(f"\n📄 CSV geladen: {len(rows)} rijen")

    words      = build_words(rows)
    read_ex    = build_read_exercises(rows)
    write_ex   = build_write_exercises(rows)
    speak_ex   = build_speak_exercises(rows)

    preview(words, read_ex, write_ex, speak_ex)
    write_data_js(words, read_ex, write_ex, speak_ex)

    print("\n✅ Klaar! Push nu naar GitHub:")
    print("   git add docs/data.js update_index.py")
    print("   git commit -m 'Data extern via data.js, gegenereerd uit CSV'")
    print("   git push")
