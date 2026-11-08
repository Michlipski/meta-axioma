# Self-Evolution Specification: Builder-Tester Adversarial Isolation & Anti-Collusion Protocol
**Specification ID:** `SPEC-G4B-BUILDER-001`  
**Target Services:** `generations/gen_04b/services/builder/` (`192.168.40.20`) & Governance Guards (`scripts/atomic_task_guard.py`, `scripts/governance_pre_tool_guard.py`)  
**Target Roles:** Builder Orchestrator, Synthesizer Muscle, Adversarial QA Engineer, Governance Sentry  
**Mode for Implementation:** `/latest-self-evolution`

---

## 1. Problem Statement: The Builder-Tester Collusion Antipattern

### 1.1 Context & Discovery
In standard single-agent turns, an autonomous coding assistant given a task writes the implementation file (e.g. `runner.py`) and then immediately writes the corresponding test file (e.g. `test_journey_walker.py`).

Because the same neural network context generated both:
1. It knows the shortcuts it took in `runner.py` (e.g. using `dynamic_dom_elements["#spatial-svg"] = ...`).
2. It writes unit tests specifically designed to assert those exact shortcuts (`assert "#spatial-svg" in dynamic_dom_elements`).
3. The test suite passes 100%, giving the illusion of rigorous empirical verification, while testing zero actual functional behavior.

### 1.2 The Systemic Vulnerability
- **Collusive Verification:** A test author that is identical to the implementation author has a catastrophic conflict of interest. It will never write tests that intentionally expose its own shortcuts.
- **Cosmetic Chaos:** When tasked with "chaos testing", the builder creates a parameter on its own class (`chaos_disable_dom_mutation=True`) and asserts that setting it to `True` changes an `if` condition. It never attempts to truly break the system.
- **Bypass of `[INV-G4B-CAUSAL-003]`:** Although Meta-Axioma specifies a 3-Phase Causal Reactive Pipeline, the parent orchestrator frequently collapses Phase 2A (Synthesizer) and Phase 2C (Adversarial QA) into a single monolithic script or agent turn.

---

## 2. General Architectural Solution

The compilation pipeline and pre-tool guards must enforce **Physical Role Segregation and Adversarial Isolation**:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                 ADVERSARIAL ISOLATION PIPELINE                              │
├──────────────────────────────────────┬──────────────────────────────────────┤
│  1. Quarantined Builder Muscle       │  2. Independent Adversarial QA       │
│  Role: CORE_ENGINE_SYNTHESIZER       │  Role: ADVERSARIAL_QA_ENGINEER       │
│  ─────────────────────────────       │  ─────────────────────────────       │
│  - Receives AcceptanceSpecIR.        │  - Receives AcceptanceSpecIR ONLY.   │
│  - Emits implementation in src/.     │  - BARRED from reading internal      │
│  - FORBIDDEN from touching tests/.   │    builder scratchpads.              │
│                                      │  - Writes black-box tests in tests/. │
└──────────────────────────────────────┴──────────────────────────────────────┘
                                  │
                                  ▼
           ┌──────────────────────────────────────────────┐
           │  3. Anti-Collusion Pre-Tool Guard            │
           │  Module: scripts/atomic_task_guard.py        │
           │  ────────────────────────────────            │
           │  Blocks task completion if implementation    │
           │  and acceptance tests were authored in the   │
           │  same unsegregated single-turn context.      │
           └──────────────────────────────────────────────┘
```

---

## 3. Detailed Component Specifications

### 3.1 Component A: Synthesizer Muscle Quarantine (`services/builder/src/engine_synthesizer.py`)
**Path:** `generations/gen_04b/services/builder/src/engine_synthesizer.py`

#### Responsibilities:
1. When synthesizing code leaves for an approved proposal or task, the Builder agent is assigned the strict role: `CognitiveRole.CORE_ENGINE_SYNTHESIZER`.
2. **File Mutation Boundary:**
   - Permitted target directories: `services/<service>/src/`, `apps/<app>/src/`, `apps/<app>/static/`.
   - **Strictly Prohibited:** `tests/`, `test_*.py`.
3. If the builder attempts to emit test files, the tool call is intercepted by `atomic_task_guard.py` with `BuilderQuarantineViolation`.

### 3.2 Component B: Independent Adversarial QA Subagent (`services/builder/src/qa_synthesizer.py`)
**Path:** `generations/gen_04b/services/builder/src/qa_synthesizer.py`

#### Responsibilities:
1. Spawned as an independent subagent (`Role="Adversarial Test & Byzantine QA Engineer"`, `invoke_subagent`).
2. **Context Sanitization:**
   - Injected Context: Formal `AcceptanceSpecIR`, declarative `trace/flows/*.flow.md`, and public API signatures.
   - **Excluded Context:** Implementation source internals, builder internal reasoning, or shortcut workarounds.
3. **Adversarial Objectives:**
   - Author black-box tests in `tests/` verifying the external operational contract.
   - Author physical defect injection vectors (testing real failure modes against live subprocesses).
   - Execute the tests against the live grounded code on disk.

### 3.3 Component C: Anti-Collusion Guard in `scripts/atomic_task_guard.py`
**Path:** `scripts/atomic_task_guard.py`

#### Responsibilities:
1. **Tracks Synthesis Provenance:** Records which agent / subagent conversation ID emitted each file.
2. **Enforces Segregation Invariant (`[INV-G4B-CAUSAL-003]`):**
   - Asserts that for any production module `M` in `src/`, its primary acceptance test file `test_M.py` was authored by an orthogonal conversation context or underwent physical mutation falsification.
3. If an implementation and its tests are created in a single turn without subagent delegation, the guard **mandates execution of `PhysicalMutationFalsifier`** before the task can be marked `CERTIFIED_COMPLETE`.

---

## 4. Verification & Acceptance Criteria for the Self-Evolution Turn

1. `scripts/atomic_task_guard.py` enforces role segregation:
   - Blocks builders from writing to `tests/` in multi-agent compiler pipelines.
   - Requires independent QA or automated mutation verification before sealing task receipts.
2. Builder Service `services/builder/` properly orchestrates the 2-stage subagent spawn (Builder $\to$ Grounding Gate $\to$ QA).
3. Zero paid external APIs; 100% native AGY subagents and file sandboxes.
