"""Decoupled Persistence across Boundary 3 ([L1-011_3]).

Formal Expression:
    T_3(S) = P(δ(S))

Operational Rule:
    Ensure strict modular separation of concerns at boundary 3. State transformation
    must be fully decoupled from physical storage persistence.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
import time


@dataclass
class PersistenceIntent:
    """Explicit decoupled persistence payload produced by state transformation."""
    record_id: str
    collection: str
    data: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    boundary: str = "BOUNDARY_3"
    timestamp: float = field(default_factory=time.time)


class Boundary3StorageAdapter(ABC):
    """Abstract interface defining the Boundary 3 storage contract."""

    @abstractmethod
    def persist(self, intent: PersistenceIntent) -> bool:
        """Persists a state transformation record across Boundary 3."""
        pass

    @abstractmethod
    def retrieve(self, collection: str, record_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a state record from Boundary 3 storage."""
        pass

    @abstractmethod
    def list_keys(self, collection: str) -> List[str]:
        """Lists all keys in a given collection."""
        pass


class InMemoryAdapter(Boundary3StorageAdapter):
    """Ephemeral in-memory implementation for sandboxes and fast tests."""

    def __init__(self):
        self._store: Dict[str, Dict[str, Dict[str, Any]]] = {}

    def persist(self, intent: PersistenceIntent) -> bool:
        if intent.collection not in self._store:
            self._store[intent.collection] = {}
        self._store[intent.collection][intent.record_id] = {
            "data": dict(intent.data),
            "metadata": dict(intent.metadata),
            "timestamp": intent.timestamp,
        }
        return True

    def retrieve(self, collection: str, record_id: str) -> Optional[Dict[str, Any]]:
        return self._store.get(collection, {}).get(record_id)

    def list_keys(self, collection: str) -> List[str]:
        return list(self._store.get(collection, {}).keys())


class FileSystemAdapter(Boundary3StorageAdapter):
    """Persistent filesystem implementation writing to structured directories."""

    def __init__(self, base_directory: Path):
        self.base_dir = Path(base_directory)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def persist(self, intent: PersistenceIntent) -> bool:
        target_dir = self.base_dir / intent.collection
        target_dir.mkdir(parents=True, exist_ok=True)
        target_file = target_dir / f"{intent.record_id}.json"

        payload = {
            "record_id": intent.record_id,
            "collection": intent.collection,
            "data": intent.data,
            "metadata": intent.metadata,
            "timestamp": intent.timestamp,
            "boundary": intent.boundary,
        }
        with open(target_file, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
        return True

    def retrieve(self, collection: str, record_id: str) -> Optional[Dict[str, Any]]:
        target_file = self.base_dir / collection / f"{record_id}.json"
        if not target_file.exists():
            return None
        with open(target_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def list_keys(self, collection: str) -> List[str]:
        target_dir = self.base_dir / collection
        if not target_dir.exists():
            return []
        return [f.stem for f in target_dir.glob("*.json")]


class Boundary3PersistenceManager:
    """Mediates state delta persistence while ensuring strict boundary decoupling."""

    def __init__(self, adapter: Optional[Boundary3StorageAdapter] = None):
        self.adapter = adapter or InMemoryAdapter()
        self.commit_history: List[PersistenceIntent] = []

    def commit_transformation(self, collection: str, record_id: str, delta: Dict[str, Any], meta: Optional[Dict[str, Any]] = None) -> PersistenceIntent:
        """Transforms state into an explicit decoupled PersistenceIntent and commits across Boundary 3."""
        intent = PersistenceIntent(
            record_id=record_id,
            collection=collection,
            data=delta,
            metadata=meta or {},
        )
        self.adapter.persist(intent)
        self.commit_history.append(intent)
        return intent

    def read_state(self, collection: str, record_id: str) -> Optional[Dict[str, Any]]:
        """Reads persisted state via Boundary 3 adapter."""
        return self.adapter.retrieve(collection, record_id)
