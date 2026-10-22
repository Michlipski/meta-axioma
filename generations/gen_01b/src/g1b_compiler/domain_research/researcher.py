"""Domain Baseline Research Engine for System G1b.

Executes Phase 0 of the compilation pipeline:
1. Classifies the natural language intent / Semantic IR into a concrete Domain Archetype.
2. Ingests empirical cognitive science axioms, heuristics, and table-stakes requirements.
3. Audits the candidate specification and statechart against domain non-negotiables.
4. Enforces baseline standards to eliminate the 'Vacuum Synthesis Trap'.
"""

from typing import Dict, List, Optional, Set
from g1b_compiler.domain_research.models import (
    DomainArchetype,
    DomainBaselineReport,
    DomainBaselineViolation,
    DomainAxiom,
    DomainHeuristic,
)
from g1b_compiler.domain_research.benchmarks import (
    MEMORIZATION_AXIOMS,
    MEMORIZATION_HEURISTICS,
    MEMORIZATION_TABLE_STAKES,
    PUZZLE_AXIOMS,
    PUZZLE_TABLE_STAKES,
)
from g1b_compiler.ir.semantic_ir import SemanticDomainIR
from g1b_compiler.ir.statechart_ir import StatechartIR


class DomainBaselineResearcher:
    """Automated domain baseline research and verification engine (Phase 0)."""

    def classify_archetype(self, semantic_ir: SemanticDomainIR) -> DomainArchetype:
        """Classifies the domain archetype from semantic intent signals."""
        signals = " ".join([
            semantic_ir.app_id.lower(),
            semantic_ir.title.lower(),
            semantic_ir.tagline.lower(),
            semantic_ir.persona.lower(),
            semantic_ir.jtbd_summary.lower(),
            " ".join(c.name.lower() + " " + c.description.lower() for c in semantic_ir.capabilities)
        ])

        mem_keywords = ["vocab", "lexis", "flashcard", "spaced repetition", "srs", "memorization", "memory", "anki", "card"]
        puzzle_keywords = ["crossword", "puzzle", "cryptic", "sudoku", "grid", "cruciverbalist"]
        kanban_keywords = ["kanban", "workspace", "task", "project", "backlog", "board"]

        if any(k in signals for k in mem_keywords):
            return DomainArchetype.MEMORIZATION_SRS
        elif any(k in signals for k in puzzle_keywords):
            return DomainArchetype.CONSTRAINT_SOLVER_PUZZLE
        elif any(k in signals for k in kanban_keywords):
            return DomainArchetype.PRODUCTIVITY_KANBAN
        else:
            return DomainArchetype.GENERAL_UTILITY

    def analyze_and_audit(
        self,
        semantic_ir: SemanticDomainIR,
        statechart_ir: StatechartIR,
        strict: bool = True
    ) -> DomainBaselineReport:
        """Performs Phase 0 Domain Baseline Research and audits specification compliance."""
        archetype = self.classify_archetype(semantic_ir)

        missing_table_stakes: List[str] = []
        anti_patterns_detected: List[str] = []
        recommendations: List[str] = []
        applicable_axioms: List[DomainAxiom] = []
        heuristics: List[DomainHeuristic] = []
        table_stakes_audited: List[str] = []

        all_state_names = self._gather_all_state_names(statechart_ir)
        all_event_names = set(statechart_ir.events.keys())
        for node in statechart_ir.states.values():
            all_event_names.update(node.on.keys())
            if node.states:
                for sub in node.states.values():
                    all_event_names.update(sub.on.keys())

        cap_names = [c.name.lower() for c in semantic_ir.capabilities]
        cap_descriptions = [c.description.lower() for c in semantic_ir.capabilities]

        if archetype == DomainArchetype.MEMORIZATION_SRS:
            applicable_axioms = list(MEMORIZATION_AXIOMS)
            heuristics = list(MEMORIZATION_HEURISTICS)
            table_stakes_audited = list(MEMORIZATION_TABLE_STAKES)

            # 1. Audit Due-Queue Gating (AX-MEM-001)
            has_due_queue = any(
                "due" in c or "srs" in c or "spaced" in c
                for c in cap_names + cap_descriptions
            ) or any("due" in s for s in all_state_names)
            if not has_due_queue:
                missing_table_stakes.append("due_queue_gating")
                recommendations.append(
                    "[AX-MEM-001 Violation] Memorization apps must gate reviews strictly by due timestamp "
                    "(next_review <= now) to prevent infinite loop false fluency."
                )

            # 2. Audit Completion Milestone (AX-MEM-002)
            has_completion = any(
                term in s for s in all_state_names
                for term in ["complete", "completed", "all_caught_up", "milestone"]
            )
            if not has_completion:
                missing_table_stakes.append("completion_milestone")
                recommendations.append(
                    "[AX-MEM-002 Violation] Spaced repetition sessions must terminate in an explicit "
                    "'Session Completed / All Caught Up' milestone when the due queue reaches zero."
                )

            # 3. Audit Habit Loop / Notification Capability (AX-MEM-005)
            has_notif = any(
                "notif" in c or "remind" in c or "habit" in c
                for c in cap_names + cap_descriptions
            ) or any("notif" in e for e in [ev.lower() for ev in all_event_names])
            if not has_notif:
                missing_table_stakes.append("habit_notification_capability")
                recommendations.append(
                    "[AX-MEM-005 Violation] Memorization apps must include opt-in daily habit reminders "
                    "(e.g. Web Notification API or local notification prompt) to prevent 90%+ habit churn."
                )

            # 4. Audit Functorial Undo (AX-MEM-004)
            has_undo = "UNDO" in all_event_names or any("undo" in c for c in cap_names)
            if not has_undo:
                missing_table_stakes.append("reversible_undo")
                recommendations.append(
                    "[AX-MEM-004 Violation] Spaced repetition rating transitions must feature a 1-tap reversible "
                    "undo to prevent accidental taps from corrupting long-term review schedules."
                )

            # 5. Audit Dual-Track Cram/Practice Mode (AX-MEM-008)
            has_cram = any(
                term in s for s in all_state_names for term in ["cram", "practice", "browse"]
            ) or any("cram" in c or "practice" in c for c in cap_names)
            if not has_cram:
                missing_table_stakes.append("cram_or_practice_mode")
                recommendations.append(
                    "[AX-MEM-008 Violation] A distinct non-punitive cram/practice mode is required for users "
                    "who want to study ahead without disrupting SM-2 intervals."
                )

        elif archetype == DomainArchetype.CONSTRAINT_SOLVER_PUZZLE:
            applicable_axioms = list(PUZZLE_AXIOMS)
            table_stakes_audited = list(PUZZLE_TABLE_STAKES)

            has_dissector = any("dissect" in s for s in all_state_names)
            if not has_dissector:
                missing_table_stakes.append("clue_anatomy_dissector")
                recommendations.append("Cryptic puzzle studios require an interactive clue anatomy dissector.")

        passed = len(missing_table_stakes) == 0

        if strict and not passed:
            raise DomainBaselineViolation(
                f"[Phase 0 Domain Baseline Audit Failed] Archetype: '{archetype.value}'. "
                f"Missing {len(missing_table_stakes)} non-negotiable table-stakes: {', '.join(missing_table_stakes)}.\n"
                + "\n".join(f" - {r}" for r in recommendations)
            )

        return DomainBaselineReport(
            app_id=semantic_ir.app_id,
            archetype=archetype,
            passed=passed,
            table_stakes_audited=table_stakes_audited,
            missing_table_stakes=missing_table_stakes,
            anti_patterns_detected=anti_patterns_detected,
            applicable_axioms=applicable_axioms,
            heuristics=heuristics,
            recommendations=recommendations,
        )

    def _gather_all_state_names(self, statechart_ir: StatechartIR) -> Set[str]:
        """Flattens all root and composite state names for auditing."""
        names: Set[str] = set()
        for s_id, node in statechart_ir.states.items():
            names.add(s_id.lower())
            if node.states:
                for sub_id in node.states.keys():
                    names.add(f"{s_id}.{sub_id}".lower())
                    names.add(sub_id.lower())
        return names
