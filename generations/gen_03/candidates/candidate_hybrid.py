"""Candidate Delta: Transitive Sheaf-Quorum Hybrid Protocol.

Evolutionary mutation for Generation 3 Epoch 3:
Cross-breeds the best traits of Candidates Alpha (Sheaf resilience),
Beta (Transitive delta propagation), and Gamma (Quorum commit safety).
"""

from __future__ import annotations

import collections
import random
import time
from typing import Any, Dict, List, Optional, Set, Tuple

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from crucible.protocol import DistributedConsensusProtocol


class CandidateHybridSheafQuorumProtocol(DistributedConsensusProtocol):
    """Candidate Delta: Evolutionary Hybrid combining Sheaves, Multi-Hop Relaying, and Quorum Leases."""

    def __init__(self):
        self.node_ids: List[str] = []
        # Committed state machine: node_id -> {key: (value, version, origin)}
        self.states: Dict[str, Dict[str, Tuple[Any, int, str]]] = {}
        # In-flight message queues: dst_node_id -> list of messages
        self.inbox: Dict[str, List[Dict[str, Any]]] = collections.defaultdict(list)
        # Quorum tracking: (key, version) -> set of nodes that have reconciled
        self.quorum_acks: Dict[Tuple[str, int], Set[str]] = collections.defaultdict(set)
        # Transitive hop cache to prevent infinite loops: set of (origin, key, version, hop_count)
        self.seen_messages: Set[Tuple[str, str, int, int]] = set()
        self.erased_bits: Dict[str, float] = collections.defaultdict(float)
        self.rng = random.Random(999)

    @property
    def name(self) -> str:
        return "Candidate Delta (Transitive Sheaf-Quorum Hybrid)"

    def register_nodes(self, node_ids: List[str]) -> None:
        self.node_ids = list(node_ids)
        for nid in self.node_ids:
            self.states[nid] = {}
            self.inbox[nid] = []
            self.erased_bits[nid] = 0.0

    def propose(self, node_id: str, key: str, value: Any) -> bool:
        if node_id not in self.states:
            return False

        cur = self.states[node_id].get(key)
        new_ver = (cur[1] + 1) if cur else 1

        # Local optimistic update
        old_val = cur[0] if cur else None
        if old_val is not None and old_val != value:
            self.erased_bits[node_id] += len(str(old_val).encode("utf-8")) * 8.0

        self.states[node_id][key] = (value, new_ver, node_id)
        self.quorum_acks[(key, new_ver)].add(node_id)

        # Broadcast restriction delta with transitive relaying enabled
        delta = {
            "type": "TRANSITIVE_SHEAF_DELTA",
            "origin": node_id,
            "src": node_id,
            "key": key,
            "value": value,
            "version": new_ver,
            "hops": 0,
        }

        for peer in self.node_ids:
            if peer != node_id:
                self.inbox[peer].append(dict(delta, dst=peer))

        return True

    def route_messages(
        self,
        active_partitions: Set[Tuple[str, str]],
        drop_rate: float = 0.0,
    ) -> int:
        delivered_count = 0
        all_pending: List[Dict[str, Any]] = []

        for dst in self.node_ids:
            all_pending.extend(self.inbox[dst])
            self.inbox[dst] = []

        majority_quorum = (len(self.node_ids) // 2) + 1

        for msg in all_pending:
            src = msg["src"]
            dst = msg["dst"]

            # Check network partition
            if (src, dst) in active_partitions or (dst, src) in active_partitions:
                self.inbox[dst].append(msg)
                continue

            # Check simulated packet drops
            if drop_rate > 0.0 and self.rng.random() < drop_rate:
                # With adaptive retry, re-queue dropped messages with 50% probability
                if self.rng.random() < 0.5:
                    self.inbox[dst].append(msg)
                continue

            # Process delivery
            delivered_count += 1
            origin = msg["origin"]
            key = msg["key"]
            val = msg["value"]
            ver = msg["version"]
            hops = msg.get("hops", 0)

            msg_id = (origin, key, ver, hops)
            if msg_id in self.seen_messages:
                continue
            self.seen_messages.add(msg_id)

            cur = self.states[dst].get(key)
            accept = False
            if cur is None:
                accept = True
            else:
                cur_val, cur_ver, cur_origin = cur
                if ver > cur_ver:
                    accept = True
                elif ver == cur_ver and (origin, str(val)) > (cur_origin, str(cur_val)):
                    accept = True

            if accept:
                if cur is not None and cur[0] != val:
                    self.erased_bits[dst] += len(str(cur[0]).encode("utf-8")) * 8.0
                self.states[dst][key] = (val, ver, origin)

            self.quorum_acks[(key, ver)].add(dst)

            # Transitive Relaying: If hops < 2, relay delta to neighbors dst is connected to
            if hops < 2:
                for neighbor in self.node_ids:
                    if neighbor not in (dst, src, origin):
                        relay_msg = {
                            "type": "TRANSITIVE_SHEAF_DELTA",
                            "origin": origin,
                            "src": dst,
                            "dst": neighbor,
                            "key": key,
                            "value": val,
                            "version": ver,
                            "hops": hops + 1,
                        }
                        self.inbox[neighbor].append(relay_msg)

        return delivered_count

    def get_node_state(self, node_id: str) -> Dict[str, Any]:
        return {k: v[0] for k, v in self.states.get(node_id, {}).items()}

    def get_erased_bits(self, node_id: Optional[str] = None) -> float:
        if node_id:
            return self.erased_bits.get(node_id, 0.0)
        return sum(self.erased_bits.values())

    def reset(self) -> None:
        self.node_ids = []
        self.states.clear()
        self.inbox.clear()
        self.quorum_acks.clear()
        self.seen_messages.clear()
        self.erased_bits.clear()
