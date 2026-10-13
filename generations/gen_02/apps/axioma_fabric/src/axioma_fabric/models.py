"""Axioma Fabric Core Domain Models.

Formal axiomatic models for distributed Sheaf-CRDT event streams,
vector clocks, zero-ambient capability tokens, and cocycle audit witnesses.
"""

from __future__ import annotations
import hashlib
import hmac
import json
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set


class PartitionState(str, Enum):
    """Network partition connectivity state."""
    HEALTHY = "healthy"
    PARTITIONED = "partitioned"
    RECONCILING = "reconciling"


@dataclass(frozen=True)
class VectorClock:
    """Causal vector clock for partial order tracking across distributed nodes."""
    clocks: Dict[str, int] = field(default_factory=dict)

    def increment(self, node_id: str) -> VectorClock:
        """Return a new VectorClock with node_id incremented."""
        new_clocks = dict(self.clocks)
        new_clocks[node_id] = new_clocks.get(node_id, 0) + 1
        return VectorClock(clocks=new_clocks)

    def merge(self, other: VectorClock) -> VectorClock:
        """Component-wise maximum join (lattice join operation \\sqcup)."""
        all_keys = set(self.clocks.keys()) | set(other.clocks.keys())
        merged = {k: max(self.clocks.get(k, 0), other.clocks.get(k, 0)) for k in all_keys}
        return VectorClock(clocks=merged)

    def is_less_than_or_equal(self, other: VectorClock) -> bool:
        """True if self <= other in causal partial order."""
        for k, v in self.clocks.items():
            if v > other.clocks.get(k, 0):
                return False
        return True

    def concurrent_with(self, other: VectorClock) -> bool:
        """True if neither clock causally dominates the other."""
        return not self.is_less_than_or_equal(other) and not other.is_less_than_or_equal(self)

    def to_dict(self) -> Dict[str, int]:
        return dict(self.clocks)

    @classmethod
    def from_dict(cls, data: Dict[str, int]) -> VectorClock:
        return cls(clocks=dict(data))


@dataclass(frozen=True)
class CapabilityToken:
    """Zero-ambient delegable capability token authenticated via HMAC-SHA256."""
    token_id: str
    subject: str
    allowed_topics: List[str]
    permissions: List[str]  # e.g., ["produce", "consume", "admin"]
    expires_at: float
    signature: str = ""

    def compute_signature(self, secret_key: str) -> str:
        """Compute HMAC-SHA256 signature for payload fields."""
        payload = f"{self.token_id}:{self.subject}:{','.join(sorted(self.allowed_topics))}:{','.join(sorted(self.permissions))}:{self.expires_at}"
        return hmac.new(secret_key.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()

    def verify(self, secret_key: str, current_time: Optional[float] = None) -> bool:
        """Verify HMAC integrity and expiration."""
        now = current_time if current_time is not None else time.time()
        if now > self.expires_at:
            return False
        expected = self.compute_signature(secret_key)
        return hmac.compare_digest(self.signature, expected)

    def allows(self, topic: str, action: str) -> bool:
        """Check if action on topic is permitted."""
        topic_match = ("*" in self.allowed_topics) or (topic in self.allowed_topics)
        action_match = ("*" in self.permissions) or (action in self.permissions)
        return topic_match and action_match

    @classmethod
    def create_signed(
        cls,
        token_id: str,
        subject: str,
        allowed_topics: List[str],
        permissions: List[str],
        ttl_seconds: float,
        secret_key: str,
    ) -> CapabilityToken:
        expires_at = time.time() + ttl_seconds
        unsigned = cls(
            token_id=token_id,
            subject=subject,
            allowed_topics=allowed_topics,
            permissions=permissions,
            expires_at=expires_at,
            signature="",
        )
        sig = unsigned.compute_signature(secret_key)
        return cls(
            token_id=token_id,
            subject=subject,
            allowed_topics=allowed_topics,
            permissions=permissions,
            expires_at=expires_at,
            signature=sig,
        )


@dataclass(frozen=True)
class CausalEvent:
    """Immutable causal event with vector clock and bit-erasure footprint."""
    event_id: str
    topic: str
    payload: Dict[str, Any]
    vector_clock: VectorClock
    origin_node: str
    timestamp: float
    byte_size: int

    @classmethod
    def create(
        cls,
        event_id: str,
        topic: str,
        payload: Dict[str, Any],
        clock: VectorClock,
        origin_node: str,
    ) -> CausalEvent:
        serialized = json.dumps(payload, sort_keys=True)
        size = len(serialized.encode("utf-8"))
        return cls(
            event_id=event_id,
            topic=topic,
            payload=payload,
            vector_clock=clock,
            origin_node=origin_node,
            timestamp=time.time(),
            byte_size=size,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "topic": self.topic,
            "payload": self.payload,
            "vector_clock": self.vector_clock.to_dict(),
            "origin_node": self.origin_node,
            "timestamp": self.timestamp,
            "byte_size": self.byte_size,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> CausalEvent:
        return cls(
            event_id=data["event_id"],
            topic=data["topic"],
            payload=data["payload"],
            vector_clock=VectorClock.from_dict(data["vector_clock"]),
            origin_node=data["origin_node"],
            timestamp=data["timestamp"],
            byte_size=data["byte_size"],
        )


@dataclass(frozen=True)
class CocycleWitness:
    """Formal audit witness certifying boundary restriction equality between subdomains."""
    witness_id: str
    node_i: str
    node_j: str
    subdomain_intersection: str
    agreed_events_count: int
    divergence_count: int
    reconciliation_applied: bool
    timestamp: float
    witness_hash: str

    @classmethod
    def build(
        cls,
        witness_id: str,
        node_i: str,
        node_j: str,
        subdomain_intersection: str,
        agreed_count: int,
        divergence_count: int,
        reconciled: bool,
    ) -> CocycleWitness:
        now = time.time()
        payload = f"{witness_id}:{node_i}:{node_j}:{subdomain_intersection}:{agreed_count}:{divergence_count}:{reconciled}:{now}"
        w_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        return cls(
            witness_id=witness_id,
            node_i=node_i,
            node_j=node_j,
            subdomain_intersection=subdomain_intersection,
            agreed_events_count=agreed_count,
            divergence_count=divergence_count,
            reconciliation_applied=reconciled,
            timestamp=now,
            witness_hash=w_hash,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "witness_id": self.witness_id,
            "node_i": self.node_i,
            "node_j": self.node_j,
            "subdomain_intersection": self.subdomain_intersection,
            "agreed_events_count": self.agreed_events_count,
            "divergence_count": self.divergence_count,
            "reconciliation_applied": self.reconciliation_applied,
            "timestamp": self.timestamp,
            "witness_hash": self.witness_hash,
        }
