---
flow: CruciverbalistSolvingAndSynthesisWorkflow
persona: CruciverbalistSolverAndArchitect
domains:
  - AxiomaCrossword
  - AppSpecification
  - GenerationalFeedback
---

# WORKFLOW: Multi-Device Solving, Clue Dissection & Constraint Synthesis

> GOAL: Deliver an edge-optimized cruciverbalist experience spanning desktop, tablet, and mobile, coupled with an asynchronous AC-3 CSP puzzle synthesis studio.

---

## FLOW 1: Multi-Device Solving & Optimistic Local Keystrokes
1. Solver opens a puzzle on desktop or mobile device.
2. Grid renders instantaneously from local cache or CDN edge.
3. User navigates grid via keyboard (Arrow keys, Space/Tab to toggle Across/Down) or mobile touch keypad.
4. User enters a letter:
   - Client updates active cell immediately (0ms latency).
   - In-memory event vector appends forward mutation `M(S_t) -> S_{t+1}` for functorial undo (`L1-002`).
   - Active clue updates to reflect intersecting across/down position.
5. In the background, client batches mutations and flushes to `PATCH /api/sessions/{session_id}` every 5 seconds.

---

## FLOW 2: Cryptic Clue Anatomy Dissection
1. Solver taps or selects a perplexing cryptic clue (e.g., *"Carthorse ordered in musical arrangement (9)"*).
2. Solver toggles the **Cryptic Dissector** tab / slide-up sheet.
3. Clue engine projects the clue AST into color-coded tokens:
   - `[FODDER: Carthorse]`
   - `[INDICATOR: ordered (Anagram Indicator)]`
   - `[DEFINITION: musical arrangement]`
4. System details wordplay mechanism: Anagram of `CARTHORSE` equates to `ORCHESTRA`.
5. Solver gains deep cruciverbalist insight without feeling cheated by an unexplained answer key.

---

## FLOW 3: Decoupled Asynchronous CSP Grid Synthesis
1. Puzzle architect opens the **Constructor Studio** tab.
2. Selects target grid dimensions (7x7 Quick or 9x9 Midi) and clicks "Synthesize New Grid (AC-3)".
3. Web tier issues `POST /api/jobs/synthesize` and returns `202 Accepted` with a unique `job_id`.
4. Asynchronous worker thread/process picks up the job, executing AC-3 forward checking and MRV backtracking.
5. Client polls `GET /api/jobs/{job_id}`, updating progress bar, backtracks count, and Landauer dissipation meters.
6. Upon completion (`200 OK`), the newly synthesized grid is automatically loaded into the studio with verified clue ASTs.

---

## FLOW 4: Landauer Thermodynamic Search Dissipation Audit
1. During or after CSP grid synthesis, user reviews the **Landauer Ledger Ribbon**.
2. For each discarded candidate word, bit erasure is audited:
   - `ΔS = k_B * ln(|D_i|)`
   - Dissipated heat `Q = TotalDiscards * k_B * T * ln(2)`
3. UI compares the entropy dissipated by intelligent AC-3 arc pruning vs. naive brute-force combinatorial search.

---

## FLOW 5: Functorial Reversibility & In-App Generational Feedback
1. Solver uses `Cmd+Z` / Undo button to roll back erroneous letters cleanly.
2. If solver encounters an awkward clue or layout friction, taps `💬 Feedback` in the header.
3. Submits feedback payload (`POST /api/feedback`), logging directly to `generations/gen_01/feedback/feedback.json` for successor compiler ingestion into Generation G2.
