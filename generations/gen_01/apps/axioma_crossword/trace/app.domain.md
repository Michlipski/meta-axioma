---
domain: AxiomaCrossword
related_domains:
  - AppSpecification
  - GenerationalFeedback
  - TelemetryAudit
---

CONSTRAINTS:
- Geometric grid topology (cell coordinates, intersections) must remain strictly decoupled from the semantic clue layer (L1-015_1).
- Cryptic clues must project into a verifiable Universal Grammar AST separating [Definition], [Indicator], and [Fodder] (L1-004).
- CPU-bound AC-3 CSP puzzle synthesis must execute in isolated asynchronous worker queues without blocking web server I/O (L1-015_1).
- Every discarded word candidate during CSP backtracking erases information (ΔS = k_B ln |D_i|) and must be audited in the Landauer ledger (L1-008).
- Client-side solver mutations must be reversible via functorial inverse morphisms (M^-1) and synchronizable across devices using idempotent deltas (L1-002).
- Storage access must be partitioned by session and puzzle to prevent concurrent write collisions (L1-011_3).

GLOSSARY:
- Cryptic Anatomy Dissector: Parser decomposing clues into Definition, Indicator, and Wordplay Fodder.
- Arc Consistency (AC-3): Constraint propagation algorithm pruning impossible words from intersecting slots.
- Landauer Search Dissipation: Minimum thermodynamic heat (kB T ln 2) dissipated when candidate paths are erased during backtracking.
- Optimistic Local Execution: Client-side immediate keystroke handling with asynchronous delta syncing.

# ENTITY: CrosswordGrid
MUST HAVE:
- grid_id: String
- title: String
- size_rows: Integer
- size_cols: Integer
- cells: List[List[String]]
- slots: List[WordSlot]
- clues: List[CrypticClue]
- symmetry: Enum (ROTATIONAL_180, SYMMETRIC_FREE)

RULES:
- R1: Intersecting across and down slots must agree on the identical character at their intersection point.
- R2: Cell values must be upper-case alphabet or "#" for black blocker cells.

# ENTITY: CrypticClue
MUST HAVE:
- clue_id: String
- slot_id: String
- number: Integer
- direction: Enum (ACROSS, DOWN)
- surface_text: String
- length: Integer
- answer: String
- definition: String
- clue_type: Enum (ANAGRAM, HIDDEN_WORD, CONTAINER, CHARADE, REVERSAL, DOUBLE_DEF, HOMOPHONE)
- indicator: String
- fodder: String
- explanation: String

RULES:
- R1: The wordplay component must computationally evaluate to the answer string.
- R2: For ANAGRAM clues, sorted(fodder) must match sorted(answer).

# ENTITY: SynthesisJob
MUST HAVE:
- job_id: String
- status: Enum (PENDING, RUNNING, COMPLETED, FAILED, TIMEOUT)
- grid_size: Integer
- backtracks_count: Integer
- pruned_candidates_count: Integer
- joules_dissipated: Float
- progress_pct: Float
- result_grid_id: Optional[String]
- error: Optional[String]

RULES:
- R1: If backtracks exceed the Landauer execution budget (5,000 steps), the job must terminate cleanly with status TIMEOUT.

# EVENT: CellLetterEntered
MUST HAVE:
- session_id: String
- row: Integer
- col: Integer
- char: String
- prev_char: String
- timestamp: Float

# EVENT: SynthesisJobDispatched
MUST HAVE:
- job_id: String
- grid_size: Integer
- worker_id: String
- timestamp: Float
