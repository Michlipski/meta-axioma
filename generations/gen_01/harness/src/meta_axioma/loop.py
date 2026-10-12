"""The Bootstrapping Core Loop: recursive generation, simulation, evaluation, and HITL."""

from __future__ import annotations

import datetime
from typing import Any, Dict, List, Optional, Tuple

from meta_axioma.config import SystemConfig
from meta_axioma.engine.engine import TwoTieredAxiomEngine
from meta_axioma.engine.generator import AxiomPromptGenerator
from meta_axioma.evaluator.evaluator import EfficacyEvaluator
from meta_axioma.hitl.intercept import HitlController
from meta_axioma.memory import PersistentMemoryManager
from meta_axioma.reports import EpochReportGenerator
from meta_axioma.simulation.decay import ComputeDecayManager
from meta_axioma.simulation.lookahead import AxiomLookaheadEngine, AxiomLookaheadResult
from meta_axioma.simulation.sandbox import SimulationSandbox
from meta_axioma.telemetry.events import EventType, TelemetryEvent
from meta_axioma.telemetry.router import TelemetryRouter
from meta_axioma.types import (
    Axiom,
    AxiomLevel,
    ComputeBudget,
    EpochTelemetry,
    HitlAction,
    PhaseState,
    TriFoldMetrics,
)


class AxiomBootstrapper:
    """Core compiler and recursive bootstrapping loop for self-constructing architecture."""

    def __init__(
        self,
        config: Optional[SystemConfig] = None,
        hitl_controller: Optional[HitlController] = None,
        telemetry_router: Optional[TelemetryRouter] = None,
    ):
        self.config = config or SystemConfig()
        self.memory = PersistentMemoryManager(
            axioms_path=self.config.axioms_path,
            architecture_path=self.config.architecture_path,
        )
        self.hitl = hitl_controller or HitlController()
        self.telemetry = telemetry_router or TelemetryRouter()

        # Engine components
        self.decay_manager = ComputeDecayManager(self.config)
        self.lookahead_engine = AxiomLookaheadEngine(self.config)
        self.sandbox = SimulationSandbox()
        self.evaluator = EfficacyEvaluator(self.config)
        self.evaluator.delta_history = self.memory.load_trajectory_history()
        self.generator = AxiomPromptGenerator()
        self.reporter = EpochReportGenerator(reports_dir=self.config.reports_dir)

        # State initialization from persistent memory
        self.current_epoch, self.current_phase, self.global_efficacy = (
            self.memory.load_architecture_state()
        )
        axioms, negative_axioms = self.memory.load_axioms()
        self.engine = TwoTieredAxiomEngine(
            axioms=axioms,
            negative_axioms=negative_axioms,
            initial_phase=self.current_phase,
        )
        if self.current_phase == PhaseState.PHASE_2_STRUCTURAL_EXECUTION:
            self.sandbox.jettison_epistemic_targets()

    def load_persistent_context(self) -> None:
        """Reloads context from AXIOMS.md and ARCHITECTURE.md."""
        self.current_epoch, self.current_phase, self.global_efficacy = (
            self.memory.load_architecture_state()
        )
        self.evaluator.delta_history = self.memory.load_trajectory_history()
        axioms, negative_axioms = self.memory.load_axioms()
        self.engine = TwoTieredAxiomEngine(
            axioms=axioms,
            negative_axioms=negative_axioms,
            initial_phase=self.current_phase,
        )

    async def step_epoch(self, user_seed: Optional[Axiom] = None) -> EpochTelemetry:
        """Executes a single recursive bootstrapping epoch.
        
        Supports comparative evaluation when user_seed is provided, allowing
        head-to-head comparison between human-seeded axioms and LLM-generated axioms.
        """
        self.current_epoch += 1
        epoch = self.current_epoch

        # 1. Compute Decay allocation
        active_count = self.engine.count_active()
        budget = self.decay_manager.calculate_budget(active_count)

        await self.telemetry.emit(
            TelemetryEvent(
                event_type=EventType.EPOCH_STARTED,
                epoch=epoch,
                payload={
                    "phase": self.engine.phase.value,
                    "active_axioms": active_count,
                    "token_budget": budget.token_budget,
                    "simulation_depth": budget.simulation_depth,
                    "has_user_seed": user_seed is not None,
                },
            )
        )

        # 2. Candidate Batch Generation (Multi-Candidate Tournament Mode)
        batch_size = self.config.candidate_pool_size
        llm_candidates = self.generator.generate_candidate_batch(
            count=batch_size,
            epoch=epoch,
            phase=self.engine.phase,
            level_0_axioms=self.engine.level_0_epistemic,
            level_1_axioms=self.engine.level_1_structural,
            negative_axioms=self.engine.active_negative_axioms,
            known_axiom_ids=set(self.engine.axioms.keys()),
            epistemic_scaffolding=self.engine.all_level_0_axioms,
        )

        for cand in llm_candidates:
            await self.telemetry.emit(
                TelemetryEvent(
                    event_type=EventType.CANDIDATE_GENERATED,
                    epoch=epoch,
                    payload={"candidate": cand.to_dict()},
                )
            )

        # 3. Assemble Tournament Pool (LLM Candidates + optional User Seed)
        tournament_pool: List[Tuple[Axiom, str]] = [(c, "LLM") for c in llm_candidates]
        if user_seed is not None:
            user_seed.origin_epoch = epoch
            tournament_pool.append((user_seed, "USER_SEED"))
            await self.telemetry.emit(
                TelemetryEvent(
                    event_type=EventType.USER_SEED_SUBMITTED,
                    epoch=epoch,
                    payload={"user_seed": user_seed.to_dict()},
                )
            )

        # 4. Multi-Candidate Target Sandbox Simulation
        metrics_by_id: Dict[str, TriFoldMetrics] = {}
        eval_records: List[Dict[str, Any]] = []

        for candidate, source in tournament_pool:
            is_clean, violation = self.engine.check_negative_invariants(candidate)
            if not is_clean:
                cand_metrics = TriFoldMetrics(
                    delta_e1=-0.1, delta_e2=-0.1, delta_e3=-0.1, aggregate_delta_e=-0.1,
                    target_details={"violation": violation},
                )
            else:
                sim_results = self.sandbox.run_simulation(
                    candidate=candidate,
                    active_axioms=self.engine.active_axioms,
                    negative_axioms=self.engine.active_negative_axioms,
                    budget=budget,
                )
                cand_metrics = self.evaluator.evaluate_simulation(
                    candidate=candidate,
                    simulation_results=sim_results,
                )

            metrics_by_id[candidate.id] = cand_metrics
            eval_records.append({
                "candidate": candidate,
                "candidate_dict": candidate.to_dict(),
                "id": candidate.id,
                "name": candidate.name,
                "level": candidate.level.value,
                "statement": candidate.statement,
                "formal_expression": candidate.formal_expression,
                "operational_rule": candidate.operational_rule,
                "source": source,
                "domain": candidate.metadata.get("exogenous_domain", "Epistemic Foundations" if candidate.level == AxiomLevel.LEVEL_0_EPISTEMIC else "Structural Systems"),
                "principle": candidate.metadata.get("source_principle", ""),
                "metrics": cand_metrics,
                "delta_e1": cand_metrics.delta_e1,
                "delta_e2": cand_metrics.delta_e2,
                "delta_e3": cand_metrics.delta_e3,
                "delta_e4": cand_metrics.delta_e4,
                "aggregate_delta_e": cand_metrics.aggregate_delta_e,
                "is_clean": is_clean,
                "violation": violation,
                "is_strictly_improving": self.evaluator.is_strictly_improving(cand_metrics),
                "system_profile": candidate.metadata.get("system_profile", {}),
            })

        # Rank all tournament candidates by aggregate_delta_e descending
        eval_records.sort(key=lambda x: x["aggregate_delta_e"], reverse=True)
        leaderboard_summary = [
            {
                "id": r["id"],
                "name": r["name"],
                "level": r["level"],
                "statement": r["statement"],
                "formal_expression": r["formal_expression"],
                "operational_rule": r["operational_rule"],
                "source": r["source"],
                "domain": r["domain"],
                "principle": r["principle"],
                "delta_e1": r["delta_e1"],
                "delta_e2": r["delta_e2"],
                "delta_e3": r["delta_e3"],
                "delta_e4": r.get("delta_e4", 0.0),
                "aggregate_delta_e": r["aggregate_delta_e"],
                "is_strictly_improving": r["is_strictly_improving"],
                "is_clean": r["is_clean"],
                "system_profile": r["system_profile"],
            }

            for r in eval_records
        ]

        # Primary LLM candidate (highest-performing LLM candidate)
        top_llm_record = next((r for r in eval_records if r["source"] == "LLM"), eval_records[0])
        llm_candidate = top_llm_record["candidate"]
        llm_metrics = top_llm_record["metrics"]

        # User seed (if present)
        user_record = next((r for r in eval_records if r["source"] == "USER_SEED"), None)
        user_metrics = user_record["metrics"] if user_record else None

        # Comparative summary
        comparative_summary = {
            "pool_size": len(tournament_pool),
            "top_candidate_id": eval_records[0]["id"],
            "top_candidate_name": eval_records[0]["name"],
            "top_aggregate_delta_e": eval_records[0]["aggregate_delta_e"],
            "runner_up_id": eval_records[1]["id"] if len(eval_records) > 1 else None,
            "runner_up_delta_e": eval_records[1]["aggregate_delta_e"] if len(eval_records) > 1 else None,
            "delta_diff": round(eval_records[0]["aggregate_delta_e"] - (eval_records[1]["aggregate_delta_e"] if len(eval_records) > 1 else 0.0), 4),
            "leaderboard": leaderboard_summary,
        }
        if user_seed is not None and user_metrics:
            comparative_summary.update({
                "llm_aggregate_delta_e": llm_metrics.aggregate_delta_e,
                "user_aggregate_delta_e": user_metrics.aggregate_delta_e,
                "user_won": user_metrics.aggregate_delta_e > llm_metrics.aggregate_delta_e,
            })

        await self.telemetry.emit(
            TelemetryEvent(
                event_type=EventType.COMPARATIVE_EVALUATION_COMPLETED,
                epoch=epoch,
                payload=comparative_summary,
            )
        )

        # 4b. Speculative Axiom Lookahead Analysis (evaluating whether to jettison)
        lookahead_result: Optional[AxiomLookaheadResult] = None
        if (
            self.engine.phase == PhaseState.PHASE_1_META_EXPLORATION
            and len(self.engine.level_0_epistemic) >= self.config.min_epistemic_axioms
        ):
            upcoming_structural = self.generator.generate_candidate_batch(
                count=3,
                epoch=epoch + 1,
                phase=PhaseState.PHASE_2_STRUCTURAL_EXECUTION,
                level_0_axioms=[],
                level_1_axioms=self.engine.level_1_structural,
                negative_axioms=self.engine.active_negative_axioms,
                known_axiom_ids=set(self.engine.axioms.keys()) | {c.id for c, _ in tournament_pool},
                epistemic_scaffolding=self.engine.all_level_0_axioms,
            )
            lookahead_result = self.lookahead_engine.evaluate_lookahead(
                current_epoch=epoch,
                active_axioms=self.engine.active_axioms,
                candidate_pool=upcoming_structural,
                negative_axioms=self.engine.active_negative_axioms,
                horizon=2,
            )
            await self.telemetry.emit(
                TelemetryEvent(
                    event_type=EventType.AXIOM_LOOKAHEAD_EVALUATED,
                    epoch=epoch,
                    payload=lookahead_result.to_dict(),
                )
            )

        # 5. Asynchronous HITL Interrupt Snapshot
        epoch_telemetry_snapshot = EpochTelemetry(
            epoch=epoch,
            phase=self.engine.phase,
            active_l0_count=len(self.engine.level_0_epistemic),
            active_l1_count=len(self.engine.level_1_structural),
            total_active=self.engine.count_active(),
            current_efficacy=self.global_efficacy,
            efficacy_derivative=self.evaluator.compute_efficacy_derivative(),
            compute_budget=budget,
            candidate_axiom=llm_candidate,
            tri_fold_metrics=llm_metrics,
            user_candidate=user_seed,
            user_metrics=user_metrics,
            comparative_summary=comparative_summary,
            candidate_pool=[c for c, _ in tournament_pool],
            tournament_leaderboard=leaderboard_summary,
            decision="PENDING_HITL",
            lookahead_analysis=lookahead_result.to_dict() if lookahead_result else None,
            timestamp=datetime.datetime.now().isoformat(),
        )

        await self.telemetry.emit(
            TelemetryEvent(
                event_type=EventType.HITL_INTERRUPT_TRIGGERED,
                epoch=epoch,
                payload={"telemetry": epoch_telemetry_snapshot.__dict__},
            )
        )

        hitl_verdict = await self.hitl.interrupt(epoch_telemetry_snapshot)

        await self.telemetry.emit(
            TelemetryEvent(
                event_type=EventType.HITL_RESPONSE_RECEIVED,
                epoch=epoch,
                payload={
                    "action": hitl_verdict.action.value,
                    "feedback": hitl_verdict.feedback,
                },
            )
        )

        # 6. Commit / Reject Resolution
        decision_label = ""
        effective_delta_e = 0.0
        jettison_occurred = False
        winning_axiom: Optional[Axiom] = None
        winning_metrics: Optional[TriFoldMetrics] = None

        if hitl_verdict.action == HitlAction.INJECT_NEGATIVE_AXIOM:
            if hitl_verdict.negative_axiom:
                self.engine.inject_negative_axiom(hitl_verdict.negative_axiom)
            for r in eval_records:
                self.engine.veto_axiom(
                    axiom=r["candidate"],
                    epoch=epoch,
                    reason=f"Human Veto: {hitl_verdict.feedback}",
                )
            decision_label = "Vetoed (Negative Axiom Injected)"

        elif hitl_verdict.action in (HitlAction.REJECT, HitlAction.REJECT_BOTH):
            for r in eval_records:
                self.engine.reject_axiom(
                    axiom=r["candidate"],
                    epoch=epoch,
                    delta_e=r["aggregate_delta_e"],
                    reason=f"HITL Reject: {hitl_verdict.feedback}",
                )
            decision_label = "Rejected by HITL"

        elif hitl_verdict.action == HitlAction.APPROVE_USER:
            # Explicitly commit User seed candidate
            if user_metrics and self.evaluator.is_strictly_improving(user_metrics):
                self.engine.commit_axiom(
                    axiom=user_seed,
                    epoch=epoch,
                    delta_e=user_metrics.aggregate_delta_e,
                )
                self.global_efficacy += user_metrics.aggregate_delta_e
                effective_delta_e = user_metrics.aggregate_delta_e
                winning_axiom = user_seed
                winning_metrics = user_metrics
                decision_label = f"Committed User Seed [{user_seed.id}] (+{user_metrics.aggregate_delta_e:.4f})"
                for r in eval_records:
                    if r["candidate"].id != user_seed.id:
                        self.engine.reject_axiom(
                            axiom=r["candidate"],
                            epoch=epoch,
                            delta_e=r["aggregate_delta_e"],
                            reason="User seed chosen over tournament candidates",
                        )
            else:
                self.engine.reject_axiom(
                    axiom=user_seed,
                    epoch=epoch,
                    delta_e=user_metrics.aggregate_delta_e if user_metrics else -0.1,
                    reason="User candidate ΔE <= 0 threshold failed",
                )
                decision_label = "User Seed Rejected (ΔE <= 0)"

        elif hitl_verdict.action == HitlAction.APPROVE_SELECTED and hitl_verdict.selected_candidate_id:
            # Commit a specific selected candidate by ID
            selected_rec = next((r for r in eval_records if r["id"] == hitl_verdict.selected_candidate_id), None)
            if selected_rec and self.evaluator.is_strictly_improving(selected_rec["metrics"]):
                winner = selected_rec["candidate"]
                w_metrics = selected_rec["metrics"]
                self.engine.commit_axiom(axiom=winner, epoch=epoch, delta_e=w_metrics.aggregate_delta_e)
                self.global_efficacy += w_metrics.aggregate_delta_e
                effective_delta_e = w_metrics.aggregate_delta_e
                winning_axiom = winner
                winning_metrics = w_metrics
                decision_label = f"Committed Selected [{winner.id}] (+{w_metrics.aggregate_delta_e:.4f})"
                for r in eval_records:
                    if r["candidate"].id != winner.id:
                        self.engine.reject_axiom(
                            axiom=r["candidate"],
                            epoch=epoch,
                            delta_e=r["aggregate_delta_e"],
                            reason=f"Alternative [{winner.id}] chosen by supervisor",
                        )
            else:
                decision_label = "Selected Candidate Rejected (ΔE <= 0)"

        elif hitl_verdict.action == HitlAction.APPROVE_BOTH and user_seed is not None and user_metrics:
            user_ok = self.evaluator.is_strictly_improving(user_metrics)
            llm_ok = self.evaluator.is_strictly_improving(llm_metrics)
            if user_ok and llm_ok:
                self.engine.commit_axiom(axiom=user_seed, epoch=epoch, delta_e=user_metrics.aggregate_delta_e)
                self.engine.commit_axiom(axiom=llm_candidate, epoch=epoch, delta_e=llm_metrics.aggregate_delta_e)
                both_delta = user_metrics.aggregate_delta_e + llm_metrics.aggregate_delta_e
                self.global_efficacy += both_delta
                effective_delta_e = both_delta
                winning_axiom = user_seed
                winning_metrics = user_metrics
                decision_label = f"Committed Both [{user_seed.id}, {llm_candidate.id}] (+{both_delta:.4f})"
            elif user_ok:
                self.engine.commit_axiom(axiom=user_seed, epoch=epoch, delta_e=user_metrics.aggregate_delta_e)
                self.global_efficacy += user_metrics.aggregate_delta_e
                effective_delta_e = user_metrics.aggregate_delta_e
                winning_axiom = user_seed
                winning_metrics = user_metrics
                decision_label = f"Committed User Seed Only (+{user_metrics.aggregate_delta_e:.4f})"
            elif llm_ok:
                self.engine.commit_axiom(axiom=llm_candidate, epoch=epoch, delta_e=llm_metrics.aggregate_delta_e)
                self.global_efficacy += llm_metrics.aggregate_delta_e
                effective_delta_e = llm_metrics.aggregate_delta_e
                winning_axiom = llm_candidate
                winning_metrics = llm_metrics
                decision_label = f"Committed LLM Candidate Only (+{llm_metrics.aggregate_delta_e:.4f})"
            else:
                decision_label = "Both Candidates Rejected (ΔE <= 0)"

        else:
            # Default: Commit the tournament winner with highest ΔE > 0
            winner_rec = eval_records[0]
            if self.evaluator.is_strictly_improving(winner_rec["metrics"]):
                winner = winner_rec["candidate"]
                w_metrics = winner_rec["metrics"]
                self.engine.commit_axiom(axiom=winner, epoch=epoch, delta_e=w_metrics.aggregate_delta_e)
                self.global_efficacy += w_metrics.aggregate_delta_e
                effective_delta_e = w_metrics.aggregate_delta_e
                winning_axiom = winner
                winning_metrics = w_metrics

                if winner_rec["source"] == "USER_SEED":
                    decision_label = f"Committed User Seed [{winner.id}] (+{w_metrics.aggregate_delta_e:.4f})"
                else:
                    decision_label = f"Committed Tournament Winner [{winner.id}] (+{w_metrics.aggregate_delta_e:.4f})"

                for r in eval_records[1:]:
                    self.engine.reject_axiom(
                        axiom=r["candidate"],
                        epoch=epoch,
                        delta_e=r["aggregate_delta_e"],
                        reason=f"Outperformed by [{winner.id}] in Epoch {epoch} tournament",
                    )
            else:
                for r in eval_records:
                    self.engine.reject_axiom(
                        axiom=r["candidate"],
                        epoch=epoch,
                        delta_e=r["aggregate_delta_e"],
                        reason="ΔE <= 0 strict threshold failed",
                    )
                decision_label = "All Tournament Candidates Rejected (ΔE <= 0)"

            # Check if HITL forced a jettison
            if hitl_verdict.action == HitlAction.FORCE_JETTISON:
                deactivated = self.engine.execute_jettison(epoch)
                self.sandbox.jettison_epistemic_targets()
                jettison_occurred = True
                decision_label += f" [Forced Jettison: Deactivated {len(deactivated)} L0 Epistemic Axioms (Retained as INACTIVE Scaffolding)]"

        # 7. Record rolling delta and check for Phase Transition (The Jettison)
        self.evaluator.record_epoch_delta(effective_delta_e)
        derivative = self.evaluator.compute_efficacy_derivative()
        lookahead_diff = lookahead_result.net_lookahead_differential if lookahead_result else None

        if (
            not jettison_occurred
            and self.engine.phase == PhaseState.PHASE_1_META_EXPLORATION
            and self.evaluator.should_trigger_jettison(
                epoch,
                active_l0_count=len(self.engine.level_0_epistemic),
                lookahead_differential=lookahead_diff,
            )
        ):
            deactivated_ids = self.engine.execute_jettison(epoch)
            self.sandbox.jettison_epistemic_targets()
            jettison_occurred = True
            decision_label += f" [Jettison Triggered: Deactivated {len(deactivated_ids)} L0 Epistemic Axioms (Retained as INACTIVE Scaffolding) & Epistemic Targets]"
            await self.telemetry.emit(
                TelemetryEvent(
                    event_type=EventType.PHASE_TRANSITION_JETTISON,
                    epoch=epoch,
                    payload={
                        "pruned_ids": deactivated_ids,
                        "deactivated_ids": deactivated_ids,
                        "derivative": derivative,
                        "lookahead_differential": lookahead_diff,
                    },
                )
            )

        # 8. Sync persistent memory markdown files (AXIOMS.md & ARCHITECTURE.md)
        chosen_metrics = winning_metrics or llm_metrics

        self.memory.sync_axioms_file(
            axioms=list(self.engine.axioms.values()),
            negative_axioms=list(self.engine.negative_axioms.values()),
            phase=self.engine.phase,
            lifecycle_logs=self.engine.lifecycle_logs,
        )
        self.memory.record_epoch_architecture(
            epoch=epoch,
            phase=self.engine.phase,
            global_efficacy=self.global_efficacy,
            efficacy_derivative=derivative,
            active_count=self.engine.count_active(),
            compute_tokens=budget.token_budget,
            metrics=chosen_metrics,
            status_action=decision_label,
        )

        completed_telemetry = EpochTelemetry(
            epoch=epoch,
            phase=self.engine.phase,
            active_l0_count=len(self.engine.level_0_epistemic),
            active_l1_count=len(self.engine.level_1_structural),
            total_active=self.engine.count_active(),
            current_efficacy=self.global_efficacy,
            efficacy_derivative=derivative,
            compute_budget=budget,
            candidate_axiom=winning_axiom or llm_candidate,
            tri_fold_metrics=winning_metrics or llm_metrics,
            user_candidate=user_seed,
            user_metrics=user_metrics,
            comparative_summary=comparative_summary,
            candidate_pool=[c for c, _ in tournament_pool],
            tournament_leaderboard=leaderboard_summary,
            decision=decision_label,
            jettison_triggered=jettison_occurred,
            lookahead_analysis=lookahead_result.to_dict() if lookahead_result else None,
            timestamp=datetime.datetime.now().isoformat(),
        )

        await self.telemetry.emit(
            TelemetryEvent(
                event_type=EventType.EPOCH_COMPLETED,
                epoch=epoch,
                payload={"telemetry": completed_telemetry.__dict__},
            )
        )

        # 9. Persist epoch reports (JSON, Markdown, and HTML Dashboard)
        self.reporter.save_epoch_report(
            telemetry=completed_telemetry,
            active_axioms=list(self.engine.axioms.values()),
            negative_axioms=self.engine.active_negative_axioms,
        )

        return completed_telemetry
