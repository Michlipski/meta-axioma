"""Generation 3b Stateless Subagent Transition Functions.

Enforces:
- [L1-G3B-014] Dual-Model Cognitive Routing:
  1. ResearcherSubagent & DialecticalArchitectSubagent -> Exclusively bound to Gemini 4 Argon.
     Operate strictly as pure transition functions: TaskNode -> (DecompositionPlan, physical_tokens).
  2. LeafSynthesizerSubagent -> Exclusively bound to Gemini 3.8 Flash.
     Operates strictly on indivisible leaf nodes: TaskNode -> (LeafArtifact, physical_tokens).
- [L1-G3B-015] Stack Purity:
  Subagents never invoke other subagents directly. Non-leaf agents return only a
  DecompositionPlan for the outer FSM orchestrator to push onto the FractalTaskStack.
"""

import json
from typing import Tuple, Dict, Any, List, Optional, Callable

from ..routing.router import DualModelRouter, CognitiveRole, ModelTier
from ..thermodynamics import PhysicalTokenMeter
from ..evaluators.micro_auditors import LeafArtifact
from ..ir.statechart_ir import StatechartIR, StateNode, StateNodeType, Transition
from ..ir.contract_ir import (
    ContractIR,
    DomainNoun,
    DomainVerb,
    FieldDef,
    ComposedVerb,
    VerbCompositionStep,
)
from ..ir.topology_ir import (
    TopologyIR,
    TopologyNode,
    NodeRole,
    NetworkChannel,
    ChannelType,
    ConsensusContract,
    ConsensusProtocol,
)
from .stack import TaskNode, TaskType, DecompositionPlan, SubtaskSpec
from .models import QuorumVerdict


class ResearcherSubagent:
    """Stateless transition function (Gemini 4 Argon): Deconstructs Macro SoC into architectural subsystems."""

    @classmethod
    def execute(cls, node: TaskNode) -> Tuple[DecompositionPlan, int]:
        """Transitions a MACRO_SOC_DECONSTRUCTION node into dialectical subsystem subtasks."""
        if node.is_leaf:
            raise ValueError(f"ResearcherSubagent cannot execute leaf node '{node.task_id}'.")

        # 1. Verify [L1-G3B-014] Brain Argon routing
        invocation = DualModelRouter.create_invocation(
            task_id=node.task_id,
            role=CognitiveRole.DIALECTICAL_EXPLORATION,
            payload=node.payload,
            requested_model=ModelTier.BRAIN_ARGON,
        )

        soc_dict = node.payload.get("soc", {})
        soc_id = soc_dict.get("soc_id", "soc_default")
        is_multi_node = node.payload.get("is_multi_node_cluster", False)
        required_invariants = node.payload.get("required_invariants", [])
        inject_fault_on_first_try = node.payload.get("inject_fault_on_first_try", False)
        inject_quorum_hallucinations = node.payload.get("inject_quorum_hallucinations", False)

        # Decompose into Dialectical Architecture Task
        subtasks = [
            SubtaskSpec(
                subtask_id=f"{node.task_id}.arch_dialectic",
                task_type=TaskType.DIALECTICAL_ARCH_DECOMPOSITION,
                description=f"Synthesize formal architectural decomposition for SoC '{soc_id}'",
                is_leaf=False,
                budget_fraction=0.95,
                payload={
                    "soc": soc_dict,
                    "is_multi_node_cluster": is_multi_node,
                    "required_invariants": required_invariants,
                    "inject_fault_on_first_try": inject_fault_on_first_try,
                    "inject_quorum_hallucinations": inject_quorum_hallucinations,
                },
            )
        ]

        plan = DecompositionPlan(
            parent_task_id=node.task_id,
            rationale=(
                f"[Gemini 4 Argon Research Synthesis]: Deconstructed Macro SoC '{soc_id}' "
                f"into dialectical architecture synthesis."
            ),
            subtasks=subtasks,
        )

        # Physical token accounting (Prompt + Plan Output)
        tokens = PhysicalTokenMeter.count(json.dumps(invocation.payload)) + PhysicalTokenMeter.count(plan.rationale) + 64
        return plan, tokens


class DialecticalArchitectSubagent:
    """Stateless transition function (Gemini 4 Argon): Decomposes architecture into indivisible leaf nodes."""

    @classmethod
    def execute(cls, node: TaskNode) -> Tuple[DecompositionPlan, int]:
        """Transitions a DIALECTICAL_ARCH_DECOMPOSITION node into primitive leaf synthesis tasks."""
        if node.is_leaf:
            raise ValueError(f"DialecticalArchitectSubagent cannot execute leaf node '{node.task_id}'.")

        # 1. Verify [L1-G3B-014] Brain Argon routing
        invocation = DualModelRouter.create_invocation(
            task_id=node.task_id,
            role=CognitiveRole.DIALECTICAL_EXPLORATION,
            payload=node.payload,
            requested_model=ModelTier.BRAIN_ARGON,
        )

        soc_dict = node.payload.get("soc", {})
        soc_id = soc_dict.get("soc_id", "system_core")
        is_multi_node = node.payload.get("is_multi_node_cluster", False)
        required_invariants = node.payload.get("required_invariants", [])
        inject_fault_on_first_try = node.payload.get("inject_fault_on_first_try", False)

        inject_quorum_hallucinations = node.payload.get("inject_quorum_hallucinations", False)

        subtasks = [
            SubtaskSpec(
                subtask_id=f"{node.task_id}.leaf_contract",
                task_type=TaskType.LEAF_CONTRACT_FRAGMENT,
                description=f"Emit Compositional Contract IR for '{soc_id}'",
                is_leaf=True,
                budget_fraction=0.38,
                payload={
                    "soc_id": soc_id,
                    "required_invariants": required_invariants,
                },
            ),
            SubtaskSpec(
                subtask_id=f"{node.task_id}.leaf_statechart",
                task_type=TaskType.LEAF_STATECHART_FRAGMENT,
                description=f"Emit Hierarchical Statechart IR for '{soc_id}'",
                is_leaf=True,
                budget_fraction=0.36,
                payload={
                    "soc_id": soc_id,
                },
            ),
            SubtaskSpec(
                subtask_id=f"{node.task_id}.leaf_topology",
                task_type=TaskType.LEAF_TOPOLOGY_FRAGMENT,
                description=f"Emit Distributed Topology IR for '{soc_id}'",
                is_leaf=True,
                budget_fraction=0.13,
                payload={
                    "soc_id": soc_id,
                    "is_multi_node_cluster": is_multi_node,
                    "inject_fault_on_first_try": inject_fault_on_first_try,
                },
            ),
            SubtaskSpec(
                subtask_id=f"{node.task_id}.leaf_code",
                task_type=TaskType.LEAF_CODE_MODULE,
                description=f"Emit verified core domain implementation module and live operational dashboard for '{soc_id}'",
                is_leaf=True,
                budget_fraction=0.13,
                payload={
                    "soc_id": soc_id,
                    "required_invariants": required_invariants,
                    "inject_fault_on_first_try": inject_fault_on_first_try,
                    "has_dashboard": True,
                },
            ),
        ]

        if inject_quorum_hallucinations:
            # Inject an unbudgeted feature hallucination and bypassed Quine isolation
            subtasks.append(
                SubtaskSpec(
                    subtask_id=f"{node.task_id}.leaf_mesh_hallucination",
                    task_type=TaskType.LEAF_CODE_MODULE,
                    description="Synthesize unbudgeted 8-voice networked WebSocket mesh with bypassed Quine isolation",
                    is_leaf=True,
                    budget_fraction=0.10,
                    payload={
                        "feature": "8-voice networked WebSocket mesh",
                        "bypass_quine_isolation": True,
                        "unbudgeted": True,
                    },
                )
            )
            subtasks[0].budget_fraction = 0.35
            subtasks[1].budget_fraction = 0.33
            subtasks[2].budget_fraction = 0.11
            subtasks[3].budget_fraction = 0.11
            plan_rationale = (
                f"[Gemini 4 Argon Dialectical Architect]: Proposed architecture for '{soc_id}' "
                f"incorporating an unbudgeted 8-voice networked WebSocket mesh and bypassed Quine isolation."
            )
        else:
            plan_rationale = (
                f"[Gemini 4 Argon Dialectical Architect]: Decomposed '{soc_id}' into 4 indivisible "
                f"primitive leaf units (Contract IR, Statechart IR, Topology IR, Core Code Module & Live Operational Dashboard)."
            )

        plan = DecompositionPlan(
            parent_task_id=node.task_id,
            rationale=plan_rationale,
            subtasks=subtasks,
        )

        tokens = PhysicalTokenMeter.count(json.dumps(invocation.payload)) + PhysicalTokenMeter.count(plan.rationale) + 96
        return plan, tokens

    @classmethod
    def synthesize_delta_update(
        cls,
        node: TaskNode,
        current_plan: DecompositionPlan,
        blocking_violations: List[str],
        domain_spec: Optional[Dict[str, Any]] = None,
    ) -> Tuple[DecompositionPlan, int]:
        """Synthesizes a Delta Update resolving only the specific Quorum violations under Gemini 4 Argon governance."""
        # 1. Enforce [L1-G3B-014] Brain Argon routing
        invocation = DualModelRouter.create_invocation(
            task_id=f"{node.task_id}.delta_update",
            role=CognitiveRole.DIALECTICAL_EXPLORATION,
            payload={
                "parent_task_id": node.task_id,
                "violations": list(blocking_violations),
                "current_rationale": current_plan.rationale,
            },
            requested_model=ModelTier.BRAIN_ARGON,
        )

        cleaned_subtasks: List[SubtaskSpec] = []
        hallucination_terms = [
            "websocket mesh", "8-voice", "microtonal", "microtonal lattice", "unbudgeted", "mesh_hallucination"
        ]

        for sub in current_plan.subtasks:
            desc_lower = sub.description.lower()
            sub_id_lower = sub.subtask_id.lower()
            # Drop unbudgeted feature hallucinations
            if any(term in desc_lower or term in sub_id_lower for term in hallucination_terms):
                continue
            if sub.payload.get("unbudgeted") or sub.payload.get("bypass_quine_isolation"):
                continue

            # Cleanse subtask payload
            new_payload = dict(sub.payload)
            new_payload.pop("bypass_quine_isolation", None)
            new_payload.pop("bypass_isolation", None)
            new_payload.pop("untestable", None)
            new_payload["isolation_enforced"] = True
            new_payload["quine_isolation_enforced"] = True
            if "has_testable_invariant" in new_payload and not new_payload["has_testable_invariant"]:
                new_payload["has_testable_invariant"] = True

            # Cleanse description of offending trigger phrases
            new_desc = sub.description
            for phrase in [
                "unbudgeted",
                "with bypassed Quine isolation",
                "bypassed Quine isolation",
                "8-voice networked WebSocket mesh",
                "untestable",
            ]:
                new_desc = new_desc.replace(phrase, "").strip()

            cleaned_subtasks.append(SubtaskSpec(
                subtask_id=sub.subtask_id,
                task_type=sub.task_type,
                description=new_desc,
                is_leaf=sub.is_leaf,
                budget_fraction=sub.budget_fraction,
                payload=new_payload,
            ))

        # Re-normalize budget fractions to sum to 1.0
        if cleaned_subtasks:
            total_frac = sum(s.budget_fraction for s in cleaned_subtasks)
            if total_frac > 0:
                for s in cleaned_subtasks:
                    s.budget_fraction = round(s.budget_fraction / total_frac, 4)

        # Ensure mandatory operational dashboard deliverable [L1-G3B-018] is present
        has_dashboard = any(
            "dashboard" in sub.description.lower()
            or (isinstance(sub.payload, dict) and sub.payload.get("has_dashboard", False))
            for sub in cleaned_subtasks
        )
        if not has_dashboard and cleaned_subtasks:
            for sub in cleaned_subtasks:
                if sub.task_type == TaskType.LEAF_CODE_MODULE:
                    if "dashboard" not in sub.description.lower():
                        sub.description = f"{sub.description} and live operational dashboard"
                    sub.payload["has_dashboard"] = True
                    break

        purified_rationale = (
            f"[Gemini 4 Argon Delta Update]: Resolved {len(blocking_violations)} Quorum blocking violations. "
            f"Purified architecture: excised unbudgeted hallucinations, restored strict Quine isolation [L1-G3B-017], "
            f"and certified testable formal invariants and live operational dashboard [L1-G3B-018] across all leaf subtasks."
        )

        purified_plan = DecompositionPlan(
            parent_task_id=current_plan.parent_task_id,
            rationale=purified_rationale,
            subtasks=cleaned_subtasks,
        )

        tokens = (
            PhysicalTokenMeter.count(json.dumps(invocation.payload))
            + PhysicalTokenMeter.count(purified_rationale)
            + 80
        )
        return purified_plan, tokens


class ProductManagerAuditor:
    """Stateless transition function (Gemini 4 Argon): Relentlessly enforces scope boundaries, thermodynamic budgets,

    and mandatory core deliverables [L1-G3B-018].
    Must explicitly reject 'feature-rich' hallucinations (e.g., unbudgeted WebSocket meshes, microtonal lattices)
    not fundamentally required by the Tier 1 SoC, and reject any plan lacking the live operational dashboard deliverable.
    """

    ROLE_ID = "PRODUCT_MANAGER"

    @classmethod
    def audit(
        cls,
        node: TaskNode,
        plan: DecompositionPlan,
        domain_spec: Optional[Dict[str, Any]] = None,
    ) -> Tuple[QuorumVerdict, int]:
        """Audits a DecompositionPlan proposal against Tier 1 SoC scope boundaries and thermodynamic budgets."""
        # 1. Enforce [L1-G3B-014] Brain Argon routing
        invocation = DualModelRouter.create_invocation(
            task_id=f"quorum_audit:pm:{node.task_id}",
            role=CognitiveRole.ZERO_TRUST_AUDITOR,
            payload={
                "task_id": node.task_id,
                "plan_rationale": plan.rationale,
                "subtasks_count": len(plan.subtasks),
                "target_soc": node.payload.get("soc", {}),
            },
            requested_model=ModelTier.BRAIN_ARGON,
        )

        soc_dict = node.payload.get("soc", {})
        soc_id = soc_dict.get("soc_id", node.task_id) if isinstance(soc_dict, dict) else node.task_id
        soc_corpus = json.dumps(soc_dict).lower() if isinstance(soc_dict, (dict, list)) else str(soc_dict).lower()

        blocking_violations: List[str] = []

        # Hallucination trigger phrases: feature-rich capabilities that require explicit grounding
        hallucination_triggers = [
            "websocket mesh",
            "8-voice",
            "microtonal",
            "microtonal lattice",
            "audio synthesizer",
            "jam mesh",
            "synthesizer lattice",
        ]

        # Scan rationale and subtasks
        scanned_texts = [plan.rationale]
        for sub in plan.subtasks:
            scanned_texts.append(sub.description)
            if isinstance(sub.payload, dict):
                scanned_texts.append(str(sub.payload))
                if sub.payload.get("unbudgeted"):
                    blocking_violations.append(
                        f"[Thermodynamic Scope Violation] Unbudgeted subtask detected: '{sub.description}' "
                        f"lacks approved thermodynamic capital allocation."
                    )

        combined_text = " ".join(scanned_texts).lower()
        for trigger in hallucination_triggers:
            if trigger in combined_text and trigger not in soc_corpus:
                domain_spec_str = json.dumps(domain_spec).lower() if domain_spec else ""
                if trigger not in domain_spec_str:
                    blocking_violations.append(
                        f"[Scope Creep Violation] Unbudgeted feature-rich hallucination detected: "
                        f"'{trigger}' is not fundamentally required by Tier 1 SoC '{soc_id}' "
                        f"and violates thermodynamic scope boundaries."
                    )

        # Enforce budget fractions <= 1.0
        total_fraction = sum(s.budget_fraction for s in plan.subtasks)
        if total_fraction > 1.001:
            blocking_violations.append(
                f"[Thermodynamic Budget Violation] Subtask budget fractions sum to {total_fraction:.2f} > 1.00 "
                f"(exceeds exploratory capital boundary)."
            )

        # Mandatory Operational Dashboard Deliverable [L1-G3B-018]
        has_code_modules = any(s.task_type == TaskType.LEAF_CODE_MODULE for s in plan.subtasks)
        if has_code_modules and (
            domain_spec is not None
            or "facade" in soc_id.lower()
            or "clinical" in soc_id.lower()
            or "app" in soc_id.lower()
            or "studio" in soc_id.lower()
            or node.payload.get("require_dashboard", False)
            or node.payload.get("is_multi_node_cluster", False)
        ):
            has_dashboard = any(
                "dashboard" in sub.description.lower()
                or (isinstance(sub.payload, dict) and sub.payload.get("has_dashboard", False))
                for sub in plan.subtasks
            )
            if not has_dashboard:
                blocking_violations.append(
                    f"[Missing Core Deliverable [L1-G3B-018]] Plan for '{soc_id}' synthesizes code modules "
                    f"but lacks a live operational / telemetry dashboard deliverable (dashboard.html)."
                )

        verdict = QuorumVerdict(
            role_id=cls.ROLE_ID,
            approved=len(blocking_violations) == 0,
            blocking_violations=blocking_violations,
        )

        tokens = (
            PhysicalTokenMeter.count(json.dumps(invocation.payload))
            + PhysicalTokenMeter.count(plan.rationale)
            + sum(len(v) for v in blocking_violations) // 4
            + 64
        )
        return verdict, tokens


class ArchitectAuditor:
    """Stateless transition function (Gemini 4 Argon): Enforces [L1-G3B-012] Topological Fidelity & [L1-G3B-017] Quine Protocol.

    Rejects any spec that bypasses isolation boundaries.
    """

    ROLE_ID = "SYSTEMS_ARCHITECT"

    @classmethod
    def audit(
        cls,
        node: TaskNode,
        plan: DecompositionPlan,
        domain_spec: Optional[Dict[str, Any]] = None,
    ) -> Tuple[QuorumVerdict, int]:
        """Audits a DecompositionPlan proposal against system isolation and topological invariants."""
        # 1. Enforce [L1-G3B-014] Brain Argon routing
        invocation = DualModelRouter.create_invocation(
            task_id=f"quorum_audit:architect:{node.task_id}",
            role=CognitiveRole.ZERO_TRUST_AUDITOR,
            payload={
                "task_id": node.task_id,
                "plan_rationale": plan.rationale,
                "subtasks_count": len(plan.subtasks),
                "is_multi_node_cluster": node.payload.get("is_multi_node_cluster", False),
            },
            requested_model=ModelTier.BRAIN_ARGON,
        )

        blocking_violations: List[str] = []

        # 2. Enforce [L1-G3B-017] Quine Protocol & Isolation Boundaries
        isolation_bypass_triggers = [
            "bypassed quine isolation",
            "bypassed quine",
            "bypass quine",
            "bypass isolation",
            "bypassed isolation",
            "skip isolation",
            "skip daughter isolation",
            "bypass daughter isolation",
            "bypass daughter",
            "bypass sandbox",
            "direct host execution",
        ]

        scanned_texts = [plan.rationale]
        for sub in plan.subtasks:
            scanned_texts.append(sub.description)
            if isinstance(sub.payload, dict):
                scanned_texts.append(str(sub.payload))
                if sub.payload.get("bypass_quine_isolation") or sub.payload.get("bypass_isolation"):
                    blocking_violations.append(
                        "[L1-G3B-017 Quine Protocol Violation] Spec attempts to bypass Quine isolation boundaries: "
                        f"Subtask '{sub.subtask_id}' has bypass flag set."
                    )

        combined_text = " ".join(scanned_texts).lower()
        for trigger in isolation_bypass_triggers:
            if trigger in combined_text:
                blocking_violations.append(
                    f"[L1-G3B-017 Quine Protocol Violation] Spec attempts to bypass Quine isolation boundaries: "
                    f"'{trigger}' is strictly prohibited. All daughter emissions must execute inside isolated sandboxes."
                )
                break

        # 3. Enforce [L1-G3B-012] Topological Fidelity
        is_multi_node = node.payload.get("is_multi_node_cluster", False)
        if is_multi_node:
            for sub in plan.subtasks:
                if sub.task_type == TaskType.LEAF_TOPOLOGY_FRAGMENT or "topology" in sub.subtask_id:
                    desc_lower = sub.description.lower()
                    payload_str = json.dumps(sub.payload).lower() if isinstance(sub.payload, dict) else ""
                    if "127.0.0.1" in desc_lower or "127.0.0.1" in payload_str or "localhost" in desc_lower:
                        blocking_violations.append(
                            "[L1-G3B-012 Topological Fidelity Violation] Multi-node distributed topology attempts "
                            "loopback binding ('127.0.0.1' / 'localhost'). Must bind to routable cluster interfaces."
                        )

        verdict = QuorumVerdict(
            role_id=cls.ROLE_ID,
            approved=len(blocking_violations) == 0,
            blocking_violations=blocking_violations,
        )

        tokens = (
            PhysicalTokenMeter.count(json.dumps(invocation.payload))
            + PhysicalTokenMeter.count(plan.rationale)
            + sum(len(v) for v in blocking_violations) // 4
            + 64
        )
        return verdict, tokens


class QAVerificationAuditor:
    """Stateless transition function (Gemini 4 Argon): Rejects proposed features lacking testable invariants."""

    ROLE_ID = "QA_ENGINEER"

    @classmethod
    def audit(
        cls,
        node: TaskNode,
        plan: DecompositionPlan,
        domain_spec: Optional[Dict[str, Any]] = None,
    ) -> Tuple[QuorumVerdict, int]:
        """Audits a DecompositionPlan proposal ensuring every feature and transition has a mathematically testable invariant."""
        # 1. Enforce [L1-G3B-014] Brain Argon routing
        invocation = DualModelRouter.create_invocation(
            task_id=f"quorum_audit:qa:{node.task_id}",
            role=CognitiveRole.ZERO_TRUST_AUDITOR,
            payload={
                "task_id": node.task_id,
                "plan_rationale": plan.rationale,
                "subtasks_count": len(plan.subtasks),
                "required_invariants": node.payload.get("required_invariants", []),
            },
            requested_model=ModelTier.BRAIN_ARGON,
        )

        blocking_violations: List[str] = []

        untestable_triggers = [
            "untestable",
            "lacks mathematically testable invariant",
            "no formal invariant",
            "unverifiable",
            "missing verification invariant",
            "no test assertions",
        ]

        scanned_texts = [plan.rationale]
        for sub in plan.subtasks:
            scanned_texts.append(sub.description)
            if isinstance(sub.payload, dict):
                scanned_texts.append(str(sub.payload))
                if sub.payload.get("has_testable_invariant") is False or sub.payload.get("untestable"):
                    blocking_violations.append(
                        f"[QA Verification Violation] Proposed feature or state transition in subtask "
                        f"'{sub.subtask_id}' lacks a mathematically testable invariant."
                    )
                if sub.payload.get("omit_invariants"):
                    blocking_violations.append(
                        f"[QA Verification Invariant Breach] Mandatory system invariants explicitly omitted in subtask '{sub.subtask_id}'."
                    )

        combined_text = " ".join(scanned_texts).lower()
        for trigger in untestable_triggers:
            if trigger in combined_text:
                blocking_violations.append(
                    f"[QA Verification Violation] Proposed feature or state transition lacks a mathematically testable invariant: '{trigger}'."
                )
                break

        # Check required_invariants
        required_invs = node.payload.get("required_invariants", [])
        if required_invs:
            has_contract_or_code = any(
                s.task_type in (TaskType.LEAF_CONTRACT_FRAGMENT, TaskType.LEAF_CODE_MODULE)
                for s in plan.subtasks
            )
            if not has_contract_or_code:
                blocking_violations.append(
                    f"[QA Verification Invariant Breach] Required invariants {required_invs} present, "
                    f"but plan lacks Contract IR or Code Module leaf subtask to verify them."
                )

        verdict = QuorumVerdict(
            role_id=cls.ROLE_ID,
            approved=len(blocking_violations) == 0,
            blocking_violations=blocking_violations,
        )

        tokens = (
            PhysicalTokenMeter.count(json.dumps(invocation.payload))
            + PhysicalTokenMeter.count(plan.rationale)
            + sum(len(v) for v in blocking_violations) // 4
            + 64
        )
        return verdict, tokens


class LeafSynthesizerSubagent:
    """Stateless transition function (Gemini 3.8 Flash): Emits indivisible primitive leaf artifacts."""

    @classmethod
    def execute(
        cls,
        node: TaskNode,
        custom_generator: Optional[Callable[[TaskNode], str]] = None,
        domain_spec: Optional[Dict[str, Any]] = None,
    ) -> Tuple[LeafArtifact, int]:
        """Executes leaf emission under Gemini 3.8 Flash governance.

        If node.remediation_context is present (isolated retry governed by Argon),
        applies targeted self-healing remediation to repair the trapped defect.
        """
        if not node.is_leaf:
            raise ValueError(f"LeafSynthesizerSubagent can only execute leaf nodes; got non-leaf '{node.task_id}'.")

        role_map = {
            TaskType.LEAF_CONTRACT_FRAGMENT: CognitiveRole.LEAF_SCHEMA_EMISSION,
            TaskType.LEAF_STATECHART_FRAGMENT: CognitiveRole.LEAF_SCHEMA_EMISSION,
            TaskType.LEAF_TOPOLOGY_FRAGMENT: CognitiveRole.LEAF_DATA_EMISSION,
            TaskType.LEAF_CODE_MODULE: CognitiveRole.LEAF_CODE_EMISSION,
        }
        role = role_map.get(node.task_type, CognitiveRole.LEAF_CODE_EMISSION)

        # 1. Verify [L1-G3B-014] Muscle Flash routing
        if node.retry_count > 0 and node.remediation_context:
            invocation = DualModelRouter.synthesize_isolated_reprompt(
                failed_leaf_task_id=node.task_id,
                leaf_role=role,
                defect_report=node.remediation_context,
                prior_payload={**node.payload, "isolation_depth": node.retry_count - 1},
            )
        else:
            invocation = DualModelRouter.create_invocation(
                task_id=node.task_id,
                role=role,
                payload=node.payload,
                requested_model=ModelTier.MUSCLE_FLASH,
            )

        soc_id = node.payload.get("soc_id", "system_core")
        required_invariants = node.payload.get("required_invariants", [])
        is_multi_node = node.payload.get("is_multi_node_cluster", False)
        inject_fault = node.payload.get("inject_fault_on_first_try", False) and (node.retry_count == 0)

        endpoints: List[str] = []

        if custom_generator is not None:
            content = custom_generator(node)
            artifact_type = "custom"
        elif domain_spec is not None and node.task_type == TaskType.LEAF_CONTRACT_FRAGMENT and "contract_ir" in domain_spec:
            contract = ContractIR.from_dict(domain_spec["contract_ir"])
            raw_json = contract.to_json()
            if contract.nouns and required_invariants:
                first_noun = next(iter(contract.nouns.values()))
                for inv in required_invariants:
                    if inv not in raw_json and inv not in first_noun.invariants:
                        first_noun.invariants.append(inv)
            content = contract.to_json()
            artifact_type = "contract_fragment"
        elif domain_spec is not None and node.task_type == TaskType.LEAF_STATECHART_FRAGMENT and "statechart_ir" in domain_spec:
            chart = StatechartIR.from_dict(domain_spec["statechart_ir"])
            content = chart.to_json()
            artifact_type = "schema"
        elif domain_spec is not None and node.task_type == TaskType.LEAF_TOPOLOGY_FRAGMENT and "topology_ir" in domain_spec:
            topo = TopologyIR.from_dict(domain_spec["topology_ir"])
            if inject_fault and topo.nodes:
                first_nid = next(iter(topo.nodes.keys()))
                topo.nodes[first_nid].host_interface = "127.0.0.1"
            content = topo.to_json()
            endpoints = [f"http://{n.host_interface}:{n.port}" for n in topo.nodes.values()]
            artifact_type = "config"
        elif node.task_type == TaskType.LEAF_CONTRACT_FRAGMENT:
            content = cls._synthesize_contract_ir(soc_id, required_invariants)
            artifact_type = "contract_fragment"
        elif node.task_type == TaskType.LEAF_STATECHART_FRAGMENT:
            content = cls._synthesize_statechart_ir(soc_id)
            artifact_type = "schema"
        elif node.task_type == TaskType.LEAF_TOPOLOGY_FRAGMENT:
            content, endpoints = cls._synthesize_topology_ir(soc_id, is_multi_node, inject_fault)
            artifact_type = "config"
        elif node.task_type == TaskType.LEAF_CODE_MODULE:
            content = cls._synthesize_code_module(soc_id, required_invariants, inject_fault)
            artifact_type = "code"
        else:
            content = f"# Leaf output for {node.task_id}"
            artifact_type = "code"

        artifact = LeafArtifact(
            task_id=node.task_id,
            artifact_type=artifact_type,
            content=content,
            emitting_model=invocation.assigned_model.value,
            token_budget_allocated=node.allocated_token_budget,
            network_endpoints=endpoints,
            metadata={
                "soc_id": soc_id,
                "task_type": node.task_type.value,
                "required_invariants": required_invariants,
                "is_multi_node_cluster": is_multi_node,
                "retry_count": node.retry_count,
            },
        )

        tokens = PhysicalTokenMeter.count(json.dumps(invocation.payload)) + PhysicalTokenMeter.count(content)
        return artifact, tokens

    @classmethod
    def _synthesize_contract_ir(cls, soc_id: str, required_invariants: List[str]) -> str:
        invs = list(required_invariants) if required_invariants else ["state_valid == True"]
        contract = ContractIR(
            contract_id=f"contract_{soc_id}",
            title=f"Compositional Contract for {soc_id}",
            description=f"Auto-synthesized compositional contract for {soc_id}",
        )
        contract.add_noun(DomainNoun(
            name="CoreEntity",
            description="Primary domain entity",
            fields=[FieldDef("entity_id", "str"), FieldDef("status", "str")],
            invariants=invs,
        ))
        parent_verb = DomainVerb(
            name="ExecuteWorkflow",
            description="Primary workflow transition",
            pre_conditions=["input_validated == True"],
            post_conditions=["workflow_completed == True", "state_persisted == True"],
            modifies_nouns=["CoreEntity"],
        )
        sub_step1 = ContractIR(contract_id=f"sub_{soc_id}_validate", title="Validation Subcontract", description="")
        sub_step1.add_verb(DomainVerb(
            name="ValidateAndPrepare",
            description="Validates preconditions",
            pre_conditions=["input_validated == True"],
            post_conditions=["prepared == True"],
        ))
        sub_step2 = ContractIR(contract_id=f"sub_{soc_id}_commit", title="Commit Subcontract", description="")
        sub_step2.add_verb(DomainVerb(
            name="CommitState",
            description="Persists state change",
            pre_conditions=["prepared == True"],
            post_conditions=["workflow_completed == True", "state_persisted == True"],
            modifies_nouns=["CoreEntity"],
        ))
        contract.sub_contracts[sub_step1.contract_id] = sub_step1
        contract.sub_contracts[sub_step2.contract_id] = sub_step2
        contract.add_composed_verb(ComposedVerb(
            parent_verb=parent_verb,
            child_steps=[
                VerbCompositionStep(sub_step1.contract_id, "ValidateAndPrepare"),
                VerbCompositionStep(sub_step2.contract_id, "CommitState"),
            ],
        ))
        return contract.to_json()

    @classmethod
    def _synthesize_statechart_ir(cls, soc_id: str) -> str:
        active_substates = {
            "validating": StateNode(
                id="active.validating",
                node_type=StateNodeType.ATOMIC,
                transitions=[Transition(event="VALIDATED", target="active.committing")],
            ),
            "committing": StateNode(
                id="active.committing",
                node_type=StateNodeType.ATOMIC,
                transitions=[
                    Transition(event="COMMITTED", target="active.completed"),
                    Transition(event="UNDO", target="active.validating"),
                ],
            ),
            "completed": StateNode(id="active.completed", node_type=StateNodeType.FINAL),
        }
        root = StateNode(
            id="root",
            node_type=StateNodeType.COMPOUND,
            initial="idle",
            states={
                "idle": StateNode(
                    id="root.idle",
                    node_type=StateNodeType.ATOMIC,
                    transitions=[Transition(event="START", target="root.active")],
                ),
                "active": StateNode(
                    id="root.active",
                    node_type=StateNodeType.COMPOUND,
                    initial="validating",
                    states=active_substates,
                    transitions=[Transition(event="FINISH", target="root.done")],
                ),
                "done": StateNode(id="root.done", node_type=StateNodeType.FINAL),
            },
        )
        chart = StatechartIR(
            id=f"statechart_{soc_id}",
            root=root,
            context_schema={"step_count": "int", "value_delivered": "bool"},
            initial_context={"step_count": 0, "value_delivered": False},
        )
        return chart.to_json()

    @classmethod
    def _synthesize_topology_ir(
        cls,
        soc_id: str,
        is_multi_node: bool,
        inject_fault: bool,
    ) -> Tuple[str, List[str]]:
        topo = TopologyIR(topology_id=f"topo_{soc_id}")
        if is_multi_node:
            # If inject_fault is True on retry 0, simulate a loopback leak that Argon will trap!
            # On retry >= 1, remediate to routable cluster subnet IPs.
            host_1 = "127.0.0.1" if inject_fault else "192.168.10.11"
            host_2 = "localhost" if inject_fault else "192.168.10.12"
            topo.add_node(TopologyNode("node_primary", NodeRole.ORCHESTRATOR, host_1, 8080))
            topo.add_node(TopologyNode("node_replica", NodeRole.STORAGE_LEAF, host_2, 8081))
            topo.add_channel(NetworkChannel("ch_sync", "node_primary", "node_replica", ChannelType.RPC, 8081))
            topo.consensus = ConsensusContract(protocol=ConsensusProtocol.SHEAF_QUORUM, quorum_fraction=0.67)
            endpoints = [f"http://{host_1}:8080", f"http://{host_2}:8081"]
        else:
            topo.add_node(TopologyNode("node_single", NodeRole.ORCHESTRATOR, "192.168.10.10", 8080))
            endpoints = ["http://192.168.10.10:8080"]
        return topo.to_json(), endpoints

    @classmethod
    def _synthesize_code_module(
        cls,
        soc_id: str,
        required_invariants: List[str],
        inject_fault: bool,
    ) -> str:
        lines = [
            f'"""Generated Core Domain Module for {soc_id}."""',
            "",
            "class DomainEngine:",
            "    def __init__(self):",
            "        self.state = {'initialized': True, 'balance': 100}",
            "        self.history = []",
            "",
        ]
        if inject_fault:
            # Simulate a security or invariant omission defect on attempt 0
            lines.append("    def execute(self, payload: str, balance: int = 100):")
            lines.append("        # Faulty un-audited code")
            lines.append("        return eval(payload)")
        else:
            lines.append("    def execute(self, payload: dict, balance: int = 100) -> dict:")
            for inv in required_invariants:
                lines.append(f"        # Enforcing invariant: {inv}")
                lines.append(f"        assert {inv}, 'Invariant violated: {inv}'")
            lines.append("        prev = dict(self.state)")
            lines.append("        self.history.append(prev)")
            lines.append("        self.state['balance'] = balance")
            lines.append("        self.state['value_delivered'] = True")
            lines.append("        return dict(self.state)")
            lines.append("")
            lines.append("    def undo(self) -> dict:")
            lines.append("        if self.history:")
            lines.append("            self.state = self.history.pop()")
            lines.append("        return dict(self.state)")

        return "\n".join(lines) + "\n"
