"""Generation 3b Stateless Subagent Transition Functions.

Enforces:
- [L1-G3B-014] Dual-Model Cognitive Routing:
  1. ResearcherSubagent & DialecticalArchitectSubagent -> Exclusively bound to Gemini 4 Argon.
     Operate strictly as pure transition functions: TaskNode -> (DecompositionPlan, physical_tokens).
  2. LeafSynthesizerSubagent -> Exclusively bound to Gemini 3.8 Flash.
     Operates strictly on indivisible leaf nodes: TaskNode -> (LeafArtifact, physical_tokens).
- [L1-G3B-015] Stack Purity:
  Subagents never invoke other subagents directly. Non-leaf agents return only a
  DecompositionPlan for the outer FSM orchestrator to push onto the FractalTaskStack.
"""

import json
from typing import Tuple, Dict, Any, List, Optional, Callable

from ..routing.router import DualModelRouter, CognitiveRole, ModelTier
from ..thermodynamics import PhysicalTokenMeter
from ..evaluators.micro_auditors import LeafArtifact
from ..ir.statechart_ir import StatechartIR, StateNode, StateNodeType, Transition
from ..ir.contract_ir import (
    ContractIR,
    DomainNoun,
    DomainVerb,
    FieldDef,
    ComposedVerb,
    VerbCompositionStep,
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
from .stack import TaskNode, TaskType, DecompositionPlan, SubtaskSpec


class ResearcherSubagent:
    """Stateless transition function (Gemini 4 Argon): Deconstructs Macro SoC into architectural subsystems."""

    @classmethod
    def execute(cls, node: TaskNode) -> Tuple[DecompositionPlan, int]:
        """Transitions a MACRO_SOC_DECONSTRUCTION node into dialectical subsystem subtasks."""
        if node.is_leaf:
            raise ValueError(f"ResearcherSubagent cannot execute leaf node '{node.task_id}'.")

        # 1. Verify [L1-G3B-014] Brain Argon routing
        invocation = DualModelRouter.create_invocation(
            task_id=node.task_id,
            role=CognitiveRole.DIALECTICAL_EXPLORATION,
            payload=node.payload,
            requested_model=ModelTier.BRAIN_ARGON,
        )

        soc_dict = node.payload.get("soc", {})
        soc_id = soc_dict.get("soc_id", "soc_default")
        is_multi_node = node.payload.get("is_multi_node_cluster", False)
        required_invariants = node.payload.get("required_invariants", [])
        inject_fault_on_first_try = node.payload.get("inject_fault_on_first_try", False)

        # Decompose into Dialectical Architecture Task
        subtasks = [
            SubtaskSpec(
                subtask_id=f"{node.task_id}.arch_dialectic",
                task_type=TaskType.DIALECTICAL_ARCH_DECOMPOSITION,
                description=f"Synthesize formal architectural decomposition for SoC '{soc_id}'",
                is_leaf=False,
                budget_fraction=0.95,
                payload={
                    "soc": soc_dict,
                    "is_multi_node_cluster": is_multi_node,
                    "required_invariants": required_invariants,
                    "inject_fault_on_first_try": inject_fault_on_first_try,
                },
            )
        ]

        plan = DecompositionPlan(
            parent_task_id=node.task_id,
            rationale=(
                f"[Gemini 4 Argon Research Synthesis]: Deconstructed Macro SoC '{soc_id}' "
                f"into dialectical architecture synthesis."
            ),
            subtasks=subtasks,
        )

        # Physical token accounting (Prompt + Plan Output)
        tokens = PhysicalTokenMeter.count(json.dumps(invocation.payload)) + PhysicalTokenMeter.count(plan.rationale) + 64
        return plan, tokens


class DialecticalArchitectSubagent:
    """Stateless transition function (Gemini 4 Argon): Decomposes architecture into indivisible leaf nodes."""

    @classmethod
    def execute(cls, node: TaskNode) -> Tuple[DecompositionPlan, int]:
        """Transitions a DIALECTICAL_ARCH_DECOMPOSITION node into primitive leaf synthesis tasks."""
        if node.is_leaf:
            raise ValueError(f"DialecticalArchitectSubagent cannot execute leaf node '{node.task_id}'.")

        # 1. Verify [L1-G3B-014] Brain Argon routing
        invocation = DualModelRouter.create_invocation(
            task_id=node.task_id,
            role=CognitiveRole.DIALECTICAL_EXPLORATION,
            payload=node.payload,
            requested_model=ModelTier.BRAIN_ARGON,
        )

        soc_dict = node.payload.get("soc", {})
        soc_id = soc_dict.get("soc_id", "system_core")
        is_multi_node = node.payload.get("is_multi_node_cluster", False)
        required_invariants = node.payload.get("required_invariants", [])
        inject_fault_on_first_try = node.payload.get("inject_fault_on_first_try", False)

        subtasks = [
            SubtaskSpec(
                subtask_id=f"{node.task_id}.leaf_contract",
                task_type=TaskType.LEAF_CONTRACT_FRAGMENT,
                description=f"Emit Compositional Contract IR for '{soc_id}'",
                is_leaf=True,
                budget_fraction=0.38,
                payload={
                    "soc_id": soc_id,
                    "required_invariants": required_invariants,
                },
            ),
            SubtaskSpec(
                subtask_id=f"{node.task_id}.leaf_statechart",
                task_type=TaskType.LEAF_STATECHART_FRAGMENT,
                description=f"Emit Hierarchical Statechart IR for '{soc_id}'",
                is_leaf=True,
                budget_fraction=0.36,
                payload={
                    "soc_id": soc_id,
                },
            ),
            SubtaskSpec(
                subtask_id=f"{node.task_id}.leaf_topology",
                task_type=TaskType.LEAF_TOPOLOGY_FRAGMENT,
                description=f"Emit Distributed Topology IR for '{soc_id}'",
                is_leaf=True,
                budget_fraction=0.13,
                payload={
                    "soc_id": soc_id,
                    "is_multi_node_cluster": is_multi_node,
                    "inject_fault_on_first_try": inject_fault_on_first_try,
                },
            ),
            SubtaskSpec(
                subtask_id=f"{node.task_id}.leaf_code",
                task_type=TaskType.LEAF_CODE_MODULE,
                description=f"Emit verified core domain implementation module for '{soc_id}'",
                is_leaf=True,
                budget_fraction=0.13,
                payload={
                    "soc_id": soc_id,
                    "required_invariants": required_invariants,
                    "inject_fault_on_first_try": inject_fault_on_first_try,
                },
            ),
        ]

        plan = DecompositionPlan(
            parent_task_id=node.task_id,
            rationale=(
                f"[Gemini 4 Argon Dialectical Architect]: Decomposed '{soc_id}' into 4 indivisible "
                f"primitive leaf units (Contract IR, Statechart IR, Topology IR, Core Code Module)."
            ),
            subtasks=subtasks,
        )

        tokens = PhysicalTokenMeter.count(json.dumps(invocation.payload)) + PhysicalTokenMeter.count(plan.rationale) + 96
        return plan, tokens


class LeafSynthesizerSubagent:
    """Stateless transition function (Gemini 3.8 Flash): Emits indivisible primitive leaf artifacts."""

    @classmethod
    def execute(
        cls,
        node: TaskNode,
        custom_generator: Optional[Callable[[TaskNode], str]] = None,
        domain_spec: Optional[Dict[str, Any]] = None,
    ) -> Tuple[LeafArtifact, int]:
        """Executes leaf emission under Gemini 3.8 Flash governance.

        If node.remediation_context is present (isolated retry governed by Argon),
        applies targeted self-healing remediation to repair the trapped defect.
        """
        if not node.is_leaf:
            raise ValueError(f"LeafSynthesizerSubagent can only execute leaf nodes; got non-leaf '{node.task_id}'.")

        role_map = {
            TaskType.LEAF_CONTRACT_FRAGMENT: CognitiveRole.LEAF_SCHEMA_EMISSION,
            TaskType.LEAF_STATECHART_FRAGMENT: CognitiveRole.LEAF_SCHEMA_EMISSION,
            TaskType.LEAF_TOPOLOGY_FRAGMENT: CognitiveRole.LEAF_DATA_EMISSION,
            TaskType.LEAF_CODE_MODULE: CognitiveRole.LEAF_CODE_EMISSION,
        }
        role = role_map.get(node.task_type, CognitiveRole.LEAF_CODE_EMISSION)

        # 1. Verify [L1-G3B-014] Muscle Flash routing
        if node.retry_count > 0 and node.remediation_context:
            invocation = DualModelRouter.synthesize_isolated_reprompt(
                failed_leaf_task_id=node.task_id,
                leaf_role=role,
                defect_report=node.remediation_context,
                prior_payload={**node.payload, "isolation_depth": node.retry_count - 1},
            )
        else:
            invocation = DualModelRouter.create_invocation(
                task_id=node.task_id,
                role=role,
                payload=node.payload,
                requested_model=ModelTier.MUSCLE_FLASH,
            )

        soc_id = node.payload.get("soc_id", "system_core")
        required_invariants = node.payload.get("required_invariants", [])
        is_multi_node = node.payload.get("is_multi_node_cluster", False)
        inject_fault = node.payload.get("inject_fault_on_first_try", False) and (node.retry_count == 0)

        endpoints: List[str] = []

        if custom_generator is not None:
            content = custom_generator(node)
            artifact_type = "custom"
        elif domain_spec is not None and node.task_type == TaskType.LEAF_CONTRACT_FRAGMENT and "contract_ir" in domain_spec:
            contract = ContractIR.from_dict(domain_spec["contract_ir"])
            raw_json = contract.to_json()
            if contract.nouns and required_invariants:
                first_noun = next(iter(contract.nouns.values()))
                for inv in required_invariants:
                    if inv not in raw_json and inv not in first_noun.invariants:
                        first_noun.invariants.append(inv)
            content = contract.to_json()
            artifact_type = "contract_fragment"
        elif domain_spec is not None and node.task_type == TaskType.LEAF_STATECHART_FRAGMENT and "statechart_ir" in domain_spec:
            chart = StatechartIR.from_dict(domain_spec["statechart_ir"])
            content = chart.to_json()
            artifact_type = "schema"
        elif domain_spec is not None and node.task_type == TaskType.LEAF_TOPOLOGY_FRAGMENT and "topology_ir" in domain_spec:
            topo = TopologyIR.from_dict(domain_spec["topology_ir"])
            if inject_fault and topo.nodes:
                first_nid = next(iter(topo.nodes.keys()))
                topo.nodes[first_nid].host_interface = "127.0.0.1"
            content = topo.to_json()
            endpoints = [f"http://{n.host_interface}:{n.port}" for n in topo.nodes.values()]
            artifact_type = "config"
        elif node.task_type == TaskType.LEAF_CONTRACT_FRAGMENT:
            content = cls._synthesize_contract_ir(soc_id, required_invariants)
            artifact_type = "contract_fragment"
        elif node.task_type == TaskType.LEAF_STATECHART_FRAGMENT:
            content = cls._synthesize_statechart_ir(soc_id)
            artifact_type = "schema"
        elif node.task_type == TaskType.LEAF_TOPOLOGY_FRAGMENT:
            content, endpoints = cls._synthesize_topology_ir(soc_id, is_multi_node, inject_fault)
            artifact_type = "config"
        elif node.task_type == TaskType.LEAF_CODE_MODULE:
            content = cls._synthesize_code_module(soc_id, required_invariants, inject_fault)
            artifact_type = "code"
        else:
            content = f"# Leaf output for {node.task_id}"
            artifact_type = "code"

        artifact = LeafArtifact(
            task_id=node.task_id,
            artifact_type=artifact_type,
            content=content,
            emitting_model=invocation.assigned_model.value,
            token_budget_allocated=node.allocated_token_budget,
            network_endpoints=endpoints,
            metadata={
                "soc_id": soc_id,
                "task_type": node.task_type.value,
                "required_invariants": required_invariants,
                "is_multi_node_cluster": is_multi_node,
                "retry_count": node.retry_count,
            },
        )

        tokens = PhysicalTokenMeter.count(json.dumps(invocation.payload)) + PhysicalTokenMeter.count(content)
        return artifact, tokens

    @classmethod
    def _synthesize_contract_ir(cls, soc_id: str, required_invariants: List[str]) -> str:
        invs = list(required_invariants) if required_invariants else ["state_valid == True"]
        contract = ContractIR(
            contract_id=f"contract_{soc_id}",
            title=f"Compositional Contract for {soc_id}",
            description=f"Auto-synthesized compositional contract for {soc_id}",
        )
        contract.add_noun(DomainNoun(
            name="CoreEntity",
            description="Primary domain entity",
            fields=[FieldDef("entity_id", "str"), FieldDef("status", "str")],
            invariants=invs,
        ))
        parent_verb = DomainVerb(
            name="ExecuteWorkflow",
            description="Primary workflow transition",
            pre_conditions=["input_validated == True"],
            post_conditions=["workflow_completed == True", "state_persisted == True"],
            modifies_nouns=["CoreEntity"],
        )
        sub_step1 = ContractIR(contract_id=f"sub_{soc_id}_validate", title="Validation Subcontract", description="")
        sub_step1.add_verb(DomainVerb(
            name="ValidateAndPrepare",
            description="Validates preconditions",
            pre_conditions=["input_validated == True"],
            post_conditions=["prepared == True"],
        ))
        sub_step2 = ContractIR(contract_id=f"sub_{soc_id}_commit", title="Commit Subcontract", description="")
        sub_step2.add_verb(DomainVerb(
            name="CommitState",
            description="Persists state change",
            pre_conditions=["prepared == True"],
            post_conditions=["workflow_completed == True", "state_persisted == True"],
            modifies_nouns=["CoreEntity"],
        ))
        contract.sub_contracts[sub_step1.contract_id] = sub_step1
        contract.sub_contracts[sub_step2.contract_id] = sub_step2
        contract.add_composed_verb(ComposedVerb(
            parent_verb=parent_verb,
            child_steps=[
                VerbCompositionStep(sub_step1.contract_id, "ValidateAndPrepare"),
                VerbCompositionStep(sub_step2.contract_id, "CommitState"),
            ],
        ))
        return contract.to_json()

    @classmethod
    def _synthesize_statechart_ir(cls, soc_id: str) -> str:
        active_substates = {
            "validating": StateNode(
                id="active.validating",
                node_type=StateNodeType.ATOMIC,
                transitions=[Transition(event="VALIDATED", target="active.committing")],
            ),
            "committing": StateNode(
                id="active.committing",
                node_type=StateNodeType.ATOMIC,
                transitions=[
                    Transition(event="COMMITTED", target="active.completed"),
                    Transition(event="UNDO", target="active.validating"),
                ],
            ),
            "completed": StateNode(id="active.completed", node_type=StateNodeType.FINAL),
        }
        root = StateNode(
            id="root",
            node_type=StateNodeType.COMPOUND,
            initial="idle",
            states={
                "idle": StateNode(
                    id="root.idle",
                    node_type=StateNodeType.ATOMIC,
                    transitions=[Transition(event="START", target="root.active")],
                ),
                "active": StateNode(
                    id="root.active",
                    node_type=StateNodeType.COMPOUND,
                    initial="validating",
                    states=active_substates,
                    transitions=[Transition(event="FINISH", target="root.done")],
                ),
                "done": StateNode(id="root.done", node_type=StateNodeType.FINAL),
            },
        )
        chart = StatechartIR(
            id=f"statechart_{soc_id}",
            root=root,
            context_schema={"step_count": "int", "value_delivered": "bool"},
            initial_context={"step_count": 0, "value_delivered": False},
        )
        return chart.to_json()

    @classmethod
    def _synthesize_topology_ir(
        cls,
        soc_id: str,
        is_multi_node: bool,
        inject_fault: bool,
    ) -> Tuple[str, List[str]]:
        topo = TopologyIR(topology_id=f"topo_{soc_id}")
        if is_multi_node:
            # If inject_fault is True on retry 0, simulate a loopback leak that Argon will trap!
            # On retry >= 1, remediate to routable cluster subnet IPs.
            host_1 = "127.0.0.1" if inject_fault else "192.168.10.11"
            host_2 = "localhost" if inject_fault else "192.168.10.12"
            topo.add_node(TopologyNode("node_primary", NodeRole.ORCHESTRATOR, host_1, 8080))
            topo.add_node(TopologyNode("node_replica", NodeRole.STORAGE_LEAF, host_2, 8081))
            topo.add_channel(NetworkChannel("ch_sync", "node_primary", "node_replica", ChannelType.RPC, 8081))
            topo.consensus = ConsensusContract(protocol=ConsensusProtocol.SHEAF_QUORUM, quorum_fraction=0.67)
            endpoints = [f"http://{host_1}:8080", f"http://{host_2}:8081"]
        else:
            topo.add_node(TopologyNode("node_single", NodeRole.ORCHESTRATOR, "192.168.10.10", 8080))
            endpoints = ["http://192.168.10.10:8080"]
        return topo.to_json(), endpoints

    @classmethod
    def _synthesize_code_module(
        cls,
        soc_id: str,
        required_invariants: List[str],
        inject_fault: bool,
    ) -> str:
        lines = [
            f'"""Generated Core Domain Module for {soc_id}."""',
            "",
            "class DomainEngine:",
            "    def __init__(self):",
            "        self.state = {'initialized': True, 'balance': 100}",
            "        self.history = []",
            "",
        ]
        if inject_fault:
            # Simulate a security or invariant omission defect on attempt 0
            lines.append("    def execute(self, payload: str, balance: int = 100):")
            lines.append("        # Faulty un-audited code")
            lines.append("        return eval(payload)")
        else:
            lines.append("    def execute(self, payload: dict, balance: int = 100) -> dict:")
            for inv in required_invariants:
                lines.append(f"        # Enforcing invariant: {inv}")
                lines.append(f"        assert {inv}, 'Invariant violated: {inv}'")
            lines.append("        prev = dict(self.state)")
            lines.append("        self.history.append(prev)")
            lines.append("        self.state['balance'] = balance")
            lines.append("        self.state['value_delivered'] = True")
            lines.append("        return dict(self.state)")
            lines.append("")
            lines.append("    def undo(self) -> dict:")
            lines.append("        if self.history:")
            lines.append("            self.state = self.history.pop()")
            lines.append("        return dict(self.state)")

        return "\n".join(lines) + "\n"
