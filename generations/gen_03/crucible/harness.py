"""The Evolutionary Crucible Adversarial Test Harness.

Executes standardized stress trials against any candidate implementing
DistributedConsensusProtocol:
1. Asymmetric Partition Trial (Transitivity failure)
2. Chaotic Flapping Edge with Packet Drops Trial
3. High-Frequency Conflict Storm Trial
"""

from __future__ import annotations

import random
import time
from typing import Any, Dict, List, Set, Tuple

from .metrics import CandidateFitnessScorecard, TrialResult, evaluate_candidate_fitness
from .protocol import DistributedConsensusProtocol


class AdversarialCrucibleHarness:
    """The independent stress test harness evaluating candidate fitness."""

    def __init__(self, random_seed: int = 42):
        self.rng = random.Random(random_seed)

    def run_all_trials(self, protocol: DistributedConsensusProtocol) -> CandidateFitnessScorecard:
        """Executes full 3-trial adversarial gauntlet against the protocol candidate."""
        t1 = self.trial_asymmetric_partition(protocol)
        t2 = self.trial_chaotic_flapping(protocol)
        t3 = self.trial_conflict_storm(protocol)

        return evaluate_candidate_fitness(protocol.name, [t1, t2, t3])

    def trial_asymmetric_partition(self, protocol: DistributedConsensusProtocol) -> TrialResult:
        """Trial 1: Asymmetric Network Partition (A <-> B, B <-> C, A <//> C)."""
        protocol.reset()
        nodes = ["node-a", "node-b", "node-c"]
        protocol.register_nodes(nodes)

        # Asymmetric partition: a <-> c is completely severed
        active_partitions: Set[Tuple[str, str]] = {("node-a", "node-c"), ("node-c", "node-a")}

        start_t = time.perf_counter()
        initial_bits = protocol.get_erased_bits()
        errors: List[str] = []

        # Concurrent mutations on partitioned ends
        ok_a = protocol.propose("node-a", "shared_key", "val_from_node_a")
        ok_c = protocol.propose("node-c", "shared_key", "val_from_node_c")
        protocol.propose("node-a", "private_a", "data_a")
        protocol.propose("node-c", "private_c", "data_c")

        # Route messages across intermediary B over 6 rounds
        routed_total = 0
        for _ in range(6):
            routed = protocol.route_messages(active_partitions, drop_rate=0.0)
            routed_total += routed

        elapsed_ms = (time.perf_counter() - start_t) * 1000.0

        # Evaluate consistency across all nodes
        state_a = protocol.get_node_state("node-a")
        state_b = protocol.get_node_state("node-b")
        state_c = protocol.get_node_state("node-c")

        consistency_rate = self._compute_state_consistency([state_a, state_b, state_c])
        passed = consistency_rate >= 0.70  # At least 70% state consistency across asymmetric split

        if not passed:
            errors.append(f"State divergence under asymmetric split. Consistency: {consistency_rate:.2f}")

        delta_bits = max(0.0, protocol.get_erased_bits() - initial_bits)
        joules = delta_bits * 2.853e-21

        return TrialResult(
            trial_name="Asymmetric Partition",
            passed=passed,
            consistency_rate=round(consistency_rate, 4),
            messages_routed=routed_total,
            duration_ms=round(elapsed_ms, 3),
            erased_bits=round(delta_bits, 2),
            joules_dissipated=joules,
            error_details=errors,
        )

    def trial_chaotic_flapping(self, protocol: DistributedConsensusProtocol) -> TrialResult:
        """Trial 2: Rapid Edge Flapping with 20% Packet Drops."""
        protocol.reset()
        nodes = ["node-a", "node-b", "node-c"]
        protocol.register_nodes(nodes)

        start_t = time.perf_counter()
        initial_bits = protocol.get_erased_bits()
        errors: List[str] = []

        routed_total = 0
        # Stream 15 sequential writes across changing nodes with flapping edge a <-> b
        for i in range(15):
            nid = nodes[i % 3]
            protocol.propose(nid, f"seq_key_{i}", f"val_{i}_{nid}")

            # Edge a <-> b flaps every 2 iterations
            partitions: Set[Tuple[str, str]] = set()
            if (i % 2) == 1:
                partitions.add(("node-a", "node-b"))
                partitions.add(("node-b", "node-a"))

            routed = protocol.route_messages(partitions, drop_rate=0.20)
            routed_total += routed

        # Quiescence phase: heal all partitions and flush remaining queues
        for _ in range(8):
            routed = protocol.route_messages(set(), drop_rate=0.0)
            routed_total += routed

        elapsed_ms = (time.perf_counter() - start_t) * 1000.0

        states = [protocol.get_node_state(nid) for nid in nodes]
        consistency_rate = self._compute_state_consistency(states)
        passed = consistency_rate >= 0.85

        if not passed:
            errors.append(f"Flapping edge caused convergence failure. Consistency: {consistency_rate:.2f}")

        delta_bits = max(0.0, protocol.get_erased_bits() - initial_bits)
        joules = delta_bits * 2.853e-21

        return TrialResult(
            trial_name="Chaotic Flapping & Drops",
            passed=passed,
            consistency_rate=round(consistency_rate, 4),
            messages_routed=routed_total,
            duration_ms=round(elapsed_ms, 3),
            erased_bits=round(delta_bits, 2),
            joules_dissipated=joules,
            error_details=errors,
        )

    def trial_conflict_storm(self, protocol: DistributedConsensusProtocol) -> TrialResult:
        """Trial 3: High-Frequency Conflict Storm (Concurrent writes to identical key)."""
        protocol.reset()
        nodes = ["node-a", "node-b", "node-c"]
        protocol.register_nodes(nodes)

        start_t = time.perf_counter()
        initial_bits = protocol.get_erased_bits()
        errors: List[str] = []

        # 30 concurrent conflicting proposals to the exact same key across all nodes
        for i in range(30):
            nid = nodes[i % 3]
            protocol.propose(nid, "hotspot_key", f"update_{i}_from_{nid}")

        # Flush message queues until quiescence
        routed_total = 0
        for _ in range(10):
            routed = protocol.route_messages(set(), drop_rate=0.0)
            routed_total += routed

        elapsed_ms = (time.perf_counter() - start_t) * 1000.0

        states = [protocol.get_node_state(nid) for nid in nodes]
        consistency_rate = self._compute_state_consistency(states)
        passed = consistency_rate == 1.0  # Conflict storm must achieve 100% convergence at quiescence

        if not passed:
            errors.append(f"Quiescent convergence incomplete after conflict storm: {consistency_rate:.2f}")

        delta_bits = max(0.0, protocol.get_erased_bits() - initial_bits)
        joules = delta_bits * 2.853e-21

        return TrialResult(
            trial_name="Conflict Storm",
            passed=passed,
            consistency_rate=round(consistency_rate, 4),
            messages_routed=routed_total,
            duration_ms=round(elapsed_ms, 3),
            erased_bits=round(delta_bits, 2),
            joules_dissipated=joules,
            error_details=errors,
        )

    @staticmethod
    def _compute_state_consistency(states: List[Dict[str, Any]]) -> float:
        """Calculates pairwise Jaccard/Value agreement across all nodes."""
        if not states or len(states) < 2:
            return 1.0

        all_keys = set().union(*(s.keys() for s in states))
        if not all_keys:
            return 1.0

        total_checks = 0
        matching_checks = 0

        for k in all_keys:
            vals = [s.get(k) for s in states]
            # Compare all pairs for this key
            for i in range(len(vals)):
                for j in range(i + 1, len(vals)):
                    total_checks += 1
                    if vals[i] == vals[j] and vals[i] is not None:
                        matching_checks += 1

        return matching_checks / max(1, total_checks)
