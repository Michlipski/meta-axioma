"""Axioma Fabric Package.

High-throughput distributed Sheaf-CRDT event streaming and real-time
state coordination fabric.
"""

from .models import (
    CapabilityToken,
    CausalEvent,
    CocycleWitness,
    PartitionState,
    VectorClock,
)
from .thermodynamics import (
    BOLTZMANN_CONSTANT,
    LANDAUER_BIT_ENERGY_JOULES,
    LandauerRingBuffer,
    ThermodynamicBackpressureError,
)
from .sheaf_broker import (
    FabricBrokerNode,
    FabricPartitionError,
    FabricSecurityError,
)
from .cocycle_auditor import FabricCocycleAuditor
from .chaos import FabricChaosCrucible
from .gateway import FabricGateway

__all__ = [
    "CapabilityToken",
    "CausalEvent",
    "CocycleWitness",
    "PartitionState",
    "VectorClock",
    "BOLTZMANN_CONSTANT",
    "LANDAUER_BIT_ENERGY_JOULES",
    "LandauerRingBuffer",
    "ThermodynamicBackpressureError",
    "FabricBrokerNode",
    "FabricPartitionError",
    "FabricSecurityError",
    "FabricCocycleAuditor",
    "FabricChaosCrucible",
    "FabricGateway",
]
