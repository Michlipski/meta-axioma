"""Comprehensive Unit & Integration Test Suite for Axioma Fabric.

Verifies:
1. Causal vector clocks & lattice join morphisms.
2. Zero-ambient HMAC capability token security.
3. Thermodynamic Landauer ring buffer dissipation & backpressure.
4. Distributed Sheaf-CRDT replication & 3-node cluster coordination.
5. Split-brain resilience under netsplits & automatic pairwise cocycle healing.
6. Chaos crucible fault injection tournament.
7. AsyncIO Gateway REST & status API endpoints.
"""

from __future__ import annotations
import asyncio
import json
import time
import unittest
import urllib.request
import urllib.error

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from axioma_fabric.chaos import FabricChaosCrucible
from axioma_fabric.cocycle_auditor import FabricCocycleAuditor
from axioma_fabric.gateway import FabricGateway
from axioma_fabric.models import (
    CapabilityToken,
    CausalEvent,
    PartitionState,
    VectorClock,
)
from axioma_fabric.sheaf_broker import (
    FabricBrokerNode,
    FabricPartitionError,
    FabricSecurityError,
)
from axioma_fabric.thermodynamics import (
    BOLTZMANN_CONSTANT,
    DEFAULT_TEMPERATURE_KELVIN,
    LN_2,
    LandauerRingBuffer,
    ThermodynamicBackpressureError,
)


class TestVectorClock(unittest.TestCase):
    def test_vector_clock_ordering_and_merge(self):
        c1 = VectorClock({"A": 1, "B": 0})
        c2 = VectorClock({"A": 1, "B": 1})
        self.assertTrue(c1.is_less_than_or_equal(c2))
        self.assertFalse(c2.is_less_than_or_equal(c1))
        self.assertFalse(c1.concurrent_with(c2))

        c3 = VectorClock({"A": 2, "B": 0})
        self.assertTrue(c2.concurrent_with(c3))

        c_merged = c2.merge(c3)
        self.assertEqual(c_merged.clocks, {"A": 2, "B": 1})
        self.assertTrue(c2.is_less_than_or_equal(c_merged))
        self.assertTrue(c3.is_less_than_or_equal(c_merged))


class TestCapabilityTokens(unittest.TestCase):
    def setUp(self):
        self.secret = "super_secret_test_key_123"

    def test_signed_token_verification(self):
        token = CapabilityToken.create_signed(
            token_id="tok_1",
            subject="agent_alpha",
            allowed_topics=["telemetry.*", "events"],
            permissions=["produce", "consume"],
            ttl_seconds=60.0,
            secret_key=self.secret,
        )
        self.assertTrue(token.verify(self.secret))
        self.assertFalse(token.verify("wrong_secret"))
        self.assertTrue(token.allows("events", "produce"))
        self.assertFalse(token.allows("events", "admin"))

    def test_expired_token(self):
        token = CapabilityToken.create_signed(
            token_id="tok_exp",
            subject="agent_exp",
            allowed_topics=["*"],
            permissions=["*"],
            ttl_seconds=-10.0,  # Expired
            secret_key=self.secret,
        )
        self.assertFalse(token.verify(self.secret))


class TestLandauerThermodynamics(unittest.TestCase):
    def test_bit_erasure_accounting(self):
        buf = LandauerRingBuffer(capacity_entries=2, max_memory_bytes=10000, token_lease_budget=100.0)
        clock = VectorClock({"A": 1})
        
        ev1 = CausalEvent.create("e1", "t", {"data": "hello_1"}, clock, "A")
        ev2 = CausalEvent.create("e2", "t", {"data": "hello_2"}, clock, "A")
        ev3 = CausalEvent.create("e3", "t", {"data": "hello_3"}, clock, "A")

        buf.append(ev1)
        buf.append(ev2)
        self.assertEqual(buf.current_entries, 2)
        self.assertEqual(buf.cumulative_erasure_joules, 0.0)

        # Appending 3rd event forces eviction of ev1
        evicted = buf.append(ev3)
        self.assertEqual(evicted, ev1)
        self.assertEqual(buf.current_entries, 2)
        self.assertGreater(buf.cumulative_erasure_joules, 0.0)

        expected_joules = ev1.byte_size * 8 * BOLTZMANN_CONSTANT * DEFAULT_TEMPERATURE_KELVIN * LN_2
        self.assertAlmostEqual(buf.cumulative_erasure_joules, expected_joules, places=28)

    def test_thermodynamic_backpressure_exhaustion(self):
        # Micro budget of 0.005 tokens; evicting ev1 will cost 0.01 tokens
        buf = LandauerRingBuffer(capacity_entries=1, max_memory_bytes=10000, token_lease_budget=0.005)
        clock = VectorClock({"A": 1})

        ev1 = CausalEvent.create("e1", "t", {"data": "A" * 100}, clock, "A")
        ev2 = CausalEvent.create("e2", "t", {"data": "B" * 100}, clock, "A")
        ev3 = CausalEvent.create("e3", "t", {"data": "C" * 100}, clock, "A")

        buf.append(ev1)
        buf.append(ev2)  # consumes token budget
        with self.assertRaises(ThermodynamicBackpressureError):
            buf.append(ev3)


class TestDistributedSheafCluster(unittest.TestCase):
    def setUp(self):
        self.secret = "test_cluster_secret_key"
        self.node_a = FabricBrokerNode("node_alpha", "U_alpha", self.secret)
        self.node_b = FabricBrokerNode("node_beta", "U_beta", self.secret)
        self.node_c = FabricBrokerNode("node_gamma", "U_gamma", self.secret)

        self.node_a.register_peer(self.node_b)
        self.node_a.register_peer(self.node_c)
        self.node_b.register_peer(self.node_a)
        self.node_b.register_peer(self.node_c)
        self.node_c.register_peer(self.node_a)
        self.node_c.register_peer(self.node_b)

        self.token = CapabilityToken.create_signed(
            token_id="tok_test",
            subject="test_user",
            allowed_topics=["*"],
            permissions=["*"],
            ttl_seconds=3600.0,
            secret_key=self.secret,
        )

    def test_replicated_write(self):
        topic = "orders"
        ev = self.node_a.publish(topic, {"item": "sensor_01", "qty": 5}, self.token)
        
        self.assertIn(ev.event_id, self.node_a.get_section(topic))
        self.assertIn(ev.event_id, self.node_b.get_section(topic))
        self.assertIn(ev.event_id, self.node_c.get_section(topic))

    def test_split_brain_resilience_and_cocycle_healing(self):
        topic = "telemetry"

        # 1. Sever link between node_a and [node_b, node_c]
        self.node_a.sever_link_to("node_beta")
        self.node_a.sever_link_to("node_gamma")
        self.node_b.sever_link_to("node_alpha")
        self.node_c.sever_link_to("node_alpha")

        self.assertEqual(self.node_a.partition_state, PartitionState.PARTITIONED)

        # 2. Publish to partitioned sides concurrently
        ev_a = self.node_a.publish(topic, {"msg": "from_isolated_alpha"}, self.token)
        ev_b = self.node_b.publish(topic, {"msg": "from_connected_beta"}, self.token)

        # 3. Verify isolation during netsplit
        sec_a = self.node_a.get_section(topic)
        sec_b = self.node_b.get_section(topic)
        sec_c = self.node_c.get_section(topic)

        self.assertIn(ev_a.event_id, sec_a)
        self.assertNotIn(ev_a.event_id, sec_b)
        self.assertNotIn(ev_a.event_id, sec_c)

        self.assertIn(ev_b.event_id, sec_b)
        self.assertIn(ev_b.event_id, sec_c)
        self.assertNotIn(ev_b.event_id, sec_a)

        # 4. Restore links
        self.node_a.restore_link_to("node_beta")
        self.node_a.restore_link_to("node_gamma")
        self.node_b.restore_link_to("node_alpha")
        self.node_c.restore_link_to("node_alpha")

        self.assertEqual(self.node_a.partition_state, PartitionState.HEALTHY)

        # 5. Audit & Reconcile
        auditor = FabricCocycleAuditor()
        witnesses = auditor.audit_cluster([self.node_a, self.node_b, self.node_c], topic, auto_reconcile=True)

        self.assertEqual(len(witnesses), 3)
        self.assertTrue(all(w.reconciliation_applied or w.divergence_count == 0 for w in witnesses))

        # 6. Verify 100% convergence across all nodes
        final_a = set(self.node_a.get_section(topic).keys())
        final_b = set(self.node_b.get_section(topic).keys())
        final_c = set(self.node_c.get_section(topic).keys())

        self.assertEqual(final_a, final_b)
        self.assertEqual(final_b, final_c)
        self.assertIn(ev_a.event_id, final_a)
        self.assertIn(ev_b.event_id, final_a)

    def test_chaos_crucible_tournament(self):
        crucible = FabricChaosCrucible([self.node_a, self.node_b, self.node_c])
        report = crucible.run_partition_tournament("chaos_test_topic", self.token, messages_per_partition=10)

        self.assertTrue(report["partition_successful"])
        self.assertTrue(report["all_nodes_converged"])
        self.assertEqual(report["total_cluster_events"], 20)


class TestFabricGateway(unittest.TestCase):
    def setUp(self):
        self.secret = "gateway_secret_999"
        self.node_a = FabricBrokerNode("node_alpha", "U_alpha", self.secret)
        self.node_b = FabricBrokerNode("node_beta", "U_beta", self.secret)
        self.node_a.register_peer(self.node_b)
        self.node_b.register_peer(self.node_a)

        self.gateway = FabricGateway([self.node_a, self.node_b], self.secret, host="127.0.0.1", port=8443)

    def test_http_api_flow(self):
        async def run_test():
            # 1. Request capability token
            token_payload = json.dumps({"subject": "test_client", "topics": ["*"], "permissions": ["*"]})
            status, _, body = await self.gateway._route_request(
                "POST", "/api/v1/auth/token", {}, {"content-type": "application/json"}, token_payload
            )
            self.assertEqual(status, 201)
            token_data = json.loads(body)
            self.assertIn("signature", token_data)

            # 2. Publish message with token
            pub_payload = json.dumps({"cpu": 45.2})
            status, _, body = await self.gateway._route_request(
                "POST",
                "/api/v1/topics/metrics/publish",
                {"node": ["node_alpha"]},
                {"content-type": "application/json", "x-capability-token": json.dumps(token_data)},
                pub_payload,
            )
            self.assertEqual(status, 200)
            pub_data = json.loads(body)
            self.assertEqual(pub_data["status"], "published")

            # 3. Read stream from node_beta (peer replication)
            status, _, body = await self.gateway._route_request(
                "GET",
                "/api/v1/topics/metrics/stream",
                {"node": ["node_beta"]},
                {},
                "",
            )
            self.assertEqual(status, 200)
            stream_data = json.loads(body)
            self.assertEqual(len(stream_data["events"]), 1)
            self.assertEqual(stream_data["events"][0]["payload"], {"cpu": 45.2})

            # 4. Check cluster status
            status, _, body = await self.gateway._route_request("GET", "/api/v1/cluster/status", {}, {}, "")
            self.assertEqual(status, 200)
            status_data = json.loads(body)
            self.assertIn("node_alpha", status_data["nodes"])
            self.assertIn("node_beta", status_data["nodes"])

            # 5. Check chaos netsplit endpoint
            status, _, body = await self.gateway._route_request(
                "POST",
                "/api/v1/cluster/chaos",
                {},
                {},
                json.dumps({"action": "partition", "group_a": ["node_alpha"], "group_b": ["node_beta"]}),
            )
            self.assertEqual(status, 200)
            self.assertEqual(self.node_a.partition_state, PartitionState.PARTITIONED)

            # 6. Check chaos heal endpoint
            status, _, body = await self.gateway._route_request(
                "POST",
                "/api/v1/cluster/chaos",
                {},
                {},
                json.dumps({"action": "heal"}),
            )
            self.assertEqual(status, 200)
            self.assertEqual(self.node_a.partition_state, PartitionState.HEALTHY)

        asyncio.run(run_test())


if __name__ == "__main__":
    unittest.main()
