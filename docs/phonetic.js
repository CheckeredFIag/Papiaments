// phonetic.js — automatisch gegenereerd door src/build_phonetic_js.py op 2026-04-21
// Bron: data/phonetic_map.json + data/phonetic_variants.json
// Pas dit bestand NIET handmatig aan; draai update_index.py opnieuw.

const PHONETIC_MAP = {
  "qui": "ki",
  "que": "ke",
  "ll": "y",
  "gu": "w",
  "qu": "k",
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
  "û": "u",
  "ñ": "ny",
  "v": "b",
  "x": "ks"
};

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

function phoneticNormalize(word) {
  let result = word.toLowerCase().trim();
  for (const [pattern, replacement] of Object.entries(PHONETIC_MAP)) {
    result = result.split(pattern).join(replacement);
  }
  return result;
}

function acceptVariant(input, threshold = 0.75) {
  const phrase = input.toLowerCase().trim();
  if (VARIANT_LOOKUP[phrase]) return { ok: true, correct: VARIANT_LOOKUP[phrase] };
  const norm = phoneticNormalize(phrase);
  for (const correct of Object.keys(ACCEPTED_VARIANTS)) {
    if (norm === phoneticNormalize(correct)) return { ok: true, correct };
  }
  return { ok: false, correct: '' };
}
