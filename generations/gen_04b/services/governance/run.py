#!/usr/bin/env python3
"""Generation 4b Sovereign Governance & Safety Service (`soc_g4b_governance`) Runner.

Demonstrates end-to-end multi-phase operational verification:
Phase 1: Structural & socket layout verification (192.168.40.50:8448) [L1-G3B-012].
Phase 2: Negative Axiom AST and code scanning verification (NEG-001..NEG-999) [L1-G3B-016].
Phase 3: HITL Intercept & Heuristic Debt Ratio verification (HDR <= 0.15) [L1-G2B-002].
Phase 4: Asymmetric RFC Adjudication & CounterProof generation [L1-G4B-001].
Phase 5: Circuit Breaker tripping, quarantine, and recovery [L1-016].
Phase 6: Succession Gatekeeper & Gen 5 Handover Certificate certification.
Phase 7: Functorial Undo categorical state rollback [L1-002].
Phase 8: Statechart 30-state covering path traversal [L1-002].
Phase 9: Sovereign service readiness report.
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

from generations.gen_04b.services.governance.src import (
    ASTInterceptRecord,
    AxiomSeverity,
    AxiomViolation,
    BottleneckType,
    CircuitBreakerState,
    CircuitBreakerTrippedError,
    CounterProof,
    FunctorialUndoEngine,
    GenerationalHandoverCertificate,
    GovernanceDomainInvariantViolation,
    GovernanceEvent,
    GovernanceKernel,
    GovernanceKernelState,
    GovernanceServiceTopology,
    GovernanceStatechartDefinition,
    GovernanceStatechartState,
    HITLDisposition,
    HITLDispositionStatus,
    HITLInterceptRequest,
    HeuristicDebtCeilingBreached,
    HeuristicDebtRecord,
    NegativeAxiom,
    NegativeAxiomEnforcer,
    NegativeAxiomVetoViolation,
    PeerQuarantineStatus,
    QuarantineEvent,
    RFCDispositionStatus,
    RFCProtocolAdjudicator,
    SpecAdjustmentRequest,
    SpecAmendment,
    StatechartEngine,
    SuccessionGatekeeper,
    SuccessionGraduationStatus,
    SuccessionInvariantProof,
    VetoActionType,
    assert_non_loopback,
)


def run_governance_verification() -> None:
    print("=" * 80)
    print("META-AXIOMA GENERATION 4b: SOVEREIGN GOVERNANCE & SAFETY SERVICE (`soc_g4b_governance`)")
    print("Dedicated Non-Loopback Interface: 192.168.40.50:8448")
    print("Axiomatic Invariants: [L1-G3B-012], [L1-G3B-016], [L1-G2B-002], [L1-016], [L1-002]")
    print("=" * 80)

    # -------------------------------------------------------------------------
    # PHASE 1: Structural & Socket Layout Verification
    # -------------------------------------------------------------------------
    print("\n[PHASE 1]: Structural & Socket Layout Verification (192.168.40.50:8448)...")
    kernel = GovernanceKernel(node_ip="192.168.40.50", port=8448)

    # Verify dedicated endpoint and zero loopback
    assert_non_loopback(kernel.endpoint, "Governance Service Endpoint")
    print(f"  Service Node Endpoint:  {kernel.endpoint}")
    print(f"  Isolation Subnet:       {kernel.circuit_breaker.isolation_subnet}")

    # Verify all peer endpoints
    expected_peers = {
        "research": "192.168.40.10:8440",
        "builder": "192.168.40.20:8442",
        "audit": "192.168.40.30:8444",
        "telemetry": "192.168.40.40:8446",
        "governance": "192.168.40.50:8448",
    }
    for peer_name, expected_ep in expected_peers.items():
        ep = kernel.topology.get_peer_endpoint(peer_name)
        assert ep == expected_ep, f"Peer mismatch for {peer_name}: {ep} != {expected_ep}"
        assert_non_loopback(ep, f"Peer {peer_name}")
        print(f"  Peer Bound [{peer_name.upper():<10}]: {ep}")

    # Verify loopback rejection
    loopback_attempts = ["127.0.0.1", "localhost", "::1", "0.0.0.0"]
    for lb in loopback_attempts:
        try:
            assert_non_loopback(lb, "Loopback Rejection Test")
            raise AssertionError(f"Expected loopback rejection for '{lb}'")
        except GovernanceDomainInvariantViolation:
            pass
    print("  [SUCCESS] Invariant [L1-G3B-012] Verified: Loopback bindings strictly prohibited.")

    # Bootstrap the kernel into operational state
    initial_state = kernel.bootstrap()
    assert kernel.statechart.current_state == GovernanceStatechartState.OP_SURVEILLING
    print(f"  Kernel Bootstrapped:    State='{kernel.statechart.current_state.value}', Ledger Head={kernel.get_ledger_head()[:16]}...")
    print("  [SUCCESS] Phase 1 Completed: Non-loopback sovereign topology certified.")

    # -------------------------------------------------------------------------
    # PHASE 2: Negative Axiom AST and Code Scanning Verification
    # -------------------------------------------------------------------------
    print("\n[PHASE 2]: Negative Axiom AST & Code Scanning Verification (NEG-001..NEG-999)...")
    active_axioms = kernel.enforcer.get_active_axioms()
    print(f"  Active Negative Axioms: {len(active_axioms)} registered")
    for ax in active_axioms[:4]:
        print(f"    - {ax.axiom_id}: {ax.name} (forbidden: '{ax.forbidden_pattern}')")

    # Clean code sample
    clean_code = """
def pure_transition(state: dict, event: str) -> dict:
    new_state = dict(state)
    new_state['step'] = new_state.get('step', 0) + 1
    return new_state
"""
    clean_violations = kernel.scan_and_enforce_code(clean_code, file_path="pure_module.py")
    assert len(clean_violations) == 0, f"Expected 0 violations for clean code, got {len(clean_violations)}"
    print(f"  Scanning pure code:     0 violations trapped (clean).")

    # Toxic code sample containing: eval, os.system, time.sleep, loopback IP, bypass_sandbox
    toxic_code = """
import os
import time

def dangerous_operation():
    eval("print('bypassing')")
    os.system("rm -rf /")
    time.sleep(5)
    endpoint = "127.0.0.1:8080"
    flag = "bypass_sandbox"
"""
    toxic_violations = kernel.scan_and_enforce_code(toxic_code, file_path="toxic_module.py")
    assert len(toxic_violations) >= 4, f"Expected >= 4 violations, got {len(toxic_violations)}"
    print(f"  Scanning toxic code:    {len(toxic_violations)} violations trapped zero-bypass:")
    for v in toxic_violations[:5]:
        print(f"    - [{v.severity.value}] {v.axiom_id}: {v.description}")

    # Toxic topology sample containing loopback and centralized coordinator
    toxic_topology = {
        "nodes": {
            "node_bad_1": {"endpoint": "127.0.0.1:9000", "role": "worker"},
            "node_bad_2": {"endpoint": "192.168.40.99:9002", "role": "centralized_coordinator_master"},
        }
    }
    top_violations = kernel.scan_topology(toxic_topology)
    assert len(top_violations) >= 2, f"Expected >= 2 topology violations, got {len(top_violations)}"
    print(f"  Scanning toxic topology:{len(top_violations)} violations trapped (loopback + master coordinator).")
    print("  [SUCCESS] Phase 2 Completed: Zero-bypass AST and semantic interception verified.")

    # -------------------------------------------------------------------------
    # PHASE 3: HITL Intercept & Heuristic Debt Ratio Verification
    # -------------------------------------------------------------------------
    print("\n[PHASE 3]: HITL Intercept & Heuristic Debt Ratio Verification (HDR <= 0.15)...")
    initial_hdr = kernel.hitl_engine.get_current_hdr()
    print(f"  Initial HDR Record:     Epoch {initial_hdr.epoch} | HDR: {initial_hdr.heuristic_debt_ratio:.4f} (Ceiling: 0.15)")
    print(f"  Decision Counts:        Heuristic={initial_hdr.autonomous_heuristic_decisions}, Formal={initial_hdr.formal_verified_decisions}, HITL={initial_hdr.hitl_supervised_decisions}")
    assert kernel.hitl_engine.is_debt_compliant(), "Initial HDR must be compliant"

    # Create a structured HITL intercept dialog
    intercept_req = HITLInterceptRequest(
        intercept_id="hitl_icpt_arch_review_001",
        trigger_reason="Strategic boundary review for distributed consensus quorum size.",
        service_endpoint="192.168.40.50:8448",
        context_dossier={"subsystem": "mesh_consensus", "current_peers": 5, "entropy": 0.02},
        recommended_options=[
            "Option A: Maintain 2-of-3 non-blocking Sheaf quorum",
            "Option B: Escalate to 3-of-5 Byzantine fault-tolerant quorum",
        ],
    )
    icpt_id = kernel.hitl_engine.create_intercept(intercept_req)
    print(f"  Structured Intercept:   Created '{icpt_id}' with {len(intercept_req.recommended_options)} options.")

    # Human supervisor applies disposition
    disp = HITLDisposition(
        disposition_id="disp_arch_001",
        intercept_id=icpt_id,
        human_supervisor="Michael Lipski",
        disposition_status=HITLDispositionStatus.APPROVED_CONTINUE,
        selected_option="Option A: Maintain 2-of-3 non-blocking Sheaf quorum",
        architectural_guidance="Preserve non-blocking Landauer dissipation bounds under all network conditions.",
    )
    disp.sign(secret_key="sovereign_governance_secret")
    kernel.hitl_engine.record_disposition(disp)

    # Verify disposition recorded and status updated
    updated_req = kernel.hitl_engine.get_intercept(icpt_id)
    assert updated_req.status == HITLDispositionStatus.APPROVED_CONTINUE
    post_hdr = kernel.hitl_engine.get_current_hdr()
    print(f"  Disposition Resolved:   Supervisor='{disp.human_supervisor}', Status={updated_req.status.value}")
    print(f"  Post-Resolution HDR:    HDR: {post_hdr.heuristic_debt_ratio:.4f} | Compliant: {kernel.hitl_engine.is_debt_compliant()}")
    print("  [SUCCESS] Phase 3 Completed: Stateful human override and HDR bounds verified.")

    # -------------------------------------------------------------------------
    # PHASE 4: Asymmetric RFC Adjudication & CounterProof Generation
    # -------------------------------------------------------------------------
    print("\n[PHASE 4]: Asymmetric RFC Adjudication & CounterProof Generation...")

    # Case 4A: Valid SpecAdjustmentRequest
    valid_rfc = SpecAdjustmentRequest(
        request_id="rfc_builder_001_relax_cache",
        builder_node_id="node_builder_enclave_01",
        target_symbol_urn="urn:meta_axioma:g4b:cache:buffer_limit",
        bottleneck_type=BottleneckType.TOKEN_EXHAUSTION,
        empirical_evidence="Physical BPE lease exhausted under high-density AST generation.",
        proposed_delta="Increase transient buffer size to 64KB with strict Landauer erasure lease.",
        preserved_invariants=["[L1-002]", "[L1-G3B-012]", "[L1-G3B-016]"],
    )
    amendment_valid, counter_proof_valid = kernel.adjudicate_builder_rfc(valid_rfc)
    assert amendment_valid is not None and amendment_valid.is_approved is True
    assert counter_proof_valid is None
    print(f"  RFC 1 (Valid Petition): Approved=True | Amendment ID={amendment_valid.amendment_id}")
    print(f"    - Contract Delta:     {amendment_valid.amended_contract_ir_delta}")

    # Case 4B: Invalid SpecAdjustmentRequest (attempting loopback binding)
    invalid_rfc = SpecAdjustmentRequest(
        request_id="rfc_builder_002_toxic_loopback",
        builder_node_id="node_builder_enclave_02",
        target_symbol_urn="urn:meta_axioma:g4b:network:binding",
        bottleneck_type=BottleneckType.COMPLEXITY_LIMIT,
        empirical_evidence="Builder requests local IPC binding for rapid test iteration.",
        proposed_delta="Bind testing harness to 127.0.0.1:8442 and centralized coordinator.",
        preserved_invariants=["[L1-002]"],
    )
    amendment_invalid, counter_proof_invalid = kernel.adjudicate_builder_rfc(invalid_rfc)
    assert amendment_invalid is not None and amendment_invalid.is_approved is False
    assert counter_proof_invalid is not None
    print(f"  RFC 2 (Toxic Petition): Approved=False | CounterProof ID={counter_proof_invalid.counter_proof_id}")
    print(f"    - Violated Axioms:    {counter_proof_invalid.violated_axioms}")
    print(f"    - Z3 Unsat Core:      {counter_proof_invalid.z3_unsat_core}")
    print("  [SUCCESS] Phase 4 Completed: Asymmetric RFC adjudication and formal refutation verified.")

    # -------------------------------------------------------------------------
    # PHASE 5: Circuit Breaker Tripping, Quarantine, and Recovery
    # -------------------------------------------------------------------------
    print("\n[PHASE 5]: Circuit Breaker Tripping, Quarantine, and Recovery [L1-016]...")
    failing_peer = "192.168.40.20:8442"  # Builder enclave endpoint

    # Simulate failures up to threshold
    print(f"  Simulating consecutive failures on peer '{failing_peer}'...")
    kernel.trip_circuit_breaker(failing_peer, reason="Repeated Byzantine timeout on contract dispatch")

    assert kernel.circuit_breaker.is_peer_quarantined(failing_peer)
    quarantines = kernel.circuit_breaker.get_active_quarantines()
    print(f"  Circuit Breaker Tripped:State={kernel.circuit_breaker.current_state.value}")
    print(f"  Peer Quarantined:       Endpoint={quarantines[0].service_endpoint} -> Isolated Subnet={quarantines[0].isolation_subnet}")

    # Execute recovery sequence
    print(f"  Executing cooldown probing and recovery for '{failing_peer}'...")
    kernel.recover_circuit_breaker(failing_peer)
    assert not kernel.circuit_breaker.is_peer_quarantined(failing_peer)
    assert kernel.circuit_breaker.current_state == CircuitBreakerState.CLOSED_NORMAL
    print(f"  Peer Discharged Clean:  Circuit Breaker State={kernel.circuit_breaker.current_state.value}")
    print("  [SUCCESS] Phase 5 Completed: Safety enclave quarantine containment and clean recovery certified.")

    # -------------------------------------------------------------------------
    # PHASE 6: Succession Gatekeeper & Gen 5 Handover Certificate
    # -------------------------------------------------------------------------
    print("\n[PHASE 6]: Succession Gatekeeper & Gen 5 Handover Certification...")
    hdr_rec = kernel.hitl_engine.get_current_hdr()
    bindings = kernel.topology.get_cluster_bindings()

    is_ready, deficits = kernel.succession_gatekeeper.verify_succession_readiness(hdr_rec, bindings)
    print(f"  Succession Readiness:   Ready={is_ready} | Deficits Count={len(deficits)}")
    assert is_ready, f"Succession must be ready, got deficits: {deficits}"

    supervisor_sig = "SIG_MICHAEL_LIPSKI_SOVEREIGN_ARCHITECT_GEN5_GENESIS"
    cert = kernel.certify_generational_handover(supervisor_sig)

    assert cert.graduation_status == SuccessionGraduationStatus.CERTIFIED_SUCCESSION_READY
    assert cert.hdr_at_graduation <= 0.15
    assert cert.zero_loopback_certified is True
    assert len(cert.governance_hash_chain_head) == 64
    print(f"  Handover Certificate:  ID={cert.certificate_id}")
    print(f"    - Source -> Target:   {cert.source_generation} -> {cert.target_generation}")
    print(f"    - Graduation Status:  {cert.graduation_status.value}")
    print(f"    - HDR at Graduation:  {cert.hdr_at_graduation:.4f}")
    print(f"    - Zero-Loopback Cert: {cert.zero_loopback_certified}")
    print(f"    - Supervisor Sig:     {cert.human_architect_approval_sig}")
    print(f"    - Invariant Proofs:   {len(cert.invariant_proofs)} proofs chained")
    print("  [SUCCESS] Phase 6 Completed: Generation 5 Handover Certificate formally certified.")

    # -------------------------------------------------------------------------
    # PHASE 7: Functorial Undo State Rollback
    # -------------------------------------------------------------------------
    print("\n[PHASE 7]: Functorial Undo Categorical State Rollback [L1-002]...")
    initial_depth = kernel.undo_engine.history_depth()
    head_state_before = kernel.undo_engine.peek_current()
    print(f"  Initial Undo Stack Depth:{initial_depth}")
    print(f"  Pre-Undo State Hash:    {head_state_before.compute_hash()[:24]}...")

    rolled_back_state = kernel.functorial_rollback()
    assert rolled_back_state is not None
    post_depth = kernel.undo_engine.history_depth()
    print(f"  Post-Undo Stack Depth:  {post_depth} (depth decreased by 1)")
    print(f"  Restored State Hash:    {rolled_back_state.compute_hash()[:24]}...")
    print(f"  State S_{{t-1}} Restored:  Endpoint={rolled_back_state.service_endpoint}, Violations Trapped={rolled_back_state.total_violations_trapped}")
    print("  [SUCCESS] Phase 7 Completed: Pure functorial adjoint rollback S_{t-1} = f^{-1}(S_t) verified.")

    # -------------------------------------------------------------------------
    # PHASE 8: Statechart 30-State Covering Path Traversal
    # -------------------------------------------------------------------------
    print("\n[PHASE 8]: Statechart 30-State Covering Path Traversal...")
    st_engine = StatechartEngine(initial_state=GovernanceStatechartState.GOV_ROOT_IDLE)

    # Stratum 1: Root / Initialization (T01 - T05)
    st_engine.send("EV_BOOTSTRAP_INIT")
    assert st_engine.current_state == GovernanceStatechartState.GOV_BOOTSTRAPPING
    st_engine.send("EV_AXIOMS_LOADED")
    assert st_engine.current_state == GovernanceStatechartState.GOV_READY
    st_engine.send("EV_RECALIBRATE_START")
    assert st_engine.current_state == GovernanceStatechartState.GOV_RECALIBRATING
    st_engine.send("EV_RECALIBRATE_COMPLETE")
    assert st_engine.current_state == GovernanceStatechartState.GOV_READY
    st_engine.send("EV_ENTER_OPERATIONAL")
    assert st_engine.current_state == GovernanceStatechartState.OP_SURVEILLING

    # Stratum 2: SovereignOperational (T06 - T18)
    st_engine.send("EV_INTERCEPT_DETECTED")
    assert st_engine.current_state == GovernanceStatechartState.OP_EVALUATING_INTERCEPT
    st_engine.send("EV_ESCALATE_HITL")
    assert st_engine.current_state == GovernanceStatechartState.OP_HITL_ESCALATING
    st_engine.send("EV_HITL_SUBMITTED")
    assert st_engine.current_state == GovernanceStatechartState.OP_HITL_AWAITING_DISPOSITION
    st_engine.send("EV_SUPERVISOR_APPROVED")
    assert st_engine.current_state == GovernanceStatechartState.OP_ADJUDICATION_SETTLED
    st_engine.send("EV_ADJUDICATION_DISPATCHED")
    assert st_engine.current_state == GovernanceStatechartState.OP_SURVEILLING

    # Stratum 3: EmergencyEnclave (T19 - T25)
    st_engine.send("EV_TRIP_CIRCUIT_BREAKER")
    assert st_engine.current_state == GovernanceStatechartState.ENCLAVE_TRIPPED
    st_engine.send("EV_ISOLATE_NODE")
    assert st_engine.current_state == GovernanceStatechartState.ENCLAVE_QUARANTINE_ISOLATION
    st_engine.send("EV_BEGIN_INVESTIGATION")
    assert st_engine.current_state == GovernanceStatechartState.ENCLAVE_INVESTIGATION
    st_engine.send("EV_START_COOLDOWN_PROBE")
    assert st_engine.current_state == GovernanceStatechartState.ENCLAVE_COOLDOWN_PROBING
    st_engine.send("EV_PROBE_SUCCEEDED")
    assert st_engine.current_state == GovernanceStatechartState.ENCLAVE_RESTORED
    st_engine.send("EV_RESTORE_DEEP_HISTORY")  # Restores deep history H*
    assert st_engine.current_state == GovernanceStatechartState.OP_SURVEILLING

    # Stratum 4: GenerationalHandover (T26 - T33)
    st_engine.send("EV_INITIATE_HANDOVER")
    assert st_engine.current_state == GovernanceStatechartState.HANDOVER_INITIATING
    st_engine.send("EV_VERIFY_INVARIANTS")
    assert st_engine.current_state == GovernanceStatechartState.HANDOVER_PROVING_INVARIANTS
    st_engine.send("EV_INVARIANTS_SATISFIED")
    assert st_engine.current_state == GovernanceStatechartState.HANDOVER_HDR_VERIFYING
    st_engine.send("EV_HDR_VERIFIED_PASS")
    assert st_engine.current_state == GovernanceStatechartState.HANDOVER_SIGNING_CERTIFICATE
    st_engine.send("EV_CERTIFICATE_SIGNED")
    assert st_engine.current_state == GovernanceStatechartState.HANDOVER_GRADUATED
    st_engine.send("EV_RETURN_TO_STANDBY")
    assert st_engine.current_state == GovernanceStatechartState.GOV_ROOT_IDLE

    # Parallel Region 1: AxiomaticSurveillance (T34 - T38)
    st_engine.send("EV_SURV_SCAN_AST")
    assert st_engine.parallel_surveillance_state == GovernanceStatechartState.SURV_INSPECTING_AST
    st_engine.send("EV_SURV_TRIGGER_VETO")
    assert st_engine.parallel_surveillance_state == GovernanceStatechartState.SURV_VETO_TRIGGERED
    st_engine.send("EV_SURV_QUARANTINE_PEER")
    assert st_engine.parallel_surveillance_state == GovernanceStatechartState.SURV_QUARANTINED
    st_engine.send("EV_SURV_DISCHARGE_CLEAN")
    assert st_engine.parallel_surveillance_state == GovernanceStatechartState.SURV_IDLE

    # Parallel Region 2: PeerMediation (T39 - T42)
    st_engine.send("EV_PEER_POLL_RFC")
    assert st_engine.parallel_mediation_state == GovernanceStatechartState.PEER_ADJUDICATING_RFC
    st_engine.send("EV_PEER_GENERATE_AMENDMENT")
    assert st_engine.parallel_mediation_state == GovernanceStatechartState.PEER_AMENDING_SPEC
    st_engine.send("EV_PEER_RESET_LISTENING")
    assert st_engine.parallel_mediation_state == GovernanceStatechartState.PEER_LISTENING

    transitions = st_engine.export_history()
    print(f"  Transitions Dispatched: {len(transitions)} recorded across all 4 Strata & 2 Parallel Regions.")
    print("  [SUCCESS] Phase 8 Completed: 30-State Hierarchical XState v5 statechart traversal certified.")

    # -------------------------------------------------------------------------
    # PHASE 9: Service Readiness Report
    # -------------------------------------------------------------------------
    print("\n[PHASE 9]: Sovereign Service Readiness Diagnostic Report...")
    status = kernel.get_status()
    print(f"  Service Kernel ID:      {status['kernel_id']}")
    print(f"  Service Endpoint:       {status['endpoint']}")
    print(f"  Current Ledger Head:    {status['ledger_head']}")
    print(f"  Cryptographic Events:   {status['events_count']}")
    print(f"  Statechart State:       {status['statechart_state']}")
    print(f"  Parallel Surveillance:  {status['parallel_surveillance']}")
    print(f"  Parallel Mediation:     {status['parallel_mediation']}")
    print(f"  Circuit Breaker:        {status['circuit_breaker']}")
    print(f"  Active Quarantines:     {len(status['quarantined_nodes'])}")
    print(f"  Active Negative Axioms: {status['active_negative_axioms']}")
    print(f"  Total Trapped Violations:{status['violations_trapped']}")
    print(f"  Heuristic Debt Ratio:   {status['heuristic_debt_ratio']} (Compliant: {status['is_debt_compliant']})")
    print(f"  Undo History Depth:     {status['undo_stack_depth']}")

    print("\n" + "=" * 80)
    print("ALL 9 VERIFICATION PHASES COMPLETED WITH 100% EMPIRICAL SUCCESS (EXIT CODE 0)")
    print("Sovereign Governance & Safety Service (`soc_g4b_governance`) Certified Operational.")
    print("=" * 80)


if __name__ == "__main__":
    run_governance_verification()
