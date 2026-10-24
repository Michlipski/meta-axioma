"""Generation 3b Thermodynamic Capital, Physical Token Accounting & Dynamic Budget Calibrator.

Enforces:
- [L1-G3B-009] 60/40 Capital Partition:
  - 60% Exploratory Capital: Leased to recursive decomposition and leaf synthesis.
  - 40% Protected Capital: Strictly reserved for terminal verification sinks.
- Physical Token Metering: Grounded in deterministic BPE-aligned regex token counting.
- Empirical Task-DAG Budget Calibration (`DynamicBudgetCalibrator`):
  Computes realistic, calibrated token budgets and point-spend predictions directly from
  task graph topology (subsystems, leaf count, non-leaf decomposition depth, and retry headroom),
  eliminating arbitrary 100x over-allocation while preserving a 60/40 safety buffer.
- Landauer Bit-Erasure Dissipation: Q = k_B * T * ln(2) * bits_erased (Joules at T=300K).
"""

from dataclasses import dataclass
import math
from pathlib import Path
import re
from typing import Dict, Any, Optional, Union


# Boltzmann constant in J/K
BOLTZMANN_K = 1.380649e-23
# Standard ambient room temperature in Kelvin
AMBIENT_T_KELVIN = 300.0
LN2 = math.log(2)


class PhysicalTokenMeter:
    """Measures physical tokens across strings, files, and directories using standard BPE regex alignment."""

    TOKEN_REGEX = re.compile(r"[a-zA-Z_]\w*|\d+|[^\w\s]|\s+")

    @classmethod
    def count(cls, text: Any) -> int:
        """Counts physical tokens in a string or stringifiable object."""
        if not text:
            return 0
        return len(cls.TOKEN_REGEX.findall(str(text)))

    @classmethod
    def measure_file(cls, path: Union[str, Path]) -> int:
        """Measures physical tokens in a file on disk."""
        p = Path(path)
        if not p.is_file():
            return 0
        try:
            return cls.count(p.read_text(encoding="utf-8", errors="ignore"))
        except Exception:
            return 0

    @classmethod
    def measure_directory(cls, dir_path: Union[str, Path]) -> Dict[str, Any]:
        """Measures physical tokens across all emitted code and data files in a directory."""
        p = Path(dir_path)
        if not p.exists():
            return {"file_count": 0, "total_tokens": 0, "files": {}}

        files_map: Dict[str, int] = {}
        total = 0
        for f in sorted(p.glob("**/*")):
            if (
                f.is_file()
                and not f.name.endswith(".pyc")
                and "__pycache__" not in str(f)
                and f.name not in ("telemetry_ledger.json", "telemetry_dashboard.md")
            ):
                toks = cls.measure_file(f)
                files_map[str(f.relative_to(p))] = toks
                total += toks

        return {"file_count": len(files_map), "total_tokens": total, "files": files_map}


class ThermodynamicExhaustionError(Exception):
    """Raised when exploratory or total token budget is exhausted."""
    pass


class ProtectedCapitalViolation(Exception):
    """Raised when exploratory tasks attempt to consume protected capital."""
    pass


@dataclass
class BudgetEstimate:
    """Empirically calibrated token budget and point-spend prediction for a compilation run."""
    recommended_total_budget: int
    exploratory_cap: int
    protected_floor: int
    predicted_argon_deliberation: int
    predicted_flash_emission: int
    predicted_exploratory_spend: int
    predicted_protected_spend: int
    predicted_total_spend: int
    expected_leaves: int
    expected_fault_retries: int
    safety_margin_factor: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "recommended_total_budget": self.recommended_total_budget,
            "exploratory_cap": self.exploratory_cap,
            "protected_floor": self.protected_floor,
            "predicted_argon_deliberation": self.predicted_argon_deliberation,
            "predicted_flash_emission": self.predicted_flash_emission,
            "predicted_exploratory_spend": self.predicted_exploratory_spend,
            "predicted_protected_spend": self.predicted_protected_spend,
            "predicted_total_spend": self.predicted_total_spend,
            "expected_leaves": self.expected_leaves,
            "expected_fault_retries": self.expected_fault_retries,
            "safety_margin_factor": self.safety_margin_factor,
        }


class DynamicBudgetCalibrator:
    """Calibrates compilation token budgets from Task-DAG structure and empirical BPE unit costs."""

    # Empirical BPE token unit baselines measured on System G3b substrate
    SOC_NORMALIZATION_BASELINE = 260
    ARGON_NON_LEAF_NODE_COST = 560
    ARGON_RETRY_DELIBERATION_COST = 265
    FLASH_LEAF_EMISSION_COST = 580
    ARGON_LEAF_VERIFICATION_COST = 275

    # Optional external LLM API context-window multiplier when running multi-turn chat sessions
    LLM_CONTEXT_WINDOW_OVERHEAD_PER_STEP = 12000

    @classmethod
    def estimate(
        cls,
        subsystems_count: int = 1,
        leaves_per_subsystem: int = 4,
        non_leaf_nodes_per_subsystem: int = 2,
        expected_fault_retries: int = 2,
        safety_margin_factor: float = 1.25,
        include_llm_context_overhead: bool = False,
    ) -> BudgetEstimate:
        """Computes a realistic 60/40 token budget and point-spend prediction."""
        if subsystems_count < 1:
            raise ValueError("subsystems_count must be >= 1")
        if leaves_per_subsystem < 1:
            raise ValueError("leaves_per_subsystem must be >= 1")
        if safety_margin_factor < 1.0:
            raise ValueError("safety_margin_factor must be >= 1.0")

        total_non_leaf = subsystems_count * non_leaf_nodes_per_subsystem
        total_leaves = subsystems_count * leaves_per_subsystem

        argon_delib = (
            cls.SOC_NORMALIZATION_BASELINE
            + (total_non_leaf * cls.ARGON_NON_LEAF_NODE_COST)
            + (expected_fault_retries * cls.ARGON_RETRY_DELIBERATION_COST)
        )
        flash_emit = (total_leaves + expected_fault_retries) * cls.FLASH_LEAF_EMISSION_COST
        argon_verify = (total_leaves + expected_fault_retries) * cls.ARGON_LEAF_VERIFICATION_COST

        if include_llm_context_overhead:
            argon_delib += (total_non_leaf + 1) * cls.LLM_CONTEXT_WINDOW_OVERHEAD_PER_STEP
            flash_emit += (total_leaves + expected_fault_retries) * cls.LLM_CONTEXT_WINDOW_OVERHEAD_PER_STEP
            argon_verify += (total_leaves + expected_fault_retries) * (cls.LLM_CONTEXT_WINDOW_OVERHEAD_PER_STEP // 2)

        pred_exploratory = argon_delib + flash_emit
        pred_protected = argon_verify
        pred_total = pred_exploratory + pred_protected

        # Size the 60/40 budget so both exploratory and protected pools have `safety_margin_factor` headroom
        needed_from_expl = (pred_exploratory * safety_margin_factor) / 0.60
        needed_from_prot = (pred_protected * safety_margin_factor) / 0.40
        raw_total = max(needed_from_expl, needed_from_prot)

        # Round up to nearest 100 tokens
        recommended_total = int(math.ceil(raw_total / 100.0)) * 100
        protected_floor = int(recommended_total * 0.40)
        exploratory_cap = recommended_total - protected_floor

        return BudgetEstimate(
            recommended_total_budget=recommended_total,
            exploratory_cap=exploratory_cap,
            protected_floor=protected_floor,
            predicted_argon_deliberation=argon_delib,
            predicted_flash_emission=flash_emit,
            predicted_exploratory_spend=pred_exploratory,
            predicted_protected_spend=pred_protected,
            predicted_total_spend=pred_total,
            expected_leaves=total_leaves,
            expected_fault_retries=expected_fault_retries,
            safety_margin_factor=safety_margin_factor,
        )

    # Empirical structural unit costs (BPE tokens per architectural graph primitive)
    TOKENS_PER_SOC_TREE_NODE = 374
    TOKENS_PER_CONTRACT_UNIT = 292  # per noun, sub-contract, or composed verb
    TOKENS_PER_STATECHART_STATE = 158
    TOKENS_PER_TOPOLOGY_ELEMENT = 96  # per node or channel
    TOKENS_PER_CODE_LEAF = 220
    TOKENS_PER_APP_MODULE = 3400  # for full production application files (server, engine, UI, dashboard, tests)
    LEAF_INVOCATION_OVERHEAD = 180

    @staticmethod
    def _count_soc_tree_nodes(soc_dict: Dict[str, Any]) -> int:
        if not soc_dict:
            return 1
        children = soc_dict.get("children", []) or soc_dict.get("sub_socs", [])
        return (
            1
            + len(soc_dict.get("actors", []))
            + len(soc_dict.get("frictions", []))
            + len(soc_dict.get("constraints", []))
            + len(children)
        )

    @staticmethod
    def _count_statechart_states(node_dict: Dict[str, Any]) -> int:
        if not node_dict:
            return 0
        states = node_dict.get("states", {})
        return 1 + sum(DynamicBudgetCalibrator._count_statechart_states(ch) for ch in states.values())

    @classmethod
    def estimate_from_structural_scope(
        cls,
        soc_tree_nodes: int = 1,
        num_nouns: int = 1,
        num_sub_contracts: int = 2,
        num_composed_verbs: int = 1,
        num_statechart_states: int = 6,
        num_topology_nodes: int = 2,
        num_topology_channels: int = 1,
        num_code_leaves: int = 1,
        expected_fault_retries: int = 0,
        safety_margin_factor: float = 1.25,
        is_full_application: bool = False,
        tokens_per_code_leaf: Optional[int] = None,
        include_llm_context_overhead: bool = False,
    ) -> BudgetEstimate:
        """A-priori structural complexity estimator for Proposal Time (Directive 3).

        Predicts BPE token expenditure solely from architectural graph counts
        (SoC tree depth, nouns, sub-contracts, statechart states, topology nodes/channels)
        BEFORE any IR JSON or source code is written, preventing circular post-hoc calibration.
        When is_full_application=True or multi-module scope is supplied, accurately estimates
        comprehensive production application workloads (>= 100,000 tokens).
        """
        soc_tokens = max(cls.SOC_NORMALIZATION_BASELINE, soc_tree_nodes * cls.TOKENS_PER_SOC_TREE_NODE)
        payload_tokens = soc_tokens + 60
        argon_delib = (
            soc_tokens
            + (2 * payload_tokens)
            + 300
            + (expected_fault_retries * cls.ARGON_RETRY_DELIBERATION_COST)
        )

        contract_units = max(1, num_nouns + num_sub_contracts + num_composed_verbs)
        c_toks = contract_units * cls.TOKENS_PER_CONTRACT_UNIT
        s_toks = max(1, num_statechart_states) * cls.TOKENS_PER_STATECHART_STATE
        t_toks = max(1, num_topology_nodes + num_topology_channels) * cls.TOKENS_PER_TOPOLOGY_ELEMENT

        leaf_unit_cost = (
            tokens_per_code_leaf
            if tokens_per_code_leaf is not None
            else (cls.TOKENS_PER_APP_MODULE if is_full_application else cls.TOKENS_PER_CODE_LEAF)
        )
        code_toks = max(1, num_code_leaves) * leaf_unit_cost

        total_leaves = 3 + max(1, num_code_leaves)
        flash_emit = (
            (c_toks + s_toks + t_toks + code_toks)
            + (total_leaves * cls.LEAF_INVOCATION_OVERHEAD)
            + (expected_fault_retries * (t_toks + cls.LEAF_INVOCATION_OVERHEAD))
        )
        argon_verify = (
            (c_toks // 2)
            + (s_toks // 2)
            + (t_toks // 2)
            + (code_toks // 2)
            + (expected_fault_retries * max(32, t_toks // 2))
        )

        if include_llm_context_overhead:
            argon_delib += (soc_tree_nodes + 2) * cls.LLM_CONTEXT_WINDOW_OVERHEAD_PER_STEP
            flash_emit += (total_leaves + expected_fault_retries) * cls.LLM_CONTEXT_WINDOW_OVERHEAD_PER_STEP
            argon_verify += (total_leaves + expected_fault_retries) * (cls.LLM_CONTEXT_WINDOW_OVERHEAD_PER_STEP // 2)

        pred_exploratory = argon_delib + flash_emit
        pred_protected = argon_verify
        pred_total = pred_exploratory + pred_protected

        needed_from_expl = (pred_exploratory * safety_margin_factor) / 0.60
        needed_from_prot = (pred_protected * safety_margin_factor) / 0.40
        raw_total = max(needed_from_expl, needed_from_prot)

        recommended_total = int(math.ceil(raw_total / 100.0)) * 100
        protected_floor = int(recommended_total * 0.40)
        exploratory_cap = recommended_total - protected_floor

        return BudgetEstimate(
            recommended_total_budget=recommended_total,
            exploratory_cap=exploratory_cap,
            protected_floor=protected_floor,
            predicted_argon_deliberation=argon_delib,
            predicted_flash_emission=flash_emit,
            predicted_exploratory_spend=pred_exploratory,
            predicted_protected_spend=pred_protected,
            predicted_total_spend=pred_total,
            expected_leaves=total_leaves,
            expected_fault_retries=expected_fault_retries,
            safety_margin_factor=safety_margin_factor,
        )

    @classmethod
    def estimate_for_domain_spec(
        cls,
        soc_dict: Dict[str, Any],
        domain_spec: Dict[str, Any],
        required_invariants: Optional[Any] = None,
        expected_fault_retries: int = 0,
        safety_margin_factor: float = 1.25,
    ) -> BudgetEstimate:
        """Extracts structural graph counts (NOT string token measurements) and delegates to estimate_from_structural_scope."""
        soc_tree_nodes = cls._count_soc_tree_nodes(soc_dict)
        c_ir = domain_spec.get("contract_ir", {})
        s_ir = domain_spec.get("statechart_ir", {})
        t_ir = domain_spec.get("topology_ir", {})

        num_nouns = len(c_ir.get("nouns", {})) or 1
        num_sub_contracts = len(c_ir.get("sub_contracts", {})) or 2
        num_composed_verbs = len(c_ir.get("composed_verbs", {})) or 1
        num_states = cls._count_statechart_states(s_ir.get("root", {})) or 6
        num_nodes = len(t_ir.get("nodes", {})) or 2
        num_channels = len(t_ir.get("channels", [])) or 1

        return cls.estimate_from_structural_scope(
            soc_tree_nodes=soc_tree_nodes,
            num_nouns=num_nouns,
            num_sub_contracts=num_sub_contracts,
            num_composed_verbs=num_composed_verbs,
            num_statechart_states=num_states,
            num_topology_nodes=num_nodes,
            num_topology_channels=num_channels,
            num_code_leaves=1,
            expected_fault_retries=expected_fault_retries,
            safety_margin_factor=safety_margin_factor,
        )



@dataclass
class ThermodynamicLedger:
    """Tracks token expenditure, prediction accuracy, and Landauer bit-erasure dissipation."""
    total_budget: int
    exploratory_cap: int
    protected_floor: int
    exploratory_spent: int = 0
    protected_spent: int = 0
    bits_erased: int = 0
    dissipated_joules: float = 0.0
    predicted_total_spend: Optional[int] = None
    predicted_exploratory_spend: Optional[int] = None

    @classmethod
    def create(
        cls,
        total_budget: Optional[int] = None,
        predicted_total_spend: Optional[int] = None,
        predicted_exploratory_spend: Optional[int] = None,
    ) -> "ThermodynamicLedger":
        """Creates a new ledger with exact 60/40 capital partition.

        If total_budget is None, uses DynamicBudgetCalibrator.estimate() to set a realistic budget.
        """
        if total_budget is None:
            est = DynamicBudgetCalibrator.estimate()
            total_budget = est.recommended_total_budget
            predicted_total_spend = est.predicted_total_spend
            predicted_exploratory_spend = est.predicted_exploratory_spend

        protected = int(total_budget * 0.40)
        exploratory = total_budget - protected
        return cls(
            total_budget=total_budget,
            exploratory_cap=exploratory,
            protected_floor=protected,
            predicted_total_spend=predicted_total_spend,
            predicted_exploratory_spend=predicted_exploratory_spend,
        )

    @classmethod
    def create_calibrated(
        cls,
        subsystems_count: int = 1,
        leaves_per_subsystem: int = 4,
        expected_fault_retries: int = 2,
        safety_margin_factor: float = 1.25,
    ) -> "ThermodynamicLedger":
        """Creates a ledger calibrated directly from the expected Task-DAG workload."""
        est = DynamicBudgetCalibrator.estimate(
            subsystems_count=subsystems_count,
            leaves_per_subsystem=leaves_per_subsystem,
            expected_fault_retries=expected_fault_retries,
            safety_margin_factor=safety_margin_factor,
        )
        return cls.create(
            total_budget=est.recommended_total_budget,
            predicted_total_spend=est.predicted_total_spend,
            predicted_exploratory_spend=est.predicted_exploratory_spend,
        )

    def spend_exploratory(self, tokens: int, bits_erased: int = 0) -> int:
        """Charges tokens against the exploratory capital pool."""
        if self.exploratory_spent + tokens > self.exploratory_cap:
            raise ProtectedCapitalViolation(
                f"Exploratory token spend ({self.exploratory_spent + tokens}) exceeds "
                f"exploratory cap ({self.exploratory_cap}). "
                f"Protected capital ({self.protected_floor} tokens) is immutable."
            )
        self.exploratory_spent += tokens
        self._record_erasure(bits_erased)
        return self.exploratory_spent

    def spend_protected(self, tokens: int, bits_erased: int = 0) -> int:
        """Charges tokens against the protected terminal verification pool."""
        if self.protected_spent + tokens > self.protected_floor:
            raise ThermodynamicExhaustionError(
                f"Protected verification spend ({self.protected_spent + tokens}) exceeds "
                f"protected budget floor ({self.protected_floor})."
            )
        self.protected_spent += tokens
        self._record_erasure(bits_erased)
        return self.protected_spent

    def _record_erasure(self, bits: int):
        """Calculates Landauer dissipation Q = k_B * T * ln(2) * bits."""
        if bits > 0:
            self.bits_erased += bits
            heat = BOLTZMANN_K * AMBIENT_T_KELVIN * LN2 * bits
            self.dissipated_joules += heat

    def to_dict(self) -> Dict[str, Any]:
        """Returns structured dictionary of ledger state including prediction accuracy."""
        total_spent = self.exploratory_spent + self.protected_spent
        utilization = round((total_spent / self.total_budget * 100), 2) if self.total_budget else 0.0
        expl_utilization = (
            round((self.exploratory_spent / self.exploratory_cap * 100), 2)
            if self.exploratory_cap else 0.0
        )

        pred_total = self.predicted_total_spend
        if pred_total and pred_total > 0 and total_spent > 0:
            error_ratio = abs(total_spent - pred_total) / pred_total
            prediction_accuracy_pct = round(max(0.0, (1.0 - error_ratio) * 100.0), 2)
        else:
            prediction_accuracy_pct = None

        return {
            "total_budget": self.total_budget,
            "exploratory_cap": self.exploratory_cap,
            "protected_floor": self.protected_floor,
            "exploratory_spent": self.exploratory_spent,
            "protected_spent": self.protected_spent,
            "total_spent": total_spent,
            "utilization_pct": utilization,
            "exploratory_utilization_pct": expl_utilization,
            "predicted_total_spend": self.predicted_total_spend,
            "predicted_exploratory_spend": self.predicted_exploratory_spend,
            "prediction_accuracy_pct": prediction_accuracy_pct,
            "unspent_reserve": self.total_budget - total_spent,
            "exploratory_remaining": self.exploratory_cap - self.exploratory_spent,
            "protected_remaining": self.protected_floor - self.protected_spent,
            "bits_erased": self.bits_erased,
            "dissipated_joules": self.dissipated_joules,
        }
