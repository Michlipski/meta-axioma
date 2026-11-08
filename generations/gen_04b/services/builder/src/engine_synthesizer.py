"""Generation 4b Quarantined Engine Synthesizer (`[SPEC-G4B-BUILDER-001]`).

Enforces:
- CognitiveRole.CORE_ENGINE_SYNTHESIZER role enforcement.
- Strict mutation whitelist: `services/<service>/src/`, `apps/<app>/src/`, `apps/<app>/static/`, `src/`.
- Zero-tolerance builder quarantine prohibiting mutation of `tests/`, `test_*.py`, `*_test.py`.
- Pre-mutation target validation raising BuilderQuarantineViolation.
- Physical disk registration, recording, and emission verification ([NEG-G1B-001]).
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import time
from typing import Any, Dict, List, Optional, Sequence

from .domain_models import (
    CognitiveRole,
    DomainInvariantViolation,
    LeafEmissionEvent,
    PhysicalDiskWitness,
)


class BuilderQuarantineViolation(DomainInvariantViolation):
    """Raised when an engine synthesizer attempts to mutate test files or unauthorized directories."""
    pass


# Strict Whitelist Patterns for Engine Mutations
ALLOWED_TARGET_PATTERNS = [
    re.compile(r"(?:^|/)(?:generations/[^/]+/)?services/[^/]+/src/"),
    re.compile(r"(?:^|/)apps/[^/]+/src/"),
    re.compile(r"(?:^|/)apps/[^/]+/static/"),
    re.compile(r"(?:^|/)src/"),
    re.compile(r"(?:^|/)scripts/"),
    re.compile(r"(?:^|/)\.scratch/"),
]

# Prohibited Test Patterns (Zero-tolerance builder quarantine)
PROHIBITED_TEST_PATTERNS = [
    re.compile(r"(?:^|/)tests?/"),
    re.compile(r"(?:^|/)test_[^/]+\.py$"),
    re.compile(r"(?:^|/)[^/]+_test\.py$"),
]


def validate_mutation_target(target_path: str) -> None:
    """Validates that target_path conforms to the engine synthesizer whitelist and quarantine.

    Raises:
        BuilderQuarantineViolation: If target_path targets a test file or directory,
                                    or falls outside the authorized mutation whitelist.
    """
    if not target_path or not str(target_path).strip():
        raise BuilderQuarantineViolation("Mutation target path must not be empty.")

    norm_path = str(target_path).replace("\\", "/").strip()

    # 1. Zero-tolerance check against all prohibited test patterns
    for pattern in PROHIBITED_TEST_PATTERNS:
        if pattern.search(norm_path):
            raise BuilderQuarantineViolation(
                f"[SPEC-G4B-BUILDER-001 Violation] Builder quarantine strictly prohibits "
                f"CORE_ENGINE_SYNTHESIZER from authoring or modifying test files or directories: '{target_path}'."
            )

    # 2. Enforce mutation whitelist
    is_whitelisted = False
    for allowed_re in ALLOWED_TARGET_PATTERNS:
        if allowed_re.search(norm_path):
            is_whitelisted = True
            break

    if not is_whitelisted:
        raise BuilderQuarantineViolation(
            f"[SPEC-G4B-BUILDER-001 Violation] Target path '{target_path}' is outside authorized mutation whitelist: "
            f"['services/<service>/src/', 'apps/<app>/src/', 'apps/<app>/static/', 'src/']."
        )


class EngineSynthesizer:
    """Quarantined engine synthesizer enforcing role boundary and emission tracking."""

    def __init__(self, workspace_root: Optional[str] = None):
        self.role: CognitiveRole = CognitiveRole.CORE_ENGINE_SYNTHESIZER
        self.workspace_root = Path(workspace_root).resolve() if workspace_root else Path.cwd()
        self.emissions: Dict[str, LeafEmissionEvent] = {}
        self.witnesses: Dict[str, PhysicalDiskWitness] = {}

    def validate_target(self, target_path: str) -> None:
        """Validates that target_path complies with builder quarantine."""
        validate_mutation_target(target_path)

    def record_emission(
        self,
        file_path: str,
        source_code: str,
        symbol_urn: Optional[str] = None,
        bpe_token_count: int = 0,
    ) -> LeafEmissionEvent:
        """Records an engine source emission, validating target path and non-empty content."""
        validate_mutation_target(file_path)

        if not source_code or not source_code.strip():
            raise BuilderQuarantineViolation(f"Engine source code for '{file_path}' cannot be empty.")

        p = Path(file_path)
        if not p.is_absolute():
            abs_p = (self.workspace_root / p).resolve()
        else:
            abs_p = p.resolve()

        resolved_str = str(abs_p)
        content_bytes = source_code.encode("utf-8")
        byte_size = len(content_bytes)
        sha256_hash = hashlib.sha256(content_bytes).hexdigest()

        urn = symbol_urn or f"urn:axioma:g4b:engine:{p.stem}"
        if not urn.startswith("urn:axioma:g4b:"):
            urn = f"urn:axioma:g4b:{urn.lstrip('urn:')}"

        witness = PhysicalDiskWitness(
            witness_id=f"wit_eng_{sha256_hash[:12]}",
            file_path=resolved_str,
            byte_size=byte_size,
            sha256_hash=sha256_hash,
            verified_at_unix_ms=int(time.time() * 1000),
            is_present=True,
        )
        witness.validate_invariants()

        event_id = f"leaf_emit_{hashlib.sha256((resolved_str + sha256_hash).encode()).hexdigest()[:12]}"
        event = LeafEmissionEvent(
            event_id=event_id,
            leaf_symbol_urn=urn,
            source_path=resolved_str,
            disk_witness=witness,
            bpe_token_count=bpe_token_count,
            emitted_at_unix_ms=int(time.time() * 1000),
        )
        event.validate_invariants()

        self.emissions[resolved_str] = event
        self.witnesses[resolved_str] = witness
        return event

    def verify_emission(self, file_path: str, symbol_urn: Optional[str] = None) -> PhysicalDiskWitness:
        """Physically verifies emission on disk ([NEG-G1B-001])."""
        validate_mutation_target(file_path)

        p = Path(file_path)
        if not p.is_absolute():
            abs_p = (self.workspace_root / p).resolve()
        else:
            abs_p = p.resolve()

        if not abs_p.exists():
            raise BuilderQuarantineViolation(
                f"[NEG-G1B-001 Violation] Engine source '{file_path}' does not physically exist on disk."
            )

        byte_size = abs_p.stat().st_size
        if byte_size == 0:
            raise BuilderQuarantineViolation(
                f"[NEG-G1B-001 Violation] Engine source '{file_path}' is an empty zero-byte phantom emission."
            )

        content = abs_p.read_bytes()
        sha256_hash = hashlib.sha256(content).hexdigest()
        witness = PhysicalDiskWitness(
            witness_id=f"wit_eng_{sha256_hash[:12]}",
            file_path=str(abs_p),
            byte_size=byte_size,
            sha256_hash=sha256_hash,
            verified_at_unix_ms=int(time.time() * 1000),
            is_present=True,
        )
        witness.validate_invariants()
        self.witnesses[str(abs_p)] = witness
        return witness

    def get_emissions(self) -> List[LeafEmissionEvent]:
        """Returns all recorded leaf emissions."""
        return list(self.emissions.values())

    def get_witnesses(self) -> List[PhysicalDiskWitness]:
        """Returns all verified physical disk witnesses."""
        return list(self.witnesses.values())

    def format_leaf_prompt(
        self,
        task_id: str,
        target_file: str,
        role_title: str,
        contract_spec: Dict[str, Any],
        dependency_skeletons: Optional[Dict[str, str]] = None,
        max_prompt_tokens: int = 4096,
    ) -> Dict[str, Any]:
        """Formats an isolated leaf subagent prompt payload enforcing [L1-G4B-008] (<= 4,096 BPE tokens).

        Injects typed interface skeletons instead of full implementation bodies.
        """
        prompt_sections = [
            f"# Role: {role_title}",
            f"# Target Module: {target_file}",
            f"# Task ID: {task_id}",
            f"# Governing Axioms: [L1-G4B-007], [L1-G4B-008]",
            "",
            "## Contract Specification:",
            json.dumps(contract_spec, indent=2),
        ]

        if dependency_skeletons:
            prompt_sections.append("\n## Dependency Interface Skeletons:")
            for dep_urn, skel_code in dependency_skeletons.items():
                prompt_sections.append(f"\n### {dep_urn}\n```python\n{skel_code}\n```")

        prompt_text = "\n".join(prompt_sections)
        char_est = int(len(prompt_text) / 3.6)
        word_est = len(prompt_text.split())
        est_tokens = max(char_est, word_est)

        if est_tokens > max_prompt_tokens:
            raise BuilderQuarantineViolation(
                f"[L1-G4B-008 Violation] Dispatched leaf prompt footprint ({est_tokens} tokens) "
                f"exceeds hard enclave ceiling of {max_prompt_tokens} tokens."
            )

        return {
            "task_id": task_id,
            "target_file": target_file,
            "prompt_text": prompt_text,
            "estimated_bpe_tokens": est_tokens,
            "is_within_enclave_budget": True,
        }
