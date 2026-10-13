"""Zero-Ambient Distributed Capability Mesh Engine (L1-G3-002).

Enforces zero ambient privileges across distributed service boundaries.
Every inter-service call (Gateway -> Service -> Worker -> Storage) must
carry an HMAC-signed capability token with cryptographic scope attenuation.
"""

from __future__ import annotations

import hashlib
import hmac
import time
import uuid
from typing import Dict, List, Optional, Set, Tuple

try:
    from .models import DistributedCapabilityToken
except ImportError:
    from models import DistributedCapabilityToken


class DistributedCapabilityAuthority:
    """Issues, delegates, attenuates, and verifies cryptographic capability tokens."""

    def __init__(self, master_secret: Optional[str] = None):
        self._secret = (master_secret or f"axioma_g3_mesh_secret_{uuid.uuid4().hex}").encode("utf-8")
        self._tokens: Dict[str, DistributedCapabilityToken] = {}
        self._revoked_tokens: Set[str] = set()

    def issue_token(
        self,
        issuer_node_id: str,
        target_service: str,
        allowed_actions: List[str],
        ttl_seconds: float = 3600.0,
        delegated_from: Optional[str] = None,
    ) -> DistributedCapabilityToken:
        """Issues an authoritative capability token scoped strictly to target_service and actions."""
        now = time.time()
        token_id = f"tok_g3_{uuid.uuid4().hex[:12]}"
        expires_at = now + ttl_seconds

        sig_payload = f"{token_id}:{issuer_node_id}:{target_service}:{sorted(allowed_actions)}:{expires_at}:{delegated_from}"
        sig = hmac.new(self._secret, sig_payload.encode("utf-8"), hashlib.sha256).hexdigest()

        tok = DistributedCapabilityToken(
            token_id=token_id,
            issuer_node_id=issuer_node_id,
            target_service=target_service,
            allowed_actions=tuple(allowed_actions),
            signature_hmac=sig,
            issued_at=now,
            expires_at=expires_at,
            delegated_from=delegated_from,
            attenuated_scope=tuple(allowed_actions),
        )
        self._tokens[token_id] = tok
        return tok

    def delegate_token(
        self,
        parent_token_id: str,
        sub_target_service: str,
        sub_actions: List[str],
        ttl_seconds: float = 600.0,
    ) -> DistributedCapabilityToken:
        """Delegates a token with strictly attenuated permissions (subset of parent)."""
        parent = self._tokens.get(parent_token_id)
        if not parent or not parent.is_valid() or parent_token_id in self._revoked_tokens:
            raise PermissionError(f"Cannot delegate from invalid or revoked token: {parent_token_id}")

        # Attenuation invariant: sub_actions must be subset of parent actions
        if "*" not in parent.allowed_actions:
            for act in sub_actions:
                if act not in parent.allowed_actions:
                    raise PermissionError(f"Privilege escalation denied: action '{act}' exceeds parent scope.")

        return self.issue_token(
            issuer_node_id=parent.target_service,
            target_service=sub_target_service,
            allowed_actions=sub_actions,
            ttl_seconds=min(ttl_seconds, parent.expires_at - time.time()),
            delegated_from=parent_token_id,
        )

    def verify_action(self, token_id: str, service: str, action: str) -> Tuple[bool, str]:
        """Validates capability token integrity, target service match, and action permission."""
        if token_id in self._revoked_tokens:
            return False, "Token has been revoked"

        tok = self._tokens.get(token_id)
        if not tok:
            return False, "Unknown token identifier"

        if not tok.is_valid():
            return False, "Token has expired"

        # Re-compute HMAC to verify against tampering
        sig_payload = f"{tok.token_id}:{tok.issuer_node_id}:{tok.target_service}:{sorted(tok.allowed_actions)}:{tok.expires_at}:{tok.delegated_from}"
        expected_sig = hmac.new(self._secret, sig_payload.encode("utf-8"), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(tok.signature_hmac, expected_sig):
            return False, "Cryptographic HMAC signature mismatch"

        if tok.target_service != "*" and tok.target_service != service:
            return False, f"Token scoped to '{tok.target_service}', cannot invoke '{service}'"

        if not tok.allows(action):
            return False, f"Action '{action}' not authorized in token scope"

        return True, "Authorized"

    def get_token(self, token_id: str) -> Optional[DistributedCapabilityToken]:
        """Retrieves a capability token by ID."""
        return self._tokens.get(token_id)

    def verify_token(self, token_id: str) -> bool:
        """Validates capability token integrity and expiration without action check."""
        if token_id in self._revoked_tokens:
            return False
        tok = self._tokens.get(token_id)
        if not tok or not tok.is_valid():
            return False
        sig_payload = f"{tok.token_id}:{tok.issuer_node_id}:{tok.target_service}:{sorted(tok.allowed_actions)}:{tok.expires_at}:{tok.delegated_from}"
        expected_sig = hmac.new(self._secret, sig_payload.encode("utf-8"), hashlib.sha256).hexdigest()
        return hmac.compare_digest(tok.signature_hmac, expected_sig)

    def revoke_token(self, token_id: str) -> None:
        self._revoked_tokens.add(token_id)
