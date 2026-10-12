---
domain: AxiomaSwarm
related_domains:
  - AppSpecification
  - GenerationalFeedback
  - TelemetryAudit
---

CONSTRAINTS:
- Total allocated VRAM must never exceed (total_vram_mb - reserved_buffer_mb) under any concurrent workload (L1-008 OOM Prevention Gate).
- When a task requires an unloaded model and available VRAM is insufficient, the orchestrator must automatically trigger deterministic LRU eviction of the least-recently used IDLE resident model.
- If all resident models are BUSY and VRAM is exhausted, the dispatch gate must hold the task in QUEUED state until capacity clears or timeout expires, never panicking the allocator.
- All model execution and task processing must occur inside Demarcated Exception Enclaves (L1-016), isolating runtime faults and returning structured witness diagnostics.
- All state mutations (model load, evict, task dispatch, completion) must be recorded in an append-only event stream (L1-002).
- Decoupled persistence across Boundary 3 (L1-011_3) isolates volatile GPU execution state from durable task history on disk.

GLOSSARY:
- VRAM Pool: Physical unified memory or dedicated GPU memory budget managed by the daemon.
- Reserved Buffer: Safety margin (e.g. 2048 MB) reserved for OS and display compositor to prevent display freezing.
- LRU Eviction: Least-Recently Used eviction policy releasing resident model tensor memory.
- Exception Enclave: Demarcated execution sandbox catching task faults, OOM signals, and timeout spikes without terminating the daemon.

# ENTITY: ModelDescriptor
MUST HAVE:
- model_id: String
- name: String
- quantization: String
- param_billions: Float
- context_length: Integer
- vram_weights_mb: Integer
- vram_kv_mb: Integer
- status: Enum (UNLOADED, RESIDENT, BUSY, EVICTED)
- specialty: Enum (REASONING, CODING, FAST_SUMMARY, VISION_EMBEDDING)
- last_active_timestamp: Float

RULES:
- R1: Model cannot transition to BUSY unless status is RESIDENT.
- R2: Model cannot transition to RESIDENT if required memory exceeds available VRAM pool capacity.

# ENTITY: SwarmTask
MUST HAVE:
- task_id: String
- prompt: String
- priority: Enum (HIGH, NORMAL, BATCH)
- status: Enum (QUEUED, PROCESSING, COMPLETED, FAILED, CANCELLED)
- tokens_processed: Integer
- vram_lease_mb: Integer
- latency_ms: Float
