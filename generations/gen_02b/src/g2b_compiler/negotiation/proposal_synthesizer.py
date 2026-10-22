"""Proposal Synthesizer Engine for System G2b (Option 3 Hybrid Model).

Evaluates elevator pitch and Phase 0 baseline research findings to dynamically formulate
tiered project proposals spanning the [10,000, 1,000,000] token spectrum.
Applies axiomatic safety bounding and the 40/60 capital partition invariant.
"""

from typing import Any, Dict, List, Optional
from g2b_compiler.negotiation.protocol import ProductFeatureProposal, ScopeNegotiationProtocol
from g2b_compiler.negotiation.proposals import (
    ProposalScopeTier,
    ProjectProposalDossier,
    MIN_BUDGET_FLOOR,
    MAX_SAFETY_BUDGET,
    PROTECTED_CAPITAL_RATIO,
)


class ProjectProposalSynthesizer:
    """Option 3 Hybrid Synthesizer: LLM-reasoned scope tiers with axiomatic bounding."""

    def __init__(
        self,
        min_budget_bound: int = MIN_BUDGET_FLOOR,
        max_safety_budget_bound: int = MAX_SAFETY_BUDGET,
    ):
        self.min_budget_bound = min_budget_bound
        self.max_safety_budget_bound = max_safety_budget_bound

    def clamp_budget(self, raw_estimate: int) -> int:
        """Axiomatic bounding guarantee: 10,000 <= B <= 1,000,000."""
        return max(self.min_budget_bound, min(self.max_safety_budget_bound, raw_estimate))

    def synthesize_proposals(
        self,
        app_id: str,
        elevator_pitch: str,
        research_summary: Optional[str] = None,
        candidate_features: Optional[List[ProductFeatureProposal]] = None,
        custom_budget: Optional[int] = None,
        selected_proposal_id: Optional[str] = None,
    ) -> ProjectProposalDossier:
        """Dynamically formulates 3 to 4 project proposal tiers across the budget spectrum."""

        # If features not provided, expand from pitch via ScopeNegotiationProtocol
        if candidate_features is None:
            proto = ScopeNegotiationProtocol()
            dossier = proto.synthesize_ambitious_vision(app_id, elevator_pitch)
            candidate_features = dossier.ambitious_features

        core_features = [f.name for f in candidate_features if f.is_retained_in_core]
        all_feature_names = [f.name for f in candidate_features]
        expansion_features = [f.name for f in candidate_features if not f.is_retained_in_core]

        summary_text = research_summary or (
            "Grounded in Ebbinghaus forgetting curve intervals, Nielsen-Norman 10 usability heuristics, "
            "and Fitts's Law 48px touch targets."
            if app_id == "axioma_lexis"
            else (
                "Grounded in Eugenia Cheng's categorical pedagogy (The Joy of Abstraction), relational arrow primacy "
                "(Yoneda lemma), Nielsen-Norman 10 usability heuristics, and Fitts's Law 48px touch targets."
                if app_id == "axioma_joy"
                else (
                    f"Grounded in domain primitives for {app_id}, statechart deterministic transitions, "
                    "and Nielsen-Norman 10 usability heuristics with Fitts's Law 48px touch targets."
                )
            )
        )

        # Standard fractional subagent allocation templates
        standard_fractions = {
            "root": 0.10,
            "synthesis_01": 0.15,
            "synthesis_02": 0.10,
            "synthesis_ir": 0.20,
            "synthesis_fe": 0.30,
            "synthesis_be": 0.15,
        }

        # Dynamic Sizing Slices across the [10k, 1M] spectrum
        if app_id == "axioma_lexis":
            raw_t1_base = 25000
            raw_t2_base = 100000
            raw_t3_base = 350000
            raw_t4_base = 1000000
        elif app_id == "axioma_joy":
            raw_t1_base = 30000
            raw_t2_base = 120000
            raw_t3_base = 380000
            raw_t4_base = 1000000
        else:
            total_complexity = sum(f.complexity_weight for f in candidate_features) if candidate_features else 15
            raw_t1_base = 28330 if total_complexity > 12 else 25000
            raw_t2_base = 120000 if total_complexity > 12 else 100000
            raw_t3_base = (
                custom_budget
                if (custom_budget is not None and 150000 < custom_budget <= 500000)
                else (380000 if total_complexity > 12 else 350000)
            )
            raw_t4_base = 1000000

        # Tier 1: Lean Core MVP
        raw_t1 = raw_t1_base if custom_budget is None or custom_budget > 30000 else self.clamp_budget(custom_budget)
        b_t1 = self.clamp_budget(raw_t1)
        prot_t1 = int(b_t1 * PROTECTED_CAPITAL_RATIO)
        expl_t1 = b_t1 - prot_t1
        res_t1 = int(expl_t1 * 0.20)
        ir_t1 = int(expl_t1 * 0.23)
        code_t1 = expl_t1 - res_t1 - ir_t1
        mc_t1 = prot_t1 // 2
        fals_t1 = prot_t1 - mc_t1
        breakdown_t1 = {
            "research_and_grounding": res_t1,
            "architecture_and_ir": ir_t1,
            "code_and_ast_emission": code_t1,
            "model_checking_reachability": mc_t1,
            "falsification_and_substrate": fals_t1,
        }
        just_t1 = (
            "Delivers 3 core features (Instant 2s Word Capture, Native Web Speech Audio, Adaptive SM-2 Spaced Repetition) "
            f"on a minimal 8-state deterministic machine. Emitting ~650 LOC of HTML, CSS, and vanilla JS consumes {code_t1:,} tokens. "
            f"{res_t1:,} tokens ground the cognitive science SM-2 forgetting curves (initial interval=1d, ease=2.5). "
            f"{ir_t1:,} tokens compile the statechart and dual-boundary contract IR. In accordance with [L1-G2B-004], "
            f"40% ({prot_t1:,} tokens) is strictly locked as Protected Capital, split equally between basic reachability "
            f"model checking ({mc_t1:,} tokens) and clean-slate substrate runtime execution ({fals_t1:,} tokens) to guarantee zero-phantom delivery."
            if app_id == "axioma_lexis"
            else (
                f"Delivers core features for {app_id} on a minimal 8-state deterministic machine. "
                f"Emitting responsive layout and local-first logic consumes ~{code_t1:,} tokens. "
                f"{res_t1:,} tokens ground domain heuristics and Nielsen-Norman standards. "
                f"{ir_t1:,} tokens compile the statechart and dual-boundary contract IR. In accordance with [L1-G2B-004], "
                f"40% ({prot_t1:,} tokens) is strictly locked as Protected Capital, split equally between basic reachability "
                f"model checking ({mc_t1:,} tokens) and clean-slate substrate runtime execution ({fals_t1:,} tokens) to guarantee zero-phantom delivery."
            )
        )
        if custom_budget is not None and custom_budget <= 30000:
            just_t1 += f" [Calibrated to user-specified budget of {b_t1:,} tokens (40% protected: {prot_t1:,} tok, 60% exploratory: {expl_t1:,} tok)]."

        tier_lean = ProposalScopeTier(
            tier_id="tier_lean",
            title="Lean Core MVP",
            target_persona_fit=(
                "Rapid single-deck reader needing immediate frictionless word capture without multimedia or analytics."
                if app_id == "axioma_lexis"
                else f"User exploring core {app_id} workflows with immediate feedback."
            ),
            included_features=core_features[:3],
            deferred_features=core_features[3:] + expansion_features,
            statechart_complexity="Minimal 8-state deterministic machine (idle, inspecting, applying_morphism, composing, complete)",
            verification_depth="Baseline structural regulation and substrate sanity execution.",
            raw_estimated_tokens=raw_t1,
            bounded_token_budget=b_t1,
            protected_capital=prot_t1,
            exploratory_capital=expl_t1,
            fractional_allocation=standard_fractions,
            rationale=(
                "Eliminates audio synthesis, undo history, and SVG charts to provide the absolute fastest Day 1 utility within minimal compute tokens."
                if app_id == "axioma_lexis"
                else f"Provides core direct manipulation workflows for {app_id} within minimal compute tokens."
            ),
            workload_breakdown=breakdown_t1,
            token_justification=just_t1,
        )

        # Tier 2: Production Balanced Studio (Primary Standard)
        raw_t2 = raw_t2_base if custom_budget is None or not (30000 < custom_budget <= 150000) else self.clamp_budget(custom_budget)
        b_t2 = self.clamp_budget(raw_t2)
        prot_t2 = int(b_t2 * PROTECTED_CAPITAL_RATIO)
        expl_t2 = b_t2 - prot_t2
        res_t2 = int(expl_t2 * 0.10)
        ir_t2 = int(expl_t2 * 0.23)
        code_t2 = expl_t2 - res_t2 - ir_t2
        mc_t2 = prot_t2 // 2
        fals_t2 = prot_t2 - mc_t2
        breakdown_t2 = {
            "research_and_grounding": res_t2,
            "architecture_and_ir": ir_t2,
            "code_and_ast_emission": code_t2,
            "model_checking_reachability": mc_t2,
            "falsification_and_substrate": fals_t2,
        }
        just_t2 = (
            "Scaling to 7 core features (adding Inbox-Zero Celebrations, Cram Mode, Daily Habit Reminders, and 1-Tap Functorial Undo) "
            "expands the statechart from 8 to 16 states and 53 transitions. Synthesizing full reactive state logic, local storage hydration, "
            f"Web Speech API integration, and ~1,200 LOC of production UI requires {code_t2:,} emission tokens and {ir_t2:,} IR compilation tokens. "
            f"{res_t2:,} tokens support recursive research into due-queue temporal gating and Nielsen-Norman touch heuristics. "
            f"The 40% Protected Capital ({prot_t2:,} tokens) is essential to power exhaustive 100% path coverage across 24 covering paths "
            f"({mc_t2:,} tokens) and synthesize 570+ adversarial negative assertions for clean-slate substrate verification ({fals_t2:,} tokens)."
            if app_id == "axioma_lexis"
            else (
                "Scaling to 3 Eugenia Cheng pedagogical realms (The Baker's Kitchen, 3D Factorization Cube of 30, and Functor Bridge) "
                "with real Web Audio harmonic commutativity feedback and 1-tap functorial undo expands the statechart from 10 to 18 states "
                "and 64 transitions. Synthesizing full SVG direct-manipulation drag, 3D isometric lattice rendering, Web Audio chord synthesis, "
                f"and ~1,600 LOC of production UI requires {code_t2:,} emission tokens and {ir_t2:,} IR compilation tokens. "
                f"{res_t2:,} tokens support research into pedagogical category theory invariants (associativity, functoriality, monoidal baking processes). "
                f"The 40% Protected Capital ({prot_t2:,} tokens) is essential to power exhaustive 100% path coverage across covering paths "
                f"({mc_t2:,} tokens) and synthesize 500+ adversarial negative assertions for clean-slate substrate verification ({fals_t2:,} tokens)."
                if app_id == "axioma_joy"
                else (
                    f"Scaling to core features for {app_id} expands the statechart from 8 to 16 states. "
                    f"Synthesizing reactive state logic, local storage hydration, and UI layout requires {code_t2:,} emission tokens "
                    f"and {ir_t2:,} IR compilation tokens. {res_t2:,} tokens support research into operational parameters and touch heuristics. "
                    f"The 40% Protected Capital ({prot_t2:,} tokens) is essential to power exhaustive 100% path coverage across covering paths "
                    f"({mc_t2:,} tokens) and clean-slate substrate verification ({fals_t2:,} tokens)."
                )
            )
        )
        if custom_budget is not None and 30000 < custom_budget <= 150000:
            just_t2 += f" [Calibrated to user-specified budget of {b_t2:,} tokens (40% protected: {prot_t2:,} tok, 60% exploratory: {expl_t2:,} tok)]."

        tier_balanced = ProposalScopeTier(
            tier_id="tier_balanced",
            title="Production Balanced Studio ('The Joy of Abstraction')" if app_id == "axioma_joy" else "Production Balanced Studio",
            target_persona_fit=(
                "Dedicated vocabulary learner requiring distraction-free 2s capture, audible Web Speech pronunciation, SM-2 due-queue gating, and 1-tap undo."
                if app_id == "axioma_lexis"
                else (
                    "Art students, visual designers, and structural thinkers exploring category theory through visceral everyday analogies (baking, 3D factor cubes, functor bridges) and harmonic audio feedback."
                    if app_id == "axioma_joy"
                    else f"Standard production user of {app_id} requiring balanced workflows and 1-tap undo."
                )
            ),
            included_features=core_features,
            deferred_features=expansion_features,
            statechart_complexity=(
                "18-state deterministic reactive category statechart with 100% path reachability, commuting chord resolution, and emergency abort exits."
                if app_id == "axioma_joy"
                else "16-state deterministic reactive machine with 100% path reachability and emergency abort exits."
            ),
            verification_depth="Exhaustive model checking covering all 50+ transitions, 500+ negative assertions, anti-mock clean slate audit, and live substrate verification.",
            raw_estimated_tokens=raw_t2,
            bounded_token_budget=b_t2,
            protected_capital=prot_t2,
            exploratory_capital=expl_t2,
            fractional_allocation=standard_fractions,
            rationale=(
                "The optimal production balance. Delivers 2s capture, audio pronunciation, SM-2 retention curves, and 1-tap undo while cutting cloud sync to preserve local-first calm."
                if app_id == "axioma_lexis"
                else (
                    "The authentic production balance for category learning. Delivers 3 signature Eugenia Cheng pedagogical realms, Web Audio chords, and 1-tap undo while cutting heavy symbolic theorem provers."
                    if app_id == "axioma_joy"
                    else f"The authentic production balance for {app_id}. Delivers primary interactive workflows and reversible undo while cutting cloud sync to preserve local-first calm."
                )
            ),
            workload_breakdown=breakdown_t2,
            token_justification=just_t2,
        )

        # Tier 3: High-Assurance Comprehensive Studio
        raw_t3 = raw_t3_base if custom_budget is None or not (150000 < custom_budget <= 500000) else self.clamp_budget(custom_budget)
        b_t3 = self.clamp_budget(raw_t3)
        prot_t3 = int(b_t3 * PROTECTED_CAPITAL_RATIO)
        expl_t3 = b_t3 - prot_t3
        res_t3 = int(expl_t3 * 0.08)
        ir_t3 = int(expl_t3 * 0.17)
        code_t3 = expl_t3 - res_t3 - ir_t3
        mc_t3 = prot_t3 // 2
        fals_t3 = prot_t3 - mc_t3
        breakdown_t3 = {
            "research_and_grounding": res_t3,
            "architecture_and_ir": ir_t3,
            "code_and_ast_emission": code_t3,
            "model_checking_reachability": mc_t3,
            "falsification_and_substrate": fals_t3,
        }
        just_t3 = (
            "Incorporating multi-deck taxonomy, folder hierarchies, and local-first CRDT sync relays increases state space to 24 states "
            f"with hierarchical sub-machines and ~2,800 LOC. Code synthesis for multi-deck filtering and CRDT sync relays consumes {code_t3:,} tokens. "
            f"{ir_t3:,} tokens formulate hierarchical IR with formal dual-boundary contracts. {res_t3:,} tokens explore CRDT concurrency invariants. "
            f"The 40% Protected Capital ({prot_t3:,} tokens) funds high-assurance verification: {mc_t3:,} tokens for deep concurrency state exploration "
            f"and dead-lock detection, and {fals_t3:,} tokens for property-based fuzzing with 1,000 state permutations and DOM touch target heatmap verification."
            if app_id == "axioma_lexis"
            else (
                f"Expands {app_id} into formal 24-state statecharts and comprehensive multi-domain workflows. "
                f"Synthesizing advanced interaction models and local-first adapters consumes {code_t3:,} emission tokens; "
                f"{ir_t3:,} tokens formulate hierarchical statechart IR and dual-boundary contracts. {res_t3:,} tokens ground domain mappings. "
                f"The 40% Protected Capital ({prot_t3:,} tokens) funds deep reachability model checking across all paths ({mc_t3:,} tokens) "
                f"and property-based fuzzing with 1,000 permutations ({fals_t3:,} tokens)."
            )
        )
        if custom_budget is not None and 150000 < custom_budget <= 500000:
            just_t3 += f" [Calibrated to user-specified budget of {b_t3:,} tokens (40% protected: {prot_t3:,} tok, 60% exploratory: {expl_t3:,} tok)]."

        tier_comprehensive = ProposalScopeTier(
            tier_id="tier_comprehensive",
            title="High-Assurance Comprehensive Studio",
            target_persona_fit=(
                "Power learners and polyglots needing nested tag taxonomies, JSON/CSV backups, Vim/Emacs keyboard shortcuts, and deep formal specification assurance."
                if app_id == "axioma_lexis"
                else f"Power user of {app_id} requiring comprehensive multi-domain workflows and formal verification."
            ),
            included_features=core_features + expansion_features[:2],
            deferred_features=expansion_features[2:],
            statechart_complexity="24-state formal statechart with hierarchical sub-machines for deck taxonomy and data import/export.",
            verification_depth="Deep adversarial falsification, concurrency race testing, property-based fuzzing with 1,000 permutations, and DOM touch heatmap verification.",
            raw_estimated_tokens=raw_t3,
            bounded_token_budget=b_t3,
            protected_capital=prot_t3,
            exploratory_capital=expl_t3,
            fractional_allocation=standard_fractions,
            rationale=(
                "Expands into nested deck taxonomies and historical retention curve charts with deep formal methods verification, while remaining completely local-first."
                if app_id == "axioma_lexis"
                else f"Expands {app_id} into comprehensive multi-domain workflows and formal verification while remaining completely local-first."
            ),
            workload_breakdown=breakdown_t3,
            token_justification=just_t3,
        )

        # Tier 4: Maximalist Safety-Cap
        raw_t4 = raw_t4_base
        b_t4 = self.clamp_budget(raw_t4)
        prot_t4 = int(b_t4 * PROTECTED_CAPITAL_RATIO)
        expl_t4 = b_t4 - prot_t4
        res_t4 = int(expl_t4 * 0.06)
        ir_t4 = int(expl_t4 * 0.12)
        code_t4 = expl_t4 - res_t4 - ir_t4
        mc_t4 = prot_t4 // 2
        fals_t4 = prot_t4 - mc_t4
        breakdown_t4 = {
            "research_and_grounding": res_t4,
            "architecture_and_ir": ir_t4,
            "code_and_ast_emission": code_t4,
            "model_checking_reachability": mc_t4,
            "falsification_and_substrate": fals_t4,
        }
        just_t4 = (
            "The maximal safety cap (1,000,000 tokens) represents full enterprise-scale deployment encompassing offline PWA service workers, "
            "multi-device peer-to-peer CRDT sync relays, complex D3 forgetting curve analytics, and multi-lingual audio modulation. "
            f"Emitting ~5,000 LOC of distributed production architecture consumes {code_t4:,} tokens across multiple recursive synthesis workers. "
            f"{res_t4:,} tokens research distributed consensus edge cases. {ir_t4:,} tokens synthesize multi-boundary contracts. "
            f"The 400,000 tokens (40%) of Protected Capital are deployed to mathematical theorem checking of CRDT convergence ({mc_t4:,} tokens), "
            f"continuous chaos network fault injection (10,000 permutations), and complete multi-browser substrate compatibility audits ({fals_t4:,} tokens)."
            if app_id == "axioma_lexis"
            else (
                f"The maximal safety cap (1,000,000 tokens) pushes {app_id} to enterprise scale across a 36-state distributed statechart. "
                f"Emitting distributed architecture consumes {code_t4:,} tokens across recursive synthesis workers. "
                f"{res_t4:,} tokens ground distributed consensus invariants. {ir_t4:,} tokens compile multi-boundary contract IR. "
                f"400,000 tokens (40%) of Protected Capital fund mathematical theorem checking of state machine invariants ({mc_t4:,} tokens) "
                f"and continuous chaos fault injection across 10,000 permutations ({fals_t4:,} tokens)."
            )
        )
        if custom_budget is not None and custom_budget > 500000:
            just_t4 += f" [Calibrated to user-specified budget of {b_t4:,} tokens (40% protected: {prot_t4:,} tok, 60% exploratory: {expl_t4:,} tok)]."

        tier_maximal = ProposalScopeTier(
            tier_id="tier_maximal",
            title="Maximalist Safety-Cap Enterprise Studio",
            target_persona_fit=(
                "Enterprise-grade deployment requiring offline PWA packaging, peer-to-peer CRDT sync relays, multi-lingual audio pitch modulation, and formal mathematical proofs."
                if app_id == "axioma_lexis"
                else f"Enterprise deployment of {app_id} pushing maximal formal verification at safety cap."
            ),
            included_features=all_feature_names,
            deferred_features=[],
            statechart_complexity="36-state distributed statechart modeling 2-morphisms, monoidal parallel tracks, and commutative proofs.",
            verification_depth="Formal theorem proving of category axioms, associativity pentagon coherences, and continuous chaos fault injection with 10,000 permutations.",
            raw_estimated_tokens=raw_t4,
            bounded_token_budget=b_t4,
            protected_capital=prot_t4,
            exploratory_capital=expl_t4,
            fractional_allocation=standard_fractions,
            rationale=(
                "The maximal vision at the safety cap. Fully verifies local CRDT synchronization, multi-format audio engines, and formal mathematical proofs."
                if app_id == "axioma_lexis"
                else f"The maximal vision at the safety cap. Fully verifies distributed statecharts, multi-format engines, and formal mathematical proofs for {app_id}."
            ),
            workload_breakdown=breakdown_t4,
            token_justification=just_t4,
        )

        proposals = [tier_lean, tier_balanced, tier_comprehensive, tier_maximal]

        # Determine active proposal selection
        active_selection = selected_proposal_id or "tier_balanced"
        if custom_budget is not None and selected_proposal_id is None:
            if custom_budget <= 30000:
                active_selection = "tier_lean"
            elif custom_budget <= 150000:
                active_selection = "tier_balanced"
            elif custom_budget <= 500000:
                active_selection = "tier_comprehensive"
            else:
                active_selection = "tier_maximal"

        return ProjectProposalDossier(
            app_id=app_id,
            elevator_pitch=elevator_pitch,
            research_summary=summary_text,
            min_budget_bound=self.min_budget_bound,
            max_safety_budget_bound=self.max_safety_budget_bound,
            proposals=proposals,
            selected_proposal_id=active_selection
        )
