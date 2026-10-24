"""Generation 3b Closed-Loop Semantic Crucible Orchestrator.

Enforces:
- [L1-G3B-014] Dual-Model Cognitive Routing (Argon Brain vs. Flash Muscle).
- [L1-G3B-015] Stack Purity & Bounded Recursion (d_max, b_max, schema-validated DecompositionPlans).
- [L1-G3B-016] Zero-Bypass Interception Invariant:
  1. Zero leaf payloads produced by Gemini 3.8 Flash may be committed without passing
     through ZeroTrustMicroAuditorRegistry and formal IR evaluators.
  2. Failed leaves enter an isolated remediation loop with exponential backoff retry budget
     (max_retries=3) governed by Argon before tripping LeafRemediationCircuitBreakerError.
- Thermodynamic Grounding:
  Live physical token accounting separating Argon deliberation, Flash leaf emission, and
  Argon protected verification sinks, including Landauer bit-erasure dissipation on rejected leaves.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Union, Callable

from ..thermodynamics import (
    ThermodynamicLedger,
    PhysicalTokenMeter,
    DynamicBudgetCalibrator,
)
from ..soc.models import SituationOfConcern, PitchInput, ReferenceProductInput
from ..soc.normalizer import SoCNormalizer
from ..ir.contract_ir import ContractIR
from ..ir.statechart_ir import StatechartIR
from ..ir.topology_ir import TopologyIR
from ..routing.router import (
    DualModelRouter,
    CognitiveRole,
    ModelTier,
    SubagentExecutionWitness,
    SubagentExecutionViolation,
)
from ..evaluators.checker import FormalModelChecker
from ..evaluators.micro_auditors import (
    LeafArtifact,
    MicroAuditResult,
    ZeroTrustMicroAuditorRegistry,
)
from .stack import (
    TaskNode,
    TaskType,
    FractalTaskStack,
)
from .subagents import (
    ResearcherSubagent,
    DialecticalArchitectSubagent,
    LeafSynthesizerSubagent,
)


class LeafRemediationCircuitBreakerError(Exception):
    """Raised when a leaf node exhausts its maximum isolated remediation retry budget."""
    pass


class ZeroBypassInterceptionViolation(Exception):
    """Raised if any code path attempts to commit an un-audited leaf artifact."""
    pass


@dataclass
class CrucibleSynthesisResult:
    """The certified output of the Milestone 3 Semantic Crucible."""
    certified_soc: SituationOfConcern
    verified_contract: Optional[ContractIR] = None
    verified_statechart: Optional[StatechartIR] = None
    verified_topology: Optional[TopologyIR] = None
    verified_code_modules: Dict[str, str] = field(default_factory=dict)
    verified_leaves: Dict[str, LeafArtifact] = field(default_factory=dict)
    audit_certificates: Dict[str, MicroAuditResult] = field(default_factory=dict)
    remediation_events: List[Dict[str, Any]] = field(default_factory=list)
    stack_trace: List[Dict[str, Any]] = field(default_factory=list)
    subagent_witnesses: List[Dict[str, Any]] = field(default_factory=list)
    thermodynamic_summary: Dict[str, Any] = field(default_factory=dict)
    argon_deliberation_tokens: int = 0
    flash_emission_tokens: int = 0
    argon_verification_tokens: int = 0


class CrucibleOrchestrator:
    """The deterministic outer FSM orchestrating the Fractal Task Stack and Zero-Trust Interception."""

    def __init__(
        self,
        total_budget: Optional[int] = None,
        d_max: int = 5,
        b_max: int = 8,
        max_leaf_retries: int = 3,
    ):
        self._explicit_budget = total_budget
        self.ledger = ThermodynamicLedger.create(total_budget=total_budget)
        self.stack = FractalTaskStack(d_max=d_max, b_max=b_max)
        self.max_leaf_retries = max_leaf_retries
        self.argon_deliberation_tokens = 0
        self.flash_emission_tokens = 0
        self.argon_verification_tokens = 0

    def run_crucible(
        self,
        seed_input: Union[SituationOfConcern, PitchInput, ReferenceProductInput],
        soc_id: str = "soc_crucible_target",
        is_multi_node_cluster: bool = False,
        required_invariants: Optional[List[str]] = None,
        inject_fault_on_first_try: bool = False,
        custom_leaf_generator: Optional[Callable[[TaskNode], str]] = None,
        domain_spec: Optional[Dict[str, Any]] = None,
        subagent_witnesses: Optional[List[SubagentExecutionWitness]] = None,
        require_live_subagents: bool = False,
    ) -> CrucibleSynthesisResult:
        """Executes the closed-loop Semantic Crucible from seed input to verified IR bundle."""
        recorded_witnesses: List[Dict[str, Any]] = []
        if subagent_witnesses:
            for w in subagent_witnesses:
                DualModelRouter.validate_subagent_witness(w)
                recorded_witnesses.append(w.to_dict())

        if require_live_subagents:
            live_brain = [
                w for w in (subagent_witnesses or [])
                if w.is_live_agy_subagent and w.assigned_model == ModelTier.BRAIN_ARGON
            ]
            live_muscle = [
                w for w in (subagent_witnesses or [])
                if w.is_live_agy_subagent and w.assigned_model == ModelTier.MUSCLE_FLASH
            ]
            if not live_brain or not live_muscle:
                raise SubagentExecutionViolation(
                    "[L1-G3B-014 Subagent Execution Violation] require_live_subagents=True, "
                    f"but found {len(live_brain)} live Brain (pro) subagents and "
                    f"{len(live_muscle)} live Muscle (flash) subagents. "
                    "You MUST spawn real Antigravity subagents via `invoke_subagent`!"
                )

        # 1. Enforce [L1-G3B-014] Outer FSM Orchestrator under Gemini 4 Argon
        DualModelRouter.create_invocation(
            task_id=f"fsm_orchestrate:{soc_id}",
            role=CognitiveRole.ORCHESTRATOR_FSM,
            payload={"soc_id": soc_id},
            requested_model=ModelTier.BRAIN_ARGON,
        )

        # 2. Enforce [L1-G3B-000] Waterloo SoC Normalization
        if isinstance(seed_input, SituationOfConcern):
            certified_soc = SoCNormalizer.normalize_tier1(seed_input)
        elif isinstance(seed_input, PitchInput):
            certified_soc = SoCNormalizer.deconstruct_pitch(seed_input, soc_id=soc_id)
        elif isinstance(seed_input, ReferenceProductInput):
            certified_soc = SoCNormalizer.reverse_audit_product(seed_input, soc_id=soc_id)
        else:
            raise TypeError(f"Unsupported seed input type: {type(seed_input)}")

        # 2b. Calibrate Task-DAG budget & point-spend prediction
        if domain_spec is not None:
            est = DynamicBudgetCalibrator.estimate_for_domain_spec(
                soc_dict=certified_soc.to_dict(),
                domain_spec=domain_spec,
                required_invariants=required_invariants,
                expected_fault_retries=2 if inject_fault_on_first_try else 0,
                safety_margin_factor=1.25,
            )
        else:
            est = DynamicBudgetCalibrator.estimate(
                subsystems_count=1,
                leaves_per_subsystem=4,
                expected_fault_retries=2 if inject_fault_on_first_try else 0,
                safety_margin_factor=1.25,
            )
        effective_budget = self._explicit_budget if self._explicit_budget is not None else est.recommended_total_budget
        self.ledger = ThermodynamicLedger.create(
            total_budget=effective_budget,
            predicted_total_spend=est.predicted_total_spend,
            predicted_exploratory_spend=est.predicted_exploratory_spend,
        )

        soc_tokens = PhysicalTokenMeter.count(str(certified_soc.to_dict()))
        self.ledger.spend_exploratory(soc_tokens)
        self.argon_deliberation_tokens += soc_tokens

        # 3. Push Root Task onto FractalTaskStack
        root_budget = self.ledger.exploratory_cap - self.ledger.exploratory_spent
        root_task = TaskNode(
            task_id=f"root:{certified_soc.soc_id}",
            task_type=TaskType.MACRO_SOC_DECONSTRUCTION,
            description=f"Root Macro SoC Deconstruction for '{certified_soc.title}'",
            allocated_token_budget=root_budget,
            depth=0,
            is_leaf=False,
            max_retries=self.max_leaf_retries,
            payload={
                "soc": certified_soc.to_dict(),
                "is_multi_node_cluster": is_multi_node_cluster,
                "required_invariants": required_invariants or [],
                "inject_fault_on_first_try": inject_fault_on_first_try,
            },
        )
        self.stack.push_root(root_task)

        verified_leaves: Dict[str, LeafArtifact] = {}
        audit_certificates: Dict[str, MicroAuditResult] = {}
        remediation_events: List[Dict[str, Any]] = []
        verified_contract: Optional[ContractIR] = None
        verified_statechart: Optional[StatechartIR] = None
        verified_topology: Optional[TopologyIR] = None
        verified_code_modules: Dict[str, str] = {}

        # 4. Deterministic Stack Execution Loop
        while not self.stack.is_empty():
            current_node = self.stack.pop()
            if current_node is None:
                break

            if not current_node.is_leaf:
                # Non-leaf task: Invoke Argon transition function to obtain DecompositionPlan
                if current_node.task_type == TaskType.MACRO_SOC_DECONSTRUCTION:
                    plan, spent = ResearcherSubagent.execute(current_node)
                elif current_node.task_type in (
                    TaskType.DIALECTICAL_ARCH_DECOMPOSITION,
                    TaskType.SUBSYSTEM_DECOMPOSITION,
                ):
                    plan, spent = DialecticalArchitectSubagent.execute(current_node)
                else:
                    raise ValueError(f"Unsupported non-leaf task type: {current_node.task_type}")

                current_node.tokens_spent += spent
                self.ledger.spend_exploratory(spent)
                self.argon_deliberation_tokens += spent

                # Push decomposed subtasks onto the stack (enforces d_max, b_max, budget partition)
                children = self.stack.push_decomposition(current_node, plan)
                for ch in children:
                    ch.max_retries = self.max_leaf_retries

            else:
                # Indivisible Leaf Task: Invoke Muscle Flash to emit LeafArtifact
                leaf_artifact, emission_tokens = LeafSynthesizerSubagent.execute(
                    current_node,
                    custom_generator=custom_leaf_generator,
                    domain_spec=domain_spec,
                )
                current_node.tokens_spent += emission_tokens
                self.ledger.spend_exploratory(emission_tokens)
                self.flash_emission_tokens += emission_tokens

                # 5. Enforce [L1-G3B-016] Zero-Bypass Interception via Argon Micro-Auditors
                audit_result, ir_defects, parsed_obj = self._intercept_and_audit_leaf(
                    current_node,
                    leaf_artifact,
                )

                # Charge verification sink against Protected Capital (40% pool)
                verify_tokens = max(32, audit_result.physical_tokens // 2)
                self.ledger.spend_protected(verify_tokens)
                self.argon_verification_tokens += verify_tokens

                if not audit_result.is_passed:
                    # Leaf failed zero-trust audit!
                    # Record Landauer bit-erasure dissipation for the discarded defective leaf
                    erased_bits = len(leaf_artifact.content.encode("utf-8")) * 8
                    self.ledger.spend_exploratory(0, bits_erased=erased_bits)

                    backoff_ms = 100 * (2 ** current_node.retry_count)
                    remediation_events.append({
                        "task_id": current_node.task_id,
                        "attempt": current_node.retry_count + 1,
                        "max_retries": current_node.max_retries,
                        "backoff_delay_ms": backoff_ms,
                        "defects": list(audit_result.defects),
                        "bits_erased": erased_bits,
                    })

                    if current_node.retry_count >= current_node.max_retries:
                        raise LeafRemediationCircuitBreakerError(
                            f"[L1-G3B-016 Circuit Breaker Tripped] Leaf '{current_node.task_id}' failed "
                            f"zero-trust audit after {current_node.retry_count + 1} attempts "
                            f"(max_retries={current_node.max_retries}). Final defects: {audit_result.defects}"
                        )

                    # Push isolated retry onto stack with Argon remediation payload
                    self.stack.push_isolated_retry(
                        current_node,
                        remediation_advice=audit_result.remediation_advice or "; ".join(audit_result.defects),
                    )
                else:
                    # Leaf passed 100% of zero-trust audits! Commit to verified bundle.
                    self._commit_verified_leaf(
                        leaf_artifact=leaf_artifact,
                        audit_result=audit_result,
                        verified_leaves=verified_leaves,
                        audit_certificates=audit_certificates,
                    )
                    if isinstance(parsed_obj, ContractIR):
                        verified_contract = parsed_obj
                    elif isinstance(parsed_obj, StatechartIR):
                        verified_statechart = parsed_obj
                    elif isinstance(parsed_obj, TopologyIR):
                        verified_topology = parsed_obj
                    elif current_node.task_type == TaskType.LEAF_CODE_MODULE:
                        verified_code_modules[current_node.task_id] = leaf_artifact.content

        thermo_summary = self.ledger.to_dict()
        thermo_summary["argon_deliberation_tokens"] = self.argon_deliberation_tokens
        thermo_summary["flash_emission_tokens"] = self.flash_emission_tokens
        thermo_summary["argon_verification_tokens"] = self.argon_verification_tokens

        return CrucibleSynthesisResult(
            certified_soc=certified_soc,
            verified_contract=verified_contract,
            verified_statechart=verified_statechart,
            verified_topology=verified_topology,
            verified_code_modules=verified_code_modules,
            verified_leaves=verified_leaves,
            audit_certificates=audit_certificates,
            remediation_events=remediation_events,
            stack_trace=list(self.stack.execution_trace),
            subagent_witnesses=recorded_witnesses,
            thermodynamic_summary=thermo_summary,
            argon_deliberation_tokens=self.argon_deliberation_tokens,
            flash_emission_tokens=self.flash_emission_tokens,
            argon_verification_tokens=self.argon_verification_tokens,
        )

    def _intercept_and_audit_leaf(
        self,
        node: TaskNode,
        leaf: LeafArtifact,
    ):
        """Runs ZeroTrustMicroAuditorRegistry + domain-specific IR formal evaluators."""
        audit_result = ZeroTrustMicroAuditorRegistry.audit_leaf(leaf)
        extra_defects: List[str] = []
        parsed_obj = None

        # Deep semantic IR validation
        if node.task_type == TaskType.LEAF_CONTRACT_FRAGMENT:
            try:
                contract = ContractIR.from_json(leaf.content)
                parsed_obj = contract
                for comp_name in contract.composed_verbs:
                    witness = contract.verify_composition(comp_name)
                    if not witness.is_valid:
                        extra_defects.extend(witness.unresolved_obligations)
            except Exception as e:
                extra_defects.append(f"ContractIR Deserialization/Validation Error: {e}")

        elif node.task_type == TaskType.LEAF_STATECHART_FRAGMENT:
            try:
                chart = StatechartIR.from_json(leaf.content)
                parsed_obj = chart
                report = FormalModelChecker.check(chart)
                if not report.is_certified:
                    extra_defects.extend(report.defect_summary)
            except Exception as e:
                extra_defects.append(f"StatechartIR Deserialization/ModelCheck Error: {e}")

        elif node.task_type == TaskType.LEAF_TOPOLOGY_FRAGMENT:
            try:
                topo = TopologyIR.from_json(leaf.content)
                parsed_obj = topo
                topo_errs = topo.validate_topological_fidelity()
                if topo_errs:
                    extra_defects.extend(topo_errs)
            except Exception as e:
                extra_defects.append(f"TopologyIR Deserialization/Fidelity Error: {e}")

        if extra_defects:
            audit_result.defects.extend(extra_defects)
            audit_result.is_passed = False
            audit_result.remediation_advice = (
                f"Leaf '{leaf.task_id}' failed formal IR/micro-audit:\n" +
                "\n".join(f"- {d}" for d in audit_result.defects)
            )

        return audit_result, extra_defects, parsed_obj

    @staticmethod
    def _commit_verified_leaf(
        leaf_artifact: LeafArtifact,
        audit_result: MicroAuditResult,
        verified_leaves: Dict[str, LeafArtifact],
        audit_certificates: Dict[str, MicroAuditResult],
    ):
        """Enforces [L1-G3B-016]: Commits a leaf ONLY if it holds a valid passing audit certificate."""
        if not audit_result or not audit_result.is_passed or audit_result.task_id != leaf_artifact.task_id:
            raise ZeroBypassInterceptionViolation(
                f"[L1-G3B-016 Violation] Attempted to commit leaf '{leaf_artifact.task_id}' "
                f"without a valid passing MicroAuditResult certificate."
            )
        verified_leaves[leaf_artifact.task_id] = leaf_artifact
        audit_certificates[leaf_artifact.task_id] = audit_result
