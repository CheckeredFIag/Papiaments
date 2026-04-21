"""
phonetic_listener.py
Fonetische vergelijking specifiek voor Papiaments.
Herkent Spaanstalige en alternatieve spellingen als correct.
"""

import re
from difflib import SequenceMatcher

# ============================================================
# FONETISCHE MAPPING
# ============================================================

PHONETIC_MAP = {
    'á': 'a', 'à': 'a', 'â': 'a',
    'é': 'e', 'è': 'e', 'ê': 'e',
    'í': 'i', 'ì': 'i', 'î': 'i',
    'ó': 'o', 'ò': 'o', 'ô': 'o',
    'ú': 'u', 'ù': 'u', 'û': 'u',
    'll': 'y',
    'gu': 'w',
    'qu': 'k',
    'ñ': 'ny',
    'v':  'b',
}

ACCEPTED_VARIANTS = {
    'bon dia': ['bon diá', 'bon dià', 'bon dia', 'buen dia', 'buenos dias'],
    'awa':     ['agua', 'aqua', 'agwa', 'awa'],
    'yama':    ['llama', 'jama', 'yama'],
    'mi ta':   ['mita', 'mi ta'],
    'danki':   ['danki', 'tranqui', 'dunkin'],
    'kachó':   ['kacho', 'kachó'],
    'cas':     ['kas', 'cas', 'casa'],
}

# Omgekeerde lookup: variant → correct woord
VARIANT_LOOKUP = {
    v.lower(): correct
    for correct, variants in ACCEPTED_VARIANTS.items()
    for v in variants
}

# ============================================================
# FUNCTIES
# ============================================================

def phonetic_normalization(word: str) -> str:
    """Normaliseert een woord naar zijn fonetische basisvorm."""
    result = word.lower().strip()
    for pattern, replacement in PHONETIC_MAP.items():
        result = result.replace(pattern, replacement)
    return result


def distance_score(word1: str, word2: str) -> float:
    """Geeft gelijkenis tussen 0.0 (totaal anders) en 1.0 (identiek)."""
    norm1 = phonetic_normalization(word1)
    norm2 = phonetic_normalization(word2)
    return round(SequenceMatcher(None, norm1, norm2).ratio(), 2)


def accept_variant(input_phrase: str, threshold: float = 0.75) -> tuple:
    """
    Controleert of een invoer een geaccepteerde variant is.
    Geeft (True, correct_woord) of (False, '') terug.
    """
    phrase = input_phrase.lower().strip()

    # Stap 1: directe lookup
    if phrase in VARIANT_LOOKUP:
        return True, VARIANT_LOOKUP[phrase]

    # Stap 2: genormaliseerde vergelijking
    norm_input = phonetic_normalization(phrase)
    for correct in ACCEPTED_VARIANTS:
        if norm_input == phonetic_normalization(correct):
            return True, correct

    # Stap 3: fuzzy matching als fallback
    for correct in ACCEPTED_VARIANTS:
        if distance_score(phrase, correct) >= threshold:
            return True, correct

    return False, ''


def language_distinction_detection(word: str) -> str:
    """Detecteert of een woord typisch Spaans, Papiaments of onbekend is."""
    spanish = [r'll', r'gu[ae]', r'ñ', r'ción$', r'mente$', r'qu[ie]']
    papiaments = [r'\bta\b', r'\bdi\b', r'^mi\b', r'ku\b', r'\bpa\b']
    w = word.lower()
    for pat in spanish:
        if re.search(pat, w):
            return 'Spaans (mogelijke fout)'
    for pat in papiaments:
        if re.search(pat, w):
            return 'Papiaments'
    return 'Onbekend'


# ============================================================
# TEST
# ============================================================

if __name__ == '__main__':
    tests = ['bon diá', 'agua', 'llama', 'mita', 'bon dia']
    print(f"{'Invoer':<20} {'Geaccepteerd':<14} {'Correct':<15} {'Taal'}")
    print('-' * 65)
    for t in tests:
        ok, correct = accept_variant(t)
        lang = language_distinction_detection(t)
        print(f"{t:<20} {'✅ ja' if ok else '❌ nee':<14} {correct:<15} {lang}")

    print("✅ Klaar! Push nu naar GitHub:")
    print("   git add phonetic_listener.py")
    print("   git commit -m 'Fonetische logica toegevoegd'")
    print("   git push")        