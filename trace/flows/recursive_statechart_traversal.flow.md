---
flow: RecursiveStatechartTraversalFlow
persona: QAEngineer
domains:
  - RecursiveFlowWalker
  - AppSpecification
  - TelemetryAudit
---

# WORKFLOW: Recursive Statechart Traversal & Headless Journey Execution

> GOAL: Guide the autonomous compiler and audit service through ingesting recursive XState v5 statecharts, synthesizing minimal compositional covering tours across nested micro-flows, solving SMT guard preambles, and executing the complete path traversal against a live application subprocess.

---

## STEP 1: Recursive Statechart IR Ingestion & Validation
- The audit service ingests the canonical `StatechartIR` AST.
- `FormalModelChecker` validates structural integrity:
  - Verifies reachability from root initial state.
  - Checks for orphaned substates, dangling transition targets, or parallel region context write collisions.
  - Emits `ModelCheckingReport`. If defects are found, compilation halts immediately.

## STEP 2: Recursive Flow Graph (RFG) Decomposition & Port Contracting
- `FlowParser` identifies all macro-nodes ($\tau \in \{\text{compound}, \text{parallel}\}$).
- Establishes modular entry ports ($En_M$) and exit ports ($Ex_M$) for each nested sub-statechart $G_{micro}(M)$.
- Verifies that cross-boundary transitions cleanly map to explicit port contracts without illegal hierarchy jumps.

## STEP 3: Compositional Hierarchical Covering Tour Synthesis
- Executes Algorithm 1 (`HierarchicalCoveringPath`):
  - Solves intra-modular Chinese Postman / Eulerian tours for each child compound node.
  - Projects orthogonal parallel regions independently to synthesize synchronized concurrent sub-tours without Cartesian state explosion.
  - Replaces macro-nodes in the parent graph with contracted transfer contracts ($\mathcal{T}_M: En_M \xrightarrow{\pi_M} Ex_M$).
  - Assembles the global sequence of `JourneyStep` records achieving 100% transition coverage.

## STEP 4: SMT Guard Preamble Solving & Path Feasibility Assertion
- For every transition carrying a guard predicate $g(context, event)$:
  - Pipes the guard condition and accumulated context valuation through the Z3 SMT bridge (`crucible_smt_check`).
  - If $\neg g(\mathbf{x}_{curr})$, synthesizes the backward Weakest Precondition preamble $\pi_{pre}$ and splices it before the target transition.
  - Traps and reports mathematically infeasible transitions as dead code.

## STEP 5: Live Subprocess Empirical Journey Walk
- `HeadlessUIJourneyWalker` boots the target application entrypoint (`apps/<app_id>/run.py`) on an ephemeral dynamically allocated port in an OS subprocess (`[NEG-G1B-002]`).
- Dynamically dispatches each `JourneyStep` via HTTP/IPC and simulated DOM interaction based on `target_selector` and `event_name` (with zero hardcoded app logic).
- Verifies:
  - Observable external state delta ($\Delta S \ne 0$) within `max_latency_ms`.
  - The 4 Universal Human Ergonomics Axioms (zero console errors, viewport bounding box containment, sensory feedback, non-occlusion).
  - 1-tap Functorial Undo reversal at designated rollback checkpoints.

## STEP 6: Teardown, Merkle Attestation & Telemetry Commit
- Shuts down the subprocess cleanly with `SIGTERM` / `SIGINT` (verifying exit code 0).
- Computes the deterministic SHA-256 attestation digest for `JourneyReport`.
- Seals the verification witness into `telemetry_ledger.json` and updates `telemetry_dashboard.html`.
