"""Domain Benchmarks and Axiom Catalogs for System G1b.

Aggregates empirical research, cognitive science foundations, competitive product analysis,
and formal domain axioms across software archetypes.
"""

from typing import Dict, List
from g1b_compiler.domain_research.models import DomainArchetype, DomainAxiom, DomainHeuristic


# ==============================================================================
# MEMORIZATION & SPACED REPETITION (SRS) BENCHMARK CATALOG
# ==============================================================================

MEMORIZATION_AXIOMS: List[DomainAxiom] = [
    DomainAxiom(
        axiom_id="AX-MEM-001",
        name="Due-Queue Temporal Isolation",
        formal_rule="Q_due(t) = { c in Deck | c.next_review <= t and not c.suspended }; Forall c in Session, c in Q_due",
        description="Cards scheduled in the future must never appear in the primary review queue. Immediate re-review is isolated to cram/practice mode.",
        is_blocking=True
    ),
    DomainAxiom(
        axiom_id="AX-MEM-002",
        name="Completion Closure & Inbox Zero",
        formal_rule="|Q_due(t)| == 0 ==> State = SessionCompleted and Action(NEXT_CARD) = INVALID",
        description="Exhausting the due queue must transition to an explicit completion milestone. Infinite deck restarts are forbidden.",
        is_blocking=True
    ),
    DomainAxiom(
        axiom_id="AX-MEM-003",
        name="Active Retrieval Isolation",
        formal_rule="Render(PromptState) intersection AnswerPayload == empty_set",
        description="Prompt state must expose only the target stimulus (headword). Definition and examples remain hidden until explicit flip.",
        is_blocking=True
    ),
    DomainAxiom(
        axiom_id="AX-MEM-004",
        name="Functorial Rating Reversibility",
        formal_rule="Forall k in Ratings, Undo(ApplyRating(c, k)) == c_prev",
        description="Accidental card rating transitions must be 1-tap reversible, restoring exact interval, ease factor, and queue position.",
        is_blocking=True
    ),
    DomainAxiom(
        axiom_id="AX-MEM-005",
        name="Calm Habit Loop & Notification Hygiene",
        formal_rule="DispatchNotification(t) ==> OptIn == True and |Q_due(t)| > 0 and (t - t_last) >= 20h",
        description="Opt-in daily reminders sent at user-preferred study hour only when due cards exist. Suppressed when 0 cards due.",
        is_blocking=True
    ),
    DomainAxiom(
        axiom_id="AX-MEM-006",
        name="Cognitive Bounding & Backlog Shield",
        formal_rule="|ActiveSessionQueue| <= MaxDailyBatch (K <= 20)",
        description="Daily active sessions are capped to at most 20 cards per batch to prevent review backlog paralysis ('Anki Hell').",
        is_blocking=False
    ),
    DomainAxiom(
        axiom_id="AX-MEM-007",
        name="Frictionless Auto-Enrichment Hydration",
        formal_rule="Input(Headword) --(<2s)--> Hydrate(Definition, IPA, Audio, Example)",
        description="Word capture requires only one field (the word), auto-enriching phonetics, definitions, and audio in under 2 seconds.",
        is_blocking=True
    ),
    DomainAxiom(
        axiom_id="AX-MEM-008",
        name="Dual-Track Study Modes",
        formal_rule="Modes = { Mode_SpacedDue (algorithmically paced), Mode_CramPractice (unrestricted exploratory) }",
        description="Clean separation between algorithmically paced spaced reviews and exploratory cramming without distorting SM-2 schedules.",
        is_blocking=True
    ),
]

MEMORIZATION_HEURISTICS: List[DomainHeuristic] = [
    DomainHeuristic(
        title="Due-Queue Pacing vs. Infinite Loops",
        category="what_works",
        description="Pacing cards strictly by due timestamps produces real synaptic spacing. Locking the session when done rewards user with completion closure.",
        impact_level="critical"
    ),
    DomainHeuristic(
        title="Calm Opt-In Notifications",
        category="what_works",
        description="A once-daily gentle reminder at the user's preferred time (e.g. 8:00 AM) that deep-links directly into card #1 prevents churn.",
        impact_level="critical"
    ),
    DomainHeuristic(
        title="Zero-Friction 1-Word Capture",
        category="what_works",
        description="Auto-hydrating definitions, IPA phonetics, and audio pronunciation keeps card capture under 2s, eliminating authoring drop-off.",
        impact_level="high"
    ),
    DomainHeuristic(
        title="1-Tap Undo for Accidental Ratings",
        category="what_works",
        description="Accidental swipes or mis-clicks can be reversed instantly with Cmd+Z without scheduling a card 2 months out.",
        impact_level="high"
    ),
    DomainHeuristic(
        title="Infinite Deck Loop Anti-Pattern",
        category="what_fails",
        description="Allowing immediate re-review of the entire deck immediately after rating provides false fluency (recognition) without long-term retention.",
        impact_level="critical"
    ),
    DomainHeuristic(
        title="Missing Habit Loop Anti-Pattern",
        category="what_fails",
        description="Having zero notification or reminder prompts causes 90%+ of memory app users to forget to open the app after day 2.",
        impact_level="critical"
    ),
    DomainHeuristic(
        title="Artificial Countdown Dwell Timers",
        category="what_fails",
        description="Forcing users to wait 10 seconds before flipping enrages experienced users and destroys focus flow.",
        impact_level="high"
    ),
    DomainHeuristic(
        title="Hyper-Granular Rating Scales",
        category="what_fails",
        description="Using 6 rating buttons (SuperMemo 0-5) introduces decision fatigue. 3 to 4 buttons (Again/Hard/Good/Easy) is the proven cognitive sweet spot.",
        impact_level="moderate"
    ),
]

MEMORIZATION_TABLE_STAKES: List[str] = [
    "due_queue_gating",               # Must gate active review cards by due timestamp
    "completion_milestone",           # Must have a distinct session completion/celebration state
    "habit_notification_capability",  # Must include reminder/notification capability
    "reversible_undo",                # Must include 1-tap undo for rating rollback
    "cram_or_practice_mode",          # Must provide an explicit practice/cram mode for un-due cards
]


# ==============================================================================
# CONSTRAINT SOLVER & PUZZLE BENCHMARK CATALOG
# ==============================================================================

PUZZLE_AXIOMS: List[DomainAxiom] = [
    DomainAxiom(
        axiom_id="AX-SOLV-001",
        name="Grid-Clue Bijective Topology",
        formal_rule="Forall run in Grid.WordSlots (length >= 2) <==> Exists! clue in Clues",
        description="Every contiguous word slot in the grid must map bijectively to an exact clue number, direction, length, and entry.",
        is_blocking=True
    ),
    DomainAxiom(
        axiom_id="AX-SOLV-002",
        name="Character Permutation & Fodder Exactness",
        formal_rule="Clue.Type == 'hidden' ==> Answer in Clean(Surface); Clue.Type == 'anagram' ==> Sorted(Fodder) == Sorted(Answer)",
        description="Cryptic wordplay mechanics must strictly satisfy character-level substring and anagram letter equalities.",
        is_blocking=True
    ),
]

PUZZLE_TABLE_STAKES: List[str] = [
    "grid_clue_bijective_topology",
    "character_exactness_verification",
    "soft_keypad_navigation",
    "clue_anatomy_dissector",
]
