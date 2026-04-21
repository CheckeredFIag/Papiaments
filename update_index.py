"""
update_index.py
Beheert de woordenlijsten in docs/index.html vanuit Python.
Gebruik: python update_index.py
"""

import re
import json
from pathlib import Path
from datetime import date

HTML_FILE = Path('docs/index.html')

# ============================================================
# FONETISCHE VARIANTEN
# ============================================================

ACCEPTED_VARIANTS = {
    'bon dia':   ['bon diá', 'bon dià', 'bon dia', 'buen dia', 'buenos dias'],
    'awa':       ['agua', 'agwa', 'awa'],
    'yama':      ['llama', 'jama', 'yama'],
    'mi ta':     ['mita', 'mi ta'],
    'danki':     ['danki', 'gracias'],
    'kachó':     ['kacho', 'kachó', 'perro'],
    'cas':       ['kas', 'cas', 'casa'],
}

# ============================================================
# LEES & SCHRIJF HTML
# ============================================================

def read_html() -> str:
    return HTML_FILE.read_text(encoding='utf-8')

def write_html(text: str):
    HTML_FILE.write_text(text, encoding='utf-8')
    print(f"✅ {HTML_FILE} opgeslagen.")

# ============================================================
# DATUMSTEMPEL BIJWERKEN
# ============================================================

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
    """Extraheer een JS array uit de HTML, ook met single quotes."""
    pattern = rf'const {var_name} = (\[.*?\]);'
    match = re.search(pattern, html, re.DOTALL)
    if not match:
        raise ValueError(f"Variabele '{var_name}' niet gevonden in HTML.")

    raw = match.group(1)

    # Converteer JS naar geldige JSON
    raw = re.sub(r"'([^']*)'", r'"\1"', raw)   # single → double quotes
    raw = re.sub(r',\s*([}\]])', r'\1', raw)     # trailing comma's weg
    # Voeg dubbele quotes toe rond property namen indien nodig
    raw = re.sub(r'([{,]\s*)(\w+)(\s*:)','\\1"\\2"\\3', raw)

    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"❌ Parse fout in '{var_name}': {e}")
        print(f"   Ruwe tekst (eerste 200 tekens): {raw[:200]}")
        raise

def replace_js_array(html: str, var_name: str, new_data: list) -> str:
    """Vervang een JS array in de HTML met nieuwe data."""
    # Bouw de JS array op met single quotes (zoals origineel)
    items = []
    for item in new_data:
        pairs = []
        for k, v in item.items():
            if isinstance(v, list):
                inner = ','.join(f"'{x}'" for x in v)
                pairs.append(f"{k}:[{inner}]")
            else:
                pairs.append(f"{k}:'{v}'")
        items.append('{' + ','.join(pairs) + '}')
    new_array = '[' + ','.join(items) + ']'

    pattern = rf'(const {var_name} = )(\[.*?\]);'
    result = re.sub(pattern, rf'\g<1>{new_array};', html, flags=re.DOTALL)
    return result

# ============================================================
# WOORDEN BEHEREN
# ============================================================

def list_all_words():
    """Toon alle huidige woorden in de app."""
    html = read_html()
    words = extract_js_array(html, 'words')
    print("\n📋 Huidige woordkaartjes:")
    for i, w in enumerate(words, 1):
        print(f"  {i}. {w['emoji']} {w['word']} = {w['meaning']}")
    print()

def add_word_card(word: str, emoji: str, meaning: str):
    """Voeg een woord toe aan de woordkaartjes."""
    html = read_html()
    words = extract_js_array(html, 'words')

    if any(w['word'] == word for w in words):
        print(f"⚠️  '{word}' staat al in de woordenlijst.")
        return

    words.append({'word': word, 'emoji': emoji, 'meaning': meaning})
    html = replace_js_array(html, 'words', words)
    html = update_date_stamp(html)
    write_html(html)
    print(f"✅ Woord '{word}' ({emoji} = {meaning}) toegevoegd.")

def add_read_exercise(word: str, emoji: str, hint: str, options: list):
    """Voeg een leesoefening toe."""
    if word not in options:
        options.append(word)

    html = read_html()
    exercises = extract_js_array(html, 'readExercises')

    if any(e['word'] == word for e in exercises):
        print(f"⚠️  Leesoefening '{word}' bestaat al.")
        return

    exercises.append({'word': word, 'emoji': emoji, 'hint': hint, 'options': options[:3]})
    html = replace_js_array(html, 'readExercises', exercises)
    html = update_date_stamp(html)
    write_html(html)
    print(f"✅ Leesoefening '{word}' toegevoegd.")

def add_speak_exercise(target: str):
    """Voeg een spreekoefening toe."""
    html = read_html()
    exercises = extract_js_array(html, 'speakExercises')

    if any(e['target'] == target for e in exercises):
        print(f"⚠️  Spreekoefening '{target}' bestaat al.")
        return

    exercises.append({'target': target})
    html = replace_js_array(html, 'speakExercises', exercises)
    html = update_date_stamp(html)
    write_html(html)
    print(f"✅ Spreekoefening '{target}' toegevoegd.")

def add_write_exercise(word: str, hint: str, letters: list, sample: str):
    """Voeg een schrijfoefening toe."""
    html = read_html()
    exercises = extract_js_array(html, 'writeExercises')

    if any(e['word'] == word for e in exercises):
        print(f"⚠️  Schrijfoefening '{word}' bestaat al.")
        return

    exercises.append({'word': word, 'hint': hint, 'letters': letters, 'sample': sample})
    html = replace_js_array(html, 'writeExercises', exercises)
    html = update_date_stamp(html)
    write_html(html)
    print(f"✅ Schrijfoefening '{word}' toegevoegd.")

# ============================================================
# VOORBEELD GEBRUIK — pas dit gedeelte aan naar wens
# ============================================================

if __name__ == '__main__':
    # Toon wat er nu in de app staat
    list_all_words()

    # --- Voeg hier nieuwe woorden toe ---
    add_word_card('laman', '🌊', 'zee')
    add_word_card('palo',  '🌳', 'boom')

    # --- Voeg leesoefeningen toe ---
    add_read_exercise(
        word='laman',
        emoji='🌊',
        hint='Hint: hier zwemmen de vissen in.',
        options=['laman', 'solo', 'cas']
    )

    # --- Voeg spreekoefeningen toe ---
    add_speak_exercise('bon nochi')
    add_speak_exercise('mi ta bai school')

    # --- Voeg schrijfoefeningen toe ---
    add_write_exercise(
        word='laman',
        hint='Tip: dit is de zee.',
        letters=['l', 'a', 'm', 'a', 'n', 'p'],
        sample='E laman ta blou.'
    )

    # Toon de bijgewerkte lijst
    list_all_words()

    print("✅ Klaar! Push nu naar GitHub:")
    print("   git add docs/index.html")
    print("   git commit -m 'Nieuwe woorden toegevoegd'")
    print("   git push")