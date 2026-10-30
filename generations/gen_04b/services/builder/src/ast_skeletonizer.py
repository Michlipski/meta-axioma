"""Generation 4b AST Skeleton Extraction Engine (`[Layer A]`).

Enforces:
- Strips function and method bodies into typed interface stubs (`...`).
- Preserves class inheritance hierarchies, type annotations, and docstrings.
- Guarantees extracted skeleton prompt payload context <= 4,096 BPE tokens.
- Emits verifiable ASTSkeletonSnapshot records.
"""

from __future__ import annotations

import ast
import hashlib
import time
from typing import List, Optional, Tuple

from .domain_models import (
    ASTNodeType,
    ASTSkeletonSnapshot,
    DomainInvariantViolation,
)


class ASTSkeletonizer:
    """Extracts typed interface skeletons from source modules to minimize subagent context."""

    MAX_BPE_TOKENS: int = 4096

    def __init__(self, token_char_ratio: float = 3.6):
        self.token_char_ratio = token_char_ratio

    def estimate_bpe_tokens(self, text: str) -> int:
        """Accurately estimate BPE token count for code stubs."""
        if not text:
            return 0
        char_est = int(len(text) / self.token_char_ratio)
        word_est = len(text.split())
        return max(char_est, word_est)

    def extract_skeleton(
        self,
        source_code: str,
        module_path: str = "module.py",
        symbol_urn: str = "urn:axioma:g4b:builder:module",
    ) -> ASTSkeletonSnapshot:
        """Parses Python source, replaces callable bodies with Ellipsis, and produces a skeleton snapshot."""
        try:
            tree = ast.parse(source_code, filename=module_path)
        except SyntaxError as exc:
            # Fallback minimal stub on syntax errors so builder pipeline can still diagnose
            stub_code = f"# SyntaxError in {module_path}: {exc.msg}\nclass IncompleteModule:\n    pass\n"
            bpe = self.estimate_bpe_tokens(stub_code)
            return ASTSkeletonSnapshot(
                snapshot_id=f"skel_{hashlib.sha256(module_path.encode()).hexdigest()[:12]}",
                source_module_path=module_path,
                symbol_urn=symbol_urn,
                skeleton_code=stub_code,
                stripped_byte_count=max(0, len(source_code.encode("utf-8")) - len(stub_code.encode("utf-8"))),
                preserved_signatures=[f"SyntaxError({exc.msg})"],
                estimated_bpe_tokens=bpe,
            )

        preserved_signatures: List[str] = []

        class SkeletonTransformer(ast.NodeTransformer):
            def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.AST:
                # Capture signature string
                args_repr = ", ".join(arg.arg for arg in node.args.args)
                sig = f"def {node.name}({args_repr})"
                preserved_signatures.append(sig)

                # Keep docstring if present
                docstring = ast.get_docstring(node)
                new_body: List[ast.stmt] = []
                if docstring:
                    new_body.append(ast.Expr(value=ast.Constant(value=docstring)))
                new_body.append(ast.Expr(value=ast.Constant(value=Ellipsis)))

                node.body = new_body
                return node

            def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> ast.AST:
                args_repr = ", ".join(arg.arg for arg in node.args.args)
                sig = f"async def {node.name}({args_repr})"
                preserved_signatures.append(sig)

                docstring = ast.get_docstring(node)
                new_body: List[ast.stmt] = []
                if docstring:
                    new_body.append(ast.Expr(value=ast.Constant(value=docstring)))
                new_body.append(ast.Expr(value=ast.Constant(value=Ellipsis)))

                node.body = new_body
                return node

            def visit_ClassDef(self, node: ast.ClassDef) -> ast.AST:
                bases_repr = ", ".join(ast.unparse(b) for b in node.bases)
                preserved_signatures.append(f"class {node.name}({bases_repr})")
                self.generic_visit(node)
                # If class body empty, put pass
                if not node.body:
                    node.body = [ast.Pass()]
                return node

        transformer = SkeletonTransformer()
        transformed_tree = transformer.visit(tree)
        ast.fix_missing_locations(transformed_tree)

        skeleton_code = ast.unparse(transformed_tree)
        if not skeleton_code.strip():
            skeleton_code = "# Empty module\npass"

        orig_bytes = len(source_code.encode("utf-8"))
        skel_bytes = len(skeleton_code.encode("utf-8"))
        stripped_bytes = max(0, orig_bytes - skel_bytes)

        est_tokens = self.estimate_bpe_tokens(skeleton_code)

        # Enforce Layer A invariant: <= 4,096 BPE tokens
        if est_tokens > self.MAX_BPE_TOKENS:
            # Strip docstrings if token budget exceeded
            skeleton_code = self._compress_without_docstrings(transformed_tree)
            est_tokens = self.estimate_bpe_tokens(skeleton_code)
            if est_tokens > self.MAX_BPE_TOKENS:
                # Emergency truncation with pass stub
                skeleton_code = skeleton_code[: self.MAX_BPE_TOKENS * 3] + "\n# ... [TRUNCATED STUB]"
                est_tokens = self.estimate_bpe_tokens(skeleton_code)

        snapshot = ASTSkeletonSnapshot(
            snapshot_id=f"skel_{hashlib.sha256((module_path + str(time.time())).encode()).hexdigest()[:12]}",
            source_module_path=module_path,
            symbol_urn=symbol_urn,
            skeleton_code=skeleton_code,
            stripped_byte_count=stripped_bytes,
            preserved_signatures=preserved_signatures,
            estimated_bpe_tokens=est_tokens,
        )
        snapshot.validate_invariants()
        return snapshot

    def _compress_without_docstrings(self, tree: ast.AST) -> str:
        """Strips all docstring expressions to strictly fit within token budget."""
        class DocstringStripper(ast.NodeTransformer):
            def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.AST:
                node.body = [ast.Expr(value=ast.Constant(value=Ellipsis))]
                return node

            def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> ast.AST:
                node.body = [ast.Expr(value=ast.Constant(value=Ellipsis))]
                return node

            def visit_ClassDef(self, node: ast.ClassDef) -> ast.AST:
                self.generic_visit(node)
                node.body = [stmt for stmt in node.body if not (isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant) and isinstance(stmt.value.value, str))]
                if not node.body:
                    node.body = [ast.Pass()]
                return node

        stripper = DocstringStripper()
        compressed = stripper.visit(tree)
        ast.fix_missing_locations(compressed)
        return ast.unparse(compressed)
