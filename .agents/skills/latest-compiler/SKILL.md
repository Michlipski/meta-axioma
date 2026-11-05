---
name: latest-compiler
description: >-
  Autonomous end-to-end application compiler using the latest generation service mesh
  (Generation 4b: Research, Builder, Audit, Telemetry, Governance). Use when the user
  wants to compile, build, synthesize, or architect an external production application into `apps/<app_name>/`.
---

# Mode 3: Latest Compiler (`/latest-compiler`)

The `/latest-compiler` mode orchestrates the full **Generation 4b Sovereign Service Mesh** (`services/research/`, `services/builder/`, `services/audit/`, `services/telemetry/`, `services/governance/`) to synthesize, verify, and seal an external production application into `apps/<app_name>/`.

---

## 1. Mandatory Pre-Execution Governance Gate (Directive 3 & `[NEG-GOV-GATE-001]`)

> [!CRITICAL]
> **Zero Code Modifications Before Approval:** Autonomous agents are strictly barred from writing or modifying any application or generation source code before emitting `project_proposals.md` and obtaining explicit human approval via `ask_question`. Direct tool calls to `edit_file` or `write_file` are intercepted and blocked at runtime by `scripts/governance_pre_tool_guard.py`.

### Step 1.1: Emit Detailed Proposals Document (`write_to_file`)
Before any application files are written, formulate a rigorous plan and write `<appDataDir>/brain/<conversation-id>/project_proposals.md` containing:
1. **Section 1 — High-Level Plan & Waterloo Tier 1 Situation of Concern (`[L1-G3B-000]`):**
   - Macro/Meso/Micro hierarchy, actors, frictions, constraints, unmet needs, Target $P_1$ persona, daily workflow, and UX ergonomics.
2. **Section 2 — Comparative Summary Matrix:**
   - Table of proposed options, unified BPE token budgets, 60% Exploratory / 40% Protected capital, predicted spend (`DynamicBudgetCalibrator.estimate_from_structural_scope()`), structural graph counts, and statechart complexity.
3. **Section 3 — Exhaustive Per-Option Engineering Specifications:**
   - Target Persona & JTBD Fit
   - Token Budget & Itemized Workload Breakdown
   - Statechart & Verification Depth
   - Included Scope (including the mandatory **Development Process Telemetry Dashboard** — `telemetry_dashboard.html` / `dashboard.html`)
   - Deliberately Deferred / Cut Scope
   - Engineering & Budget Justification
   - Socratic Red Team Critique (`[L1-G4B-009]`, `[INV-G4B-REDTEAM-001]`)

### Step 1.2: Elicit Approval via `ask_question`
Link to `[project_proposals.md](file:///...)` in the chat and invoke `ask_question` to let the human architect select or steer the option.

---

## 2. 3-Phase Causal Reactive Pipeline (`[INV-G4B-CAUSAL-001..003]`)

Once the human architect approves the proposal, execute synthesis through the strictly sequential 3-Phase Causal Pipeline:

### Phase 1: Sovereign Brain / Research & Architecture Gate (Sequential)
1. Spawn the Brain subagent via `invoke_subagent` (`Role="Domain Ontologist & Contract Proof Engineer"` or `Role="Human Ergonomics & UX Architect"`; `Model="flash"` by default to conserve Argon quota unless `ENABLE_ARGON=True`).
2. Await its completion message.
3. Extract certified Waterloo SoC, formal domain contracts (`ContractIR`), statechart specifications (`StatechartIR`), and topology (`TopologyIR`).

### Phase 2A: Code Synthesizer Muscle (Sequential to Phase 1 — `Model="flash"`)
1. Spawn `CognitiveRole.CORE_ENGINE_SYNTHESIZER` via `invoke_subagent`.
2. Inject Phase 1's certified architectural specifications into the prompt.
3. Synthesize all application modules directly into `apps/<app_name>/` (`engine.py`, `server.py`, `persistence.py`, `schemas/`, `index.html`, `style.css`, `app.js`).

### Phase 2B: Physical Disk Grounding Witness Gate (`[INV-G4B-CAUSAL-001]`)
1. Inspect the disk substrate: verify `file_exists == True` for 100% of declared application manifest files.
2. Verify `byte_size > 0` (strictly non-empty; anti-zero-byte invariant).
3. Compute and record SHA-256 digests for every emitted file.
4. If any file is missing or empty, raise a fatal `PhantomEmissionViolation` (`[NEG-G1B-001]`) and halt immediately.

### Phase 2C: Reactive Verification & Byzantine QA Muscle (Post-Phase 2B — `Model="flash"`)
1. Spawn `CognitiveRole.ADVERSARIAL_QA_ENGINEER` to execute the empirical test suite and the **Anti-Mock Subprocess Entrypoint Smoke Test (`[NEG-G1B-002]`)**:
   - The test must launch the entrypoint script in an independent OS subprocess (`subprocess.Popen(["python3", entrypoint_path, ...])`).
   - Assert zero startup crashes (no missing relative imports or syntax errors).
   - Assert operational liveness (service binds operational port, responds to healthcheck).
   - Assert clean teardown upon `SIGTERM` / `SIGINT`.
2. Spawn `CognitiveRole.OPERATIONAL_DASHBOARD_SYNTHESIZER` to compile the standalone development process telemetry dashboard (`dashboard.html` / `telemetry_dashboard.html`).

### Phase 2D: Reactive Mesh Leaf Convergence Gate (`[INV-G4B-CAUSAL-003]`)
- Verify that leaf execution witnesses, micro-audits, and empirical tests verified the exact physical SHA-256 digests recorded in Phase 2B.

### Phase 3: Merkle Attestation & Quine Crucible Certification (`[L1-G4B-003]`)
- Aggregate subagent execution witnesses into a cryptographic Merkle root hash.
- Seal `telemetry_ledger.json` and `telemetry_dashboard.html` into `generations/gen_04b/epochs/<epoch_name>/`.
