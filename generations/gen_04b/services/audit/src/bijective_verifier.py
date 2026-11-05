"""Generation 4b Bijective Contract Verification Engine (`soc_g4b_audit`).

Enforces:
- [L1-G3B-011] Universal Compositional Contract IR & Domain Invariants.
- [L1-G4B-001] Sovereign Mesh Verification Gate.
- Formal Rules:
  - BIJ-001: Strict Bijective Symbol Mapping (Total Injectivity & Surjectivity; Anti-Phantom Invariant).
  - BIJ-002: Cryptographic Docstring & Specification Hash Synchronization (@spec_hash: <sha256>).
  - BIJ-003: Type-Signature & Parameter Morphism Isomorphism.
"""

from __future__ import annotations

import ast
import hashlib
import json
import re
import time
from typing import Any, Dict, List, Optional, Set, Tuple
import uuid

from generations.gen_04b.protocols.deliverable_bundle import ContractBijectivityWitness
from .domain_models import (
    AuditSeverity,
    BijectiveVerificationViolation,
    RogueSymbolViolation,
    SignatureMismatchViolation,
    SpecificationDriftViolation,
    UnimplementedVerbViolation,
)


class BijectiveVerifier:
    """Mathematical verification engine proving bijection between ContractIR and AST code."""

    SPEC_HASH_PATTERN = re.compile(r"@spec_hash:\s*([a-fA-F0-9]{64})")

    def __init__(self, verifier_node_id: str = "node_bijective_sentry") -> None:
        self.verifier_node_id = verifier_node_id

    @staticmethod
    def compute_spec_hash(verb: Any) -> str:
        """Computes deterministic 64-char SHA-256 spec hash for a domain verb."""
        name = getattr(verb, "name", "")
        params = getattr(verb, "parameters", [])
        param_list = []
        for p in params:
            if hasattr(p, "name"):
                param_list.append({"name": p.name, "type_name": getattr(p, "type_name", "")})
            elif isinstance(p, dict):
                param_list.append({"name": p.get("name", ""), "type_name": p.get("type_name", "")})
            else:
                param_list.append({"name": str(p), "type_name": ""})

        return_type = getattr(verb, "return_type", "void")
        pre_conditions = sorted(list(getattr(verb, "pre_conditions", [])))
        post_conditions = sorted(list(getattr(verb, "post_conditions", [])))

        payload = {
            "name": name,
            "parameters": param_list,
            "return_type": return_type,
            "pre_conditions": pre_conditions,
            "post_conditions": post_conditions,
        }
        canonical_json = json.dumps(payload, sort_keys=True)
        return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()

    def extract_ast_symbols(
        self, tree: ast.AST
    ) -> Tuple[Dict[str, ast.ClassDef], Dict[str, ast.FunctionDef | ast.AsyncFunctionDef]]:
        """Extracts public (exported) class and function definitions from module AST."""
        classes: Dict[str, ast.ClassDef] = {}
        functions: Dict[str, ast.FunctionDef | ast.AsyncFunctionDef] = {}

        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.ClassDef):
                if not node.name.startswith("_"):
                    classes[node.name] = node
                    # Also collect public methods from public classes
                    for item in node.body:
                        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            if not item.name.startswith("_"):
                                functions[item.name] = item
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if not node.name.startswith("_"):
                    functions[node.name] = node

        return classes, functions

    def verify_bijectivity(
        self,
        source_code: str,
        contract: Any,
        source_file: str = "module.py",
        allow_empty_nouns: bool = True,
    ) -> ContractBijectivityWitness:
        """Verifies strict bijection between ContractIR and AST code under BIJ-001..003."""
        witness_id = f"wit_bij_{uuid.uuid4().hex[:12]}"
        contract_id = getattr(contract, "contract_id", "contract_anonymous")

        try:
            tree = ast.parse(source_code)
        except SyntaxError as e:
            raise BijectiveVerificationViolation(f"Syntax error in candidate source '{source_file}': {e.msg}")

        classes, functions = self.extract_ast_symbols(tree)

        # 1. Resolve Contract Nouns and Verbs
        nouns_dict = getattr(contract, "nouns", {})
        verbs_dict = getattr(contract, "verbs", {})

        declared_nouns: Set[str] = set(nouns_dict.keys())
        declared_verbs: Set[str] = set(verbs_dict.keys())

        ast_function_names: Set[str] = set(functions.keys())
        ast_class_names: Set[str] = set(classes.keys())

        # 2. Rule BIJ-001: Strict Bijective Symbol Mapping
        # Total Surjectivity (Anti-Phantom / Zero-Rogue Invariant)
        rogue_functions = sorted(list(ast_function_names - declared_verbs))
        if rogue_functions:
            raise RogueSymbolViolation(
                f"[BIJ-001 Violation] Rogue public function(s) detected with zero contract mapping: {rogue_functions}"
            )

        # Total Injectivity (Completeness Invariant)
        unmapped_verbs = sorted(list(declared_verbs - ast_function_names))
        if unmapped_verbs:
            raise UnimplementedVerbViolation(
                f"[BIJ-001 Violation] Contract verb(s) declared but unimplemented in AST: {unmapped_verbs}"
            )

        # Noun Bijectivity Check (if nouns are declared)
        if declared_nouns and not allow_empty_nouns:
            rogue_classes = sorted(list(ast_class_names - declared_nouns))
            if rogue_classes:
                raise RogueSymbolViolation(
                    f"[BIJ-001 Violation] Rogue class(es) detected without contract noun: {rogue_classes}"
                )
            unmapped_nouns = sorted(list(declared_nouns - ast_class_names))
            if unmapped_nouns:
                raise UnimplementedVerbViolation(
                    f"[BIJ-001 Violation] Contract noun(s) declared but missing in AST: {unmapped_nouns}"
                )

        # 3. Rule BIJ-002: Docstring & Specification Hash Verification
        spec_hashes: Dict[str, str] = {}
        for verb_name, func_node in functions.items():
            verb = verbs_dict.get(verb_name)
            if not verb:
                continue

            expected_hash = self.compute_spec_hash(verb)
            spec_hashes[verb_name] = expected_hash

            docstring = ast.get_docstring(func_node, clean=True)
            if not docstring:
                raise SpecificationDriftViolation(
                    f"[BIJ-002 Violation] Function '{verb_name}' in '{source_file}' has no docstring specification."
                )

            # Check for @spec_hash directive
            match = self.SPEC_HASH_PATTERN.search(docstring)
            if not match:
                raise SpecificationDriftViolation(
                    f"[BIJ-002 Violation] Function '{verb_name}' docstring missing mandatory '@spec_hash: <sha256>' tag."
                )

            extracted_hash = match.group(1).lower()
            if extracted_hash != expected_hash.lower():
                raise SpecificationDriftViolation(
                    f"[BIJ-002 Violation] Specification drift in '{verb_name}': docstring spec_hash '{extracted_hash}' "
                    f"does not match ContractIR hash '{expected_hash}'."
                )

            # Check pre- and post-condition clauses in docstring
            pre_conditions = getattr(verb, "pre_conditions", [])
            for pre in pre_conditions:
                if pre not in docstring and f":pre {pre}" not in docstring:
                    raise SpecificationDriftViolation(
                        f"[BIJ-002 Violation] Function '{verb_name}' docstring missing declared pre-condition clause: '{pre}'."
                    )

            post_conditions = getattr(verb, "post_conditions", [])
            for post in post_conditions:
                if post not in docstring and f":post {post}" not in docstring:
                    raise SpecificationDriftViolation(
                        f"[BIJ-002 Violation] Function '{verb_name}' docstring missing declared post-condition clause: '{post}'."
                    )

        # 4. Rule BIJ-003: Signature & Parameter Morphism Isomorphism
        for verb_name, func_node in functions.items():
            verb = verbs_dict.get(verb_name)
            if not verb:
                continue

            contract_params = getattr(verb, "parameters", [])
            expected_param_names = []
            for p in contract_params:
                if hasattr(p, "name"):
                    expected_param_names.append(p.name)
                elif isinstance(p, dict):
                    expected_param_names.append(p.get("name", ""))
                else:
                    expected_param_names.append(str(p))

            # Filter out 'self' / 'cls' if present
            ast_params = [arg.arg for arg in func_node.args.args if arg.arg not in ("self", "cls")]

            if ast_params != expected_param_names:
                raise SignatureMismatchViolation(
                    f"[BIJ-003 Violation] Parameter mismatch in '{verb_name}': expected {expected_param_names}, got {ast_params}"
                )

        witness = ContractBijectivityWitness(
            witness_id=witness_id,
            contract_id=contract_id,
            source_file=source_file,
            is_bijective=True,
            mapped_verbs=sorted(list(ast_function_names)),
            unmapped_verbs=[],
            rogue_functions=[],
            docstring_hash_matches=True,
            spec_hashes=spec_hashes,
            timestamp_unix_ms=int(time.time() * 1000),
        )
        witness.validate_invariants()
        return witness
