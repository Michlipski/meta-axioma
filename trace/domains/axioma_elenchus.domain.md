# Domain: Axioma Elenchus (`soc_epistemic_curiosity_engine`)

- **Generation:** System $G_{3b}$ (`SystemG3bCompiler` + Reflexive Quine Daughter Crucible `SystemG3b_Daughter_Prime`)
- **App Path:** `apps/axioma_elenchus/` (`generations/gen_03b/apps/axioma_elenchus/`)
- **Port:** `8097`
- **Human Intent Witness:** `trace/intent_elicitation_axioma_elenchus.json` (`WITNESS_PE_C727D17740F7F851`)

## 1. Waterloo Situation of Concern (`[L1-G3B-000]`)
- **Root Friction:** Current educational and knowledge-retrieval systems enforce linear progression and dispense definitive answers when an Explorer hits a cognitive wall in abstract domains like Category Theory. This bypasses cognitive struggle, destroys meta-curiosity, and produces fragile knowledge graphs.
- **Co-Equal Actors:**
  - **The Explorer (Human):** Navigates the Category Theory conceptual DAG, submits formal structural proofs, tests conjectures in conceptual dead-ends, and triggers 1-tap **Functorial Undo** (`Cmd+Z`).
  - **The Socratic Probe (Agent on Local RTX 4060 / `qwen2.5`):** Generates dialectical counter-axioms without spoilers via local Ollama (`http://192.168.10.40:11434/api/generate`, model `qwen2.5`, 8GB VRAM, $\le 25\text{ms}$ latency budget) with automatic `[L1-016]` Exception Enclave fallback to the deterministic Lakatosian Socratic Elenchus Kernel.
  - **The Epistemic Validator (Engine):** Enforces compositional prerequisite contracts (`TransitionToExploringFunctors`), physically blocking `"Exploring Functors"` until `"Mastery of Morphisms"` evaluates to `True`.

## 2. Core Entities (`ContractIR` Nouns)
1. **`EpistemicNode` (`sub_foundation_morphisms`)**
   - Fields: `node_id: str`, `stratum: str`, `concept_title: str`, `mastery_of_morphisms: bool`, `mastery_score: int`, `functor_unlocked: bool`, `dead_end_depth: int`, `history_checkpoint_id: str`, `proof_obligation: str`
   - Invariants: `mastery_score >= 0`, `mastery_score <= 100`, `dead_end_depth >= 0`
2. **`SocraticProbeSession` (`sub_socratic_probe`)**
   - Fields: `session_id: str`, `target_node_id: str`, `ollama_endpoint: str`, `model_tag: str`, `gpu_device: str`, `vram_mb: int`, `inference_latency_ms: int`, `dialectical_friction_score: int`, `contradiction_posed: str`, `enclave_fallback_active: bool`
   - Invariants: `inference_latency_ms >= 0`, `inference_latency_ms <= 25`, `dialectical_friction_score >= 1`, `vram_mb >= 8192`
3. **`EpistemicValidationGate` (`sub_epistemic_validator`)**
   - Fields: `gate_id: str`, `prerequisite_node_id: str`, `target_higher_state: str`, `precondition_morphisms_mastered: bool`, `elenchus_resolved: bool`, `transition_authorized: bool`, `functorial_rollback_count: int`, `proof_witness_hash: str`
   - Invariants: `functorial_rollback_count >= 0`

## 3. Compositional Contracts (`ContractIR` Verbs)
- **`TransitionToExploringFunctors`:**
  - `sub_foundation_morphisms::CertifyMasteryOfMorphisms` (`EpistemicNode` $\to$ `EpistemicNode`, postcondition `mastery_of_morphisms == True and mastery_score >= 85`)
  - $\to$ `sub_socratic_probe::ExecuteDialecticalElenchus` (`EpistemicNode` $\to$ `SocraticProbeSession`, precondition `mastery_of_morphisms == True and mastery_score >= 85`, postcondition `inference_latency_ms <= 25 and dialectical_friction_score >= 1 and vram_mb >= 8192`)
  - $\to$ `sub_epistemic_validator::UnlockExploringFunctors` (`SocraticProbeSession` $\to$ `EpistemicValidationGate`, postcondition `precondition_morphisms_mastered == True and elenchus_resolved == True and transition_authorized == True`)
- **`TriggerFunctorialUndo`:**
  - Rolls back from any conceptual dead-end (`dead_end_associativity`, `conceptual_dead_end`, `functor_dead_end`) via `HistoryType.DEEP` (`foundational_history`, `higher_history`) and records Landauer bit erasure (`[L1-012]`).
