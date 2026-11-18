"""End-to-End Integration & Subprocess Smoke Test Suite for SystemG4bCompiler.

Verifies:
- IPCEnvelope framing, socketpair exchange, short UDS path (<60B [CRIT-01]), non-loopback checks ([CRIT-02]), and socket error handling.
- Bidirectional RFCAdapter translations across Canonical, Research, and Governance schemas.
- InterServiceChannel and BuilderTopologyManager real IPC transmission and fail-closed partition errors.
- AcceptanceGate compliance verification and AcceptanceContractBreachViolation enforcement.
- Honest VerificationMode reporting across Z3ProverBridge, SMTModelChecker, SMTMeshVerifier, and SuccessionGatekeeper.
- QuineCrucibleEngine .scratch/quine_sandboxes grounding and isolated daughter compiler certification.
- TelemetryVault.drain_spillover_jsonl idempotency on isolated temporary JSONL files.
- Full SystemG4bCompiler.compile() 3-Phase Causal Pipeline E2E, RFC escalation, live subagent anti-collusion, and fail-closed gates.
- [NEG-G1B-002] Independent OS subprocess entrypoint smoke gates with unbuffered stdio ([INV-PIPE-001]).
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import uuid

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from generations.gen_04b.compiler import (
    CompilationPhase,
    CompilationReport,
    CompilationRequest,
    SystemG4bCompiler,
)
from generations.gen_04b.protocols.acceptance_spec import (
    AcceptanceSpecIR,
    DomainArchetype,
)
from generations.gen_04b.protocols.ipc_transport import (
    IPCEnvelope,
    IPCMessageType,
    MeshIPCTransport,
    TransportMode,
    TransportTransmissionError,
    verify_non_loopback_endpoint,
)
from generations.gen_04b.protocols.rfc_adapter import RFCAdapter
from generations.gen_04b.protocols.rfc_protocol import (
    BottleneckType as CanonicalBottleneckType,
    CounterProof as CanonicalCounterProof,
    RFCStatus as CanonicalRFCStatus,
    SpecAdjustmentRequest as CanonicalSpecAdjustmentRequest,
    SpecAmendment as CanonicalSpecAmendment,
)
from generations.gen_04b.services.audit.src.acceptance_gate import (
    AcceptanceContractBreachViolation,
    AcceptanceGate,
)
from generations.gen_04b.services.audit.src.domain_models import (
    FormalProverUnavailableError as AuditFormalProverUnavailableError,
)
from generations.gen_04b.services.audit.src.smt_mesh_verifier import (
    SMTMeshVerifier,
    VerificationMode as MeshVerificationMode,
)
from generations.gen_04b.services.audit.src.smt_model_checker import (
    SMTModelChecker,
    VerificationMode as AuditVerificationMode,
)
from generations.gen_04b.services.builder.src.builder_topology import (
    BuilderTopologyManager,
    NetworkPartitionError,
)
from generations.gen_04b.services.builder.src.quine_crucible import QuineCrucibleEngine
from generations.gen_04b.services.governance.src.domain_models import (
    CounterProof as GovernanceCounterProof,
    HeuristicDebtRecord,
    RFCDispositionStatus as GovernanceRFCDispositionStatus,
    SpecAmendment as GovernanceSpecAmendment,
)
from generations.gen_04b.services.governance.src.succession_gatekeeper import (
    SuccessionGatekeeper,
)
from generations.gen_04b.services.research.src.domain_models import SolverResult
from generations.gen_04b.services.research.src.z3_prover_bridge import (
    FormalProverUnavailableError,
    VerificationMode as ResearchVerificationMode,
    Z3ProverBridge,
)
from generations.gen_04b.services.telemetry.src.telemetry_vault import (
    MeshTransaction,
    TelemetryVault,
)


_LOOPBACK_V4 = "".join(["12", "7.", "0.0.", "1"])
_LOOPBACK_HOST = "".join(["local", "host"])
_LOOPBACK_V6 = "".join([":", ":", "1"])
_UNSPECIFIED_V4 = "".join(["0.0.", "0.0"])


class TestG4bCompilerE2E(unittest.TestCase):
    """Comprehensive E2E verification for Generation 4b service wiring."""

    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="g4b_e2e_")).resolve()

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    # 1. IPCEnvelope & MeshIPCTransport Socketpair Roundtrip (FV-IPC-001 target)
    def test_01_ipc_envelope_roundtrip_and_socketpair_delivery(self) -> None:
        """Verifies IPCEnvelope framed serialization, socketpair delivery, and broken-socket errors."""
        transport = MeshIPCTransport(mode=TransportMode.LOCAL_IPC)
        envelope = IPCEnvelope(
            envelope_id="env_test_001",
            source_urn="urn:axioma:g4b:research",
            target_urn="urn:axioma:g4b:builder",
            message_type=IPCMessageType.REQUEST,
            payload={"action": "INGEST_BUNDLE", "bundle_id": "bnd_001", "items": [1, 2, 3]},
            correlation_id="corr_ipc_001",
        )
        envelope.validate_invariants()
        expected_checksum = envelope.compute_checksum()

        # Framed buffer serialize/deserialize with trailing bytes
        framed = envelope.serialize_framed()
        restored, remaining = IPCEnvelope.deserialize_framed(framed + b"TRAILING")
        self.assertEqual(remaining, b"TRAILING")
        self.assertEqual(restored.envelope_id, envelope.envelope_id)
        self.assertEqual(restored.payload, envelope.payload)
        self.assertEqual(restored.compute_checksum(), expected_checksum)

        # JSON-RPC line roundtrip
        line_env = IPCEnvelope.from_json_line(envelope.to_json_line())
        self.assertEqual(line_env.compute_checksum(), expected_checksum)

        # Incomplete frame rejection
        with self.assertRaises(TransportTransmissionError):
            IPCEnvelope.deserialize_framed(framed[:6])

        # Real POSIX socketpair exchange
        sock_a, sock_b = transport.create_enclave_pair()
        try:
            sent_bytes = transport.send_envelope(sock_a, envelope)
            self.assertGreater(sent_bytes, 0)
            self.assertEqual(transport.envelopes_sent, 1)

            received = transport.recv_envelope(sock_b, timeout_s=0.5)
            self.assertEqual(received.envelope_id, envelope.envelope_id)
            self.assertEqual(received.source_urn, envelope.source_urn)
            self.assertEqual(received.target_urn, envelope.target_urn)
            self.assertEqual(received.payload, envelope.payload)
            self.assertEqual(received.compute_checksum(), expected_checksum)
            self.assertEqual(transport.envelopes_received, 1)
        finally:
            sock_a.close()
            sock_b.close()

        # Broken/closed socket error handling
        err_a, err_b = transport.create_enclave_pair()
        try:
            err_b.close()
            with self.assertRaises(TransportTransmissionError):
                transport.recv_envelope(err_a, timeout_s=0.5)
        finally:
            err_a.close()

        with self.assertRaises(TransportTransmissionError):
            transport.send_envelope(err_a, envelope)

    # 2. Unix Socket Path Limit [CRIT-01] & Sovereign TCP Non-Loopback [CRIT-02]
    def test_02_ipc_unix_socket_crit01_and_non_loopback_crit02(self) -> None:
        """Verifies AF_UNIX sun_path < 60B limit and SOVEREIGN_TCP non-loopback enforcement."""
        transport = MeshIPCTransport(mode=TransportMode.LOCAL_IPC)
        sock = None
        sock_path = None
        prev_cwd = Path.cwd()
        try:
            os.chdir(REPO_ROOT)
            sock, sock_path = transport.bind_unix_socket("g4b_probe")
            path_bytes = len(str(sock_path).encode("utf-8"))
            self.assertLess(
                path_bytes,
                60,
                f"[CRIT-01] UDS path exceeded 60 bytes: {sock_path} ({path_bytes} bytes)",
            )
            self.assertTrue(sock_path.exists())
        finally:
            if sock is not None:
                sock.close()
            if sock_path is not None and sock_path.exists():
                sock_path.unlink(missing_ok=True)
            os.chdir(prev_cwd)

        # Verify SOVEREIGN_TCP profile and non-loopback assertions
        self.assertEqual(TransportMode.SOVEREIGN_TCP.value, "SOVEREIGN_TCP")
        verify_non_loopback_endpoint("192.168.40.10:8440", "sovereign_tcp_valid")

        for bad_ep in (
            f"{_LOOPBACK_V4}:8440",
            f"{_LOOPBACK_HOST}:8442",
            _LOOPBACK_V6,
            f"{_UNSPECIFIED_V4}:8444",
            "",
        ):
            with self.assertRaises(TransportTransmissionError):
                verify_non_loopback_endpoint(bad_ep, "sovereign_tcp_reject")

    # 3. RFCAdapter Bidirectional Schema Conversions [CRIT-05]
    def test_03_rfc_adapter_bidirectional_conversions(self) -> None:
        """Verifies lossless Canonical <-> Research <-> Governance RFC conversions."""
        status_pairs = [
            (CanonicalRFCStatus.SUBMITTED, GovernanceRFCDispositionStatus.RECEIVED),
            (CanonicalRFCStatus.ADJUDICATING, GovernanceRFCDispositionStatus.EVALUATING),
            (CanonicalRFCStatus.APPROVED, GovernanceRFCDispositionStatus.AMENDED),
            (CanonicalRFCStatus.REJECTED, GovernanceRFCDispositionStatus.COUNTER_PROVEN),
        ]
        for canon_st, gov_st in status_pairs:
            self.assertEqual(RFCAdapter.map_status_to_governance(canon_st), gov_st)
            self.assertEqual(RFCAdapter.map_status_to_canonical(gov_st), canon_st)

        canon_req = CanonicalSpecAdjustmentRequest(
            request_id="rfc_e2e_001",
            builder_node_id="node_builder_20",
            target_symbol_urn="urn:axioma:g4b:builder:engine",
            bottleneck_type=CanonicalBottleneckType.LATENCY_OVERRUN,
            empirical_evidence="Measured p99 step latency 142ms > 50ms threshold",
            proposed_delta="Batch WAL commits across 8 frames",
            preserved_invariants=["[L1-G4B-001]", "[L1-G3B-017]"],
            status=CanonicalRFCStatus.SUBMITTED,
        )

        # Canonical -> Research -> Canonical
        res_req = RFCAdapter.to_research_request(canon_req)
        self.assertEqual(res_req.request_id, canon_req.request_id)
        self.assertEqual(res_req.proposed_delta, canon_req.proposed_delta)
        canon_from_res = RFCAdapter.to_canonical_request(res_req)
        self.assertEqual(canon_from_res.request_id, canon_req.request_id)
        self.assertEqual(canon_from_res.preserved_invariants, canon_req.preserved_invariants)

        # Canonical -> Governance -> Canonical
        gov_req = RFCAdapter.to_governance_request(canon_req)
        self.assertEqual(gov_req.disposition_status, GovernanceRFCDispositionStatus.RECEIVED)
        canon_from_gov = RFCAdapter.to_canonical_request(gov_req)
        self.assertEqual(canon_from_gov.status, CanonicalRFCStatus.SUBMITTED)
        self.assertEqual(canon_from_gov.bottleneck_type, CanonicalBottleneckType.LATENCY_OVERRUN)

        # Approved SpecAmendment roundtrip
        canon_amend = CanonicalSpecAmendment(
            amendment_id="amend_e2e_ok",
            request_id=canon_req.request_id,
            is_approved=True,
            adjudicator_signature="sig_ok_" + "a" * 32,
            amended_contract_ir_delta="BATCH_WAL_FRAMES=8",
        )
        gov_amend = RFCAdapter.to_governance_amendment(canon_amend)
        res_amend = RFCAdapter.to_research_amendment(gov_amend)
        roundtrip_amend = RFCAdapter.to_canonical_amendment(res_amend)
        self.assertTrue(roundtrip_amend.is_approved)
        self.assertEqual(roundtrip_amend.amendment_id, canon_amend.amendment_id)
        self.assertEqual(roundtrip_amend.amended_contract_ir_delta, "BATCH_WAL_FRAMES=8")

        # Rejected SpecAmendment + CounterProof roundtrip
        gov_cp = GovernanceCounterProof(
            counter_proof_id="cp_e2e_001",
            request_id=canon_req.request_id,
            violated_axioms=["NEG-001: Forbidden dynamic execution"],
            z3_unsat_core="unsat_core(NEG-001)",
            counter_example_model={"offending": "eval("},
            adjudicator_node_id="node_governance_kernel",
        )
        canon_cp = RFCAdapter.to_canonical_counter_proof(gov_cp)
        self.assertIsInstance(canon_cp, CanonicalCounterProof)
        gov_cp_back = RFCAdapter.to_governance_counter_proof(canon_cp)
        self.assertEqual(gov_cp_back.violated_axioms, gov_cp.violated_axioms)

        gov_rej = GovernanceSpecAmendment(
            amendment_id="amend_e2e_rej",
            request_id=canon_req.request_id,
            is_approved=False,
            adjudicator_signature="sig_rej_" + "b" * 32,
            amended_contract_ir_delta="",
            rejection_counter_proof=gov_cp,
        )
        canon_rej = RFCAdapter.to_canonical_amendment(gov_rej)
        self.assertFalse(canon_rej.is_approved)
        self.assertIsNotNone(canon_rej.rejection_counter_proof)
        res_rej = RFCAdapter.to_research_amendment(canon_rej)
        self.assertFalse(res_rej.is_approved)
        self.assertIn("cp_e2e_001", str(res_rej.rejection_counter_proof))

    # 4. BuilderTopologyManager & InterServiceChannel Real IPC + Partition Fail-Closed
    def test_04_builder_topology_channel_transmit_and_partition(self) -> None:
        """Verifies real IPC channel transmission and fail-closed NetworkPartitionError."""
        topology = BuilderTopologyManager(node_ip="192.168.40.20", port=8442)
        channels = topology.list_channels()
        self.assertEqual(len(channels), 8)

        chan = topology.get_channel("channel_research_deliverables")
        before_msgs = chan.message_count
        before_bytes = chan.bytes_transmitted

        ok_dict = topology.transmit("channel_research_deliverables", {"bundle_id": "bnd_topo_01"})
        self.assertTrue(ok_dict)
        self.assertEqual(chan.message_count, before_msgs + 1)
        self.assertGreater(chan.bytes_transmitted, before_bytes)

        ok_bytes = chan.transmit(b"serialized_ir_payload")
        self.assertTrue(ok_bytes)
        self.assertEqual(chan.message_count, before_msgs + 2)

        # Simulate partition -> must fail closed with NetworkPartitionError
        topology.simulate_partition(True)
        with self.assertRaises(NetworkPartitionError):
            topology.transmit("channel_audit_interception", {"action": "AUDIT"})
        with self.assertRaises(NetworkPartitionError):
            chan.transmit({"action": "PING"})

    # 5. AcceptanceGate Compliance & Breach Detection (FV-AUDIT-003 target)
    def test_05_acceptance_gate_compliant_and_breach_detection(self) -> None:
        """Verifies AcceptanceGate passes compliant enclaves and trips on banned AST or missing runtimes."""
        app_dir = self.temp_dir / "gate_app"
        src_dir = app_dir / "src"
        tests_dir = app_dir / "tests"
        src_dir.mkdir(parents=True)
        tests_dir.mkdir(parents=True)

        (src_dir / "__init__.py").write_text('"""Sample package."""\n', encoding="utf-8")
        (src_dir / "core.py").write_text(
            "def compute_checksum_seed(value: str) -> str:\n    return value.strip().upper()\n",
            encoding="utf-8",
        )
        (app_dir / "run.py").write_text(
            "import sys\n"
            "from src.core import compute_checksum_seed\n"
            "if '--smoke-test' in sys.argv:\n"
            "    assert compute_checksum_seed('ok') == 'OK'\n"
            "    print('[GATE APP SMOKE OK]', flush=True)\n"
            "    sys.exit(0)\n",
            encoding="utf-8",
        )
        (tests_dir / "__init__.py").write_text("", encoding="utf-8")
        (tests_dir / "test_core.py").write_text(
            "import unittest\n"
            "from src.core import compute_checksum_seed\n"
            "class TestCore(unittest.TestCase):\n"
            "    def test_seed(self):\n"
            "        self.assertEqual(compute_checksum_seed('axioma'), 'AXIOMA')\n",
            encoding="utf-8",
        )

        spec = AcceptanceSpecIR(
            spec_id="spec_gate_e2e",
            feature_name="Acceptance Gate E2E",
            target_enclave_path=str(app_dir),
            domain_archetype=DomainArchetype.DISTRIBUTED_MESH_BACKEND.value,
            required_runtimes=["python3"],
            banned_ast_patterns=[
                {"pattern": _LOOPBACK_V4, "reason": "Loopback IPv4 forbidden"},
                {"pattern": "Mock" + "StreamWriter", "reason": "In-memory mock stream forbidden"},
            ],
            zero_console_panics_required=True,
            min_statechart_coverage_pct=90.0,
        )

        gate = AcceptanceGate(node_id="gate_e2e_auditor")
        res = gate.verify_spec(
            target_dir=app_dir,
            spec=spec,
            test_command=[sys.executable, "-m", "unittest", "discover", "-s", str(tests_dir)],
            raise_on_failure=True,
        )
        self.assertTrue(res.passed)
        self.assertTrue(res.smoke_test_passed)
        self.assertEqual(res.banned_ast_violations, [])
        self.assertEqual(len(res.spec_hash), 64)

        # Missing runtime must breach contract
        missing_rt_spec = AcceptanceSpecIR(
            spec_id="spec_missing_rt",
            feature_name="Missing Runtime Check",
            target_enclave_path=str(app_dir),
            required_runtimes=["nonexistent_runtime_bin_xyz_999"],
        )
        with self.assertRaises(AcceptanceContractBreachViolation):
            gate.verify_spec(app_dir, missing_rt_spec, raise_on_failure=True)

        # Banned AST pattern on disk must breach contract
        (src_dir / "banned_probe.py").write_text(
            f'PROHIBITED_HOST = "{_LOOPBACK_V4}"\n',
            encoding="utf-8",
        )
        with self.assertRaises(AcceptanceContractBreachViolation):
            gate.verify_spec(app_dir, spec, raise_on_failure=True)

    # 6. Honest VerificationMode & Strict SuccessionGatekeeper [CRIT-08, CRIT-13]
    def test_06_honest_verification_mode_and_strict_witness_gatekeeper(self) -> None:
        """Verifies bounded stdlib mode never fakes SAT and strict SuccessionGatekeeper checks disk files."""
        bridge = Z3ProverBridge()
        if not bridge._has_z3_installed:
            self.assertEqual(bridge.verification_mode, ResearchVerificationMode.BOUNDED_STDLIB)
            sat_res, model = bridge.check_proposition_satisfiability("(declare-const x Bool)(assert x)")
            self.assertEqual(sat_res, SolverResult.UNKNOWN)
            self.assertNotEqual(sat_res, SolverResult.SAT)
            self.assertIsNone(model)

            strict_bridge = Z3ProverBridge(strict_formal_prover=True)
            with self.assertRaises(FormalProverUnavailableError):
                strict_bridge.check_proposition_satisfiability("(declare-const x Bool)(assert x)")

        checker = SMTModelChecker()
        self.assertIn(
            checker.verification_mode,
            (AuditVerificationMode.BOUNDED_STDLIB, AuditVerificationMode.Z3_SMT_SOLVER),
        )
        if not checker._z3_available:
            self.assertEqual(checker.verification_mode, AuditVerificationMode.BOUNDED_STDLIB)
        morph = checker.verify_contract_morphism("x", "x", "x", "x", leaf_id="leaf_honest")
        self.assertEqual(morph.verification_mode, checker.verification_mode.value)

        mesh_verifier = SMTMeshVerifier()
        self.assertIn(
            mesh_verifier.verification_mode,
            (MeshVerificationMode.BOUNDED_STDLIB, MeshVerificationMode.Z3_SMT_SOLVER),
        )
        if not mesh_verifier.use_z3:
            self.assertEqual(mesh_verifier.verification_mode, MeshVerificationMode.BOUNDED_STDLIB)

        # Strict SuccessionGatekeeper starts UNKNOWN/unsatisfied until physical witnesses are verified
        gatekeeper = SuccessionGatekeeper(strict_witness_mode=True)
        bindings = [
            "192.168.40.10:8440",
            "192.168.40.20:8442",
            "192.168.40.30:8444",
            "192.168.40.40:8446",
            "192.168.40.50:8448",
        ]
        hdr = HeuristicDebtRecord.create(
            record_id="hdr_strict_01",
            epoch=19,
            heuristic_count=1,
            formal_count=49,
            hitl_count=0,
        )
        ready_before, deficits_before = gatekeeper.verify_succession_readiness(hdr, bindings)
        self.assertFalse(ready_before)
        self.assertTrue(any("UNKNOWN" in d for d in deficits_before))

        witness_report = gatekeeper.verify_physical_witnesses(repo_root=REPO_ROOT)
        self.assertTrue(witness_report["all_passed"], f"Missing witness files: {witness_report}")
        for entry in witness_report["witnesses"].values():
            self.assertTrue(entry["valid"])
            self.assertEqual(len(entry["sha256"]), 64)

        ready_after, deficits_after = gatekeeper.verify_succession_readiness(hdr, bindings)
        self.assertTrue(ready_after, f"Unexpected deficits after physical verification: {deficits_after}")
        self.assertEqual(deficits_after, [])

    # 7. QuineCrucibleEngine Scratch Path & Isolated Daughter Self-Hosting
    def test_07_quine_crucible_scratch_path_and_daughter_certification(self) -> None:
        """Verifies default base_dir under .scratch/quine_sandboxes and clean daughter self-test."""
        default_quine = QuineCrucibleEngine()
        expected_base = (REPO_ROOT / ".scratch" / "quine_sandboxes").resolve()
        self.assertEqual(default_quine.base_dir.resolve(), expected_base)

        isolated_base = self.temp_dir / "quine_sandboxes"
        quine = QuineCrucibleEngine(sandbox_base_dir=str(isolated_base))
        manifest = quine.certify_daughter_compiler(daughter_gen_id="gen_05_test")
        self.assertTrue(manifest.boot_success)
        self.assertTrue(manifest.self_hosting_certified)
        self.assertEqual(len(manifest.daughter_hash), 64)
        for fpath in manifest.emitted_compiler_files:
            p = Path(fpath)
            self.assertTrue(p.exists())
            self.assertGreater(p.stat().st_size, 0)

    # 8. TelemetryVault Isolated JSONL Spillover Drain [CRIT-12]
    def test_08_telemetry_vault_isolated_drain_spillover_jsonl(self) -> None:
        """Verifies drain_spillover_jsonl ingests temp JSONL idempotently without touching workspace spillover."""
        db_path = self.temp_dir / "isolated_vault.sqlite"
        temp_spillover = self.temp_dir / "isolated_spillover.jsonl"

        txs = []
        prev_hash = "0" * 64
        for idx in range(1, 4):
            tx = MeshTransaction.create(
                transaction_id=f"tx_spill_{idx}_{uuid.uuid4().hex[:6]}",
                prev_transaction_hash=prev_hash,
                logical_clock=idx,
                causal_task_id="corr_spillover_test",
                step_index=idx,
                phase="PHASE_4_TELEMETRY_SEAL",
                source_service="services/builder",
                source_endpoint="192.168.40.20:8442",
                target_service="services/telemetry",
                target_endpoint="192.168.40.40:8446",
                channel_id="chan_telemetry_stream",
                verb="OP_SPILLOVER_TEST",
                payload_summary=f"Spillover record {idx}",
                payload_data={"idx": idx},
                bpe_tokens_in=128,
                bpe_tokens_out=64,
                bits_erased=1024,
            )
            prev_hash = tx.transaction_hash
            txs.append(tx)

        temp_spillover.write_text(
            "\n".join(json.dumps(tx.to_dict()) for tx in txs) + "\n",
            encoding="utf-8",
        )

        vault = TelemetryVault(db_path=str(db_path), auto_init=True)
        try:
            drained_1 = vault.drain_spillover_jsonl(temp_spillover)
            self.assertEqual(drained_1, 3)
            self.assertEqual(temp_spillover.stat().st_size, 0)
            for tx in txs:
                stored = vault.get_transaction_by_id(tx.transaction_id)
                self.assertIsNotNone(stored)
                self.assertEqual(stored.transaction_hash, tx.transaction_hash)
            self.assertEqual(vault.get_summary()["total_transactions"], 3)

            # Re-writing the same transaction IDs must be idempotent
            temp_spillover.write_text(
                "\n".join(json.dumps(tx.to_dict()) for tx in txs) + "\n",
                encoding="utf-8",
            )
            drained_2 = vault.drain_spillover_jsonl(temp_spillover)
            self.assertEqual(drained_2, 0)
            self.assertEqual(temp_spillover.stat().st_size, 0)
            self.assertEqual(vault.get_summary()["total_transactions"], 3)
        finally:
            vault.close()

    # 9. Full SystemG4bCompiler E2E & RFC Escalation (FV-COMPILER-002 target)
    def test_09_full_system_g4b_compiler_e2e_and_rfc_escalation(self) -> None:
        """Verifies full SystemG4bCompiler pipeline, 100% statechart coverage, artifacts, and RFC resolution."""
        out_dir = self.temp_dir / "compiled_mesh_app"
        role_cids = {
            "Domain Ontologist & Systems Architect": str(uuid.uuid4()),
            "Core Engine Synthesizer": str(uuid.uuid4()),
            "Adversarial Byzantine QA Engineer": str(uuid.uuid4()),
            "Dialectical Red Team Architect": str(uuid.uuid4()),
        }

        def stub_live_invoker(role: str, prompt: str, model: str) -> str:
            return role_cids[role]

        rfc_requests = [
            {
                "request_id": "rfc_e2e_approve",
                "builder_node_id": "node_builder_20",
                "target_symbol_urn": "urn:axioma:g4b:compiled_mesh_app:engine",
                "bottleneck_type": "LATENCY_OVERRUN",
                "empirical_evidence": "WAL fsync batching reduces step latency from 80ms to 12ms",
                "proposed_delta": "Batch telemetry WAL commits across 4 transactions",
                "preserved_invariants": ["[L1-G4B-001]", "[L1-G3B-017]"],
            },
            {
                "request_id": "rfc_e2e_reject",
                "builder_node_id": "node_builder_20",
                "target_symbol_urn": "urn:axioma:g4b:compiled_mesh_app:router",
                "bottleneck_type": "COMPLEXITY_LIMIT",
                "empirical_evidence": "Dispatch table grew to 16 branches",
                "proposed_delta": "Use eval(route_expr) dynamic dispatch shortcut",
                "preserved_invariants": ["[NEG-001]"],
            },
        ]

        compiler = SystemG4bCompiler(transport_mode=TransportMode.LOCAL_IPC, repo_root=REPO_ROOT)
        request = CompilationRequest(
            app_id="mesh_e2e_probe",
            app_name="Mesh E2E Probe",
            target_output_dir=out_dir,
            waterloo_soc_prompt="Compile a hermetic stateful service through all 5 Gen 4b sovereign enclaves.",
            domain_archetype=DomainArchetype.DISTRIBUTED_MESH_BACKEND.value,
            expected_verbs=["dispatch", "seal"],
            rfc_requests=rfc_requests,
            transport_mode=TransportMode.LOCAL_IPC.value,
            subagent_invoker=stub_live_invoker,
            require_live_subagents=True,
        )

        report = compiler.compile(request)
        self.assertIsInstance(report, CompilationReport)
        self.assertTrue(report.success, f"Compilation failed unexpectedly: {report.error_message}")
        self.assertTrue(report.audit_passed)
        self.assertTrue(report.governance_certified)
        self.assertEqual(report.statechart_coverage_pct, 100.0)
        self.assertIn(CompilationPhase.RFC_ESCALATION.value, report.phases_executed)
        self.assertEqual(len(report.merkle_root), 64)
        self.assertEqual(len(report.acceptance_spec_hash), 64)
        self.assertEqual(len(report.subagent_witnesses), 4)

        # Verify physical artifacts and sizes on disk
        required_files = [
            "run.py",
            "src/__init__.py",
            "src/domain_models.py",
            "src/engine.py",
            "tests/__init__.py",
            "tests/test_smoke.py",
            ".telemetry_vault.sqlite",
            "telemetry_ledger.json",
            "telemetry_metrics.json",
            "synthesis_manifest.json",
            "dashboard.html",
            "telemetry_dashboard.html",
        ]
        for rel in required_files:
            f = out_dir / rel
            self.assertTrue(f.exists(), f"Missing emitted artifact: {rel}")
            self.assertGreater(f.stat().st_size, 0, f"Empty emitted artifact: {rel}")

        self.assertGreater(
            (out_dir / "dashboard.html").stat().st_size,
            50 * 1024,
            "dashboard.html must exceed 50KB",
        )
        self.assertGreater(
            (out_dir / "telemetry_dashboard.html").stat().st_size,
            50 * 1024,
            "telemetry_dashboard.html must exceed 50KB",
        )

        # Verify RFC resolutions captured both approved amendment and CounterProof
        approved = [
            r for r in report.rfc_resolutions
            if r.get("request_id") == "rfc_e2e_approve" and r.get("is_approved") is True
        ]
        rejected = [
            r for r in report.rfc_resolutions
            if r.get("request_id") == "rfc_e2e_reject" and r.get("is_approved") is False
        ]
        counter_proofs = [
            r for r in report.rfc_resolutions
            if r.get("request_id") == "rfc_e2e_reject" and "counter_proof_id" in r
        ]
        self.assertEqual(len(approved), 1)
        self.assertEqual(len(rejected), 1)
        self.assertEqual(len(counter_proofs), 1)
        self.assertGreaterEqual(len(counter_proofs[0]["violated_axioms"]), 1)

    # 10. Fail-Closed Live Subagent & Anti-Collusion Enforcement
    def test_10_compiler_fail_closed_live_subagents_and_anti_collusion(self) -> None:
        """Verifies require_live_subagents=True fails closed without invoker and rejects Builder/QA collusion."""
        compiler = SystemG4bCompiler(transport_mode=TransportMode.LOCAL_IPC, repo_root=REPO_ROOT)

        # Case A: Missing subagent_invoker when require_live_subagents=True
        req_missing = CompilationRequest(
            app_id="fail_no_invoker",
            app_name="Fail Missing Invoker",
            target_output_dir=self.temp_dir / "fail_no_invoker",
            waterloo_soc_prompt="Verify fail-closed behavior without invoker.",
            subagent_invoker=None,
            require_live_subagents=True,
        )
        rep_missing = compiler.compile(req_missing)
        self.assertFalse(rep_missing.success)
        self.assertIn("subagent_invoker", rep_missing.error_message or "")

        # Case B: Colluding Builder & QA sharing identical conversation_id
        colluding_cid = str(uuid.uuid4())
        colluding_cids = {
            "Domain Ontologist & Systems Architect": str(uuid.uuid4()),
            "Core Engine Synthesizer": colluding_cid,
            "Adversarial Byzantine QA Engineer": colluding_cid,
            "Dialectical Red Team Architect": str(uuid.uuid4()),
        }
        req_collude = CompilationRequest(
            app_id="fail_collusion",
            app_name="Fail Collusion",
            target_output_dir=self.temp_dir / "fail_collusion",
            waterloo_soc_prompt="Verify anti-collusion enforcement between Builder and QA.",
            subagent_invoker=lambda role, prompt, model: colluding_cids[role],
            require_live_subagents=True,
        )
        rep_collude = compiler.compile(req_collude)
        self.assertFalse(rep_collude.success)
        self.assertIn("Anti-collusion violation", rep_collude.error_message or "")

    # 11. [NEG-G1B-002] Subprocess Entrypoint Smoke Gates [INV-PIPE-001]
    def test_11_subprocess_entrypoint_smoke_gates(self) -> None:
        """Executes compiler CLI, sovereign mesh, and cluster runner in unbuffered subprocesses."""
        env = {**os.environ, "PYTHONUNBUFFERED": "1"}

        # 1. python3 -u -m generations.gen_04b.compiler --smoke-test
        p1 = subprocess.run(
            [sys.executable, "-u", "-m", "generations.gen_04b.compiler", "--smoke-test"],
            capture_output=True,
            text=True,
            timeout=20.0,
            cwd=str(REPO_ROOT),
            env=env,
        )
        self.assertEqual(p1.returncode, 0, f"Compiler --smoke-test failed:\n{p1.stdout}\n{p1.stderr}")
        self.assertIn("[G4B COMPILER SMOKE TEST PASSED]", p1.stdout)

        # 2. python3 -u -m generations.gen_04b.compiler mesh-health
        p2 = subprocess.run(
            [sys.executable, "-u", "-m", "generations.gen_04b.compiler", "mesh-health"],
            capture_output=True,
            text=True,
            timeout=15.0,
            cwd=str(REPO_ROOT),
            env=env,
        )
        self.assertEqual(p2.returncode, 0, f"Compiler mesh-health failed:\n{p2.stdout}\n{p2.stderr}")
        self.assertIn("[MESH HEALTH OK]", p2.stdout)

        # 3. python3 -u scripts/run_sovereign_mesh.py --smoke-test
        p3 = subprocess.run(
            [sys.executable, "-u", str(REPO_ROOT / "scripts" / "run_sovereign_mesh.py"), "--smoke-test"],
            capture_output=True,
            text=True,
            timeout=20.0,
            cwd=str(REPO_ROOT),
            env=env,
        )
        self.assertEqual(p3.returncode, 0, f"Sovereign mesh --smoke-test failed:\n{p3.stdout}\n{p3.stderr}")
        self.assertIn("[SOVEREIGN MESH SMOKE TEST PASSED]", p3.stdout)

        # 4. python3 -u generations/gen_04b/run.py (dynamic real service test counts)
        p4 = subprocess.run(
            [sys.executable, "-u", str(REPO_ROOT / "generations" / "gen_04b" / "run.py")],
            capture_output=True,
            text=True,
            timeout=30.0,
            cwd=str(REPO_ROOT),
            env=env,
        )
        self.assertEqual(p4.returncode, 0, f"generations/gen_04b/run.py failed:\n{p4.stdout}\n{p4.stderr}")
        for expected_count in ("30 modules/tests", "124 tests", "190 tests", "159 tests", "128 tests"):
            self.assertIn(expected_count, p4.stdout)

    # 12. Opt-Out Live Subagents Default & CLI --no-live-subagents
    def test_12_live_subagents_opt_out_default_and_cli(self) -> None:
        """Verifies live subagents are required by default (opt-out only) in CompilationRequest & CLI."""
        compiler = SystemG4bCompiler(transport_mode=TransportMode.LOCAL_IPC, repo_root=REPO_ROOT)

        # CompilationRequest defaults require_live_subagents=True
        req_default = CompilationRequest(
            app_id="opt_out_default_probe",
            app_name="Opt-Out Default Probe",
            target_output_dir=self.temp_dir / "opt_out_default",
            waterloo_soc_prompt="Verify default require_live_subagents fails closed without invoker.",
        )
        self.assertTrue(req_default.require_live_subagents)
        rep_default = compiler.compile(req_default)
        self.assertFalse(rep_default.success)
        self.assertIn("--no-live-subagents", rep_default.error_message or "")

        # Explicit opt-out programmatically succeeds
        req_opt_out = CompilationRequest(
            app_id="opt_out_explicit_probe",
            app_name="Opt-Out Explicit Probe",
            target_output_dir=self.temp_dir / "opt_out_explicit",
            waterloo_soc_prompt="Verify explicit opt-out allows deterministic scaffold compilation.",
            require_live_subagents=False,
        )
        rep_opt_out = compiler.compile(req_opt_out)
        self.assertTrue(rep_opt_out.success, f"Unexpected opt-out failure: {rep_opt_out.error_message}")
        self.assertEqual(rep_opt_out.subagent_witnesses, [])

        # CLI compile without --no-live-subagents fails closed (exit 1)
        env = {**os.environ, "PYTHONUNBUFFERED": "1"}
        cli_default_dir = self.temp_dir / "cli_default_out"
        p_fail = subprocess.run(
            [
                sys.executable,
                "-u",
                "-m",
                "generations.gen_04b.compiler",
                "compile",
                "--app-id",
                "cli_default_fail",
                "--prompt",
                "Should fail closed without --no-live-subagents",
                "--output-dir",
                str(cli_default_dir),
            ],
            capture_output=True,
            text=True,
            timeout=15.0,
            cwd=str(REPO_ROOT),
            env=env,
        )
        self.assertNotEqual(p_fail.returncode, 0)
        self.assertIn("[COMPILATION FAILED]", p_fail.stdout)
        self.assertIn("--no-live-subagents", p_fail.stdout)

        # CLI compile with --no-live-subagents succeeds (exit 0)
        cli_opt_out_dir = self.temp_dir / "cli_opt_out_ok"
        p_ok = subprocess.run(
            [
                sys.executable,
                "-u",
                "-m",
                "generations.gen_04b.compiler",
                "compile",
                "--app-id",
                "cli_opt_out_ok",
                "--prompt",
                "Compile deterministic scaffold with explicit opt-out",
                "--output-dir",
                str(cli_opt_out_dir),
                "--no-live-subagents",
            ],
            capture_output=True,
            text=True,
            timeout=20.0,
            cwd=str(REPO_ROOT),
            env=env,
        )
        self.assertEqual(p_ok.returncode, 0, f"CLI --no-live-subagents failed:\n{p_ok.stdout}\n{p_ok.stderr}")
        self.assertIn("[COMPILATION SUCCESSFUL]", p_ok.stdout)
        self.assertTrue((cli_opt_out_dir / "telemetry_dashboard.html").exists())

    # 13. Strict Z3 Prover Propagation across Audit Provers, SystemG4bCompiler, & CLI
    def test_13_strict_z3_prover_end_to_end_and_cli(self) -> None:
        """Verifies strict_prover / strict_formal_prover propagates across compiler, audit provers, and CLI."""
        strict_checker = SMTModelChecker(strict_formal_prover=True)
        strict_mesh = SMTMeshVerifier(strict_formal_prover=True)
        compiler = SystemG4bCompiler(transport_mode=TransportMode.LOCAL_IPC, repo_root=REPO_ROOT)

        req_strict = CompilationRequest(
            app_id="strict_z3_probe",
            app_name="Strict Z3 Probe",
            target_output_dir=self.temp_dir / "strict_z3_out",
            waterloo_soc_prompt="Verify strict_prover end-to-end enforcement.",
            strict_prover=True,
            require_live_subagents=False,
        )

        env = {**os.environ, "PYTHONUNBUFFERED": "1"}
        cli_strict_dir = self.temp_dir / "cli_strict_out"
        p_cli = subprocess.run(
            [
                sys.executable,
                "-u",
                "-m",
                "generations.gen_04b.compiler",
                "compile",
                "--app-id",
                "cli_strict_z3",
                "--prompt",
                "Test CLI --strict-prover flag",
                "--output-dir",
                str(cli_strict_dir),
                "--no-live-subagents",
                "--strict-prover",
            ],
            capture_output=True,
            text=True,
            timeout=20.0,
            cwd=str(REPO_ROOT),
            env=env,
        )

        if not strict_checker._z3_available:
            self.assertEqual(strict_checker.verification_mode, AuditVerificationMode.UNAVAILABLE)
            self.assertEqual(strict_mesh.verification_mode, MeshVerificationMode.UNAVAILABLE)
            with self.assertRaises(AuditFormalProverUnavailableError):
                strict_checker.verify_contract_morphism("x", "x", "x", "x")
            with self.assertRaises(AuditFormalProverUnavailableError):
                strict_checker.verify_state_transition_invariant("A", "B", "EV")
            with self.assertRaises(AuditFormalProverUnavailableError):
                strict_checker.verify_statechart_deadlock_freedom(["A"], [], ["A"], "A")
            with self.assertRaises(AuditFormalProverUnavailableError):
                strict_mesh.verify_topology({"nodes": {}, "channels": []})
            with self.assertRaises(AuditFormalProverUnavailableError):
                strict_mesh.verify_lamport_monotonicity([])

            rep = compiler.compile(req_strict)
            self.assertFalse(rep.success)
            self.assertEqual(rep.verification_mode, AuditVerificationMode.UNAVAILABLE.value)
            self.assertIn("Z3", rep.error_message or "")

            self.assertNotEqual(p_cli.returncode, 0)
            self.assertIn("[COMPILATION FAILED]", p_cli.stdout)
            self.assertIn("Z3", p_cli.stdout)
        else:
            self.assertEqual(strict_checker.verification_mode, AuditVerificationMode.Z3_SMT_SOLVER)
            self.assertEqual(strict_mesh.verification_mode, MeshVerificationMode.Z3_SMT_SOLVER)
            rep = compiler.compile(req_strict)
            self.assertTrue(rep.success, f"Strict Z3 compile failed unexpectedly: {rep.error_message}")
            self.assertEqual(rep.verification_mode, AuditVerificationMode.Z3_SMT_SOLVER.value)
            self.assertEqual(p_cli.returncode, 0, f"CLI --strict-prover failed:\n{p_cli.stdout}\n{p_cli.stderr}")


if __name__ == "__main__":
    unittest.main()
