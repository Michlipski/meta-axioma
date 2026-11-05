# Generation 5 Candidate Novel Services (`general/candidate_services.md`)

> **Document Type:** Exploratory Service Architecture Dossier  
> **Target:** Generation 5 ($G_5$)  
> **Author:** Sovereign Research Service (`services/research/`, 192.168.40.10)  
> **Status:** Candidate Proposals for Architecture Expansion  

---

## 1. Motivation: Beyond the Initial 5 Enclaves

Generation 4b established five core enclaves: `research`, `builder`, `audit`, `telemetry`, and `governance`. While these cover the core synthesis loop (specification $\to$ code emission $\to$ verification $\to$ observation $\to$ control), they leave critical operational gaps at the outer boundaries of software systems engineering:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                      GENERATION 5 ENCLAVE EXPANSION TOPOLOGY                           │
├────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                        │
│   [ Research ] ───► [ Knowledge Graph* ] ───► [ Builder ] ───► [ Audit ]               │
│        ▲                                           │             │                     │
│        │        ┌─────────────────────────┐        │             │                     │
│        │        │   EVENT MESH FABRIC*    │        ▼             ▼                     │
│        └───────►│  (mesh.events.* pub/sub)│◄───────┴────── [ Simulator* ]              │
│                 └───────────┬─────────────┘                      │                     │
│                             ▼                                    │                     │
│   [ Governance ] ◄─── [ Telemetry ] ◄────────── [ Deployer* ] ◄──┘                     │
│                                                                                        │
│   * Indicates Proposed Candidate Service for Generation 5                              │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Candidate Service 1: Sovereign Deployment Enclave (`services/deployer/`)

### 2.1 The Operational Problem
Generation 4b compiles applications to the disk directory `apps/<app_name>/` and runs a local smoke test. However, it lacks native primitives to package, provision, deploy, monitor rolling canaries, and execute zero-downtime blue-green cutovers across heterogeneous nodes.

### 2.2 Proposed Capabilities in Generation 5
- **Hermetic Container & Binary Packaging:** Emits single-binary or zero-dependency container images (OCI-compliant or lightweight chroot bundles).
- **Canary Mesh Orchestrator:** Manages progressive traffic shifting ($5\% \to 25\% \to 100\%$) across multiple network nodes.
- **Automated Rollback Circuit Breakers:** Listens directly to Telemetry Service anomaly signals; immediately issues rollback transactions if invariant violation thresholds are breached within the canary window.
- **Service Mesh Proxy Configuration:** Generates and hot-reloads Envoy/WireGuard routing configurations dynamically.

### 2.3 Proposed URN & Port Allocation
- **IP / Port:** `192.168.40.60:8460` (or `10.5.0.60:8460` in Gen 5 distributed subnet)
- **URN Namespace:** `urn:axioma:g5:deployer:...`

---

## 3. Candidate Service 2: Autonomous Persona Simulator (`services/simulator/`)

### 3.1 The Operational Problem
Applications compiled in Generation 4b are verified against static test suites, headless journey walkers, and synthetic unit asserts. However, they lack empirical observation under chaotic, realistic, multi-user behavioral conditions.

### 3.2 Proposed Capabilities in Generation 5
- **Generative Persona Swarms:** Instantiates heterogeneous synthetic user personas (e.g., novice user, malicious adversarial fuzzer, power user under high network latency, accessibility screen-reader user).
- **Continuous Behavioral Journey Stressing:** Executes concurrent realistic user sessions against deployed frontends and backends, discovering race conditions, state machine deadlocks, and UX cognitive bottlenecks.
- **Accessibility & Ergonomic Scorer:** Automatically scores application usability against Nielsen Norman heuristics, WCAG AAA accessibility, and Landauer cognitive load metrics.

### 3.3 Proposed URN & Port Allocation
- **IP / Port:** `192.168.40.70:8470`
- **URN Namespace:** `urn:axioma:g5:simulator:...`

---

## 4. Candidate Service 3: Epistemic Knowledge Graph & Lineage (`services/knowledge_graph/`)

### 4.1 The Operational Problem
Currently, each compilation epoch and generation stores research artifacts and telemetry ledgers in isolated JSON/SQLite files. Cross-generational pattern recognition, anti-pattern taboo enforcement, and architectural lineage queries require manual script parsing.

### 4.2 Proposed Capabilities in Generation 5
- **Unified Graph Database:** Ingests AST nodes, statechart transitions, test results, human vetoes (`NEG-###`), and Waterloo SoC models into a unified queryable hypergraph (e.g., embedded Kùzu or SQLite Graph).
- **Cross-Generational Taboo Ingestion:** Automatically warns the Builder or Researcher when a proposed solution closely mirrors a previously failed or vetoed architecture from prior generations ($S_0 \to G_4$).
- **Semantic Code Lineage:** Traces every emitted function and class back to the originating human prompt, Waterloo SoC friction, and formal invariant URN.

### 4.3 Proposed URN & Port Allocation
- **IP / Port:** `192.168.40.80:8480`
- **URN Namespace:** `urn:axioma:g5:knowledge_graph:...`

---

## 5. Candidate Service 4: Sovereign Event Mesh & Pub/Sub Fabric (`services/event_mesh/`)

### 5.1 The Operational Problem
In Generation 4b, service communication relies predominantly on point-to-point HTTP RFC exchanges (`192.168.40.X`), synchronous push ingestion (`POST /api/v1/telemetry/ingest`), or post-tool execution hooks (`PostToolUse`). This creates several structural weaknesses:
1. **Coupled Sensory Burden:** Synthesizers, auditors, and compilers must explicitly know about and push to Telemetry.
2. **Ambient Task Blindspots:** When background subagents, skills, or standalone verification scripts run without explicit push wiring, Telemetry remains completely blind. Relying on transcript scraping is ungrounded and fragile.
3. **Write-Lock Contention:** Multi-agent bursts pushing directly to a single SQLite WAL store risk lock timeouts and dropped metrics.

### 5.2 Proposed Capabilities in Generation 5
- **Decentralized Pub/Sub Message Fabric:** High-throughput, non-blocking asynchronous event bus (embedded NATS, ZeroMQ, or shared-memory ring buffers) serving both local processes and distributed multi-host nodes over WireGuard.
- **Typed Topic Taxonomy (`mesh.events.*`):**
  - `mesh.events.research.*`: SoC deconstruction, contract derivation, statechart generation.
  - `mesh.events.builder.*`: AST leaf synthesis, file grounding witnesses, compilation cycles.
  - `mesh.events.audit.*`: Micro-auditor AST checks, SMT verification, Byzantine fuzz runs.
  - `mesh.events.telemetry.*`: Transaction logging, Merkle ledger anchoring, Landauer calorimetry.
  - `mesh.events.governance.*`: Quorum consensus, human HITL intercepts, vetoes (`NEG-###`).
- **Sovereign Decoupled Consumers:** Telemetry, Governance, and Audit subscribe as sovereign listeners. Any task or tool "using the system" automatically emits domain events without knowing who consumes them.
- **Guaranteed At-Least-Once Delivery & Replay:** Durable event logs allow newly booted services or telemetry cockpits to replay history from timestamp $t_0$.

### 5.3 Proposed URN & Port Allocation
- **IP / Port:** `192.168.40.90:8490` (or `10.5.0.90:8490` in Gen 5 distributed subnet)
- **URN Namespace:** `urn:axioma:g5:event_mesh:...`

---

## 6. Architectural Decision Path & Triage Boundary

Per the formal audit triage specified in [`general/audit_triage_and_next_steps.md`](audit_triage_and_next_steps.md):
1. **Intra-Generational Isolation (Gen 4b):** Generation 4b maintains its strict single-workstation disk boundary (`apps/<app_name>/`) and embedded SQLite WAL engine. Attempting to deploy live cloud instances or run distributed message brokers inside 4b violates `HERM-003`.
2. **Inter-Generational Mandate (Generation 5):** All four candidate enclaves (`deployer`, `simulator`, `knowledge_graph`, `event_mesh`) are formally allocated as independent sovereign enclaves in Generation 5. This upholds the Zero-Code Boundary (`[L1-G4B-002]`) and completes the full autonomous lifecycle: **Design $\to$ Build $\to$ Verify $\to$ Deploy $\to$ Simulate $\to$ Observe**.
