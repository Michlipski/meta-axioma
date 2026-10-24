"""Dynamically Compiled Domain Models for Contract: contract_byzantine_kinetic_facade."""

from dataclasses import dataclass, field
from typing import Any, Dict, List


class DomainInvariantViolationError(AssertionError):
    """Raised when a domain noun invariant is breached at runtime."""
    pass


@dataclass
class GossipPacket:
    """Cryptographically signed P2P gossip telemetry packet between spatial neighbors"""
    packet_id: str = ''
    sender_node_id: str = ''
    epoch_round: int = 0
    message_type: str = ''
    reported_wind_speed: float = 0.0
    signature_hash: str = ''

    def validate_invariants(self) -> bool:
        """Structurally enforces all ContractIR invariants for this noun."""
        if not (getattr(self, 'epoch_round') >= 0):
            raise DomainInvariantViolationError(f"Invariant violated on GossipPacket: epoch_round >= 0 (got {getattr(self, 'epoch_round')})")
        return True


@dataclass
class LouverNode:
    """Motorized architectural louver with microcontroller, optical encoder, and actuator"""
    node_id: str = ''
    blade_angle_deg: float = 90.0
    target_angle_deg: float = 0.0
    angular_velocity_dps: float = 15.0
    local_wind_speed_mps: float = 0.0
    local_shear_strain_kpa: float = 0.0
    consensus_state: str = ''
    optical_encoder_calibrated: bool = True
    consecutive_calm_epochs: int = 3

    def validate_invariants(self) -> bool:
        """Structurally enforces all ContractIR invariants for this noun."""
        if not (getattr(self, 'optical_encoder_calibrated') == True):
            raise DomainInvariantViolationError(f"Invariant violated on LouverNode: optical_encoder_calibrated == True (got {getattr(self, 'optical_encoder_calibrated')})")
        if not (getattr(self, 'blade_angle_deg') >= 0.0):
            raise DomainInvariantViolationError(f"Invariant violated on LouverNode: blade_angle_deg >= 0.0 (got {getattr(self, 'blade_angle_deg')})")
        if not (getattr(self, 'angular_velocity_dps') <= 15.0):
            raise DomainInvariantViolationError(f"Invariant violated on LouverNode: angular_velocity_dps <= 15.0 (got {getattr(self, 'angular_velocity_dps')})")
        if not (getattr(self, 'blade_angle_deg') <= 90.0):
            raise DomainInvariantViolationError(f"Invariant violated on LouverNode: blade_angle_deg <= 90.0 (got {getattr(self, 'blade_angle_deg')})")
        if not (getattr(self, 'consecutive_calm_epochs') >= 3):
            raise DomainInvariantViolationError(f"Invariant violated on LouverNode: consecutive_calm_epochs >= 3 (got {getattr(self, 'consecutive_calm_epochs')})")
        return True


@dataclass
class QuorumConsensusWitness:
    """Byzantine quorum proof confirming supermajority neighbor shear consensus"""
    node_id: str = ''
    epoch_round: int = 0
    active_neighbors_count: int = 2
    shear_confirmations_count: int = 0
    supermajority_ratio: float = 0.6667
    is_locked: bool = True

    def validate_invariants(self) -> bool:
        """Structurally enforces all ContractIR invariants for this noun."""
        if not (getattr(self, 'active_neighbors_count') >= 2):
            raise DomainInvariantViolationError(f"Invariant violated on QuorumConsensusWitness: active_neighbors_count >= 2 (got {getattr(self, 'active_neighbors_count')})")
        if not (getattr(self, 'supermajority_ratio') >= 0.6667):
            raise DomainInvariantViolationError(f"Invariant violated on QuorumConsensusWitness: supermajority_ratio >= 0.6667 (got {getattr(self, 'supermajority_ratio')})")
        if not (getattr(self, 'is_locked') == True):
            raise DomainInvariantViolationError(f"Invariant violated on QuorumConsensusWitness: is_locked == True (got {getattr(self, 'is_locked')})")
        return True


@dataclass
class WindShearTelemetry:
    """Dual anemometer sensory reading cross-validation and shear computation"""
    probe_id: str = ''
    node_id: str = ''
    timestamp_epoch_ms: int = 0
    primary_anemometer_mps: float = 0.0
    secondary_anemometer_mps: float = 0.0
    computed_shear_mps: float = 0.0
    is_valid: bool = True

    def validate_invariants(self) -> bool:
        """Structurally enforces all ContractIR invariants for this noun."""
        if not (getattr(self, 'is_valid') == True):
            raise DomainInvariantViolationError(f"Invariant violated on WindShearTelemetry: is_valid == True (got {getattr(self, 'is_valid')})")
        if not (getattr(self, 'computed_shear_mps') >= 0.0):
            raise DomainInvariantViolationError(f"Invariant violated on WindShearTelemetry: computed_shear_mps >= 0.0 (got {getattr(self, 'computed_shear_mps')})")
        return True

