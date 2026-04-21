"""
Genereert docs/phonetic.js vanuit data/phonetic_map.json en data/phonetic_variants.json.
De browser gebruikt dit bestand voor client-side fonetische vergelijking.
"""

import json
from datetime import date
from pathlib import Path

_ROOT         = Path(__file__).parent.parent
DATA_DIR      = _ROOT / 'data'
PHONETIC_FILE = _ROOT / 'docs' / 'phonetic.js'


def build_phonetic_js():
    phonetic_map = json.loads((DATA_DIR / 'phonetic_map.json').read_text(encoding='utf-8'))
    variants     = json.loads((DATA_DIR / 'phonetic_variants.json').read_text(encoding='utf-8'))

    # Vlak map uitklappen: accenten + klanken, gesorteerd op patroonlengte (lang eerst)
    flat_map = {**phonetic_map['accents'], **phonetic_map['sounds']}
    flat_map = dict(sorted(flat_map.items(), key=lambda x: -len(x[0])))

    # Omgekeerde lookup: variant → correct woord
    variant_lookup: dict[str, str] = {}
    for correct, vs in variants.items():
        for v in vs:
            variant_lookup[v.lower()] = correct

    today   = date.today().isoformat()
    content = f"""// phonetic.js — automatisch gegenereerd door src/build_phonetic_js.py op {today}
// Bron: data/phonetic_map.json + data/phonetic_variants.json
// Pas dit bestand NIET handmatig aan; draai update_index.py opnieuw.

const PHONETIC_MAP = {json.dumps(flat_map, ensure_ascii=False, indent=2)};

const ACCEPTED_VARIANTS = {json.dumps(variants, ensure_ascii=False, indent=2)};

const VARIANT_LOOKUP = {json.dumps(variant_lookup, ensure_ascii=False, indent=2)};

function phoneticNormalize(word) {{
  let result = word.toLowerCase().trim();
  for (const [pattern, replacement] of Object.entries(PHONETIC_MAP)) {{
    result = result.split(pattern).join(replacement);
  }}
  return result;
}}

function acceptVariant(input, threshold = 0.75) {{
  const phrase = input.toLowerCase().trim();
  if (VARIANT_LOOKUP[phrase]) return {{ ok: true, correct: VARIANT_LOOKUP[phrase] }};
  const norm = phoneticNormalize(phrase);
  for (const correct of Object.keys(ACCEPTED_VARIANTS)) {{
    if (norm === phoneticNormalize(correct)) return {{ ok: true, correct }};
  }}
  return {{ ok: false, correct: '' }};
}}
"""
    PHONETIC_FILE.parent.mkdir(parents=True, exist_ok=True)
    PHONETIC_FILE.write_text(content, encoding='utf-8')
    print(f"  📄 {PHONETIC_FILE} ({PHONETIC_FILE.stat().st_size:,} bytes)")
