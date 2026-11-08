#!/usr/bin/env python3
"""AST Skeletonizer CLI (`scripts/skeleton.py`).

Provides rapid, token-efficient interface skeletonization for developer pair-programming,
interactive Antigravity agent sessions, and compiler subagents.

Enforces:
- [L1-G4B-007] Strips function and method bodies into typed interface stubs (`...`).
- [L1-G4B-008] Guarantees extracted prompt context <= 4,096 BPE tokens.
- Preserves class hierarchies, signatures, docstrings, and type annotations.
- Emits human-readable code stubs or structured JSON snapshots.

Usage:
    python scripts/skeleton.py path/to/module.py
    python scripts/skeleton.py path/to/dir/ --recursive --stats
    python scripts/skeleton.py path/to/module.py --json
    cat module.py | python scripts/skeleton.py -
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path
import sys
import time
from typing import Any, Dict, List, Optional, Tuple

# Ensure repository root and Gen 4b builder service are in sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
BUILDER_ROOT = REPO_ROOT / "generations" / "gen_04b" / "services" / "builder"

for p in [str(REPO_ROOT), str(BUILDER_ROOT)]:
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from generations.gen_04b.services.builder.src.ast_skeletonizer import ASTSkeletonizer
    from generations.gen_04b.services.builder.src.domain_models import ASTSkeletonSnapshot
except ImportError:
    # Direct import fallback if running inside builder directory
    try:
        from src.ast_skeletonizer import ASTSkeletonizer
        from src.domain_models import ASTSkeletonSnapshot
    except ImportError:
        # Hermetic standalone fallback if builder modules unavailable
        class ASTSkeletonizer:  # type: ignore[no-redef]
            MAX_BPE_TOKENS = 4096

            def __init__(self, token_char_ratio: float = 3.6):
                self.token_char_ratio = token_char_ratio

            def estimate_bpe_tokens(self, text: str) -> int:
                if not text:
                    return 0
                return max(int(len(text) / self.token_char_ratio), len(text.split()))

            def extract_skeleton(self, source_code: str, module_path: str = "module.py", symbol_urn: str = ""):
                try:
                    tree = ast.parse(source_code, filename=module_path)
                except SyntaxError as exc:
                    stub = f"# SyntaxError in {module_path}: {exc.msg}\nclass IncompleteModule:\n    pass\n"
                    return type("ASTSkeletonSnapshot", (), {
                        "snapshot_id": f"skel_{hashlib.sha256(module_path.encode()).hexdigest()[:12]}",
                        "source_module_path": module_path,
                        "symbol_urn": symbol_urn,
                        "skeleton_code": stub,
                        "stripped_byte_count": max(0, len(source_code.encode()) - len(stub.encode())),
                        "preserved_signatures": [f"SyntaxError({exc.msg})"],
                        "estimated_bpe_tokens": self.estimate_bpe_tokens(stub),
                        "to_dict": lambda s: {
                            "source_module_path": module_path,
                            "estimated_bpe_tokens": s.estimated_bpe_tokens,
                            "skeleton_code": s.skeleton_code,
                        }
                    })()

                preserved_signatures: List[str] = []

                class SkeletonTransformer(ast.NodeTransformer):
                    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.AST:
                        args_repr = ", ".join(arg.arg for arg in node.args.args)
                        preserved_signatures.append(f"def {node.name}({args_repr})")
                        doc = ast.get_docstring(node)
                        new_body: List[ast.stmt] = []
                        if doc:
                            new_body.append(ast.Expr(value=ast.Constant(value=doc)))
                        new_body.append(ast.Expr(value=ast.Constant(value=Ellipsis)))
                        node.body = new_body
                        return node

                    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> ast.AST:
                        args_repr = ", ".join(arg.arg for arg in node.args.args)
                        preserved_signatures.append(f"async def {node.name}({args_repr})")
                        doc = ast.get_docstring(node)
                        new_body: List[ast.stmt] = []
                        if doc:
                            new_body.append(ast.Expr(value=ast.Constant(value=doc)))
                        new_body.append(ast.Expr(value=ast.Constant(value=Ellipsis)))
                        node.body = new_body
                        return node

                    def visit_ClassDef(self, node: ast.ClassDef) -> ast.AST:
                        bases = ", ".join(ast.unparse(b) for b in node.bases)
                        preserved_signatures.append(f"class {node.name}({bases})")
                        self.generic_visit(node)
                        if not node.body:
                            node.body = [ast.Pass()]
                        return node

                transformer = SkeletonTransformer()
                transformed = transformer.visit(tree)
                ast.fix_missing_locations(transformed)
                code = ast.unparse(transformed)
                tokens = self.estimate_bpe_tokens(code)
                return type("ASTSkeletonSnapshot", (), {
                    "snapshot_id": f"skel_{hashlib.sha256(module_path.encode()).hexdigest()[:12]}",
                    "source_module_path": module_path,
                    "symbol_urn": symbol_urn,
                    "skeleton_code": code,
                    "stripped_byte_count": max(0, len(source_code.encode()) - len(code.encode())),
                    "preserved_signatures": preserved_signatures,
                    "estimated_bpe_tokens": tokens,
                    "to_dict": lambda s: {
                        "source_module_path": module_path,
                        "estimated_bpe_tokens": s.estimated_bpe_tokens,
                        "skeleton_code": s.skeleton_code,
                        "preserved_signatures": s.preserved_signatures,
                    }
                })()


def process_source(
    skeletonizer: ASTSkeletonizer,
    source_code: str,
    module_path: str,
    max_tokens: int = 4096,
) -> Any:
    """Extracts and formats the AST skeleton snapshot."""
    stem = Path(module_path).stem.replace("-", "_")
    return skeletonizer.extract_skeleton(
        source_code=source_code,
        module_path=module_path,
        symbol_urn=f"urn:axioma:g4b:cli:{stem}",
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Extract typed interface skeletons from Python source modules to minimize agent token spend."
    )
    parser.add_argument(
        "paths",
        nargs="+",
        help="One or more Python file paths, directory paths, or '-' for standard input.",
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=4096,
        help="Maximum BPE token limit for emitted skeleton (default: 4096).",
    )
    parser.add_argument(
        "-r", "--recursive",
        action="store_true",
        help="Recursively scan directories for .py files.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="emit_json",
        help="Emit structured JSON with metadata and signatures instead of raw code.",
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Emit a Markdown summary table of compression statistics.",
    )

    args = parser.parse_args()
    skeletonizer = ASTSkeletonizer()
    skeletonizer.MAX_BPE_TOKENS = args.max_tokens

    # Collect files
    files_to_process: List[Tuple[str, str]] = []  # (display_path, content)

    for p in args.paths:
        if p == "-":
            stdin_content = sys.stdin.read()
            files_to_process.append(("stdin", stdin_content))
            continue

        target = Path(p)
        if not target.exists():
            print(f"Error: path does not exist: {p}", file=sys.stderr)
            return 1

        if target.is_file():
            try:
                content = target.read_text(encoding="utf-8", errors="ignore")
                files_to_process.append((str(target), content))
            except Exception as e:
                print(f"Error reading {p}: {e}", file=sys.stderr)
        elif target.is_dir():
            pattern = "**/*.py" if args.recursive else "*.py"
            for py_file in sorted(target.glob(pattern)):
                if any(ignored in str(py_file) for ignored in [".git", "__pycache__", ".scratch", "node_modules"]):
                    continue
                try:
                    content = py_file.read_text(encoding="utf-8", errors="ignore")
                    files_to_process.append((str(py_file), content))
                except Exception as e:
                    print(f"Error reading {py_file}: {e}", file=sys.stderr)

    if not files_to_process:
        print("No Python files found to process.", file=sys.stderr)
        return 1

    snapshots = []
    stats_data = []

    for display_path, content in files_to_process:
        t0 = time.perf_counter()
        snapshot = process_source(skeletonizer, content, display_path, max_tokens=args.max_tokens)
        elapsed_ms = (time.perf_counter() - t0) * 1000

        raw_tokens = skeletonizer.estimate_bpe_tokens(content)
        skel_tokens = snapshot.estimated_bpe_tokens
        reduction = ((raw_tokens - skel_tokens) / max(1, raw_tokens)) * 100

        snapshots.append(snapshot)
        stats_data.append({
            "path": display_path,
            "raw_bytes": len(content.encode("utf-8")),
            "skel_bytes": len(snapshot.skeleton_code.encode("utf-8")),
            "raw_tokens": raw_tokens,
            "skel_tokens": skel_tokens,
            "reduction_pct": reduction,
            "latency_ms": elapsed_ms,
        })

    if args.stats:
        print("| File | Raw Tokens | Skeleton Tokens | Reduction % | Latency |")
        print("|---|---|---|---|---|")
        total_raw = sum(s["raw_tokens"] for s in stats_data)
        total_skel = sum(s["skel_tokens"] for s in stats_data)
        total_reduc = ((total_raw - total_skel) / max(1, total_raw)) * 100 if total_raw > 0 else 0
        for s in stats_data:
            print(f"| `{Path(s['path']).name}` | {s['raw_tokens']:,} | {s['skel_tokens']:,} | {s['reduction_pct']:.1f}% | {s['latency_ms']:.2f}ms |")
        if len(stats_data) > 1:
            print(f"| **TOTAL ({len(stats_data)} files)** | **{total_raw:,}** | **{total_skel:,}** | **{total_reduc:.1f}%** | - |")
        return 0

    if args.emit_json:
        out = [s.to_dict() if hasattr(s, "to_dict") else {
            "source_module_path": s.source_module_path,
            "estimated_bpe_tokens": s.estimated_bpe_tokens,
            "skeleton_code": s.skeleton_code,
            "preserved_signatures": getattr(s, "preserved_signatures", []),
        } for s in snapshots]
        print(json.dumps(out if len(out) > 1 else out[0], indent=2))
        return 0

    # Default output: formatted skeleton code
    for i, s in enumerate(snapshots):
        if len(snapshots) > 1:
            print(f"# ==============================================================================")
            print(f"# File: {s.source_module_path} (Estimated BPE Tokens: {s.estimated_bpe_tokens})")
            print(f"# ==============================================================================\n")
        print(s.skeleton_code)
        if len(snapshots) > 1 and i < len(snapshots) - 1:
            print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
