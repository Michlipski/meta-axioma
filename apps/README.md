# Meta-Axioma Standardized Applications Registry (`/apps`)

This directory serves as the canonical registry and top-level index of all **non-generator software applications** compiled across the Meta-Axioma generational lineage ($G_1, G_2, \dots$).

> 📋 **Systems Portfolio & Feedback Ledger:** See [`SYSTEMS_PORTFOLIO.md`](file:///Users/michaellipski/dev/meta-axioma/SYSTEMS_PORTFOLIO.md) for the active 6-system testing portfolio, post-mortems, and the Active Feedback Elicitation Protocol.

---

## 1. The High-Level Jettison Telos
The recursive bootstrapping of compilers is not an insular closed circuit. Its ultimate purpose is **The High-Level Jettison**: producing robust, delightful, and human-controllable production software applications that people genuinely love and find useful (Target $P_1$ Ergonomics).

All applications in this registry are compiled from formal specifications using the structural invariants discovered and proven by the compiler lineage.

---

## 2. Standardized Application Anatomy
Every application inside `/apps/<app_id>/` (and canonically located at `generations/gen_XX/apps/<app_id>/`) strictly adheres to [`trace/domains/app_specification.domain.md`](file:///Users/michaellipski/dev/meta-axioma/trace/domains/app_specification.domain.md):

```
apps/<app_id>/
├── app.json                # Canonical Machine-Readable Manifest
├── README.md               # Human-readable documentation, UX, how to run
├── run.py                  # Standard zero-dependency Python entrypoint (chmod +x)
├── trace/                  # Declarative TRACE specification for this app
│   ├── app.domain.md       # Domain entities, constraints, and invariants
│   └── ux_flow.flow.md     # Persona goal completion flows (Target P1)
├── schema/                 # Dual-boundary schemas
│   ├── nouns.json          # Typed data schemas (Nouns - L1-015, L1-004)
│   └── verbs.json          # Deterministic state automata transitions (Verbs - L1-015)
├── src/                    # Modular application backend code
│   ├── __init__.py
│   ├── server.py           # Zero-trust HTTP / MCP API gateway & state engine
├── data/                   # Decoupled state persistence (Boundary 3 - L1-011_3)
│   ├── seed.json           # Baseline seed data
│   └── app_state.json      # Active runtime state snapshot
├── static/                 # Front-end user interface (Target P1 ergonomics)
│   ├── index.html          # Semantic HTML5 layout
│   ├── style.css           # Ergonomic stylesheet & design system
│   └── app.js              # Reactive UI client with undo/redo & live telemetry
└── tests/                  # Verification test suite
    ├── __init__.py
    └── test_app.py         # Standard self-healing & invariant verification tests
```

---

## 3. Active Applications Catalog

| App ID | Name | Generation | Port | Description | Invariants Embodied |
| :--- | :--- | :--- | :--- | :--- | :--- |
| [`axioma_flow`](file:///Users/michaellipski/dev/meta-axioma/apps/axioma_flow/) | **Axioma Flow** | $G_1$ | `8088` | Invariant-bounded, Landauer-audited Kanban & Task workspace with functorial undo/redo and exception enclaves. | `L1-002`, `L1-004`, `L1-011_3`, `L1-008`, `L1-015`, `L1-016`, `L1-015_1` |
| [`axioma_lexis`](file:///Users/michaellipski/dev/meta-axioma/apps/axioma_lexis/) | **Axioma Lexis** | $G_1$ | `8090` | Adaptive Spaced Repetition (SM-2) vocabulary & flashcard app for Android with progressive dictionary lookup and functorial undo. | `L1-002`, `L1-004`, `L1-011_3`, `L1-008`, `L1-015`, `L1-016`, `L1-015_1` |
| [`axioma_dual_fsm`](file:///Users/michaellipski/dev/meta-axioma/apps/axioma_dual_fsm/) | **Axioma Dual FSM** | $G_1$ | `8092` | Zero-trust AI runtime governance kernel gating LLMs through coupled dual FSMs, tool failure loops, and de-escalation. | `L1-002`, `L1-004`, `L1-011_3`, `L1-008`, `L1-015`, `L1-016`, `L1-015_1` |
| [`axioma_crossword`](file:///Users/michaellipski/dev/meta-axioma/apps/axioma_crossword/) | **Axioma Crossword** | $G_{1b}$ | `8094` | Cryptic crossword solving studio with 2-column solver workbench, soft mobile keypad, Clue Anatomy Dissector, and symmetrical grid solver. | `L1-G1B-001`, `L1-G1B-002`, `NEG-G1B-001`, `L1-002`, `L1-004`, `L1-011_3` |
| [`axioma_eink`](file:///Users/michaellipski/dev/meta-axioma/apps/axioma_eink/) | **Axioma E-Ink** | $G_1$ | `8096` | Asynchronous Task Router & Ambient Electrophoretic Glanceboard for Kindle/Kobo with strict zero-JS, 15m meta-refresh, and Daily Big 3–5 focus bounding. | `L1-002`, `L1-004`, `L1-011_3`, `L1-008`, `L1-015`, `L1-016`, `L1-015_1` |
| [`axioma_swarm`](file:///Users/michaellipski/dev/meta-axioma/apps/axioma_swarm/) | **Axioma Swarm** | $G_1$ | `8098` | Local LLM Edge Orchestrator & Micro-Swarm Daemon coordinating quantized model VRAM lifecycles, LRU eviction, and OOM-isolated task dispatch. | `L1-008`, `L1-016`, `L1-015`, `L1-002`, `L1-011_3`, `L1-015_1` |
| [`axioma_sentinel`](file:///Users/michaellipski/dev/meta-axioma/apps/axioma_sentinel/) | **Axioma Sentinel** | $G_2$ | `8092` | Autonomous Infrastructure & Daemon Health Sentinel safeguarding multi-process health and Landauer dissipation. | `L1-G2-001`, `L1-G2-002`, `L1-G2-003`, `L1-G2-004`, `L1-008` |
| [`axioma_fabric`](file:///Users/michaellipski/dev/meta-axioma/apps/axioma_fabric/) | **Axioma Fabric** | $G_2$ | `8443` | High-throughput distributed Sheaf-CRDT event streaming and coordination fabric with Landauer ring buffers, zero-ambient HMAC capability tokens, and real-time operations dashboard. | `L1-G2-001`, `L1-G2-002`, `L1-G2-003`, `L1-G2-004`, `L1-G2-008`, `L1-008`, `L1-017` |
| [`axioma_mesh`](file:///Users/michaellipski/dev/meta-axioma/apps/axioma_mesh/) | **Axioma Mesh** | $G_3$ | `8200` | General Distributed Systems & Complex Backend Orchestrator with sheaf consensus, zero-trust delegation, CQRS rollbacks, and enclave healing. | `L1-G3-001`, `L1-G3-002`, `L1-G3-003`, `L1-G3-004`, `L1-G3-005`, `L1-G3-006`, `L1-008` |

---

## 4. Running Any Application
Every standardized application is fully self-contained using the local Python 3.14 standard library (zero external packages or paid APIs):

```bash
# Example: Launch Axioma Flow (Kanban Workspace)
python3 apps/axioma_flow/run.py

# Example: Launch Axioma Lexis (Android Vocabulary & Spaced Repetition)
python3 apps/axioma_lexis/run.py

# Example: Launch Axioma Dual FSM (Zero-Trust AI Governance Kernel)
python3 apps/axioma_dual_fsm/run.py
```
Then visit `http://localhost:<port>` in your web browser, or on mobile visit `http://<LAN_IP>:<port>`.
