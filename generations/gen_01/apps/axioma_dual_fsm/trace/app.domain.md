---
domain: AxiomaDualFsm
related_domains:
  - AppSpecification
  - GenerationalFeedback
  - TelemetryAudit
---

CONSTRAINTS:
- The Inner Dialogue FSM and Outer Security FSM must execute as orthogonal, concurrent state automata.
- The Dominance Rule (Φ_halt) is invariant: If the Outer FSM transitions to CONTAINED_QUARANTINE or ATOMIC_HALT, the Inner FSM must immediately freeze in HALTED state.
- The Inner FSM cannot jump directly from INTENT_IDENTIFIED to ACTION_DISPATCHED without traversing AWAITING_APPROVAL for authorized actions.
- Action execution results must transition through OUTCOME_EVALUATED to recover gracefully from tool timeouts or runtime API errors.
- De-escalation is permitted from ELEVATED_SCRUTINY back to ACTIVE_MONITORING upon payload clearance, but CONTAINED_QUARANTINE and ATOMIC_HALT require an explicit human REVERT_STATE morphism.
- All state rollbacks (L1-002) must generate an immutable, cryptographic Audit Witness.

GLOSSARY:
- Inner FSM: State machine governing conversational dialogue and task planning progress.
- Outer FSM: State machine governing security boundaries, rate envelopes, token entropy, and exfiltration invariants.
- Halting Morphism (Φ_halt): The coupled mapping enforcing that an outer security violation dominates and halts inner execution.
- Outcome Evaluation: Deterministic evaluation of tool execution results to handle transient runtime failures without crashing the dialogue state.
- Revert Morphism: Functorial inverse transition stepping the state machine back to a verified safe state while recording an audit witness.

# ENTITY: InnerFsmState
MUST HAVE:
- current_state: Enum (IDLE, INTENT_IDENTIFIED, PARAM_ELICITATION, PLAN_PROPOSED, AWAITING_APPROVAL, ACTION_DISPATCHED, OUTCOME_EVALUATED, RESPONSE_SYNTHESIZED, TERMINAL_SUCCESS, TERMINAL_FAILED, HALTED)
- current_intent: String
- extracted_params: Dictionary
- active_plan: Optional[String]
- action_result: Optional[Dictionary]

RULES:
- R1: State transition ACTION_DISPATCHED must terminate in OUTCOME_EVALUATED before response synthesis.
- R2: If OUTCOME_EVALUATED reports tool failure, state must route to PLAN_PROPOSED (for tool fallback) or PARAM_ELICITATION (for user correction).

# ENTITY: OuterFsmState
MUST HAVE:
- current_state: Enum (SECURE_STANDBY, ACTIVE_MONITORING, ELEVATED_SCRUTINY, CONTAINED_QUARANTINE, ATOMIC_HALT)
- token_velocity: Float
- measured_entropy: Float
- active_capability_leases: List[String]
- taint_flags: List[String]
- violation_reason: Optional[String]

RULES:
- R1: Transition ELEVATED_SCRUTINY -> ACTIVE_MONITORING is valid when inspection clears anomaly.
- R2: Transition to ATOMIC_HALT emits a cryptographic Audit Witness and isolates the session in an Exception Enclave (L1-016).

# ENTITY: AuditWitness
MUST HAVE:
- witness_id: String
- trigger_event: String
- inner_state_at_halt: String
- outer_state_at_halt: String
- offending_tokens_digest: String
- blast_radius_contained: Boolean
- landauer_erased_bits: Float
- timestamp: Float

# EVENT: InnerTransitionCompleted
TRIGGER: Emitted on valid dialogue state step.
PAYLOAD: from_state, to_state, intent, timestamp

# EVENT: OuterSecurityEscalated
TRIGGER: Emitted when token anomalies or boundary violations escalate security posture.
PAYLOAD: from_state, to_state, reason, entropy, velocity

# EVENT: CoupledHaltTriggered
TRIGGER: Emitted when Outer FSM forces immediate halting of Inner FSM.
PAYLOAD: outer_state, inner_state_frozen, witness_id

# EVENT: FunctorialRevertExecuted
TRIGGER: Emitted when human operator triggers rollback morphism from halt.
PAYLOAD: rollback_witness_id, target_checkpoint, restored_at
