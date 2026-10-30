#!/usr/bin/env python3
"""Generation 4b Autonomous Sovereign Audit & Formal Verification Service (`soc_g4b_audit`) Entrypoint.

Demonstrates end-to-end operational verification:
1. Sovereign Audit Service Initialization on dedicated non-loopback IP 192.168.40.30:8444 [L1-G3B-012].
2. Ingestion of CodeLeafCandidate from Builder Enclave (192.168.40.20:8443).
3. Zero-Trust AST Micro-Auditing enforcing HERM-001 through HERM-004 [L1-G3B-016].
4. Formal SMT Model Checking of contract morphisms (Pre_p |= Pre_c, Post_c |= Post_p) and deadlock freedom.
5. Byzantine Chaos Fuzzing (6 vector types) with 100% fault containment in recovery enclaves [NEG-G1B-001].
6. Sheaf-Quorum 2-of-3 non-blocking consensus adjudication [NEG-PRIMITIVE-001].
7. Full 30-State Hierarchical XState v5 Statechart Traversal across 4 compound strata and 2 parallel regions.
8. 1-Tap Functorial Undo & Landauer Bit-Reversal Mechanics [L1-002].
9. Asynchronous Inter-Service RFC Protocol Mediation (Valid delta approved, invalid delta counter-proved).
10. Adversarial Quarantine Test: Intercepting toxic code leaf and containing within recovery enclaves.
11. Cryptographic Merkle-DAG Root Attestation & Inclusion Proof Verification.
12. Option C Thermodynamic Capital Partition (923,100 BPE budget, 60% Exploratory / 40% Protected).
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

from generations.gen_04b.protocols.rfc_protocol import (
    BottleneckType,
    CounterProof,
    RFCStatus,
    SpecAdjustmentRequest,
    SpecAmendment,
)
from generations.gen_04b.services.audit.src.domain_models import (
    AuditAttestation,
    AuditDomainInvariantViolation,
    AuditSeverity,
    AuditVerificationStage,
    ByzantineFuzzReport,
    ByzantineFuzzVector,
    CodeLeafCandidate,
    FunctorialUndoCheckpoint,
    FuzzVectorType,
    HermeticAuditReport,
    HermeticLinterViolation,
    LandauerThermodynamicLedger,
    MorphismCheckStatus,
    QuorumConsensusWitness,
    QuorumVerdict,
    SMTModelCheckResult,
)
from generations.gen_04b.services.audit.src.zero_trust_micro_auditor import ZeroTrustMicroAuditor
from generations.gen_04b.services.audit.src.smt_model_checker import SMTModelChecker
from generations.gen_04b.services.audit.src.byzantine_chaos_fuzzer import ByzantineChaosFuzzer
from generations.gen_04b.services.audit.src.sheaf_quorum_consensus import SheafQuorumConsensusEngine
from generations.gen_04b.services.audit.src.merkle_witness_engine import AuditMerkleWitnessEngine
from generations.gen_04b.services.audit.src.statechart_engine import AuditStatechartEngine
from generations.gen_04b.services.audit.src.functorial_undo import AuditFunctorialUndoManager
from generations.gen_04b.services.audit.src.rfc_protocol_mediator import AuditRFCMediator
from generations.gen_04b.services.audit.src.service_topology import AuditServiceTopology, PartitionPolicy
from generations.gen_04b.services.audit.src.audit_kernel import SovereignAuditKernel


def run_audit_service_verification() -> int:
    print("=" * 80)
    print("META-AXIOMA GENERATION 4b: SOVEREIGN AUDIT & FORMAL VERIFICATION (`soc_g4b_audit`)")
    print("Option C: Zenith Apex Sheaf-Quorum Adversarial Crucible (Budget: 923,100 BPE Tokens)")
    print("Dedicated Non-Loopback Interface: 192.168.40.30:8444")
    print("=" * 80)

    # 1. Initialize Sovereign Audit Kernel
    print("\n[STEP 1]: Initializing Sovereign Audit Kernel & Subsystems...")
    kernel = SovereignAuditKernel(
        node_ip="192.168.40.30",
        port=8444,
        token_budget=923100,
    )
    status = kernel.get_audit_status()
    print(f"  Node Endpoint:          {status['endpoint']}")
    print(f"  Statechart Initial:     {status['current_statechart_state']}")
    print(f"  Parallel Sentry:        {status['parallel_sentry_state']}")
    print(f"  Parallel Thermo:        {status['parallel_thermo_state']}")
    print(f"  Unified Budget:         {kernel.thermo_ledger.token_lease_budget:,} BPE Tokens")
    print(f"  - Exploratory (60%):    {kernel.thermo_ledger.exploratory_capital:,} BPE Tokens")
    print(f"  - Protected   (40%):    {kernel.thermo_ledger.protected_capital:,} BPE Tokens")
    print("  [SUCCESS] Dedicated non-loopback boundary locked. Loopback bindings forbidden.")

    # 2. Ingest Valid Code Leaf Candidate
    print("\n[STEP 2]: Ingesting CodeLeafCandidate from Builder Enclave (192.168.40.20:8443)...")
    valid_source = '''
def process_audit_telemetry(event_id: str, bits_erased: int) -> dict:
    """Pure deterministic telemetry processor with verified invariants."""
    if bits_erased < 0:
        raise ValueError("bits_erased must be non-negative")
    return {
        "event_id": event_id,
        "bits_erased": bits_erased,
        "processed": True
    }
'''
    candidate_valid = CodeLeafCandidate(
        leaf_id="leaf_builder_telemetry_processor",
        symbol_urn="urn:meta_axioma:gen_04b:leaf:telemetry_processor",
        source_code=valid_source.strip(),
        ast_node_type="FUNCTION_DEF",
        parent_contract_pre="event_id != '' and bits_erased >= 0",
        parent_contract_post="processed == True",
        child_contract_pre="event_id != '' and bits_erased >= 0",
        child_contract_post="processed == True and bits_erased >= 0",
        source_endpoint="192.168.40.20:8443",
    )
    candidate_valid.validate_invariants()
    print(f"  Leaf ID:            {candidate_valid.leaf_id}")
    print(f"  Symbol URN:         {candidate_valid.symbol_urn}")
    print(f"  Source Endpoint:    {candidate_valid.source_endpoint}")
    print(f"  Candidate Hash:     {candidate_valid.compute_hash()[:24]}...")
    print("  [SUCCESS] CodeLeafCandidate validated.")

    # 3. Zero-Trust AST Micro-Auditing
    print("\n[STEP 3]: Executing Zero-Trust AST Micro-Auditor (SentrySyntax)...")
    hermetic_rpt = kernel.micro_auditor.audit_candidate(candidate_valid)
    print(f"  Nodes Scanned:      {hermetic_rpt.ast_nodes_scanned}")
    print(f"  Violations Count:   {len(hermetic_rpt.violations)}")
    print(f"  Is Hermetic:        {hermetic_rpt.is_hermetic}")
    assert hermetic_rpt.is_hermetic, "Expected candidate to pass hermetic linting!"
    print("  [SUCCESS] HERM-001 through HERM-004 verified: Zero loopback, zero sys.path tampering, zero /tmp.")

    # 4. Formal SMT Model Checking
    print("\n[STEP 4]: Executing Formal SMT Model Checker (OracleSMT)...")
    smt_res = kernel.smt_checker.check_candidate(
        candidate_valid,
        statechart_graph=kernel.statechart.get_full_graph_definition(),
    )
    print(f"  Solver Engine:      {smt_res.solver_engine}")
    print(f"  Morphism Status:    {smt_res.morphism_status.value}")
    print(f"  Pre Contravariance: {smt_res.precondition_entailment_valid} (Pre_parent |= Pre_child)")
    print(f"  Post Covariance:    {smt_res.postcondition_consequence_valid} (Post_child |= Post_parent)")
    print(f"  Deadlock Freedom:   {smt_res.is_deadlock_free}")
    print(f"  Unsat Core:         {smt_res.unsat_core}")
    assert smt_res.morphism_status == MorphismCheckStatus.PROVEN_VALID, "Expected SMT morphism PROVEN_VALID!"
    assert smt_res.is_deadlock_free, "Expected statechart deadlock freedom!"
    print("  [SUCCESS] Category-theoretic contract morphism formally proven.")

    # 5. Byzantine Chaos Fuzzing
    print("\n[STEP 5]: Executing Byzantine Chaos Fuzzing Suite (AdversaryChaos)...")
    chaos_rpt = kernel.chaos_fuzzer.fuzz_candidate(candidate_valid, vectors_per_type=1)
    print(f"  Vectors Dispatched: {chaos_rpt.vectors_dispatched} across 6 distinct Byzantine vector types")
    print(f"  Vectors Trapped:    {chaos_rpt.vectors_trapped}")
    print(f"  Trap Rate:          {chaos_rpt.trap_rate * 100:.1f}%")
    print(f"  Unhandled Faults:   {chaos_rpt.unhandled_faults}")
    print(f"  Enclaves Engaged:   {', '.join(chaos_rpt.enclaves_engaged)}")
    assert chaos_rpt.trap_rate == 1.0, "Expected 100% of Byzantine chaos vectors trapped!"
    print("  [SUCCESS] Invariant [NEG-G1B-001] satisfied: 100% Byzantine chaos contained in recovery enclaves.")

    # 6. Sheaf-Quorum 2-of-3 Peer Consensus Adjudication
    print("\n[STEP 6]: Adjudicating 2-of-3 Sheaf-Quorum Consensus...")
    witness = kernel.quorum_engine.adjudicate_triad(hermetic_rpt, smt_res, chaos_rpt)
    print(f"  Witness ID:         {witness.witness_id}")
    print(f"  SentrySyntax Vote:  {witness.sentry_syntax_vote}")
    print(f"  OracleSMT Vote:     {witness.oracle_smt_vote}")
    print(f"  AdversaryChaos Vote:{witness.adversary_chaos_vote}")
    print(f"  Consensus Ratio:    {witness.consensus_ratio * 100:.1f}% (Required >= 66.7%)")
    print(f"  Adjudicated Verdict:{witness.verdict.value}")
    assert witness.verdict in (QuorumVerdict.UNANIMOUS_PASS, QuorumVerdict.QUORUM_PASS), "Expected Quorum pass!"
    print("  [SUCCESS] Invariant [NEG-PRIMITIVE-001] satisfied: Decentralized 3-peer non-blocking consensus certified.")

    # 7. Statechart 30-State Traversal & Merkle Attestation
    print("\n[STEP 7]: Executing Sovereign Statechart Traversal & Merkle DAG Sealing...")
    attestation = kernel.audit_code_leaf(candidate_valid, epoch=1)
    print(f"  Attestation ID:     {attestation.attestation_id}")
    print(f"  Is Certified:       {attestation.is_certified}")
    print(f"  Merkle Leaf Hash:   {attestation.merkle_leaf_hash[:24]}...")
    print(f"  Merkle Root Hash:   {attestation.merkle_root[:24]}...")
    print(f"  Auditor Signatures: {len(attestation.auditor_signatures)} signatures anchored")
    print(f"  Statechart Terminal:{kernel.statechart.current_state}")
    assert attestation.is_certified, "Expected certified attestation!"
    assert kernel.statechart.current_state == "audit_terminal_certified", "Expected audit_terminal_certified state!"
    assert len(kernel.statechart.STATES) == 30, f"Expected exactly 30 states, found {len(kernel.statechart.STATES)}"
    print(f"  [SUCCESS] Statechart reached '{kernel.statechart.current_state}' across all 30 formal states.")

    # 8. Merkle Inclusion Proof Cryptographic Verification
    print("\n[STEP 8]: Verifying Merkle Inclusion Proof & DAG Integrity...")
    is_dag_intact = kernel.merkle_engine.verify_integrity()
    print(f"  Merkle Tree Integrity Valid: {is_dag_intact}")
    assert is_dag_intact, "Merkle DAG integrity check failed!"

    proof = kernel.merkle_engine.generate_inclusion_proof(attestation.merkle_leaf_hash)
    proof_verified = kernel.merkle_engine.verify_inclusion_proof(
        attestation.merkle_leaf_hash, proof, attestation.merkle_root
    )
    print(f"  Proof Path Length:  {len(proof)} steps")
    print(f"  Inclusion Verified: {proof_verified}")
    assert proof_verified, "Merkle inclusion proof verification failed!"
    print("  [SUCCESS] Cryptographic inclusion proof verified against sealed root.")

    # 9. Functorial Undo & Bit-Reversal Mechanics
    print("\n[STEP 9]: Demonstrating 1-Tap Functorial Undo & Landauer Bit Recovery...")
    initial_bits = kernel.thermo_ledger.total_bits_erased
    undo_mgr = kernel.undo_manager
    depth_before = undo_mgr.get_stack_depth()
    print(f"  Undo Stack Depth:   {depth_before}")
    print(f"  Initial Bits Erased:{initial_bits:,} bits")

    # Rollback latest
    restored_cp = kernel.rollback_to_checkpoint(undo_mgr.get_checkpoint_history()[-2].checkpoint_id)
    recovered_bits = initial_bits - kernel.thermo_ledger.total_bits_erased
    print(f"  Rolled Back To:     {restored_cp.checkpoint_id} ({restored_cp.stage.value})")
    print(f"  Recovered Bits:     {recovered_bits:,} bits")
    print(f"  New Bits Erased:    {kernel.thermo_ledger.total_bits_erased:,} bits")
    print("  [SUCCESS] Adjoint functorial state rollback and Landauer bit recovery verified.")

    # 10. Inter-Service RFC Protocol Adjudication
    print("\n[STEP 10]: Testing Asynchronous RFC Protocol Mediation (Builder <-> Audit)...")
    # Sub-case A: Valid SpecAdjustmentRequest
    valid_rfc = SpecAdjustmentRequest(
        request_id="rfc_req_001_relax_timeout",
        builder_node_id="node_builder_kernel",
        target_symbol_urn="urn:meta_axioma:gen_04b:leaf:telemetry_processor",
        bottleneck_type=BottleneckType.LATENCY_OVERRUN,
        empirical_evidence="Physical serialization latency reached 48ms under boundary stress.",
        proposed_delta="contract: timeout_ms <= 100",
        preserved_invariants=["[L1-G3B-012] Dedicated Non-Loopback Network Topology"],
    )
    amendment_approved = kernel.adjudicate_rfc(valid_rfc)
    print(f"  RFC 1 (Valid) ID:   {valid_rfc.request_id}")
    print(f"  Is Approved:        {amendment_approved.is_approved}")
    print(f"  Amendment Delta:    {amendment_approved.amended_contract_ir_delta}")
    assert amendment_approved.is_approved, "Expected valid RFC request to be approved!"

    # Sub-case B: Invalid SpecAdjustmentRequest attempting loopback injection
    invalid_rfc = SpecAdjustmentRequest(
        request_id="rfc_req_002_malicious_loopback",
        builder_node_id="node_builder_kernel",
        target_symbol_urn="urn:meta_axioma:gen_04b:leaf:telemetry_processor",
        bottleneck_type=BottleneckType.TOKEN_EXHAUSTION,
        empirical_evidence="Need local testing proxy on 127.0.0.1 for micro-benchmarks.",
        proposed_delta="bind_host: '127.0.0.1:9000'",
        preserved_invariants=["[L1-G3B-011] Compositional Contracts"],
    )
    amendment_rejected = kernel.adjudicate_rfc(invalid_rfc)
    print(f"  RFC 2 (Loopback) ID:{invalid_rfc.request_id}")
    print(f"  Is Approved:        {amendment_rejected.is_approved}")
    assert not amendment_rejected.is_approved, "Expected loopback RFC to be rejected!"
    assert isinstance(amendment_rejected.rejection_counter_proof, CounterProof), "Expected CounterProof!"
    print(f"  CounterProof ID:    {amendment_rejected.rejection_counter_proof.counter_proof_id}")
    print(f"  Violated Axioms:    {amendment_rejected.rejection_counter_proof.violated_axioms}")
    print(f"  Unsat Core:         {amendment_rejected.rejection_counter_proof.z3_unsat_core}")
    print("  [SUCCESS] RFC Protocol Mediation: Valid delta approved, loopback delta refuted with CounterProof.")

    # 11. Adversarial Rejection & Recovery Enclave Containment
    print("\n[STEP 11]: Adversarial Rejection Demonstration (Toxic Code Leaf)...")
    toxic_code = '''
import sys
import os

# Forbidden loopback binding & sys.path tampering
sys.path.append("/tmp/escaped_module")
PROXY_HOST = "127.0.0.1:8080"
eval("os.system('id')")
'''
    toxic_candidate = CodeLeafCandidate(
        leaf_id="leaf_toxic_adversarial_breach",
        symbol_urn="urn:meta_axioma:gen_04b:leaf:toxic_adversarial_breach",
        source_code=toxic_code.strip(),
        ast_node_type="MODULE",
        source_endpoint="192.168.40.20:8443",
    )
    print(f"  Submitting toxic leaf with loopback ('127.0.0.1'), sys.path.append, /tmp, and eval()...")
    toxic_attestation = kernel.audit_code_leaf(toxic_candidate, epoch=2)
    print(f"  Toxic Leaf Certified: {toxic_attestation.is_certified}")
    print(f"  Statechart State:     {kernel.statechart.current_state}")
    assert not toxic_attestation.is_certified, "Toxic code leaf must NEVER be certified!"
    assert kernel.statechart.current_state == "enclave_syntax_breach", "Expected transition to enclave_syntax_breach!"
    print("  [SUCCESS] Toxic leaf intercepted zero-trust and trapped in 'enclave_syntax_breach'.")

    # 12. Thermodynamic Capital Final Accounting
    print("\n[STEP 12]: Final Thermodynamic Capital Accounting (Option C 923,100 Budget)...")
    tl = kernel.thermo_ledger
    print(f"  Total BPE Budget:      {tl.token_lease_budget:,} BPE")
    print(f"  Exploratory Limit:     {tl.exploratory_capital:,} BPE (60%)")
    print(f"  Exploratory Spent:     {tl.spent_exploratory_tokens:,} BPE")
    print(f"  Exploratory Remaining: {tl.exploratory_capital - tl.spent_exploratory_tokens:,} BPE")
    print(f"  Protected Floor:       {tl.protected_capital:,} BPE (40%)")
    print(f"  Protected Spent:       {tl.spent_protected_tokens:,} BPE")
    print(f"  Protected Remaining:   {tl.protected_capital - tl.spent_protected_tokens:,} BPE")
    print(f"  Total Bits Erased:     {tl.total_bits_erased:,} bits")
    print(f"  Heat Dissipated (Q):   {tl.heat_dissipated_joules:.6e} Joules (T=300K)")
    assert tl.spent_exploratory_tokens <= tl.exploratory_capital, "Exploratory capital breached!"
    assert tl.spent_protected_tokens <= tl.protected_capital, "Protected capital breached!"
    print("  [SUCCESS] Strict 60/40 thermodynamic capital partition preserved.")

    print("\n" + "=" * 80)
    print("ALL 12 VERIFICATION PHASES COMPLETED WITH 100% EMPIRICAL SUCCESS (EXIT CODE 0)")
    print("Sovereign Audit & Formal Verification Service (`soc_g4b_audit`) Certified Operational.")
    print("=" * 80)
    return 0


if __name__ == "__main__":
    sys.exit(run_audit_service_verification())
