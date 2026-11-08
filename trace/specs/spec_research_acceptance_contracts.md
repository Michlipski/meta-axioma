# Self-Evolution Specification: Machine-Readable Acceptance Contracts (`AcceptanceSpecIR`)
**Specification ID:** `SPEC-G4B-RESEARCH-001`  
**Target Services:** `generations/gen_04b/services/research/` (`192.168.40.10`) & `protocols/`  
**Target Roles:** Sovereign Research Service, Protocol Architect, Domain Ontologist  
**Mode for Implementation:** `/latest-self-evolution`

---

## 1. Problem Statement: The Ambiguity of Natural Language Proposals

### 1.1 Context & Discovery
In Meta-Axioma Generation 4b, the Research Service authoritatively deconstructs Waterloo Tier 1 Situations of Concern (`[L1-G3B-000]`), produces domain contracts (`ContractIR`), and emits detailed proposals in `project_proposals.md`.

However, the **acceptance criteria and operational constraints** (such as *"must execute via an embedded Node.js probe"*, *"must run an independent OS subprocess"*, *"must fail if downstream code is damaged"*) are currently recorded as **unstructured English markdown prose**.

### 1.2 The Systemic Vulnerability
- **Semantic Loss in Downstream Synthesis:** When the Builder receives `project_proposals.md`, it reads English prose and decides how to implement it. If a requirement is technically demanding (e.g. configuring a headless JS runtime without external npm packages), the LLM agent frequently takes the path of least cognitive resistance—substituting in-memory dictionary mocks.
- **Unenforceable Verification:** The Audit Service has no mechanical schema to parse. It cannot automatically know which external runtimes were mandated, which files must be grounded, or which chaos mutations must be proven.
- **Human Verification Leak:** Because the acceptance contract is not machine-executable, the burden of verifying compliance falls entirely on the human architect.

---

## 2. General Architectural Solution

The Research Service and protocol mesh must emit a formal, strongly-typed **`AcceptanceSpecIR`**:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                 ACCEPTANCE CONTRACT PIPELINE                                │
├──────────────────────────────────────┬──────────────────────────────────────┤
│  Research Output (Phase 1)           │  Audit Verification Gate (Phase 2C)  │
│  ─────────────────────────           │  ─────────────────────────────────── │
│  Emits `AcceptanceSpecIR`:           │  Auditor loads `AcceptanceSpecIR`:   │
│  - required_runtimes                 │  - Asserts runtimes are invoked      │
│  - banned_ast_patterns               │  - Runs banned-pattern AST linters   │
│  - physical_falsification_targets    │  - Executes automated disk mutations │
│  - max_latency_ms thresholds         │  - Enforces hard latency bounds      │
└──────────────────────────────────────┴──────────────────────────────────────┘
```

---

## 3. Detailed Component Specifications

### 3.1 Component A: Formal Protocol Dataclasses (`protocols/acceptance_spec.py`)
**Path:** `generations/gen_04b/protocols/acceptance_spec.py` (and re-exported in `deliverable_bundle.py`)

```python
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict, Any

@dataclass(frozen=True)
class FalsificationVector:
    """Formal definition of a physical defect injection to prove test non-tautology."""
    vector_id: str
    target_file_relative_path: str       # e.g. "apps/axioma_phenoflora/static/app.js"
    target_symbol_or_pattern: str        # e.g. "renderSpatialCanvas"
    mutation_type: str                   # "COMMENT_OUT" | "RETURN_EMPTY" | "INVERT_CONDITION"
    expected_failure_exception: str      # e.g. "DOMMutationTimeoutViolation"
    reversion_witness_required: bool = True

@dataclass(frozen=True)
class AcceptanceSpecIR:
    """Machine-readable contract defining empirical requirements for a builder task."""
    spec_id: str
    feature_name: str
    target_enclave_path: str             # e.g. "generations/gen_04b/services/audit/src/journey_walker/"
    required_runtimes: List[str]         # e.g. ["python3", "node"]
    banned_ast_patterns: List[Dict[str, str]]  # e.g. [{"pattern": "dynamic_dom_elements", "reason": "No in-memory DOM spoofing"}]
    falsification_vectors: List[FalsificationVector]
    max_latency_per_step_ms: float = 200.0
    zero_console_panics_required: bool = True
    min_statechart_coverage_pct: float = 90.0
    telemetry_digest_required: bool = True

    def to_dict(self) -> Dict[str, Any]:
        ...

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> AcceptanceSpecIR:
        ...
```

### 3.2 Component B: Research Service Emission (`services/research/src/spec_emitter.py`)
**Path:** `generations/gen_04b/services/research/src/spec_emitter.py`

#### Responsibilities:
1. Whenever the Research Service compiles a `ResearchDeliverableBundle` or prepares an evolutionary proposal, it automatically derives `AcceptanceSpecIR` from the Waterloo Tier 1 Situation of Concern (`[L1-G3B-000]`).
2. Persists the machine-readable contract to `acceptance_spec.json` alongside `project_proposals.md`.
3. Injects this contract directly into downstream prompts for both the Builder (`CORE_ENGINE_SYNTHESIZER`) and the Adversarial QA subagent (`ADVERSARIAL_QA_ENGINEER`).

### 3.3 Component C: Audit Engine Binding (`services/audit/src/acceptance_gate.py`)
**Path:** `generations/gen_04b/services/audit/src/acceptance_gate.py`

#### Responsibilities:
1. In Phase 2C (Adversarial QA), the Audit Kernel loads `acceptance_spec.json`.
2. Mechanically validates each constraint in the IR:
   - Verifies that external binaries in `required_runtimes` (e.g. `node`) were called during test execution.
   - Executes AST scan across newly emitted files for any identifiers in `banned_ast_patterns`.
   - Programmatically executes every `FalsificationVector` via `PhysicalMutationFalsifier`.
3. If any constraint fails, the Audit Kernel raises `AcceptanceContractBreachViolation` and refuses to issue a Merkle attestation witness.

---

## 4. Verification & Acceptance Criteria for the Self-Evolution Turn

1. `protocols/acceptance_spec.py` passes serialization, deserialization, and SHA-256 roundtrip tests.
2. `ResearchDeliverableBundle` includes `acceptance_spec: Optional[AcceptanceSpecIR]`.
3. `AcceptanceGate` in `services/audit/` correctly parses `acceptance_spec.json`, verifies required runtimes, and triggers falsification tests.
4. Zero external paid APIs; 100% native Python/JSON schemas.
