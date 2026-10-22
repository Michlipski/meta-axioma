"""Token Meter & Real Artifact Accounting for System G2b.

Provides deterministic, physical token measurement of prompts, emitted code files,
IR specifications, and runtime execution logs to ensure all reported token expenditures
are grounded in real computational artifacts.
"""

from pathlib import Path
import re
from typing import Any, Dict, List, Optional
from g2b_compiler.recursion.models import RecursionNode, WorkerType


class TokenMeter:
    """Measures, records, and verifies real physical token expenditures."""

    # Standard BPE-aligned regex token pattern
    TOKEN_REGEX = re.compile(r"[a-zA-Z_]\w*|\d+|[^\w\s]|\s+")

    @classmethod
    def count_tokens(cls, text: str) -> int:
        """Counts tokens in a string using standard word/punctuation/whitespace BPE alignment."""
        if not text:
            return 0
        return len(cls.TOKEN_REGEX.findall(text))

    @classmethod
    def measure_file(cls, file_path: Path) -> int:
        """Measures physical tokens in a file on disk."""
        if not file_path.exists() or not file_path.is_file():
            return 0
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            return cls.count_tokens(content)
        except Exception:
            return 0

    @classmethod
    def measure_directory(cls, dir_path: Path) -> Dict[str, Any]:
        """Measures physical tokens across all emitted code and data files in an app directory."""
        if not dir_path.exists():
            return {"file_count": 0, "total_code_tokens": 0, "files": {}}

        files_map: Dict[str, int] = {}
        total_tokens = 0
        # Exclude pycache and binary files
        for f in dir_path.glob("**/*"):
            if f.is_file() and not f.name.endswith((".pyc", ".html", ".md")) and "__pycache__" not in str(f):
                toks = cls.measure_file(f)
                rel_name = str(f.relative_to(dir_path))
                files_map[rel_name] = toks
                total_tokens += toks

        return {
            "file_count": len(files_map),
            "total_tokens": total_tokens,
            "total_code_tokens": total_tokens,
            "files": files_map,
        }

    @classmethod
    def audit_recursion_tree(cls, root: RecursionNode) -> Dict[str, Any]:
        """Validates that parent allotments are inclusive and child spends sum up correctly."""
        root.reconcile_totals()

        node_records: List[Dict[str, Any]] = []
        imbalances: List[str] = []

        def visit(node: RecursionNode):
            child_allotted_sum = sum(c.token_cost for c in node.children)
            child_used_sum = sum(c.tokens_used for c in node.children)

            # Check hierarchical inclusive allotment invariant:
            # node.token_cost >= node.self_allotted + sum(child.token_cost)
            expected_min_allotted = (node.self_allotted or 0) + child_allotted_sum
            if node.children and node.token_cost < expected_min_allotted:
                imbalances.append(
                    f"Node {node.node_id} ({node.name}) allotment {node.token_cost} is less than self ({node.self_allotted}) + children sum ({child_allotted_sum})"
                )

            # Check usage reconciliation invariant:
            # node.tokens_used == node.self_used + child_used_sum
            if node.tokens_used != (node.self_used + child_used_sum):
                imbalances.append(
                    f"Node {node.node_id} ({node.name}) tokens_used {node.tokens_used} != self_used ({node.self_used}) + children used ({child_used_sum})"
                )

            node_records.append({
                "node_id": node.node_id,
                "name": node.name,
                "worker_type": node.worker_type.value if hasattr(node.worker_type, "value") else str(node.worker_type),
                "subgoal": node.subgoal,
                "depth": node.depth,
                "total_allotted": node.token_cost,
                "self_allotted": node.self_allotted,
                "self_used": node.self_used,
                "sub_tree_used": node.tokens_used,
                "child_count": len(node.children),
            })

            for c in node.children:
                visit(c)

        visit(root)

        total_exploratory_allotted = sum(
            (n["self_allotted"] or 0) for n in node_records if not WorkerType(n["worker_type"]).is_terminal
        )
        total_protected_allotted = sum(
            (n["self_allotted"] or 0) for n in node_records if WorkerType(n["worker_type"]).is_terminal
        )
        total_exploratory_used = sum(
            n["self_used"] for n in node_records if not WorkerType(n["worker_type"]).is_terminal
        )
        total_protected_used = sum(
            n["self_used"] for n in node_records if WorkerType(n["worker_type"]).is_terminal
        )

        return {
            "root_allotted": root.token_cost,
            "root_used": root.tokens_used,
            "total_nodes": len(node_records),
            "exploratory_allotted": total_exploratory_allotted,
            "protected_allotted": total_protected_allotted,
            "exploratory_used": total_exploratory_used,
            "protected_used": total_protected_used,
            "is_balanced": len(imbalances) == 0,
            "imbalances": imbalances,
            "nodes": node_records,
        }
