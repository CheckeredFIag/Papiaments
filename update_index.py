"""
update_index.py
Beheert de woordenlijsten in docs/index.html vanuit Python.
Laadt woorden en emoji's uit aruba_papiamento_db_structuur.csv
Gebruik: python update_index.py
"""

import re
import csv
import json
from pathlib import Path
from datetime import date

HTML_FILE = Path('docs/index.html')
CSV_FILE  = Path('aruba_papiamento_db_structuur.csv')

# ============================================================
# CSV INLEZEN
# ============================================================

def load_csv() -> list[dict]:
    rows = []
    with open(CSV_FILE, encoding='utf-8') as f:
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

def get_words_from_csv(niveau: str = None) -> list[dict]:
    rows = load_csv()
    result = []
    seen = set()
    for row in rows:
        if row['type'] != 'woord':
            continue
        if niveau and row['niveau'] != niveau:
            continue
        key = row['woord']
        if key in seen:
            continue
        seen.add(key)
        result.append(row)
    return result

def get_sentences_from_csv() -> list[dict]:
    return [r for r in load_csv() if r['type'] == 'zin']

# ============================================================
# LEES & SCHRIJF HTML
# ============================================================

def read_html() -> str:
    return HTML_FILE.read_text(encoding='utf-8')

def write_html(text: str):
    HTML_FILE.write_text(text, encoding='utf-8')
    print(f"✅ {HTML_FILE} opgeslagen.")

def update_date_stamp(html: str) -> str:
    today = date.today().isoformat()
    return re.sub(
        r'<!-- Updated on \d{4}-\d{2}-\d{2} -->',
        f'<!-- Updated on {today} -->',
        html
    )

# ============================================================
# JS ARRAY LEZEN EN SCHRIJVEN
# ============================================================

def extract_js_array(html: str, var_name: str) -> list:
    """Extraheer een JS array uit de HTML, ook met single quotes en emoji's."""
    pattern = rf'const {var_name} = (\[.*?\]);'
    match = re.search(pattern, html, re.DOTALL)
    if not match:
        raise ValueError(f"Variabele '{var_name}' niet gevonden in HTML.")

    raw = match.group(1)

    # Stap 1: escaped single quotes tijdelijk vervangen
    raw = raw.replace("\\'", "##SQUOTE##")

    # Stap 2: single quotes → double quotes
    raw = re.sub(r"'([^']*)'", r'"\1"', raw)

    # Stap 3: tijdelijke placeholder terugzetten als escaped quote in JSON
    raw = raw.replace("##SQUOTE##", "'")

    # Stap 4: trailing comma's verwijderen (JS staat dit toe, JSON niet)
    raw = re.sub(r',\s*\]', ']', raw)
    raw = re.sub(r',\s*\}', '}', raw)

    # Stap 5: ongequote JS keys → gequote JSON keys (bv. word: → "word":)
    raw = re.sub(r'(?<=[{,])\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'"\1":', raw)

    # Stap 6: dubbele double quotes rechtzetten (als een key al quotes had)
    raw = re.sub(r'""([^"]+)""', r'"\1"', raw)

    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"❌ Parse fout in '{var_name}': {e}")
        # Toon de exacte plek van de fout
        lines = raw.splitlines()
        for i, line in enumerate(lines, 1):
            print(f"  {i:>3}: {line}")
        raise

def replace_js_array(html: str, var_name: str, new_data: list) -> str:
    items = []
    for item in new_data:
        pairs = []
        for k, v in item.items():
            if isinstance(v, list):
                inner = ','.join(f"'{x}'" for x in v)
                pairs.append(f"{k}:[{inner}]")
            else:
                val = str(v).replace("'", "\\'")
                pairs.append(f"{k}:'{val}'")
        items.append('{' + ','.join(pairs) + '}')
    new_array = '[' + ','.join(items) + ']'
    pattern = rf'(const {var_name} = )(\[.*?\]);'
    return re.sub(pattern, rf'\g<1>{new_array};', html, flags=re.DOTALL)

# ============================================================
# SYNCHRONISATIE — met niveau veld
# ============================================================

def sync_words_from_csv():
    """Synchroniseer ALLE woorden uit CSV, met niveau erbij."""
    html = read_html()
    current = extract_js_array(html, 'words')
    bestaande = {w['word'] for w in current}

    nieuw = 0
    for row in get_words_from_csv():
        if row['woord'] in bestaande:
            continue
        current.append({
            'word':    row['woord'],
            'emoji':   row['emoji'],
            'meaning': row['nl'],
            'niveau':  row['niveau'],   # ← nieuw: niveau meeschrijven
        })
        bestaande.add(row['woord'])
        print(f"  ➕ [{row['niveau']:>5}] {row['emoji']}  {row['woord']} = {row['nl']}")
        nieuw += 1

    if nieuw == 0:
        print("✅ Alle woorden staan al in de app.")
        return

    html = replace_js_array(html, 'words', current)
    html = update_date_stamp(html)
    write_html(html)
    print(f"\n✅ {nieuw} nieuwe woorden toegevoegd.")

def sync_speak_from_csv():
    """Voeg zinnen toe als spreekoefeningen, met niveau."""
    html = read_html()
    current = extract_js_array(html, 'speakExercises')
    bestaande = {e['target'] for e in current}

    nieuw = 0
    for row in get_sentences_from_csv():
        if row['woord'] in bestaande:
            continue
        current.append({
            'target': row['woord'],
            'niveau': row['niveau'],   # ← nieuw: niveau meeschrijven
        })
        bestaande.add(row['woord'])
        print(f"  ➕ 🎤  [{row['niveau']}]  {row['woord']}")
        nieuw += 1

    if nieuw == 0:
        print("✅ Alle zinnen staan al als spreekoefening.")
        return

    html = replace_js_array(html, 'speakExercises', current)
    html = update_date_stamp(html)
    write_html(html)
    print(f"\n✅ {nieuw} nieuwe spreekoefeningen toegevoegd.")

# ============================================================
# HANDMATIG TOEVOEGEN
# ============================================================

def add_word_card(word: str, emoji: str, meaning: str, niveau: str = 'all'):
    html = read_html()
    words = extract_js_array(html, 'words')
    if any(w['word'] == word for w in words):
        print(f"⚠️  '{word}' staat al in de woordenlijst.")
        return
    words.append({'word': word, 'emoji': emoji, 'meaning': meaning, 'niveau': niveau})
    html = replace_js_array(html, 'words', words)
    html = update_date_stamp(html)
    write_html(html)
    print(f"✅ Woord '{word}' ({emoji} = {meaning}) toegevoegd.")

def add_read_exercise(word: str, emoji: str, hint: str, options: list, niveau: str = 'all'):
    if word not in options:
        options.append(word)
    html = read_html()
    exercises = extract_js_array(html, 'readExercises')
    if any(e['word'] == word for e in exercises):
        print(f"⚠️  Leesoefening '{word}' bestaat al.")
        return
    exercises.append({'word': word, 'emoji': emoji, 'hint': hint,
                      'options': options[:3], 'niveau': niveau})
    html = replace_js_array(html, 'readExercises', exercises)
    html = update_date_stamp(html)
    write_html(html)
    print(f"✅ Leesoefening '{word}' toegevoegd.")

def add_speak_exercise(target: str, niveau: str = 'all'):
    html = read_html()
    exercises = extract_js_array(html, 'speakExercises')
    if any(e['target'] == target for e in exercises):
        print(f"⚠️  Spreekoefening '{target}' bestaat al.")
        return
    exercises.append({'target': target, 'niveau': niveau})
    html = replace_js_array(html, 'speakExercises', exercises)
    html = update_date_stamp(html)
    write_html(html)
    print(f"✅ Spreekoefening '{target}' toegevoegd.")

def add_write_exercise(word: str, hint: str, letters: list, sample: str, niveau: str = 'all'):
    html = read_html()
    exercises = extract_js_array(html, 'writeExercises')
    if any(e['word'] == word for e in exercises):
        print(f"⚠️  Schrijfoefening '{word}' bestaat al.")
        return
    exercises.append({'word': word, 'hint': hint, 'letters': letters,
                      'sample': sample, 'niveau': niveau})
    html = replace_js_array(html, 'writeExercises', exercises)
    html = update_date_stamp(html)
    write_html(html)
    print(f"✅ Schrijfoefening '{word}' toegevoegd.")

# ============================================================
# OVERZICHT
# ============================================================

def list_all_words():
    html = read_html()
    words = extract_js_array(html, 'words')
    print(f"\n📋 Huidige woordkaartjes in app ({len(words)} stuks):")
    for i, w in enumerate(words, 1):
        niveau = w.get('niveau', '?')
        print(f"  {i:>2}. [{niveau:>5}] {w['emoji']}  {w['word']:<20} = {w['meaning']}")
    print()

def preview_csv():
    rows = load_csv()
    print(f"\n📄 CSV bevat {len(rows)} rijen:\n")
    for row in rows:
        print(f"  [{row['niveau']:>5}] {row['type']:<5}  {row['emoji']}  "
              f"{row['woord']:<25} = {row['nl']}")
    print()

# ============================================================
# HOOFDPROGRAMMA
# ============================================================

if __name__ == '__main__':
    print("=" * 55)
    print("  Papiaments Leeravontuur — update_index.py")
    print("=" * 55)

    preview_csv()
    list_all_words()

    print("📥 Alle woorden synchroniseren vanuit CSV...")
    sync_words_from_csv()

    print("\n🎤 Zinnen toevoegen als spreekoefeningen...")
    sync_speak_from_csv()

    list_all_words()

    print("✅ Klaar! Push nu naar GitHub:")
    print("   git add update_index.py")
    print("   git commit -m 'Niveau-filter toegevoegd'")
    print("   git push")