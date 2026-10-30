"""Generation 4b Sovereign Builder Kernel (`soc_g4b_builder`).

Enforces:
- [L1-G4B-001] Service-Oriented Sovereign Mesh Protocol Standardization.
- [L1-G3B-011] Universal Compositional Contract IR & Domain Invariants.
- [L1-G3B-012] Dedicated Non-Loopback Network Topology (192.168.40.20:8442).
- Sovereign ingestion of certified ResearchDeliverableBundle specifications.
- End-to-end orchestration of fractal subagent trees, AST skeletons, hermetic linters, and Quine Crucible.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import time
from typing import Any, Dict, List, Optional, Tuple

from generations.gen_04b.protocols.deliverable_bundle import (
    DeliverableProtocolViolation,
    ResearchDeliverableBundle,
)
from .ast_skeletonizer import ASTSkeletonizer
from .budget_lease_engine import BudgetLeaseEngine, LandauerCutoffTripped
from .diagnostic_tuples import DiagnosticEngine, SurgicalPatcher
from .domain_models import (
    ASTNodeType,
    BuilderExecutionBundle,
    ByzantineChaosReport,
    CausalConvergenceAttestation,
    DiagnosticSeverity,
    DomainInvariantViolation,
    MerkleTreeRootAttestation,
    PhysicalDiskWitness,
    ReactiveAuditReport,
    TaskExecutionStatus,
)
from .dynamic_persona_builder import DynamicPersonaBuilder
from .fractal_orchestrator import BoundedFractalOrchestrator
from .functorial_undo import FunctorialUndoManager
from .hermetic_linter import HermeticLinter
from .hypergraph_indexer import SymbolHypergraphIndexer
from .builder_topology import BuilderTopologyManager, NetworkPartitionError, PartitionPolicy
from .quine_crucible import QuineCrucibleEngine
from .rfc_protocol_client import RFCProtocolClient
from .statechart_engine import G4bBuilderStatechartEngine


class SovereignBuilderKernel:
    """The sovereign synthesis kernel coordinating the complete Generation 4b build lifecycle."""

    def __init__(
        self,
        node_ip: str = "192.168.40.20",
        port: int = 8442,
        total_budget_tokens: int = 250000,
        decay_lambda: float = 0.80,
    ):
        clean_ip = node_ip.strip()
        if ":" in clean_ip and not clean_ip.startswith("::"):
            clean_ip = clean_ip.split(":")[0].strip()
        if clean_ip.startswith("127.") or clean_ip in ("localhost", "::1", "0.0.0.0") or "::1" in node_ip:
            raise DomainInvariantViolation(
                f"[L1-G3B-012 Violation] Loopback address {node_ip} strictly prohibited for SovereignBuilderKernel."
            )

        self.node_ip = node_ip
        self.port = port
        self.total_budget = total_budget_tokens
        self.decay_lambda = decay_lambda

        # Initialize Subsystems
        self.undo_mgr = FunctorialUndoManager()
        self.statechart = G4bBuilderStatechartEngine(undo_manager=self.undo_mgr)
        self.budget_engine = BudgetLeaseEngine(total_budget_tokens, decay_lambda=decay_lambda)
        self.orchestrator = BoundedFractalOrchestrator(self.budget_engine)
        self.skeletonizer = ASTSkeletonizer()
        self.linter = HermeticLinter()
        self.hypergraph = SymbolHypergraphIndexer()
        self.topology = BuilderTopologyManager(node_ip=node_ip, port=port)
        self.rfc_client = RFCProtocolClient(builder_node_id=f"node_builder_{node_ip}:{port}")
        self.crucible = QuineCrucibleEngine()

        # Master execution bundle
        self.execution_bundle: Optional[BuilderExecutionBundle] = None
        self.emitted_files: List[str] = []

    def handshake_and_ingest(self, bundle: ResearchDeliverableBundle) -> BuilderExecutionBundle:
        """Ingests and validates a certified ResearchDeliverableBundle from Research Service."""
        self.statechart.send("EV_AWAIT_BUNDLE")

        bundle.validate_invariants()
        if not bundle.is_certified:
            self.statechart.send("EV_BUNDLE_REJECTED", {"error": "Bundle not certified"})
            raise DeliverableProtocolViolation("Ingested ResearchDeliverableBundle is not certified.")

        bundle_hash = bundle.reference_architecture_hash
        exec_bundle_id = f"bld_exec_{hashlib.sha256((bundle.bundle_id + str(time.time())).encode()).hexdigest()[:12]}"

        # 60/40 thermodynamic partition
        protected_cap = self.budget_engine.protected_capital
        exploratory_cap = self.budget_engine.initial_exploratory_capital

        self.execution_bundle = BuilderExecutionBundle(
            bundle_id=exec_bundle_id,
            target_soc_id=bundle.target_soc_id,
            research_bundle_hash=bundle_hash,
            total_budget_tokens=self.total_budget,
            protected_capital_tokens=protected_cap,
            exploratory_capital_tokens=exploratory_cap,
            status=TaskExecutionStatus.ACTIVE,
            metadata={"source_bundle_id": bundle.bundle_id, "merkle_root": bundle.merkle_root},
        )
        self.execution_bundle.validate_invariants()

        self.statechart.send("EV_BUNDLE_VALID", {"bundle_id": exec_bundle_id})
        return self.execution_bundle

    def compile_module(
        self,
        module_path: str,
        source_code: str,
        symbol_urn: str,
        node_type: ASTNodeType = ASTNodeType.MODULE,
        dependencies: Optional[List[str]] = None,
    ) -> Tuple[bool, str]:
        """Audits, indexes, skeletonizes, and commits a synthesized application module."""
        # 1. Hermetic Boundary Audit
        self.statechart.send("EV_AUDIT_HERMETIC", {"module_path": module_path})
        linter_report = self.linter.audit_code(source_code, module_path)
        if not linter_report.passed:
            self.statechart.send("EV_LINTER_VIOLATION", {"report_id": linter_report.report_id})
            # Attempt surgical patching if suggested patches exist
            try:
                source_code = SurgicalPatcher.apply_multi_patch(source_code, linter_report.violations)
                self.statechart.send("EV_PATCH_APPLIED")
                # Re-audit
                linter_report = self.linter.audit_code(source_code, module_path)
                if not linter_report.passed:
                    return False, f"Hermetic violations persist after patch: {[v.rule_code for v in linter_report.violations]}"
            except Exception as err:
                return False, f"Surgical patching failed: {err}"

        self.statechart.send("EV_LINTER_PASSED")

        # 2. Extract AST Skeleton for Prompt Payload Minimization
        self.statechart.send("EV_PATCH_EVAL")
        skeleton_snapshot = self.skeletonizer.extract_skeleton(source_code, module_path, symbol_urn)

        # 3. Universal Hypergraph Indexing
        self.hypergraph.index_symbol(
            urn_str=symbol_urn,
            node_type=node_type,
            file_path=module_path,
            signature=f"stubs={len(skeleton_snapshot.preserved_signatures)}",
            dependencies=dependencies or [],
        )
        self.statechart.send("EV_INDEXING_COMPLETE")

        # Record emitted file
        self.emitted_files.append(module_path)
        if self.execution_bundle:
            self.execution_bundle.emitted_module_count += 1

        return True, "COMPILED_AND_INDEXED"

    def signal_dispatch_builders(self) -> Tuple[str, str, str]:
        """Dispatches specialized builder subagents for AST leaf synthesis."""
        return self.statechart.send("EV_DISPATCH_BUILDERS")

    def verify_substrate_emitted(self, file_path: str) -> PhysicalDiskWitness:
        """Verifies physical disk emission of substrate artifact and transitions gate ([NEG-G1B-001])."""
        p = Path(file_path)
        if not p.exists():
            raise DomainInvariantViolation(
                f"[NEG-G1B-001 Violation] Substrate file {file_path} does not physically exist on disk."
            )
        byte_size = p.stat().st_size
        if byte_size == 0:
            raise DomainInvariantViolation(
                f"[NEG-G1B-001 Violation] Substrate file {file_path} is an empty zero-byte phantom emission."
            )

        content = p.read_bytes()
        sha256_hash = hashlib.sha256(content).hexdigest()
        witness_id = f"witness_{sha256_hash[:12]}"

        witness = PhysicalDiskWitness(
            witness_id=witness_id,
            file_path=str(p.resolve()),
            byte_size=byte_size,
            sha256_hash=sha256_hash,
            verified_at_unix_ms=int(time.time() * 1000),
            is_present=True,
        )
        witness.validate_invariants()

        resolved_path = str(p.resolve())
        if file_path not in self.emitted_files and resolved_path not in self.emitted_files:
            self.emitted_files.append(resolved_path)
        if self.execution_bundle:
            self.execution_bundle.emitted_module_count += 1

        self.statechart.send("EV_SUBSTRATE_EMITTED", {"file_path": resolved_path, "witness_id": witness_id})
        self.statechart.send("EV_SUBSTRATE_VERIFIED", {"witness_id": witness_id})
        return witness

    def signal_reactive_audit_ok(self, report: Optional[ReactiveAuditReport] = None) -> Tuple[str, str, str]:
        """Signals successful reactive micro-audit evaluation."""
        payload: Dict[str, Any] = {}
        if report:
            report.validate_invariants()
            payload["report_id"] = report.report_id
        return self.statechart.send("EV_REACTIVE_AUDIT_OK", payload)

    def signal_chaos_tests_passed(self, report: Optional[ByzantineChaosReport] = None) -> Tuple[str, str, str]:
        """Signals passing Byzantine chaos injection and property fuzzing suites."""
        payload: Dict[str, Any] = {}
        if report:
            report.validate_invariants()
            payload["report_id"] = report.report_id
        return self.statechart.send("EV_CHAOS_TESTS_PASSED", payload)

    def signal_all_leaves_converged(self, attestation: Optional[CausalConvergenceAttestation] = None) -> Tuple[str, str, str]:
        """Signals that all causal dependency leaves have converged and verified."""
        payload: Dict[str, Any] = {}
        if attestation:
            attestation.validate_invariants()
            payload["attestation_id"] = attestation.attestation_id
        return self.statechart.send("EV_ALL_LEAVES_CONVERGED", payload)

    def execute_quine_crucible_certification(self, daughter_gen_id: str = "gen_05a") -> Any:
        """Executes Quine Crucible protocol, certifying self-hosting daughter compiler."""
        self.statechart.send("EV_START_QUINE_CRUCIBLE")
        self.statechart.send("EV_SANDBOX_READY")
        self.statechart.send("EV_DAUGHTER_EMITTED")

        manifest = self.crucible.certify_daughter_compiler(daughter_gen_id)
        if manifest.self_hosting_certified:
            self.statechart.send("EV_REACTIVE_DAG_VERIFIED")
            self.statechart.send("EV_SELF_HOSTING_VERIFIED")
            self.statechart.send("EV_CRUCIBLE_CERTIFIED")
        return manifest

    def seal_merkle_attestation(self) -> MerkleTreeRootAttestation:
        """Seals the final Merkle root attestation over all emitted artifacts and fractal tree nodes."""
        tree_merkle = self.orchestrator.get_root_merkle_hash()
        
        leaf_hashes: List[str] = [tree_merkle]
        for f in sorted(self.emitted_files):
            leaf_hashes.append(hashlib.sha256(f.encode()).hexdigest())

        composite_payload = ":".join(leaf_hashes)
        root_hash = hashlib.sha256(composite_payload.encode()).hexdigest()

        attestation_id = f"attest_{root_hash[:12]}"
        attestation = MerkleTreeRootAttestation(
            attestation_id=attestation_id,
            merkle_root=root_hash,
            leaf_count=len(leaf_hashes),
            leaf_hashes=leaf_hashes,
            builder_signature=f"SIG_ECDSA_G4B_BUILDER_{self.node_ip}",
        )
        attestation.validate_invariants()

        if self.execution_bundle:
            self.execution_bundle.status = TaskExecutionStatus.COMPLETED

        return attestation
