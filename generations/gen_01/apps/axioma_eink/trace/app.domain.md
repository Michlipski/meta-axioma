---
domain: AxiomaEink
related_domains:
  - AppSpecification
  - GenerationalFeedback
  - TelemetryAudit
---

CONSTRAINTS:
- The active daily focus board must strictly contain between 1 and 5 tasks (Daily Big 3-5 focus envelope) to eliminate cognitive overload.
- The dedicated e-ink display endpoint (/display) must be zero-JavaScript, containing no <script> tags and no CSS animations, ensuring 100% crash-free rendering on low-power e-readers.
- The display view must include a 15-minute HTTP-equiv meta-refresh (<meta http-equiv="refresh" content="900">) for automated ambient updates.
- All task mutations must be mediated by an append-only event log (L1-002) supporting replay, undo/redo, and offline reconciliation.
- Persistence must be decoupled across Boundary 3 (L1-011_3) separating raw event logs from rendered view caches.
- Request handling must execute inside Demarcated Exception Enclaves (L1-016) containing runtime faults.

GLOSSARY:
- Daily Big 3-5: Mental model bounding active focus tasks to the 3 to 5 highest impact priorities for the day.
- Electrophoretic Display: Physical e-paper screen that retains state without power, but flashes during full redraws.
- Meta-Refresh: Standard HTML header directing browsers to automatically reload the page at a fixed interval.

# ENTITY: TaskItem
MUST HAVE:
- task_id: String
- title: String
- status: Enum (TODO, DONE)
- priority: Integer (1..5)
- tag: String
- is_focus: Boolean
- created_at: Float
- completed_at: Optional[Float]

RULES:
- R1: When status transitions to DONE, completed_at must record the monotonic timestamp.
- R2: Priority must be an integer between 1 and 5.

# ENTITY: TaskEvent
MUST HAVE:
- event_id: String
- event_type: Enum (TASK_CREATED, TASK_TOGGLED, TASK_REORDERED, TASK_DELETED, FOCUS_SET)
- payload: Dictionary
- timestamp: Float

RULES:
- R1: Events are strictly append-only and immutable. State is derived via deterministic left-fold reduction.

# EVENT: TaskCreated
MUST HAVE:
- task_id: String
- title: String
- priority: Integer
- timestamp: Float

# EVENT: TaskToggled
MUST HAVE:
- task_id: String
- new_status: Enum (TODO, DONE)
- timestamp: Float
