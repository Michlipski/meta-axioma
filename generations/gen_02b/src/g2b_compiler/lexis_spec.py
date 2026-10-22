"""Clean Domain Specification and IR Formulations for Axioma Lexis in System G2b.

Built 100% from the ground up from the ambitious elevator pitch:
"A fast, distraction-free, local-first vocabulary and spaced repetition studio. Type just the word ->
auto-hydrate definition, pronunciation, and example. Bite-sized daily reviews with adaptive spaced repetition,
1-tap undo, multi-deck tagging, retention curve analytics, and calm local-first sync."
"""

from g2b_compiler.ir.semantic_ir import (
    SemanticDomainIR, EntitySpec, EntityField, FieldType, DomainCapability, DomainInvariant
)
from g2b_compiler.ir.statechart_ir import StatechartIR, StateNode, Transition, EventSpec
from g2b_compiler.ir.contract_ir import DualBoundaryContractIR, NounContract, VerbContract


def build_lexis_g2b_semantic_ir() -> SemanticDomainIR:
    """Builds comprehensive Semantic Domain IR for Axioma Lexis under Generation 2b."""
    word_entity = EntitySpec(
        name="Word",
        plural_name="Words",
        description="A vocabulary term with pronunciation, definitions, examples, deck associations, tags, and SRS scheduling state.",
        fields=[
            EntityField(name="id", field_type=FieldType.STRING, description="UUID primary key"),
            EntityField(name="word", field_type=FieldType.STRING, description="Headword text"),
            EntityField(name="definition", field_type=FieldType.STRING, description="Clear English definition"),
            EntityField(name="part_of_speech", field_type=FieldType.STRING, description="noun, verb, adjective, etc."),
            EntityField(name="phonetic", field_type=FieldType.STRING, required=False, default="", description="IPA phonetic transcription"),
            EntityField(name="example", field_type=FieldType.STRING, required=False, default="", description="Contextual usage sentence"),
            EntityField(name="deck_id", field_type=FieldType.STRING, default="default", description="Associated deck foreign key"),
            EntityField(name="tags", field_type=FieldType.LIST_STRING, default=[], description="Categorical tags"),
            EntityField(name="status", field_type=FieldType.STRING, default="learning", description="learning | review | mastered"),
            EntityField(name="interval_days", field_type=FieldType.FLOAT, default=1.0, description="Current SRS interval in days"),
            EntityField(name="ease_factor", field_type=FieldType.FLOAT, default=2.5, description="SM-2 ease multiplier"),
            EntityField(name="repetition_level", field_type=FieldType.INTEGER, default=0, description="Consecutive successful recalls"),
            EntityField(name="next_review", field_type=FieldType.FLOAT, default=0.0, description="Timestamp when card is next due for review"),
        ]
    )

    deck_entity = EntitySpec(
        name="Deck",
        plural_name="Decks",
        description="A collection of vocabulary cards belonging to a specific topic or language.",
        fields=[
            EntityField(name="id", field_type=FieldType.STRING, description="Deck identifier"),
            EntityField(name="name", field_type=FieldType.STRING, description="Deck title"),
            EntityField(name="description", field_type=FieldType.STRING, default="", description="Deck summary"),
            EntityField(name="color", field_type=FieldType.STRING, default="#6366f1", description="UI accent color"),
        ]
    )

    capabilities = [
        DomainCapability(name="InstantWordCapture", description="2-second capture from word input", affected_entities=["Word"]),
        DomainCapability(name="SpeechPronunciation", description="Native browser Web Speech API pronunciation", affected_entities=["Word"]),
        DomainCapability(name="SpacedFlashcardReview", description="Adaptive SM-2 review session", affected_entities=["Word"], is_core_value=True),
        DomainCapability(name="DueQueueGating", description="Paced algorithmic due-queue filtering only cards where next_review <= now (AX-MEM-001).", affected_entities=["Word"]),
        DomainCapability(name="CompletionMilestone", description="Inbox-Zero celebration card when due queue reaches zero (AX-MEM-002).", affected_entities=["Word"]),
        DomainCapability(name="CramPracticeMode", description="Exploratory review mode for un-due cards without corrupting SM-2 intervals (AX-MEM-008).", affected_entities=["Word"]),
        DomainCapability(name="FunctorialUndo", description="1-tap rollback for accidental ratings (AX-MEM-004).", affected_entities=["Word"]),
        DomainCapability(name="DeckManagement", description="Multi-deck creation, tagging, and organization", affected_entities=["Deck", "Word"]),
        DomainCapability(name="RetentionAnalytics", description="Visual Ebbinghaus forgetting curves and mastery stats", affected_entities=["Word"]),
        DomainCapability(name="LocalFirstSync", description="Offline-first JSON export/import snapshot sync", affected_entities=["Word", "Deck"]),
        DomainCapability(name="HabitNotificationPrompt", description="Opt-in daily review reminder via Web Notification API (AX-MEM-005).", affected_entities=["Word"]),
    ]

    invariants = [
        # Tier 1 Structural Axioms
        DomainInvariant(invariant_id="L1-002", statement="Functorial Undo Reversibility", formal_rule="M_undo(M_rate(S)) == S"),
        DomainInvariant(invariant_id="L1-011_3", statement="Decoupled Persistence", formal_rule="State delta isolated from storage adapters"),
        DomainInvariant(invariant_id="L1-016", statement="Demarcated Exception Enclaves", formal_rule="Errors bounded in recovery cycles"),
        DomainInvariant(invariant_id="NEG-G2-005", statement="Anti-Mock Substrate", formal_rule="Zero simulated notifications or mock timers"),
        DomainInvariant(invariant_id="NEG-G2-006", statement="Clean-Slate Storage", formal_rule="Zero dummy test fixtures in production initial state"),

        # Tier 2 Universal Usability & Ergonomics
        DomainInvariant(invariant_id="HEUR-UX-001", statement="Visibility of System Status", formal_rule="All async operations declare visible progress state"),
        DomainInvariant(invariant_id="HEUR-UX-003", statement="User Control & Freedom", formal_rule="All compound states provide emergency cancel/abort exit"),
        DomainInvariant(invariant_id="HEUR-UX-005", statement="Error Prevention", formal_rule="Destructive actions require confirmation or undo"),
        DomainInvariant(invariant_id="HEUR-COG-001", statement="Fitts's Law Touch Target Baseline", formal_rule="Touch targets measure >= 44x44px"),
        DomainInvariant(invariant_id="HEUR-COG-002", statement="Hick's Law Micro-Session Bounding", formal_rule="Review micro-sessions capped at <= 15 cards"),

        # Tier 3 Domain Cognitive Science
        DomainInvariant(invariant_id="AX-MEM-001", statement="Due-Queue Temporal Isolation", formal_rule="Q_due(t) = { c in Deck | c.next_review <= t }"),
        DomainInvariant(invariant_id="AX-MEM-002", statement="Completion Closure & Inbox Zero", formal_rule="|Q_due(t)| == 0 ==> State = SessionCompleted"),
        DomainInvariant(invariant_id="AX-MEM-004", statement="Functorial Rating Reversibility", formal_rule="Undo(ApplyRating(c, k)) == c_prev"),
        DomainInvariant(invariant_id="AX-MEM-005", statement="Calm Habit Loop & Notification Hygiene", formal_rule="DispatchNotification(t) ==> OptIn == True and |Q_due| > 0"),
        DomainInvariant(invariant_id="AX-MEM-008", statement="Dual-Track Study Modes", formal_rule="Modes = { Mode_SpacedDue, Mode_CramPractice }"),
    ]

    clean_seeds = {
        "decks": [
            {
                "id": "deck_core",
                "name": "General Vocabulary",
                "description": "Essential reading and literature vocabulary.",
                "color": "#6366f1"
            }
        ],
        "words": [
            {
                "id": "word_axioma_zuhandenheit",
                "word": "zuhandenheit",
                "definition": "Readiness-to-hand; the practical, absorbed familiarity with tools in purposeful human activity.",
                "part_of_speech": "noun",
                "phonetic": "/tsuːˈhandn̩haɪt/",
                "example": "When a hammer is functioning seamlessly, it withdraws from conscious contemplation into pure zuhandenheit.",
                "deck_id": "deck_core",
                "tags": ["philosophy", "phenomenology"],
                "status": "learning",
                "interval_days": 1.0,
                "ease_factor": 2.5,
                "repetition_level": 0,
                "next_review": 1776000000.0
            }
        ]
    }

    return SemanticDomainIR(
        app_id="axioma_lexis",
        title="Axioma Lexis",
        tagline="Adaptive Spaced Repetition Vocabulary & Flashcards",
        persona="The Focus Learner & Deep Reader",
        jtbd_summary="Capture words in 2 seconds while reading, organize into decks, and retain them effortlessly through bite-sized, low-pressure spaced reviews.",
        entities=[word_entity, deck_entity],
        capabilities=capabilities,
        invariants=invariants,
        initial_clean_seeds=clean_seeds
    )


def build_lexis_g2b_statechart_ir() -> StatechartIR:
    """Builds formal XState v5 Statechart IR for Axioma Lexis under Generation 2b."""
    states = {
        "idle": StateNode(
            id="idle",
            description="Launch dashboard showing search bar, quick deck stats, due badge, and module launchers.",
            on={
                "CAPTURE_START": Transition(target="capturing", event="CAPTURE_START"),
                "START_REVIEW": Transition(target="reviewing", event="START_REVIEW"),
                "START_CRAM": Transition(target="cramming", event="START_CRAM"),
                "OPEN_DECKS": Transition(target="deck_management", event="OPEN_DECKS"),
                "OPEN_ANALYTICS": Transition(target="analytics", event="OPEN_ANALYTICS"),
                "OPEN_SYNC": Transition(target="sync", event="OPEN_SYNC"),
                "OPEN_NOTIFICATIONS": Transition(target="notification_prompt", event="OPEN_NOTIFICATIONS"),
            }
        ),
        "capturing": StateNode(
            id="capturing",
            initial="typing",
            description="Single-word capture and dictionary hydration with offline fallback enclave.",
            states={
                "typing": StateNode(
                    id="typing",
                    on={
                        "SUBMIT_WORD": Transition(target="hydrating", event="SUBMIT_WORD"),
                        "CANCEL": Transition(target="idle", event="CANCEL"),
                    }
                ),
                "hydrating": StateNode(
                    id="hydrating",
                    description="Asynchronously querying dictionary data.",
                    on={
                        "HYDRATE_SUCCESS": Transition(target="preview", event="HYDRATE_SUCCESS"),
                        "HYDRATE_FAIL": Transition(target="offline_fallback", event="HYDRATE_FAIL"),
                    }
                ),
                "preview": StateNode(
                    id="preview",
                    description="Displaying fetched definition, phonetics, and example.",
                    on={
                        "CONFIRM_SAVE": Transition(target="idle", event="CONFIRM_SAVE"),
                        "CANCEL": Transition(target="idle", event="CANCEL"),
                    }
                ),
                "offline_fallback": StateNode(
                    id="offline_fallback",
                    meta={"is_error_state": True},
                    description="Permits manual entry when offline.",
                    on={
                        "SAVE_MANUAL": Transition(target="idle", event="SAVE_MANUAL"),
                        "RETRY": Transition(target="hydrating", event="RETRY"),
                        "CANCEL": Transition(target="idle", event="CANCEL"),
                    }
                )
            },
            on={
                "ABORT": Transition(target="idle", event="ABORT")
            }
        ),
        "reviewing": StateNode(
            id="reviewing",
            initial="prompt",
            description="Compound state governing bite-sized spaced repetition review.",
            states={
                "prompt": StateNode(
                    id="prompt",
                    description="Front of card: displays headword, phonetics, and audio trigger.",
                    on={
                        "FLIP_CARD": Transition(target="revealed", event="FLIP_CARD"),
                        "EXIT_REVIEW": Transition(target="idle", event="EXIT_REVIEW"),
                    }
                ),
                "revealed": StateNode(
                    id="revealed",
                    meta={"is_value_state": True},
                    description="Back of card: definition revealed with SM-2 rating buttons.",
                    on={
                        "RATE_FORGOT": Transition(target="advancing", event="RATE_FORGOT"),
                        "RATE_HARD": Transition(target="advancing", event="RATE_HARD"),
                        "RATE_GOOD": Transition(target="advancing", event="RATE_GOOD"),
                        "RATE_EASY": Transition(target="advancing", event="RATE_EASY"),
                        "UNDO": Transition(target="prompt", event="UNDO"),
                    }
                ),
                "advancing": StateNode(
                    id="advancing",
                    description="Computes SM-2 delta and presents next card or concludes session.",
                    on={
                        "NEXT_CARD": Transition(target="prompt", event="NEXT_CARD"),
                        "SESSION_COMPLETE": Transition(target="completed", event="SESSION_COMPLETE"),
                    }
                ),
                "completed": StateNode(
                    id="completed",
                    description="Explicit milestone celebration state when due queue hits zero (AX-MEM-002).",
                    on={
                        "CLOSE_SESSION": Transition(target="idle", event="CLOSE_SESSION"),
                        "CRAM_AHEAD": Transition(target="cramming", event="CRAM_AHEAD"),
                    }
                )
            },
            on={
                "EXIT_REVIEW": Transition(target="idle", event="EXIT_REVIEW")
            }
        ),
        "cramming": StateNode(
            id="cramming",
            initial="prompt",
            description="Exploratory practice mode for un-due cards without SM-2 mutation (AX-MEM-008).",
            states={
                "prompt": StateNode(
                    id="prompt",
                    on={
                        "FLIP_CRAM": Transition(target="revealed", event="FLIP_CRAM"),
                        "EXIT_CRAM": Transition(target="idle", event="EXIT_CRAM"),
                    }
                ),
                "revealed": StateNode(
                    id="revealed",
                    on={
                        "NEXT_CRAM": Transition(target="prompt", event="NEXT_CRAM"),
                        "EXIT_CRAM": Transition(target="idle", event="EXIT_CRAM"),
                    }
                )
            },
            on={
                "EXIT_CRAM": Transition(target="idle", event="EXIT_CRAM")
            }
        ),
        "deck_management": StateNode(
            id="deck_management",
            initial="browsing",
            description="Multi-deck organization and tag filtering.",
            states={
                "browsing": StateNode(
                    id="browsing",
                    on={
                        "CREATE_DECK": Transition(target="creating_deck", event="CREATE_DECK"),
                        "CLOSE_DECKS": Transition(target="idle", event="CLOSE_DECKS"),
                    }
                ),
                "creating_deck": StateNode(
                    id="creating_deck",
                    on={
                        "CONFIRM_CREATE_DECK": Transition(target="browsing", event="CONFIRM_CREATE_DECK"),
                        "CANCEL": Transition(target="browsing", event="CANCEL"),
                    }
                )
            },
            on={
                "CLOSE": Transition(target="idle", event="CLOSE")
            }
        ),
        "analytics": StateNode(
            id="analytics",
            initial="viewing",
            description="Ebbinghaus forgetting curve and mastery stats.",
            states={
                "viewing": StateNode(
                    id="viewing",
                    on={
                        "CLOSE_ANALYTICS": Transition(target="idle", event="CLOSE_ANALYTICS")
                    }
                )
            },
            on={
                "CLOSE": Transition(target="idle", event="CLOSE")
            }
        ),
        "sync": StateNode(
            id="sync",
            initial="viewing",
            description="Local-first snapshot export and backup.",
            states={
                "viewing": StateNode(
                    id="viewing",
                    on={
                        "EXPORT_DATA": Transition(target="viewing", event="EXPORT_DATA"),
                        "IMPORT_DATA": Transition(target="viewing", event="IMPORT_DATA"),
                        "CLOSE_SYNC": Transition(target="idle", event="CLOSE_SYNC")
                    }
                )
            },
            on={
                "CLOSE": Transition(target="idle", event="CLOSE")
            }
        ),
        "notification_prompt": StateNode(
            id="notification_prompt",
            description="Modal configuring opt-in daily habit reminders (AX-MEM-005).",
            on={
                "SAVE_PREFERENCES": Transition(target="idle", event="SAVE_PREFERENCES"),
                "CLOSE_SETTINGS": Transition(target="idle", event="CLOSE_SETTINGS"),
                "CLOSE": Transition(target="idle", event="CLOSE")
            }
        )
    }

    events = {
        "CAPTURE_START": EventSpec(name="CAPTURE_START"),
        "START_REVIEW": EventSpec(name="START_REVIEW"),
        "START_CRAM": EventSpec(name="START_CRAM"),
        "OPEN_DECKS": EventSpec(name="OPEN_DECKS"),
        "OPEN_ANALYTICS": EventSpec(name="OPEN_ANALYTICS"),
        "OPEN_SYNC": EventSpec(name="OPEN_SYNC"),
        "OPEN_NOTIFICATIONS": EventSpec(name="OPEN_NOTIFICATIONS"),
        "SUBMIT_WORD": EventSpec(name="SUBMIT_WORD"),
        "HYDRATE_SUCCESS": EventSpec(name="HYDRATE_SUCCESS"),
        "HYDRATE_FAIL": EventSpec(name="HYDRATE_FAIL"),
        "CONFIRM_SAVE": EventSpec(name="CONFIRM_SAVE"),
        "CANCEL": EventSpec(name="CANCEL"),
        "ABORT": EventSpec(name="ABORT"),
        "SAVE_MANUAL": EventSpec(name="SAVE_MANUAL"),
        "RETRY": EventSpec(name="RETRY"),
        "FLIP_CARD": EventSpec(name="FLIP_CARD"),
        "RATE_FORGOT": EventSpec(name="RATE_FORGOT"),
        "RATE_HARD": EventSpec(name="RATE_HARD"),
        "RATE_GOOD": EventSpec(name="RATE_GOOD"),
        "RATE_EASY": EventSpec(name="RATE_EASY"),
        "UNDO": EventSpec(name="UNDO"),
        "NEXT_CARD": EventSpec(name="NEXT_CARD"),
        "SESSION_COMPLETE": EventSpec(name="SESSION_COMPLETE"),
        "CLOSE_SESSION": EventSpec(name="CLOSE_SESSION"),
        "CRAM_AHEAD": EventSpec(name="CRAM_AHEAD"),
        "EXIT_REVIEW": EventSpec(name="EXIT_REVIEW"),
        "FLIP_CRAM": EventSpec(name="FLIP_CRAM"),
        "NEXT_CRAM": EventSpec(name="NEXT_CRAM"),
        "EXIT_CRAM": EventSpec(name="EXIT_CRAM"),
        "CREATE_DECK": EventSpec(name="CREATE_DECK"),
        "CONFIRM_CREATE_DECK": EventSpec(name="CONFIRM_CREATE_DECK"),
        "CLOSE_DECKS": EventSpec(name="CLOSE_DECKS"),
        "CLOSE_ANALYTICS": EventSpec(name="CLOSE_ANALYTICS"),
        "EXPORT_DATA": EventSpec(name="EXPORT_DATA"),
        "IMPORT_DATA": EventSpec(name="IMPORT_DATA"),
        "CLOSE_SYNC": EventSpec(name="CLOSE_SYNC"),
        "SAVE_PREFERENCES": EventSpec(name="SAVE_PREFERENCES"),
        "CLOSE_SETTINGS": EventSpec(name="CLOSE_SETTINGS"),
        "CLOSE": EventSpec(name="CLOSE"),
    }

    return StatechartIR(
        machine_id="axioma_lexis_g2b",
        initial="idle",
        states=states,
        events=events,
        context_schema={"deck": [], "decks": [], "review_index": 0}
    )


def build_lexis_g2b_contract_ir() -> DualBoundaryContractIR:
    """Builds Dual Boundary Contract IR for Axioma Lexis in System G2b."""
    word_noun = NounContract(
        entity_name="Word",
        fields={
            "id": "string",
            "word": "string",
            "definition": "string",
            "part_of_speech": "string",
            "phonetic": "string",
            "example": "string",
            "deck_id": "string",
            "tags": "string[]",
            "status": "string",
            "interval_days": "number",
            "ease_factor": "number",
            "repetition_level": "number",
            "next_review": "number",
        },
        required_fields=["id", "word", "definition", "status", "interval_days", "ease_factor"],
        description="A vocabulary term with pronunciation, definitions, examples, deck associations, and SRS state."
    )

    deck_noun = NounContract(
        entity_name="Deck",
        fields={
            "id": "string",
            "name": "string",
            "description": "string",
            "color": "string",
        },
        required_fields=["id", "name"],
        description="A collection of vocabulary cards belonging to a specific topic or language."
    )

    verbs = {
        "CAPTURE_WORD": VerbContract(
            action_name="captureWord",
            from_state="capturing.preview",
            to_state="idle",
            event_payload_type="{ word: Word }",
            description="Appends a new hydrated word to the persistent deck.",
            has_side_effect=True
        ),
        "RATE_FLASHCARD": VerbContract(
            action_name="rateFlashcard",
            from_state="reviewing.revealed",
            to_state="reviewing.advancing",
            event_payload_type="{ word_id: string, rating: 'FORGOT' | 'HARD' | 'GOOD' | 'EASY' }",
            description="Updates SM-2 repetition intervals with reversible history snapshot.",
            has_side_effect=True
        ),
        "UNDO_REVIEW": VerbContract(
            action_name="undoReview",
            from_state="reviewing.revealed",
            to_state="reviewing.prompt",
            event_payload_type="{}",
            description="Restores preceding flashcard state from history stack without side-effect leaks.",
            has_side_effect=True
        ),
        "CREATE_DECK": VerbContract(
            action_name="createDeck",
            from_state="decks.creating",
            to_state="decks.list",
            event_payload_type="{ deck: Deck }",
            description="Creates a new topic deck container.",
            has_side_effect=True
        ),
    }

    return DualBoundaryContractIR(
        app_id="axioma_lexis",
        nouns={"Word": word_noun, "Deck": deck_noun},
        verbs=verbs
    )
