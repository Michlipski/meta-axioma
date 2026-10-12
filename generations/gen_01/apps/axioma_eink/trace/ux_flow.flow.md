---
flow: EinkTaskRoutingWorkflow
persona: AmbientFocusWorker
domains:
  - AxiomaEink
  - AppSpecification
  - GenerationalFeedback
---

# WORKFLOW: Daily Focus Orchestration & Ambient E-Ink Routing

> GOAL: Enable calm, non-distracting daily priority management across phones/laptops while routing a high-contrast, zero-JS ambient glanceboard to electrophoretic e-reader screens.

---

## FLOW 1: Daily Big 3-5 Focus Formulation
1. Operator opens management dashboard (`http://localhost:8096`) on phone or laptop.
2. Selects or adds up to 5 high-impact focus tasks for today.
3. System assigns priority rank (1 through 5) and optional context tag (e.g. `@work`, `@deepwork`).
4. Event stream records `TASK_CREATED` and `FOCUS_SET`.
5. State reducer recalculates the Daily Big 3-5 focus snapshot.

---

## FLOW 2: Ambient E-Ink Display Auto-Refresh
1. E-reader device (Kindle/Kobo) opens `http://<local-ip>:8096/display`.
2. Server serves static, zero-JavaScript HTML with high-contrast electrophoretic typography.
3. Display shows current date, completion progress (e.g. "2 of 4 done"), and the Big 3-5 items formatted in large font.
4. Browser schedules next refresh in 900 seconds (`<meta http-equiv="refresh" content="900">`).
5. E-reader screen sleeps peacefully with zero CPU or socket battery drain.

---

## FLOW 3: Task Completion & State Reconciliation
1. Operator finishes a priority item and taps checkmark on phone.
2. Event `TASK_TOGGLED` appended with status `DONE`.
3. Functorial history records mutation for 1-tap `Cmd+Z` undo.
4. Upon next 15-minute refresh (or immediate manual reload on e-reader), completed item displays with a bold checkmark and clean strike-through.

---

## FLOW 4: Hardware Simulator Inspection
1. Operator reviews tasks on desktop before walking away.
2. Desktop dashboard features an integrated "E-Ink Simulator" showing the exact 1-bit monochrome appearance of the e-reader screen.
3. Confirms readability and visual balance before leaving desk.

---

## FLOW 5: Transgenerational User Feedback
1. Operator reports hardware refresh artifacts or mental-model divergence via the in-app `💬 Feedback` widget.
2. Submits payload to `POST /api/feedback`, persisting directly into the Generation G1/G2 learning dossier.
