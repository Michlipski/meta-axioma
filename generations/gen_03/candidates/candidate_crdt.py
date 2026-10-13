"""Candidate Beta: Delta-State Conflict-Free Replicated Data Type (Delta-CRDT).

Implements DistributedConsensusProtocol using bounded causal dot stores
and join-semilattices (Almeida, Baquero, Shoker 2016, 2018).
"""

from __future__ import annotations

import collections
import random
from typing import Any, Dict, List, Optional, Set, Tuple

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from crucible.protocol import DistributedConsensusProtocol


class CandidateDeltaCRDTProtocol(DistributedConsensusProtocol):
    """Candidate Beta: Delta-CRDT with Causal Context and Dot Stores."""

    def __init__(self):
        self.node_ids: List[str] = []
        # Causal sequence counters per node: node_id -> int
        self.counters: Dict[str, int] = collections.defaultdict(int)
        # Replicated state: node_id -> {key: (value, dot_origin, dot_seq)}
        self.stores: Dict[str, Dict[str, Tuple[Any, str, int]]] = {}
        # Causal contexts: node_id -> {origin_node_id: max_seq_seen}
        self.contexts: Dict[str, Dict[str, int]] = {}
        # Message inboxes: node_id -> list of deltas
        self.inbox: Dict[str, List[Dict[str, Any]]] = collections.defaultdict(list)
        self.erased_bits: Dict[str, float] = collections.defaultdict(float)
        self.rng = random.Random(2026)

    @property
    def name(self) -> str:
        return "Candidate Beta (Delta-CRDT)"

    def register_nodes(self, node_ids: List[str]) -> None:
        self.node_ids = list(node_ids)
        for nid in self.node_ids:
            self.stores[nid] = {}
            self.contexts[nid] = {other: 0 for other in self.node_ids}
            self.counters[nid] = 0
            self.inbox[nid] = []
            self.erased_bits[nid] = 0.0

    def propose(self, node_id: str, key: str, value: Any) -> bool:
        if node_id not in self.stores:
            return False

        # Advance causal dot
        self.counters[node_id] += 1
        dot_seq = self.counters[node_id]
        self.contexts[node_id][node_id] = dot_seq

        # Record in local dot store
        old = self.stores[node_id].get(key)
        if old is not None:
            # Overwrote prior local dot -> bit erasure
            self.erased_bits[node_id] += len(str(old[0]).encode("utf-8")) * 8.0

        self.stores[node_id][key] = (value, node_id, dot_seq)

        # Broadcast delta mutator
        delta = {
            "type": "DELTA_MUTATOR",
            "src": node_id,
            "key": key,
            "value": value,
            "dot_origin": node_id,
            "dot_seq": dot_seq,
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

        for msg in all_pending:
            src = msg["src"]
            dst = msg["dst"]

            # Partition check
            if (src, dst) in active_partitions or (dst, src) in active_partitions:
                self.inbox[dst].append(msg)
                continue

            # Packet drop check
            if drop_rate > 0.0 and self.rng.random() < drop_rate:
                continue

            self._merge_delta(dst, msg)
            delivered_count += 1

        return delivered_count

    def _merge_delta(self, dst: str, delta: Dict[str, Any]) -> None:
        key = delta["key"]
        val = delta["value"]
        origin = delta["dot_origin"]
        seq = delta["dot_seq"]

        cur_ctx = self.contexts[dst].get(origin, 0)
        local_entry = self.stores[dst].get(key)

        # Monotonic lattice join condition
        if local_entry is None:
            self.stores[dst][key] = (val, origin, seq)
            self.contexts[dst][origin] = max(cur_ctx, seq)
        else:
            loc_val, loc_origin, loc_seq = local_entry
            # Compare causal dots
            if seq > loc_seq or (seq == loc_seq and (origin, str(val)) > (loc_origin, str(loc_val))):
                # Replace local with incoming delta
                self.erased_bits[dst] += len(str(loc_val).encode("utf-8")) * 8.0
                self.stores[dst][key] = (val, origin, seq)
                self.contexts[dst][origin] = max(cur_ctx, seq)
            else:
                # Discard incoming delta
                self.erased_bits[dst] += len(str(val).encode("utf-8")) * 8.0
                self.contexts[dst][origin] = max(cur_ctx, seq)

    def get_node_state(self, node_id: str) -> Dict[str, Any]:
        st = self.stores.get(node_id, {})
        return {k: v[0] for k, v in st.items()}

    def get_erased_bits(self, node_id: Optional[str] = None) -> float:
        if node_id:
            return self.erased_bits.get(node_id, 0.0)
        return sum(self.erased_bits.values())

    def reset(self) -> None:
        self.node_ids = []
        self.counters.clear()
        self.stores.clear()
        self.contexts.clear()
        self.inbox.clear()
        self.erased_bits.clear()
