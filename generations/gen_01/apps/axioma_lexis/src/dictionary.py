"""Dictionary Lookup Engine with Local Cache and Free API Fallback.

Provides progressive dictionary lookup: definitions, part of speech, US/UK
phonetics, usage examples, synonyms, and translations without paid API dependencies.
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional
import urllib.request
import urllib.error

APP_DIR = Path(__file__).parent.parent
DATA_DIR = APP_DIR / "data"
DICT_SEED_FILE = DATA_DIR / "dictionary_seed.json"


class DictionaryEngine:
    """Manages word lookups across local pre-seeded dictionary and free web sources."""

    def __init__(self):
        self._local_cache: Dict[str, Dict[str, Any]] = self._load_local_seed()

    def _load_local_seed(self) -> Dict[str, Dict[str, Any]]:
        if DICT_SEED_FILE.exists():
            try:
                with open(DICT_SEED_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def lookup(self, raw_word: str) -> Dict[str, Any]:
        """Looks up a word, querying local seed dictionary first, then free public API."""
        word = raw_word.strip().lower()
        if not word:
            raise ValueError("Word cannot be empty.")

        # 1. Local seed check (Fast & offline)
        if word in self._local_cache:
            entry = dict(self._local_cache[word])
            entry["source"] = "local_dictionary"
            return entry

        # 2. Free Public Dictionary API (api.dictionaryapi.dev)
        try:
            url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{urllib.parse.quote(word)}"
            req = urllib.request.Request(url, headers={"User-Agent": "AxiomaLexis/1.0"})
            with urllib.request.urlopen(req, timeout=3.5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                if isinstance(data, list) and len(data) > 0:
                    parsed = self._parse_api_response(word, data[0])
                    # Cache locally
                    self._local_cache[word] = parsed
                    return parsed
        except Exception:
            pass

        # 3. Clean fallback entry for unrecognized or offline words
        fallback = {
            "word": word,
            "part_of_speech": "noun",
            "phonetic_us": f"/{word}/",
            "phonetic_uk": f"/{word}/",
            "definition": f"Definition for '{word}'. Tap to edit meaning or notes.",
            "example": f"This is an example sentence using the word '{word}'.",
            "synonyms": [],
            "antonyms": [],
            "translation_es": "",
            "source": "fallback",
        }
        return fallback

    def _parse_api_response(self, word: str, api_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extracts structured fields from Free Dictionary API format."""
        phonetic_us = api_data.get("phonetic", f"/{word}/")
        phonetic_uk = phonetic_us
        phonetics_list = api_data.get("phonetics", [])
        for p in phonetics_list:
            text = p.get("text")
            audio = p.get("audio", "")
            if text:
                if "uk" in audio.lower():
                    phonetic_uk = text
                else:
                    phonetic_us = text

        meanings = api_data.get("meanings", [])
        part_of_speech = meanings[0].get("partOfSpeech", "noun") if meanings else "noun"
        definition = "No definition found."
        example = f"Example context for {word}."
        synonyms = []
        antonyms = []

        if meanings:
            defs = meanings[0].get("definitions", [])
            if defs:
                definition = defs[0].get("definition", definition)
                example = defs[0].get("example", example)
                synonyms = defs[0].get("synonyms", [])[:4]
                antonyms = defs[0].get("antonyms", [])[:4]

        return {
            "word": word,
            "part_of_speech": part_of_speech,
            "phonetic_us": phonetic_us,
            "phonetic_uk": phonetic_uk,
            "definition": definition,
            "example": example,
            "synonyms": synonyms,
            "antonyms": antonyms,
            "translation_es": "",
            "source": "free_dictionary_api",
        }
