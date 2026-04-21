// phonetic.js — automatisch gegenereerd door src/build_phonetic_js.py op 2026-04-22
// Bron: data/phonetic_map.json + data/phonetic_variants.json
// Pas dit bestand NIET handmatig aan; draai update_index.py opnieuw.

// Accenten (á→a, é→e, …)
const PHONETIC_ACCENTS = {
  "á": "a",
  "à": "a",
  "â": "a",
  "é": "e",
  "è": "e",
  "ê": "e",
  "í": "i",
  "ì": "i",
  "î": "i",
  "ó": "o",
  "ò": "o",
  "ô": "o",
  "ú": "u",
  "ù": "u",
  "û": "u"
};

// Vaste klanken (ll→y, ñ→ny, v→b, h→"", …) — langste patronen eerst
const PHONETIC_FIXED = {
  "ll": "y",
  "ch": "ch",
  "rr": "r",
  "ñ": "ny",
  "v": "b",
  "x": "ks",
  "h": ""
};

// Contextregels (c/g afhankelijk van volgende letter)
const PHONETIC_CONTEXT = {
  "gu": {
    "before": [
      "e",
      "i"
    ],
    "output": "g"
  },
  "qu": {
    "before": [
      "e",
      "i"
    ],
    "output": "k"
  },
  "g_soft": {
    "before": [
      "e",
      "i"
    ],
    "output": "h"
  },
  "c_soft": {
    "before": [
      "e",
      "i"
    ],
    "output": "s"
  },
  "c": {
    "before": [
      "a",
      "o",
      "u"
    ],
    "output": "k"
  }
};

// Losse tekens (j→h, y→j, overige ongewijzigd)
const PHONETIC_SINGLE = {
  "a": "a",
  "b": "b",
  "d": "d",
  "e": "e",
  "f": "f",
  "g": "g",
  "i": "i",
  "j": "h",
  "k": "k",
  "l": "l",
  "m": "m",
  "n": "n",
  "o": "o",
  "p": "p",
  "r": "r",
  "s": "s",
  "t": "t",
  "u": "u",
  "y": "j"
};

// Woorden die ongewijzigd blijven
const PHONETIC_EXCEPTIONS = new Set(["aruba", "papiamento", "cas", "scol", "cacho", "poko poko", "no papia asina liher"]);

const ACCEPTED_VARIANTS = {
  "bo ta": [
    "bo ta",
    "vota",
    "bota",
    "vo ta"
  ],
  "bon dia": [
    "bon diá",
    "bon dià",
    "bon dia",
    "buen dia",
    "buenos dias"
  ],
  "awa": [
    "agua",
    "aqua",
    "agwa",
    "awa"
  ],
  "yama": [
    "llama",
    "jama",
    "yama"
  ],
  "mi ta": [
    "mita",
    "mi ta"
  ],
  "danki": [
    "danki",
    "tranqui",
    "dunkin"
  ],
  "kachó": [
    "kacho",
    "kachó"
  ],
  "cas": [
    "kas",
    "cas"
  ],
  "mi ta aki": [
    "mi ta aki",
    "mita aqui",
    "mi ta aqui"
  ],
  "bo ta aki": [
    "bo ta aki",
    "vota aqui",
    "vota aquí",
    "bota aki",
    "bo ta aqui"
  ]
};

const VARIANT_LOOKUP = {
  "bo ta": "bo ta",
  "vota": "bo ta",
  "bota": "bo ta",
  "vo ta": "bo ta",
  "bon diá": "bon dia",
  "bon dià": "bon dia",
  "bon dia": "bon dia",
  "buen dia": "bon dia",
  "buenos dias": "bon dia",
  "agua": "awa",
  "aqua": "awa",
  "agwa": "awa",
  "awa": "awa",
  "llama": "yama",
  "jama": "yama",
  "yama": "yama",
  "mita": "mi ta",
  "mi ta": "mi ta",
  "danki": "danki",
  "tranqui": "danki",
  "dunkin": "danki",
  "kacho": "kachó",
  "kachó": "kachó",
  "kas": "cas",
  "cas": "cas",
  "mi ta aki": "mi ta aki",
  "mita aqui": "mi ta aki",
  "mi ta aqui": "mi ta aki",
  "bo ta aki": "bo ta aki",
  "vota aqui": "bo ta aki",
  "vota aquí": "bo ta aki",
  "bota aki": "bo ta aki",
  "bo ta aqui": "bo ta aki"
};

function _applyContextSounds(text) {
  let result = text;
  result = result.replace(/gu(?=[ei])/g, 'g');
  result = result.replace(/qu(?=[ei])/g, 'k');
  result = result.replace(/g(?=[ei])/g, 'h');
  result = result.replace(/c(?=[ei])/g, 's');
  result = result.replace(/c(?=[aou])/g, 'k');
  result = result.replace(/c(?![aeiou])/g, 'k');
  return result;
}

function phoneticNormalize(word) {
  const w = (word || '').toLowerCase().trim();
  if (PHONETIC_EXCEPTIONS.has(w)) return w;

  // 1. Accenten
  let result = w;
  for (const [pat, rep] of Object.entries(PHONETIC_ACCENTS)) {
    result = result.split(pat).join(rep);
  }
  // 2. Vaste klanken (langste patronen eerst)
  for (const [pat, rep] of Object.entries(PHONETIC_FIXED)) {
    result = result.split(pat).join(rep);
  }
  // 3. Contextafhankelijke klanken
  result = _applyContextSounds(result);
  // 4. Losse tekens
  result = result.split('').map(ch => PHONETIC_SINGLE[ch] ?? ch).join('');
  return result;
}

function acceptVariant(input, threshold = 0.75) {
  const phrase = (input || '').toLowerCase().trim();
  if (VARIANT_LOOKUP[phrase]) return { ok: true, correct: VARIANT_LOOKUP[phrase] };
  const norm = phoneticNormalize(phrase);
  for (const correct of Object.keys(ACCEPTED_VARIANTS)) {
    if (norm === phoneticNormalize(correct)) return { ok: true, correct };
  }
  return { ok: false, correct: '' };
}
