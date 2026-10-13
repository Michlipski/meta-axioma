"""Abstract Protocol Interface for the Evolutionary Crucible.

Every candidate distributed consensus architecture must implement this interface
to compete in the independent adversarial stress harness.
"""

from __future__ import annotations

import abc
from typing import Any, Dict, List, Optional, Set, Tuple


class DistributedConsensusProtocol(abc.ABC):
    """Abstract interface defining required behaviors for consensus candidates."""

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Name of the candidate architecture."""
        pass

    @abc.abstractmethod
    def register_nodes(self, node_ids: List[str]) -> None:
        """Initializes the cluster topology with given node identifiers."""
        pass

    @abc.abstractmethod
    def propose(self, node_id: str, key: str, value: Any) -> bool:
        """Initiates a state mutation proposal on a specific node."""
        pass

    @abc.abstractmethod
    def route_messages(
        self,
        active_partitions: Set[Tuple[str, str]],
        drop_rate: float = 0.0,
    ) -> int:
        """Processes message queues between nodes respecting active partitions and packet drops.
        
        Returns count of messages successfully delivered.
        """
        pass

    @abc.abstractmethod
    def get_node_state(self, node_id: str) -> Dict[str, Any]:
        """Returns the current state dictionary as observed by node_id."""
        pass

    @abc.abstractmethod
    def get_erased_bits(self, node_id: Optional[str] = None) -> float:
        """Returns cumulative bits erased (logically irreversible erasures) for node or cluster."""
        pass

    @abc.abstractmethod
    def reset(self) -> None:
        """Resets the protocol to initial pristine state."""
        pass
