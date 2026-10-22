---
name: generator-prompter
description: >-
  Synthesizes cache-busted, entropy-mutated execution prompts for Meta-Axioma compilers
  and generators (e.g. System G2b Compiler, System G1/G1b/G2/G3 Compilers). Use this skill
  when the user asks to generate, mutate, or craft an application initialization prompt for
  a specific generator, incorporating random cache-busting nonces, linguistic perturbations,
  and compiler invariant constraints.
---

# Generator Prompter Skill

This skill generates unique, cache-busting prompts tailored for Meta-Axioma compilers and application generators (such as `System G2b Compiler`, `System G1 Compiler`, `System G1b Compiler`, `System G2 Compiler`, `System G3 Compiler`, or custom generators).

Cache busting prevents LLMs and API proxies from returning cached responses or bypassing exploratory deliberation by injecting nonces, timestamps, random entropy tags, and semantic linguistic mutations into the prompt.

---

## Workflow & Procedures

### Step 1: Identify Generator & Core Concept
1. **Target Generator:** Confirm the target compiler/generator (e.g., `System G2b Compiler`).
   - Consult [`references/generators_catalog.md`](./references/generators_catalog.md) to inspect the invariant contracts of each generator.
2. **Elevator Pitch:** Identify the core application vision, domain, or inspiration (e.g., *"A category theory teaching application for early education inspired by Eugenia Cheng's success teaching category theory to arts students."*).
3. **Execution Mode:**
   - **Script Execution (Recommended):** Run the automated helper script [`scripts/bust_cache_prompt.py`](./scripts/bust_cache_prompt.py).
   - **Manual Formulation:** Manually apply the cache-busting rules detailed below.

---

### Step 2: Automated Generation via Helper Script

Execute the helper script directly inside the sandbox:

```bash
# Generate a single cache-busted prompt for System G2b Compiler
python3 .agents/skills/generator-prompter/scripts/bust_cache_prompt.py \
  --generator "System G2b Compiler" \
  --pitch "A category theory teaching application for early education inspired by Eugenia Cheng's success teaching category theory to arts students." \
  --mutation-level moderate

# Generate multiple varied options with header styling
python3 .agents/skills/generator-prompter/scripts/bust_cache_prompt.py \
  --generator "System G2b Compiler" \
  --pitch "A category theory teaching application for early education inspired by Eugenia Cheng's success teaching category theory to arts students." \
  --mutation-level high \
  --nonce-style header \
  --count 3
```

#### Script Options Reference
- `-g, --generator`: Target compiler name (default: `System G2b Compiler`).
- `-p, --pitch`: Elevator pitch or application concept.
- `-m, --mutation-level`: Degree of linguistic mutation (`subtle`, `moderate`, `high`).
- `-n, --nonce-style`: Prefix style (`comment`, `tag`, `header`, `stealth`).
- `--count N`: Generate $N$ distinct mutated variations.
- `--no-invariants`: Exclude generator-specific architectural invariant checklist.
- `--no-gate`: Exclude Directive 3 plan-first approval gate reminder.
- `--json`: Output structured JSON containing variations.

---

### Step 3: Cache-Busting Mutation Rules (For Manual or Custom Formulation)

When composing or reviewing a prompt manually, apply all four layers of cache busting:

#### 1. High-Entropy Prefix Nonce
Every prompt must start with a non-cached prefix containing unique entropy:
- **HTML/Markdown Comment (Default):**
  `<!-- META_AXIOMA_NONCE: RUN_<HEX12> | TS: <ISO8601_UTC> | ENTROPY: 0x<HEX12> -->`
- **Metadata Tag:**
  `[Session Dispatch Nonce: RUN_<HEX12> | Ref: 0x<HEX8>]`
- **Execution Vector Header:**
  `> 🛡️ **Execution Vector:** RUN_<HEX12> | **Timestamp:** <ISO8601>Z`

#### 2. Opening Phrase Mutation
Rotate opening phrasing across variations:
- *"Let's build our next application using the {generator}:"*
- *"Please synthesize and construct our next application using the {generator}:"*
- *"Initiate compilation and deployment of our next application via the {generator}:"*
- *"Assemble, verify, and emit our next application leveraging the {generator}:"*
- *"We are ready to architect and build our next application utilizing the {generator}:"*

#### 3. Pitch Semantic & Syntactic Perturbation
Mutate the pitch text to break string matching while strictly preserving semantic intent:
- **Synonym Swaps:**
  - `teaching application` $\to$ `educational platform` / `interactive learning studio` / `teaching workbench`
  - `early education` $\to$ `early childhood education` / `foundational education` / `young learners`
  - `inspired by` $\to$ `drawing inspiration from` / `modeled after the work of` / `informed by the pedagogical principles of`
  - `success teaching` $\to$ `celebrated success introducing` / `groundbreaking approach to teaching` / `proven track record conveying`
  - `arts students` $\to$ `fine arts students` / `students in the creative arts and humanities`
  - `category theory` $\to$ `category theory concepts (objects, morphisms, functorial composition)`
- **Sentence Restructuring:** Invert independent clauses or introduce qualifying focus statements (e.g., *"Prioritizing concrete tactile metaphors before formal abstraction."*).

#### 4. Clean Seed Prompts (No Embedded Directive Reminders)
Seed prompts must remain **clean, natural user prompts** containing only the cache-busting nonce, the opening generator invocation, and the elevator pitch.
- **Do NOT** append `**Compiler & Architectural Invariants:**` or `> ⚠️ **Mandatory Protocol Reminder:**` blocks to seed prompts unless explicitly requested with `--include-invariants` or `--include-gate`.
- All compiler governance rules (Directive 3, Directive 5, `invoke_subagent` Brain/Muscle routing, single-budget `estimate_from_structural_scope()` calibration, and `app_output_dir` auditing) live in [`AGENTS.md`](../../../AGENTS.md) and [`.agents/skills/system-g3b-compiler/SKILL.md`](../system-g3b-compiler/SKILL.md).

---

## Reference Examples

See [`examples/example_prompts.md`](./examples/example_prompts.md) for concrete before/after prompt variations across multiple compilers and domains.
