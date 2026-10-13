#!/usr/bin/env python3
"""Axioma Fabric Command-Line Interface (CLI).

Terminal extremity for streaming production, consumption, cluster topology audits,
Landauer thermodynamic dissipation inspection, and chaos fault injection.
"""

from __future__ import annotations
import argparse
import asyncio
import json
import os
import sys
import time

# Ensure packages can be resolved
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from axioma_fabric.chaos import FabricChaosCrucible
from axioma_fabric.cocycle_auditor import FabricCocycleAuditor
from axioma_fabric.gateway import FabricGateway
from axioma_fabric.models import CapabilityToken
from axioma_fabric.sheaf_broker import FabricBrokerNode

SECRET_KEY_DEFAULT = "axioma_secret_dev_key_g2_2026"


def create_default_cluster(secret_key: str = SECRET_KEY_DEFAULT) -> list[FabricBrokerNode]:
    """Create a 3-node in-process broker cluster (Node α, Node β, Node γ)."""
    alpha = FabricBrokerNode("node_alpha", "U_alpha", secret_key)
    beta = FabricBrokerNode("node_beta", "U_beta", secret_key)
    gamma = FabricBrokerNode("node_gamma", "U_gamma", secret_key)

    alpha.register_peer(beta)
    alpha.register_peer(gamma)
    beta.register_peer(alpha)
    beta.register_peer(gamma)
    gamma.register_peer(alpha)
    gamma.register_peer(beta)

    return [alpha, beta, gamma]


def cmd_keygen(args: argparse.Namespace) -> None:
    token = CapabilityToken.create_signed(
        token_id=f"cap_{args.subject}_{int(time.time())}",
        subject=args.subject,
        allowed_topics=args.topics.split(","),
        permissions=args.permissions.split(","),
        ttl_seconds=args.ttl,
        secret_key=args.secret,
    )
    data = {
        "token_id": token.token_id,
        "subject": token.subject,
        "allowed_topics": token.allowed_topics,
        "permissions": token.permissions,
        "expires_at": token.expires_at,
        "signature": token.signature,
    }
    print(json.dumps(data, indent=2))


def cmd_produce(args: argparse.Namespace) -> None:
    cluster = create_default_cluster(args.secret)
    node_map = {n.node_id: n for n in cluster}
    node = node_map.get(args.node, cluster[0])

    # Build token
    token = CapabilityToken.create_signed(
        token_id="cli_producer_token",
        subject="cli_operator",
        allowed_topics=[args.topic],
        permissions=["produce"],
        ttl_seconds=3600,
        secret_key=args.secret,
    )

    try:
        payload = json.loads(args.payload)
    except Exception:
        payload = {"data": args.payload}

    ev = node.publish(args.topic, payload, token)
    print(f"Published event: {ev.event_id}")
    print(f"Vector clock: {ev.vector_clock.to_dict()}")
    print(f"Origin node: {ev.origin_node}")


def cmd_audit(args: argparse.Namespace) -> None:
    cluster = create_default_cluster(args.secret)
    auditor = FabricCocycleAuditor()
    witnesses = auditor.audit_cluster(cluster, args.topic, auto_reconcile=True)

    print(f"=== Pairwise Cocycle Audit for topic '{args.topic}' ===")
    for w in witnesses:
        status = "PASSED (Coherent)" if w.divergence_count == 0 else "DIVERGENT"
        print(f"- {w.node_i} <-> {w.node_j} [{w.subdomain_intersection}]: {status} (Agreed: {w.agreed_events_count}, Div: {w.divergence_count})")
        print(f"  Witness Hash: {w.witness_hash[:16]}...")


def cmd_serve(args: argparse.Namespace) -> None:
    cluster = create_default_cluster(args.secret)
    web_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "web"))
    gw = FabricGateway(cluster, args.secret, host=args.host, port=args.port, web_dir=web_dir)

    print(f"Starting Axioma Fabric Gateway on http://{args.host}:{args.port}")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(gw.start())
        print("Press Ctrl+C to stop.")
        loop.run_forever()
    except KeyboardInterrupt:
        print("\nShutting down gateway...")
        loop.run_until_complete(gw.stop())
    finally:
        loop.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Axioma Fabric CLI")
    parser.add_argument("--secret", default=SECRET_KEY_DEFAULT, help="HMAC secret key")
    subparsers = parser.add_subparsers(dest="command")

    # keygen
    p_key = subparsers.add_parser("keygen", help="Generate capability token")
    p_key.add_argument("--subject", default="operator")
    p_key.add_argument("--topics", default="*")
    p_key.add_argument("--permissions", default="produce,consume")
    p_key.add_argument("--ttl", type=float, default=3600.0)

    # produce
    p_prod = subparsers.add_parser("produce", help="Publish event")
    p_prod.add_argument("--topic", default="telemetry.sensors")
    p_prod.add_argument("--node", default="node_alpha")
    p_prod.add_argument("--payload", default='{"metric": "cpu", "value": 42}')

    # audit
    p_aud = subparsers.add_parser("audit", help="Run pairwise cocycle audit")
    p_aud.add_argument("--topic", default="telemetry.sensors")

    # serve
    p_srv = subparsers.add_parser("serve", help="Run AsyncIO Gateway server")
    p_srv.add_argument("--host", default="127.0.0.1")
    p_srv.add_argument("--port", type=int, default=8443)

    args = parser.parse_args()
    if args.command == "keygen":
        cmd_keygen(args)
    elif args.command == "produce":
        cmd_produce(args)
    elif args.command == "audit":
        cmd_audit(args)
    elif args.command == "serve":
        cmd_serve(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
