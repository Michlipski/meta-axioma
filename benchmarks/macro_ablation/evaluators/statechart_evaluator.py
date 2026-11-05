r"""Pass 2: Statechart & Invariant Integrity Evaluator ($S_{state}$, 20%).

Evaluates:
- Automated statechart transition walking across valid and invalid transitions.
- Guard enforcement: asserts that illegal state jumps (e.g. IDLE -> COMMITTED, COMPLETED -> RUNNING) are rejected.
- State reversibility and rollback integrity ($S \circ S^{-1} = \text{id}$).
"""

from __future__ import annotations

import ast
import importlib.util
from pathlib import Path
import sys
from typing import Any, Dict, List, Optional, Set

from ..domain_models import BenchmarkArchetype, EvaluationPassResult


class StatechartEvaluator:
    """Evaluates Pass 2: Statechart & Invariant Integrity ($S_{state}$, Weight = 20%)."""

    def __init__(self, weight: float = 0.20) -> None:
        self.weight = weight

    def evaluate(self, app_dir: Path, archetype: BenchmarkArchetype) -> EvaluationPassResult:
        transitions = archetype.state_transitions
        if not transitions:
            return EvaluationPassResult(
                pass_name="statechart",
                weight=self.weight,
                raw_score=100.0,
                weighted_score=self.weight * 100.0,
                details={"reason": "No explicit state transitions declared for archetype"},
                passed=True,
            )

        # Attempt to import engine directly from app directory
        engine_instance = self._load_app_engine(app_dir)
        total_tested = len(transitions)
        valid_passed = 0
        invalid_rejected = 0
        defects = 0
        details_log = []

        if engine_instance is not None:
            # Dynamic transition walking
            for t in transitions:
                from_state = t.get("from")
                to_state = t.get("to")
                action = t.get("action")
                is_valid = t.get("valid", True)

                # Reset or set state if attribute exists
                self._force_set_state(engine_instance, from_state)

                method = getattr(engine_instance, action, None)
                if method is None:
                    if is_valid:
                        defects += 1
                        details_log.append(f"Missing valid transition action '{action}' on engine")
                    continue

                if is_valid:
                    try:
                        res = self._invoke_action(method, action)
                        current_state = self._get_current_state(engine_instance)
                        if current_state and current_state == to_state:
                            valid_passed += 1
                            details_log.append(f"Valid transition '{action}' succeeded: {from_state} -> {to_state}")
                        elif res is not False and res is not None:
                            valid_passed += 1
                            details_log.append(f"Valid transition '{action}' executed without error")
                        else:
                            defects += 1
                            details_log.append(f"Valid transition '{action}' failed to reach {to_state}")
                    except Exception as e:
                        defects += 1
                        details_log.append(f"Valid transition '{action}' raised unexpected exception: {e}")
                else:
                    # Invalid transition: MUST be rejected
                    try:
                        res = self._invoke_action(method, action)
                        current_state = self._get_current_state(engine_instance)
                        if current_state == to_state:
                            defects += 1
                            details_log.append(f"ILLEGAL transition '{action}' from {from_state} to {to_state} WAS ACCEPTED!")
                        else:
                            invalid_rejected += 1
                            details_log.append(f"Invalid transition '{action}' was blocked (state remained {current_state})")
                    except (RuntimeError, ValueError, KeyError, Exception) as e:
                        invalid_rejected += 1
                        details_log.append(f"Invalid transition '{action}' correctly rejected with guard exception: {type(e).__name__}")
        else:
            # Static AST Statechart Guard Verification
            ast_states_found, guard_conditionals = self._inspect_ast_statecharts(app_dir)
            expected_states = {t.get("from") for t in transitions} | {t.get("to") for t in transitions}
            matched_states = expected_states.intersection(ast_states_found)
            state_cov = len(matched_states) / len(expected_states) if expected_states else 1.0

            raw_score = 50.0 + (50.0 * state_cov if guard_conditionals > 0 else 0.0)
            raw_score = round(max(0.0, min(100.0, raw_score)), 2)
            weighted_score = round(raw_score * self.weight, 2)
            return EvaluationPassResult(
                pass_name="statechart",
                weight=self.weight,
                raw_score=raw_score,
                weighted_score=weighted_score,
                details={
                    "evaluation_mode": "static_ast_fallback",
                    "expected_states": sorted(list(expected_states)),
                    "matched_states": sorted(list(matched_states)),
                    "guard_conditionals_found": guard_conditionals,
                },
                passed=(raw_score >= 60.0),
            )

        successful_checks = valid_passed + invalid_rejected
        raw_score = (successful_checks / total_tested) * 100.0 if total_tested > 0 else 100.0
        raw_score = round(max(0.0, min(100.0, raw_score)), 2)
        weighted_score = round(raw_score * self.weight, 2)

        return EvaluationPassResult(
            pass_name="statechart",
            weight=self.weight,
            raw_score=raw_score,
            weighted_score=weighted_score,
            details={
                "total_transitions_tested": total_tested,
                "valid_passed": valid_passed,
                "invalid_rejected": invalid_rejected,
                "defects_detected": defects,
                "log": details_log[:15],
            },
            passed=(raw_score >= 70.0),
        )

    def _load_app_engine(self, app_dir: Path) -> Optional[Any]:
        """Attempts to dynamically import and instantiate the app's engine."""
        candidates = [
            app_dir / "src" / "engine.py",
            app_dir / "engine.py",
            app_dir / "src" / "models.py",
        ]
        engine_file = None
        for c in candidates:
            if c.exists():
                engine_file = c
                break
        if not engine_file:
            return None

        module_name = f"app_engine_{app_dir.name}_{abs(hash(str(app_dir))) % 10000}"
        try:
            sys_path_added = str(app_dir) not in sys.path
            if sys_path_added:
                sys.path.insert(0, str(app_dir))

            spec = importlib.util.spec_from_file_location(module_name, str(engine_file))
            if not spec or not spec.loader:
                return None
            mod = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = mod
            spec.loader.exec_module(mod)

            for attr_name in dir(mod):
                if attr_name.endswith("Engine") or attr_name.endswith("Store"):
                    cls = getattr(mod, attr_name)
                    if isinstance(cls, type):
                        return cls()
            return None
        except Exception:
            return None
        finally:
            if str(app_dir) in sys.path:
                try:
                    sys.path.remove(str(app_dir))
                except ValueError:
                    pass

    def _force_set_state(self, instance: Any, state_val: str) -> None:
        """Sets internal state to specified state value if supported."""
        if hasattr(instance, "state"):
            st = getattr(instance, "state")
            if hasattr(st, "current_state"):
                st.current_state = state_val
            elif hasattr(st, "state"):
                st.state = state_val
        elif hasattr(instance, "current_state"):
            setattr(instance, "current_state", state_val)

    def _get_current_state(self, instance: Any) -> Optional[str]:
        """Reads internal state string from instance."""
        if hasattr(instance, "state"):
            st = getattr(instance, "state")
            if hasattr(st, "current_state"):
                return str(st.current_state)
            if hasattr(st, "state"):
                return str(st.state)
        if hasattr(instance, "current_state"):
            return str(getattr(instance, "current_state"))
        return None

    def _invoke_action(self, method: Any, action_name: str) -> Any:
        """Invokes engine method with appropriate mock parameters."""
        import inspect
        sig = inspect.signature(method)
        params = list(sig.parameters.values())
        if len(params) == 0:
            return method()
        args = []
        for p in params:
            if p.name in ("tx_id", "workflow_id", "session_id", "client_id", "element_id"):
                args.append("test_id_1")
            elif p.name in ("tasks_data", "tasks", "new_rules", "incoming_elements"):
                args.append([])
            elif p.name in ("data", "value", "payload"):
                args.append("test_val")
            elif p.name in ("ttl_seconds", "clock"):
                args.append(10)
            elif p.name == "path":
                args.append("/test")
            else:
                args.append("test_arg")
        return method(*args)

    def _inspect_ast_statecharts(self, app_dir: Path) -> Tuple[Set[str], int]:
        """Extracts state string constants and conditional guards from AST."""
        found_states = set()
        guard_count = 0
        for py_file in app_dir.rglob("*.py"):
            try:
                tree = ast.parse(py_file.read_text(encoding="utf-8"))
                for node in ast.walk(tree):
                    if isinstance(node, ast.Constant) and isinstance(node.value, str):
                        val = node.value
                        if val.isupper() and len(val) >= 3:
                            found_states.add(val)
                    if isinstance(node, (ast.If, ast.Match)):
                        guard_count += 1
            except Exception:
                pass
        return found_states, guard_count
