---
trigger: model_decision
description: "Mandatory empirical execution witness and anti-phantom emission gate for Meta-Axioma: prohibits simulated completion without physical file verification and passing runtime tests."
---

# 🛡️ Empirical Execution Witness & Anti-Phantom Emission Gate (`NEG-G1B-001`)

## 1. The Core Invariant
Autonomous agents default to "simulated completion"—declaring a system, feature, or compiler pipeline "verified" or "complete" based on in-memory representations, abstract reachability checks, or unexecuted source files. In Meta-Axioma, **simulated completion is strictly forbidden**.

## 2. Operational Directives for Agents

1. **Mandatory Physical Emission:**
   - Any compiler or code generator task must emit tangible, non-zero-byte files to the file system.
   - Never report completion before verifying that all required manifest files exist on disk (`path.exists()` and `st_size > 0`).

2. **Mandatory Substrate Test Execution:**
   - Writing tests to disk is insufficient. The tests must be **executed** on the target runtime substrate (e.g., Python 3.14 `unittest`).
   - The agent must inspect actual stdout/stderr, confirm zero failures/errors, verify a non-zero test count, and display the execution witness in the trajectory.

3. **Ban on Cosmetic Proxy Assertions & Semantic Phantoms (`[L1-G3B-011]`):**
   - Writing tests that check cosmetic proxies (`len(output) > 0`, `assert "<rect" in svg`, `assert "class " in code`) as proof of functional competence is strictly prohibited.
   - Any emitted artifact or interface must be verified by simulating or executing the **downstream consumer's operational contract** (e.g. an independent decoder verifying decodability, an engine executing code, a client validating schema responses).
   - If a test verifies an encoder, it must execute a consumer decoder: $f^{-1}(f(x)) == x$.

4. **Topological Fidelity & Anti-Loopback Gateway (`[L1-G3B-012]`):**
   - Testing cross-device or multi-node distributed contracts against a collapsed single-node loopback (`127.0.0.1`) is strictly forbidden.
   - Applications requiring local network peer discovery must dynamically verify active physical LAN interfaces and reject loopback defaults.

5. **No Phantom Journey Steps (`[L1-G3B-013]`):**
   - E2E journey walkers are strictly forbidden from appending in-memory mock actions (`actions.append(...)`) to claim step completion.
   - Every step must be driven by and asserted against an observable change in external runtime state.

6. **Mechanical Gate Enforcement:**
   - `SystemG1bCompiler`, `SystemG2bCompiler`, and `SystemG3bCompiler` enforce Post-Emission Execution Gates.
   - If an agent invokes `compile()` without `target_output_dir`, it raises `PhantomEmissionViolation`.
   - If an emitted application fails any test in its generated test harness, it raises `PostEmissionExecutionFailure`.
   - Do not bypass this gate.
