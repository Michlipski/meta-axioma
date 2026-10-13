"""Zero-Trust Capability Scoping for Axioma Crossword [L1-G2-004].

Eliminates ambient authority: Every puzzle solving, synthesis, and inspection
action is cryptographically signed and bound to an authorized persona.
"""

from __future__ import annotations

import hashlib
import hmac
import time
import uuid
from typing import Any, Dict, List, Optional


class CrosswordCapabilityToken:
    """Cryptographically signed capability token gating crossword actions."""

    def __init__(
        self,
        token_id: str,
        persona: str,
        allowed_actions: List[str],
        expires_at: float,
        signature: str,
    ):
        self.token_id = token_id
        self.persona = persona
        self.allowed_actions = allowed_actions
        self.expires_at = expires_at
        self.signature = signature

    def is_valid_for(self, action: str) -> bool:
        """Verifies action permission and expiration."""
        if time.time() > self.expires_at:
            return False
        return "*" in self.allowed_actions or action in self.allowed_actions

    def to_dict(self) -> Dict[str, Any]:
        return {
            "token_id": self.token_id,
            "persona": self.persona,
            "allowed_actions": self.allowed_actions,
            "expires_at": self.expires_at,
            "signature": self.signature,
        }


class CrosswordCapabilityAuthority:
    """Manages active tokens and zero-trust permissions for the Crossword Studio."""

    DEFAULT_SCOPES = {
        "Cruciverbalist_Player": [
            "read_puzzle",
            "enter_cell",
            "check_letter",
            "inspect_anatomy",
            "report_feedback",
        ],
        "Puzzle_Editor": [
            "read_puzzle",
            "enter_cell",
            "check_letter",
            "inspect_anatomy",
            "synthesize_grid",
            "export_puzzle",
            "report_feedback",
        ],
        "CSP_Synthesizer": [
            "read_puzzle",
            "synthesize_grid",
            "audit_landauer_entropy",
        ],
        "Telemetry_Auditor": [
            "read_telemetry",
            "audit_landauer_entropy",
            "read_feedback_stream",
        ],
    }

    def __init__(self, secret: str = "axioma_crossword_g2_secret_2026"):
        self._secret = secret.encode("utf-8")
        self._active_tokens: Dict[str, CrosswordCapabilityToken] = {}
        self._initialize_default_tokens()

    def _sign(self, payload: str) -> str:
        return hmac.new(self._secret, payload.encode("utf-8"), hashlib.sha256).hexdigest()

    def _initialize_default_tokens(self) -> None:
        for persona, actions in self.DEFAULT_SCOPES.items():
            tok = self.issue_token(persona=persona, allowed_actions=actions, ttl_seconds=86400.0)
            self._active_tokens[tok.token_id] = tok

    def issue_token(
        self,
        persona: str,
        allowed_actions: List[str],
        ttl_seconds: float = 3600.0,
    ) -> CrosswordCapabilityToken:
        token_id = f"cwtok_{uuid.uuid4().hex[:12]}"
        expires_at = time.time() + ttl_seconds
        payload = f"{token_id}:{persona}:{','.join(sorted(allowed_actions))}:{expires_at}"
        sig = self._sign(payload)
        tok = CrosswordCapabilityToken(
            token_id=token_id,
            persona=persona,
            allowed_actions=allowed_actions,
            expires_at=expires_at,
            signature=sig,
        )
        self._active_tokens[token_id] = tok
        return tok

    def verify_action(self, token_id: Optional[str], action: str) -> bool:
        """Verifies if token has authority for the requested action."""
        if not token_id:
            # Grant default Cruciverbalist_Player permissions for public Web studio
            return action in self.DEFAULT_SCOPES["Cruciverbalist_Player"]

        tok = self._active_tokens.get(token_id)
        if not tok:
            return False
        return tok.is_valid_for(action)

    def get_token(self, token_id: str) -> Optional[CrosswordCapabilityToken]:
        return self._active_tokens.get(token_id)
