"""Domain models and data definitions for Axioma E-Ink Task Router.

Employs Functorial Event Sourcing ([L1-002]) and Decoupled Persistence ([L1-011_3]).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
import time
from typing import Any, Dict, List, Optional


class TaskStatus(str, Enum):
    TODO = "TODO"
    DONE = "DONE"


class EventType(str, Enum):
    TASK_CREATED = "TASK_CREATED"
    TASK_TOGGLED = "TASK_TOGGLED"
    TASK_REORDERED = "TASK_REORDERED"
    TASK_DELETED = "TASK_DELETED"
    FOCUS_SET = "FOCUS_SET"


@dataclass
class TaskItem:
    task_id: str
    title: str
    status: TaskStatus = TaskStatus.TODO
    priority: int = 1  # 1 to 5 for Big 3-5
    tag: str = "@focus"
    is_focus: bool = True
    created_at: float = field(default_factory=time.time)
    completed_at: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "title": self.title,
            "status": self.status.value,
            "priority": self.priority,
            "tag": self.tag,
            "is_focus": self.is_focus,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> TaskItem:
        return cls(
            task_id=data["task_id"],
            title=data["title"],
            status=TaskStatus(data.get("status", "TODO")),
            priority=int(data.get("priority", 1)),
            tag=data.get("tag", "@focus"),
            is_focus=data.get("is_focus", True),
            created_at=data.get("created_at", time.time()),
            completed_at=data.get("completed_at"),
        )


@dataclass
class TaskEvent:
    event_id: str
    event_type: EventType
    payload: Dict[str, Any]
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "payload": self.payload,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> TaskEvent:
        return cls(
            event_id=data["event_id"],
            event_type=EventType(data["event_type"]),
            payload=data.get("payload", {}),
            timestamp=data.get("timestamp", time.time()),
        )


@dataclass
class EinkBoardState:
    board_title: str
    sync_timestamp: float
    total_focus_tasks: int
    completed_count: int
    tasks: List[TaskItem]
    quote_of_the_day: str = "Simplicity is prerequisite for reliability. — Dijkstra"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "board_title": self.board_title,
            "sync_timestamp": self.sync_timestamp,
            "total_focus_tasks": self.total_focus_tasks,
            "completed_count": self.completed_count,
            "tasks": [t.to_dict() for t in self.tasks],
            "quote_of_the_day": self.quote_of_the_day,
        }


@dataclass
class FeedbackItem:
    feedback_id: str
    category: str
    comment: str
    timestamp: float = field(default_factory=time.time)
    generation: str = "gen_01"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
