---
domain: AxiomaLexisDomain
related_domains:
  - AxiomRegistry
  - AppSpecification
---

CONSTRAINTS:
- Flashcard review ratings must preserve functorial reversibility ([L1-002]): accidental ratings can be undone instantly.
- Spaced repetition intervals must adapt dynamically to memory retention via SM-2 algorithms.
- Word lookups must be progressive: definitions load immediately with offline fallback and online streaming enrichment.
- Decoupled persistence across Boundary 3 ([L1-011_3]): word deck mutations must be pure transformations persisted without unmediated side effects.
- Deleted words must formally account for Landauer bit erasure against the thermodynamic limit ([L1-008]).
- Unexpected network or audio failures must be isolated inside Demarcated Exception Enclaves ([L1-016]).

GLOSSARY:
- Axioma Lexis: Autonomous vocabulary dictionary and adaptive flashcards application for Android.
- SRS Rating: The four-button memory feedback: Forgot, Hard, Good, Easy.
- Ease Factor: The individual multiplier determining how quickly review intervals grow for a word.

# ENTITY: Word
MUST HAVE:
- id: String
- word: String
- definition: String
- part_of_speech: String
- phonetic_us: String (Optional)
- phonetic_uk: String (Optional)
- example: String (Optional)
- synonyms: List[String] (Optional)
- antonyms: List[String] (Optional)
- translation_es: String (Optional)
- repetition_level: Integer
- interval_days: Float
- ease_factor: Float
- next_review: Float
- status: String (learning, review, mastered)

# EVENT: WordReviewed
TRIGGER:
- Emitted when a user submits an SRS rating for a flashcard.
PAYLOAD:
- word_id
- rating (FORGOT, HARD, GOOD, EASY)
- new_interval_days
- new_ease_factor
- next_review
