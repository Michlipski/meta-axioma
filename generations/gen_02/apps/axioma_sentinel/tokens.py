"""Zero-Trust Capability Scoping for Axioma Sentinel [L1-G2-004].

Eliminates ambient authority: Every agent tool invocation must provide a valid,
cryptographically signed capability token scoped to the executing persona.
"""

from typing import Any, Dict, List, Optional
import hashlib
import hmac
import time
import uuid

from g2_compiler.capability_scoping import CapabilityTokenManager
from g2_compiler.types import CapabilitySecurityFault, CapabilityToken


class SentinelCapabilityAuthority:
    """Manages active tokens, permissions, and cryptographic witnesses for Sentinel."""

    DEFAULT_SCOPES = {
        "AI_Architect": [
            "read_telemetry",
            "rollback_state",
            "issue_token",
            "simulate_breach",
            "compile_app",
            "inspect_memory",
        ],
        "Research_Subagent": [
            "read_telemetry",
            "query_knowledge_graph",
            "propose_hypothesis",
        ],
        "Edge_Daemon": [
            "sync_state",
            "report_heartbeat",
            "audit_landauer_erasure",
        ],
        "Autonomous_Coder": [
            "read_telemetry",
            "execute_sandbox_test",
            "mutate_workspace",
        ],
    }

    def __init__(self, signing_secret: Optional[str] = "sentinel_root_secret_2026"):
        self.manager = CapabilityTokenManager(signing_secret=signing_secret)
        self._active_tokens: Dict[str, CapabilityToken] = {}
        self._initialize_default_tokens()

    def _initialize_default_tokens(self) -> None:
        """Issues baseline operational tokens for standard personas."""
        for persona, actions in self.DEFAULT_SCOPES.items():
            tok = self.manager.issue_token(persona=persona, allowed_actions=actions, ttl_seconds=86400.0)
            self._active_tokens[tok.token_id] = tok

    def get_token(self, token_id: str) -> Optional[CapabilityToken]:
        """Retrieves a token by ID."""
        return self._active_tokens.get(token_id)

    def issue_new_token(
        self, persona: str, allowed_actions: List[str], ttl_seconds: float = 3600.0
    ) -> CapabilityToken:
        """Issues a new scoped token and registers it in the active cache."""
        tok = self.manager.issue_token(persona=persona, allowed_actions=allowed_actions, ttl_seconds=ttl_seconds)
        self._active_tokens[tok.token_id] = tok
        return tok

    def verify_action(self, token_id: Optional[str], requested_action: str) -> CapabilityToken:
        """Verifies capability token. Raises CapabilitySecurityFault on ambient or unauthorized access."""
        if not token_id:
            raise CapabilitySecurityFault(
                f"[L1-G2-004 SECURITY FAULT] Ambient execution blocked: Action '{requested_action}' "
                f"attempted without a CapabilityToken."
            )

        token = self.get_token(token_id)
        if not token:
            raise CapabilitySecurityFault(
                f"[L1-G2-004 SECURITY FAULT] Unknown or expired token '{token_id}' for action '{requested_action}'."
            )

        if not self.manager.verify_token(token, requested_action):
            raise CapabilitySecurityFault(
                f"[L1-G2-004 SECURITY FAULT] Token '{token_id}' (Persona: '{token.persona}') "
                f"lacks permission for action '{requested_action}'. Allowed: {token.allowed_actions}."
            )

        return token

    def export_tokens_summary(self) -> List[Dict[str, Any]]:
        """Exports serialized tokens for UI dashboard display."""
        now = time.time()
        result = []
        for tok in self._active_tokens.values():
            result.append({
                "token_id": tok.token_id,
                "persona": tok.persona,
                "allowed_actions": tok.allowed_actions,
                "expires_in_seconds": max(0, int(tok.expires_at - now)),
                "witness_signature": tok.cryptographic_witness[:16] + "...",
                "is_expired": now > tok.expires_at,
            })
        return sorted(result, key=lambda x: x["persona"])
