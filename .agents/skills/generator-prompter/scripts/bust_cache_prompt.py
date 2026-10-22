#!/usr/bin/env python3
"""Cache-Busting Generator Prompt Synthesizer for Meta-Axioma.

Generates uniquely mutated, cache-busted execution prompts for Meta-Axioma compilers
and generators (e.g., System G2b Compiler, System G1/G1b/G2/G3 Compilers).

Prevents LLM prefix caching and exact prompt matching via:
1. High-entropy prefix tags (nonces, UUIDs, ISO timestamps, hexadecimal entropy).
2. Preamble & greeting variations.
3. Linguistic mutations of the elevator pitch (synonym substitution, phrase restructuring).
4. Section header and formatting variations.
5. Generator-specific architectural and invariant injections.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib
import json
import os
import random
import re
import sys
import time
from typing import Any, Dict, List, Optional, Tuple
import uuid


# -----------------------------------------------------------------------------
# Linguistic Variation Tables & Synonyms
# -----------------------------------------------------------------------------

OPENING_TEMPLATES = [
    "Let's build our next application using the {generator}:",
    "Please synthesize and construct our next application using the {generator}:",
    "Initiate compilation and deployment of our next application via the {generator}:",
    "We are ready to architect and build our next application utilizing the {generator}:",
    "Let's assemble our next production application with the {generator}:",
    "Bootstrap our next application through the {generator}:",
    "Assemble, verify, and emit our next application leveraging the {generator}:",
    "Let's proceed with building our next software system using the {generator}:",
    "Deploy the complete compilation pipeline for our next application using the {generator}:",
    "Let's create our next flagship application using the {generator}:",
]

PITCH_HEADERS = [
    "**Elevator Pitch:**",
    "### Elevator Pitch",
    "**Core Elevator Pitch & Vision:**",
    "### Project Elevator Pitch:",
    "> **Elevator Pitch:**",
    "**Application Concept & Pitch:**",
    "#### System Elevator Pitch:",
]

REQUIREMENTS_HEADERS = [
    "**Compiler & Architectural Invariants:**",
    "### Architectural Mandate & Directives:",
    "**Target Invariants & Execution Directives:**",
    "### Core Compilation Constraints:",
    "**Governing Principles & Compiler Gate:**",
]

# Domain synonym maps for semantic perturbation
SYNONYM_MAP: Dict[str, List[str]] = {
    "teaching application": [
        "educational platform",
        "interactive learning studio",
        "teaching workbench",
        "pedagogical application",
        "learning environment",
    ],
    "teaching": [
        "introducing",
        "instructing",
        "explaining",
        "demystifying",
        "conveying",
    ],
    "application": [
        "studio",
        "system",
        "software suite",
        "interactive workspace",
        "platform",
    ],
    "early education": [
        "early childhood education",
        "foundational education",
        "young learners and elementary education",
        "early stage learning",
        "introductory childhood education",
    ],
    "inspired by": [
        "drawing inspiration from",
        "modeled after the work of",
        "informed by the pedagogical principles of",
        "grounded in the insights of",
        "taking cues from",
    ],
    "success teaching": [
        "celebrated success introducing",
        "groundbreaking approach to teaching",
        "proven track record conveying",
        "triumphant methodology teaching",
        "acclaimed work explaining",
    ],
    "arts students": [
        "fine arts students",
        "students in the creative arts and humanities",
        "visual and performing arts students",
        "creative arts learners",
    ],
    "category theory": [
        "category theory concepts (objects, morphisms, functorial composition)",
        "mathematical category theory and structural reasoning",
        "category theory fundamentals",
        "formal category theory",
    ],
    "build": [
        "construct",
        "compile",
        "synthesize",
        "architect",
        "implement",
    ],
    "next": [
        "upcoming",
        "succeeding",
        "subsequent",
    ],
    "real-time": [
        "live",
        "instantaneous",
        "synchronous",
        "low-latency",
    ],
    "workflow": [
        "operational pipeline",
        "user flow",
        "task progression",
    ],
    "collaborative": [
        "multi-user",
        "shared",
        "cooperative",
    ],
    "dashboard": [
        "command center",
        "glanceboard",
        "operations console",
    ],
    "distributed": [
        "decentralized",
        "multi-node",
        "networked",
    ],
    "simple": [
        "frictionless",
        "streamlined",
        "distraction-free",
        "intuitive",
    ],
    "modern": [
        "state-of-the-art",
        "contemporary",
        "refined",
    ],
    "robust": [
        "resilient",
        "battle-tested",
        "invariant-backed",
    ],
}

# Generator-specific invariant notes
GENERATOR_INVARIANTS: Dict[str, List[str]] = {
    "System G2b Compiler": [
        "Adhere strictly to Directive 3: High-level plan (persona, JTBD, workflow, UX) and Dynamic Token Proposals ([L1-G2B-004], [L1-G2B-005]) with 40% Protected Capital / 60% Exploratory Capital.",
        "Mandatory Approval Gate: Present proposals and elicit selection via `ask_question` before executing code generation.",
        "Multi-Tier Interlocking Gate ([L1-G2B-001]): Satisfy Tier 1 structural invariants (functorial undo L1-002, decoupled persistence L1-011_3), Tier 2 usability heuristics (Nielsen-Norman 10, Fitts, Hick, Miller), and Tier 3 domain benchmarks.",
        "Anti-Phantom Emission Gate ([NEG-G1B-001]): Emitted working files must be physically verified on disk and backed by passing substrate runtime tests.",
    ],
    "System G1 Compiler": [
        "Enforce core S0 invariants: Functorial Undo/Redo (L1-002), Decoupled Persistence (L1-011_3), Landauer compute bounds (L1-008), Exception Enclaves (L1-016).",
        "Dual-Boundary Contract: Explicit nouns schema (nouns.json) and deterministic state transitions (verbs.json).",
        "Zero-trust API gateway and standalone zero-dependency Python server.",
    ],
    "System G1b Compiler": [
        "Focus on high-ergonomic micro-interactions, responsive dual-column workbenches, and soft virtual keypads.",
        "Anti-phantom emission gate ([NEG-G1B-001]) and physical test execution witness.",
    ],
    "System G2 Compiler": [
        "Distributed Sheaf-CRDT event streaming (Axioma Fabric substrate).",
        "Zero-ambient HMAC capability tokens, Landauer ring buffers, and autonomous daemon health sentinels.",
    ],
    "System G3b Compiler": [
        "Enforce [L1-G3B-000] Waterloo SoC Normalization: Deconstruct the prompt into a solution-agnostic Tier 1 SituationOfConcern (MACRO, MESO, MICRO) before proposing architectures.",
        "Adhere strictly to Directive 3 & Directive 5: Formulate the High-Level Plan and Dynamic Token Proposals using a SINGLE unified BPE budget calibrated a-priori via `DynamicBudgetCalibrator.estimate_from_structural_scope()` (60% Exploratory Capital / 40% Protected Capital — no 'two-budget' splits or post-hoc token counting) and elicit approval via `ask_question` before code generation.",
        "Mandatory Live Subagent Spawning (`[L1-G3B-014]` & Directive 5): You MUST physically call `invoke_subagent` with `Model=\"pro\"` for Brain tasks (SoC Research & Dialectical Architecture Decomposition) and `Model=\"flash\"` for concurrent Muscle leaf-generation tasks (IR payloads, backend modules, frontend UI, and tests). Record each subagent's real `conversationId` and BPE token counts in `SubagentExecutionWitness` objects and pass `require_live_subagents=True` to `SystemG3bCompiler.compile()`.",
        "Enforce [L1-G3B-016], [NEG-G1B-001], & [L1-G3B-017]: Pass both `target_output_dir` (epoch directory) and `app_output_dir` (`apps/<app_name>/`) into `SystemG3bCompiler.compile()` so 100% of application files pass `ZeroTrustMicroAuditorRegistry`, execute live subprocess tests, and are sealed into `telemetry_ledger.json` + `telemetry_dashboard.md`.",
    ],
    "System G3 Compiler": [
        "General distributed systems, transitive sheaf-quorum consensus (Axioma Mesh), OpenTelemetry tracing, and User Zero grounding.",
        "Production accessibility, bilingual parity, and strict privacy boundaries.",
    ],
}


# -----------------------------------------------------------------------------
# Cache-Busting Nonce & Entropy Generators
# -----------------------------------------------------------------------------

def generate_nonce_header(
    style: str = "comment",
    seed_override: Optional[str] = None,
) -> str:
    """Generate a high-entropy cache-busting prefix string.
    
    Styles:
    - comment: HTML/Markdown comment containing UUID, timestamp, entropy hex
    - tag: Bracketed metadata tag
    - header: Formal compilation run header
    - stealth: Subtle trailing whitespace and invisible zero-width unicode
    """
    if seed_override is not None:
        # Deterministic generation for reproducible test runs
        seed_hash = hashlib.sha256(seed_override.encode()).hexdigest()
        random_hex = seed_hash[:12]
        iso_ts = "2026-10-20T00:00:00.000000+00:00"
        run_id = f"RUN_{random_hex.upper()}"
    else:
        now = datetime.now(timezone.utc)
        iso_ts = now.isoformat()
        raw_uuid = str(uuid.uuid4())
        random_hex = hashlib.sha256(f"{raw_uuid}:{time.time_ns()}".encode()).hexdigest()[:12]
        run_id = f"RUN_{random_hex.upper()}"

    if style == "comment":
        return f"<!-- META_AXIOMA_NONCE: {run_id} | TS: {iso_ts} | ENTROPY: 0x{random_hex} -->\n"
    elif style == "tag":
        return f"[Session Dispatch Nonce: {run_id} | Ref: 0x{random_hex[:8]}]\n\n"
    elif style == "header":
        return (
            f"> 🛡️ **Execution Vector:** `{run_id}` | **Timestamp:** `{iso_ts[:19]}Z`\n\n"
        )
    elif style == "stealth":
        # Combines a short hash with a dynamic session stamp
        return f"<!-- cache-bust-id: {random_hex} -->\n"
    else:
        return f"<!-- NONCE: {run_id} -->\n"


def mutate_pitch_text(
    pitch: str,
    mutation_level: str = "moderate",
    rng: Optional[random.Random] = None,
) -> str:
    """Apply linguistic perturbation to an elevator pitch.
    
    Levels:
    - subtle: 1-2 synonym swaps, punctuation preserve
    - moderate: 3-5 synonym swaps, slight clause variation
    - high: aggressive paraphrase and structural inversion
    """
    if rng is None:
        rng = random.Random()

    result = pitch
    swap_budget = {"subtle": 2, "moderate": 4, "high": 7}.get(mutation_level, 4)
    swaps_done = 0

    # Sort keys by length descending to match compound terms first
    sorted_keys = sorted(SYNONYM_MAP.keys(), key=len, reverse=True)

    for phrase in sorted_keys:
        if swaps_done >= swap_budget:
            break
        pattern = re.compile(re.escape(phrase), re.IGNORECASE)
        match = pattern.search(result)
        if match:
            candidates = SYNONYM_MAP[phrase]
            # 70% probability to swap if matched
            if rng.random() < 0.85:
                choice = rng.choice(candidates)
                # Preserve capitalized leading char if original was capitalized
                matched_text = match.group(0)
                if matched_text[0].isupper():
                    choice = choice[0].upper() + choice[1:]
                result = pattern.sub(choice, result, count=1)
                swaps_done += 1

    # Ensure at least one mutation occurs even if no domain synonyms matched
    if swaps_done == 0:
        qualifiers = [
            "Specifically engineered for high usability and robust execution: ",
            "Grounded in verified domain principles: ",
            "Architected from first principles: ",
            "Designed for intuitive clarity and delightful ergonomics: ",
        ]
        result = rng.choice(qualifiers) + result

    # Optional connector injection for high mutation
    if mutation_level == "high" and rng.random() > 0.5:
        connectors = [
            " Designed specifically to nurture intuitive mental models.",
            " Emphasizing visceral, tangible exploration over rote symbol manipulation.",
            " Prioritizing concrete metaphors before formal abstraction.",
        ]
        result = result.rstrip(". ") + "." + rng.choice(connectors)

    return result


def resolve_generator_invariants(generator: str) -> List[str]:
    """Find matching invariants for the given generator string."""
    for key, invs in GENERATOR_INVARIANTS.items():
        if key.lower() in generator.lower() or generator.lower() in key.lower():
            return invs
    # Default generic invariant list
    return [
        "Adhere to zero-trust axiomatic boundaries and decoupled persistence.",
        "Formulate a plan-first specification with explicit scope trade-offs before code emission.",
        "Ensure all emitted code passes runtime verification with zero mocks on live substrate.",
    ]


# -----------------------------------------------------------------------------
# Main Prompt Generation Engine
# -----------------------------------------------------------------------------

@dataclass
class PromptGenerationOptions:
    generator: str = "System G3b Compiler"
    pitch: str = (
        "A category theory teaching application for early education inspired by "
        "Eugenia Cheng's success teaching category theory to arts students."
    )
    mutation_level: str = "moderate"  # subtle, moderate, high
    nonce_style: str = "comment"      # comment, tag, header, stealth
    include_invariants: bool = False
    include_execution_gate: bool = False
    seed: Optional[int] = None
    custom_invariants: Optional[List[str]] = None


def generate_cache_busting_prompt(options: PromptGenerationOptions) -> str:
    """Generate a mutated, cache-busting prompt tailored for the specified generator."""
    rng = random.Random(options.seed) if options.seed is not None else random.Random()

    # 1. Nonce & Prefix
    seed_tag = str(options.seed) if options.seed is not None else None
    prefix = generate_nonce_header(style=options.nonce_style, seed_override=seed_tag)

    # 2. Opening Template
    opening_template = rng.choice(OPENING_TEMPLATES)
    opening_text = opening_template.format(generator=options.generator)

    # 3. Elevator Pitch Header & Mutated Pitch
    pitch_header = rng.choice(PITCH_HEADERS)
    mutated_pitch = mutate_pitch_text(options.pitch, mutation_level=options.mutation_level, rng=rng)

    # 4. Construct Core Prompt Body
    body_parts = [
        prefix,
        opening_text,
        "",
        pitch_header,
        "",
        mutated_pitch,
    ]

    # 5. Optional Generator Invariants & Execution Gate (disabled by default; rules live in AGENTS.md & skills)
    if options.include_invariants:
        req_header = rng.choice(REQUIREMENTS_HEADERS)
        invariants = options.custom_invariants or resolve_generator_invariants(options.generator)
        body_parts.extend(["", req_header])
        for inv in invariants:
            bullet_char = rng.choice(["-", "*"])
            body_parts.append(f"{bullet_char} {inv}")

    if options.include_execution_gate:
        gate_notes = [
            "",
            "> ⚠️ **Mandatory Protocol Reminder:** In accordance with Directive 3, please formulate the high-level plan (persona, JTBD, UX flow, and dynamic token proposal options) and elicit human approval via `ask_question` prior to synthesizing concrete codebase artifacts.",
        ]
        body_parts.extend(gate_notes)

    # Trailing newline
    return "\n".join(body_parts).strip() + "\n"


# -----------------------------------------------------------------------------
# CLI Interface
# -----------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate cache-busted, mutated prompts for Meta-Axioma generators/compilers.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-g", "--generator",
        default="System G3b Compiler",
        help="Target generator or compiler name (e.g. 'System G3b Compiler', 'System G2b Compiler')",
    )
    parser.add_argument(
        "-p", "--pitch",
        default="A category theory teaching application for early education inspired by Eugenia Cheng's success teaching category theory to arts students.",
        help="Elevator pitch or core application vision",
    )
    parser.add_argument(
        "-m", "--mutation-level",
        choices=["subtle", "moderate", "high"],
        default="moderate",
        help="Degree of linguistic mutation/synonym perturbation applied to the prompt",
    )
    parser.add_argument(
        "-n", "--nonce-style",
        choices=["comment", "tag", "header", "stealth"],
        default="comment",
        help="Visual style of the cache-busting nonce prefix",
    )
    parser.add_argument(
        "--include-invariants",
        action="store_true",
        help="Include generator-specific architectural invariant checklist in the prompt (off by default)",
    )
    parser.add_argument(
        "--include-gate",
        action="store_true",
        help="Include the Directive 3 plan-first execution gate reminder in the prompt (off by default)",
    )
    parser.add_argument(
        "--no-invariants",
        action="store_true",
        help="Deprecated no-op (invariants are omitted by default)",
    )
    parser.add_argument(
        "--no-gate",
        action="store_true",
        help="Deprecated no-op (gate reminders are omitted by default)",
    )
    parser.add_argument(
        "-s", "--seed",
        type=int,
        default=None,
        help="Deterministic pseudo-random seed (omit for true randomness)",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=1,
        help="Number of distinct mutated prompt variations to generate",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON object containing generated prompt variations",
    )

    args = parser.parse_args()

    results: List[Dict[str, Any]] = []

    for i in range(args.count):
        current_seed = (args.seed + i) if args.seed is not None else None
        opts = PromptGenerationOptions(
            generator=args.generator,
            pitch=args.pitch,
            mutation_level=args.mutation_level,
            nonce_style=args.nonce_style,
            include_invariants=bool(args.include_invariants),
            include_execution_gate=bool(args.include_gate),
            seed=current_seed,
        )
        prompt = generate_cache_busting_prompt(opts)
        results.append({
            "variation_index": i + 1,
            "generator": args.generator,
            "seed": current_seed,
            "prompt": prompt,
        })

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        for item in results:
            if args.count > 1:
                print(f"=== VARIATION {item['variation_index']} ===")
            print(item["prompt"])
            if args.count > 1:
                print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
