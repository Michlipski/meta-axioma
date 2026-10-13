"""Candidate Alpha: Topological Cellular Sheaf Consensus.

Implements DistributedConsensusProtocol using topological open cover
restriction maps and cohomology gluing reconciliation (Robinson 2014, 2020).
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


class CandidateSheafProtocol(DistributedConsensusProtocol):
    """Candidate Alpha: Cellular Sheaf Consensus Engine."""

    def __init__(self):
        self.node_ids: List[str] = []
        # Local section state per node: node_id -> {key: (value, version, timestamp)}
        self.sections: Dict[str, Dict[str, Tuple[Any, int, float]]] = {}
        # In-flight message queue: List of (src, dst, payload)
        self.inbox: Dict[str, List[Dict[str, Any]]] = collections.defaultdict(list)
        self.erased_bits: Dict[str, float] = collections.defaultdict(float)
        self.rng = random.Random(1337)

    @property
    def name(self) -> str:
        return "Candidate Alpha (Cellular Sheaf)"

    def register_nodes(self, node_ids: List[str]) -> None:
        self.node_ids = list(node_ids)
        for nid in self.node_ids:
            self.sections[nid] = {}
            self.inbox[nid] = []
            self.erased_bits[nid] = 0.0

    def propose(self, node_id: str, key: str, value: Any) -> bool:
        if node_id not in self.sections:
            return False

        current = self.sections[node_id].get(key)
        new_ver = (current[1] + 1) if current else 1
        now = time.time()
        self.sections[node_id][key] = (value, new_ver, now)

        # Queue restriction update to all other nodes in the open cover
        for peer in self.node_ids:
            if peer != node_id:
                msg = {
                    "type": "RESTRICTION_MAP",
                    "src": node_id,
                    "dst": peer,
                    "key": key,
                    "value": value,
                    "version": new_ver,
                    "timestamp": now,
                }
                self.inbox[peer].append(msg)

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

        for msg in all_pending:
            src = msg["src"]
            dst = msg["dst"]

            # Check network partition
            if (src, dst) in active_partitions or (dst, src) in active_partitions:
                # Re-queue for next round (partitioned)
                self.inbox[dst].append(msg)
                continue

            # Check simulated packet drop
            if drop_rate > 0.0 and self.rng.random() < drop_rate:
                # Packet lost
                continue

            # Process restriction delivery
            self._apply_restriction(dst, msg)
            delivered_count += 1

        return delivered_count

    def _apply_restriction(self, dst: str, msg: Dict[str, Any]) -> None:
        key = msg["key"]
        val = msg["value"]
        ver = msg["version"]
        ts = msg["timestamp"]

        cur = self.sections[dst].get(key)
        if cur is None:
            self.sections[dst][key] = (val, ver, ts)
        else:
            cur_val, cur_ver, cur_ts = cur
            # Tie-break rule: highest version, then highest timestamp
            if (ver > cur_ver) or (ver == cur_ver and ts > cur_ts):
                # We overwrite the current value -> bit erasure!
                erased_size = len(str(cur_val).encode("utf-8")) * 8.0
                self.erased_bits[dst] += erased_size
                self.sections[dst][key] = (val, ver, ts)
            else:
                # Incoming value discarded
                erased_size = len(str(val).encode("utf-8")) * 8.0
                self.erased_bits[dst] += erased_size

    def get_node_state(self, node_id: str) -> Dict[str, Any]:
        sec = self.sections.get(node_id, {})
        return {k: v[0] for k, v in sec.items()}

    def get_erased_bits(self, node_id: Optional[str] = None) -> float:
        if node_id:
            return self.erased_bits.get(node_id, 0.0)
        return sum(self.erased_bits.values())

    def reset(self) -> None:
        self.node_ids = []
        self.sections.clear()
        self.inbox.clear()
        self.erased_bits.clear()
