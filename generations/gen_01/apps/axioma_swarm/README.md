# Axioma Swarm: Local LLM Edge Orchestrator & Micro-Swarm Daemon

> **Portfolio System 06** • Port `8098` • Generation `gen_01`  
> Stateful edge daemon coordinating quantized local model VRAM lifecycles, tensor memory allocations, LRU evictions, and failure-isolated task dispatch on consumer hardware.

---

## 1. Overview & Architectural Thesis

Running multiple open-weights models (e.g. reasoning, coding, extraction) on consumer hardware (such as Apple Silicon Unified Memory or single Nvidia GPUs) typically results in sudden Out-Of-Memory (OOM) kernel panics when concurrent models exceed physical limits.

**Axioma Swarm** enforces zero-trust physical resource constraints:
1. **Mathematical Memory Leases ([`L1-008`](file:///Users/michaellipski/dev/meta-axioma/trace/domains/trace_evolution.domain.md)):** Calculates model footprint ($W_{\text{weights}} + K_{\text{context}} \times L_{\text{layers}}$) prior to allocation. Rejects or gates any request that would pierce the OS reserved buffer.
2. **Deterministic LRU Model Eviction:** Automatically evicts the least recently active resident model when VRAM headroom is tight, seamlessly swapping in specialized models.
3. **Demarcated Exception Enclaves ([`L1-016`](file:///Users/michaellipski/dev/meta-axioma/trace/domains/trace_evolution.domain.md)):** Isolates task processing and inference memory spikes inside exception boundaries, returning structured error witnesses and immediately releasing VRAM without taking down the host daemon.
4. **Append-Only Event Sourcing ([`L1-002`](file:///Users/michaellipski/dev/meta-axioma/trace/domains/trace_evolution.domain.md)):** Every model load, eviction, and task state mutation is persisted to an immutable event log in `data/events.json`.

---

## 2. Axiomatic Mapping & Invariants

| Axiom ID | Formal Principle | Concrete Implementation in `axioma_swarm` |
|---|---|---|
| **L1-008** | Physical Resource & Landauer Bounds | Mathematical VRAM budget allocator (`VramPool`, `vram_manager.py`). Restricts allocations to $M_{\text{usable}} = M_{\text{total}} - M_{\text{reserved}}$ with OOM prevention gate. |
| **L1-016** | Demarcated Exception Enclaves | Traps model worker faults, inference timeouts, and memory spikes within `ExceptionEnclave`, returning structured recovery witnesses. |
| **L1-015** | Zero-Trust Scoping (Nouns & Verbs) | Strict schemas for model descriptors, VRAM states, and deterministic state transitions (`LOAD_MODEL`, `EVICT_MODEL`, `DISPATCH_TASK`). |
| **L1-002** | Functorial Event Sourcing | Append-only event log in `data/events.json` recording every residency mutation and task dispatch. |
| **L1-011_3** | Decoupled Persistence | Complete separation between ephemeral GPU residency state and durable disk records in `data/tasks.json`. |
| **L1-015_1** | Compositional Boundary Isolation | Decoupled model worker lifecycle preventing cascaded failures across models. |
| **NEG-G2-003** | Main Flow & Domain Test Gate | 100% automated test coverage across VRAM budget enforcement, LRU eviction, OOM gating, enclave containment, and REST APIs. |

---

## 3. Endpoints & API Reference

| Endpoint | Method | Description |
|---|---|---|
| `/` | `GET` | Edge ML Operations Dashboard with live VRAM topology bar, model rack, and task console. |
| `/api/vram` | `GET` | Returns real-time VRAM allocation metrics, available headroom, and device profile. |
| `/api/models` | `GET` | Lists all registered models in the catalog and their residency status (`UNLOADED`, `RESIDENT`, `BUSY`). |
| `/api/models/{id}/load` | `POST` | Loads model into VRAM, automatically triggering LRU eviction of idle models if needed. |
| `/api/models/{id}/evict` | `POST` | Manually evicts model from VRAM, immediately reclaiming tensor memory. |
| `/api/tasks` | `GET` | Returns list of all active, queued, and completed swarm tasks. |
| `/api/tasks/dispatch` | `POST` | Submits and executes a task with priority, specialty routing, and enclave containment. |
| `/api/tasks/{id}/cancel` | `POST` | Cancels a queued task. |
| `/api/feedback` | `POST` | Appends transgenerational feedback to `data/feedback.json`. |
| `/api/telemetry` | `GET` | Aggregated daemon throughput, token counts, and enclave isolation stats. |
| `/health` | `GET` | Standard health probe. |

---

## 4. Launching the Edge Daemon

```bash
# Launch on default port 8098
python3 apps/axioma_swarm/run.py

# Or launch on custom port
python3 apps/axioma_swarm/run.py 8198
```
Then visit `http://localhost:8098` to monitor VRAM allocation, swap local models, and dispatch edge tasks.
