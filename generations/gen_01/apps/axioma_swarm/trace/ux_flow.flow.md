---
flow: SwarmEdgeOrchestrationWorkflow
persona: EdgeMlEngineer
domains:
  - AxiomaSwarm
  - AppSpecification
  - GenerationalFeedback
---

# WORKFLOW: Local LLM Edge Orchestration & Micro-Swarm Daemon

> GOAL: Dynamically coordinate multiple quantized local models across limited consumer VRAM budgets with zero OOM panics, transparent allocation metrics, and failure-isolated task dispatch.

---

## FLOW 1: Hardware Resource Inspection & Memory Topology
1. Operator accesses operations dashboard (`http://localhost:8098`).
2. Dashboard queries `GET /api/vram` displaying total VRAM, active allocations, reserved OS buffer, and headroom.
3. System visualizes the resident model rack with per-model weights and KV cache utilization.

---

## FLOW 2: Intelligent Task Dispatch with Auto-Eviction
1. Operator submits prompt (e.g. "Generate optimized AC-3 backtracking solver in Python") with specialty tag `CODING` and priority `HIGH`.
2. Orchestrator inspects available models and selects `Qwen-2.5-Coder-7B-Q4_K_M`.
3. If model is `UNLOADED` and VRAM is tight, orchestrator deterministically evicts the oldest `IDLE` resident model via LRU policy.
4. Model transitions to `RESIDENT`, then `BUSY`.
5. Inference executes inside `ExceptionEnclave`, measuring latency and token throughput.
6. Result returned to operator; model transitions back to `RESIDENT` (IDLE).

---

## FLOW 3: Manual Model Swapping & Eviction
1. Operator manually unloads or loads specific weights to benchmark cold-start latency.
2. Direct API call `POST /api/models/{id}/evict` reclaims VRAM in zero clock cycles.
3. Event log records `MODEL_EVICTED` and derived VRAM pool updates immediately.

---

## FLOW 4: Enclave Fault Containment
1. If a worker encounters an invalid token stream or excessive context length, `ExceptionEnclave` traps the fault.
2. System returns structured error witness with recovery recommendation.
3. VRAM lease is immediately reclaimed; host daemon continues running smoothly.

---

## FLOW 5: Transgenerational Feedback Loop
1. Operator submits observations on model swap latency or allocation friction via `POST /api/feedback`.
2. Persisted into Generation G1/G2 ledger for successor compiler refinement.
