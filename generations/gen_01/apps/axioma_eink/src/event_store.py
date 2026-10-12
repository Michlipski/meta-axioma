"""Append-Only Event Store & Deterministic State Reducer for Axioma E-Ink.

Implements Functorial Event Sourcing ([L1-002]) and Decoupled Persistence ([L1-011_3]).
Enforces the Daily Big 3-5 focus invariant (maximum 5 active focus priorities).
"""

from __future__ import annotations

import json
from pathlib import Path
import threading
import time
from typing import Any, Dict, List, Optional, Tuple
import uuid

from models import EinkBoardState, EventType, FeedbackItem, TaskItem, TaskStatus, TaskEvent


class EventStore:
    """Thread-safe, append-only event store with deterministic left-fold state reduction."""

    MAX_FOCUS_TASKS = 5

    def __init__(self, data_path: Optional[Path] = None):
        self.lock = threading.RLock()
        if data_path is None:
            self.data_dir = Path(__file__).parent.parent / "data"
            self.data_file = self.data_dir / "events.json"
        else:
            self.data_file = data_path
            self.data_dir = self.data_file.parent

        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.events: List[TaskEvent] = []
        self.tasks: Dict[str, TaskItem] = {}
        self.undo_stack: List[str] = []  # Stack of reversible event IDs
        self.telemetry = {
            "events_replayed": 0,
            "events_appended": 0,
            "undo_invocations": 0,
            "state_reductions": 0,
            "started_at": time.time(),
        }
        self._load_and_replay()

    def _load_and_replay(self) -> None:
        """Loads all events from disk and rebuilds current state via left-fold replay."""
        with self.lock:
            self.events = []
            self.tasks = {}
            if self.data_file.exists():
                try:
                    with open(self.data_file, "r", encoding="utf-8") as f:
                        raw = json.load(f)
                    if isinstance(raw, list):
                        for item in raw:
                            evt = TaskEvent.from_dict(item)
                            self.events.append(evt)
                            self._apply_event_locked(evt, record_undo=False)
                            self.telemetry["events_replayed"] += 1
                except Exception as e:
                    # In case of corruption or empty file, keep memory clean
                    pass

    def _persist_events_locked(self) -> None:
        """Persists entire event log atomically to disk."""
        tmp_file = self.data_file.with_suffix(".tmp")
        payload = [e.to_dict() for e in self.events]
        with open(tmp_file, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
        tmp_file.replace(self.data_file)

    def _apply_event_locked(self, evt: TaskEvent, record_undo: bool = True) -> None:
        """Pure state transition reducer step."""
        self.telemetry["state_reductions"] += 1
        etype = evt.event_type
        payload = evt.payload

        if etype == EventType.TASK_CREATED:
            task = TaskItem.from_dict(payload["task"])
            self.tasks[task.task_id] = task

        elif etype == EventType.TASK_TOGGLED:
            task_id = payload["task_id"]
            if task_id in self.tasks:
                task = self.tasks[task_id]
                new_status = TaskStatus(payload["new_status"])
                task.status = new_status
                task.completed_at = payload.get("completed_at")

        elif etype == EventType.TASK_REORDERED:
            order = payload.get("task_ids", [])
            for priority_idx, tid in enumerate(order, start=1):
                if tid in self.tasks:
                    self.tasks[tid].priority = priority_idx

        elif etype == EventType.TASK_DELETED:
            task_id = payload["task_id"]
            if task_id in self.tasks:
                del self.tasks[task_id]

        elif etype == EventType.FOCUS_SET:
            task_id = payload["task_id"]
            is_focus = bool(payload["is_focus"])
            if task_id in self.tasks:
                self.tasks[task_id].is_focus = is_focus

        if record_undo and etype != EventType.TASK_REORDERED:
            self.undo_stack.append(evt.event_id)

    # -------------------------------------------------------------------------
    # Public Command API
    # -------------------------------------------------------------------------

    def create_task(
        self,
        title: str,
        priority: Optional[int] = None,
        tag: str = "@focus",
        is_focus: Optional[bool] = None,
    ) -> TaskItem:
        """Creates a new task, enforcing Daily Big 3-5 focus invariant."""
        with self.lock:
            focus_count = sum(1 for t in self.tasks.values() if t.is_focus)
            if is_focus is None:
                # Default to focus if slots remain, otherwise backlog
                is_focus = focus_count < self.MAX_FOCUS_TASKS
            elif is_focus and focus_count >= self.MAX_FOCUS_TASKS:
                raise ValueError(
                    f"Daily Big 3-5 focus invariant violated: maximum {self.MAX_FOCUS_TASKS} active focus priorities allowed."
                )

            task_id = f"task_{uuid.uuid4().hex[:8]}"
            if priority is None:
                priority = min(focus_count + 1, self.MAX_FOCUS_TASKS) if is_focus else 99

            task = TaskItem(
                task_id=task_id,
                title=title.strip(),
                status=TaskStatus.TODO,
                priority=priority,
                tag=tag.strip() if tag else "@focus",
                is_focus=is_focus,
                created_at=time.time(),
            )

            evt = TaskEvent(
                event_id=f"evt_{uuid.uuid4().hex[:8]}",
                event_type=EventType.TASK_CREATED,
                payload={"task": task.to_dict()},
                timestamp=time.time(),
            )

            self.events.append(evt)
            self._apply_event_locked(evt, record_undo=True)
            self._persist_events_locked()
            self.telemetry["events_appended"] += 1
            return task

    def toggle_task(self, task_id: str) -> TaskItem:
        """Toggles task status between TODO and DONE."""
        with self.lock:
            if task_id not in self.tasks:
                raise KeyError(f"Task with ID {task_id} not found.")

            task = self.tasks[task_id]
            new_status = TaskStatus.DONE if task.status == TaskStatus.TODO else TaskStatus.TODO
            completed_at = time.time() if new_status == TaskStatus.DONE else None

            evt = TaskEvent(
                event_id=f"evt_{uuid.uuid4().hex[:8]}",
                event_type=EventType.TASK_TOGGLED,
                payload={
                    "task_id": task_id,
                    "previous_status": task.status.value,
                    "new_status": new_status.value,
                    "completed_at": completed_at,
                },
                timestamp=time.time(),
            )

            self.events.append(evt)
            self._apply_event_locked(evt, record_undo=True)
            self._persist_events_locked()
            self.telemetry["events_appended"] += 1
            return self.tasks[task_id]

    def set_focus(self, task_id: str, is_focus: bool) -> TaskItem:
        """Promotes or demotes task to/from Daily Big 3-5 focus board."""
        with self.lock:
            if task_id not in self.tasks:
                raise KeyError(f"Task with ID {task_id} not found.")

            current_focus_count = sum(1 for t in self.tasks.values() if t.is_focus and t.task_id != task_id)
            if is_focus and current_focus_count >= self.MAX_FOCUS_TASKS:
                raise ValueError(
                    f"Daily Big 3-5 focus invariant violated: maximum {self.MAX_FOCUS_TASKS} active focus priorities allowed."
                )

            evt = TaskEvent(
                event_id=f"evt_{uuid.uuid4().hex[:8]}",
                event_type=EventType.FOCUS_SET,
                payload={"task_id": task_id, "is_focus": is_focus},
                timestamp=time.time(),
            )

            self.events.append(evt)
            self._apply_event_locked(evt, record_undo=True)
            self._persist_events_locked()
            self.telemetry["events_appended"] += 1
            return self.tasks[task_id]

    def reorder_tasks(self, task_ids: List[str]) -> List[TaskItem]:
        """Reorders task priorities."""
        with self.lock:
            # Validate IDs
            for tid in task_ids:
                if tid not in self.tasks:
                    raise KeyError(f"Task with ID {tid} not found.")

            evt = TaskEvent(
                event_id=f"evt_{uuid.uuid4().hex[:8]}",
                event_type=EventType.TASK_REORDERED,
                payload={"task_ids": task_ids},
                timestamp=time.time(),
            )

            self.events.append(evt)
            self._apply_event_locked(evt, record_undo=True)
            self._persist_events_locked()
            self.telemetry["events_appended"] += 1
            return [self.tasks[tid] for tid in task_ids]

    def delete_task(self, task_id: str) -> Dict[str, Any]:
        """Deletes a task by ID."""
        with self.lock:
            if task_id not in self.tasks:
                raise KeyError(f"Task with ID {task_id} not found.")

            deleted_task = self.tasks[task_id]
            evt = TaskEvent(
                event_id=f"evt_{uuid.uuid4().hex[:8]}",
                event_type=EventType.TASK_DELETED,
                payload={"task_id": task_id, "task": deleted_task.to_dict()},
                timestamp=time.time(),
            )

            self.events.append(evt)
            self._apply_event_locked(evt, record_undo=True)
            self._persist_events_locked()
            self.telemetry["events_appended"] += 1
            return {"status": "deleted", "task_id": task_id}

    def undo(self) -> Dict[str, Any]:
        """Undoes the most recent reversible action via compensatory event appending."""
        with self.lock:
            if not self.undo_stack:
                return {"status": "noop", "message": "Nothing to undo."}

            last_event_id = self.undo_stack.pop()
            # Find the corresponding event
            target_evt = next((e for e in reversed(self.events) if e.event_id == last_event_id), None)
            if not target_evt:
                return {"status": "noop", "message": "Event target not found."}

            compensatory_evt: Optional[TaskEvent] = None
            ts = time.time()

            if target_evt.event_type == EventType.TASK_CREATED:
                # Compensatory: delete the created task
                tid = target_evt.payload["task"]["task_id"]
                if tid in self.tasks:
                    compensatory_evt = TaskEvent(
                        event_id=f"evt_undo_{uuid.uuid4().hex[:8]}",
                        event_type=EventType.TASK_DELETED,
                        payload={"task_id": tid, "task": self.tasks[tid].to_dict()},
                        timestamp=ts,
                    )

            elif target_evt.event_type == EventType.TASK_TOGGLED:
                # Compensatory: revert to previous status
                tid = target_evt.payload["task_id"]
                prev_status = target_evt.payload["previous_status"]
                comp_at = None if prev_status == TaskStatus.TODO.value else ts
                compensatory_evt = TaskEvent(
                    event_id=f"evt_undo_{uuid.uuid4().hex[:8]}",
                    event_type=EventType.TASK_TOGGLED,
                    payload={
                        "task_id": tid,
                        "previous_status": target_evt.payload["new_status"],
                        "new_status": prev_status,
                        "completed_at": comp_at,
                    },
                    timestamp=ts,
                )

            elif target_evt.event_type == EventType.TASK_DELETED:
                # Compensatory: recreate the deleted task
                restored_task = target_evt.payload["task"]
                compensatory_evt = TaskEvent(
                    event_id=f"evt_undo_{uuid.uuid4().hex[:8]}",
                    event_type=EventType.TASK_CREATED,
                    payload={"task": restored_task},
                    timestamp=ts,
                )

            elif target_evt.event_type == EventType.FOCUS_SET:
                # Compensatory: invert focus flag
                tid = target_evt.payload["task_id"]
                orig_focus = target_evt.payload["is_focus"]
                compensatory_evt = TaskEvent(
                    event_id=f"evt_undo_{uuid.uuid4().hex[:8]}",
                    event_type=EventType.FOCUS_SET,
                    payload={"task_id": tid, "is_focus": not orig_focus},
                    timestamp=ts,
                )

            if compensatory_evt:
                self.events.append(compensatory_evt)
                self._apply_event_locked(compensatory_evt, record_undo=False)
                self._persist_events_locked()
                self.telemetry["undo_invocations"] += 1
                return {"status": "undone", "undone_event_id": last_event_id, "compensatory_event_id": compensatory_evt.event_id}

            return {"status": "noop", "message": "Cannot synthesize compensatory event."}

    # -------------------------------------------------------------------------
    # Public Read API & Snapshots
    # -------------------------------------------------------------------------

    def get_board_state(self) -> EinkBoardState:
        """Computes current electrophoretic glanceboard state (Daily Big 3-5 focus items)."""
        with self.lock:
            focus_tasks = [t for t in self.tasks.values() if t.is_focus]
            focus_tasks.sort(key=lambda t: (t.priority, t.created_at))
            focus_tasks = focus_tasks[: self.MAX_FOCUS_TASKS]
            completed = sum(1 for t in focus_tasks if t.status == TaskStatus.DONE)

            return EinkBoardState(
                board_title="DAILY FOCUS • BIG 3–5",
                sync_timestamp=time.time(),
                total_focus_tasks=len(focus_tasks),
                completed_count=completed,
                tasks=focus_tasks,
                quote_of_the_day="Simplicity is prerequisite for reliability. — Dijkstra",
            )

    def get_all_tasks(self) -> Dict[str, Any]:
        """Returns partitioned focus and backlog tasks with board statistics."""
        with self.lock:
            board = self.get_board_state()
            all_list = list(self.tasks.values())
            all_list.sort(key=lambda t: (0 if t.is_focus else 1, t.priority, t.created_at))

            focus_items = [t.to_dict() for t in all_list if t.is_focus]
            backlog_items = [t.to_dict() for t in all_list if not t.is_focus]

            return {
                "board": board.to_dict(),
                "focus_tasks": focus_items,
                "backlog_tasks": backlog_items,
                "total_count": len(all_list),
                "total_events": len(self.events),
                "can_undo": len(self.undo_stack) > 0,
            }

    def seed_if_empty(self, seed_data: List[Dict[str, Any]]) -> None:
        """Initializes default tasks if the event store is clean."""
        with self.lock:
            if not self.tasks and not self.events:
                for item in seed_data:
                    title = item.get("title", "")
                    priority = item.get("priority", 1)
                    tag = item.get("tag", "@focus")
                    is_focus = item.get("is_focus", True)
                    # Use un-locked create
                    task_id = f"task_{uuid.uuid4().hex[:8]}"
                    task = TaskItem(
                        task_id=task_id,
                        title=title,
                        status=TaskStatus.DONE if item.get("status") == "DONE" else TaskStatus.TODO,
                        priority=priority,
                        tag=tag,
                        is_focus=is_focus,
                        created_at=time.time(),
                        completed_at=time.time() if item.get("status") == "DONE" else None,
                    )
                    evt = TaskEvent(
                        event_id=f"evt_{uuid.uuid4().hex[:8]}",
                        event_type=EventType.TASK_CREATED,
                        payload={"task": task.to_dict()},
                        timestamp=time.time(),
                    )
                    self.events.append(evt)
                    self._apply_event_locked(evt, record_undo=False)
                self._persist_events_locked()
