"""CLI and entrypoint for the Axiom Bootstrapper with Comparative Evaluation."""

from __future__ import annotations

import argparse
import asyncio
import sys
from typing import Optional

from meta_axioma.hitl.intercept import HitlController
from meta_axioma.loop import AxiomBootstrapper
from meta_axioma.telemetry.events import TelemetryEvent
from meta_axioma.types import (
    Axiom,
    AxiomLevel,
    AxiomStatus,
    EpochTelemetry,
    HitlAction,
    HitlVerdict,
    NegativeAxiom,
)


def format_telemetry_console(event: TelemetryEvent) -> None:
    """Pretty prints telemetry stream events to console."""
    ev_type = event.event_type.value
    p = event.payload

    if ev_type == "EPOCH_STARTED":
        print(f"\n{'='*75}")
        has_seed_str = " (Comparative Seed Active)" if p.get("has_user_seed") else ""
        print(f"▶ [EPOCH {event.epoch}] Starting Bootstrapping Cycle | Phase: {p.get('phase')}{has_seed_str}")
        print(f"  Inverse Compute Budget: Tokens={p.get('token_budget'):,} | Depth={p.get('simulation_depth')}")
        print(f"{'='*75}")

    elif ev_type == "CANDIDATE_GENERATED":
        cand = p.get("candidate", {})
        print(f"\n🤖 LLM Candidate Generated: [{cand.get('id')}] {cand.get('name')}")
        print(f"   Statement: {cand.get('statement')}")
        print(f"   Formal:    {cand.get('formal_expression')}")
        print(f"   Rule:      {cand.get('operational_rule')}")

    elif ev_type == "USER_SEED_SUBMITTED":
        seed = p.get("user_seed", {})
        print(f"\n👤 User Seed Injected:      [{seed.get('id')}] {seed.get('name')}")
        print(f"   Statement: {seed.get('statement')}")
        print(f"   Formal:    {seed.get('formal_expression')}")
        print(f"   Rule:      {seed.get('operational_rule')}")

    elif ev_type == "COMPARATIVE_EVALUATION_COMPLETED":
        leaderboard = p.get("leaderboard", [])
        if leaderboard:
            has_t4 = any(r.get("delta_e4", 0.0) != 0.0 for r in leaderboard)
            print(f"\n{'*'*78}")
            print(f"⚔️  TOURNAMENT EVALUATION (Pool Size: {p.get('pool_size', len(leaderboard))})")
            print(f"{'-'*78}")
            if has_t4:
                print(f"  {'ID':<10} {'Candidate Name':<20} {'Source':<9} {'ΔE1':>7} {'ΔE2':>7} {'ΔE3':>7} {'ΔE4':>7} {'Agg ΔE':>8}")
                print(f"  {'-'*76}")
                for r in leaderboard:
                    src_tag = "USER" if r.get("source") == "USER_SEED" else "LLM"
                    name_cut = (r.get("name")[:18] + "..") if len(r.get("name", "")) > 20 else r.get("name", "")
                    print(f"  {r['id']:<10} {name_cut:<20} {src_tag:<9} {r.get('delta_e1', 0.0):+7.4f} {r.get('delta_e2', 0.0):+7.4f} {r.get('delta_e3', 0.0):+7.4f} {r.get('delta_e4', 0.0):+7.4f} {r.get('aggregate_delta_e', 0.0):+8.4f}")
            else:
                print(f"  {'ID':<10} {'Candidate Name':<22} {'Source':<9} {'ΔE1':>7} {'ΔE2':>7} {'ΔE3':>7} {'Agg ΔE':>8}")
                print(f"  {'-'*68}")
                for r in leaderboard:
                    src_tag = "USER" if r.get("source") == "USER_SEED" else "LLM"
                    name_cut = (r.get("name")[:20] + "..") if len(r.get("name", "")) > 22 else r.get("name", "")
                    print(f"  {r['id']:<10} {name_cut:<22} {src_tag:<9} {r.get('delta_e1', 0.0):+7.4f} {r.get('delta_e2', 0.0):+7.4f} {r.get('delta_e3', 0.0):+7.4f} {r.get('aggregate_delta_e', 0.0):+8.4f}")
            print(f"{'-'*78}")
            print(f"  Winner: [{p.get('top_candidate_id')}] {p.get('top_candidate_name')} (ΔE = {p.get('top_aggregate_delta_e', 0.0):+.4f})")
            if p.get("user_aggregate_delta_e") is not None:
                usr_agg = p.get("user_aggregate_delta_e", 0.0)
                llm_agg = p.get("llm_aggregate_delta_e", 0.0)
                diff = p.get("delta_diff", 0.0)
                leader = "USER SEED" if diff > 0 else ("TIED" if diff == 0 else "LLM CANDIDATE")
                print(f"  User Seed ΔE: {usr_agg:+7.4f} | LLM Top ΔE: {llm_agg:+7.4f} | Leader: {leader}")
            print(f"{'*'*78}")

    elif ev_type == "EVALUATION_COMPLETED" and "delta_e1" in p:
        tier_str = p.get("tier", "STRUCTURAL")
        t1_label = "Search Diversity" if tier_str == "EPISTEMIC" else "Self-Constructor"
        t2_label = "Refutation Velocity" if tier_str == "EPISTEMIC" else "Self-Evaluator"
        t3_label = "Structural Yield" if tier_str == "EPISTEMIC" else "Control Group"

        print(f"\n📊 Tri-Fold Simulation Results ({tier_str}):")
        print(f"   ├─ Target 1 ({t1_label}): ΔE1 = {p.get('delta_e1'):+.4f}")
        print(f"   ├─ Target 2 ({t2_label}): ΔE2 = {p.get('delta_e2'):+.4f}")
        print(f"   ├─ Target 3 ({t3_label}): ΔE3 = {p.get('delta_e3'):+.4f}")
        print(f"   └─ Aggregate Efficacy Delta:        ΔE  = {p.get('aggregate_delta_e'):+.4f}")

    elif ev_type == "AXIOM_COMMITTED":
        print(f"✅ COMMITTED: Axiom [{p.get('axiom_id')}] (ΔE = {p.get('delta_e'):+.4f}) committed to active set.")

    elif ev_type == "AXIOM_REJECTED":
        print(f"❌ REJECTED: Candidate axiom did not meet criteria ({p.get('reason') or p.get('delta_e')}).")

    elif ev_type == "AXIOM_LOOKAHEAD_EVALUATED":
        rec = p.get("recommendation", "UNKNOWN")
        diff = p.get("net_lookahead_differential", 0.0)
        tokens = p.get("compute_dividend_tokens", 0)
        depth = p.get("compute_dividend_depth", 0)
        jb = p.get("jettison_branch", {})
        rb = p.get("retain_branch", {})
        print(f"\n🔮 AXIOM LOOKAHEAD EVALUATION (Horizon H={p.get('lookahead_horizon', 2)}):")
        print(f"   ├─ Recommendation:            {rec} (Confidence: {int(p.get('confidence_score', 0)*100)}%)")
        print(f"   ├─ Net Differential Λ(H):     {diff:+.4f} (Branch A vs Branch B)")
        print(f"   ├─ Speculative Compute Gain:  +{tokens:,} tokens, +{depth} depth levels")
        print(f"   ├─ Branch A (Speculative Jettison): Proj ΔE = {jb.get('projected_cumulative_delta', 0.0):+.4f} (Active n={jb.get('active_axiom_count')}, T={jb.get('tokens'):,})")
        print(f"   └─ Branch B (Retain Scaffolding):   Proj ΔE = {rb.get('projected_cumulative_delta', 0.0):+.4f} (Active n={rb.get('active_axiom_count')}, T={rb.get('tokens'):,})")

    elif ev_type == "PHASE_TRANSITION_JETTISON":
        print(f"\n⚡ [PHASE TRANSITION] The Jettison triggered! Deactivated Level 0 axioms: {p.get('deactivated_ids') or p.get('pruned_ids')}")
        print(f"   (Retained as INACTIVE scaffolding in memory and dashboard. Engine transitioned to PHASE_2_STRUCTURAL_EXECUTION.)")

    elif ev_type == "EPOCH_COMPLETED":
        tel = p.get("telemetry", {})
        print(f"\n🏁 Epoch {event.epoch} Complete. Global Efficacy: {tel.get('current_efficacy', 0.0):.4f} | Total Active: {tel.get('total_active')}")


async def interactive_hitl_callback(telemetry: EpochTelemetry) -> HitlVerdict:
    """Interactive command-line HITL interrupt supporting single or comparative decisions."""
    llm_c = telemetry.candidate_axiom
    user_c = telemetry.user_candidate
    llm_m = telemetry.tri_fold_metrics
    user_m = telemetry.user_metrics

    print(f"\n{'*'*75}")
    print(f"🚨 [HITL INTERRUPT] Epoch {telemetry.epoch} Boundary Reached")
    print(f"{'*'*75}")

    # Comparative mode prompt
    if user_c is not None and user_m is not None and llm_m is not None:
        diff = round(user_m.aggregate_delta_e - llm_m.aggregate_delta_e, 4)
        print(f"Tournament Summary:")
        print(f"  • LLM Candidate:  [{llm_c.id if llm_c else '-'}] {llm_c.name if llm_c else ''} (ΔE = {llm_m.aggregate_delta_e:+.4f})")
        print(f"  • User Seed:       [{user_c.id}] {user_c.name} (ΔE = {user_m.aggregate_delta_e:+.4f})")
        print(f"  • Relative Delta:  User Seed is {diff:+.4f} ΔE relative to LLM")
        print(f"\nDecisions:")
        print(f"  [1] Commit User Seed (APPROVE_USER)")
        print(f"  [2] Commit LLM Candidate (APPROVE_LLM)")
        print(f"  [3] Commit Both (APPROVE_BOTH)")
        print(f"  [4] Reject Both")
        print(f"  [v] Veto (Inject Negative Axiom Invariant)")
        print(f"  [j] Force The Jettison")

        if not sys.stdin.isatty():
            # In non-interactive mode with user seed, prefer the winner
            preferred = HitlAction.APPROVE_USER if diff >= 0 else HitlAction.APPROVE_LLM
            return HitlVerdict(action=preferred, feedback="Auto-approved tournament leader")

        loop = asyncio.get_running_loop()
        choice = await loop.run_in_executor(None, lambda: input("Enter decision [1/2/3/4/v/j] (default 1): ").strip().lower())

        if choice == "2":
            return HitlVerdict(action=HitlAction.APPROVE_LLM, feedback="Human selected LLM candidate")
        elif choice == "3":
            return HitlVerdict(action=HitlAction.APPROVE_BOTH, feedback="Human committed both candidates")
        elif choice == "4":
            return HitlVerdict(action=HitlAction.REJECT_BOTH, feedback="Human rejected both candidates")
        elif choice == "v":
            pattern = await loop.run_in_executor(None, lambda: input("Forbidden pattern keyword/phrase: ").strip())
            rationale = await loop.run_in_executor(None, lambda: input("Rationale for negative invariant: ").strip())
            neg = NegativeAxiom(
                id=f"NEG-{telemetry.epoch:03d}",
                name=f"Veto Invariant Epoch {telemetry.epoch}",
                forbidden_pattern=pattern,
                rationale=rationale,
                injected_at_epoch=telemetry.epoch,
            )
            return HitlVerdict(
                action=HitlAction.INJECT_NEGATIVE_AXIOM,
                feedback=f"Vetoed with forbidden pattern: {pattern}",
                negative_axiom=neg,
            )
        elif choice == "j":
            return HitlVerdict(action=HitlAction.FORCE_JETTISON, feedback="Human forced phase transition jettison")

        return HitlVerdict(action=HitlAction.APPROVE_USER, feedback="Human selected User seed")

    # Standard single candidate prompt
    cand = llm_c
    agg = llm_m.aggregate_delta_e if llm_m else 0.0
    print(f"Candidate: [{cand.id if cand else 'None'}] {cand.name if cand else ''}")
    print(f"Simulated ΔE: {agg:+.4f} across Tri-Fold Targets.")
    print(f"Options: [A]pprove | [R]eject | [V]eto (Inject Negative Axiom) | [J]ettison")

    if not sys.stdin.isatty():
        return HitlVerdict(action=HitlAction.APPROVE, feedback="Auto-approved in non-interactive mode")

    loop = asyncio.get_running_loop()
    choice = await loop.run_in_executor(None, lambda: input("Enter decision [A/r/v/j] (default A): ").strip().lower())

    if choice == "r":
        reason = await loop.run_in_executor(None, lambda: input("Rejection reason: ").strip())
        return HitlVerdict(action=HitlAction.REJECT, feedback=reason or "Human rejected")
    elif choice == "v":
        pattern = await loop.run_in_executor(None, lambda: input("Forbidden pattern keyword/phrase: ").strip())
        rationale = await loop.run_in_executor(None, lambda: input("Rationale for negative invariant: ").strip())
        neg = NegativeAxiom(
            id=f"NEG-{telemetry.epoch:03d}",
            name=f"Veto Invariant Epoch {telemetry.epoch}",
            forbidden_pattern=pattern,
            rationale=rationale,
            injected_at_epoch=telemetry.epoch,
        )
        return HitlVerdict(
            action=HitlAction.INJECT_NEGATIVE_AXIOM,
            feedback=f"Vetoed with forbidden pattern: {pattern}",
            negative_axiom=neg,
        )
    elif choice == "j":
        return HitlVerdict(action=HitlAction.FORCE_JETTISON, feedback="Human forced phase transition jettison")

    return HitlVerdict(action=HitlAction.APPROVE, feedback="Human approved")


async def async_main() -> None:
    parser = argparse.ArgumentParser(description="Meta-Axioma: Axiom Bootstrapper")
    parser.add_argument("--epochs", type=int, default=1, help="Number of epochs to run")
    parser.add_argument("--interactive", action="store_true", help="Enable interactive HITL prompts")
    parser.add_argument("--status", action="store_true", help="Print current status and exit")

    # CLI flags for user seed
    parser.add_argument("--seed-name", type=str, default=None, help="Name of human seed axiom")
    parser.add_argument("--seed-statement", type=str, default=None, help="Statement of human seed axiom")
    parser.add_argument("--seed-level", type=str, default="1", choices=["0", "1"], help="Axiom level (0=Epistemic, 1=Structural)")
    parser.add_argument("--seed-formal", type=str, default="", help="Formal mathematical expression")
    parser.add_argument("--seed-rule", type=str, default="", help="Operational compiler rule")

    args = parser.parse_args()

    hitl = HitlController()
    if args.interactive:
        hitl.set_callback(interactive_hitl_callback)

    bootstrapper = AxiomBootstrapper(hitl_controller=hitl)
    bootstrapper.telemetry.subscribe_sync(format_telemetry_console)

    if args.status:
        print("\n=== Meta-Axioma Current Status ===")
        print(f"Current Epoch: {bootstrapper.current_epoch}")
        print(f"Phase:         {bootstrapper.engine.phase.value}")
        print(f"Efficacy:      {bootstrapper.global_efficacy:.4f}")
        print(f"Active Axioms: {bootstrapper.engine.count_active()}")
        print(f"  Level 0 (Epistemic):  {len(bootstrapper.engine.level_0_epistemic)}")
        print(f"  Level 1 (Structural): {len(bootstrapper.engine.level_1_structural)}")
        print(f"  Negative Axioms:     {len(bootstrapper.engine.active_negative_axioms)}")
        for ax in bootstrapper.engine.active_axioms:
            print(f"  - [{ax.id}] ({ax.level.value}) {ax.name}")
        return

    # Check CLI user seed
    cli_user_seed: Optional[Axiom] = None
    if args.seed_name and args.seed_statement:
        level_enum = AxiomLevel.LEVEL_0_EPISTEMIC if args.seed_level == "0" else AxiomLevel.LEVEL_1_STRUCTURAL
        prefix = "L0-SEED" if level_enum == AxiomLevel.LEVEL_0_EPISTEMIC else "L1-SEED"
        cli_user_seed = Axiom(
            id=f"{prefix}-{bootstrapper.current_epoch + 1:03d}",
            level=level_enum,
            name=args.seed_name,
            statement=args.seed_statement,
            formal_expression=args.seed_formal or r"\mathcal{S}_{\text{user}} \implies \text{True}",
            operational_rule=args.seed_rule or "Enforce human-seeded invariant.",
            status=AxiomStatus.CANDIDATE,
        )

    print(f"\n🚀 Launching Axiom Bootstrapper (Target Epochs: {args.epochs})")

    for i in range(args.epochs):
        epoch_num = bootstrapper.current_epoch + 1
        user_seed_for_epoch = cli_user_seed

        # In interactive mode, prompt if operator wants to input a seed for this epoch
        if args.interactive and sys.stdin.isatty() and not cli_user_seed:
            prompt_input = input(f"\n[Epoch {epoch_num}] Do you want to submit a User Seed Axiom to compete with the LLM? [y/N]: ").strip().lower()
            if prompt_input == "y":
                lvl_choice = input("  Axiom Level [0=Epistemic, 1=Structural] (default 1): ").strip()
                lvl = AxiomLevel.LEVEL_0_EPISTEMIC if lvl_choice == "0" else AxiomLevel.LEVEL_1_STRUCTURAL
                name = input("  Axiom Name: ").strip()
                stmt = input("  Axiom Statement: ").strip()
                formal = input("  Formal Expression (optional): ").strip()
                rule = input("  Operational Rule (optional): ").strip()

                prefix = "L0-USER" if lvl == AxiomLevel.LEVEL_0_EPISTEMIC else "L1-USER"
                user_seed_for_epoch = Axiom(
                    id=f"{prefix}-{epoch_num:03d}",
                    level=lvl,
                    name=name or f"User Seed {epoch_num}",
                    statement=stmt or "Custom user structural invariant",
                    formal_expression=formal or r"\mathcal{S}_{\text{custom}}",
                    operational_rule=rule or "Enforce operator invariant",
                    status=AxiomStatus.CANDIDATE,
                )

        await bootstrapper.step_epoch(user_seed=user_seed_for_epoch)


def main() -> None:
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
