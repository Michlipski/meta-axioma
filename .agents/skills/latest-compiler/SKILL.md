---
name: latest-compiler
description: >-
  Autonomous end-to-end application compiler using the latest generation service mesh
  (Generation 4b: Research, Builder, Audit, Telemetry, Governance). Use when the user
  wants to compile, build, synthesize, or architect an external production application into `apps/<app_name>/`.
---

# Mode 3: Latest Compiler (`/latest-compiler`)

The `/latest-compiler` mode orchestrates the full **Generation 4b Sovereign Service Mesh** (`services/research/`, `services/builder/`, `services/audit/`, `services/telemetry/`, `services/governance/`) via **`SystemG4bCompiler`** (`generations/gen_04b/compiler/orchestrator.py`) to synthesize, verify, and seal an external production application into `apps/<app_name>/`.

---

## 0. Mandatory `SystemG4bCompiler` Execution Routing (Zero Mesh Bypass)

- **Always execute `/latest-compiler` builds through `SystemG4bCompiler` (`generations/gen_04b/compiler/`):** Do NOT synthesize Gen 4b apps with ad-hoc procedural scripts that bypass the 5-service mesh or emit mock telemetry.
- **Live Subagents Opt-Out Default:** Live AGY subagent orchestration (`invoke_subagent` across Phase 1 Brain, Phase 2A Muscle, Phase 2C Blind QA, and Phase 3 Red Team) is **required by default** (`CompilationRequest.require_live_subagents = True`). Single-agent / offline scaffold execution is **opt-out only** (pass `require_live_subagents=False` programmatically or `--no-live-subagents` on the CLI, only when explicitly requested).
- **Programmatic Compilation (default live subagents):**
  ```python
  from generations.gen_04b.compiler import CompilationRequest, SystemG4bCompiler
  from generations.gen_04b.protocols.ipc_transport import TransportMode

  compiler = SystemG4bCompiler(transport_mode=TransportMode.LOCAL_IPC)
  report = compiler.compile(
      CompilationRequest(
          app_id="<app_id>",
          app_name="<App Name>",
          target_output_dir="apps/<app_name>",
          waterloo_soc_prompt=prompt,
          subagent_invoker=live_subagent_invoker,
          # require_live_subagents=True by default (opt out via False)
          # strict_prover=True to fail closed unless z3-solver is installed
      ),
  )
  ```
- **CLI Entrypoint (`python3 -m generations.gen_04b.compiler` / `axioma-g4b`):**
  - Default `compile` enforces `require_live_subagents=True` and fails closed when no live subagent invoker is attached.
  - Explicit opt-out for deterministic scaffold / smoke runs: `python3 -m generations.gen_04b.compiler compile --app-id <app_id> --app-name "<App Name>" --prompt "<SoC>" --output-dir apps/<app_name> --no-live-subagents --transport-mode local_ipc`.
  - Pass `--strict-prover` when `z3-solver` (`pip install -e ".[formal]"`) is required to fail closed rather than running in `BOUNDED_STDLIB` mode.

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

### Phase 1: Sovereign Brain / Research & Architecture Gate (Sequential — `Model="pro"`, Gemini 4 Neon)
1. Spawn the Brain subagent via `invoke_subagent` (`Role="Domain Ontologist & Contract Proof Engineer"` or `Role="Human Ergonomics & UX Architect"`; always-on **Gemini 4 Neon** via `Model="pro"` with zero `ENABLE_ARGON` feature flag, per `generations/gen_04b/protocols/cognitive_routing.py`).
2. Await its completion message.
3. Extract certified Waterloo SoC, formal domain contracts (`ContractIR`), statechart specifications (`StatechartIR`), and topology (`TopologyIR`).

### Phase 2A: Code Synthesizer Muscle (Sequential to Phase 1 — `Model="flash"`, Gemini 4 Hydrogen)
1. Spawn `CognitiveRole.CORE_ENGINE_SYNTHESIZER` via `invoke_subagent` (`Model="flash"`, **Gemini 4 Hydrogen**).
2. Inject Phase 1's certified architectural specifications into the prompt.
3. Synthesize all application modules directly into `apps/<app_name>/` (`engine.py`, `server.py`, `persistence.py`, `schemas/`, `index.html`, `style.css`, `app.js`).

### Phase 2B: Physical Disk Grounding Witness Gate (`[INV-G4B-CAUSAL-001]`)
1. Inspect the disk substrate: verify `file_exists == True` for 100% of declared application manifest files.
2. Verify `byte_size > 0` (strictly non-empty; anti-zero-byte invariant).
3. Compute and record SHA-256 digests for every emitted file.
4. If any file is missing or empty, raise a fatal `PhantomEmissionViolation` (`[NEG-G1B-001]`) and halt immediately.

### Phase 2C: Reactive Verification & Byzantine QA Muscle (Post-Phase 2B — `Model="flash"`, Gemini 4 Hydrogen)
1. Spawn `CognitiveRole.ADVERSARIAL_QA_ENGINEER` (`Model="flash"`, **Gemini 4 Hydrogen**) to execute the empirical test suite and the **Anti-Mock Subprocess Entrypoint Smoke Test (`[NEG-G1B-002]`)**:
   - **[NEG-SANDBOX-001] Zero-Bypass Invariant:** All tests must run strictly inside standard sandbox mode (`BypassSandbox: false`). Never escalate to `BypassSandbox: true` (which triggers human permission modals).
   - **Hermetic HTTP Testing:** Because macOS sandbox blocks outbound localhost TCP (`connect(('127.0.0.1', ...))`), HTTP handler tests must use `socket.socketpair()` for zero-network HTTP verification.
   - **[NEG-PROC-001] Prohibition of Process Killing:** Never execute `kill -9`, `killall`, or `pkill` via shell commands. All test servers must bind to ephemeral port 0 (`socket.bind(('127.0.0.1', 0))`) or use `socket.socketpair()`. Teardown must be handled cleanly within Python via `proc.terminate()` or `proc.send_signal(signal.SIGINT/SIGTERM)`.
   - **[NEG-SHELL-002] Zero Shell Access to Sibling Brain Directories:** Never run shell commands (`tail`, `cat`, `grep`, `ls`) targeting sibling subagent directories (`~/.gemini/antigravity/brain/<subagent_id>/`). Use host tool `read_file` instead.
   - **[INV-PIPE-001] Mandatory Unbuffered Subprocess Execution:** All entrypoint startup banners must use `print(..., flush=True)`, and subprocess tests must launch Python unbuffered (`python3 -u ...` or `env={"PYTHONUNBUFFERED": "1"}`) to prevent pipe buffer deadlocks.
   - **Subprocess Smoke Test:** Launch the entrypoint script in an independent OS subprocess (`subprocess.Popen(["python3", "-u", entrypoint_path, ...])`).
     * Assert zero startup crashes (no missing relative imports or syntax errors).
     * Assert operational liveness via stdout startup confirmation banner within $\le 5\text{s}$.
     * Assert clean teardown upon `SIGTERM` / `SIGINT` (exit code 0 within $\le 2\text{s}$).
2. Spawn `CognitiveRole.OPERATIONAL_DASHBOARD_SYNTHESIZER` (`Model="flash"`, **Gemini 4 Hydrogen**) to compile the standalone development process telemetry dashboard (`dashboard.html` / `telemetry_dashboard.html`).

### Phase 2D: Reactive Mesh Leaf Convergence Gate (`[INV-G4B-CAUSAL-003]`)
- Verify that leaf execution witnesses, micro-audits, and empirical tests verified the exact physical SHA-256 digests recorded in Phase 2B.

### Phase 3: Audit Gate, Red Team (`Model="pro"`, Gemini 4 Neon), Merkle Attestation & Telemetry Certification (`[L1-G4B-003]`, `[L1-G4B-008]`)
- `SystemG4bCompiler` automatically runs `ZeroTrustMicroAuditor`, `AcceptanceGate`, and Dialectical Red Team critique (`SOCRATIC_RED_TEAM`, always-on **Gemini 4 Neon** via `Model="pro"`), commits mesh transactions into `.telemetry_vault.sqlite`, computes the SHA-256 Merkle root across phases, and seals `telemetry_ledger.json`, `telemetry_metrics.json`, `synthesis_manifest.json`, `dashboard.html`, and `telemetry_dashboard.html` in `target_output_dir` (and mirror artifacts into `generations/gen_04b/epochs/<epoch_name>/` when compiling an epoch).
- If live AGY subagent transcripts need post-compile token reconciliation, run `python3 scripts/reconcile_dashboard_telemetry.py --app <app_name> --main-cid <uuid> --subagents <cids>` and audit with `ZeroTrustMicroAuditor.audit_dashboard_deliverable()`.
