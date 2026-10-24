"""Generation 3b Universal Intermediate Representations (IR).

Exports:
- Hierarchical Statechart IR (XState v5 semantics, compound, parallel, history states)
- Compositional Contract IR (Nouns, Verbs, Pre/Post composition proofs)
- Distributed Topology IR (Nodes, Channels, Sheaf-Quorum consensus, Anti-Loopback Fidelity)
"""

from .statechart_ir import (
    StateNodeType,
    HistoryType,
    Transition,
    StateNode,
    StatechartIR,
)
from .contract_ir import (
    FieldDef,
    DomainNoun,
    DomainVerb,
    VerbCompositionStep,
    ComposedVerb,
    ContractProofWitness,
    ContractIR,
)
from .topology_ir import (
    NodeRole,
    ChannelType,
    ConsensusProtocol,
    TopologyNode,
    NetworkChannel,
    ConsensusContract,
    TopologyIR,
    TopologicalLoopbackViolation,
)

__all__ = [
    # Statechart
    "StateNodeType",
    "HistoryType",
    "Transition",
    "StateNode",
    "StatechartIR",
    # Contract
    "FieldDef",
    "DomainNoun",
    "DomainVerb",
    "VerbCompositionStep",
    "ComposedVerb",
    "ContractProofWitness",
    "ContractIR",
    # Topology
    "NodeRole",
    "ChannelType",
    "ConsensusProtocol",
    "TopologyNode",
    "NetworkChannel",
    "ConsensusContract",
    "TopologyIR",
    "TopologicalLoopbackViolation",
]
