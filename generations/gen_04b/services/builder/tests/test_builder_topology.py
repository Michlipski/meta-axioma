"""Adversarial & Network Topology Test Suite for Builder Mesh & Dedicated Channels (`[L1-G3B-012]`).

Validates:
1. Sovereign LAN IP binding on 192.168.40.20:8442.
2. Trapping and rejection of loopback bindings (127.0.0.1, localhost, ::1, 0.0.0.0) raising DomainInvariantViolation.
3. Verification of all 8 dedicated inter-service channels:
   - channel_research_deliverables (Research -> Builder)
   - channel_rfc_petitions (Builder -> Research)
   - channel_audit_interception (Builder -> Audit)
   - channel_telemetry_stream (Builder -> Telemetry)
   - channel_governance_veto (Governance -> Builder)
   - channel_merkle_attestation (Builder -> Telemetry)
   - channel_quine_crucible_isolation (Builder -> Crucible Sandbox)
   - channel_operator_hud (Builder -> Local Process HUD)
4. Enforcement of fail-closed partition policy: network disconnection blocks all channel transmissions.
5. Ingestion of certified ResearchDeliverableBundle and rejection of uncertified bundles.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
import sys
import unittest

BUILDER_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = BUILDER_ROOT.parent.parent.parent
for p in [str(BUILDER_ROOT), str(REPO_ROOT)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from generations.gen_04b.protocols.deliverable_bundle import (
    DeliverableProtocolViolation,
    ResearchDeliverableBundle,
)
from src.builder_kernel import SovereignBuilderKernel
from src.builder_topology import (
    BuilderTopologyManager,
    InterServiceChannel,
    NetworkPartitionError,
    PartitionPolicy,
)
from src.domain_models import DomainInvariantViolation, TaskExecutionStatus


class TestBuilderTopology(unittest.TestCase):
    """Rigorous verification of non-loopback network topology and 8 dedicated inter-service channels."""

    def setUp(self) -> None:
        self.kernel = SovereignBuilderKernel(node_ip="192.168.40.20", port=8442)
        self.topology = self.kernel.topology
        self.sample_sha256 = hashlib.sha256(b"bundle_ref_arch_sample").hexdigest()

    def test_sovereign_ip_binding_and_rejection_of_loopback(self) -> None:
        # Valid binding
        self.assertEqual(self.kernel.node_ip, "192.168.40.20")
        self.assertEqual(self.kernel.port, 8442)
        self.assertEqual(self.topology.endpoint, "192.168.40.20:8442")

        # Prohibited loopback addresses
        loopback_candidates = [
            "127.0.0.1",
            "localhost",
            "::1",
            "0.0.0.0",
            "127.0.1.1",
        ]
        for bad_ip in loopback_candidates:
            with self.subTest(bad_ip=bad_ip):
                with self.assertRaises(DomainInvariantViolation):
                    SovereignBuilderKernel(node_ip=bad_ip, port=8442)
                with self.assertRaises(DomainInvariantViolation):
                    BuilderTopologyManager(node_ip=bad_ip, port=8442)

    def test_eight_dedicated_inter_service_channels(self) -> None:
        channels = self.topology.list_channels()
        self.assertEqual(len(channels), 8, "Must have exactly 8 dedicated inter-service channels.")

        expected_channels = {
            "channel_research_deliverables",
            "channel_rfc_petitions",
            "channel_audit_interception",
            "channel_telemetry_stream",
            "channel_governance_veto",
            "channel_merkle_attestation",
            "channel_quine_crucible_isolation",
            "channel_operator_hud",
        }
        actual_channel_names = {ch.channel_name for ch in channels}
        self.assertEqual(actual_channel_names, expected_channels)

        # Verify all channel endpoints are non-loopback IPs
        for ch in channels:
            for ep in (ch.source_endpoint, ch.target_endpoint):
                ip = ep.split(":")[0].strip()
                self.assertFalse(
                    ip.startswith("127.") or ip in ("localhost", "::1", "0.0.0.0"),
                    f"Prohibited loopback in endpoint: {ep}",
                )
                self.assertTrue(ip.startswith("192.168.40."), f"Expected 192.168.40.x subnet, got {ip}")

    def test_fail_closed_partition_policy(self) -> None:
        # Under normal connectivity, transmission succeeds
        success = self.topology.transmit(
            channel_name="channel_rfc_petitions",
            payload_bytes=b'{"action": "PETITION_SUBMISSION"}',
        )
        self.assertTrue(success)
        ch = self.topology.get_channel("channel_rfc_petitions")
        self.assertEqual(ch.message_count, 1)
        self.assertGreater(ch.bytes_transmitted, 0)

        # Simulate partition event
        self.topology.simulate_partition(partitioned=True)
        self.assertTrue(self.topology.is_partitioned)

        # Under FAIL_CLOSED policy, transmissions MUST raise NetworkPartitionError
        with self.assertRaises(NetworkPartitionError):
            self.topology.transmit(
                channel_name="channel_telemetry_stream",
                payload_bytes=b'{"metric": "LANDAUER_BIT_ERASURE"}',
            )

        # Reconnecting allows transmission to resume
        self.topology.simulate_partition(partitioned=False)
        self.assertFalse(self.topology.is_partitioned)
        resumed = self.topology.transmit(
            channel_name="channel_telemetry_stream",
            payload_bytes=b'{"metric": "RESUMED"}',
        )
        self.assertTrue(resumed)

    def test_certified_research_bundle_handshake(self) -> None:
        # Certified bundle
        bundle = ResearchDeliverableBundle(
            bundle_id="bundle_certified_01",
            target_soc_id="soc_g4b_builder",
            hypothesis_id="hyp_01",
            constraint_analysis_id="const_01",
            failure_mode_id="fail_01",
            tradeoff_matrix_id="trade_01",
            reference_architecture_hash=self.sample_sha256,
            merkle_root=self.sample_sha256,
            is_certified=True,
        )

        exec_bundle = self.kernel.handshake_and_ingest(bundle)
        self.assertEqual(exec_bundle.target_soc_id, "soc_g4b_builder")
        self.assertEqual(exec_bundle.status, TaskExecutionStatus.ACTIVE)
        self.assertEqual(self.kernel.statechart.active_main_state, "bundle_validated")

    def test_uncertified_research_bundle_rejection(self) -> None:
        # Uncertified bundle MUST be rejected
        uncertified_bundle = ResearchDeliverableBundle(
            bundle_id="bundle_uncert_02",
            target_soc_id="soc_g4b_builder",
            hypothesis_id="hyp_02",
            constraint_analysis_id="const_02",
            failure_mode_id="fail_02",
            tradeoff_matrix_id="trade_02",
            reference_architecture_hash=self.sample_sha256,
            merkle_root=self.sample_sha256,
            is_certified=False,  # Uncertified!
        )

        with self.assertRaises(DeliverableProtocolViolation):
            self.kernel.handshake_and_ingest(uncertified_bundle)

        self.assertEqual(self.kernel.statechart.active_main_state, "handshake_rejected_enclave")


if __name__ == "__main__":
    unittest.main()
