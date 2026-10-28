# Meta-Axioma Standardized Applications Registry (`/apps`)

This directory serves as the canonical registry and top-level index of all **non-generator software applications** compiled across the Meta-Axioma generational lineage ($G_1, G_2, \dots$).

> 📋 **Systems Portfolio & Feedback Ledger:** See [`SYSTEMS_PORTFOLIO.md`](../SYSTEMS_PORTFOLIO.md) for the active 6-system testing portfolio, post-mortems, and the Active Feedback Elicitation Protocol.

---

## 1. The High-Level Jettison Telos
The recursive bootstrapping of compilers is not an insular closed circuit. Its ultimate purpose is **The High-Level Jettison**: producing robust, delightful, and human-controllable production software applications that people genuinely love and find useful (Target $P_1$ Ergonomics).

All applications in this registry are compiled from formal specifications using the structural invariants discovered and proven by the compiler lineage.

---

## 2. Standardized Application Anatomy
Every application inside `/apps/<app_id>/` (and canonically located at `generations/gen_XX/apps/<app_id>/`) strictly adheres to [`trace/domains/app_specification.domain.md`](../trace/domains/app_specification.domain.md):

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
| [`axioma_flow`](axioma_flow/) | **Axioma Flow** | $G_1$ | `8088` | Invariant-bounded, Landauer-audited Kanban & Task workspace with functorial undo/redo and exception enclaves. | `L1-002`, `L1-004`, `L1-011_3`, `L1-008`, `L1-015`, `L1-016`, `L1-015_1` |
| [`axioma_lexis`](axioma_lexis/) | **Axioma Lexis** | $G_{2b}$ | `8090` | Fast, distraction-free, local-first vocabulary studio with auto-hydrated definitions, Web Speech audio, adaptive SM-2 SRS, and 1-tap reversible undo. | `L1-G2B-001`, `L1-G2B-002`, `NEG-G1B-001`, `L1-002`, `L1-004`, `L1-011_3` |
| [`axioma_dual_fsm`](axioma_dual_fsm/) | **Axioma Dual FSM** | $G_1$ | `8092` | Zero-trust AI runtime governance kernel gating LLMs through coupled dual FSMs, tool failure loops, and de-escalation. | `L1-002`, `L1-004`, `L1-011_3`, `L1-008`, `L1-015`, `L1-016`, `L1-015_1` |
| [`axioma_crossword`](axioma_crossword/) | **Axioma Crossword** | $G_{1b}$ | `8094` | Cryptic crossword solving studio with 2-column solver workbench, soft mobile keypad, Clue Anatomy Dissector, and symmetrical grid solver. | `L1-G1B-001`, `L1-G1B-002`, `NEG-G1B-001`, `L1-002`, `L1-004`, `L1-011_3` |
| [`axioma_eink`](axioma_eink/) | **Axioma E-Ink** | $G_1$ | `8096` | Asynchronous Task Router & Ambient Electrophoretic Glanceboard for Kindle/Kobo with strict zero-JS, 15m meta-refresh, and Daily Big 3–5 focus bounding. | `L1-002`, `L1-004`, `L1-011_3`, `L1-008`, `L1-015`, `L1-016`, `L1-015_1` |
| [`axioma_swarm`](axioma_swarm/) | **Axioma Swarm** | $G_1$ | `8098` | Local LLM Edge Orchestrator & Micro-Swarm Daemon coordinating quantized model VRAM lifecycles, LRU eviction, and OOM-isolated task dispatch. | `L1-008`, `L1-016`, `L1-015`, `L1-002`, `L1-011_3`, `L1-015_1` |
| [`axioma_sentinel`](axioma_sentinel/) | **Axioma Sentinel** | $G_2$ | `8092` | Autonomous Infrastructure & Daemon Health Sentinel safeguarding multi-process health and Landauer dissipation. | `L1-G2-001`, `L1-G2-002`, `L1-G2-003`, `L1-G2-004`, `L1-008` |
| [`axioma_fabric`](axioma_fabric/) | **Axioma Fabric** | $G_2$ | `8443` | High-throughput distributed Sheaf-CRDT event streaming and coordination fabric with Landauer ring buffers, zero-ambient HMAC capability tokens, and real-time operations dashboard. | `L1-G2-001`, `L1-G2-002`, `L1-G2-003`, `L1-G2-004`, `L1-G2-008`, `L1-008`, `L1-017` |
| [`axioma_mesh`](axioma_mesh/) | **Axioma Mesh** | $G_3$ | `8200` | General Distributed Systems & Complex Backend Orchestrator with sheaf consensus, zero-trust delegation, CQRS rollbacks, and enclave healing. | `L1-G3-001`, `L1-G3-002`, `L1-G3-003`, `L1-G3-004`, `L1-G3-005`, `L1-G3-006`, `L1-008` |
| [`axioma_airscratch`](axioma_airscratch/) | **Axioma AirScratch** | $G_{3b}$ | `8095` | Asynchronous Device-to-Device Scratchpad & File Drop (Mac ↔ Android) with Sheaf-CRDT ring buffer, pure Python QR pairing, mobile camera direct-drop, and 1-tap Functorial Undo. | `L1-G3B-000`, `L1-G3B-001`, `L1-G3B-003`, `L1-G3B-005`, `L1-G3B-006`, `L1-002`, `L1-011_3`, `NEG-G1B-001` |
| [`axioma_elenchus`](axioma_elenchus/) | **Axioma Elenchus** | $G_{3b}$ | `8097` | Socratic Epistemic Curiosity & Category Theory Studio (`soc_epistemic_curiosity_engine`) with 18-node Deep-History XState v5 Statechart, Compositional Prerequisite Contracts (`Mastery of Morphisms` guarding `Exploring Functors`), Local RTX 4060 (`192.168.10.40:11434`) Ollama `qwen2.5` inference ($\le 25\text{ms}$) + `[L1-016]` Lakatosian Exception Enclave, and Reflexive Quine Daughter Crucible certification. | `L1-G3B-000`, `L1-G3B-011`, `L1-G3B-012`, `L1-G3B-013`, `L1-G3B-014`, `L1-G3B-015`, `L1-G3B-016`, `L1-G3B-017`, `L1-002`, `L1-012`, `L1-016`, `NEG-G1B-001` |
| [`axioma_cancrizans`](axioma_cancrizans/) | **Axioma Cancrizans** | $G_{3b}$ | `8099` | Interactive Euclidean Polyrhythm & Topological Canon Studio (`soc_euclidean_canon_studio`) uniting Bjorklund's maximal evenness algorithm $E(k, n, \rho)$ and Godfried Toussaint's polygon/deep-rhythm geometry with Bach's Crab Canon (`CANCRIZANS`), Mirror Inversion (`SPIEGELKANON`), non-orientable Möbius Strip (`MOEBIUS_TABLE`), Artin braid consonance solver, 18-node Deep-History XState v5 Statechart with Functorial Undo, 4-timbre WebAudio synth, and Reflexive Quine Daughter Crucible certification. | `L1-G3B-000`, `L1-G3B-009`, `L1-G3B-011`, `L1-G3B-012`, `L1-G3B-013`, `L1-G3B-014`, `L1-G3B-015`, `L1-G3B-016`, `L1-G3B-017`, `L1-002`, `L1-011_3`, `L1-016`, `NEG-G1B-001` |
| [`axioma_kinetic_facade`](axioma_kinetic_facade/) | **Axioma Kinetic Façade** | $G_{3b}$ | `8101` | Decentralized Byzantine Fault-Tolerant Kinetic Louver Mesh (`soc_byzantine_kinetic_facade`) uniting 9 P2P actuator nodes across 12 cardinal gossip channels (`10.99.10.x`), 3-phase pBFT supermajority ($\ge 2/3$) consensus invariant, 18-state Hierarchical XState v5 Statechart, Orderly Calibrated Unwind Recovery Pipeline, 2D SVG diagnostic dashboard, and Reflexive Quine Daughter Crucible certification. | `L1-G3B-000`, `L1-G3B-011`, `L1-G3B-012`, `L1-G3B-013`, `L1-G3B-014`, `L1-G3B-015`, `L1-G3B-016`, `L1-G3B-017`, `L1-002`, `L1-011_3`, `L1-012`, `L1-016`, `NEG-G1B-001` |
| [`axioma_evolution_dashboard`](axioma_evolution_dashboard/) | **Axioma Evolution Dashboard** | $G_{3b}$ | `8105` | Architectural Evolution Studio & Topology Workbench mapping the entire 7-stage Meta-Axioma lineage ($S_0 \to G_1 \to G_2 \to G_3 \to G_{1b} \to G_{2b} \to G_{3b}$) with pinned G3b zenith architecture HUD, Beehive-inspired 4-tier SVG topology canvas, side-by-side comparative diffing, 6 transformation nodes, 6-subsystem component drill-down, and Michael Lipski's foundational epistemic contributions. | `L1-G3B-000`, `L1-G3B-011`, `L1-G3B-012`, `L1-G3B-013`, `L1-G3B-014`, `L1-G3B-015`, `L1-G3B-016`, `L1-G3B-018`, `L1-002`, `NEG-G1B-001` |
| [`axioma_heliotrope`](axioma_heliotrope/) | **Axioma Heliotrope** | $G_{3b}$ | `8080` | Heliotropic Microclimate & Solar Shadow Choreographer Studio (`soc_heliotropic_microclimate_studio`) with pure-Python NOAA solar ephemeris, 3D polygon shadow extrusion across 600-cell ($30\text{m} \times 20\text{m}$) parcel grid, cumulative insolation integration, microclimate asset qualification (Raised Bed, Gazebo, Tanning Deck), 1-tap Functorial Undo, and live compiler Development Process Telemetry Dashboard. | `L1-G3B-000`, `L1-G3B-011`, `L1-G3B-012`, `L1-G3B-013`, `L1-G3B-014`, `L1-G3B-015`, `L1-G3B-016`, `L1-G3B-017`, `L1-G3B-018`, `L1-002`, `L1-016`, `NEG-G1B-001` |
| [`axioma_go`](axioma_go/) | **Axioma Go** | $G_{4b}$ | `8082` | Tactical Go Dojo favoring depth over breadth on a 10x10 grid (A1-K10) with 6 automated capturing showcases (Snapback, Ladder, Geta, Crane's Nest, Double Atari, Under the Stones), interactive "Fork & Play" branching, dynamic liberty heatmap, pulsing atari threat halos, and 1-tap Functorial Undo. | `L1-G4B-001`, `L1-G4B-002`, `L1-G4B-003`, `L1-G4B-004`, `L1-G4B-005`, `L1-G4B-008`, `L1-G3B-000`, `L1-G3B-011`, `L1-G3B-018`, `L1-002`, `L1-016`, `NEG-G1B-001` |
| [`axioma_consensus`](axioma_consensus/) | **Axioma Consensus** | $G_{4b}$ | `8083` | Sovereign Multi-Node Byzantine Gossip & Causal Consensus Cluster Node synchronizing distributed vector clocks, reconciling conflicted state via pure state-based CRDTs across dedicated non-loopback network topologies (`192.168.40.0/24`), negotiating protocol adjustments via the Asymmetric RFC Bus with formal Z3 SMT CounterProofs, and executing 2-of-3 Sheaf-Quorum adversarial auditing. | `L1-G4B-001`, `L1-G4B-002`, `L1-G4B-003`, `L1-G4B-004`, `L1-G4B-008`, `L1-G4B-009`, `L1-G3B-000`, `L1-G3B-011`, `L1-G3B-012`, `L1-G3B-018`, `L1-002`, `L1-016`, `NEG-G1B-001`, `NEG-PRIMITIVE-001` |
| [`soc_g4b_researcher`](soc_g4b_researcher/) | **Axioma G4b Sovereign Researcher** | $G_{4b\text{-Init}}$ | `8440` | Sovereign Decoupled Epistemic Research Engine & Universal Crucible (`soc_g4b_researcher`), canonical at `generations/gen_04b/services/research/`, with 18 algebraic domain nouns, 32-state hierarchical XState v5 statechart, 5-tier anti-bias novelty engine (zero-context islands, Weisfeiler-Lehman graph taboo distance $D \ge 0.40$, dialectical inversion `NEG_PRIMITIVE`, 5D Pareto frontier, Lehman & Stanley novelty metric), Z3 SMT prover bridge, asymmetric RFC bus, and standalone Development Process Telemetry Dashboard deliverable (`[L1-G3B-018]`). | `L1-G3B-000`, `L1-G3B-011`, `L1-G3B-012`, `L1-G3B-013`, `L1-G3B-014`, `L1-G3B-015`, `L1-G3B-016`, `L1-G3B-017`, `L1-G3B-018`, `L1-002`, `L1-016`, `NEG-G1B-001` |
| [`soc_g4b_builder`](soc_g4b_builder/) | **Axioma G4b Sovereign Builder** | $G_{4b\text{-Dev}}$ | `8442` | Sovereign Autonomous Builder Enclave & Quine Crucible (`soc_g4b_builder`), located at `generations/gen_04b/services/builder/`, with 16 algebraic domain nouns, 28-state hierarchical XState v5 statechart, bounded fractal subagent tree ($d \le 4, b \le 5$, $\lambda \le 0.80$, $C_{\min} = 1,024$), 4-layer AST compiler substrate (Tree-sitter skeletonization $\le 4,096$ tokens, typed diagnostic tuples, compile-time hermetic linters, Universal Symbol URN hypergraph), and standalone Development Process Telemetry Dashboard deliverable (`[L1-G3B-018]`). | `L1-G3B-000`, `L1-G3B-011`, `L1-G3B-012`, `L1-G3B-014`, `L1-G3B-016`, `L1-G3B-017`, `L1-G3B-018`, `L1-G4B-001`, `L1-G4B-002`, `L1-G4B-003`, `L1-002`, `L1-016`, `NEG-G1B-001` |
| [`soc_g4b_audit`](soc_g4b_audit/) | **Axioma G4b Sovereign Audit** | $G_{4b\text{-Audit}}$ | `8444` | Sovereign Audit & Formal Verification Service (`soc_g4b_audit`), located at `generations/gen_04b/services/audit/`, with 16 algebraic domain nouns, 30-state hierarchical XState v5 statechart, Zero-Trust AST Micro-Auditor (`HERM-001..004`), SMT formal model checker (Native SMT + Z3), Byzantine chaos fuzzer (6 vector types, 100% trapped), 2-of-3 non-blocking Sheaf-Quorum consensus, SHA-256 Merkle DAG witness anchoring, and standalone Development Process Telemetry Dashboard deliverable (`[L1-G3B-018]`). | `L1-G3B-000`, `L1-G3B-011`, `L1-G3B-012`, `L1-G3B-016`, `L1-G3B-017`, `L1-G3B-018`, `L1-G4B-001`, `L1-G4B-003`, `L1-002`, `L1-016`, `NEG-G1B-001`, `NEG-PRIMITIVE-001` |
| [`soc_g4b_telemetry`](soc_g4b_telemetry/) | **Axioma G4b Sovereign Telemetry** | $G_{4b\text{-Telemetry}}$ | `8446` | Sovereign Telemetry & Evaluation Service (`soc_g4b_telemetry`), canonical at `generations/gen_04b/services/telemetry/`, with 18 algebraic domain models, 30-state hierarchical XState v5 statechart, real-time Landauer heat calculation ($Q = k_B T \ln 2 \cdot \text{bits}$), empirical cluster SLA benchmark evaluation ($P_{50}, P_{90}, P_{99}$, availability, throughput), multi-source ingestion from Phases 1-3, 1-tap Functorial Undo bit recovery, and standalone zero-CDN Development Process Telemetry Dashboard (`[L1-G3B-018]`). | `L1-G3B-000`, `L1-G3B-011`, `L1-G3B-012`, `L1-G3B-014`, `L1-G3B-016`, `L1-G3B-017`, `L1-G3B-018`, `L1-G4B-001`, `L1-G4B-003`, `L1-G4B-008`, `L1-002`, `L1-016`, `NEG-G1B-001` |
| [`soc_g4b_governance`](soc_g4b_governance/) | **Axioma G4b Sovereign Governance** | $G_{4b\text{-Governance}}$ | `8448` | Sovereign Governance & Safety Service (`soc_g4b_governance`), canonical at `generations/gen_04b/services/governance/`, with 16 algebraic domain models, 30-state hierarchical XState v5 statechart, real-time negative axiom AST & semantic interception (`NEG-001..NEG-999`), stateful Human-in-the-Loop Intercept Hub with Heuristic Debt Ratio monitoring ($\text{HDR} \le 0.15$), asymmetric mesh RFC adjudication with formal SMT `CounterProof` emission, tri-state cluster safety enclaves & selective peer quarantine (`192.168.40.240/28`), Generation 5 succession gatekeeper with cryptographic handover certification, 1-tap Functorial Undo categorical rollback ($S_{t-1} = f^{-1}(S_t)$), and standalone zero-CDN Development Process Telemetry Dashboard deliverable (`[L1-G3B-018]`). | `L1-G3B-000`, `L1-G3B-011`, `L1-G3B-012`, `L1-G3B-014`, `L1-G3B-016`, `L1-G3B-017`, `L1-G3B-018`, `L1-G4B-001`, `L1-G4B-003`, `L1-G4B-008`, `L1-002`, `L1-016`, `NEG-G1B-001`, `NEG-PRIMITIVE-001` |

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
