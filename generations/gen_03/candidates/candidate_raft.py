"""Candidate Gamma: Quorum State Machine Replication (Raft-style).

Implements DistributedConsensusProtocol using leader terms, majority quorum
log replication, and state machine commits (Ongaro & Ousterhout 2014).
"""

from __future__ import annotations

import collections
import random
from typing import Any, Dict, List, Optional, Set, Tuple

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from crucible.protocol import DistributedConsensusProtocol


class CandidateRaftQuorumProtocol(DistributedConsensusProtocol):
    """Candidate Gamma: Raft-style Quorum Log Replication Engine."""

    def __init__(self):
        self.node_ids: List[str] = []
        self.leader_id: Optional[str] = None
        self.current_term: int = 1
        # Replicated logs: node_id -> list of (term, index, key, value)
        self.logs: Dict[str, List[Tuple[int, int, str, Any]]] = {}
        # Committed state machine: node_id -> {key: value}
        self.state_machines: Dict[str, Dict[str, Any]] = {}
        # Commit index per node
        self.commit_indices: Dict[str, int] = collections.defaultdict(int)
        # In-flight RPC inboxes: node_id -> list of RPCs
        self.inbox: Dict[str, List[Dict[str, Any]]] = collections.defaultdict(list)
        # Quorum tracking for uncommitted entries on leader: index -> set of acked node_ids
        self.quorum_acks: Dict[int, Set[str]] = collections.defaultdict(set)
        self.erased_bits: Dict[str, float] = collections.defaultdict(float)
        self.rng = random.Random(777)

    @property
    def name(self) -> str:
        return "Candidate Gamma (Raft Quorum)"

    def register_nodes(self, node_ids: List[str]) -> None:
        self.node_ids = list(node_ids)
        self.leader_id = self.node_ids[0] if self.node_ids else None
        self.current_term = 1

        for nid in self.node_ids:
            self.logs[nid] = []
            self.state_machines[nid] = {}
            self.commit_indices[nid] = 0
            self.inbox[nid] = []
            self.erased_bits[nid] = 0.0

    def propose(self, node_id: str, key: str, value: Any) -> bool:
        if not self.leader_id or node_id not in self.node_ids:
            return False

        # If propose is called on a follower, route to leader
        if node_id != self.leader_id:
            msg = {
                "type": "CLIENT_FORWARD",
                "src": node_id,
                "dst": self.leader_id,
                "key": key,
                "value": value,
            }
            self.inbox[self.leader_id].append(msg)
            return True

        # Leader receives proposal
        leader_log = self.logs[self.leader_id]
        entry_idx = len(leader_log) + 1
        entry = (self.current_term, entry_idx, key, value)
        leader_log.append(entry)

        # Leader acks its own entry
        self.quorum_acks[entry_idx].add(self.leader_id)

        # Broadcast AppendEntries RPCs to followers
        for peer in self.node_ids:
            if peer != self.leader_id:
                rpc = {
                    "type": "APPEND_ENTRIES",
                    "src": self.leader_id,
                    "dst": peer,
                    "term": self.current_term,
                    "entry": entry,
                    "leader_commit": self.commit_indices[self.leader_id],
                }
                self.inbox[peer].append(rpc)

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

            if (src, dst) in active_partitions or (dst, src) in active_partitions:
                self.inbox[dst].append(msg)
                continue

            if drop_rate > 0.0 and self.rng.random() < drop_rate:
                continue

            mtype = msg["type"]
            if mtype == "CLIENT_FORWARD":
                # Leader receives forwarded proposal
                self.propose(dst, msg["key"], msg["value"])
                delivered_count += 1

            elif mtype == "APPEND_ENTRIES":
                # Follower appends entry to its log
                entry = msg["entry"]
                self.logs[dst].append(entry)
                # Send ACK to leader
                ack_rpc = {
                    "type": "APPEND_ACK",
                    "src": dst,
                    "dst": src,
                    "index": entry[1],
                }
                self.inbox[src].append(ack_rpc)
                delivered_count += 1

                # Apply committed entries if leader committed
                self._apply_commits(dst, msg.get("leader_commit", 0))

            elif mtype == "APPEND_ACK":
                # Leader collects ACKs
                idx = msg["index"]
                self.quorum_acks[idx].add(src)
                # Check if quorum reached
                if len(self.quorum_acks[idx]) >= majority_quorum:
                    if idx > self.commit_indices[dst]:
                        self.commit_indices[dst] = idx
                        self._apply_commits(dst, idx)
                delivered_count += 1

        return delivered_count

    def _apply_commits(self, node_id: str, up_to_index: int) -> None:
        log = self.logs.get(node_id, [])
        cur_commit = self.commit_indices[node_id]

        target_commit = min(up_to_index, len(log))
        if target_commit > cur_commit:
            for i in range(cur_commit, target_commit):
                term, idx, key, val = log[i]
                old_val = self.state_machines[node_id].get(key)
                if old_val is not None:
                    # Logically overwritten in state machine -> erased bits
                    self.erased_bits[node_id] += len(str(old_val).encode("utf-8")) * 8.0
                self.state_machines[node_id][key] = val
            self.commit_indices[node_id] = target_commit

    def get_node_state(self, node_id: str) -> Dict[str, Any]:
        return dict(self.state_machines.get(node_id, {}))

    def get_erased_bits(self, node_id: Optional[str] = None) -> float:
        if node_id:
            return self.erased_bits.get(node_id, 0.0)
        return sum(self.erased_bits.values())

    def reset(self) -> None:
        self.node_ids = []
        self.leader_id = None
        self.current_term = 1
        self.logs.clear()
        self.state_machines.clear()
        self.commit_indices.clear()
        self.inbox.clear()
        self.quorum_acks.clear()
        self.erased_bits.clear()
