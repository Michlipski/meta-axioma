"""Domain models and data definitions for Axioma Swarm Edge Orchestrator.

Employs Physical Resource Limits ([L1-008]), Zero-Trust Scoping ([L1-015]),
and Functorial Event Sourcing ([L1-002]).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
import time
from typing import Any, Dict, List, Optional


class ModelStatus(str, Enum):
    UNLOADED = "UNLOADED"
    RESIDENT = "RESIDENT"
    BUSY = "BUSY"
    EVICTED = "EVICTED"


class ModelSpecialty(str, Enum):
    REASONING = "REASONING"
    CODING = "CODING"
    FAST_SUMMARY = "FAST_SUMMARY"
    VISION_EMBEDDING = "VISION_EMBEDDING"


class TaskPriority(str, Enum):
    HIGH = "HIGH"
    NORMAL = "NORMAL"
    BATCH = "BATCH"


class TaskStatus(str, Enum):
    QUEUED = "QUEUED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class EventType(str, Enum):
    MODEL_LOADED = "MODEL_LOADED"
    MODEL_EVICTED = "MODEL_EVICTED"
    TASK_QUEUED = "TASK_QUEUED"
    TASK_DISPATCHED = "TASK_DISPATCHED"
    TASK_COMPLETED = "TASK_COMPLETED"
    TASK_FAILED = "TASK_FAILED"
    TASK_CANCELLED = "TASK_CANCELLED"


@dataclass
class ModelDescriptor:
    model_id: str
    name: str
    quantization: str
    param_billions: float
    context_length: int
    vram_weights_mb: int
    vram_kv_mb: int
    specialty: ModelSpecialty
    status: ModelStatus = ModelStatus.UNLOADED
    last_active_timestamp: float = field(default_factory=time.time)

    @property
    def total_memory_mb(self) -> int:
        return self.vram_weights_mb + self.vram_kv_mb

    def to_dict(self) -> Dict[str, Any]:
        return {
            "model_id": self.model_id,
            "name": self.name,
            "quantization": self.quantization,
            "param_billions": self.param_billions,
            "context_length": self.context_length,
            "vram_weights_mb": self.vram_weights_mb,
            "vram_kv_mb": self.vram_kv_mb,
            "total_memory_mb": self.total_memory_mb,
            "specialty": self.specialty.value,
            "status": self.status.value,
            "last_active_timestamp": self.last_active_timestamp,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ModelDescriptor:
        return cls(
            model_id=data["model_id"],
            name=data["name"],
            quantization=data["quantization"],
            param_billions=float(data["param_billions"]),
            context_length=int(data.get("context_length", 4096)),
            vram_weights_mb=int(data["vram_weights_mb"]),
            vram_kv_mb=int(data.get("vram_kv_mb", 512)),
            specialty=ModelSpecialty(data.get("specialty", "REASONING")),
            status=ModelStatus(data.get("status", "UNLOADED")),
            last_active_timestamp=float(data.get("last_active_timestamp", time.time())),
        )


@dataclass
class VramPool:
    total_vram_mb: int = 16384  # 16 GB default
    allocated_vram_mb: int = 0
    reserved_buffer_mb: int = 2048  # 2 GB reserved for OS compositor
    device_name: str = "Apple M3 Max (36GB Unified Memory Mode)"

    @property
    def usable_vram_mb(self) -> int:
        return max(0, self.total_vram_mb - self.reserved_buffer_mb)

    @property
    def available_vram_mb(self) -> int:
        return max(0, self.usable_vram_mb - self.allocated_vram_mb)

    @property
    def utilization_pct(self) -> float:
        if self.usable_vram_mb == 0:
            return 100.0
        return round((self.allocated_vram_mb / self.usable_vram_mb) * 100.0, 1)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_vram_mb": self.total_vram_mb,
            "usable_vram_mb": self.usable_vram_mb,
            "allocated_vram_mb": self.allocated_vram_mb,
            "reserved_buffer_mb": self.reserved_buffer_mb,
            "available_vram_mb": self.available_vram_mb,
            "utilization_pct": self.utilization_pct,
            "device_name": self.device_name,
        }


@dataclass
class SwarmTask:
    task_id: str
    prompt: str
    specialty_required: ModelSpecialty = ModelSpecialty.REASONING
    target_model_id: Optional[str] = None
    priority: TaskPriority = TaskPriority.NORMAL
    status: TaskStatus = TaskStatus.QUEUED
    tokens_processed: int = 0
    vram_lease_mb: int = 0
    latency_ms: float = 0.0
    created_at: float = field(default_factory=time.time)
    completed_at: Optional[float] = None
    result_output: Optional[str] = None
    error_witness: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "prompt": self.prompt,
            "specialty_required": self.specialty_required.value,
            "target_model_id": self.target_model_id,
            "priority": self.priority.value,
            "status": self.status.value,
            "tokens_processed": self.tokens_processed,
            "vram_lease_mb": self.vram_lease_mb,
            "latency_ms": self.latency_ms,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
            "result_output": self.result_output,
            "error_witness": self.error_witness,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> SwarmTask:
        return cls(
            task_id=data["task_id"],
            prompt=data["prompt"],
            specialty_required=ModelSpecialty(data.get("specialty_required", "REASONING")),
            target_model_id=data.get("target_model_id"),
            priority=TaskPriority(data.get("priority", "NORMAL")),
            status=TaskStatus(data.get("status", "QUEUED")),
            tokens_processed=int(data.get("tokens_processed", 0)),
            vram_lease_mb=int(data.get("vram_lease_mb", 0)),
            latency_ms=float(data.get("latency_ms", 0.0)),
            created_at=float(data.get("created_at", time.time())),
            completed_at=data.get("completed_at"),
            result_output=data.get("result_output"),
            error_witness=data.get("error_witness"),
        )


@dataclass
class SwarmEvent:
    event_id: str
    event_type: EventType
    payload: Dict[str, Any]
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "payload": self.payload,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> SwarmEvent:
        return cls(
            event_id=data["event_id"],
            event_type=EventType(data["event_type"]),
            payload=data.get("payload", {}),
            timestamp=float(data.get("timestamp", time.time())),
        )


@dataclass
class FeedbackItem:
    feedback_id: str
    category: str
    comment: str
    timestamp: float = field(default_factory=time.time)
    generation: str = "gen_01"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
