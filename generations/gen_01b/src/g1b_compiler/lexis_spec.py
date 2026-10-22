"""Clean Domain Specification and IR Formulations for Axioma Lexis in System G1b.

Employs the stripped-down, authentic elevator pitch without reactionary micro-prescriptive clutter:
"A fast, distraction-free, local-first vocabulary app. Type just the word -> auto-hydrate
definition, pronunciation, and example. Bite-sized daily reviews with adaptive spaced repetition
and 1-tap undo."
"""

from g1b_compiler.ir.semantic_ir import (
    SemanticDomainIR, EntitySpec, EntityField, FieldType, DomainCapability, DomainInvariant
)
from g1b_compiler.ir.statechart_ir import StatechartIR, StateNode, Transition, EventSpec
from g1b_compiler.ir.contract_ir import DualBoundaryContractIR, NounContract, VerbContract


def build_lexis_semantic_ir() -> SemanticDomainIR:
    """Builds clean Semantic IR for Axioma Lexis."""
    word_entity = EntitySpec(
        name="Word",
        plural_name="Words",
        description="A vocabulary term with pronunciation, definitions, examples, and SRS scheduling state.",
        fields=[
            EntityField(name="id", field_type=FieldType.STRING, description="UUID primary key"),
            EntityField(name="word", field_type=FieldType.STRING, description="Headword text"),
            EntityField(name="definition", field_type=FieldType.STRING, description="Clear English definition"),
            EntityField(name="part_of_speech", field_type=FieldType.STRING, description="e.g. noun, verb, adjective"),
            EntityField(name="phonetic", field_type=FieldType.STRING, required=False, default="", description="IPA phonetic transcription"),
            EntityField(name="example", field_type=FieldType.STRING, required=False, default="", description="Contextual usage sentence"),
            EntityField(name="status", field_type=FieldType.STRING, default="learning", description="learning | review | mastered"),
            EntityField(name="interval_days", field_type=FieldType.FLOAT, default=1.0, description="Current SRS interval"),
            EntityField(name="ease_factor", field_type=FieldType.FLOAT, default=2.5, description="SM-2 ease multiplier"),
            EntityField(name="repetition_level", field_type=FieldType.INTEGER, default=0, description="Consecutive successful recalls"),
            EntityField(name="next_review", field_type=FieldType.FLOAT, default=0.0, description="Timestamp for next review"),
        ]
    )

    capabilities = [
        DomainCapability(name="InstantWordCapture", description="2-second capture from word input", affected_entities=["Word"]),
        DomainCapability(name="SpacedFlashcardReview", description="Adaptive SM-2 review session", affected_entities=["Word"], is_core_value=True),
        DomainCapability(name="DueQueueGating", description="Paced algorithmic due-queue filtering only cards where next_review <= now (AX-MEM-001).", affected_entities=["Word"]),
        DomainCapability(name="HabitNotificationPrompt", description="Opt-in daily review reminder via browser Web Notification API (AX-MEM-005).", affected_entities=["Word"]),
        DomainCapability(name="CramPracticeMode", description="Exploratory review mode for un-due cards without corrupting SM-2 intervals (AX-MEM-008).", affected_entities=["Word"]),
        DomainCapability(name="FunctorialUndo", description="1-tap rollback for accidental ratings (AX-MEM-004).", affected_entities=["Word"]),
        DomainCapability(name="DeckManagement", description="Offline-first deck search and browsing", affected_entities=["Word"]),
    ]

    invariants = [
        DomainInvariant(invariant_id="AX-MEM-001", statement="Due-Queue Temporal Isolation", formal_rule="Q_due(t) = { c in Deck | c.next_review <= t }"),
        DomainInvariant(invariant_id="AX-MEM-002", statement="Completion Closure & Inbox Zero", formal_rule="|Q_due(t)| == 0 ==> State = SessionCompleted"),
        DomainInvariant(invariant_id="AX-MEM-004", statement="Functorial Rating Reversibility", formal_rule="Undo(ApplyRating(c, k)) == c_prev"),
        DomainInvariant(invariant_id="AX-MEM-005", statement="Calm Habit Loop & Notification Hygiene", formal_rule="DispatchNotification(t) ==> OptIn == True and |Q_due| > 0"),
        DomainInvariant(invariant_id="AX-MEM-008", statement="Dual-Track Study Modes", formal_rule="Modes = { Mode_SpacedDue, Mode_CramPractice }"),
        DomainInvariant(invariant_id="L1-002", statement="Functorial Undo Reversibility", formal_rule="M_undo(M_rate(S)) == S"),
        DomainInvariant(invariant_id="L1-011_3", statement="Decoupled Persistence", formal_rule="State delta isolated from storage adapters"),
        DomainInvariant(invariant_id="NEG-G2-005", statement="Anti-Mock Substrate", formal_rule="Zero simulated notifications or mock timers"),
        DomainInvariant(invariant_id="NEG-G2-006", statement="Clean-Slate Storage", formal_rule="Zero mock test fixtures in production initial state"),
    ]

    # Pristine clean seed: zero fake test junk, only essential foundational seed
    clean_seeds = {
        "words": [
            {
                "id": "word_axioma_zuhandenheit",
                "word": "zuhandenheit",
                "definition": "Readiness-to-hand; the practical, absorbed familiarity with tools in purposeful human activity.",
                "part_of_speech": "noun",
                "phonetic": "/tsuːˈhandn̩haɪt/",
                "example": "When a hammer is functioning seamlessly, it withdraws from conscious contemplation into pure zuhandenheit.",
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
        persona="The Focus Learner & Reader",
        jtbd_summary="Capture words in 2 seconds while reading and retain them effortlessly through bite-sized, low-pressure spaced reviews.",
        entities=[word_entity],
        capabilities=capabilities,
        invariants=invariants,
        initial_clean_seeds=clean_seeds
    )


def build_lexis_statechart_ir() -> StatechartIR:
    """Builds formal XState v5 Statechart IR for Axioma Lexis."""
    states = {
        "idle": StateNode(
            id="idle",
            description="Launch dashboard showing search bar, quick deck stats, and review launcher.",
            on={
                "CAPTURE_START": Transition(target="capturing", event="CAPTURE_START", description="User begins typing a word"),
                "START_REVIEW": Transition(target="reviewing", event="START_REVIEW", description="User launches daily review session"),
                "START_CRAM": Transition(target="cramming", event="START_CRAM", description="User launches unrestricted practice cram"),
                "OPEN_NOTIFICATIONS": Transition(target="notification_prompt", event="OPEN_NOTIFICATIONS", description="User configures reminders"),
                "BROWSE_DECK": Transition(target="deck_browsing", event="BROWSE_DECK", description="User opens deck list"),
            }
        ),
        "capturing": StateNode(
            id="capturing",
            initial="typing",
            description="Compound state governing single-word capture and dictionary hydration.",
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
                    description="Displaying fetched definition and example.",
                    on={
                        "CONFIRM_SAVE": Transition(target="idle", event="CONFIRM_SAVE", description="Word saved to local deck"),
                        "CANCEL": Transition(target="idle", event="CANCEL"),
                    }
                ),
                "offline_fallback": StateNode(
                    id="offline_fallback",
                    description="Permits manual entry when offline.",
                    meta={"is_error_state": True},
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
            description="Compound state governing bite-sized spaced repetition flashcard review.",
            states={
                "prompt": StateNode(
                    id="prompt",
                    description="Front of card: displays headword and phonetics.",
                    on={
                        "FLIP_CARD": Transition(target="revealed", event="FLIP_CARD", description="User reveals card answer"),
                        "EXIT_REVIEW": Transition(target="idle", event="EXIT_REVIEW"),
                    }
                ),
                "revealed": StateNode(
                    id="revealed",
                    description="Back of card: definition revealed with SM-2 rating buttons.",
                    meta={"is_value_state": True},  # Core JTBD delivered here!
                    on={
                        "RATE_FORGOT": Transition(target="advancing", event="RATE_FORGOT"),
                        "RATE_HARD": Transition(target="advancing", event="RATE_HARD"),
                        "RATE_GOOD": Transition(target="advancing", event="RATE_GOOD"),
                        "RATE_EASY": Transition(target="advancing", event="RATE_EASY"),
                        "UNDO": Transition(target="prompt", event="UNDO", description="Reversible undo"),
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
                    description="Explicit milestone celebratory state when due queue reaches zero (AX-MEM-002).",
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
                    description="Front of cram card.",
                    on={
                        "FLIP_CRAM": Transition(target="revealed", event="FLIP_CRAM"),
                        "EXIT_CRAM": Transition(target="idle", event="EXIT_CRAM"),
                    }
                ),
                "revealed": StateNode(
                    id="revealed",
                    description="Back of cram card.",
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
        "notification_prompt": StateNode(
            id="notification_prompt",
            description="Modal configuring opt-in daily habit reminders (AX-MEM-005).",
            on={
                "SAVE_PREFERENCES": Transition(target="idle", event="SAVE_PREFERENCES"),
                "CLOSE_SETTINGS": Transition(target="idle", event="CLOSE_SETTINGS"),
            }
        ),
        "deck_browsing": StateNode(
            id="deck_browsing",
            description="Viewing and searching saved vocabulary cards.",
            on={
                "CLOSE": Transition(target="idle", event="CLOSE"),
                "DELETE_WORD": Transition(target="deck_browsing", event="DELETE_WORD"),
            }
        )
    }

    events = {
        "CAPTURE_START": EventSpec(name="CAPTURE_START"),
        "START_REVIEW": EventSpec(name="START_REVIEW"),
        "START_CRAM": EventSpec(name="START_CRAM"),
        "OPEN_NOTIFICATIONS": EventSpec(name="OPEN_NOTIFICATIONS"),
        "BROWSE_DECK": EventSpec(name="BROWSE_DECK"),
        "SUBMIT_WORD": EventSpec(name="SUBMIT_WORD", payload_fields=["word"]),
        "HYDRATE_SUCCESS": EventSpec(name="HYDRATE_SUCCESS", payload_fields=["word_data"]),
        "HYDRATE_FAIL": EventSpec(name="HYDRATE_FAIL", payload_fields=["error"]),
        "CONFIRM_SAVE": EventSpec(name="CONFIRM_SAVE"),
        "CANCEL": EventSpec(name="CANCEL"),
        "SAVE_MANUAL": EventSpec(name="SAVE_MANUAL", payload_fields=["definition"]),
        "RETRY": EventSpec(name="RETRY"),
        "ABORT": EventSpec(name="ABORT"),
        "FLIP_CARD": EventSpec(name="FLIP_CARD"),
        "EXIT_REVIEW": EventSpec(name="EXIT_REVIEW"),
        "RATE_FORGOT": EventSpec(name="RATE_FORGOT"),
        "RATE_HARD": EventSpec(name="RATE_HARD"),
        "RATE_GOOD": EventSpec(name="RATE_GOOD"),
        "RATE_EASY": EventSpec(name="RATE_EASY"),
        "UNDO": EventSpec(name="UNDO"),
        "NEXT_CARD": EventSpec(name="NEXT_CARD"),
        "SESSION_COMPLETE": EventSpec(name="SESSION_COMPLETE"),
        "CLOSE_SESSION": EventSpec(name="CLOSE_SESSION"),
        "CRAM_AHEAD": EventSpec(name="CRAM_AHEAD"),
        "FLIP_CRAM": EventSpec(name="FLIP_CRAM"),
        "NEXT_CRAM": EventSpec(name="NEXT_CRAM"),
        "EXIT_CRAM": EventSpec(name="EXIT_CRAM"),
        "SAVE_PREFERENCES": EventSpec(name="SAVE_PREFERENCES", payload_fields=["reminder_hour"]),
        "CLOSE_SETTINGS": EventSpec(name="CLOSE_SETTINGS"),
        "CLOSE": EventSpec(name="CLOSE"),
        "DELETE_WORD": EventSpec(name="DELETE_WORD", payload_fields=["word_id"]),
    }

    return StatechartIR(
        machine_id="axioma_lexis_fsm",
        initial="idle",
        description="Formal XState v5 Statechart for Axioma Lexis Vocabulary Studio",
        states=states,
        events=events,
        context_schema={
            "active_word": None,
            "deck": [],
            "review_queue": [],
            "current_card_index": 0,
            "history_stack": []
        }
    )


def build_lexis_contract_ir() -> DualBoundaryContractIR:
    """Builds Contract IR defining Nouns and Verbs."""
    word_noun = NounContract(
        entity_name="Word",
        fields={
            "id": "string",
            "word": "string",
            "definition": "string",
            "part_of_speech": "string",
            "phonetic": "string",
            "example": "string",
            "status": "string",
            "interval_days": "number",
            "ease_factor": "number",
            "repetition_level": "number",
            "next_review": "number",
        },
        required_fields=["id", "word", "definition", "status", "interval_days", "ease_factor"]
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
    }

    return DualBoundaryContractIR(
        app_id="axioma_lexis",
        nouns={"Word": word_noun},
        verbs=verbs
    )
