---
domain: GenerationalFeedback
related_domains:
  - AxiomRegistry
  - EvaluationTargets
  - AppSpecification
  - TelemetryAudit
---

CONSTRAINTS:
- Architectural lessons learned from failures, human vetoes, or teleological misalignments in Generation $G_N$ must be permanently recorded and cannot be erased.
- Generation $G_N$ cannot complete generational handover or synthesize the foundational basis for $G_{N+1}$ without compiling a verified `GenerationalFeedbackDossier`.
- Generation $G_{N+1}$ must ingest all inherited lessons from predecessor generations as compile-time constraints, negative invariants, or evaluation target penalties.
- Regressions against inherited lessons are treated as fatal compilation faults (`GenerationalRegressionFault`).

GLOSSARY:
- Generational Lesson: A discrete atomic post-mortem record documenting an observed failure, root cause, human oracle ruling, and successor prescription.
- Feedback Dossier: The cumulative compilation of lessons, post-mortems, and architectural constraints produced by generation $G_N$ for generation $G_{N+1}$.
- Inherited Constraint: A formal compiler invariant or negative rule derived from a predecessor lesson that strictly binds successor generations.
- Verification Illusion: The epistemic failure mode where internal automated tests pass 100% on a system that is unvalidated against the human oracle's utility function.
- Transgenerational Epistemic Inheritance: The formal mechanism by which qualitative experience, mistakes, and human critiques are preserved across multi-generational compiler evolution.

# ENTITY: GenerationalLesson
MUST HAVE:
- lesson_id: String (Pattern: ^LES-G\d{2}-\d{3}$)
- generation: String (Pattern: ^gen_\d{2}$)
- title: String
- category: Enum (ELICITATION_FAILURE, VERIFICATION_ILLUSION, COMPUTE_WASTE, ERGONOMIC_FRICTION, BOUNDARY_LEAKAGE)
- severity: Enum (LOW, MEDIUM, HIGH, CRITICAL)
- incident_summary: String
- root_cause: String
- human_oracle_ruling: String
- successor_prescriptions: List of String
- created_at: Float

RULES:
- R1: Lessons with HIGH or CRITICAL severity must map to at least one successor prescription that enforces an architectural constraint.
- R2: Lessons cannot be removed or overwritten; any refinement must append a superseding lesson.

# ENTITY: GenerationalFeedbackDossier
MUST HAVE:
- generation_origin: String (Pattern: ^gen_\d{2}$)
- successor_generation: String (Pattern: ^gen_\d{2}$)
- total_lessons: Integer
- lessons: List of GenerationalLesson
- inherited_negative_constraints: List of String
- compiled_at: Float
- signed_off_by: String

RULES:
- R1: Must be serialized both as human-readable `FEEDBACK.md` and machine-readable `feedback.json`.
- R2: The successor basis generator for $G_{N+1}$ must ingest `feedback.json` before emitting candidate axioms.
- R3: An empty dossier is forbidden if any human vetoes or application compilation errors occurred during the generation.

# EVENT: LessonCaptured
TRIGGER:
- Emitted whenever an architectural friction, human veto, or verification illusion is recorded.
PAYLOAD:
- lesson_id
- generation
- category
- severity

# EVENT: FeedbackCompiled
TRIGGER:
- Emitted when a generation compiles its complete feedback dossier for the successor.
PAYLOAD:
- generation_origin
- successor_generation
- total_lessons
- inherited_negative_constraints

# EVENT: ConstraintsInherited
TRIGGER:
- Emitted when a successor generation initializes and activates constraints from a predecessor dossier.
PAYLOAD:
- successor_generation
- source_generation
- constraints_count
