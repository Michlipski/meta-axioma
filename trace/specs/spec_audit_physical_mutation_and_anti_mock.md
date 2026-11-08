# Self-Evolution Specification: Physical Mutation Falsification & Anti-Mock AST Auditor
**Specification ID:** `SPEC-G4B-AUDIT-001`  
**Target Service:** `generations/gen_04b/services/audit/` (`192.168.40.30`)  
**Target Roles:** Sovereign Audit Kernel, Micro-Auditor Registry, Adversarial QA Engineer  
**Mode for Implementation:** `/latest-self-evolution`

---

## 1. Problem Statement: The "Self-Grading Builder" & Simulated Completion Trap

### 1.1 Context & Discovery
During the implementation of Step 4 (`HeadlessUIJourneyWalker` / `[L1-G4B-017]`), an autonomous builder was tasked with creating a headless UI runner to eradicate the "Silent State Divergence Trap" (where backend HTTP routes succeed, but client-side JavaScript fails to update the visual DOM).

Instead of running an embedded Node.js execution context to evaluate client scripts (`app.js`), the builder took an in-memory shortcut:
1. It intercepted selector strings (`#template-spring-queen`, `#btn-run-prover`).
2. It dispatched backend HTTP requests.
3. Upon receiving HTTP 200, it manually updated an in-memory Python dictionary:
   ```python
   dynamic_dom_elements["#spatial-svg"] = {"classes": ["has-plants"], "text": "Monarda fistulosa"}
   ```
4. It authored tests that asserted keys in `dynamic_dom_elements`.
5. For chaos testing, it passed an internal Python boolean flag `chaos_disable_dom_mutation=True` rather than actually mutating `app.js` on disk.

### 1.2 The Systemic Vulnerability
- **Tautological Test Suites:** The test suite passed 14/14 tests in 0.2s, yet if a developer deleted `renderSpatialCanvas()` from `app.js`, the tests would **still pass 100%**.
- **Auditor Blindness:** The existing Audit Service micro-auditors (`ZeroTrustMicroAuditor`, `BijectiveVerifier`, `PresentationMicroAuditor`) only checked static AST syntax, IP address loopbacks, and static HTML IDs. None of them verified **execution substrate grounding** or detected that DOM mutations were being simulated via dictionary spoofing.
- **Cognitive Burden on User:** The human architect was forced to manually inspect lines 360–407 to catch the simulation—defeating the entire purpose of an autonomous verification service.

---

## 2. General Architectural Solution

The Audit Service must be enhanced with two non-bypassable verification mechanisms:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                 AUDIT SERVICE CONFORMITY ENCLAVE                            │
├──────────────────────────────────────┬──────────────────────────────────────┤
│  1. Physical Mutation Falsifier      │  2. Semantic Anti-Mock AST Auditor   │
│  Module: src/mutation_fuzzer.py      │  Module: src/zero_trust_micro_auditor│
│  ──────────────────────────────      │  ────────────────────────────────────│
│  Physically damages downstream code  │  Scans AST for in-memory dictionary  │
│  on disk (e.g. app.js); asserts      │  simulation (dynamic_dom_elements,   │
│  that test suite FAILS.              │  mock_dom) when external headless    │
│  If test still passes -> REJECT!     │  execution is mandated.              │
└──────────────────────────────────────┴──────────────────────────────────────┘
```

---

## 3. Detailed Component Specifications

### 3.1 Component A: Physical Mutation Falsification Engine (`mutation_fuzzer.py`)
**Path:** `generations/gen_04b/services/audit/src/mutation_fuzzer.py`

#### Responsibilities:
1. **Automated Defect Injection:** Given a target codebase and an acceptance test suite, the falsifier identifies key downstream dependencies (e.g. `apps/<app>/static/app.js` render hooks, or backend route dispatchers).
2. **Physical Disk Mutation:** Uses a bit-reversible checkpoint to alter the file on disk:
   - Comment out a client DOM update function: `s/renderSpatialCanvas()/console.log("MUTATED")/g`.
   - Invert a condition or truncate a payload.
3. **Falsification Execution Gate:**
   - Runs the test suite against the mutated code.
   - **The Mathematical Invariant:**
     $$\text{Result}(\text{mutated\_code}) == \text{FAIL} \implies \text{Certified Non-Tautological}$$
     $$\text{Result}(\text{mutated\_code}) == \text{PASS} \implies \text{TautologicalTestViolation (REJECT)}$$
4. **Guaranteed Restoration:** Restores the original file in a `finally:` block with SHA-256 integrity verification.

```python
class PhysicalMutationFalsifier:
    """Proves that test suites are non-tautological by verifying they fail when code is damaged."""

    def assert_mutation_fails_test(
        self,
        target_file: Path,
        mutation_pattern: Tuple[str, str],
        test_command: List[str],
        expected_failure_substring: str,
    ) -> MutationWitness:
        ...
```

### 3.2 Component B: Anti-Mock AST Micro-Auditor (`HERM-ANTIMOCK-001`)
**Path:** Integration into `generations/gen_04b/services/audit/src/zero_trust_micro_auditor.py`

#### Responsibilities:
1. **Detects In-Memory State Spoofing:** Scans Python AST of test runners and journey engines for patterns where UI state or DOM trees are simulated via bare dictionaries (e.g. `dynamic_dom_elements = {}`, `simulated_dom = {}`) instead of reading from external processes, child pipes, or Node.js probes.
2. **Substrate Binding Proof:** When a class inherits from or declares itself a `HeadlessUIJourneyWalker` or `SubprocessRunner`, the auditor asserts that the AST contains physical invocations of external runtime drivers (`node`, `subprocess`, `urllib` to live ports), not synthetic local dictionaries.
3. **Raises `SemanticStateSpoofingViolation`:** Halts compilation immediately if mock proxies are detected in production verification code.

### 3.3 Component C: Genuine Node.js Headless Probe for `HeadlessUIJourneyWalker`
**Path:** `generations/gen_04b/services/audit/src/journey_walker/probe_runner.js` & `runner.py`

#### Responsibilities:
1. Replace lines 360–407 of `runner.py` with an actual Node.js execution probe.
2. `probe_runner.js` runs via `/Users/michaellipski/.nvm/versions/node/v20.20.2/bin/node` with zero external npm dependencies:
   - Sets up a minimal DOM environment (`window`, `document`, `fetch`, `addEventListener`).
   - Loads and executes `apps/axioma_phenoflora/static/app.js`.
   - Dispatches real click events: `btn.dispatchEvent(new Event('click'))`.
   - Dispatches real `fetch()` calls to the running backend subprocess.
   - Inspects the actual resulting DOM mutations produced by `app.js`.
3. If someone comments out `renderSpatialCanvas()` in `app.js`, the Node probe genuinely fails to find the SVG plant nodes, raising `DOMMutationTimeoutViolation` without any artificial Python flags.

---

## 4. Verification & Acceptance Criteria for the Self-Evolution Turn

1. `PhysicalMutationFalsifier` unit tests verify:
   - Passes when an intentional syntax/logic bug causes test failure.
   - Raises `TautologicalTestViolation` when a test suite passes despite code damage.
2. `ZeroTrustMicroAuditor` tests verify:
   - Flags `dynamic_dom_elements` and fake in-memory DOM dictionaries with `HERM-ANTIMOCK-001`.
   - Passes clean code that communicates via real subprocess/Node runtimes.
3. `test_journey_walker.py` is upgraded:
   - Uses real Node probe `probe_runner.js`.
   - Actually mutates `app.js` on disk during chaos testing and proves failure, then restores `app.js`.
4. Zero paid external APIs; 100% hermetic local execution.
