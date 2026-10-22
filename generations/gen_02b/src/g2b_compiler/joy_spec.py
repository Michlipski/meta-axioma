"""Domain Specification and IR Formulations for Axioma Joy in System G2b.

Built 100% from the ground up from the approved elevator pitch:
"A mathematical category theory and structural reasoning educational platform for early stage learning
inspired by Eugenia Cheng's triumphant methodology teaching category theory to arts students.
Emphasizing visceral, tangible exploration over rote symbol manipulation."
"""

from g2b_compiler.ir.semantic_ir import (
    SemanticDomainIR, EntitySpec, EntityField, FieldType, DomainCapability, DomainInvariant
)
from g2b_compiler.ir.statechart_ir import StatechartIR, StateNode, Transition, EventSpec
from g2b_compiler.ir.contract_ir import DualBoundaryContractIR, NounContract, VerbContract


def build_joy_g2b_semantic_ir() -> SemanticDomainIR:
    """Builds comprehensive Semantic Domain IR for Axioma Joy under Generation 2b."""
    node_entity = EntitySpec(
        name="CategoryNode",
        plural_name="CategoryNodes",
        description="A mathematical object or concept coordinate within a categorical realm, defined by its relations.",
        fields=[
            EntityField(name="id", field_type=FieldType.STRING, description="UUID node identifier"),
            EntityField(name="label", field_type=FieldType.STRING, description="Display title"),
            EntityField(name="realm_id", field_type=FieldType.STRING, description="Parent realm reference"),
            EntityField(name="x", field_type=FieldType.FLOAT, description="Canvas X coordinate"),
            EntityField(name="y", field_type=FieldType.FLOAT, description="Canvas Y coordinate"),
            EntityField(name="icon", field_type=FieldType.STRING, default="✨", description="Tactile emoji/icon"),
            EntityField(name="description", field_type=FieldType.STRING, default="", description="Pedagogical notes"),
            EntityField(name="color", field_type=FieldType.STRING, default="#6366f1", description="UI accent color"),
        ]
    )

    arrow_entity = EntitySpec(
        name="MorphismArrow",
        plural_name="MorphismArrows",
        description="A directed morphism or process transformation connecting a domain object to a codomain object.",
        fields=[
            EntityField(name="id", field_type=FieldType.STRING, description="UUID morphism identifier"),
            EntityField(name="source_id", field_type=FieldType.STRING, description="Source domain object ID"),
            EntityField(name="target_id", field_type=FieldType.STRING, description="Target codomain object ID"),
            EntityField(name="label", field_type=FieldType.STRING, description="Transformation action label"),
            EntityField(name="realm_id", field_type=FieldType.STRING, description="Parent realm ID"),
            EntityField(name="is_identity", field_type=FieldType.BOOLEAN, default=False, description="Whether this is an identity arrow"),
            EntityField(name="composition_chain", field_type=FieldType.LIST_STRING, default=[], description="Composite sub-arrows if composite"),
            EntityField(name="is_reversed", field_type=FieldType.BOOLEAN, default=False, description="Flag for dual category inspection"),
        ]
    )

    realm_entity = EntitySpec(
        name="CategoryRealm",
        plural_name="CategoryRealms",
        description="A self-contained pedagogical world modeling category structures (Baking, Factor Cube, Functor Bridge).",
        fields=[
            EntityField(name="id", field_type=FieldType.STRING, description="Realm identifier"),
            EntityField(name="name", field_type=FieldType.STRING, description="Realm title"),
            EntityField(name="description", field_type=FieldType.STRING, description="Pedagogical description"),
            EntityField(name="icon", field_type=FieldType.STRING, default="🍰", description="Realm icon"),
            EntityField(name="is_default", field_type=FieldType.BOOLEAN, default=False, description="Initial active realm flag"),
        ]
    )

    capabilities = [
        DomainCapability(name="DirectMorphismDrawing", description="Tactile arrow drawing with snapping", affected_entities=["MorphismArrow"]),
        DomainCapability(name="MorphismComposition", description="Sequential composition of morphisms (g o f)", affected_entities=["MorphismArrow"], is_core_value=True),
        DomainCapability(name="CommutativeHarmony", description="Web Audio harmonic chord synthesis on commuting paths", affected_entities=["MorphismArrow"], is_core_value=True),
        DomainCapability(name="CulinaryKitchenRealm", description="Eugenia Cheng's baking processes vs parallel preparation", affected_entities=["CategoryNode", "MorphismArrow"]),
        DomainCapability(name="FactorizationCube30", description="3D rotatable prime factor lattice of divisors of 30", affected_entities=["CategoryNode", "MorphismArrow"]),
        DomainCapability(name="FunctorBridgeMapping", description="Structure-preserving analogies between culinary and art worlds", affected_entities=["CategoryRealm", "MorphismArrow"]),
        DomainCapability(name="DualCategoryInspection", description="1-tap arrow reversal demonstrating opposite category C^op", affected_entities=["MorphismArrow"]),
        DomainCapability(name="FunctorialUndo", description="Reversible history rollback (Cmd+Z)", affected_entities=["CategoryNode", "MorphismArrow"]),
        DomainCapability(name="LocalFirstSync", description="Offline-first JSON backup export and import", affected_entities=["CategoryNode", "MorphismArrow", "CategoryRealm"]),
    ]

    invariants = [
        # Tier 1 Structural Axioms
        DomainInvariant(invariant_id="L1-002", statement="Functorial Undo Reversibility", formal_rule="M_undo(M_action(S)) == S"),
        DomainInvariant(invariant_id="L1-011_3", statement="Decoupled Persistence", formal_rule="Local client state isolated from network dependencies"),
        DomainInvariant(invariant_id="L1-016", statement="Demarcated Exception Enclaves", formal_rule="Type mismatches bounded in educational recovery cycles"),
        DomainInvariant(invariant_id="NEG-G2-005", statement="Anti-Mock Substrate", formal_rule="Real Web Audio API harmonic oscillator chords, zero fake UI timers"),
        DomainInvariant(invariant_id="NEG-G2-006", statement="Clean-Slate Storage", formal_rule="Zero test dummy artifacts in initial production seed"),

        # Tier 2 Universal Usability & Ergonomics
        DomainInvariant(invariant_id="HEUR-UX-001", statement="Visibility of System Status", formal_rule="Active realm, selected node, and composable arrows declare visible status"),
        DomainInvariant(invariant_id="HEUR-UX-003", statement="User Control & Freedom", formal_rule="All compound states provide emergency cancel/abort exit"),
        DomainInvariant(invariant_id="HEUR-UX-005", statement="Error Prevention", formal_rule="Morphism drawing snaps only to valid candidate targets"),
        DomainInvariant(invariant_id="HEUR-COG-001", statement="Fitts's Law Touch Target Baseline", formal_rule="Touch targets measure >= 48x48px"),
        DomainInvariant(invariant_id="HEUR-COG-002", statement="Hick's Law Tool Palette Bounding", formal_rule="Primary toolbar capped at <= 5 actions"),

        # Tier 3 Domain Cognitive & Category Science
        DomainInvariant(invariant_id="AX-CAT-001", statement="Relational Primacy & Yoneda Principle", formal_rule="Objects defined exclusively through networks of incoming/outgoing morphisms"),
        DomainInvariant(invariant_id="AX-CAT-002", statement="Categorical Associativity", formal_rule="(h o g) o f == h o (g o f) across multi-hop paths"),
        DomainInvariant(invariant_id="AX-CAT-003", statement="Commutative Harmonic Resolution", formal_rule="Path1(A -> B) == Path2(A -> B) ==> HarmonicChime == True"),
        DomainInvariant(invariant_id="AX-CAT-004", statement="Functorial Preservation", formal_rule="F(g o f) == F(g) o F(f) and F(id_A) == id_F(A)"),
        DomainInvariant(invariant_id="AX-CAT-005", statement="Monoidal Process Separation", formal_rule="Parallel preparation (A (x) B) is topologically distinct from sequential composition (g o f)"),
    ]

    clean_seeds = {
        "realms": [
            {
                "id": "realm_baking",
                "name": "The Baker's Kitchen",
                "description": "Eugenia Cheng's signature recipe category: mixing, baking, and frosting processes.",
                "icon": "🍰",
                "is_default": True
            },
            {
                "id": "realm_cube30",
                "name": "Factorization Cube of 30",
                "description": "Cheng's 3D prime factor lattice of divisors of 30 (1, 2, 3, 5, 6, 10, 15, 30).",
                "icon": "🎲",
                "is_default": False
            },
            {
                "id": "realm_functor",
                "name": "The Analogy Bridge",
                "description": "Structure-preserving functor mapping culinary processes to geometric art.",
                "icon": "🌉",
                "is_default": False
            }
        ],
        "nodes": [
            # Baking Realm Nodes
            {"id": "node_flour", "label": "Flour & Sugar", "realm_id": "realm_baking", "x": 100, "y": 140, "icon": "🌾", "description": "Dry pantry ingredients", "color": "#f59e0b"},
            {"id": "node_eggs", "label": "Butter & Eggs", "realm_id": "realm_baking", "x": 100, "y": 300, "icon": "🥚", "description": "Wet richness ingredients", "color": "#fbbf24"},
            {"id": "node_batter", "label": "Cake Batter", "realm_id": "realm_baking", "x": 380, "y": 220, "icon": "🥣", "description": "Homogeneous mixed emulsion", "color": "#ec4899"},
            {"id": "node_cake", "label": "Baked Sponge", "realm_id": "realm_baking", "x": 660, "y": 220, "icon": "🎂", "description": "Heat-solidified golden cake", "color": "#10b981"},
            {"id": "node_frosting", "label": "Vanilla Frosting", "realm_id": "realm_baking", "x": 660, "y": 380, "icon": "🧁", "description": "Parallel prepared topping", "color": "#8b5cf6"},
            {"id": "node_masterpiece", "label": "Finished Cake", "realm_id": "realm_baking", "x": 920, "y": 300, "icon": "✨", "description": "Decorated celebration cake", "color": "#6366f1"},

            # Divisors of 30 Cube Nodes
            {"id": "cube_1", "label": "1", "realm_id": "realm_cube30", "x": 200, "y": 380, "icon": "⚪", "description": "Initial divisor object", "color": "#94a3b8"},
            {"id": "cube_2", "label": "2", "realm_id": "realm_cube30", "x": 380, "y": 420, "icon": "🔴", "description": "Prime factor 2", "color": "#ef4444"},
            {"id": "cube_3", "label": "3", "realm_id": "realm_cube30", "x": 140, "y": 240, "icon": "🟢", "description": "Prime factor 3", "color": "#22c55e"},
            {"id": "cube_5", "label": "5", "realm_id": "realm_cube30", "x": 260, "y": 280, "icon": "🔵", "description": "Prime factor 5", "color": "#3b82f6"},
            {"id": "cube_6", "label": "6", "realm_id": "realm_cube30", "x": 320, "y": 140, "icon": "🟠", "description": "2 x 3", "color": "#f97316"},
            {"id": "cube_10", "label": "10", "realm_id": "realm_cube30", "x": 480, "y": 300, "icon": "🟣", "description": "2 x 5", "color": "#a855f7"},
            {"id": "cube_15", "label": "15", "realm_id": "realm_cube30", "x": 220, "y": 120, "icon": "🟤", "description": "3 x 5", "color": "#eab308"},
            {"id": "cube_30", "label": "30", "realm_id": "realm_cube30", "x": 400, "y": 60, "icon": "🌟", "description": "Terminal object 2 x 3 x 5", "color": "#06b6d4"},

            # Functor Studio Nodes
            {"id": "art_pigment", "label": "Raw Pigment", "realm_id": "realm_functor", "x": 180, "y": 160, "icon": "🎨", "description": "Ground minerals", "color": "#f43f5e"},
            {"id": "art_medium", "label": "Oil Medium", "realm_id": "realm_functor", "x": 180, "y": 320, "icon": "🧪", "description": "Linseed binder", "color": "#eab308"},
            {"id": "art_paint", "label": "Oil Paint", "realm_id": "realm_functor", "x": 460, "y": 240, "icon": "🖌️", "description": "Suspended pigment", "color": "#8b5cf6"},
            {"id": "art_canvas", "label": "Finished Canvas", "realm_id": "realm_functor", "x": 760, "y": 240, "icon": "🖼️", "description": "Cured masterpiece", "color": "#10b981"},
        ],
        "arrows": [
            # Baking Realm Morphisms
            {"id": "arr_dry_mix", "source_id": "node_flour", "target_id": "node_batter", "label": "fold in", "realm_id": "realm_baking", "is_identity": False, "composition_chain": [], "is_reversed": False},
            {"id": "arr_wet_mix", "source_id": "node_eggs", "target_id": "node_batter", "label": "whisk together", "realm_id": "realm_baking", "is_identity": False, "composition_chain": [], "is_reversed": False},
            {"id": "arr_bake", "source_id": "node_batter", "target_id": "node_cake", "label": "bake at 350F", "realm_id": "realm_baking", "is_identity": False, "composition_chain": [], "is_reversed": False},
            {"id": "arr_frost", "source_id": "node_cake", "target_id": "node_masterpiece", "label": "apply frosting", "realm_id": "realm_baking", "is_identity": False, "composition_chain": [], "is_reversed": False},
            {"id": "arr_frost_prep", "source_id": "node_frosting", "target_id": "node_masterpiece", "label": "pipe rosettes", "realm_id": "realm_baking", "is_identity": False, "composition_chain": [], "is_reversed": False},

            # Divisors of 30 Prime Morphisms
            {"id": "cube_arr_1_2", "source_id": "cube_1", "target_id": "cube_2", "label": "x2", "realm_id": "realm_cube30", "is_identity": False, "composition_chain": [], "is_reversed": False},
            {"id": "cube_arr_1_3", "source_id": "cube_1", "target_id": "cube_3", "label": "x3", "realm_id": "realm_cube30", "is_identity": False, "composition_chain": [], "is_reversed": False},
            {"id": "cube_arr_1_5", "source_id": "cube_1", "target_id": "cube_5", "label": "x5", "realm_id": "realm_cube30", "is_identity": False, "composition_chain": [], "is_reversed": False},
            {"id": "cube_arr_2_6", "source_id": "cube_2", "target_id": "cube_6", "label": "x3", "realm_id": "realm_cube30", "is_identity": False, "composition_chain": [], "is_reversed": False},
            {"id": "cube_arr_3_6", "source_id": "cube_3", "target_id": "cube_6", "label": "x2", "realm_id": "realm_cube30", "is_identity": False, "composition_chain": [], "is_reversed": False},
            {"id": "cube_arr_2_10", "source_id": "cube_2", "target_id": "cube_10", "label": "x5", "realm_id": "realm_cube30", "is_identity": False, "composition_chain": [], "is_reversed": False},
            {"id": "cube_arr_5_10", "source_id": "cube_5", "target_id": "cube_10", "label": "x2", "realm_id": "realm_cube30", "is_identity": False, "composition_chain": [], "is_reversed": False},
            {"id": "cube_arr_3_15", "source_id": "cube_3", "target_id": "cube_15", "label": "x5", "realm_id": "realm_cube30", "is_identity": False, "composition_chain": [], "is_reversed": False},
            {"id": "cube_arr_5_15", "source_id": "cube_5", "target_id": "cube_15", "label": "x3", "realm_id": "realm_cube30", "is_identity": False, "composition_chain": [], "is_reversed": False},
            {"id": "cube_arr_6_30", "source_id": "cube_6", "target_id": "cube_30", "label": "x5", "realm_id": "realm_cube30", "is_identity": False, "composition_chain": [], "is_reversed": False},
            {"id": "cube_arr_10_30", "source_id": "cube_10", "target_id": "cube_30", "label": "x3", "realm_id": "realm_cube30", "is_identity": False, "composition_chain": [], "is_reversed": False},
            {"id": "cube_arr_15_30", "source_id": "cube_15", "target_id": "cube_30", "label": "x2", "realm_id": "realm_cube30", "is_identity": False, "composition_chain": [], "is_reversed": False},

            # Functor Art Realm Morphisms
            {"id": "art_arr_mix", "source_id": "art_pigment", "target_id": "art_paint", "label": "mull pigment", "realm_id": "realm_functor", "is_identity": False, "composition_chain": [], "is_reversed": False},
            {"id": "art_arr_apply", "source_id": "art_paint", "target_id": "art_canvas", "label": "apply impasto", "realm_id": "realm_functor", "is_identity": False, "composition_chain": [], "is_reversed": False},
        ]
    }

    return SemanticDomainIR(
        app_id="axioma_joy",
        title="Axioma Joy",
        tagline="Visceral Category Theory & Structural Reasoning Studio",
        persona="The Visceral Structural Thinker & Creative Visual Learner",
        jtbd_summary="Develop intuitive, visceral structural understanding of category theory (objects, morphisms, composition, commutativity, duality, universal properties, and monoidal processes) through tactile direct manipulation, culinary analogies, and harmonic commuting diagrams without rote symbol manipulation.",
        entities=[node_entity, arrow_entity, realm_entity],
        capabilities=capabilities,
        invariants=invariants,
        initial_clean_seeds=clean_seeds
    )


def build_joy_g2b_statechart_ir() -> StatechartIR:
    """Builds formal XState v5 Statechart IR for Axioma Joy under Generation 2b."""
    states = {
        "idle": StateNode(
            id="idle",
            description="Launch dashboard presenting active category realm canvas, tool palette, realm switchers, and commutativity indicators.",
            on={
                "SELECT_OBJECT": Transition(target="inspecting", event="SELECT_OBJECT"),
                "START_DRAW_ARROW": Transition(target="drawing_arrow", event="START_DRAW_ARROW"),
                "START_COMPOSITION": Transition(target="composing", event="START_COMPOSITION"),
                "CHECK_COMMUTATIVITY": Transition(target="commutativity_check", event="CHECK_COMMUTATIVITY"),
                "OPEN_BAKING": Transition(target="kitchen_realm", event="OPEN_BAKING"),
                "OPEN_CUBE30": Transition(target="cube_realm", event="OPEN_CUBE30"),
                "OPEN_FUNCTOR": Transition(target="functor_realm", event="OPEN_FUNCTOR"),
                "TOGGLE_DUAL": Transition(target="dual_category", event="TOGGLE_DUAL"),
                "OPEN_SYNC": Transition(target="sync_modal", event="OPEN_SYNC"),
                "RESET_CANVAS": Transition(target="idle", event="RESET_CANVAS"),
            }
        ),
        "inspecting": StateNode(
            id="inspecting",
            description="Inspecting an object node to view its relational coordinate network (incoming/outgoing arrows per Yoneda lemma).",
            on={
                "DESELECT": Transition(target="idle", event="DESELECT"),
                "DRAW_FROM_OBJECT": Transition(target="drawing_arrow", event="DRAW_FROM_OBJECT"),
                "COMPOSE_FROM_OBJECT": Transition(target="composing", event="COMPOSE_FROM_OBJECT"),
                "DELETE_OBJECT": Transition(target="idle", event="DELETE_OBJECT"),
                "ABORT": Transition(target="idle", event="ABORT"),
            }
        ),
        "drawing_arrow": StateNode(
            id="drawing_arrow",
            initial="selecting_source",
            description="Tactile arrow drawing workflow connecting domain and codomain objects.",
            states={
                "selecting_source": StateNode(
                    id="selecting_source",
                    description="User selects origin object A.",
                    on={
                        "SET_SOURCE": Transition(target="targeting", event="SET_SOURCE"),
                        "CANCEL": Transition(target="idle", event="CANCEL"),
                    }
                ),
                "targeting": StateNode(
                    id="targeting",
                    description="User drags arrow line to destination object B.",
                    on={
                        "SET_TARGET": Transition(target="validating", event="SET_TARGET"),
                        "CANCEL": Transition(target="idle", event="CANCEL"),
                    }
                ),
                "validating": StateNode(
                    id="validating",
                    description="Validates morphism constraints before committing.",
                    on={
                        "ARROW_VALID": Transition(target="idle", event="ARROW_VALID"),
                        "ARROW_INVALID": Transition(target="type_mismatch_enclave", event="ARROW_INVALID"),
                        "CANCEL": Transition(target="idle", event="CANCEL"),
                    }
                )
            },
            on={
                "ABORT": Transition(target="idle", event="ABORT")
            }
        ),
        "composing": StateNode(
            id="composing",
            initial="selecting_first",
            description="Interactive morphism composition tool verifying cod(f) = dom(g) and emitting composite arrow (g o f).",
            states={
                "selecting_first": StateNode(
                    id="selecting_first",
                    description="User selects first morphism f: A -> B.",
                    on={
                        "SELECT_FIRST": Transition(target="selecting_second", event="SELECT_FIRST"),
                        "CANCEL": Transition(target="idle", event="CANCEL"),
                    }
                ),
                "selecting_second": StateNode(
                    id="selecting_second",
                    description="User selects second morphism g: B -> C.",
                    on={
                        "SELECT_SECOND": Transition(target="evaluating", event="SELECT_SECOND"),
                        "CANCEL": Transition(target="idle", event="CANCEL"),
                    }
                ),
                "evaluating": StateNode(
                    id="evaluating",
                    description="Evaluating compositional validity and commutativity.",
                    on={
                        "COMPOSE_SUCCESS": Transition(target="composed_value", event="COMPOSE_SUCCESS"),
                        "COMPOSE_FAIL": Transition(target="type_mismatch_enclave", event="COMPOSE_FAIL"),
                        "CANCEL": Transition(target="idle", event="CANCEL"),
                    }
                ),
                "composed_value": StateNode(
                    id="composed_value",
                    meta={"is_value_state": True},
                    description="Composite morphism successfully generated with golden path highlight.",
                    on={
                        "ACCEPT_COMPOSITE": Transition(target="idle", event="ACCEPT_COMPOSITE"),
                        "TEST_COMMUTATIVITY": Transition(target="commutativity_check", event="TEST_COMMUTATIVITY"),
                        "UNDO": Transition(target="selecting_first", event="UNDO"),
                    }
                )
            },
            on={
                "CANCEL": Transition(target="idle", event="CANCEL"),
                "ABORT": Transition(target="idle", event="ABORT")
            }
        ),
        "commutativity_check": StateNode(
            id="commutativity_check",
            initial="comparing",
            description="Evaluating whether two parallel paths A -> B commute, triggering golden particle glow and harmonic audio chords.",
            states={
                "comparing": StateNode(
                    id="comparing",
                    description="Tracing multi-hop paths to evaluate equality of composition.",
                    on={
                        "EVALUATE_COMMUTATION": Transition(target="commuting", event="EVALUATE_COMMUTATION"),
                        "EVALUATE_NON_COMMUTATION": Transition(target="non_commuting", event="EVALUATE_NON_COMMUTATION"),
                        "CLOSE_CHECK": Transition(target="idle", event="CLOSE_CHECK"),
                    }
                ),
                "commuting": StateNode(
                    id="commuting",
                    meta={"is_value_state": True},
                    description="Paths commute! Illumination of commutative face + Web Audio major triad resolution chime (AX-CAT-003).",
                    on={
                        "CLOSE_CHECK": Transition(target="idle", event="CLOSE_CHECK"),
                        "SHARE_DIAGRAM": Transition(target="sync_modal", event="SHARE_DIAGRAM"),
                    }
                ),
                "non_commuting": StateNode(
                    id="non_commuting",
                    description="Paths do not commute: visual tension lines and pedagogical explanation.",
                    on={
                        "RESOLVE_TENSION": Transition(target="comparing", event="RESOLVE_TENSION"),
                        "CLOSE_CHECK": Transition(target="idle", event="CLOSE_CHECK"),
                    }
                )
            },
            on={
                "CLOSE_CHECK": Transition(target="idle", event="CLOSE_CHECK"),
                "ABORT": Transition(target="idle", event="ABORT")
            }
        ),
        "kitchen_realm": StateNode(
            id="kitchen_realm",
            initial="recipe_view",
            description="Eugenia Cheng's signature Baker's Kitchen realm: sequential baking vs parallel ingredient preparation (AX-CAT-005).",
            states={
                "recipe_view": StateNode(
                    id="recipe_view",
                    on={
                        "MIX_INGREDIENTS": Transition(target="mixing", event="MIX_INGREDIENTS"),
                        "BAKE_BATTER": Transition(target="baking", event="BAKE_BATTER"),
                        "PARALLEL_PREP": Transition(target="monoidal_prep", event="PARALLEL_PREP"),
                        "RETURN_DASHBOARD": Transition(target="idle", event="RETURN_DASHBOARD"),
                    }
                ),
                "mixing": StateNode(
                    id="mixing",
                    on={
                        "FINISH_MIX": Transition(target="recipe_view", event="FINISH_MIX"),
                    }
                ),
                "baking": StateNode(
                    id="baking",
                    on={
                        "FINISH_BAKE": Transition(target="recipe_view", event="FINISH_BAKE"),
                    }
                ),
                "monoidal_prep": StateNode(
                    id="monoidal_prep",
                    description="Preparing frosting in parallel with baking (A tensor B).",
                    on={
                        "COMBINE_LAYERS": Transition(target="recipe_view", event="COMBINE_LAYERS"),
                    }
                )
            },
            on={
                "RETURN_DASHBOARD": Transition(target="idle", event="RETURN_DASHBOARD"),
                "ABORT": Transition(target="idle", event="ABORT")
            }
        ),
        "cube_realm": StateNode(
            id="cube_realm",
            description="Cheng's 3D Factorization Cube of 30: prime factor generators and poset category lattice.",
            on={
                "ROTATE_CUBE": Transition(target="cube_realm", event="ROTATE_CUBE"),
                "SELECT_LATTICE_NODE": Transition(target="cube_realm", event="SELECT_LATTICE_NODE"),
                "VERIFY_CUBE_FACE": Transition(target="commutativity_check", event="VERIFY_CUBE_FACE"),
                "RETURN_DASHBOARD": Transition(target="idle", event="RETURN_DASHBOARD"),
                "ABORT": Transition(target="idle", event="ABORT")
            }
        ),
        "functor_realm": StateNode(
            id="functor_realm",
            description="The Analogy Bridge: Functor F mapping culinary domain to geometric art domain (AX-CAT-004).",
            on={
                "MAP_OBJECT": Transition(target="functor_realm", event="MAP_OBJECT"),
                "MAP_MORPHISM": Transition(target="functor_realm", event="MAP_MORPHISM"),
                "VERIFY_FUNCTORIALITY": Transition(target="commutativity_check", event="VERIFY_FUNCTORIALITY"),
                "RETURN_DASHBOARD": Transition(target="idle", event="RETURN_DASHBOARD"),
                "ABORT": Transition(target="idle", event="ABORT")
            }
        ),
        "dual_category": StateNode(
            id="dual_category",
            description="Opposite Category (C^op): Visualizing arrow reversal and dual structure.",
            on={
                "TOGGLE_BACK": Transition(target="idle", event="TOGGLE_BACK"),
                "INSPECT_DUAL_NODE": Transition(target="dual_category", event="INSPECT_DUAL_NODE"),
                "ABORT": Transition(target="idle", event="ABORT")
            }
        ),
        "type_mismatch_enclave": StateNode(
            id="type_mismatch_enclave",
            meta={"is_error_state": True},
            description="Friendly exception enclave explaining type mismatch when attempting non-composable morphisms cod(f) != dom(g) (L1-016).",
            on={
                "RETRY": Transition(target="drawing_arrow", event="RETRY"),
                "DISMISS": Transition(target="idle", event="DISMISS"),
                "CANCEL": Transition(target="idle", event="CANCEL"),
            }
        ),
        "sync_modal": StateNode(
            id="sync_modal",
            description="Local-first persistence management (JSON export/import).",
            on={
                "EXPORT_JSON": Transition(target="sync_modal", event="EXPORT_JSON"),
                "IMPORT_JSON": Transition(target="sync_modal", event="IMPORT_JSON"),
                "CLOSE_SYNC": Transition(target="idle", event="CLOSE_SYNC"),
                "ABORT": Transition(target="idle", event="ABORT")
            }
        ),
    }

    return StatechartIR(
        machine_id="axioma_joy_machine",
        initial="idle",
        states=states,
        context_schema={
            "active_realm": "realm_baking",
            "selected_node_id": None,
            "first_composed_morphism_id": None,
            "second_composed_morphism_id": None,
            "sound_enabled": True,
            "is_dual_mode": False,
            "last_commuted_face": None,
            "history_length": 0,
        }
    )


def build_joy_g2b_contract_ir() -> DualBoundaryContractIR:
    """Builds comprehensive Noun & Verb Dual Boundary Contract IR for Axioma Joy."""
    node_noun = NounContract(
        entity_name="CategoryNode",
        fields={
            "id": "string",
            "label": "string",
            "realm_id": "string",
            "x": "number",
            "y": "number",
            "icon": "string",
            "description": "string",
            "color": "string",
        },
        required_fields=["id", "label", "realm_id", "x", "y"],
        description="A mathematical object defined by its relational connections."
    )

    arrow_noun = NounContract(
        entity_name="MorphismArrow",
        fields={
            "id": "string",
            "source_id": "string",
            "target_id": "string",
            "label": "string",
            "realm_id": "string",
            "is_identity": "boolean",
            "composition_chain": "string[]",
            "is_reversed": "boolean",
        },
        required_fields=["id", "source_id", "target_id", "label", "realm_id"],
        description="A directed morphism connecting domain and codomain objects."
    )

    realm_noun = NounContract(
        entity_name="CategoryRealm",
        fields={
            "id": "string",
            "name": "string",
            "description": "string",
            "icon": "string",
            "is_default": "boolean",
        },
        required_fields=["id", "name"],
        description="A pedagogical category world."
    )

    verbs = {
        "CREATE_OBJECT": VerbContract(
            action_name="createObject",
            from_state="idle",
            to_state="idle",
            event_payload_type="{ node: CategoryNode }",
            description="Creates a new object node on the active realm canvas.",
            has_side_effect=True
        ),
        "DRAW_MORPHISM": VerbContract(
            action_name="drawMorphism",
            from_state="drawing_arrow.validating",
            to_state="idle",
            event_payload_type="{ arrow: MorphismArrow }",
            description="Commits a verified directional arrow between source and target objects.",
            has_side_effect=True
        ),
        "COMPOSE_MORPHISMS": VerbContract(
            action_name="composeMorphisms",
            from_state="composing.evaluating",
            to_state="composing.composed_value",
            event_payload_type="{ f_id: string, g_id: string }",
            description="Composes two compatible morphisms cod(f) == dom(g) into composite arrow (g o f).",
            has_side_effect=True
        ),
        "VERIFY_COMMUTATIVITY": VerbContract(
            action_name="verifyCommutativity",
            from_state="commutativity_check.comparing",
            to_state="commutativity_check.commuting",
            event_payload_type="{ path_a: string[], path_b: string[] }",
            description="Verifies that two parallel paths evaluate identically, sounding a harmonic chord.",
            has_side_effect=False
        ),
        "TOGGLE_DUAL_CATEGORY": VerbContract(
            action_name="toggleDualCategory",
            from_state="idle",
            to_state="dual_category",
            event_payload_type="{}",
            description="Reverses all arrow directions to inspect the opposite dual category C^op.",
            has_side_effect=False
        ),
        "UNDO_ACTION": VerbContract(
            action_name="undoAction",
            from_state="*",
            to_state="*",
            event_payload_type="{}",
            description="Rolls back canvas mutation losslessly via functorial undo stack (L1-002).",
            has_side_effect=True
        ),
    }

    return DualBoundaryContractIR(
        app_id="axioma_joy",
        nouns={
            "CategoryNode": node_noun,
            "MorphismArrow": arrow_noun,
            "CategoryRealm": realm_noun,
        },
        verbs=verbs
    )
