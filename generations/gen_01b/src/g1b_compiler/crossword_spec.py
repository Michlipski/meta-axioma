"""Clean Domain Specification and IR Formulations for Axioma Crossword in System G1b.

Employs the stripped-down, authentic elevator pitch without reactionary micro-prescriptive clutter:
"A clean, responsive cryptic crossword solving and construction studio. Play puzzles with fluid
keyboard/touch navigation and a clue dissector that teaches you how the cryptic clue works
(definition vs. indicator vs. fodder). Generate fresh, symmetrical grids on demand."
"""

from g1b_compiler.ir.semantic_ir import (
    SemanticDomainIR, EntitySpec, EntityField, FieldType, DomainCapability, DomainInvariant
)
from g1b_compiler.ir.statechart_ir import StatechartIR, StateNode, Transition, EventSpec
from g1b_compiler.ir.contract_ir import DualBoundaryContractIR, NounContract, VerbContract


def build_crossword_semantic_ir() -> SemanticDomainIR:
    """Builds clean Semantic IR for Axioma Crossword."""
    grid_entity = EntitySpec(
        name="CrosswordGrid",
        plural_name="CrosswordGrids",
        description="A crossword grid structure with cell intersections and clues.",
        fields=[
            EntityField(name="grid_id", field_type=FieldType.STRING, description="UUID primary key"),
            EntityField(name="title", field_type=FieldType.STRING, description="Puzzle title"),
            EntityField(name="size_rows", field_type=FieldType.INTEGER, default=7),
            EntityField(name="size_cols", field_type=FieldType.INTEGER, default=7),
            EntityField(name="cells", field_type=FieldType.JSON, description="2D matrix of letters / '#' blockers"),
            EntityField(name="symmetry", field_type=FieldType.STRING, default="ROTATIONAL_180"),
        ]
    )

    clue_entity = EntitySpec(
        name="CrypticClue",
        plural_name="CrypticClues",
        description="A cryptic crossword clue with verifiable universal grammar dissection.",
        fields=[
            EntityField(name="clue_id", field_type=FieldType.STRING, description="UUID primary key"),
            EntityField(name="grid_id", field_type=FieldType.STRING, description="Foreign key to grid"),
            EntityField(name="number", field_type=FieldType.INTEGER),
            EntityField(name="direction", field_type=FieldType.STRING, description="ACROSS | DOWN"),
            EntityField(name="surface_text", field_type=FieldType.STRING, description="Full clue reading"),
            EntityField(name="answer", field_type=FieldType.STRING, description="Upper-case solution word"),
            EntityField(name="definition", field_type=FieldType.STRING, description="Straight definition part"),
            EntityField(name="indicator", field_type=FieldType.STRING, description="Wordplay operator (e.g. anagram indicator)"),
            EntityField(name="fodder", field_type=FieldType.STRING, description="Input material to transform"),
            EntityField(name="clue_type", field_type=FieldType.STRING, default="ANAGRAM"),
        ]
    )

    job_entity = EntitySpec(
        name="SynthesisJob",
        plural_name="SynthesisJobs",
        description="Background AC-3 grid synthesis worker job.",
        fields=[
            EntityField(name="job_id", field_type=FieldType.STRING, description="Job tracking ID"),
            EntityField(name="status", field_type=FieldType.STRING, default="PENDING"),
            EntityField(name="grid_size", field_type=FieldType.INTEGER, default=7),
            EntityField(name="backtracks_count", field_type=FieldType.INTEGER, default=0),
            EntityField(name="progress_pct", field_type=FieldType.FLOAT, default=0.0),
        ]
    )

    capabilities = [
        DomainCapability(name="OptimisticSolving", description="0ms keystroke grid navigation and entry", affected_entities=["CrosswordGrid"]),
        DomainCapability(name="CrypticDissection", description="Interactive clue anatomy dissection", affected_entities=["CrypticClue"], is_core_value=True),
        DomainCapability(name="GridSynthesis", description="Asynchronous AC-3 constraint grid generator", affected_entities=["SynthesisJob", "CrosswordGrid"]),
    ]

    invariants = [
        DomainInvariant(invariant_id="L1-002", statement="Functorial Reversibility", formal_rule="Undo letter restores preceding grid state"),
        DomainInvariant(invariant_id="L1-004", statement="Universal Grammar", formal_rule="Clue AST decomposes to Definition + Indicator + Fodder"),
        DomainInvariant(invariant_id="NEG-G2-009", statement="Lexical Purity", formal_rule="All words in clue surface must be valid English words; answer not in clue"),
    ]

    clean_seeds = {
        "crossword_grids": [
            {
                "grid_id": "grid_seed_quick_01",
                "title": "Axioma Quick Cryptic #1",
                "size_rows": 7,
                "size_cols": 7,
                "cells": [
                    ["A", "X", "I", "O", "M", "#", "#"],
                    ["#", "#", "N", "#", "E", "#", "#"],
                    ["#", "#", "F", "#", "S", "#", "#"],
                    ["#", "#", "O", "#", "H", "#", "#"],
                    ["#", "#", "R", "#", "#", "#", "#"],
                    ["#", "#", "M", "#", "#", "#", "#"],
                    ["#", "#", "#", "#", "#", "#", "#"]
                ],
                "symmetry": "ROTATIONAL_180"
            }
        ]
    }

    return SemanticDomainIR(
        app_id="axioma_crossword",
        title="Axioma Crossword",
        tagline="Distributed Cryptic Crossword Studio & Dissector",
        persona="Cruciverbalist Solver & Puzzle Architect",
        jtbd_summary="Solve cryptic crosswords with instant keystroke validation and learn cryptic mechanisms through interactive clue anatomy dissection.",
        entities=[grid_entity, clue_entity, job_entity],
        capabilities=capabilities,
        invariants=invariants,
        initial_clean_seeds=clean_seeds
    )


def build_crossword_statechart_ir() -> StatechartIR:
    """Builds formal XState v5 Statechart IR for Axioma Crossword."""
    states = {
        "solving": StateNode(
            id="solving",
            initial="grid_navigating",
            description="Compound state governing active puzzle solving and grid navigation.",
            states={
                "grid_navigating": StateNode(
                    id="grid_navigating",
                    description="User moving between grid cells.",
                    on={
                        "SELECT_CELL": Transition(target="grid_navigating", event="SELECT_CELL"),
                        "ENTER_LETTER": Transition(target="letter_entered", event="ENTER_LETTER"),
                        "INSPECT_CLUE": Transition(target="dissecting", event="INSPECT_CLUE"),
                        "OPEN_STUDIO": Transition(target="synthesizing", event="OPEN_STUDIO"),
                    }
                ),
                "letter_entered": StateNode(
                    id="letter_entered",
                    description="Letter entered optimistically in local memory.",
                    on={
                        "AUTO_ADVANCE": Transition(target="grid_navigating", event="AUTO_ADVANCE"),
                        "UNDO_LETTER": Transition(target="grid_navigating", event="UNDO_LETTER", description="Reversible rollback"),
                        "GRID_COMPLETE": Transition(target="completed", event="GRID_COMPLETE"),
                    }
                ),
                "completed": StateNode(
                    id="completed",
                    description="Puzzle completed successfully.",
                    meta={"is_value_state": True},
                    on={
                        "NEW_PUZZLE": Transition(target="grid_navigating", event="NEW_PUZZLE"),
                    }
                )
            }
        ),
        "dissecting": StateNode(
            id="dissecting",
            initial="viewing",
            description="Compound state governing cryptic clue anatomy dissection.",
            states={
                "viewing": StateNode(
                    id="viewing",
                    description="Displaying parsed Definition, Indicator, and Fodder tokens.",
                    meta={"is_value_state": True},  # Core learning value delivered here!
                    on={
                        "DISMISS_DISSECTOR": Transition(target="solving.grid_navigating", event="DISMISS_DISSECTOR"),
                        "NEXT_CLUE": Transition(target="viewing", event="NEXT_CLUE"),
                    }
                )
            },
            on={
                "CLOSE": Transition(target="solving.grid_navigating", event="CLOSE")
            }
        ),
        "synthesizing": StateNode(
            id="synthesizing",
            initial="configuring",
            description="Compound state governing asynchronous AC-3 grid synthesis.",
            states={
                "configuring": StateNode(
                    id="configuring",
                    description="Selecting grid dimensions (7x7 or 9x9).",
                    on={
                        "START_SYNTHESIS": Transition(target="worker_running", event="START_SYNTHESIS"),
                        "CANCEL": Transition(target="solving.grid_navigating", event="CANCEL"),
                    }
                ),
                "worker_running": StateNode(
                    id="worker_running",
                    description="Asynchronous AC-3 backtracking worker.",
                    on={
                        "POLL_PROGRESS": Transition(target="worker_running", event="POLL_PROGRESS"),
                        "SYNTHESIS_SUCCESS": Transition(target="solving.grid_navigating", event="SYNTHESIS_SUCCESS"),
                        "SYNTHESIS_FAIL": Transition(target="error", event="SYNTHESIS_FAIL"),
                    }
                ),
                "error": StateNode(
                    id="error",
                    description="Synthesis timeout or dictionary exhaustion.",
                    meta={"is_error_state": True},
                    on={
                        "RETRY": Transition(target="worker_running", event="RETRY"),
                        "CANCEL": Transition(target="solving.grid_navigating", event="CANCEL"),
                    }
                )
            },
            on={
                "ABORT": Transition(target="solving.grid_navigating", event="ABORT")
            }
        )
    }

    events = {
        "SELECT_CELL": EventSpec(name="SELECT_CELL", payload_fields=["row", "col"]),
        "ENTER_LETTER": EventSpec(name="ENTER_LETTER", payload_fields=["char"]),
        "INSPECT_CLUE": EventSpec(name="INSPECT_CLUE", payload_fields=["clue_id"]),
        "OPEN_STUDIO": EventSpec(name="OPEN_STUDIO"),
        "AUTO_ADVANCE": EventSpec(name="AUTO_ADVANCE"),
        "UNDO_LETTER": EventSpec(name="UNDO_LETTER"),
        "GRID_COMPLETE": EventSpec(name="GRID_COMPLETE"),
        "NEW_PUZZLE": EventSpec(name="NEW_PUZZLE"),
        "DISMISS_DISSECTOR": EventSpec(name="DISMISS_DISSECTOR"),
        "NEXT_CLUE": EventSpec(name="NEXT_CLUE"),
        "CLOSE": EventSpec(name="CLOSE"),
        "START_SYNTHESIS": EventSpec(name="START_SYNTHESIS", payload_fields=["grid_size"]),
        "CANCEL": EventSpec(name="CANCEL"),
        "POLL_PROGRESS": EventSpec(name="POLL_PROGRESS"),
        "SYNTHESIS_SUCCESS": EventSpec(name="SYNTHESIS_SUCCESS", payload_fields=["grid"]),
        "SYNTHESIS_FAIL": EventSpec(name="SYNTHESIS_FAIL", payload_fields=["error"]),
        "RETRY": EventSpec(name="RETRY"),
        "ABORT": EventSpec(name="ABORT"),
    }

    return StatechartIR(
        machine_id="axioma_crossword_fsm",
        initial="solving",
        description="Formal XState v5 Statechart for Axioma Crossword Studio",
        states=states,
        events=events,
        context_schema={
            "active_grid": None,
            "selected_cell": {"row": 0, "col": 0},
            "selected_clue": None,
            "undo_stack": []
        }
    )


def build_crossword_contract_ir() -> DualBoundaryContractIR:
    """Builds Contract IR for Axioma Crossword."""
    grid_noun = NounContract(
        entity_name="CrosswordGrid",
        fields={
            "grid_id": "string",
            "title": "string",
            "size_rows": "number",
            "size_cols": "number",
            "cells": "string[][]",
            "symmetry": "string"
        },
        required_fields=["grid_id", "title", "size_rows", "size_cols", "cells"]
    )

    clue_noun = NounContract(
        entity_name="CrypticClue",
        fields={
            "clue_id": "string",
            "grid_id": "string",
            "number": "number",
            "direction": "string",
            "surface_text": "string",
            "answer": "string",
            "definition": "string",
            "indicator": "string",
            "fodder": "string",
            "clue_type": "string"
        },
        required_fields=["clue_id", "grid_id", "number", "direction", "surface_text", "answer", "definition"]
    )

    job_noun = NounContract(
        entity_name="SynthesisJob",
        fields={
            "job_id": "string",
            "status": "string",
            "grid_size": "number",
            "backtracks_count": "number",
            "progress_pct": "number"
        },
        required_fields=["job_id", "status", "grid_size"]
    )

    verbs = {
        "ENTER_LETTER": VerbContract(
            action_name="enterLetter",
            from_state="solving.grid_navigating",
            to_state="solving.letter_entered",
            event_payload_type="{ row: number, col: number, char: string }",
            description="Optimistically mutates active cell with reversible undo token.",
            has_side_effect=True
        ),
        "DISSECT_CLUE": VerbContract(
            action_name="dissectClue",
            from_state="solving.grid_navigating",
            to_state="dissecting.viewing",
            event_payload_type="{ clue_id: string }",
            description="Projects clue AST into Definition, Indicator, and Fodder tokens."
        ),
        "DISPATCH_SYNTHESIS": VerbContract(
            action_name="dispatchSynthesis",
            from_state="synthesizing.configuring",
            to_state="synthesizing.worker_running",
            event_payload_type="{ grid_size: number }",
            description="Spawns decoupled AC-3 worker thread to construct new grid.",
            has_side_effect=True
        )
    }

    return DualBoundaryContractIR(
        app_id="axioma_crossword",
        nouns={"CrosswordGrid": grid_noun, "CrypticClue": clue_noun, "SynthesisJob": job_noun},
        verbs=verbs
    )
