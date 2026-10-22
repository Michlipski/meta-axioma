"""Multi-Tier Interlocking Gate for System G2b.

Enforces [L1-G2B-001] (Multi-Tier Interlocking Conjunction) and [L1-G2B-002] (Stateful Human Overrides).
"""

from typing import Any, Dict, List, Optional
from g2b_compiler.matrix.models import MultiTierAuditResult, MultiTierAxiomViolation
from g2b_compiler.matrix.heuristics import UsabilityHeuristicAuditor
from g2b_compiler.overrides.registry import StatefulOverrideRegistry
from g2b_compiler.ir.semantic_ir import SemanticDomainIR
from g2b_compiler.ir.statechart_ir import StatechartIR


class MultiTierInterlockingGate:
    """Evaluates the conjunction of Structural, Usability, and Domain Benchmarks."""

    def __init__(self, override_registry: Optional[StatefulOverrideRegistry] = None):
        self.auditor = UsabilityHeuristicAuditor()
        self.registry = override_registry or StatefulOverrideRegistry()

    def audit_specification(
        self,
        semantic_ir: SemanticDomainIR,
        statechart_ir: StatechartIR,
        strict: bool = True
    ) -> MultiTierAuditResult:
        """Audits the multi-tier matrix across the specification."""
        tier_1_violations = []
        tier_2_violations = []
        tier_3_violations = []
        applied_overrides = []
        unresolved_tier_2 = []

        # 1. Tier 1 Structural Invariants (Hard gates)
        state_dict = statechart_ir.to_dict()
        if not state_dict.get("states"):
            tier_1_violations.append("Statechart has zero states defined.")
        if state_dict.get("initial") not in state_dict.get("states", {}):
            tier_1_violations.append(f"Initial state '{state_dict.get('initial')}' is not in states pool.")

        # 2. Tier 2 Usability & Ergonomics
        heuristic_violations = self.auditor.audit_statechart_usability(state_dict)
        for v in heuristic_violations:
            tier_2_violations.append(v)
            # Check stateful override
            ex = self.registry.is_exempt(v["heuristic_id"], v["component_hash"])
            if ex:
                applied_overrides.append(f"Override applied: {ex.exemption_id} for {v['component_name']}")
            else:
                unresolved_tier_2.append(v)

        # 3. Tier 3 Domain Benchmarks
        is_srs = any("srs" in cap.name.lower() or "review" in cap.name.lower() for cap in semantic_ir.capabilities)
        if is_srs:
            has_milestone = any("completed" in s for s in statechart_ir.collect_all_state_ids())
            if not has_milestone:
                tier_3_violations.append("[AX-MEM-002 Violation] Spaced repetition sessions must terminate in an explicit 'completed' milestone.")

            has_cram = any("cram" in s for s in statechart_ir.collect_all_state_ids())
            if not has_cram:
                tier_3_violations.append("[AX-MEM-008 Violation] Memorization systems must provide a distinct practice/cram mode.")

        is_category = any("category" in cap.name.lower() or "morphism" in cap.name.lower() or "commutativ" in cap.name.lower() for cap in semantic_ir.capabilities)
        if is_category:
            has_commuting = any("commut" in s for s in statechart_ir.collect_all_state_ids())
            if not has_commuting:
                tier_3_violations.append("[AX-CAT-003 Violation] Category reasoning platforms must provide a commutativity verification state.")
            has_composition = any("compos" in s for s in statechart_ir.collect_all_state_ids())
            if not has_composition:
                tier_3_violations.append("[AX-CAT-002 Violation] Category platforms must provide an interactive composition workflow.")

        tier_1_passed = len(tier_1_violations) == 0
        tier_2_passed = len(unresolved_tier_2) == 0
        tier_3_passed = len(tier_3_violations) == 0
        all_passed = tier_1_passed and tier_2_passed and tier_3_passed

        summary = (
            f"Multi-Tier Audit: T1={tier_1_passed} (fails={len(tier_1_violations)}), "
            f"T2={tier_2_passed} (unresolved={len(unresolved_tier_2)}, overridden={len(applied_overrides)}), "
            f"T3={tier_3_passed} (fails={len(tier_3_violations)})"
        )

        result = MultiTierAuditResult(
            passed=all_passed,
            tier_1_passed=tier_1_passed,
            tier_2_passed=tier_2_passed,
            tier_3_passed=tier_3_passed,
            tier_1_violations=tier_1_violations,
            tier_2_violations=tier_2_violations,
            tier_3_violations=tier_3_violations,
            applied_overrides=applied_overrides,
            unresolved_heuristic_violations=unresolved_tier_2,
            audit_summary=summary
        )

        if strict and not all_passed:
            msgs = []
            if tier_1_violations:
                msgs.append("Tier 1 Structural: " + "; ".join(tier_1_violations))
            if unresolved_tier_2:
                msgs.append("Tier 2 Usability: " + "; ".join(v["message"] for v in unresolved_tier_2))
            if tier_3_violations:
                msgs.append("Tier 3 Domain: " + "; ".join(tier_3_violations))
            raise MultiTierAxiomViolation(f"[Multi-Tier Verification Failure] {summary} Details: {' | '.join(msgs)}")

        return result
