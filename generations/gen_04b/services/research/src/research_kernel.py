"""Generation 4b Sovereign Research Kernel (`soc_g4b_researcher`).

Enforces:
- [L1-G4B-001] Decoupled Research Sovereignty: Research operates independently of builder enclaves.
- [L1-G4B-002] The Zero-Code Research Boundary Invariant:
  The research service is physically and logically prohibited from writing production application
  code files (.py, .js, .html, etc.) or executing build commands. Research tools are strictly
  read-only introspection and schema emission.
- [L1-G3B-000] Waterloo Tier 1 Situation of Concern Grounding.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import time
from typing import Any, Dict, List, Optional, Set
import uuid

from .domain_models import (
    BottleneckType,
    ConstraintAnalysis,
    DomainInvariantViolation,
    EpistemicCrucibleTarget,
    FailureModeModel,
    HypothesisDefinition,
    MerkleDagWitness,
    ResearchDeliverableBundle,
    TradeoffMatrix,
)


class ZeroCodeBoundaryViolation(Exception):
    """Raised when the research engine attempts to emit production code or bypass read-only bounds."""
    pass


class ResearchKernelStateError(Exception):
    """Raised when operations are invoked out of sequential lifecycle order."""
    pass


class SovereignResearchKernel:
    """The Sovereign Research Kernel enforcing decoupled epistemic discovery."""

    BANNED_WRITE_EXTENSIONS: Set[str] = {
        ".py", ".js", ".ts", ".html", ".css", ".sh", ".bash", ".c", ".cpp", ".rs", ".go"
    }

    def __init__(
        self,
        kernel_id: Optional[str] = None,
        node_ip: str = "192.168.40.10",
        port: int = 8201,
        repo_root: Optional[Path] = None,
    ):
        self.kernel_id = kernel_id or f"kernel_{uuid.uuid4().hex[:8]}"
        self.node_ip = node_ip
        self.port = port
        self.repo_root = repo_root or Path.cwd()

        # Invariant check: Topological fidelity ([L1-G3B-012])
        if self.node_ip.startswith("127.") or self.node_ip in ("localhost", "::1"):
            raise DomainInvariantViolation(
                f"[L1-G3B-012 Violation] Kernel cannot bind to loopback address: {self.node_ip}"
            )

        self.current_target: Optional[EpistemicCrucibleTarget] = None
        self.active_hypotheses: Dict[str, HypothesisDefinition] = {}
        self.active_constraints: Dict[str, ConstraintAnalysis] = {}
        self.active_failure_models: Dict[str, FailureModeModel] = {}
        self.active_tradeoff_matrices: Dict[str, TradeoffMatrix] = {}
        self.deliverable_vault: Dict[str, ResearchDeliverableBundle] = {}
        self.audit_log: List[Dict[str, Any]] = []

    def enforce_zero_code_boundary(self, attempted_path: str, action: str) -> None:
        """Physical enforcement of [L1-G4B-002]. Prohibits code-writing tools."""
        p = Path(attempted_path)
        if p.suffix.lower() in self.BANNED_WRITE_EXTENSIONS or action.lower() in ("write", "execute", "compile"):
            self._log_event("ZERO_CODE_VIOLATION_TRAPPED", {"path": attempted_path, "action": action})
            raise ZeroCodeBoundaryViolation(
                f"[L1-G4B-002 Violation] Sovereign Research Kernel is prohibited from {action} "
                f"operation on code file '{attempted_path}'. Research service has strictly read-only tools."
            )

    def initialize_campaign(self, target: EpistemicCrucibleTarget) -> Dict[str, Any]:
        """Initializes a formal epistemic research campaign for a Waterloo SoC."""
        target.validate_invariants()
        self.current_target = target
        event = {
            "kernel_id": self.kernel_id,
            "event": "CAMPAIGN_INITIALIZED",
            "target_id": target.target_id,
            "problem_statement": target.problem_statement,
            "lease": target.exploratory_token_lease,
            "timestamp": time.time_ns(),
        }
        self._log_event("CAMPAIGN_INITIALIZED", event)
        return event

    def formulate_hypothesis(
        self,
        theoretical_claim: str,
        governing_axioms: List[str],
        expected_complexity_class: str,
        formal_conjecture_z3: str,
        hypothesis_id: Optional[str] = None,
    ) -> HypothesisDefinition:
        """Synthesizes a formally stated hypothesis with SMT conjecture."""
        if not self.current_target:
            raise ResearchKernelStateError("Campaign must be initialized before formulating hypotheses.")

        hyp_id = hypothesis_id or f"hyp_{uuid.uuid4().hex[:8]}"
        hyp = HypothesisDefinition(
            hypothesis_id=hyp_id,
            theoretical_claim=theoretical_claim,
            governing_axioms=governing_axioms,
            expected_complexity_class=expected_complexity_class,
            formal_conjecture_z3=formal_conjecture_z3,
        )
        hyp.validate_invariants()
        self.active_hypotheses[hyp_id] = hyp
        self._log_event("HYPOTHESIS_FORMULATED", hyp.to_dict())
        return hyp

    def analyze_constraints(
        self,
        physical_latency_budget_ms: int,
        landauer_erasure_budget_bits: int,
        topological_interfaces: List[str],
        vetoed_negative_axioms: List[str],
        analysis_id: Optional[str] = None,
    ) -> ConstraintAnalysis:
        """Extracts physical and topological boundary limits."""
        ca_id = analysis_id or f"ca_{uuid.uuid4().hex[:8]}"
        ca = ConstraintAnalysis(
            analysis_id=ca_id,
            physical_latency_budget_ms=physical_latency_budget_ms,
            landauer_erasure_budget_bits=landauer_erasure_budget_bits,
            topological_interfaces=topological_interfaces,
            vetoed_negative_axioms=vetoed_negative_axioms,
        )
        ca.validate_invariants()
        self.active_constraints[ca_id] = ca
        self._log_event("CONSTRAINTS_ANALYZED", ca.to_dict())
        return ca

    def model_failure_modes(
        self,
        byzantine_vectors: List[str],
        partition_scenarios: List[str],
        deadlock_states: List[str],
        recovery_pipeline_urns: List[str],
        model_id: Optional[str] = None,
    ) -> FailureModeModel:
        """Models Byzantine, partition, and deadlock failure topologies."""
        fm_id = model_id or f"fm_{uuid.uuid4().hex[:8]}"
        fm = FailureModeModel(
            model_id=fm_id,
            byzantine_vectors=byzantine_vectors,
            partition_scenarios=partition_scenarios,
            deadlock_states=deadlock_states,
            recovery_pipeline_urns=recovery_pipeline_urns,
        )
        fm.validate_invariants()
        self.active_failure_models[fm_id] = fm
        self._log_event("FAILURE_MODES_MODELED", fm.to_dict())
        return fm

    def evaluate_tradeoffs(
        self,
        evaluated_options: List[str],
        pareto_frontier_options: List[str],
        scoring_weights: Dict[str, float],
        selection_proof: str,
        matrix_id: Optional[str] = None,
    ) -> TradeoffMatrix:
        """Formal multi-objective Pareto trade-off adjudication."""
        tm_id = matrix_id or f"tm_{uuid.uuid4().hex[:8]}"
        tm = TradeoffMatrix(
            matrix_id=tm_id,
            evaluated_options=evaluated_options,
            pareto_frontier_options=pareto_frontier_options,
            scoring_weights=scoring_weights,
            selection_proof=selection_proof,
        )
        tm.validate_invariants()
        self.active_tradeoff_matrices[tm_id] = tm
        self._log_event("TRADEOFFS_EVALUATED", tm.to_dict())
        return tm

    def compile_deliverable_bundle(
        self,
        target_soc_id: str,
        hypothesis_id: str,
        constraint_analysis_id: str,
        failure_mode_id: str,
        tradeoff_matrix_id: str,
        merkle_root: str,
        bundle_id: Optional[str] = None,
    ) -> ResearchDeliverableBundle:
        """Assembles verified sub-deliverables into an immutable ResearchDeliverableBundle."""
        if hypothesis_id not in self.active_hypotheses:
            raise KeyError(f"Unknown hypothesis_id: {hypothesis_id}")
        if constraint_analysis_id not in self.active_constraints:
            raise KeyError(f"Unknown constraint_analysis_id: {constraint_analysis_id}")
        if failure_mode_id not in self.active_failure_models:
            raise KeyError(f"Unknown failure_mode_id: {failure_mode_id}")
        if tradeoff_matrix_id not in self.active_tradeoff_matrices:
            raise KeyError(f"Unknown tradeoff_matrix_id: {tradeoff_matrix_id}")

        b_id = bundle_id or f"rdb_{uuid.uuid4().hex[:8]}"

        # Compute deterministic reference architecture hash over inputs
        raw_payload = json.dumps(
            {
                "soc": target_soc_id,
                "hyp": self.active_hypotheses[hypothesis_id].to_dict(),
                "ca": self.active_constraints[constraint_analysis_id].to_dict(),
                "fm": self.active_failure_models[failure_mode_id].to_dict(),
                "tm": self.active_tradeoff_matrices[tradeoff_matrix_id].to_dict(),
            },
            sort_keys=True,
        )
        ref_hash = hashlib.sha256(raw_payload.encode("utf-8")).hexdigest()

        bundle = ResearchDeliverableBundle(
            bundle_id=b_id,
            target_soc_id=target_soc_id,
            hypothesis_id=hypothesis_id,
            constraint_analysis_id=constraint_analysis_id,
            failure_mode_id=failure_mode_id,
            tradeoff_matrix_id=tradeoff_matrix_id,
            reference_architecture_hash=ref_hash,
            merkle_root=merkle_root,
            is_certified=False,
            metadata={"created_at_ns": time.time_ns(), "kernel_id": self.kernel_id},
        )
        bundle.validate_invariants()
        self.deliverable_vault[b_id] = bundle
        self._log_event("BUNDLE_COMPILED", bundle.to_dict())
        return bundle

    def certify_deliverable_bundle(self, bundle_id: str, auditor_signature: str) -> ResearchDeliverableBundle:
        """Formally certifies a bundle upon passing all adversarial verification sinks."""
        if bundle_id not in self.deliverable_vault:
            raise KeyError(f"Bundle not found: {bundle_id}")

        bundle = self.deliverable_vault[bundle_id]
        bundle.is_certified = True
        bundle.metadata["certified_by"] = auditor_signature
        bundle.metadata["certified_at_ns"] = time.time_ns()
        bundle.validate_invariants()
        self._log_event("BUNDLE_CERTIFIED", {"bundle_id": bundle_id, "signature": auditor_signature})
        return bundle

    def introspect_repository_ast(self, relative_path: str) -> Dict[str, Any]:
        """Read-only introspection of repository AST skeletons ([L1-G4B-007])."""
        target = (self.repo_root / relative_path).resolve()
        if not target.exists() or not target.is_file():
            raise FileNotFoundError(f"Cannot introspect non-existent file: {relative_path}")

        code = target.read_text(encoding="utf-8")
        # Deterministic AST skeleton summary: lines, size, sha256
        h = hashlib.sha256(code.encode("utf-8")).hexdigest()
        lines = [line.strip() for line in code.splitlines() if line.strip() and not line.strip().startswith("#")]
        classes = [line for line in lines if line.startswith("class ")]
        functions = [line for line in lines if line.startswith("def ")]

        return {
            "path": relative_path,
            "sha256": h,
            "total_lines": len(code.splitlines()),
            "classes": classes,
            "functions": functions,
            "skeleton_hash": f"sha256:{h}",
        }

    def _log_event(self, event_name: str, payload: Dict[str, Any]) -> None:
        self.audit_log.append({
            "event": event_name,
            "kernel_id": self.kernel_id,
            "timestamp_ns": time.time_ns(),
            "payload": payload,
        })
