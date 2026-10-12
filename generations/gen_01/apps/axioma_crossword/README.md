# Axioma Crossword (`axioma_crossword`)

> **Zero-Dependency Distributed Cryptic Crossword Engine & Asynchronous Constraint Studio**  
> *Compiled by System G1 under Invariants [L1-004], [L1-015_1], [L1-008], [L1-002], [L1-011_3], and [L1-016]*

---

## 1. System Overview

Axioma Crossword is a globally scalable cruciverbalist solving and construction application:
- **Port:** `8094`
- **Target Persona:** Cruciverbalist Solver & Puzzle Architect
- **Multi-Device Responsiveness:** 2-column desktop workbench, tablet split layout, and mobile touch interface with custom 26-letter soft keypad.
- **Client-Side Optimistic Execution:** Zero-latency keystrokes with asynchronous delta sync (`L1-002`, `L1-011_3`).
- **Cryptic Anatomy Dissector:** Universal Grammar AST parse tree (`L1-004`) separating `[DEFINITION]`, `[INDICATOR]`, and `[FODDER]`.
- **Decoupled Asynchronous CSP Synthesizer:** AC-3 backtracking solver offloaded to isolated background worker threads (`L1-015_1`).
- **Landauer Thermodynamic Accounting:** Audits information erasure bits and dissipated thermal energy ($\Delta S = k_B \ln |D_i|$) during backtracking search (`L1-008`).

---

## 2. Quickstart

### Launch Server
```bash
python3 apps/axioma_crossword/run.py
```
Open **http://localhost:8094** in your browser.

### Run Test Suite
```bash
python3 -m unittest -v generations/gen_01/apps/axioma_crossword/tests/test_app.py
```

---

## 3. Structural Axioms Embodied

| Axiom ID | Formal Principle | Embodied Mechanism |
| :--- | :--- | :--- |
| **`L1-004`** | Universal Grammar Projection | Cryptic Clue AST decomposes surface text into Definition, Indicator, and Fodder tokens with verifiable wordplay semantics. |
| **`L1-015_1`** | Compositional Boundary Isolation | CPU-bound AC-3 CSP puzzle synthesis is decoupled into background worker pools (`worker_pool.py`), keeping web I/O non-blocking. |
| **`L1-008`** | Landauer Limits & Physical Decay | Backtracked search branches erase information, logging Landauer dissipated heat ($k_B T \ln 2$) with strict execution leases. |
| **`L1-002`** | Functorial State Reversibility | Local solver mutations form a reversible event log supporting instant `Cmd+Z` undo/redo and multi-device delta merging. |
| **`L1-011_3`** | Decoupled Persistence | Partitioned session documents (`data/sessions/`) and immutable puzzles (`data/puzzles/`) with optimistic concurrency control. |
| **`L1-016`** | Demarcated Exception Enclaves | Request handlers and synthesis workers execute inside fault-isolated enclaves, preventing global crashes. |

---

## 4. API Endpoints

- `GET /api/puzzles` — List available crossword puzzles.
- `GET /api/puzzles/{puzzle_id}` — Get immutable puzzle grid and clue ASTs (Edge-cacheable).
- `GET /api/sessions/{session_id}` — Get or initialize a solver session.
- `POST /api/sessions/{session_id}/delta` — Optimistic cell change mutation.
- `POST /api/jobs/synthesize` — Enqueue asynchronous AC-3 CSP puzzle synthesis (`202 Accepted`).
- `GET /api/jobs/{job_id}` — Poll worker progress, backtracks, and Landauer dissipation.
- `POST /api/feedback` — Submit user critique into the transgenerational learning stream.
- `GET /api/telemetry` — Retrieve aggregate performance and thermal dissipation metrics.
