"""Tier 1 Situation of Concern & Universal IR Seed Specification for `soc_byzantine_kinetic_facade`.

Axioma Kinetic Façade Studio (Canonical Port 8101):
1. Root Frictions:
   - Centralized building management systems (BMS) fail or partition during severe storm microbursts,
     stranding motorized kinetic louvers at sail attack angles (>45 deg) and causing destructive torque
     and mounting bracket failure (>450 N*m).
   - Sensor icing or Byzantine node faults report false calm or spurious storms, risking structural
     fatigue or unnecessary daylight lockout.
   - Physical mechanical actuators cannot execute in-memory 'Functorial Undo' rollbacks without violating
     thermodynamic causality and gear inertia; requires an Orderly Calibrated Unwind Recovery Pipeline.
2. Actors:
   - The Wind Vector (Adversary): Atmospheric microbursts exceeding 25.0 m/s with localized shear gradients.
   - The Mesh Node (Autonomous Edge Agent): Motorized kinetic louver with local microcontroller, optical
     blade angle encoder (0-90 deg), and dual ultrasonic anemometers.
   - Facade Structural Engineer & Facility Director (Human Stakeholder): Verifies occupant safety, zero
     facade detachment, and monitors real-time pBFT consensus on a lightweight 2D diagnostic dashboard.
3. Architectural Constraints:
   - [L1-G3B-012] Topological Fidelity: 9 nodes arranged in a 3x3 spatial lattice interconnected by 12
     bidirectional P2P gossip channels, binding strictly to routable non-loopback interfaces (10.99.10.x:8101).
   - [L1-G3B-011] Compositional Contract: Louver transitions to locked_flat_rigid (0 deg) ONLY if >= 2/3
     active physical neighbors confirm wind shear > 25.0 m/s within the epoch window.
   - [L1-G3B-017] Reflexive Quine Daughter Isolation Protocol: Certified daughter compiler sandbox verification.
"""

from typing import Dict, Any, List

from .models import (
    SituationOfConcern,
    SoCAltitude,
    Actor,
    Friction,
    FrictionSeverity,
    EnvironmentalConstraint,
    ConstraintType,
)
from .normalizer import SoCNormalizer
from ..ir.contract_ir import (
    ContractIR,
    DomainNoun,
    DomainVerb,
    FieldDef,
    ComposedVerb,
    VerbCompositionStep,
)
from ..ir.statechart_ir import (
    StatechartIR,
    StateNode,
    StateNodeType,
    Transition,
)
from ..ir.topology_ir import (
    TopologyIR,
    TopologyNode,
    NodeRole,
    NetworkChannel,
    ChannelType,
    ConsensusContract,
    ConsensusProtocol,
)


SOC_ID_FACADE = "soc_byzantine_kinetic_facade"

REQUIRED_INVARIANTS_FACADE: List[str] = [
    "blade_angle_deg >= 0.0",
    "blade_angle_deg <= 90.0",
    "angular_velocity_dps <= 15.0",
    "optical_encoder_calibrated == True",
    "supermajority_ratio >= 0.6667",
    "consecutive_calm_epochs >= 3",
]


def build_kinetic_facade_soc() -> SituationOfConcern:
    """Constructs and normalizes the Tier 1 Situation of Concern for `soc_byzantine_kinetic_facade`."""
    macro_soc = SituationOfConcern(
        soc_id=SOC_ID_FACADE,
        title="Axioma Kinetic Façade Studio: Byzantine Fault-Tolerant Louver Mesh & Aerodynamic Shear Mitigator",
        narrative=(
            "Contemporary high-rise kinetic building envelopes deploy motorized louvers for solar heat-gain "
            "management and daylight harvesting. During severe atmospheric microbursts and wind-shear gradients, "
            "localized airflow exceeds 25.0 m/s, inducing severe aerodynamic lift and mounting shear. Centralized "
            "building management systems (BMS) frequently partition, crash, or suffer power surges during severe "
            "storms, stranding louvers at high attack angles (acting as sails) and causing mounting bracket tearing "
            "and envelope detachment. Axioma Kinetic Façade Studio establishes an autonomous 3x3 P2P IoT mesh "
            "where motorized louvers reach Byzantine consensus over 12 bidirectional gossip links to lock flat rigid "
            "(0 deg) when supermajorities (>= 2/3) of physical neighbors confirm wind shear, and execute an Orderly "
            "Calibrated Unwind Recovery Pipeline upon sustained calm."
        ),
        altitude=SoCAltitude.MACRO,
        actors=[
            Actor(
                name="The Wind Vector (Adversary)",
                role="Atmospheric Aerodynamic Adversary",
                motivations=[
                    "Generate localized velocity gradients and severe microbursts exceeding 25.0 m/s",
                    "Exploit high louver attack angles to induce destructive aerodynamic lift and torque (> 450 N*m)",
                    "Create localized asymmetric pressure fields across high-rise building envelopes",
                ],
                frustrations=[
                    "Louvers transitioning to flat rigid (0 deg) orientation shedding aerodynamic drag by 88%",
                    "Decentralized sensor quorum detecting localized microbursts even when central BMS is offline",
                ],
            ),
            Actor(
                name="The Mesh Node (Autonomous Edge Agent)",
                role="Microcontroller-driven Kinetic Louver Actuator",
                motivations=[
                    "Maximize solar daylighting and thermal efficiency during calm conditions (0 to 90 deg tracking)",
                    "Preserve mechanical and structural mounting integrity under high wind-shear conditions",
                    "Reach rapid P2P Byzantine consensus (< 250ms) with physical spatial neighbors without central authority",
                ],
                frustrations=[
                    "Centralized controller partitions leaving actuators stranded at sail angles during sudden storms",
                    "Faulty or iced anemometer probes injecting misleading or Byzantine sensor noise",
                    "Physical gear and actuator backlash when abrupt software rollback commands violate mechanical inertia",
                ],
            ),
            Actor(
                name="Facade Structural Engineer & Facility Director",
                role="Human Architectural Safety Supervisor",
                motivations=[
                    "Eliminate structural envelope failures and zero facade panel detachments during category 3+ storms",
                    "Verify autonomous compliance with ISO/ASTM wind-load building codes and fail-closed safety standards",
                    "Inspect live mesh status and pBFT consensus audit trails on a lightweight diagnostic dashboard",
                ],
                frustrations=[
                    "Opaque proprietary BMS black-boxes with unverified failure modes during network partitions",
                    "Unbudgeted, heavyweight 3D physics simulations that cannot run on edge field tablets",
                    "False-alarm lockouts that permanently freeze facade shading due to single faulty sensors",
                ],
            ),
        ],
        frictions=[
            Friction(
                description="Centralized BMS single-point-of-failure strands louvers at sail attack angles during microbursts",
                severity=FrictionSeverity.CRITICAL,
                impact="Catastrophic mechanical torque exceeding 450 N*m, shearing mounting brackets and tearing envelope panels",
                trigger_conditions=["Severe storm lightning strike or network drop severs centralized BMS connectivity"],
            ),
            Friction(
                description="Byzantine and sensor faults: iced or drifting anemometers report false calm or spurious storms",
                severity=FrictionSeverity.HIGH,
                impact="Individual nodes either lock out unnecessarily (reducing daylight) or stay open during dangerous shear",
                trigger_conditions=["Probe icing, electrical noise, or sensor degradation on local node"],
            ),
            Friction(
                description="Actuator mechanical hysteresis: in-memory undo functor violates physical mechanics and gearbox causality",
                severity=FrictionSeverity.CRITICAL,
                impact="Sudden reverse torque trips motor drives or strips gearbox teeth under high aerodynamic loading",
                trigger_conditions=["Naïve software rollback command issued without ramped unwind calibration"],
            ),
            Friction(
                description="Daylighting optimization vs. aerodynamic safety trade-off",
                severity=FrictionSeverity.MEDIUM,
                impact="Premature recovery causes oscillation between open sail and emergency lock under gusty conditions",
                trigger_conditions=["Transient lulls in storm eye followed by secondary microbursts"],
            ),
        ],
        constraints=[
            EnvironmentalConstraint(
                nature=ConstraintType.THERMODYNAMIC,
                description="Maximum allowable aerodynamic blade torque before structural mounting failure is 450 N*m (reached at > 25.0 m/s when angle > 30 deg); flat rigid lock (0 deg) reduces drag coefficient Cd by 88%",
                boundary_limit="Torque <= 450 N*m; Flat angle = 0.0 deg",
            ),
            EnvironmentalConstraint(
                nature=ConstraintType.TECHNICAL,
                description="Actuator dynamic slew rate bounded to max 15.0 deg/s with mandatory ramped deceleration to prevent gearbox shearing",
                boundary_limit="Slew rate <= 15.0 deg/s",
            ),
            EnvironmentalConstraint(
                nature=ConstraintType.REGULATORY,
                description="Byzantine fault tolerance requires >= 2/3 supermajority consensus of physical neighbors before entering locked flat rigid state",
                boundary_limit="Neighbor shear confirmations / active neighbors >= 0.6667",
            ),
            EnvironmentalConstraint(
                nature=ConstraintType.TECHNICAL,
                description="[L1-G3B-012] Topological Fidelity: 9 nodes on routable cluster subnet (10.99.10.x:8101), interconnected by 12 bidirectional P2P gossip channels, rejecting single-machine loopback shortcuts",
                boundary_limit="Non-loopback 10.99.10.x subnet",
            ),
        ],
        unmet_needs=[
            "Autonomous decentralized Byzantine quorum consensus on atmospheric shear without reliance on central BMS backhaul",
            "Robust Byzantine tolerance against faulty or deceptive sensor nodes within local cliques",
            "Physically causal Orderly Calibrated Unwind Recovery Pipeline from locked_flat_rigid back to phototropic tracking",
            "Lightweight 2D SVG diagnostic telemetry dashboard visualizing lattice topology, live blade angles, gossip pulses, and pBFT consensus logs",
        ],
    )

    SoCNormalizer.normalize_tier1(macro_soc)

    meso_specs = [
        {
            "soc_id": "soc_meso_p2p_byzantine_consensus",
            "title": "Subsystem: P2P Gossip & Sheaf-Quorum Aerodynamic Consensus",
            "narrative": "Decentralized louver nodes in a 3x3 spatial lattice broadcast signed dual-anemometer telemetry and vote on shear events without a central coordinator.",
            "frictions": [
                Friction(
                    description="P2P packet loss and Byzantine sensor deception during high wind bursts",
                    severity=FrictionSeverity.HIGH,
                    impact="Could prevent quorum formation or trigger false lockdowns",
                    trigger_conditions=["High RF attenuation or sensor icing"],
                ).to_dict()
            ],
            "unmet_needs": ["Cryptographic gossip propagation and 2/3 supermajority voting over 12 bidirectional links"],
        }
    ]
    SoCNormalizer.decompose_fractal(macro_soc, meso_specs)

    micro_specs = [
        {
            "soc_id": "soc_micro_calibrated_actuator_unwind",
            "title": "Interaction: Microcontroller Optical Slew & Calibrated Unwind",
            "narrative": "Local edge microcontroller executing smooth motor acceleration ramps, optical encoder zeroing, and orderly calm recovery.",
            "frictions": [
                Friction(
                    description="Mechanical backlash and motor inertia during abrupt state changes",
                    severity=FrictionSeverity.HIGH,
                    impact="Gear tooth fatigue or motor thermal tripping",
                    trigger_conditions=["Abrupt reversal command without deceleration"],
                ).to_dict()
            ],
            "unmet_needs": ["Controlled staged slew rate (<= 15 deg/s) and sustained 3-epoch calm verification window"],
        }
    ]
    SoCNormalizer.decompose_fractal(macro_soc.sub_socs[0], micro_specs)

    return macro_soc


def build_kinetic_facade_contract_ir() -> ContractIR:
    """Constructs the Universal Compositional ContractIR for `soc_byzantine_kinetic_facade`."""
    nouns = {
        "LouverNode": DomainNoun(
            name="LouverNode",
            description="Motorized architectural louver with microcontroller, optical encoder, and actuator",
            fields=[
                FieldDef("node_id", "str", False, "Spatial identifier e.g. node_c"),
                FieldDef("blade_angle_deg", "float", False, "Current optical blade angle (0.0 to 90.0 deg)"),
                FieldDef("target_angle_deg", "float", False, "Target angle commanded by solar tracker or safety override"),
                FieldDef("angular_velocity_dps", "float", False, "Current slew rate in deg/s"),
                FieldDef("local_wind_speed_mps", "float", False, "Locally computed wind speed"),
                FieldDef("local_shear_strain_kpa", "float", False, "Mounting bracket strain gauge reading"),
                FieldDef("consensus_state", "str", False, "Node state: TRACKING, PREPARE, COMMIT, LOCKED_FLAT, RECOVERING"),
                FieldDef("optical_encoder_calibrated", "bool", False, "True if optical zero-index is verified"),
                FieldDef("consecutive_calm_epochs", "int", False, "Count of consecutive calm heartbeat rounds"),
            ],
            invariants=[
                "optical_encoder_calibrated == True",
                "blade_angle_deg >= 0.0",
                "angular_velocity_dps <= 15.0",
            ],
        ),
        "WindShearTelemetry": DomainNoun(
            name="WindShearTelemetry",
            description="Dual anemometer sensory reading cross-validation and shear computation",
            fields=[
                FieldDef("probe_id", "str", False, "Ultrasonic probe assembly ID"),
                FieldDef("node_id", "str", False, "Originating louver node ID"),
                FieldDef("timestamp_epoch_ms", "int", False, "POSIX millisecond timestamp"),
                FieldDef("primary_anemometer_mps", "float", False, "Primary sonic wind speed"),
                FieldDef("secondary_anemometer_mps", "float", False, "Secondary sonic wind speed"),
                FieldDef("computed_shear_mps", "float", False, "Cross-validated wind velocity"),
                FieldDef("is_valid", "bool", False, "True if primary and secondary are within tolerance"),
            ],
            invariants=[
                "is_valid == True",
                "computed_shear_mps >= 0.0",
            ],
        ),
        "GossipPacket": DomainNoun(
            name="GossipPacket",
            description="Cryptographically signed P2P gossip telemetry packet between spatial neighbors",
            fields=[
                FieldDef("packet_id", "str", False, "Unique packet UUID"),
                FieldDef("sender_node_id", "str", False, "Originating neighbor node ID"),
                FieldDef("epoch_round", "int", False, "Sequential consensus epoch index"),
                FieldDef("message_type", "str", False, "GOSSIP_TELEMETRY, PRE_PREPARE, PREPARE, COMMIT, CALM"),
                FieldDef("reported_wind_speed", "float", False, "Reported wind speed reading"),
                FieldDef("signature_hash", "str", False, "SHA-256 payload signature"),
            ],
            invariants=[
                "epoch_round >= 0",
            ],
        ),
        "QuorumConsensusWitness": DomainNoun(
            name="QuorumConsensusWitness",
            description="Byzantine quorum proof confirming supermajority neighbor shear consensus",
            fields=[
                FieldDef("node_id", "str", False, "Subject louver node"),
                FieldDef("epoch_round", "int", False, "Consensus round index"),
                FieldDef("active_neighbors_count", "int", False, "Number of active spatial grid neighbors"),
                FieldDef("shear_confirmations_count", "int", False, "Number of neighbors confirming shear > 25 m/s"),
                FieldDef("supermajority_ratio", "float", False, "Ratio of confirmations to active neighbors"),
                FieldDef("is_locked", "bool", False, "True if supermajority meets 2/3 requirement"),
            ],
            invariants=[
                "active_neighbors_count >= 2",
                "supermajority_ratio >= 0.6667",
                "is_locked == True",
            ],
        ),
    }

    # Child Sub-Contract 1: Ultrasonic Anemometer Sampling
    sub_telemetry = ContractIR(
        contract_id="sub_wind_telemetry",
        title="Ultrasonic Anemometer Sampling Subcontract",
        description="Samples redundant sonic probes and cross-validates for differential error.",
    )
    sub_telemetry.add_verb(DomainVerb(
        name="SampleWindShearTelemetry",
        description="Sample dual ultrasonic anemometers and validate cross-sensor reading.",
        pre_conditions=[
            "optical_encoder_calibrated == True",
        ],
        post_conditions=[
            "telemetry_sampled == True",
            "is_valid == True",
        ],
        modifies_nouns=["WindShearTelemetry"],
    ))

    # Child Sub-Contract 2: P2P Gossip Broadcast
    sub_gossip = ContractIR(
        contract_id="sub_byzantine_gossip",
        title="Byzantine Gossip Broadcast Subcontract",
        description="Broadcasts signed telemetry to physical grid neighbors over TLS channels.",
    )
    sub_gossip.add_verb(DomainVerb(
        name="BroadcastGossipProposal",
        description="Broadcast proposal to adjacent cardinal neighbors.",
        pre_conditions=[
            "telemetry_sampled == True",
            "is_valid == True",
        ],
        post_conditions=[
            "gossip_broadcast_complete == True",
            "packet_verified == True",
        ],
        modifies_nouns=["GossipPacket"],
    ))

    # Child Sub-Contract 3: pBFT Quorum Verification
    sub_consensus = ContractIR(
        contract_id="sub_pBFT_consensus",
        title="Practical Byzantine Fault Tolerance Consensus Subcontract",
        description="Verifies 2/3 supermajority consensus across active physical neighbors.",
    )
    sub_consensus.add_verb(DomainVerb(
        name="VerifyNeighborQuorum",
        description="Compute neighborhood quorum confirmations and verify supermajority.",
        pre_conditions=[
            "gossip_broadcast_complete == True",
            "packet_verified == True",
        ],
        post_conditions=[
            "quorum_consensus_verified == True",
            "supermajority_ratio >= 0.6667",
            "is_locked == True",
        ],
        modifies_nouns=["QuorumConsensusWitness"],
    ))

    # Child Sub-Contract 4: Aerodynamic Flat Lock Stance
    sub_stance = ContractIR(
        contract_id="sub_aerodynamic_stance",
        title="Aerodynamic Flat Lock Actuator Subcontract",
        description="Engages fail-safe 0-degree rigid flat lockdown upon quorum certification.",
    )
    sub_stance.add_verb(DomainVerb(
        name="ExecuteEmergencyFlatLock",
        description="Slew blade to 0 degrees to shed aerodynamic shear.",
        pre_conditions=[
            "quorum_consensus_verified == True",
            "is_locked == True",
        ],
        post_conditions=[
            "blade_angle_deg == 0",
            "flat_lock_engaged == True",
        ],
        modifies_nouns=["LouverNode"],
    ))

    # Formal Composed Verb: MitigateAerodynamicShearCycle
    parent_verb = DomainVerb(
        name="MitigateAerodynamicShearCycle",
        description=(
            "Closed-loop Byzantine shear mitigation cycle: sample anemometers -> broadcast gossip "
            "-> verify neighbor supermajority quorum -> execute emergency 0-degree flat lock."
        ),
        pre_conditions=[
            "optical_encoder_calibrated == True",
        ],
        post_conditions=[
            "flat_lock_engaged == True",
            "blade_angle_deg == 0",
        ],
        modifies_nouns=["LouverNode", "WindShearTelemetry", "QuorumConsensusWitness"],
    )

    steps = [
        VerbCompositionStep(
            child_contract_id="sub_wind_telemetry",
            child_verb_name="SampleWindShearTelemetry",
            argument_bindings={"node_id": "node_id"},
            output_binding="telemetry",
        ),
        VerbCompositionStep(
            child_contract_id="sub_byzantine_gossip",
            child_verb_name="BroadcastGossipProposal",
            argument_bindings={"node_id": "node_id"},
            output_binding="broadcast_status",
        ),
        VerbCompositionStep(
            child_contract_id="sub_pBFT_consensus",
            child_verb_name="VerifyNeighborQuorum",
            argument_bindings={"node_id": "node_id"},
            output_binding="witness",
        ),
        VerbCompositionStep(
            child_contract_id="sub_aerodynamic_stance",
            child_verb_name="ExecuteEmergencyFlatLock",
            argument_bindings={"node_id": "node_id"},
            output_binding="lock_status",
        ),
    ]

    composed = {
        "MitigateAerodynamicShearCycle": ComposedVerb(
            parent_verb=parent_verb,
            child_steps=steps,
        )
    }

    contract = ContractIR(
        contract_id="contract_byzantine_kinetic_facade",
        title="Axioma Byzantine Kinetic Façade Contract",
        description="Formal invariants, nouns, and verbs governing P2P kinetic louver mesh and aerodynamic shear mitigation",
        nouns=nouns,
        verbs={},
        composed_verbs=composed,
    )

    contract.sub_contracts[sub_telemetry.contract_id] = sub_telemetry
    contract.sub_contracts[sub_gossip.contract_id] = sub_gossip
    contract.sub_contracts[sub_consensus.contract_id] = sub_consensus
    contract.sub_contracts[sub_stance.contract_id] = sub_stance

    return contract


def build_kinetic_facade_statechart_ir() -> StatechartIR:
    """Constructs the Universal Hierarchical StatechartIR (exactly 18 states) for `soc_byzantine_kinetic_facade`."""
    # Substates of boot (3 atomic states)
    sn_hw_init = StateNode(
        id="boot.hw_init",
        node_type=StateNodeType.ATOMIC,
        description="Hardware POST: verify motor driver, optical encoder, and sonic anemometers",
        transitions=[Transition(event="HW_OK", target="boot.calibration", description="POST passed")],
    )
    sn_calib = StateNode(
        id="boot.calibration",
        node_type=StateNodeType.ATOMIC,
        description="Optical encoder zero-index homing and angular limit calibration",
        transitions=[Transition(event="CALIBRATED", target="boot.neighbor_discovery", description="Optical index calibrated")],
    )
    sn_disc = StateNode(
        id="boot.neighbor_discovery",
        node_type=StateNodeType.ATOMIC,
        description="P2P neighbor handshake across 12 gossip grid channels",
        transitions=[Transition(event="MESH_JOINED", target="active", description="Neighbor links established")],
    )

    sn_boot = StateNode(
        id="boot",
        node_type=StateNodeType.COMPOUND,
        initial="boot.hw_init",
        description="Louver node initialization compound state",
        states={
            "boot.hw_init": sn_hw_init,
            "boot.calibration": sn_calib,
            "boot.neighbor_discovery": sn_disc,
        },
    )

    # Substates of active.normal_operation (3 atomic states)
    sn_sun_tracking = StateNode(
        id="normal_operation.sun_tracking",
        node_type=StateNodeType.ATOMIC,
        description="Phototropic tracking: computing optimal solar shading angle based on sun vector",
        transitions=[
            Transition(event="SOLAR_TICK", target="normal_operation.slew_positioning", description="New solar angle target calculated"),
            Transition(event="SHEAR_DETECTED", target="active.adversarial_consensus", description="Local wind shear exceeds 25 m/s"),
        ],
    )
    sn_slew = StateNode(
        id="normal_operation.slew_positioning",
        node_type=StateNodeType.ATOMIC,
        description="Controlled motor actuation slew at <= 15 deg/s",
        transitions=[
            Transition(event="TARGET_REACHED", target="normal_operation.calm_idle", description="Target angle reached within 0.5 deg"),
            Transition(event="SHEAR_DETECTED", target="active.adversarial_consensus", description="Wind burst interrupts slew"),
        ],
    )
    sn_idle = StateNode(
        id="normal_operation.calm_idle",
        node_type=StateNodeType.ATOMIC,
        description="Calm steady-state holding position; continuous anemometer sampling",
        transitions=[
            Transition(event="SUN_MOVED", target="normal_operation.sun_tracking", description="Solar ephemeris step update"),
            Transition(event="SHEAR_DETECTED", target="active.adversarial_consensus", description="Local or neighbor wind shear spike"),
        ],
    )

    sn_normal = StateNode(
        id="active.normal_operation",
        node_type=StateNodeType.COMPOUND,
        initial="normal_operation.sun_tracking",
        description="Normal daylighting and phototropic solar tracking operation",
        states={
            "normal_operation.sun_tracking": sn_sun_tracking,
            "normal_operation.slew_positioning": sn_slew,
            "normal_operation.calm_idle": sn_idle,
        },
    )

    # Substates of active.adversarial_consensus (3 atomic states: pBFT rounds)
    sn_pre_prepare = StateNode(
        id="adversarial_consensus.pre_prepare",
        node_type=StateNodeType.ATOMIC,
        description="pBFT Round 1: Local node detects shear, signs telemetry, and broadcasts proposal",
        transitions=[
            Transition(event="PROPOSAL_BROADCAST", target="adversarial_consensus.prepare", description="Telemetry broadcast to grid neighbors"),
        ],
    )
    sn_prepare = StateNode(
        id="adversarial_consensus.prepare",
        node_type=StateNodeType.ATOMIC,
        description="pBFT Round 2: Collecting neighbor PREPARE gossip packets; verifying 2/3 supermajority",
        transitions=[
            Transition(event="QUORUM_PREPARED", target="adversarial_consensus.commit", description=">= 2/3 neighbor confirmation received"),
            Transition(event="GUST_ABATED", target="active.normal_operation", description="Transient noise below threshold; return to tracking"),
        ],
    )
    sn_commit = StateNode(
        id="adversarial_consensus.commit",
        node_type=StateNodeType.ATOMIC,
        description="pBFT Round 3: Broadcasting signed COMMIT and initiating flat-lock command",
        transitions=[
            Transition(event="QUORUM_COMMITTED", target="active.locked_flat_rigid", description="Byzantine consensus sealed; execute lock"),
        ],
    )

    sn_consensus = StateNode(
        id="active.adversarial_consensus",
        node_type=StateNodeType.COMPOUND,
        initial="adversarial_consensus.pre_prepare",
        description="Decentralized Byzantine fault-tolerant consensus pipeline",
        states={
            "adversarial_consensus.pre_prepare": sn_pre_prepare,
            "adversarial_consensus.prepare": sn_prepare,
            "adversarial_consensus.commit": sn_commit,
        },
    )

    # Emergency locked flat rigid state (1 final state)
    sn_locked_flat = StateNode(
        id="active.locked_flat_rigid",
        node_type=StateNodeType.FINAL,
        description="Aerodynamic fail-closed lockdown at 0 deg blade angle; drag reduced by 88%",
        transitions=[
            Transition(event="CALM_THRESHOLD_DETECTED", target="active.unwind_recovery", description="Wind speed dropped below 12 m/s; enter unwind pipeline"),
        ],
    )

    # Substates of active.unwind_recovery (2 atomic states)
    sn_calm_check = StateNode(
        id="unwind_recovery.calm_sustained_check",
        node_type=StateNodeType.ATOMIC,
        description="Orderly Recovery Phase 1: Verify calm (<12 m/s) sustained for >= 3 consecutive heartbeat epochs across >= 2/3 neighbors",
        transitions=[
            Transition(event="CALM_CONFIRMED_3X", target="unwind_recovery.staged_motor_unwind", description="Sustained calm consensus certified"),
            Transition(event="SHEAR_SPIKE", target="active.locked_flat_rigid", description="Secondary wind burst aborts recovery back to flat lock"),
        ],
    )
    sn_staged_unwind = StateNode(
        id="unwind_recovery.staged_motor_unwind",
        node_type=StateNodeType.ATOMIC,
        description="Orderly Recovery Phase 2: Ramped, calibrated motor rotation back to phototropic tracking without gear shock",
        transitions=[
            Transition(event="UNWIND_COMPLETE", target="active.normal_operation", description="Calibrated recovery complete; resume normal tracking"),
            Transition(event="SHEAR_SPIKE", target="active.locked_flat_rigid", description="Wind burst triggers immediate fail-closed return"),
        ],
    )

    sn_unwind = StateNode(
        id="active.unwind_recovery",
        node_type=StateNodeType.COMPOUND,
        initial="unwind_recovery.calm_sustained_check",
        description="Orderly Calibrated Unwind Recovery Pipeline (replaces physically impossible Functorial Undo)",
        states={
            "unwind_recovery.calm_sustained_check": sn_calm_check,
            "unwind_recovery.staged_motor_unwind": sn_staged_unwind,
        },
    )

    # Active compound state (contains normal_op, consensus, locked_flat, unwind_recovery)
    sn_active = StateNode(
        id="active",
        node_type=StateNodeType.COMPOUND,
        initial="active.normal_operation",
        description="Operational state encompassing normal tracking, Byzantine consensus, lockdown, and recovery",
        states={
            "active.normal_operation": sn_normal,
            "active.adversarial_consensus": sn_consensus,
            "active.locked_flat_rigid": sn_locked_flat,
            "active.unwind_recovery": sn_unwind,
        },
    )

    # Root compound state
    root = StateNode(
        id="facade_system",
        node_type=StateNodeType.COMPOUND,
        initial="boot",
        description="Root hierarchical state machine for Byzantine kinetic facade louver node",
        states={
            "boot": sn_boot,
            "active": sn_active,
        },
    )

    return StatechartIR(
        id="statechart_byzantine_kinetic_facade",
        root=root,
        context_schema={
            "node_id": "str",
            "blade_angle_deg": "float",
            "target_angle_deg": "float",
            "local_wind_speed": "float",
            "consecutive_calm_epochs": "int",
            "active_neighbors": "int",
            "shear_confirmations": "int",
            "quorum_locked": "bool",
        },
        initial_context={
            "node_id": "node_c",
            "blade_angle_deg": 0.0,
            "target_angle_deg": 45.0,
            "local_wind_speed": 4.2,
            "consecutive_calm_epochs": 0,
            "active_neighbors": 4,
            "shear_confirmations": 0,
            "quorum_locked": False,
        },
    )


def build_kinetic_facade_topology_ir(inject_fault: bool = False) -> TopologyIR:
    """Constructs the 9-node 3x3 spatial lattice TopologyIR adhering to [L1-G3B-012] Topological Fidelity."""
    # 9 spatial nodes on routable cluster subnet 10.99.10.x (canonical port 8101)
    ip_base = "127.0.0.1" if inject_fault else "10.99.10"
    
    nodes = {
        "node_nw": TopologyNode("node_nw", NodeRole.WORKER, f"{ip_base}.11" if not inject_fault else "127.0.0.1", 8101, ["louver_actuator", "dual_anemometer", "optical_encoder"], 512),
        "node_n":  TopologyNode("node_n",  NodeRole.WORKER, f"{ip_base}.12" if not inject_fault else "127.0.0.1", 8101, ["louver_actuator", "dual_anemometer", "optical_encoder"], 512),
        "node_ne": TopologyNode("node_ne", NodeRole.WORKER, f"{ip_base}.13" if not inject_fault else "127.0.0.1", 8101, ["louver_actuator", "dual_anemometer", "optical_encoder"], 512),
        "node_w":  TopologyNode("node_w",  NodeRole.WORKER, f"{ip_base}.14" if not inject_fault else "127.0.0.1", 8101, ["louver_actuator", "dual_anemometer", "optical_encoder"], 512),
        "node_c":  TopologyNode("node_c",  NodeRole.WORKER, f"{ip_base}.15" if not inject_fault else "127.0.0.1", 8101, ["louver_actuator", "dual_anemometer", "optical_encoder"], 512),
        "node_e":  TopologyNode("node_e",  NodeRole.WORKER, f"{ip_base}.16" if not inject_fault else "127.0.0.1", 8101, ["louver_actuator", "dual_anemometer", "optical_encoder"], 512),
        "node_sw": TopologyNode("node_sw", NodeRole.WORKER, f"{ip_base}.17" if not inject_fault else "127.0.0.1", 8101, ["louver_actuator", "dual_anemometer", "optical_encoder"], 512),
        "node_s":  TopologyNode("node_s",  NodeRole.WORKER, f"{ip_base}.18" if not inject_fault else "127.0.0.1", 8101, ["louver_actuator", "dual_anemometer", "optical_encoder"], 512),
        "node_se": TopologyNode("node_se", NodeRole.WORKER, f"{ip_base}.19" if not inject_fault else "127.0.0.1", 8101, ["louver_actuator", "dual_anemometer", "optical_encoder"], 512),
    }

    # Exactly 12 bidirectional P2P gossip links in 3x3 lattice
    grid_edges = [
        ("node_nw", "node_n"),
        ("node_n",  "node_ne"),
        ("node_w",  "node_c"),
        ("node_c",  "node_e"),
        ("node_sw", "node_s"),
        ("node_s",  "node_se"),
        ("node_nw", "node_w"),
        ("node_w",  "node_sw"),
        ("node_n",  "node_c"),
        ("node_c",  "node_s"),
        ("node_ne", "node_e"),
        ("node_e",  "node_se"),
    ]

    channels = []
    for src, tgt in grid_edges:
        channels.append(NetworkChannel(
            channel_id=f"chan_{src}_{tgt}",
            source_node_id=src,
            target_node_id=tgt,
            channel_type=ChannelType.GOSSIP,
            port=8101,
            latency_ms_budget=20,
            tls_enforced=True,
        ))

    consensus = ConsensusContract(
        protocol=ConsensusProtocol.SHEAF_QUORUM,
        quorum_fraction=0.67,
        heartbeat_interval_ms=250,
        partition_strategy="fail_closed",
    )

    return TopologyIR(
        topology_id="topology_byzantine_kinetic_facade",
        nodes=nodes,
        channels=channels,
        consensus=consensus,
    )


def build_kinetic_facade_domain_spec() -> Dict[str, Any]:
    """Returns the serializable domain_spec bundle for `soc_byzantine_kinetic_facade`."""
    contract = build_kinetic_facade_contract_ir()
    statechart = build_kinetic_facade_statechart_ir()
    topology = build_kinetic_facade_topology_ir(inject_fault=False)
    endpoints = [
        f"http://{n.host_interface}:{n.port}"
        for n in topology.nodes.values()
    ]
    return {
        "contract_ir": contract.to_dict(),
        "statechart_ir": statechart.to_dict(),
        "topology_ir": topology.to_dict(),
        "endpoints": endpoints,
        "canonical_port": 8101,
        "required_invariants": REQUIRED_INVARIANTS_FACADE,
    }
