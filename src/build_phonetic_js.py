"""
Genereert docs/phonetic.js vanuit data/phonetic_map.json en data/phonetic_variants.json.
Ondersteunt vaste regels, contextregels en uitzonderingen.
"""

import json
from datetime import date
from pathlib import Path

_ROOT         = Path(__file__).parent.parent
DATA_DIR      = _ROOT / 'data'
PHONETIC_FILE = _ROOT / 'docs' / 'phonetic.js'


def _ctx_replace_lines(ctx: dict) -> str:
    """Genereer JS replace-statements voor contextafhankelijke klanken."""
    lines = []
    order = ['gu', 'qu', 'g_soft', 'c_soft', 'c']
    for key in order:
        rule = ctx.get(key)
        if not rule:
            continue
        chars  = ''.join(rule['before'])
        letter = key.replace('_soft', '')
        out    = rule['output']
        lines.append(
            f"  result = result.replace(/{letter}(?=[{chars}])/g, '{out}');"
        )
    # resterende c → k
    lines.append("  result = result.replace(/c(?![aeiou])/g, 'k');")
    return '\n'.join(lines)


def build_phonetic_js():
    phonetic_map = json.loads((DATA_DIR / 'phonetic_map.json').read_text(encoding='utf-8'))
    variants     = json.loads((DATA_DIR / 'phonetic_variants.json').read_text(encoding='utf-8'))

    accents    = phonetic_map['accents']
    fixed      = dict(sorted(phonetic_map['fixed_sounds'].items(), key=lambda x: -len(x[0])))
    ctx        = phonetic_map['context_sounds']
    single     = phonetic_map['single_sounds']
    exceptions = phonetic_map['exceptions']['no_change']

    variant_lookup: dict[str, str] = {
        v.lower(): correct
        for correct, vs in variants.items()
        for v in vs
    }

    ctx_lines = _ctx_replace_lines(ctx)
    today     = date.today().isoformat()

    content = f"""// phonetic.js — automatisch gegenereerd door src/build_phonetic_js.py op {today}
// Bron: data/phonetic_map.json + data/phonetic_variants.json
// Pas dit bestand NIET handmatig aan; draai update_index.py opnieuw.

// Accenten (á→a, é→e, …)
const PHONETIC_ACCENTS = {json.dumps(accents, ensure_ascii=False, indent=2)};

// Vaste klanken (ll→y, ñ→ny, v→b, h→"", …) — langste patronen eerst
const PHONETIC_FIXED = {json.dumps(fixed, ensure_ascii=False, indent=2)};

// Contextregels (c/g afhankelijk van volgende letter)
const PHONETIC_CONTEXT = {json.dumps(ctx, ensure_ascii=False, indent=2)};

// Losse tekens (j→h, y→j, overige ongewijzigd)
const PHONETIC_SINGLE = {json.dumps(single, ensure_ascii=False, indent=2)};

// Woorden die ongewijzigd blijven
const PHONETIC_EXCEPTIONS = new Set({json.dumps(exceptions, ensure_ascii=False)});

const ACCEPTED_VARIANTS = {json.dumps(variants, ensure_ascii=False, indent=2)};

const VARIANT_LOOKUP = {json.dumps(variant_lookup, ensure_ascii=False, indent=2)};

function _applyContextSounds(text) {{
  let result = text;
{ctx_lines}
  return result;
}}

function phoneticNormalize(word) {{
  const w = (word || '').toLowerCase().trim();
  if (PHONETIC_EXCEPTIONS.has(w)) return w;

  // 1. Accenten
  let result = w;
  for (const [pat, rep] of Object.entries(PHONETIC_ACCENTS)) {{
    result = result.split(pat).join(rep);
  }}
  // 2. Vaste klanken (langste patronen eerst)
  for (const [pat, rep] of Object.entries(PHONETIC_FIXED)) {{
    result = result.split(pat).join(rep);
  }}
  // 3. Contextafhankelijke klanken
  result = _applyContextSounds(result);
  // 4. Losse tekens
  result = result.split('').map(ch => PHONETIC_SINGLE[ch] ?? ch).join('');
  return result;
}}

function acceptVariant(input, threshold = 0.75) {{
  const phrase = (input || '').toLowerCase().trim();
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
