---
domain: AppSpecification
related_domains:
  - AxiomRegistry
  - EvaluationTargets
  - TelemetryAudit
---

CONSTRAINTS:
- Every non-generator application compiled by any generation must adhere strictly to the standardized /apps structure.
- Applications must embody the active structural invariants of their originating generation.
- Decoupled persistence (Boundary 3) is strictly mandatory: runtime state mutations must not perform unmediated disk I/O outside data/.
- Zero-trust MCP boundaries (Nouns in schema/nouns.json, Verbs in schema/verbs.json) must be declared and validated.
- All non-standard exceptions or invariant suspensions must be isolated within demarcated exception enclaves.
- Standard applications must run locally with zero paid third-party dependencies (Python 3.14 standard library).
- Phase 0 Human Intent Elicitation is strictly mandatory: No non-generator application may be synthesized or compiled without a verified HumanIntentWitness establishing the human's actual daily workflow, mental model, and utility function (LES-G1-001).

GLOSSARY:
- App Manifest (app.json): The canonical machine-readable metadata file declaring the app's identity, generation origin, port, and embodied invariants.
- Noun Boundary: The typed schema contract defining data structures exchanged with the application.
- Verb Boundary: The deterministic finite state automaton governing allowed operations.
- Non-Generator Application: An end-user software system optimized for human utility, cognitive ergonomics, and controllability (Target P1).
- Human Intent Witness: A formal trace artifact verifying that the human oracle's workflow, pain points, and utility functions were elicited and approved before compilation.

# ENTITY: HumanIntentWitness
MUST HAVE:
- app_id: String (Pattern: ^[a-z0-9_]+$)
- persona_verified: String
- primary_jobs_to_be_done: List[String]
- core_benefit_statement: String
- human_signoff_status: Enum (DRAFT, ELICITED, SIGNED_OFF, REJECTED)
- signed_off_at: Float

RULES:
- R1: Compilation is strictly blocked if human_signoff_status != SIGNED_OFF.
- R2: Synthetic/hallucinated elicitation without human oracle dialogue is forbidden (LES-G1-001).

# ENTITY: ApplicationManifest
MUST HAVE:
- app_id: String (Pattern: ^[a-z0-9_]+$)
- name: String
- version: String
- tagline: String
- description: String
- generation_origin: String (Pattern: ^gen_\d{2}$)
- target_persona: String
- port: Integer
- deep_ast_digest: String
- invariants_embodied: List[String]
- entrypoint: String
- compiled_at: Float
- compiled_by: String

RULES:
- R1: The app_id must match the containing directory name.
- R2: The port must be deterministically assigned and collision-free within the generational registry.
- R3: The invariants_embodied must include all active Level 1 structural axioms of the originating generation.

# ENTITY: StandardAppLayout
MUST CONTAIN:
- app.json: Application manifest.
- README.md: Human-readable documentation, UX ergonomics, and execution commands.
- run.py: Executable entrypoint launching the application.
- dashboard.html: Interactive real-time operational and telemetry dashboard (FSM statechart HUD, invariant verification monitor, Landauer dissipation counters, and operator controls) [L1-G3B-018].
- trace/: Declarative TRACE domain and workflow specifications.
  - app.domain.md: Entity and invariant definitions.
  - ux_flow.flow.md: User interaction state machine and ergonomic flow (Target P1).
- schema/: Dual-boundary specifications.
  - nouns.json: Typed data schemas (Nouns).
  - verbs.json: Deterministic state automata transitions (Verbs).
- src/: Modular backend source code.
  - __init__.py
  - engine.py: Functorial state engine with reversible morphism history (L1-002).
  - server.py: Zero-trust MCP gateway HTTP server (L1-015).
  - persistence.py: Boundary 3 storage adapter (L1-011_3).
  - enclaves.py: Demarcated exception enclaves (L1-016).
- data/: Decoupled state persistence.
  - seed.json: Baseline initial seed dataset.
  - state.json: Active runtime state snapshot.
- static/: Ergonomic frontend user interface.
  - index.html: Semantic HTML5 document.
  - style.css: Modern ergonomic stylesheet.
  - app.js: Reactive client with undo/redo and live Landauer dissipation telemetry.
- tests/: Verification test suite.
  - test_app.py: Automated tests verifying 100% compliance with invariants.

# EVENT: AppCompiled
TRIGGER:
- Emitted when an ApplicationCompiler synthesizes a complete application adhering to the standard layout.
PAYLOAD:
- app_id
- generation_origin
- path
- deep_ast_digest
- port

# EVENT: AppVerified
TRIGGER:
- Emitted when an application passes its full verification test suite.
PAYLOAD:
- app_id
- test_count
- pass_rate
- thermodynamic_erasure_bits
