#!/usr/bin/env python3
"""Compiles the flagship production application 'Axioma Flow' using System G_1."""

import sys
from pathlib import Path

# Add G1 compiler to sys.path
g1_src = Path(__file__).parent / "src"
sys.path.insert(0, str(g1_src))

from g1_compiler import (
    ApplicationCompiler,
    ApplicationSpec,
    AppModelSpec,
    AppModelField,
    AppActionSpec,
)

def compile_axioma_flow():
    spec = ApplicationSpec(
        app_id="axioma_flow",
        title="Axioma Flow",
        tagline="The Invariant-Bounded, Landauer-Audited Workspace",
        description=(
            "A local-first, distraction-free Kanban & Task Orchestrator compiled autonomously "
            "by System G_1 to realize the High-Level Jettison. Built for engineers and systems thinkers "
            "who demand provable state safety, reversible history (time-travel undo/redo), "
            "zero external dependencies, and real-time thermodynamic efficiency."
        ),
        target_persona="Autonomous AI System Architect & Software Engineer",
        ergonomic_goals=[
            "Zero cognitive friction with instant drag-and-drop state transitions.",
            "Keyboard-first workflow with native Cmd+Z / Cmd+Shift+Z functorial time travel.",
            "Live Landauer bit-erasure and Joule tracking on every state mutation.",
            "Humane, non-destructive error handling via Demarcated Exception Enclaves.",
            "Completely self-contained with zero paid or external dependencies.",
        ],
        port=8088,
        models=[
            AppModelSpec(
                name="Task",
                plural_name="tasks",
                fields=[
                    AppModelField("id", "str", required=True),
                    AppModelField("title", "str", required=True),
                    AppModelField("description", "str", required=False),
                    AppModelField("status", "str", required=True, default="backlog"),
                    AppModelField("priority", "str", required=True, default="medium"),
                    AppModelField("created_at", "float", required=True),
                ],
            )
        ],
        actions=[
            AppActionSpec("CREATE_ITEM", "IDLE", "STATE_UPDATED", "Creates a new task payload"),
            AppActionSpec("UPDATE_ITEM", "IDLE", "STATE_UPDATED", "Updates task fields"),
            AppActionSpec("DELETE_ITEM", "IDLE", "STATE_UPDATED", "Deletes task and audits bit erasure"),
            AppActionSpec("MOVE_ITEM", "IDLE", "STATE_UPDATED", "Transitions task between Kanban columns"),
        ],
        initial_seed_data={
            "tasks": [
                {
                    "id": "task_101",
                    "title": "Implement Landauer Dissipation Accounting",
                    "description": "Formally account for erased computational bits against kB T ln 2.",
                    "status": "done",
                    "priority": "critical",
                    "created_at": 1776000000.0,
                },
                {
                    "id": "task_102",
                    "title": "Integrate Zero-Trust MCP Dual-Boundary Gateway",
                    "description": "Validate Noun schemas and Verb FSM state automata transitions.",
                    "status": "done",
                    "priority": "high",
                    "created_at": 1776001000.0,
                },
                {
                    "id": "task_103",
                    "title": "Functorial Time-Travel (Undo/Redo)",
                    "description": "Ensure category-theoretic morphism reversibility across all state transitions.",
                    "status": "in_progress",
                    "priority": "high",
                    "created_at": 1776002000.0,
                },
                {
                    "id": "task_104",
                    "title": "Demarcate Exception Enclaves for Edge Cases",
                    "description": "Isolate failure blast radiuses and provide humane, actionable error recovery.",
                    "status": "review",
                    "priority": "medium",
                    "created_at": 1776003000.0,
                },
                {
                    "id": "task_105",
                    "title": "Prepare Generation 2 Successor Handover",
                    "description": "Endogenously formulate evaluation targets and foundational basis for G2.",
                    "status": "backlog",
                    "priority": "medium",
                    "created_at": 1776004000.0,
                },
            ]
        },
    )

    compiler = ApplicationCompiler()
    app_dir = compiler.compile(spec)
    print(f"✨ Successfully compiled '{spec.title}' into: {app_dir}")
    return app_dir

if __name__ == "__main__":
    compile_axioma_flow()
