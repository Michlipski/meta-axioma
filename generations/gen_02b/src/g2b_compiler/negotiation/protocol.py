"""Scope Negotiation Protocol: Ambitious Discovery & Deliberate Scope-Cutting for System G2b."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ProductFeatureProposal:
    feature_id: str
    name: str
    description: str
    category: str  # "CORE_JTBD" | "ERGONOMIC_ENHANCEMENT" | "ADVANCED_EXPANSION" | "HABIT_LOOP"
    complexity_weight: int  # 1 to 5
    is_ambitious_candidate: bool = True
    is_retained_in_core: bool = False
    cut_rationale: Optional[str] = None


@dataclass
class AmbitiousScopeDossier:
    app_id: str
    elevator_pitch: str
    expanded_persona: str
    daily_user_workflow: str
    ambitious_features: List[ProductFeatureProposal]
    estimated_tokens_full_scope: int
    estimated_tokens_lean_scope: int


class ScopeNegotiationProtocol:
    """Orchestrates Phase 0-A (Ambitious Discovery) to Phase 0-C (Scope-Cut Lock)."""

    def synthesize_ambitious_lexis_vision(self, elevator_pitch: str) -> AmbitiousScopeDossier:
        """Step 1 (Phase 0-A): Expands elevator pitch into the maximal viable vision across cognitive science & market benchmarks."""
        features = [
            ProductFeatureProposal(
                feature_id="FEAT-CAPTURE-2S",
                name="Instant 2-Second Word Capture",
                description="Type unfamiliar word -> instant dictionary definition, IPA phonetics, part-of-speech, and contextual sentence.",
                category="CORE_JTBD",
                complexity_weight=2,
                is_retained_in_core=True
            ),
            ProductFeatureProposal(
                feature_id="FEAT-SPEECH-AUDIO",
                name="Native Web Speech Audio Pronunciation",
                description="1-tap audible US/UK speech synthesis using real browser Web Speech API (zero mock).",
                category="CORE_JTBD",
                complexity_weight=2,
                is_retained_in_core=True
            ),
            ProductFeatureProposal(
                feature_id="FEAT-SRS-PACED",
                name="Adaptive SM-2 Spaced Repetition (Due-Queue Gating)",
                description="Strict spacing effect: words only enter active review when next_review <= now. Immediate re-review forbidden (AX-MEM-001).",
                category="CORE_JTBD",
                complexity_weight=3,
                is_retained_in_core=True
            ),
            ProductFeatureProposal(
                feature_id="FEAT-MILESTONE-CLOSURE",
                name="Inbox-Zero Milestone Celebration Card",
                description="When due queue hits 0, display explicit completion celebration card with time-to-next-card countdown (AX-MEM-002).",
                category="CORE_JTBD",
                complexity_weight=2,
                is_retained_in_core=True
            ),
            ProductFeatureProposal(
                feature_id="FEAT-CRAM-MODE",
                name="Unrestricted Practice / Cram Mode",
                description="Allow quizzing un-due cards ahead of schedule without corrupting SM-2 intervals (AX-MEM-008).",
                category="ERGONOMIC_ENHANCEMENT",
                complexity_weight=2,
                is_retained_in_core=True
            ),
            ProductFeatureProposal(
                feature_id="FEAT-CALM-HABIT",
                name="Calm Daily Habit Loop Reminders",
                description="Opt-in, once-daily browser notification when cards are due. Zero spam (AX-MEM-005).",
                category="HABIT_LOOP",
                complexity_weight=2,
                is_retained_in_core=True
            ),
            ProductFeatureProposal(
                feature_id="FEAT-FUNCTORIAL-UNDO",
                name="Universal 1-Tap Rating Undo (Cmd+Z)",
                description="Functorial history rollback restoring exact preceding card and SM-2 parameters on accidental rating click (AX-MEM-004).",
                category="ERGONOMIC_ENHANCEMENT",
                complexity_weight=2,
                is_retained_in_core=True
            ),
            # Ambitious expansions to be evaluated for deliberate cutting:
            ProductFeatureProposal(
                feature_id="FEAT-MULTI-DECK",
                name="Multi-Deck Taxonomy & Folder Hierarchy",
                description="Create nested decks, tags, and category folders for multiple languages.",
                category="ADVANCED_EXPANSION",
                complexity_weight=4,
                is_retained_in_core=False,
                cut_rationale="Adds cognitive navigation friction. The core pitch emphasizes distraction-free single-stream focus."
            ),
            ProductFeatureProposal(
                feature_id="FEAT-CLOUD-SYNC",
                name="Cloud Account Sync & Multi-Device CRDT Relay",
                description="Remote account login, JWT auth, and cloud database replication.",
                category="ADVANCED_EXPANSION",
                complexity_weight=5,
                is_retained_in_core=False,
                cut_rationale="Violates local-first simplicity. Local-first storage + JSON export provides privacy and reliability without cloud servers."
            ),
            ProductFeatureProposal(
                feature_id="FEAT-ANALYTICS-CHARTS",
                name="Complex Retention Analytics & Forgetting Curve Charts",
                description="Multi-axis D3 charts graphing historical retention rates, ease factor decay, and hourly memory heatmaps.",
                category="ADVANCED_EXPANSION",
                complexity_weight=4,
                is_retained_in_core=False,
                cut_rationale="Excessive cognitive overhead. Simple deck count and due counter are sufficient for the daily reading workflow."
            )
        ]

        return AmbitiousScopeDossier(
            app_id="axioma_lexis",
            elevator_pitch=elevator_pitch,
            expanded_persona="The Focus Learner & Reader: Captures words in 2 seconds while reading on desktop/mobile and reviews them in low-pressure bite-sized daily sessions.",
            daily_user_workflow="1. Encounter unfamiliar word while reading -> 2. Paste or type into capture bar -> 3. Instant auto-hydrated definition and pronunciation -> 4. Word added to deck (due immediately) -> 5. Daily 3-5 minute spaced review with 1-tap undo -> 6. Inbox zero celebration card.",
            ambitious_features=features,
            estimated_tokens_full_scope=85000,
            estimated_tokens_lean_scope=38000
        )

    def synthesize_generic_vision(self, app_id: str, elevator_pitch: str) -> AmbitiousScopeDossier:
        """Step 1 (Phase 0-A): Generically expands any elevator pitch into ambitious discovery features and deliberate cuts."""
        features = [
            ProductFeatureProposal(
                feature_id="FEAT-CORE-WORKSPACE",
                name="Interactive Direct-Manipulation Workspace",
                description=f"Primary visual interaction canvas implementing core operations for {app_id}.",
                category="CORE_JTBD",
                complexity_weight=3,
                is_retained_in_core=True
            ),
            ProductFeatureProposal(
                feature_id="FEAT-STATE-DETERMINISM",
                name="Deterministic State Machine Transitions",
                description="Rigid finite state automata with zero-ambiguity transitions and error boundaries.",
                category="CORE_JTBD",
                complexity_weight=2,
                is_retained_in_core=True
            ),
            ProductFeatureProposal(
                feature_id="FEAT-SENSORY-FEEDBACK",
                name="Rich Sensory & Tactile Feedback",
                description="Visual and acoustic cues indicating valid actions, state transformations, and completions.",
                category="ERGONOMIC_ENHANCEMENT",
                complexity_weight=2,
                is_retained_in_core=True
            ),
            ProductFeatureProposal(
                feature_id="FEAT-FUNCTORIAL-UNDO",
                name="Functorial Reversible History (Cmd+Z)",
                description="1-tap reversible time-travel history restoring exact preceding state snapshot (L1-002).",
                category="ERGONOMIC_ENHANCEMENT",
                complexity_weight=2,
                is_retained_in_core=True
            ),
            ProductFeatureProposal(
                feature_id="FEAT-LOCAL-FIRST-STORAGE",
                name="Decoupled Local-First Persistence",
                description="Pristine client-side state persistence without external telemetry or mock fixtures (L1-011_3).",
                category="CORE_JTBD",
                complexity_weight=2,
                is_retained_in_core=True
            ),
            ProductFeatureProposal(
                feature_id="FEAT-EXCEPTION-ENCLAVES",
                name="Demarcated Exception Enclaves & Input Validation",
                description="Zero-trust input boundaries preventing malformed or out-of-domain payloads (L1-016).",
                category="CORE_JTBD",
                complexity_weight=2,
                is_retained_in_core=True
            ),
            # Ambitious expansions evaluated for deliberate cutting:
            ProductFeatureProposal(
                feature_id="FEAT-CLOUD-SYNC-EXP",
                name="Cloud Account Sync & Remote Multi-Tenant Relay",
                description="Cloud user authentication, OAuth credentials, and remote database replication.",
                category="ADVANCED_EXPANSION",
                complexity_weight=5,
                is_retained_in_core=False,
                cut_rationale="Violates local-first simplicity. Local-first storage + JSON export provides privacy and reliability without cloud servers."
            ),
            ProductFeatureProposal(
                feature_id="FEAT-COMPLEX-ANALYTICS",
                name="Complex Historical Analytics & Multi-Axis Telemetry",
                description="D3 analytics dashboards charting long-term usage telemetry and heatmaps.",
                category="ADVANCED_EXPANSION",
                complexity_weight=4,
                is_retained_in_core=False,
                cut_rationale="Adds cognitive navigation friction. Preserves focused direct manipulation with zero bloat."
            )
        ]

        return AmbitiousScopeDossier(
            app_id=app_id,
            elevator_pitch=elevator_pitch,
            expanded_persona=f"The Focused User of {app_id}: Direct manipulation and immediate cognitive value without unnecessary complexity.",
            daily_user_workflow="1. Launch application -> 2. Inspect active canvas -> 3. Execute core state transition -> 4. Receive instant feedback -> 5. Functorial undo if needed -> 6. Session completion.",
            ambitious_features=features,
            estimated_tokens_full_scope=95000,
            estimated_tokens_lean_scope=40000
        )

    def synthesize_ambitious_joy_vision(self, elevator_pitch: str) -> AmbitiousScopeDossier:
        """Step 1 (Phase 0-A): Expands category theory educational pitch into Eugenia Cheng's visceral pedagogical model."""
        features = [
            ProductFeatureProposal(
                feature_id="FEAT-DIRECT-CANVAS",
                name="Direct Manipulation Category Canvas",
                description="Tactile SVG canvas for drawing objects and directional morphisms with visual arrowheads and snapping.",
                category="CORE_JTBD",
                complexity_weight=3,
                is_retained_in_core=True
            ),
            ProductFeatureProposal(
                feature_id="FEAT-CULINARY-REALM",
                name="The Baker's Kitchen Category",
                description="Eugenia Cheng's signature baking domain: Flour + Sugar + Eggs -> Batter -> Cake, contrasting sequential composition and parallel ingredient prep (AX-CAT-005).",
                category="CORE_JTBD",
                complexity_weight=2,
                is_retained_in_core=True
            ),
            ProductFeatureProposal(
                feature_id="FEAT-COMMUTING-HARMONY",
                name="Interactive Commutative Loop Engine & Audio Chimes",
                description="Detects commuting paths, illuminates the commutative face with golden particle flow, and synthesizes consonant Web Audio chords (AX-CAT-003).",
                category="CORE_JTBD",
                complexity_weight=3,
                is_retained_in_core=True
            ),
            ProductFeatureProposal(
                feature_id="FEAT-FACTOR-CUBE-30",
                name="Cheng's 3D Factorization Cube of 30",
                description="Rotatable 3D isometric lattice diagram of divisors of 30 (1, 2, 3, 5, 6, 10, 15, 30) demonstrating prime factor generators and poset categories.",
                category="CORE_JTBD",
                complexity_weight=3,
                is_retained_in_core=True
            ),
            ProductFeatureProposal(
                feature_id="FEAT-FUNCTOR-BRIDGE",
                name="Structure-Preserving Functor Analogy Bridge",
                description="Dual-pane canvas mapping Culinary World -> Geometric Art World, verifying F(g o f) = F(g) o F(f) across domains (AX-CAT-004).",
                category="CORE_JTBD",
                complexity_weight=3,
                is_retained_in_core=True
            ),
            ProductFeatureProposal(
                feature_id="FEAT-DUAL-CATEGORY",
                name="Dual Opposite Category Inspection (C^op)",
                description="1-tap morphism arrow reversal demonstrating duality and how flipping all relationships yields the dual category (AX-CAT-001).",
                category="ERGONOMIC_ENHANCEMENT",
                complexity_weight=2,
                is_retained_in_core=True
            ),
            ProductFeatureProposal(
                feature_id="FEAT-FUNCTORIAL-UNDO",
                name="Functorial Reversible History (Cmd+Z)",
                description="Reversible time-travel stack restoring exact preceding canvas snapshot on any action (L1-002).",
                category="ERGONOMIC_ENHANCEMENT",
                complexity_weight=2,
                is_retained_in_core=True
            ),
            ProductFeatureProposal(
                feature_id="FEAT-LOCAL-FIRST-SYNC",
                name="Decoupled Local-First Persistence & Export",
                description="Pristine client-side state storage in localStorage with JSON export/import (L1-011_3).",
                category="CORE_JTBD",
                complexity_weight=2,
                is_retained_in_core=True
            ),
            ProductFeatureProposal(
                feature_id="FEAT-EXCEPTION-ENCLAVES",
                name="Demarcated Type Mismatch Enclaves",
                description="Gentle visual feedback when attempting non-composable morphisms cod(f) != dom(g) (L1-016).",
                category="CORE_JTBD",
                complexity_weight=2,
                is_retained_in_core=True
            ),
            # Deliberately deferred expansions:
            ProductFeatureProposal(
                feature_id="FEAT-P2P-COLLAB",
                name="Peer-to-Peer Real-Time Collaborative Canvas",
                description="WebRTC data channels and CRDT multi-user whiteboard for live synchronous drawing.",
                category="ADVANCED_EXPANSION",
                complexity_weight=5,
                is_retained_in_core=False,
                cut_rationale="Adds complex networking dependencies and signaling servers. Local-first direct manipulation provides calm, focused personal learning."
            ),
            ProductFeatureProposal(
                feature_id="FEAT-THEOREM-PROVER",
                name="Symbolic Coq/Lean Theorem Prover Backend",
                description="Exporting commuting diagrams to formal Coq/Lean interactive proof assistant code.",
                category="ADVANCED_EXPANSION",
                complexity_weight=5,
                is_retained_in_core=False,
                cut_rationale="Contradicts Eugenia Cheng's foundational pedagogical mission: teaching category theory to arts students by eliminating intimidating formal symbolic overhead."
            )
        ]

        return AmbitiousScopeDossier(
            app_id="axioma_joy",
            elevator_pitch=elevator_pitch,
            expanded_persona="The Visceral Structural Thinker & Creative Visual Learner: Art students, designers, and visual learners exploring relational mathematics, structural reasoning, and category theory without rote arithmetic or notation dread.",
            daily_user_workflow="1. Launch studio -> 2. Explore signature Baker's Kitchen -> 3. Draw arrows and compose paths -> 4. Hear consonant chord resolution when diagrams commute -> 5. Rotate 3D Factorization Cube of 30 -> 6. Inspect Functor Bridge across worlds -> 7. Functorial undo if needed -> 8. Local backup.",
            ambitious_features=features,
            estimated_tokens_full_scope=110000,
            estimated_tokens_lean_scope=45000
        )

    def synthesize_ambitious_vision(self, app_id: str, elevator_pitch: str) -> AmbitiousScopeDossier:
        """Generic entrypoint dispatching by application domain ID."""
        if app_id == "axioma_lexis":
            return self.synthesize_ambitious_lexis_vision(elevator_pitch)
        if app_id == "axioma_joy":
            return self.synthesize_ambitious_joy_vision(elevator_pitch)
        return self.synthesize_generic_vision(app_id, elevator_pitch)


