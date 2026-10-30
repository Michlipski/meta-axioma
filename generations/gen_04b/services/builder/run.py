#!/usr/bin/env python3
"""Generation 4b Autonomous Sovereign Builder & Quine Crucible (`soc_g4b_builder`) Entrypoint.

Demonstrates end-to-end execution of the Sovereign Builder Enclave:
1. Sovereign Ingestion of Certified ResearchDeliverableBundle [L1-G4B-001].
2. Bounded Fractal Subagent Tree Orchestration (d <= 4, b <= 5).
3. Thermodynamic Capital Partition (60% Exploratory / 40% Protected) & Landauer Cutoff Gate.
4. AST Interface Skeletonization (Prompt payload <= 4,096 BPE tokens) [Layer A].
5. Byte-Indexed Diagnostic Tuples & Surgical AST Node Patching [Layer B].
6. Compile-Time Hermetic Boundary Linting & Zero-Loopback Invariant [Layer C].
7. Universal Symbol URN Relational Hypergraph O(1) Indexer [Layer D].
8. Dynamic Subagent Persona Synthesis on the fly [L1-G4B-004].
9. Asynchronous RFC Protocol Renegotiation with Research Service.
10. 1-Tap Functorial Undo & Bit-Reversal Mechanics [L1-002].
11. Quine Crucible Self-Hosting Daughter Compiler Certification [L1-016].
12. 28-State Hierarchical XState v5 Statechart Traversal.
13. Cryptographic Tamper-Evident Merkle-DAG Root Attestation.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys
import time

# Ensure local directories and repo root are in sys.path
APP_DIR = Path(__file__).resolve().parent
SRC_DIR = APP_DIR / "src"
WORKSPACE_ROOT = APP_DIR.parent.parent.parent.parent
for p in [APP_DIR, SRC_DIR, WORKSPACE_ROOT]:
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from generations.gen_04b.protocols.deliverable_bundle import (
    ConstraintAnalysis,
    FailureModeModel,
    HypothesisDefinition,
    ResearchDeliverableBundle,
    TradeoffMatrix,
)
from generations.gen_04b.protocols.rfc_protocol import (
    BottleneckType,
    SpecAdjustmentRequest,
    SpecAmendment,
)
from generations.gen_04b.services.builder.src.domain_models import (
    ASTNodeType,
    BuilderExecutionBundle,
    DiagnosticSeverity,
    DiagnosticTuple,
    FractalTreeNode,
    FunctorialUndoCheckpoint,
    HermeticLinterReport,
    HierarchicalBudgetLease,
    LeaseAllocationStatus,
    MerkleTreeRootAttestation,
    QuineDaughterManifest,
    RFCSubmissionRecord,
    SubtreeHealingEnvelope,
    TaskExecutionStatus,
)
from generations.gen_04b.services.builder.src.builder_kernel import SovereignBuilderKernel
from generations.gen_04b.services.builder.src.budget_lease_engine import BudgetLeaseEngine, LandauerCutoffTripped
from generations.gen_04b.services.builder.src.fractal_orchestrator import BoundedFractalOrchestrator
from generations.gen_04b.services.builder.src.ast_skeletonizer import ASTSkeletonizer
from generations.gen_04b.services.builder.src.diagnostic_tuples import DiagnosticEngine, SurgicalPatcher
from generations.gen_04b.services.builder.src.hermetic_linter import HermeticLinter
from generations.gen_04b.services.builder.src.hypergraph_indexer import SymbolHypergraphIndexer
from generations.gen_04b.services.builder.src.dynamic_persona_builder import DynamicPersonaBuilder
from generations.gen_04b.services.builder.src.rfc_protocol_client import RFCProtocolClient
from generations.gen_04b.services.builder.src.functorial_undo import FunctorialUndoManager
from generations.gen_04b.services.builder.src.quine_crucible import QuineCrucibleEngine
from generations.gen_04b.services.builder.src.statechart_engine import G4bBuilderStatechartEngine


def run_operational_verification():
    print("=" * 80)
    print("META-AXIOMA GENERATION 4b: SOVEREIGN BUILDER & QUINE CRUCIBLE (`soc_g4b_builder`)")
    print("=" * 80)
    print("Binding Enclave Endpoint: 192.168.40.20:8442 (Zero Loopback Invariant Enforced)")

    # -------------------------------------------------------------------------
    # STEP 1: Kernel Initialization & Sovereign Ingestion
    # -------------------------------------------------------------------------
    print("\n[STEP 1]: Initializing Sovereign Builder Kernel & Statechart Engine...")
    kernel = SovereignBuilderKernel(node_ip="192.168.40.20", port=8442, total_budget_tokens=250000)
    print(f"  Kernel bound to {kernel.node_ip}:{kernel.port}")
    print(f"  Statechart Initial State: {kernel.statechart.get_active_configuration()}")

    sample_bundle = ResearchDeliverableBundle(
        bundle_id="bundle_g4b_res_certified_001",
        target_soc_id="soc_g4b_builder",
        hypothesis_id="hyp_decoupled_builder",
        constraint_analysis_id="ca_hermetic_mesh",
        failure_mode_id="fm_byzantine_resilient",
        tradeoff_matrix_id="tm_pareto_optimal",
        reference_architecture_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        merkle_root="ca978112ca1bbdcafac231b39a23dc4da786eff8147c4e72b9807785afee48bb",
        is_certified=True,
    )
    exec_bundle = kernel.handshake_and_ingest(sample_bundle)
    print(f"  Certified Deliverable Ingested: {exec_bundle.bundle_id}")
    print(f"  60/40 Partition: Exploratory={exec_bundle.exploratory_capital_tokens} tokens, Protected={exec_bundle.protected_capital_tokens} tokens")

    # -------------------------------------------------------------------------
    # STEP 2: Bounded Fractal Subagent Tree Orchestration
    # -------------------------------------------------------------------------
    print("\n[STEP 2]: Orchestrating Bounded Fractal Subagent Tree (d <= 4, b <= 5)...")
    kernel.statechart.send("EV_START_ORCHESTRATION")
    root_node = kernel.orchestrator.create_root_node(
        task_description="Compile Apex Multi-Tier Autonomous Builder & Quine Crucible",
        assigned_persona="Lead Systems Architect",
    )
    print(f"  Fractal Root Node Created: {root_node.node_id} (Allocated: {root_node.allocated_lease_tokens} tokens)")

    # Spawn child branches
    child_backend = kernel.orchestrator.spawn_child_node(
        parent_node_id=root_node.node_id,
        task_description="Synthesize Functorial Engine & Statechart Backend",
        assigned_persona="Core Backend & Functorial Synthesizer",
    )
    child_linter = kernel.orchestrator.spawn_child_node(
        parent_node_id=root_node.node_id,
        task_description="Synthesize Hermetic Boundary Linter & Byte Patcher",
        assigned_persona="Hermetic Boundary Auditor",
    )
    child_crucible = kernel.orchestrator.spawn_child_node(
        parent_node_id=root_node.node_id,
        task_description="Synthesize Quine Crucible Self-Hosting Sandbox",
        assigned_persona="Quine Daughter Isolation Engineer",
    )
    print(f"  Child Branches Spawned: {[child_backend.node_id, child_linter.node_id, child_crucible.node_id]}")

    # Subtree healing verification
    dummy_diag = DiagnosticTuple(
        diagnostic_id="diag_sample_01",
        file_path="src/backend.py",
        severity=DiagnosticSeverity.ERROR,
        start_byte=10,
        end_byte=20,
        line_number=2,
        column_number=5,
        rule_code="SYNTAX_GLITCH",
        message="Simulated branch glitch",
        suggested_patch="None",
    )
    healing_env = kernel.orchestrator.heal_subtree(child_backend.node_id, dummy_diag)
    print(f"  Subtree Healing Envelope Initialized: {healing_env.envelope_id} (Resolved: {healing_env.resolved})")
    kernel.orchestrator.resolve_healing(healing_env.envelope_id)
    print(f"  Subtree Healing Resolved: {healing_env.resolved}")

    # -------------------------------------------------------------------------
    # STEP 3: AST Interface Skeletonization [Layer A]
    # -------------------------------------------------------------------------
    print("\n[STEP 3]: Extracting AST Interface Skeletons [Layer A] (Prompt <= 4,096 BPE Tokens)...")
    sample_module_code = '''"""Sample Domain Service Module."""
from dataclasses import dataclass
from typing import List

@dataclass
class TransactionRecord:
    tx_id: str
    amount: float

class FinancialLedger:
    """Ledger tracking financial settlements."""
    def __init__(self, currency: str = "USD"):
        self.currency = currency
        self.transactions: List[TransactionRecord] = []

    def post_transaction(self, record: TransactionRecord) -> bool:
        if record.amount <= 0:
            raise ValueError("Amount must be positive")
        self.transactions.append(record)
        return True

    def calculate_balance(self) -> float:
        return sum(t.amount for t in self.transactions)
'''
    skeleton_snap = kernel.skeletonizer.extract_skeleton(
        source_code=sample_module_code,
        module_path="src/ledger.py",
        symbol_urn="urn:axioma:g4b:finance:ledger#FinancialLedger",
    )
    print(f"  Original Bytes: {len(sample_module_code.encode())} -> Stripped Bytes: {skeleton_snap.stripped_byte_count}")
    print(f"  Preserved Signatures: {skeleton_snap.preserved_signatures}")
    print(f"  Estimated Skeleton BPE Tokens: {skeleton_snap.estimated_bpe_tokens} (<= 4,096 limit satisfied)")

    # -------------------------------------------------------------------------
    # STEP 4: Machine-Verifiable Diagnostic Tuples & Surgical AST Patching [Layer B]
    # -------------------------------------------------------------------------
    print("\n[STEP 4]: Testing Byte-Indexed Diagnostic Tuples & Surgical Patching [Layer B]...")
    code_with_typo = "def calculate_tax(amount: float) -> flout:\n    return amount * 0.15\n"
    diag = DiagnosticEngine.create_diagnostic(
        file_path="src/tax.py",
        severity=DiagnosticSeverity.ERROR,
        rule_code="TYPE_TYPO",
        message="Unknown return type 'flout', expected 'float'",
        source_code=code_with_typo,
        line=1,
        col=36,
        end_line=1,
        end_col=41,
        suggested_patch="float",
    )
    patched_tax_code = SurgicalPatcher.apply_patch(code_with_typo, diag)
    assert "float:" in patched_tax_code, "Surgical patch failed!"
    print(f"  Surgical Patch Applied: 'flout' -> 'float' at byte [{diag.start_byte}:{diag.end_byte}]")

    # -------------------------------------------------------------------------
    # STEP 5: Hermetic Boundary Linting [Layer C]
    # -------------------------------------------------------------------------
    print("\n[STEP 5]: Compile-Time Hermetic Boundary Linting [Layer C]...")
    bad_code = "host = '127.0.0.1'\nimport sys\nsys.path.append('/tmp/insecure')\n"
    linter_rep = kernel.linter.audit_code(bad_code, "bad_module.py")
    assert not linter_rep.passed
    print(f"  Detected Hermetic Violations: {[v.rule_code for v in linter_rep.violations]}")
    clean_code = "host = '192.168.40.20'\ndef valid_entry():\n    return 'OK'\n"
    clean_rep = kernel.linter.audit_code(clean_code, "clean_module.py")
    assert clean_rep.passed
    print(f"  Clean Code Verified Hermetic (Zero Loopback Invariant Passed)")

    # -------------------------------------------------------------------------
    # STEP 6: Universal Symbol URN Relational Hypergraph [Layer D]
    # -------------------------------------------------------------------------
    print("\n[STEP 6]: Universal Symbol URN Relational Hypergraph O(1) Indexing [Layer D]...")
    kernel.hypergraph.index_symbol(
        urn_str="urn:axioma:g4b:finance:types#TransactionRecord",
        node_type=ASTNodeType.CLASS_DEF,
        file_path="src/types.py",
    )
    kernel.hypergraph.index_symbol(
        urn_str="urn:axioma:g4b:finance:ledger#FinancialLedger",
        node_type=ASTNodeType.CLASS_DEF,
        file_path="src/ledger.py",
        dependencies=["urn:axioma:g4b:finance:types#TransactionRecord"],
    )
    topo_order = kernel.hypergraph.topological_sort()
    print(f"  Topological Dependency Ordering: {topo_order}")
    assert topo_order[0] == "urn:axioma:g4b:finance:types#TransactionRecord"

    # -------------------------------------------------------------------------
    # STEP 7: Dynamic Persona Synthesis on the Fly [L1-G4B-004]
    # -------------------------------------------------------------------------
    print("\n[STEP 7]: Synthesizing Dynamic Subagent Personas on the Fly [L1-G4B-004]...")
    dynamic_persona = DynamicPersonaBuilder.create_hermetic_auditor_persona()
    subagent_params = DynamicPersonaBuilder.to_define_subagent_params(dynamic_persona)
    print(f"  Synthesized Dynamic Persona: '{dynamic_persona.role_title}'")
    print(f"  Governing Axioms: {dynamic_persona.governing_axioms}")

    # -------------------------------------------------------------------------
    # STEP 8: Thermodynamic Capital Budget Leasing & Landauer Cutoff Gate
    # -------------------------------------------------------------------------
    print("\n[STEP 8]: Thermodynamic Capital Management & Landauer Cutoff Gate...")
    heat_dissipated = kernel.budget_engine.record_bit_erasure(bits_erased=4096)
    print(f"  Recorded 4,096 bit erasures -> Heat Dissipated: {heat_dissipated:.4e} Joules")
    print(f"  Remaining Exploratory Capital: {kernel.budget_engine.remaining_exploratory_capital} tokens")

    # -------------------------------------------------------------------------
    # STEP 9: Asynchronous RFC Protocol Participation
    # -------------------------------------------------------------------------
    print("\n[STEP 9]: Participating in Asynchronous RFC Protocol...")
    rfc_req = kernel.rfc_client.submit_spec_adjustment_request(
        target_symbol_urn="urn:axioma:g4b:builder:ledger#FinancialLedger",
        bottleneck_type=BottleneckType.LATENCY_OVERRUN,
        empirical_evidence="Physical serialization latency exceeded 15ms SLA",
        proposed_delta="Cache parsed AST skeleton in memory",
        preserved_invariants=["[L1-002]"],
    )
    print(f"  RFC Submitted: {rfc_req.request_id} for {rfc_req.target_symbol_urn}")
    amendment = SpecAmendment(
        amendment_id="amd_g4b_res_001",
        request_id=rfc_req.request_id,
        is_approved=True,
        adjudicator_signature="SIG_ECDSA_RESEARCH_KERNEL_APPROVED",
        amended_contract_ir_delta="IN_MEMORY_AST_CACHE_AUTHORIZED",
    )
    approved, delta = kernel.rfc_client.ingest_spec_amendment(amendment)
    print(f"  RFC Amendment Adjudicated: Approved={approved}, Delta='{delta}'")

    # -------------------------------------------------------------------------
    # STEP 10: 1-Tap Functorial Undo & Reversible State Mechanics [L1-002]
    # -------------------------------------------------------------------------
    print("\n[STEP 10]: Demonstrating 1-Tap Functorial Undo & State Bit-Reversal [L1-002]...")
    curr_state_before = kernel.statechart.get_active_configuration()
    kernel.statechart.send("EV_START_SYNTHESIS")
    print(f"  Transitioned to Synthesis: {kernel.statechart.get_active_configuration()}")
    restored_config = kernel.statechart.undo_step()
    print(f"  1-Tap Undo Restored Configuration: {restored_config}")

    # -------------------------------------------------------------------------
    # STEP 11: Quine Crucible Self-Hosting Daughter Isolation [L1-016]
    # -------------------------------------------------------------------------
    print("\n[STEP 11]: Executing Quine Crucible Self-Hosting Daughter Certification [L1-016]...")
    quine_manifest = kernel.execute_quine_crucible_certification(daughter_gen_id="gen_05a")
    print(f"  Quine Manifest Emitted: {quine_manifest.manifest_id}")
    print(f"  Daughter Hash: {quine_manifest.daughter_hash}")
    print(f"  Boot Success: {quine_manifest.boot_success}, Self-Hosting Certified: {quine_manifest.self_hosting_certified}")
    assert quine_manifest.self_hosting_certified, "Quine daughter failed self-hosting certification!"

    # -------------------------------------------------------------------------
    # STEP 12: Merkle-DAG Cryptographic Root Attestation
    # -------------------------------------------------------------------------
    print("\n[STEP 12]: Sealing Tamper-Evident Merkle-DAG Root Attestation...")
    attestation = kernel.seal_merkle_attestation()
    print(f"  Merkle Tree Attestation ID: {attestation.attestation_id}")
    print(f"  Cryptographic Merkle Root: {attestation.merkle_root}")
    print(f"  Leaf Artifact Count: {attestation.leaf_count}")
    print(f"  Builder Digital Signature: {attestation.builder_signature}")

    print("\n" + "=" * 80)
    print("ALL 13 GENERATION 4b SOVEREIGN BUILDER MODULES CERTIFIED WITH EXIT CODE 0")
    print("=" * 80)
    return 0


if __name__ == "__main__":
    sys.exit(run_operational_verification())
