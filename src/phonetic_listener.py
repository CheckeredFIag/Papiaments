"""
Fonetische vergelijking specifiek voor Papiaments.
Laadt klankmapping en varianten uit data/phonetic_map.json en data/phonetic_variants.json.
Ondersteunt vaste regels, contextregels (c/g voor bepaalde klinkers) en uitzonderingen.
"""

import json
import re
from difflib import SequenceMatcher
from pathlib import Path

_DATA = Path(__file__).parent.parent / 'data'


def _load_phonetic_map() -> dict:
    return json.loads((_DATA / 'phonetic_map.json').read_text(encoding='utf-8'))


def _load_variants() -> dict[str, list[str]]:
    return json.loads((_DATA / 'phonetic_variants.json').read_text(encoding='utf-8'))


_MAP = _load_phonetic_map()

_ACCENTS    = _MAP['accents']
_FIXED      = dict(sorted(_MAP['fixed_sounds'].items(), key=lambda x: -len(x[0])))
_CTX        = _MAP['context_sounds']
_SINGLE     = _MAP['single_sounds']
_EXCEPTIONS = set(_MAP['exceptions']['no_change'])

ACCEPTED_VARIANTS = _load_variants()

VARIANT_LOOKUP = {
    v.lower(): correct
    for correct, variants in ACCEPTED_VARIANTS.items()
    for v in variants
}


# ── Context-regels (volgorde: specifiek → algemeen) ────────────────────────

def _apply_context_sounds(text: str) -> str:
    result = text

    # gu voor e/i → g  (bijv. guerra → gera, guia → gia)
    rule = _CTX.get('gu')
    if rule:
        chars = ''.join(rule['before'])
        result = re.sub(f'gu(?=[{chars}])', rule['output'], result)

    # qu voor e/i → k  (bijv. que → ke, quiero → kiero)
    rule = _CTX.get('qu')
    if rule:
        chars = ''.join(rule['before'])
        result = re.sub(f'qu(?=[{chars}])', rule['output'], result)

    # g voor e/i → h   (bijv. gente → hente)
    rule = _CTX.get('g_soft')
    if rule:
        chars = ''.join(rule['before'])
        result = re.sub(f'g(?=[{chars}])', rule['output'], result)

    # c voor e/i → s   (bijv. ciudad → siudad)
    rule = _CTX.get('c_soft')
    if rule:
        chars = ''.join(rule['before'])
        result = re.sub(f'c(?=[{chars}])', rule['output'], result)

    # c voor a/o/u → k (bijv. casa → kasa, coche → koche)
    rule = _CTX.get('c')
    if rule:
        chars = ''.join(rule['before'])
        result = re.sub(f'c(?=[{chars}])', rule['output'], result)

    # resterende c (bijv. aan het einde of voor medeklinker) → k
    result = re.sub(r'c(?![aeiou])', 'k', result)

    return result


# ── Hoofdfunctie ───────────────────────────────────────────────────────────

def phonetic_normalization(word: str) -> str:
    result = word.lower().strip()

    if result in _EXCEPTIONS:
        return result

    # 1. Accenten
    for pattern, replacement in _ACCENTS.items():
        result = result.replace(pattern, replacement)

    # 2. Vaste klanken (langste patronen eerst)
    for pattern, replacement in _FIXED.items():
        result = result.replace(pattern, replacement)

    # 3. Contextafhankelijke klanken
    result = _apply_context_sounds(result)

    # 4. Losse tekens (j→h, y→j, etc.)
    result = ''.join(_SINGLE.get(ch, ch) for ch in result)

    return result


def distance_score(word1: str, word2: str) -> float:
    norm1 = phonetic_normalization(word1)
    norm2 = phonetic_normalization(word2)
    return round(SequenceMatcher(None, norm1, norm2).ratio(), 2)


def accept_variant(input_phrase: str, threshold: float = 0.75) -> tuple[bool, str]:
    phrase = input_phrase.lower().strip()

    if phrase in VARIANT_LOOKUP:
        return True, VARIANT_LOOKUP[phrase]

    norm_input = phonetic_normalization(phrase)
    for correct in ACCEPTED_VARIANTS:
        if norm_input == phonetic_normalization(correct):
            return True, correct

    for correct in ACCEPTED_VARIANTS:
        if distance_score(phrase, correct) >= threshold:
            return True, correct

    return False, ''


def language_distinction_detection(word: str) -> str:
    spanish    = [r'll', r'gu[ae]', r'ñ', r'ción$', r'mente$', r'qu[ie]']
    papiaments = [r'\bta\b', r'\bdi\b', r'^mi\b', r'ku\b', r'\bpa\b']
    w = word.lower()
    for pat in spanish:
        if re.search(pat, w):
            return 'Spaans (mogelijke fout)'
    for pat in papiaments:
        if re.search(pat, w):
            return 'Papiaments'
    return 'Onbekend'


# ── Test ───────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    tests = [
        ('bon diá',   'bon dia'),
        ('agua',      'awa'),
        ('llama',     'yama'),
        ('mita',      'mi ta'),
        ('guerra',    None),
        ('gente',     None),
        ('ciudad',    None),
        ('casa',      None),
        ('que',       None),
        ('aruba',     None),
    ]
    print(f"{'Invoer':<20} {'Genorm.':<15} {'Accept?':<10} {'Correct':<15} {'Taal'}")
    print('-' * 75)
    for t, _ in tests:
        norm = phonetic_normalization(t)
        ok, correct = accept_variant(t)
        lang = language_distinction_detection(t)
        print(f"{t:<20} {norm:<15} {'✅' if ok else '❌':<10} {correct:<15} {lang}")
