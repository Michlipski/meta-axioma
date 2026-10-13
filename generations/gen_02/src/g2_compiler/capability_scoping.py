"""Introspectable Zero-Trust Capability Scoping [L1-G2-004].

Object-Capability (KeyKOS / seL4) Principle:
    Action(t) ⟹ Token(t) ∈ Scope(Persona) ∧ Witness(t) ≠ ⊥
    All external tool capabilities and autonomous actions must be demarked by granular,
    introspectable capability tokens with cryptographic audit witnesses.
    Unscoped or ambient execution authority is strictly prohibited.
"""

from typing import Any, Callable, Dict, List, Optional
import hashlib
import hmac
import time
import uuid

from g2_compiler.types import CapabilitySecurityFault, CapabilityToken


class CapabilityTokenManager:
    """Issues, scopes, and verifies cryptographic capability tokens for zero-trust tool access."""

    def __init__(self, signing_secret: Optional[str] = None):
        self._secret = (signing_secret or uuid.uuid4().hex).encode("utf-8")
        self._audit_witnesses: List[str] = []

    def issue_token(
        self,
        persona: str,
        allowed_actions: List[str],
        ttl_seconds: float = 3600.0,
    ) -> CapabilityToken:
        """Issues an introspectable capability token with cryptographic HMAC witness."""
        token_id = f"cap_{uuid.uuid4().hex[:12]}"
        now = time.time()
        expires = now + ttl_seconds
        nonce = uuid.uuid4().hex[:8]

        # Form message for cryptographic witness
        message = f"{token_id}|{persona}|{','.join(sorted(allowed_actions))}|{now}|{expires}|{nonce}"
        witness = hmac.new(self._secret, message.encode("utf-8"), hashlib.sha256).hexdigest()

        return CapabilityToken(
            token_id=token_id,
            persona=persona,
            allowed_actions=allowed_actions,
            issued_at=now,
            expires_at=expires,
            nonce=nonce,
            cryptographic_witness=witness,
        )

    def verify_token(self, token: CapabilityToken, requested_action: str) -> bool:
        """Verifies integrity, expiration, and action permission of a capability token."""
        now = time.time()
        if now > token.expires_at:
            return False

        if requested_action not in token.allowed_actions:
            return False

        # Re-compute witness
        message = (
            f"{token.token_id}|{token.persona}|"
            f"{','.join(sorted(token.allowed_actions))}|{token.issued_at}|{token.expires_at}|{token.nonce}"
        )
        expected_witness = hmac.new(self._secret, message.encode("utf-8"), hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected_witness, token.cryptographic_witness)

    def execute_scoped_tool(
        self,
        token: Optional[CapabilityToken],
        tool_action: str,
        tool_callable: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """Executes a tool under explicit capability token boundary.
        
        Rejects ambient or unscoped authority with CapabilitySecurityFault.
        """
        if token is None:
            raise CapabilitySecurityFault(
                f"Ambient execution rejected: Tool action '{tool_action}' invoked without CapabilityToken."
            )

        if not self.verify_token(token, tool_action):
            raise CapabilitySecurityFault(
                f"Capability violation: Token '{token.token_id}' for persona '{token.persona}' "
                f"not authorized or expired for action '{tool_action}'."
            )

        # Log cryptographic witness
        action_witness = hashlib.sha256(
            f"{token.token_id}:{tool_action}:{time.time()}".encode("utf-8")
        ).hexdigest()
        self._audit_witnesses.append(action_witness)

        return tool_callable(*args, **kwargs)

    def get_audit_witnesses(self) -> List[str]:
        """Returns log of all executed capability-scoped witnesses."""
        return list(self._audit_witnesses)
