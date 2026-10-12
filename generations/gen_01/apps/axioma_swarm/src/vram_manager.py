"""VRAM Tensor Memory Budget Allocator & LRU Eviction Engine for Axioma Swarm.

Enforces Physical Resource Bounds ([L1-008]) and OOM Prevention Gates.
"""

from __future__ import annotations

from pathlib import Path
import threading
import time
from typing import Any, Dict, List, Optional, Tuple

from models import ModelDescriptor, ModelSpecialty, ModelStatus, VramPool


class OomPreventionError(RuntimeError):
    """Raised when an allocation request would exceed the safe VRAM capacity."""
    pass


class VramManager:
    """Thread-safe VRAM allocator with LRU model eviction and allocator safety gates."""

    DEFAULT_CATALOG: List[ModelDescriptor] = [
        ModelDescriptor(
            model_id="qwen-2.5-coder-7b",
            name="Qwen 2.5 Coder 7B (Q4_K_M)",
            quantization="Q4_K_M",
            param_billions=7.6,
            context_length=8192,
            vram_weights_mb=4800,
            vram_kv_mb=1024,
            specialty=ModelSpecialty.CODING,
            status=ModelStatus.UNLOADED,
        ),
        ModelDescriptor(
            model_id="llama-3.2-3b",
            name="Llama 3.2 3B Instruct (Q8_0)",
            quantization="Q8_0",
            param_billions=3.2,
            context_length=4096,
            vram_weights_mb=3400,
            vram_kv_mb=512,
            specialty=ModelSpecialty.REASONING,
            status=ModelStatus.UNLOADED,
        ),
        ModelDescriptor(
            model_id="phi-3.5-mini",
            name="Phi 3.5 Mini Instruct (Q4_K_S)",
            quantization="Q4_K_S",
            param_billions=3.8,
            context_length=4096,
            vram_weights_mb=2400,
            vram_kv_mb=512,
            specialty=ModelSpecialty.FAST_SUMMARY,
            status=ModelStatus.UNLOADED,
        ),
        ModelDescriptor(
            model_id="deepseek-r1-8b",
            name="DeepSeek R1 Distill 8B (Q4_K_M)",
            quantization="Q4_K_M",
            param_billions=8.0,
            context_length=8192,
            vram_weights_mb=5200,
            vram_kv_mb=1024,
            specialty=ModelSpecialty.REASONING,
            status=ModelStatus.UNLOADED,
        ),
        ModelDescriptor(
            model_id="bge-large-en",
            name="BGE Large English (FP16 Embeddings)",
            quantization="FP16",
            param_billions=0.34,
            context_length=2048,
            vram_weights_mb=680,
            vram_kv_mb=128,
            specialty=ModelSpecialty.VISION_EMBEDDING,
            status=ModelStatus.UNLOADED,
        ),
    ]

    def __init__(self, pool: Optional[VramPool] = None):
        self.lock = threading.RLock()
        self.pool = pool or VramPool()
        self.models: Dict[str, ModelDescriptor] = {}
        self.eviction_history: List[Dict[str, Any]] = []

        # Populate catalog
        for desc in self.DEFAULT_CATALOG:
            self.models[desc.model_id] = ModelDescriptor(
                model_id=desc.model_id,
                name=desc.name,
                quantization=desc.quantization,
                param_billions=desc.param_billions,
                context_length=desc.context_length,
                vram_weights_mb=desc.vram_weights_mb,
                vram_kv_mb=desc.vram_kv_mb,
                specialty=desc.specialty,
                status=ModelStatus.UNLOADED,
                last_active_timestamp=time.time(),
            )

    def get_vram_state(self) -> Dict[str, Any]:
        """Returns the current VRAM budget snapshot."""
        with self.lock:
            return self.pool.to_dict()

    def get_models(self) -> List[Dict[str, Any]]:
        """Returns the list of all registered models and their residency status."""
        with self.lock:
            return [m.to_dict() for m in self.models.values()]

    def can_fit_without_eviction(self, model_id: str) -> bool:
        """Checks if a model can fit in available VRAM without evicting other models."""
        with self.lock:
            if model_id not in self.models:
                raise KeyError(f"Model {model_id} not found in catalog.")
            model = self.models[model_id]
            if model.status in [ModelStatus.RESIDENT, ModelStatus.BUSY]:
                return True
            return self.pool.available_vram_mb >= model.total_memory_mb

    def allocate_model(self, model_id: str) -> Tuple[ModelDescriptor, List[str]]:
        """Allocates VRAM for model, deterministically evicting IDLE resident models if needed.
        
        Returns tuple of (loaded_model, list_of_evicted_model_ids).
        Raises OomPreventionError if model cannot fit even after evicting all idle models.
        """
        with self.lock:
            if model_id not in self.models:
                raise KeyError(f"Model {model_id} not registered.")

            model = self.models[model_id]
            if model.status in [ModelStatus.RESIDENT, ModelStatus.BUSY]:
                model.last_active_timestamp = time.time()
                return model, []

            required_mb = model.total_memory_mb
            if required_mb > self.pool.usable_vram_mb:
                raise OomPreventionError(
                    f"Physical VRAM limit exceeded: Model {model_id} requires {required_mb}MB, "
                    f"which exceeds the entire usable budget of {self.pool.usable_vram_mb}MB."
                )

            evicted_ids: List[str] = []

            # Perform LRU eviction while memory is insufficient
            while self.pool.available_vram_mb < required_mb:
                # Find idle resident models
                idle_models = [m for m in self.models.values() if m.status == ModelStatus.RESIDENT]
                if not idle_models:
                    busy_count = sum(1 for m in self.models.values() if m.status == ModelStatus.BUSY)
                    raise OomPreventionError(
                        f"OOM Prevention Gate Triggered: Cannot allocate {required_mb}MB for {model_id}. "
                        f"All {busy_count} resident models are actively BUSY with concurrent tasks. "
                        f"Available headroom: {self.pool.available_vram_mb}MB."
                    )

                # Sort by least recently active
                idle_models.sort(key=lambda m: m.last_active_timestamp)
                victim = idle_models[0]

                # Evict victim
                self._evict_model_locked(victim.model_id)
                evicted_ids.append(victim.model_id)

            # Allocate target model
            self.pool.allocated_vram_mb += required_mb
            model.status = ModelStatus.RESIDENT
            model.last_active_timestamp = time.time()

            return model, evicted_ids

    def evict_model(self, model_id: str) -> ModelDescriptor:
        """Manually evicts a model, releasing its tensor memory back to the pool."""
        with self.lock:
            return self._evict_model_locked(model_id)

    def _evict_model_locked(self, model_id: str) -> ModelDescriptor:
        if model_id not in self.models:
            raise KeyError(f"Model {model_id} not found.")

        model = self.models[model_id]
        if model.status == ModelStatus.BUSY:
            raise RuntimeError(f"Cannot evict model {model_id}: active inference task in progress.")

        if model.status == ModelStatus.RESIDENT:
            released_mb = model.total_memory_mb
            self.pool.allocated_vram_mb = max(0, self.pool.allocated_vram_mb - released_mb)
            model.status = ModelStatus.UNLOADED
            self.eviction_history.append({
                "model_id": model_id,
                "freed_mb": released_mb,
                "timestamp": time.time(),
            })

        return model

    def acquire_inference(self, model_id: str) -> ModelDescriptor:
        """Marks model as BUSY for an active task."""
        with self.lock:
            if model_id not in self.models:
                raise KeyError(f"Model {model_id} not found.")
            model = self.models[model_id]
            if model.status != ModelStatus.RESIDENT:
                raise RuntimeError(f"Cannot acquire inference on model {model_id} in state {model.status.value}.")
            model.status = ModelStatus.BUSY
            model.last_active_timestamp = time.time()
            return model

    def release_inference(self, model_id: str) -> ModelDescriptor:
        """Returns model to RESIDENT state upon task completion."""
        with self.lock:
            if model_id not in self.models:
                raise KeyError(f"Model {model_id} not found.")
            model = self.models[model_id]
            if model.status == ModelStatus.BUSY:
                model.status = ModelStatus.RESIDENT
                model.last_active_timestamp = time.time()
            return model
