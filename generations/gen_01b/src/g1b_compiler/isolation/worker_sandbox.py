"""Synthesis Worker Sandbox for System G1b (Guardrail 3).

Grounded in [L1-015_1] (Compositional Boundary Isolation).
Workers operate on strictly local interfaces, blind to global ambient prompts.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from g1b_compiler.ir.contract_ir import NounContract, VerbContract


@dataclass
class LocalWorkerTask:
    task_id: str
    target_component: str
    input_contract: Dict[str, Any]
    output_contract: Dict[str, Any]
    local_invariants: List[str]


class SynthesisWorkerSandbox:
    """Encapsulates worker execution to local interface specifications."""

    def __init__(self, task: LocalWorkerTask):
        self.task = task

    def get_scoped_prompt(self) -> str:
        """Returns strictly scoped prompt containing only local interfaces."""
        return (
            f"TASK: Implement {self.task.target_component}\n"
            f"INPUT INTERFACE: {self.task.input_contract}\n"
            f"OUTPUT INTERFACE: {self.task.output_contract}\n"
            f"LOCAL INVARIANTS: {', '.join(self.task.local_invariants)}\n"
            "NOTE: Do not assume ambient global variables or external state beyond the declared interfaces."
        )
