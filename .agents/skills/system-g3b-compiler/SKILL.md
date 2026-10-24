---
name: system-g3b-compiler
description: >-
  End-to-end execution protocol for the System G3b Compiler (Autonomous Universal Systems Compiler
  in generations/gen_03b/src/g3b_compiler/). Activate and read this skill whenever the user asks to
  build, compile, synthesize, or architect an application using the System G3b Compiler or Generation 3b.
---

# System G3b Compiler (`SystemG3bCompiler`) Execution Skill

Whenever a user asks to build or compile an application using the **System G3b Compiler**, follow this mandatory 3-phase protocol without needing reminders in the user's prompt.

---

## Phase 1: Emit Detailed Proposals Document (`write_to_file` $\to$ `project_proposals.md`) & `ask_question` Gate (Directive 3)

> [!IMPORTANT]
> **NEVER call `ask_question` without FIRST calling `write_to_file` to emit the full Detailed Project Proposals Document (`<appDataDir>/brain/<conversation-id>/project_proposals.md`)!** Putting short summaries inside `ask_question` options without emitting the full `project_proposals.md` artifact is strictly forbidden.

Before emitting any application code:

1. **Waterloo Tier 1 Situation of Concern (`[L1-G3B-000]`):**
   - Deconstruct the user's seed prompt into a solution-agnostic `SituationOfConcern` hierarchy (`MACRO`, `MESO`, `MICRO`) identifying `actors`, `frictions`, `constraints`, and `unmet_needs`.
2. **A-Priori Single-Budget Calibration (`DynamicBudgetCalibrator.estimate_from_structural_scope`):**
   - **Strictly Prohibited:** Never invent two separate budgets (such as an unmetered "full agentic" budget alongside a "crucible BPE" budget), and never count tokens of already-written JSON/code and call it a "pre-execution prediction."
   - For each proposed project option (e.g., Option A / Option B / Option C), define its structural graph scope (`soc_tree_nodes`, `num_nouns`, `num_sub_contracts`, `num_composed_verbs`, `num_statechart_states`, `num_topology_nodes`, `num_topology_channels`, `num_code_leaves`).
   - **Full-Application Multi-Module Scaling ($\ge 100,000$ Tokens):** For production applications (Target $P_1$) containing full multi-module architectures (`server.py`, `engine.py`, `persistence.py`, `enclaves.py`, `index.html`, `style.css`, `app.js`, `dashboard.html`, `test_app.py`), pass `is_full_application=True` and `num_code_leaves=5..8`. This naturally and honestly scales budgets into the **$120,000 - 350,000$ BPE token tier** without 99% unspent padding:
     ```python
     from g3b_compiler.thermodynamics import DynamicBudgetCalibrator

     # Full production application budget estimate
     est = DynamicBudgetCalibrator.estimate_from_structural_scope(
         soc_tree_nodes=15,
         num_nouns=4,
         num_sub_contracts=4,
         num_composed_verbs=2,
         num_statechart_states=18,
         num_topology_nodes=3,
         num_topology_channels=3,
         num_code_leaves=7,
         is_full_application=True,
         expected_fault_retries=2,
     )
     # est.recommended_total_budget >= 100,000 tokens
     ```
   - Every option must preserve **60% Exploratory Capital** (`est.exploratory_cap`) and **40% Protected Capital** (`est.protected_floor`).
3. **Physically Emit `project_proposals.md` via `write_to_file` BEFORE Calling `ask_question`:**
   - Call `write_to_file` to write `<appDataDir>/brain/<conversation-id>/project_proposals.md` with `ArtifactMetadata={"UserFacing": True, "RequestFeedback": False, "Summary": "Detailed High-Level Plan & Dynamic Token Proposals Dossier"}`.
   - The `project_proposals.md` file MUST include all three mandatory sections:
     1. **Section 1 — High-Level Plan & Waterloo Tier 1 Situation of Concern (`[L1-G3B-000]`):** Macro/Meso/Micro decomposition, target persona, primary JTBD, daily workflow, structural architecture, and UX ergonomics.
     2. **Section 2 — Comparative Summary Matrix:** Markdown table comparing all options (`Option Name`, `Unified BPE Token Budget`, `Exploratory (60%)`, `Protected (40%)`, `Predicted Spend`, `Structural Graph Counts`, `Core Scope`, and `Statechart Complexity`).
     3. **Section 3 — Exhaustive Per-Option Engineering Specifications:** Write out all 6 subsections for **EVERY** option (Option A, Option B, Option C, etc.):
        - **Target Persona & JTBD Fit**
        - **Token Budget & Workload Partition** (Total Unified BPE Tokens, 60% Exploratory, 40% Protected, and itemized BPE breakdown across SoC Research, Dialectical Decomposition, Contract/Statechart/Topology IR Leaves, Application Code Leaves, Model Checking, and Runtime Sinks)
        - **Statechart & Verification Depth** (states, compound/parallel/history nodes, transitions, covering paths, verification sinks)
        - **Included Scope:** (detailed bulleted list of features, backend modules, visual UI components, and interactions — **MANDATORY:** Must explicitly specify the **Development Process Telemetry Dashboard (`telemetry_dashboard.html` / `dashboard.html`)** for EVERY option, detailing compile-time thermodynamic spend gauges, subagent execution witnesses, Quorum consensus trace, Landauer dissipation meters, and substrate test verification witnesses — explicitly clarifying that this is the telemetry dashboard of the development/compilation process itself, not an end-user product UI)
        - **Deliberately Deferred / Cut Scope** (explicit list of features cut to prevent scope creep, with technical rationale)
        - **Engineering & Budget Justification** (detailed explanation of why the `estimate_from_structural_scope()` budget fits the LOC emission and formal verification burden)
4. **Link the Artifact & Call `ask_question`:**
   - Only AFTER `write_to_file` has created `project_proposals.md`, call `ask_question` to elicit the human architect's selection, and link to `[project_proposals.md](file:///...)` in your message.

---

## Phase 2: Mandatory Live Subagent Spawning (`invoke_subagent`), 2-Stage Gating, & Orthogonal Personas (`[L1-G3B-014]` & Directive 5)

Once the human architect approves an option, **monolithic single-agent code generation in the main conversation is strictly forbidden (`SubagentExecutionViolation`)**. In-process `@classmethod` helpers are local unit-test fallbacks only.

You MUST execute live subagent spawning in **two strictly sequential stages** using the **orthogonally maximal persona set** (`PersonaRegistry`) to prevent context convergence:

> [!TIP]
> **Argon Feature Flag & Quota Protection (`ENABLE_ARGON`):**
> `DualModelRouter.ENABLE_ARGON` is set to `False` by default to prevent Argon / Gemini Pro quota exhaustion. When `ENABLE_ARGON` is `False`, invoke **both** Brain and Muscle subagents with `Model="flash"`. The sequential 2-stage gating and specialized prompt scaffolding remain 100% active.

### Stage 1: The Brain / Research & Architecture Gate (`Model="flash"` when Argon disabled, else `"pro"`)
> [!IMPORTANT]
> **Anti-Race Condition Gate:** NEVER launch Muscle subagents in parallel with the Brain in the same initial tool call! The synthesizers must receive the Brain's finalized architecture in their prompts.

1. Call `invoke_subagent` with `Model="flash"` (or `Model="pro"` if `ENABLE_ARGON=True`):
   - **`Role="Human Ergonomics & UX Architect"`** (`CognitiveRole.HUMAN_ERGONOMICS_ARCHITECT`): Deconstructs Target $P_1$, daily workflow, and cognitive ergonomics.
   - **`Role="Domain Ontologist & Contract Proof Engineer"`** (`CognitiveRole.DOMAIN_ONTOLOGIST`): Formalizes nouns, invariants, and `ContractIR`.
   - *(Or combined lead role `Role="G3b Dialectical Architect & SoC Researcher"`).*
2. **Stop and Await Completion:** Wait for the Brain subagent's response. Extract the certified Waterloo Tier 1 `SituationOfConcern`, the `DecompositionPlan`, and domain contract specifications.

### Stage 2: The Muscle / Orthogonal Parallel Synthesis (`Model="flash"` — Gemini 3.8 Flash)
Only AFTER Stage 1 returns, launch the specialized Muscle subagents concurrently, passing the Brain's actual research and architectural specifications into their prompts:
1. **`Role="Core Backend & Functorial Engine Synthesizer"`** (`CognitiveRole.CORE_ENGINE_SYNTHESIZER`):
   - Synthesizes `src/engine.py`, `src/server.py`, `src/persistence.py`, `src/enclaves.py`, and `schema/`.
2. **`Role="Operational Dashboard & Telemetry Synthesizer"`** (`CognitiveRole.OPERATIONAL_DASHBOARD_SYNTHESIZER`):
   - Synthesizes `telemetry_dashboard.html` / `dashboard.html`, development process telemetry visualizer, subagent witness HUD, Landauer dissipation meters, and test verification proofs (`[L1-G3B-018]`).
3. **`Role="Adversarial Test & Byzantine QA Engineer"`** (`CognitiveRole.ADVERSARIAL_QA_ENGINEER`):
   - Synthesizes `tests/test_app.py`, injecting Byzantine fault modes (false calm, packet drops, motor stalls), edge-case fuzzing, and asserting exit code 0.

### Stage 3: Construct `SubagentExecutionWitness` Records
For every subagent spawned across both stages, record its real `conversationId` and measure prompt and response BPE tokens via `PhysicalTokenMeter.count()`:
```python
from g3b_compiler import (
    CognitiveRole,
    ModelTier,
    PhysicalTokenMeter,
    SubagentExecutionWitness,
    DualModelRouter,
)

# Model assigned respects DualModelRouter.ENABLE_ARGON (Flash fallback when Argon disabled)
brain_model = DualModelRouter.get_authorized_model(CognitiveRole.HUMAN_ERGONOMICS_ARCHITECT)

witnesses = [
    SubagentExecutionWitness(
        task_id="stage1:architect_research",
        subagent_role="Human Ergonomics & UX Architect",
        cognitive_role=CognitiveRole.HUMAN_ERGONOMICS_ARCHITECT,
        assigned_model=brain_model,  # ModelTier.MUSCLE_FLASH when ENABLE_ARGON=False
        conversation_id="<real-uuid-from-invoke_subagent>",
        prompt_bpe_tokens=PhysicalTokenMeter.count(brain_prompt),
        response_bpe_tokens=PhysicalTokenMeter.count(brain_response),
        is_live_agy_subagent=True,
    ),
    SubagentExecutionWitness(
        task_id="stage2:core_backend",
        subagent_role="Core Backend & Functorial Engine Synthesizer",
        cognitive_role=CognitiveRole.CORE_ENGINE_SYNTHESIZER,
        assigned_model=ModelTier.MUSCLE_FLASH,
        conversation_id="<real-uuid-from-invoke_subagent>",
        prompt_bpe_tokens=PhysicalTokenMeter.count(backend_prompt),
        response_bpe_tokens=PhysicalTokenMeter.count(backend_response),
        is_live_agy_subagent=True,
    ),
    SubagentExecutionWitness(
        task_id="stage2:operational_dashboard",
        subagent_role="Operational Dashboard & Telemetry Synthesizer",
        cognitive_role=CognitiveRole.OPERATIONAL_DASHBOARD_SYNTHESIZER,
        assigned_model=ModelTier.MUSCLE_FLASH,
        conversation_id="<real-uuid-from-invoke_subagent>",
        prompt_bpe_tokens=PhysicalTokenMeter.count(dash_prompt),
        response_bpe_tokens=PhysicalTokenMeter.count(dash_response),
        is_live_agy_subagent=True,
    ),
    SubagentExecutionWitness(
        task_id="stage2:adversarial_qa",
        subagent_role="Adversarial Test & Byzantine QA Engineer",
        cognitive_role=CognitiveRole.ADVERSARIAL_QA_ENGINEER,
        assigned_model=ModelTier.MUSCLE_FLASH,
        conversation_id="<real-uuid-from-invoke_subagent>",
        prompt_bpe_tokens=PhysicalTokenMeter.count(qa_prompt),
        response_bpe_tokens=PhysicalTokenMeter.count(qa_response),
        is_live_agy_subagent=True,
    ),
]
```

---

## Phase 2b: Adversarial Quorum Consensus Gate (Argon Governance)

Immediately after initial proposal decomposition and before the Fractal Task Stack begins leaf emission, the outer FSM runs `run_adversarial_quorum_gate()`. It broadcasts the draft spec concurrently to three stateless auditors powered exclusively by Gemini 4 Argon:

1. **`ProductManagerAuditor` (Role: `PRODUCT_MANAGER`):** Relentlessly enforces scope boundaries, thermodynamic budgets, and **Mandatory Core Deliverables (`[L1-G3B-018]`)**. Rejects unbudgeted feature-rich hallucinations (e.g., unbudgeted WebSocket meshes, microtonal lattices) not fundamentally required by the Tier 1 SoC, AND rejects any plan that omits the **Development Process Telemetry Dashboard** (`telemetry_dashboard.html` / `dashboard.html`) documenting compile-time subagents, budgets, and verification sinks.
2. **`ArchitectAuditor` (Role: `SYSTEMS_ARCHITECT`):** Enforces system invariants (`[L1-G3B-012]` Topological Fidelity, `[L1-G3B-017]` Quine Protocol); rejects any spec that attempts to bypass isolation boundaries (e.g., bypassed Quine isolation, multi-node loopback leaks).
3. **`QAVerificationAuditor` (Role: `QA_ENGINEER`):** Rejects any proposed feature or state transition lacking a mathematically testable invariant in `ContractIR` or `StatechartIR`, or missing operational dashboard verification sinks.

**The Resolution Gate:**
- If `ALL` verdicts return `approved == True`: Transition state to IR synthesis.
- If `ANY` verdict returns `approved == False`: Block progression. Concatenate all `blocking_violations` and route state back to `DialecticalArchitectSubagent` (Argon) to synthesize a targeted Delta Update resolving only the specific violations (including injecting the missing dashboard deliverable). Loop until unanimous consensus is achieved before emitting any leaf code.

---

## Phase 3: Quine Daughter Isolation Protocol (`[L1-G3B-017]`), Full-App Auditing (`[L1-G3B-016]`), & Cryptographic Telemetry


1. **Execute the Reflexive Quine Daughter Isolation Protocol (`[L1-G3B-017]`):**
   - Never omit the Quine Daughter Crucible! Every `SystemG3bCompiler` build must prove reflexive universality by executing `compiler.execute_quine_crucible(...)`, where the Parent (`G3b`) emits the Daughter Compiler (`G3b'`) into `generations/gen_03b/epochs/epoch_<name>_quine_crucible/daughter_compiler`, boots `compile_seed.py` in an isolated subprocess on the target `SituationOfConcern` and `domain_spec`, and extracts `quine_result["daughter_witness"]`.
2. **Never Bypass Leaf Quotas or Hide App Files Outside Telemetry:**
   - Do not modify `subagents.py` to inflate `token_budget_allocated`.
   - Always pass **both** `target_output_dir` (the epoch directory `generations/gen_03b/epochs/epoch_<name>/`) and `app_output_dir` (the full interactive application directory `generations/gen_03b/apps/<app_name>/` or `apps/<app_name>/`), along with `daughter_witness=quine_result["daughter_witness"]`, `subagent_witnesses=witnesses`, and `require_live_subagents=True`, into `SystemG3bCompiler.compile()`:
     ```python
     quine_result = compiler.execute_quine_crucible(
         parent_soc=parent_soc,
         novel_downstream_soc=soc,
         sandbox_root_dir=quine_sandbox_dir,
         downstream_invariants=required_invariants,
         downstream_domain_spec=domain_spec,
         subagent_witnesses=witnesses,
         require_live_subagents=True,
     )
     report = compiler.compile(
         seed_input=soc,
         target_output_dir=epoch_dir,
         app_output_dir=app_dir,
         soc_id=soc.soc_id,
         is_multi_node_cluster=True,
         required_invariants=required_invariants,
         inject_fault_on_first_try=True,
         daughter_witness=quine_result["daughter_witness"],
         domain_spec=domain_spec,
         subagent_witnesses=witnesses,
         require_live_subagents=True,
     )
     ```
3. **Verify Physical Artifacts & Cryptographic Chain (`[NEG-G1B-001]`, `[L1-G3B-018]`):**
   - Confirm that `SystemG3bCompiler.compile()` audits 100% of `.py`, `.js`, `.html`, and `.css` files in `app_output_dir` through `ZeroTrustMicroAuditorRegistry`, physically checks for the presence of the **Operational Dashboard** (`dashboard.html` / `telemetry_dashboard.html`), executes both the epoch test suite and the application test suite in live subprocesses (`exit_code == 0`), and seals `telemetry_ledger.json` + `telemetry_dashboard.md` + `telemetry_dashboard.html` with `CryptographicTelemetryEngine.verify_ledger_integrity(report["telemetry"]) == True`.

