"""Axioma Sentinel Terminal CLI Extremity [L1-G2-007 Kinetic Chaining].

Propagates the core AST semantic momentum into the terminal interface
without syntactic impedance mismatch. Provides rapid keyboard-driven control.
"""

from typing import List, Optional
import argparse
import json
import sys

from .core import SentinelCoreEngine
from .types import ActionStatus


def run_cli(args: Optional[List[str]] = None) -> int:
    """Executes Sentinel CLI commands."""
    parser = argparse.ArgumentParser(description="Axioma Sentinel Terminal Interface (G2 Kinetic Extremity)")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # 1. status
    subparsers.add_parser("status", help="Print real-time system state & metrics")

    # 2. dispatch
    dispatch_p = subparsers.add_parser("dispatch", help="Dispatch capability-scoped tool action")
    dispatch_p.add_argument("--tool", type=str, default="read_telemetry", help="Tool name")
    dispatch_p.add_argument("--key", type=str, default="cli_status", help="Target key")
    dispatch_p.add_argument("--val", type=str, default="ACTIVE", help="Target value")
    dispatch_p.add_argument("--token", type=str, default=None, help="Capability token ID")

    # 3. simulate-breach
    subparsers.add_parser("simulate-breach", help="Trigger 3-pass enclave auto-repair")

    # 4. rollback
    subparsers.add_parser("rollback", help="Execute 1-click functorial state rollback")

    # 5. tokens
    subparsers.add_parser("tokens", help="List active zero-trust capability tokens")

    parsed = parser.parse_args(args)
    if not parsed.command:
        parser.print_help()
        return 0

    engine = SentinelCoreEngine()

    if parsed.command == "status":
        summary = engine.get_system_summary()
        print("\n=================== AXIOMA SENTINEL STATUS ===================")
        print(f"System Status:      {summary['workspace_state'].get('system_status')}")
        print(f"State Hash:         {summary['state_hash'][:16]}...")
        print(f"Total Actions:      {summary['total_actions']}")
        print(f"Healed Incidents:   {summary['healed_incidents']}")
        print(f"Active Tokens:      {len(summary['tokens'])}")
        print(f"Landauer Erasure:   {summary['total_erased_bits']} bits ({summary['total_dissipated_joules']:.2e} Joules)")
        print("==============================================================\n")
        return 0

    elif parsed.command == "tokens":
        tokens = engine.capability_authority.export_tokens_summary()
        print("\n================ ACTIVE ZERO-TRUST TOKENS ================")
        for t in tokens:
            print(f"[{t['token_id']}] {t['persona']} (Expires: {t['expires_in_seconds']}s)")
            print(f"   Allowed: {', '.join(t['allowed_actions'])}")
            print(f"   Witness: {t['witness_signature']}")
        print("==========================================================\n")
        return 0

    elif parsed.command == "dispatch":
        tok_id = parsed.token
        if not tok_id:
            tokens = engine.capability_authority.export_tokens_summary()
            tok_id = tokens[0]["token_id"]

        action = engine.dispatch_agent_action(
            tool_name=parsed.tool,
            parameters={"target_key": parsed.key, "target_value": parsed.val},
            token_id=tok_id,
        )
        print(f"[+] Action Dispatched: {action.action_id} | Status: {action.status.value}")
        print(f"    Witness Hash: {action.witness_hash[:16]}...")
        print(f"    Dissipation: {action.erased_bits} bits ({action.dissipated_joules:.2e} J)")
        return 0

    elif parsed.command == "simulate-breach":
        tokens = engine.capability_authority.export_tokens_summary()
        architect_tok = next(t for t in tokens if t["persona"] == "AI_Architect")
        action = engine.dispatch_agent_action(
            tool_name="simulate_breach",
            parameters={"count": "100", "target_key": "cli_healed"},
            token_id=architect_tok["token_id"],
            simulate_fault=True,
        )
        print(f"[!] Invariant Breach Injected -> Enclave Auto-Repair Triggered [L1-G2-002]")
        print(f"    Status: {action.status.value}")
        for step in action.remediation_notes:
            print(f"    • {step}")
        return 0

    elif parsed.command == "rollback":
        res = engine.rollback_to_last_checkpoint()
        if res["success"]:
            print(f"[↺] State successfully rolled back to checkpoint: {res['restored_checkpoint_id']}")
            print(f"    Restored State Hash: {res['state_hash'][:16]}...")
        else:
            print(f"[!] Rollback failed: {res.get('message')}")
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(run_cli())
