"""
Fonetische vergelijking specifiek voor Papiaments.
Laadt klankmapping en varianten uit data/phonetic_map.json en data/phonetic_variants.json.
"""

import json
import re
from difflib import SequenceMatcher
from pathlib import Path

_DATA = Path(__file__).parent.parent / 'data'

def _load_phonetic_map() -> dict[str, str]:
    raw = json.loads((_DATA / 'phonetic_map.json').read_text(encoding='utf-8'))
    # accenten eerst, dan klanken — langere patronen voor kortere
    combined = {**raw['accents'], **raw['sounds']}
    return dict(sorted(combined.items(), key=lambda x: -len(x[0])))


def _load_variants() -> dict[str, list[str]]:
    return json.loads((_DATA / 'phonetic_variants.json').read_text(encoding='utf-8'))


PHONETIC_MAP      = _load_phonetic_map()
ACCEPTED_VARIANTS = _load_variants()

VARIANT_LOOKUP = {
    v.lower(): correct
    for correct, variants in ACCEPTED_VARIANTS.items()
    for v in variants
}


# ── Functies ───────────────────────────────────────────────────────────────

def phonetic_normalization(word: str) -> str:
    result = word.lower().strip()
    for pattern, replacement in PHONETIC_MAP.items():
        result = result.replace(pattern, replacement)
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
    tests = ['bon diá', 'agua', 'llama', 'mita', 'bon dia']
    print(f"{'Invoer':<20} {'Geaccepteerd':<14} {'Correct':<15} {'Taal'}")
    print('-' * 65)
    for t in tests:
        ok, correct = accept_variant(t)
        lang = language_distinction_detection(t)
        print(f"{t:<20} {'✅ ja' if ok else '❌ nee':<14} {correct:<15} {lang}")
