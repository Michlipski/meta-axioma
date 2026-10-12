# Axioma E-Ink: Asynchronous Task Router for Electrophoretic Displays

> **Portfolio System 05** • Port `8096` • Generation `gen_01`  
> Ambient focus routing for e-paper displays (Kindle / Kobo / Boox) coupled with a reactive desktop and mobile priority studio.

---

## 1. Overview & Architectural Thesis

Modern productivity tools suffer from notification saturation and continuous visual distraction. **Axioma E-Ink** bridges low-power, zero-distraction ambient e-paper hardware with high-frequency desktop/mobile task capture.

Adhering to **Directive 3 (Plan-First & Human Usability $P_1$)**, the system decouples high-speed priority management from the calm, glanceable consumption of daily work.

### Hardware Interface Constraints
1. **Strict Zero-JavaScript (`/display`):** No `<script>` tags, zero DOM scripting. Kindle WebKit browsers run in severely memory-constrained sandbox environments where client-side JavaScript routinely crashes.
2. **15-Minute Meta-Refresh:** Includes `<meta http-equiv="refresh" content="900">` for automated ambient page reload. The Kindle display sleeps peacefully between refreshes with zero CPU or battery draw.
3. **Electrophoretic Typography:** 1-bit high-contrast black/white typography with zero CSS animations or transitions, eliminating screen flash flicker.
4. **Daily Big 3–5 Bounded Focus:** Restricts active ambient focus tasks to a maximum of 5 items. Additional items are preserved in a decoupled inbox/backlog.

---

## 2. Axiomatic Mapping & Invariants

| Axiom ID | Formal Principle | Concrete Implementation in `axioma_eink` |
|---|---|---|
| **L1-002** | Functorial Event Sourcing | All task mutations (`TASK_CREATED`, `TASK_TOGGLED`, `TASK_REORDERED`, `TASK_DELETED`, `FOCUS_SET`) are persisted to an append-only JSON stream in `data/events.json`. Current state is derived via pure deterministic left-fold replay. |
| **L1-004** | State Transition Determinism | State reducer strictly evaluates events in sequence without external side effects. |
| **L1-008** | Functorial Reversibility | Full undo capability (`POST /api/undo` / `Cmd+Z`) via automatic generation of compensatory events appended to the event log. |
| **L1-011_3** | Decoupled Persistence | Complete separation between the append-only event stream and view generation pipelines (`display_renderer.py`). |
| **L1-015** | Thermodynamic Compute Bounds | Zero client-side computation on e-reader devices; static pre-rendered HTML payloads under 10 KB. |
| **L1-016** | Exception Enclave Isolation | All HTTP routes execute within `ExceptionEnclave` boundaries, returning structured witness records upon unexpected exceptions. |
| **NEG-G2-003** | Main Flow & Domain Test Gate | 100% automated test coverage across event replay, Big 3-5 focus cap enforcement, zero-JS validation, and HTTP endpoints. |

---

## 3. Endpoints & API Reference

| Endpoint | Method | Description |
|---|---|---|
| `/` | `GET` | Desktop & Mobile Priority Management Studio with embedded hardware simulator. |
| `/display` | `GET` | **Zero-JS Ambient Electrophoretic View** with `<meta http-equiv="refresh" content="900">`. |
| `/display/raw` | `GET` | Plaintext priority glanceboard for terminal or curl inspection. |
| `/api/tasks` | `GET` | Returns partitioned active focus tasks and backlog items with event metadata. |
| `/api/tasks` | `POST` | Creates a new task. Rejects 6th focus task with `422` unless demoted to backlog. |
| `/api/tasks/{id}/toggle` | `POST` | Toggles status between `TODO` and `DONE`. |
| `/api/tasks/{id}/focus` | `POST` | Promotes/demotes task between Daily Big 3-5 board and backlog. |
| `/api/tasks/reorder` | `POST` | Updates priority order of focus items. |
| `/api/tasks/{id}` | `DELETE` | Removes task from board. |
| `/api/undo` | `POST` | Synthesizes and appends compensatory event for the most recent action. |
| `/api/feedback` | `POST` | Appends transgenerational feedback to `data/feedback.json`. |
| `/api/telemetry` | `GET` | System health, event counts, and enclave safety telemetry. |
| `/health` | `GET` | Standard health check probe. |

---

## 4. Hardware Setup (Kindle / Kobo)

1. Connect your Kindle or Kobo to the same Wi-Fi network as your host machine.
2. Launch the Experimental Web Browser on the e-reader:
   - Kindle: Menu $\to$ Experimental Browser $\to$ Navigate to `http://<YOUR_LAN_IP>:8096/display`.
3. Set your Kindle on your desk or beside your workstation. It will automatically update every 15 minutes, consuming zero power while displaying your Daily Big 3–5 priorities.
