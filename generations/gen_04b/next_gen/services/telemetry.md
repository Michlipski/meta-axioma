# Generation 5 Unified Telemetry & Evaluation Service Dossier (`services/telemetry.md`)

> **Enclave Target:** `services/telemetry/` (192.168.40.40)  
> **Target Successor:** Generation 5 Unified Telemetry Enclave  
> **Source Directive:** [L1-G4B-003] Hierarchical Merkle-DAG Telemetry, [L1-G4B-008] Mandatory Post-Synthesis Orchestrator Witness Reconciliation Gate  
> **Status:** Active Evolution Notes & Desiderata  

---

## 1. Context & Generation 4b Baseline

In Generation 4b, the **Telemetry & Evaluation Service** (`services/telemetry/`) provides the sensory apparatus and historical ledger for Meta-Axioma:
- **Hierarchical Merkle-DAG Ledger (`[L1-G4B-003]`):** Every RFC exchange, model-check result, and build artifact is hashed and anchored into a tamper-evident SHA-256 Merkle-DAG.
- **SQLite WAL Event Store (`event_store.py` / `telemetry_vault.db`):** High-throughput, crash-safe event streaming with WAL journaling.
- **Native Co-Located Presentation Cockpit (`services/telemetry/cockpit/`):** Unified web-based cockpit HUD (`cockpit_server.py`) serving live Canvas/SVG topologies, 36-state hierarchical XState v5 statecharts, and Server-Sent Event (SSE) transaction streaming directly from the service enclave.
- **Post-Synthesis Reconciliation Gate (`[L1-G4B-008]`):** Reconciles isolated subagent execution witnesses, replaces placeholder UUIDs with authentic conversation IDs, and anchors empirical token spends from `transcript.jsonl`.
- **Anti-Mock Subprocess Entrypoint Smoke Invariant (`[NEG-G1B-002]`):** Fully audited CLI entrypoint (`run.py`) supporting `--smoke-test`, `--cockpit`, and standalone 12-step certification executed via live OS subprocesses.

---

## 2. Generation 4b Friction Points & Limitations

1. **Single-Process SQLite Contention & The 79.2% Ingress Convergence Law:** Empirical analysis of 886 transactions in `telemetry_vault.db` proves that **79.2% of all mesh ingress converges on `services/telemetry`** (494 tx from orchestrator, 194 tx from governance, 14 tx from audit). While the local SQLite WAL ring buffer currently handles this with sub-50ms latency (38.8ms average), scaling across multi-host nodes in Generation 5 will immediately turn Telemetry into an Amdahl serialization bottleneck under distributed burst concurrency.
2. **Passive Push Ingestion vs. Ambient System Blindspot:** In Gen 4b, Telemetry relies on callers actively pushing records (`POST /api/v1/telemetry/ingest`) or manual hook interception (`PostToolUse`). If an agent, background task, or skill runs without explicit push wiring, Telemetry remains completely blind. Scraping private chat transcripts (`transcript.jsonl`) or running file-polling daemons is fragile, asynchronous, and unprincipled.
3. **Bimodal Latency Regime Contention:** Telemetry logs reveal a strictly bimodal latency spectrum: fast deterministic transport loops (38.8ms) run alongside heavy cognitive deliberation loops (`telemetry -> governance` at 15.5s, `governance -> research` at 13.3s). In Gen 4b, sharing event loops risks false heartbeat timeouts when cognitive deliberation blocks I/O.
4. **Token Mass vs. Transaction Cadence Mismatch:** Verification accounts for 21.0% of transactions (186 tx) but only 8.4% of BPE token volume (16,035 tokens), while synthesis accounts for 79.0% of transactions but 91.6% of tokens (175,215 tokens). Naive linear budget models fail to account for verb mass variance ($550\text{ tokens/tx}$ for `WRITE_FILE` vs $89\text{ tokens/tx}$ for `RUN_TEST_SUITE`).
5. **Statechart Topology vs. Transaction Buffer Disconnect (The "36 vs 2" Invariant):** The visual topology rendered in `cockpit/index.html` tracks a 36-state hierarchical XState v5 state machine (6 compound strata, 2 parallel regions, 4 deep history states, 6 recovery enclaves). However, the underlying transaction buffer initially required 2 bootstrap dummy records to prevent blank canvas renders on fresh boot, because the statechart was not event-sourced natively from the ingested stream.
6. **Coarse-Grained Epoch Granularity vs. Hardware-Level Nanosecond Metrics:** Timestamps and token metrics in Gen 4b are largely aggregate and derived from BPE token spend rather than nanosecond clock timestamps and empirical hardware energy/Landauer dissipation ($k_B T \ln 2$).
7. **Local Subnet & Socket Fallbacks:** Binding to virtual mesh IPs (`192.168.40.40`) requires loopback `127.0.0.1` fallbacks in single-host local development environments due to missing OS network aliases.

---

## 3. Generation 5 Desired Capabilities & Aspirations

### 3.1 Distributed OpenTelemetry & W3C Trace Mesh
- Full adoption of OpenTelemetry (OTel) wire standards with W3C `traceparent` header propagation across all HTTP, RPC, and WireGuard interfaces.
- Seamless tracing across physically separated machines, visualizing end-to-end spans from human prompt down to micro-auditor AST checks.

### 3.2 Real-Time Reactive WebSocket Cockpit HUD
- Telemetry Cockpit (`192.168.40.40:8440`) upgrades from an SSE/HTTP polling model to a live asynchronous, full-duplex WebSocket server.
- The browser HUD streams live agent status, token decay curves, AST node counts, and error spikes in real-time ($< 16\text{ms}$ frame latency).

### 3.3 State Delta Time-Travel Replay & Pure Event-Sourced Projections
- Moves from storing monolithic state snapshots to storing pure **Statechart Delta Events**:
  $$S_{t+1} = \Delta_t(S_t)$$
- The cockpit UI statechart is a pure mathematical projection $\mathcal{P}(E_{0..t})$ of the consumed event log.
- Allows bidirectional scrubbing: slide back in time to inspect exact application state at step 42, fork the timeline, inject a counterfactual event, and observe execution divergent paths—without requiring synthetic bootstrap records.

### 3.4 Multi-Tier Log Tiering & Landauer Pruning
- Automatically prunes high-entropy noisy log streams (e.g. heartbeat pings) while preserving cryptographically compressed Merkle proofs of core business transactions, preventing unbounded disk bloat.

### 3.5 Pure Event-Driven Architecture (EDA) & Sovereign Event Fabric
- Shift from synchronous request-response push and hook interception toward a **Decentralized Event Fabric / Pub-Sub Mesh (`mesh.events.*`)**.
- Any process "using the system"—whether compiling an app, executing a research SoC deconstruction, running an AST micro-audit, or triggering an agent skill—publishes strongly typed, immutable domain events onto the fabric.
- Telemetry subscribes as a sovereign consumer (`services/telemetry/`), automatically capturing all system activity across threads, processes, and nodes without intrusive transcript scraping or polling daemons.

### 3.6 Hardware Landauer Calorimetry & Monotonic Nanosecond Timestamps
- Nanosecond monotonic event timestamps (`CLOCK_MONOTONIC_RAW`).
- True Landauer thermodynamic tracking: measuring CPU cycle dissipation, GPU micro-wattage, and Landauer erasure cost ($E = k_B T \ln 2$) per synthesized token and AST mutation.

### 3.7 Subprocess Smoke & Living Service Contracts (`[NEG-G1B-002]`)
- Unconditional enforcement of the Anti-Mock Subprocess Entrypoint Smoke Invariant. Every telemetry daemon, event adapter, and cockpit server must pass continuous subprocess smoke verification (`subprocess.Popen(["python3", "run.py", ...])`) demonstrating clean boot, socket binding, and clean shutdown.

---

## 4. Proposed Invariants for Gen 5 Telemetry

- **`[L1-G5-TEL-001]` Tamper-Evident Hash Chain:** Every telemetry event must link to the SHA-256 hash of the immediately preceding event, maintaining an unbroken cryptographic lineage.
- **`[L1-G5-TEL-002]` Zero Synthetic Witness Invariant:** Unconditional preservation of `[L1-G4B-008]`. Final deliverables must contain authentic, reconciled conversation IDs and empirical BPE token counts extracted from real transcripts.
- **`[L1-G5-TEL-003]` Non-Blocking Asynchronous Persistence:** Telemetry logging must never block the critical path of code synthesis or runtime transaction processing.
- **`[L1-G5-TEL-004]` Sovereign Pub/Sub Event Ingestion:** Telemetry must consume strictly via pub/sub event subscriptions without intercepting caller process memory or scraping raw transcript logs.
- **`[L1-G5-TEL-005]` Pure Event-Sourced Statechart Duality:** The cockpit UI statechart must be a pure projection $\mathcal{P}(E_{0..t})$ of the consumed event log, with zero synthetic bootstrap records.
- **`[L1-G5-TEL-006]` Empirical Subprocess Smoke Invariant (`[NEG-G1B-002]`):** All telemetry daemon entrypoints must boot, bind, stream, and tear down cleanly in live OS subprocesses.
- **`[L1-G5-TEL-007]` Topological Zero-Traffic Invariant Proofs:** Telemetry must continuously evaluate the directed transaction adjacency matrix $\mathbf{A}$, mathematically proving that forbidden channels (e.g. `services/research -> services/audit == 0`, `services/builder -> services/governance == 0`) remain strictly zero.
- **`[L1-G5-TEL-008]` Zero-Heat Observer Verification Invariant:** Telemetry must assert that all transactions within `PHASE_1_RESEARCH_GATE` and `PHASE_2C_VERIFICATION` dissipate exactly $0.0\text{ J}$ of Landauer heat ($\text{BitsErased} \equiv 0$), halting compilation if destructive in-place mutation is detected during test passes.

---

## 5. Open Research Spikes & Inquiries

1. *Embedded High-Throughput Time-Series Engine:* Single-writer SQLite WAL contention ceiling ($> 100,000\text{ events/sec}$) vs. DuckDB / Columnar Parquet append-only segments.
2. *Sovereign Pub/Sub Transport:* Embedded NATS vs. ZeroMQ vs. shared memory ring buffers for zero-overhead local and cross-host event distribution.
3. *Zero-CDN Visual Graph Rendering:* How can we render force-directed 3D node graphs in pure, vanilla ES6 without pulling heavy external NPM dependencies?
4. *Hardware Calorimetry Integration:* Low-overhead CPU/GPU energy counters (RAPL / macOS power metrics) for empirical Landauer thermodynamic validation.
