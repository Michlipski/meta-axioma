"""Axioma Fabric Distributed Sheaf-CRDT Broker Node.

Implements local topological open covering sections F(U_i), causal vector clock
progression, monotonic CRDT lattice join, and 3-pass ephemeral healing enclaves.
"""

from __future__ import annotations
import asyncio
import logging
import time
import uuid
from typing import Any, Callable, Dict, List, Optional, Set
from .models import CapabilityToken, CausalEvent, PartitionState, VectorClock
from .thermodynamics import LandauerRingBuffer, ThermodynamicBackpressureError

logger = logging.getLogger("axioma_fabric.broker")


class FabricSecurityError(Exception):
    """Raised when an unauthenticated or unauthorized action is attempted."""
    pass


class FabricPartitionError(Exception):
    """Raised when communication fails due to an active network partition."""
    pass


class FabricBrokerNode:
    """Distributed Broker Node governing an open topological subdomain U_i."""

    def __init__(
        self,
        node_id: str,
        subdomain: str,
        secret_key: str,
        ring_capacity: int = 2000,
        token_lease: float = 5000.0,
    ) -> None:
        self.node_id = node_id
        self.subdomain = subdomain
        self.secret_key = secret_key
        
        self.clock = VectorClock({node_id: 0})
        self.partition_state = PartitionState.HEALTHY
        self._severed_links: Set[str] = set()
        
        # Topic -> LandauerRingBuffer
        self._topic_buffers: Dict[str, LandauerRingBuffer] = {}
        self.ring_capacity = ring_capacity
        self.token_lease = token_lease
        
        # Topic -> Dict[event_id, CausalEvent] (Local Sheaf Section)
        self._sheaf_sections: Dict[str, Dict[str, CausalEvent]] = {}
        
        # Peer registry: node_id -> FabricBrokerNode reference
        self.peers: Dict[str, FabricBrokerNode] = {}

    def register_peer(self, peer: FabricBrokerNode) -> None:
        """Register a peer broker node in the cluster."""
        if peer.node_id != self.node_id:
            self.peers[peer.node_id] = peer

    def sever_link_to(self, peer_id: str) -> None:
        """Simulate asymmetric netsplit cutting outgoing link to peer."""
        self._severed_links.add(peer_id)
        if self._severed_links:
            self.partition_state = PartitionState.PARTITIONED

    def restore_link_to(self, peer_id: str) -> None:
        """Restore network link to peer."""
        self._severed_links.discard(peer_id)
        if not self._severed_links:
            self.partition_state = PartitionState.HEALTHY

    def is_link_severed(self, peer_id: str) -> bool:
        return peer_id in self._severed_links

    def _get_buffer(self, topic: str) -> LandauerRingBuffer:
        if topic not in self._topic_buffers:
            self._topic_buffers[topic] = LandauerRingBuffer(
                capacity_entries=self.ring_capacity,
                token_lease_budget=self.token_lease,
            )
        return self._topic_buffers[topic]

    def _execute_in_enclave(self, func: Callable, *args: Any, max_passes: int = 3, **kwargs: Any) -> Any:
        """Execute operation within a 3-pass ephemeral self-healing enclave."""
        last_err: Optional[Exception] = None
        for attempt in range(1, max_passes + 1):
            try:
                return func(*args, **kwargs)
            except (ThermodynamicBackpressureError, FabricSecurityError):
                # Hard invariant errors cannot be swallowed by enclaves
                raise
            except Exception as e:
                last_err = e
                logger.warning("Enclave pass %d failed on node %s: %s", attempt, self.node_id, e)
                time.sleep(0.005 * attempt)
        raise RuntimeError(f"Enclave exceeded {max_passes} self-healing passes on {self.node_id}: {last_err}") from last_err

    def publish(
        self,
        topic: str,
        payload: Dict[str, Any],
        token: CapabilityToken,
        auto_replicate: bool = True,
    ) -> CausalEvent:
        """Publish an event to a topic under capability authentication.
        
        Advances local vector clock and merges into local sheaf section F(U_i).
        If links are healthy, replicates to connected peers.
        """
        if not token.verify(self.secret_key):
            raise FabricSecurityError(f"Invalid or expired capability token for subject {token.subject}")
        if not token.allows(topic, "produce"):
            raise FabricSecurityError(f"Token does not permit produce on topic {topic}")

        # Advance vector clock
        self.clock = self.clock.increment(self.node_id)
        
        event_id = f"evt_{self.node_id}_{self.clock.clocks[self.node_id]}_{uuid.uuid4().hex[:6]}"
        event = CausalEvent.create(
            event_id=event_id,
            topic=topic,
            payload=payload,
            clock=self.clock,
            origin_node=self.node_id,
        )

        # Store in local section and ring buffer
        buf = self._get_buffer(topic)
        buf.append(event)
        
        if topic not in self._sheaf_sections:
            self._sheaf_sections[topic] = {}
        self._sheaf_sections[topic][event.event_id] = event

        # Cooperative replication to connected peers
        if auto_replicate:
            for peer_id, peer in self.peers.items():
                if not self.is_link_severed(peer_id) and not peer.is_link_severed(self.node_id):
                    try:
                        self._execute_in_enclave(peer.receive_peer_event, event)
                    except Exception as e:
                        logger.debug("Failed replication to %s: %s", peer_id, e)

        return event

    def receive_peer_event(self, event: CausalEvent) -> bool:
        """Ingest event from a peer node, performing CRDT lattice join."""
        if self.is_link_severed(event.origin_node):
            raise FabricPartitionError(f"Link severed from origin node {event.origin_node}")

        # Update vector clock with lattice join
        self.clock = self.clock.merge(event.vector_clock)

        topic = event.topic
        if topic not in self._sheaf_sections:
            self._sheaf_sections[topic] = {}

        # Idempotent CRDT insertion
        if event.event_id not in self._sheaf_sections[topic]:
            self._sheaf_sections[topic][event.event_id] = event
            buf = self._get_buffer(topic)
            buf.append(event)
            return True
        return False

    def get_section(self, topic: str) -> Dict[str, CausalEvent]:
        """Return local sheaf section F(U_i) for topic."""
        return dict(self._sheaf_sections.get(topic, {}))

    def get_stream(self, topic: str, since_clock: Optional[VectorClock] = None) -> List[CausalEvent]:
        """Read causal stream for a topic."""
        events = list(self.get_section(topic).values())
        # Sort causally by timestamp and event_id
        events.sort(key=lambda e: (e.timestamp, e.event_id))
        
        if since_clock is None:
            return events
        
        # Filter events that are strictly newer than since_clock
        filtered: List[CausalEvent] = []
        for e in events:
            if not e.vector_clock.is_less_than_or_equal(since_clock):
                filtered.append(e)
        return filtered

    def get_thermodynamics(self, topic: str) -> Dict[str, Any]:
        """Retrieve thermodynamic Landauer telemetry for topic."""
        buf = self._get_buffer(topic)
        return {
            "current_entries": buf.current_entries,
            "current_bytes": buf.current_bytes,
            "cumulative_erasure_joules": buf.cumulative_erasure_joules,
            "remaining_token_budget": buf.remaining_token_budget,
            "token_lease_budget": buf.token_lease_budget,
        }
