r"""Pass 2: Statechart & Invariant Integrity Evaluator ($S_{state}$, 20%).

Evaluates:
- Automated statechart transition walking across valid and invalid transitions.
- Prerequisite state-chain execution so stateful transitions run genuinely.
- Type-aware action invocation respecting defaults and annotations.
- Guard enforcement: asserts that illegal state jumps (e.g. IDLE -> COMMITTED, COMPLETED -> RUNNING) are rejected.
- Tightened AST fallback with paired guard & transition-structure verification (capped at 75.0).
"""

from __future__ import annotations

import ast
from collections import deque
from collections.abc import Mapping, Sequence, Set as AbstractSet
from enum import Enum
from http.server import BaseHTTPRequestHandler
import importlib
import importlib.util
import inspect
from pathlib import Path
import shutil
import sys
import types
import typing
from typing import Any, Dict, List, Optional, Set, Tuple
import uuid

from ..domain_models import BenchmarkArchetype, EvaluationPassResult


_WORKSPACE_ROOT = Path(__file__).resolve().parents[3]


def _make_scratch_temp_dir(prefix: str = "statechart_eval_") -> Path:
    """Allocates a hermetic temporary directory strictly inside workspace .scratch/."""
    scratch_root = _WORKSPACE_ROOT / ".scratch"
    scratch_root.mkdir(parents=True, exist_ok=True)
    temp_dir = scratch_root / f"{prefix}{uuid.uuid4().hex[:10]}"
    temp_dir.mkdir(parents=True, exist_ok=True)
    return temp_dir


def _purge_app_modules(
    app_dir: Optional[Path] = None,
    pre_modules: Optional[Set[str]] = None,
) -> None:
    """Purges dynamically loaded candidate modules to avoid cross-app pollution (VULN-CAL-06)."""
    resolved_app = app_dir.resolve() if app_dir is not None else None
    for key in list(sys.modules.keys()):
        if key == "src" or key.startswith("src.") or key.startswith("app_engine_") or key.startswith("app_sc_"):
            sys.modules.pop(key, None)
            continue
        if pre_modules is not None and key not in pre_modules:
            mod = sys.modules.get(key)
            mod_file = getattr(mod, "__file__", None) if mod is not None else None
            if resolved_app is not None and mod_file:
                try:
                    mod_path = Path(mod_file).resolve()
                    if resolved_app == mod_path or resolved_app in mod_path.parents:
                        sys.modules.pop(key, None)
                        continue
                except Exception:
                    pass
            if mod_file and resolved_app is not None and str(resolved_app) in str(mod_file):
                sys.modules.pop(key, None)


class StatechartEvaluator:
    """Evaluates Pass 2: Statechart & Invariant Integrity ($S_{state}$, Weight = 20%)."""

    _ENGINE_SUFFIXES = (
        "Engine",
        "Store",
        "Node",
        "Router",
        "Manager",
        "StateMachine",
        "Statechart",
        "Coordinator",
        "Executor",
        "Gateway",
        "Storage",
    )
    _PACKAGE_CANDIDATE_MODULES = (
        "src.engine",
        "src.statechart",
        "src.state_machine",
        "src.models",
        "src.node",
        "src.coordinator",
        "src.executor",
        "src.router",
        "src.gateway",
        "src.storage",
    )
    _STATE_NAMES = {"state", "current_state", "status", "phase", "mode"}

    def __init__(self, weight: float = 0.20) -> None:
        self.weight = weight

    def evaluate(self, app_dir: Path, archetype: BenchmarkArchetype) -> EvaluationPassResult:
        app_dir = app_dir.resolve()
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

        pre_modules = set(sys.modules.keys())
        orig_sys_path = list(sys.path)
        temp_dir = _make_scratch_temp_dir(prefix="statechart_eval_")

        try:
            engine_cls, engine_instance = self._load_app_engine(app_dir, transitions, temp_dir)
            total_tested = len(transitions)
            valid_passed = 0
            invalid_rejected = 0
            defects = 0
            details_log: List[str] = []

            if engine_instance is not None:
                initial_state = self._get_current_state(engine_instance)
                for t in transitions:
                    from_state = t.get("from")
                    to_state = t.get("to")
                    action = t.get("action")
                    is_valid = t.get("valid", True)

                    # Use a fresh isolated instance when possible to avoid cross-transition state leakage
                    work_inst = (
                        self._safe_instantiate(engine_cls, temp_dir)
                        if engine_cls is not None
                        else None
                    )
                    if work_inst is None:
                        work_inst = engine_instance

                    self._prepare_source_state(
                        work_inst,
                        from_state=from_state,
                        initial_state=initial_state,
                        transitions=transitions,
                        temp_dir=temp_dir,
                    )

                    method = getattr(work_inst, action, None) if action else None
                    if method is None:
                        if is_valid:
                            defects += 1
                            details_log.append(f"Missing valid transition action '{action}' on engine")
                        else:
                            # Missing illegal action cannot accidentally trigger an illegal jump
                            invalid_rejected += 1
                            details_log.append(f"Illegal action '{action}' absent on engine (blocked)")
                        continue

                    if is_valid:
                        try:
                            res = self._invoke_action(method, action, temp_dir=temp_dir)
                            current_state = self._get_current_state(work_inst)
                            if current_state is not None:
                                if current_state.upper() == str(to_state).upper():
                                    valid_passed += 1
                                    details_log.append(
                                        f"Valid transition '{action}' succeeded: {from_state} -> {to_state}"
                                    )
                                else:
                                    defects += 1
                                    details_log.append(
                                        f"Valid transition '{action}' failed to reach {to_state} (at {current_state})"
                                    )
                            elif res is not False and res is not None:
                                valid_passed += 1
                                details_log.append(
                                    f"Valid transition '{action}' executed without error"
                                )
                            else:
                                defects += 1
                                details_log.append(
                                    f"Valid transition '{action}' returned falsy/None with no observable state"
                                )
                        except Exception as e:
                            defects += 1
                            details_log.append(
                                f"Valid transition '{action}' raised unexpected exception: {e}"
                            )
                    else:
                        # Invalid transition: MUST be rejected
                        try:
                            self._invoke_action(method, action, temp_dir=temp_dir)
                            current_state = self._get_current_state(work_inst)
                            if current_state is not None and current_state.upper() == str(to_state).upper():
                                defects += 1
                                details_log.append(
                                    f"ILLEGAL transition '{action}' from {from_state} to {to_state} WAS ACCEPTED!"
                                )
                            else:
                                invalid_rejected += 1
                                details_log.append(
                                    f"Invalid transition '{action}' was blocked (state remained {current_state})"
                                )
                        except Exception as e:
                            invalid_rejected += 1
                            details_log.append(
                                f"Invalid transition '{action}' correctly rejected with guard exception: {type(e).__name__}"
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
                        "evaluation_mode": "dynamic_execution",
                        "engine_class": getattr(engine_cls, "__name__", type(engine_instance).__name__),
                        "total_transitions_tested": total_tested,
                        "valid_passed": valid_passed,
                        "invalid_rejected": invalid_rejected,
                        "defects_detected": defects,
                        "log": details_log[:15],
                    },
                    passed=(raw_score >= 70.0),
                )

            # Tightened Static AST Statechart Fallback (capped at 75.0)
            expected_states = {str(t.get("from")) for t in transitions if t.get("from")} | {
                str(t.get("to")) for t in transitions if t.get("to")
            }
            expected_actions = {str(t.get("action")) for t in transitions if t.get("action")}
            ast_states_found, paired_guards, transition_structures, found_actions = (
                self._inspect_ast_statecharts(app_dir, expected_states=expected_states, expected_actions=expected_actions)
            )

            matched_states = expected_states.intersection(ast_states_found)
            matched_actions = expected_actions.intersection(found_actions)
            state_cov = len(matched_states) / len(expected_states) if expected_states else 1.0
            action_cov = len(matched_actions) / len(expected_actions) if expected_actions else 1.0
            has_structural_guards = paired_guards > 0 or transition_structures > 0

            if not has_structural_guards:
                raw_score = round(min(45.0, 45.0 * state_cov), 2)
            else:
                guard_density = min(
                    1.0,
                    (paired_guards + transition_structures) / max(1, len(transitions)),
                )
                raw_score = round(
                    min(75.0, 75.0 * (0.45 * state_cov + 0.35 * action_cov + 0.20 * guard_density)),
                    2,
                )

            weighted_score = round(raw_score * self.weight, 2)
            return EvaluationPassResult(
                pass_name="statechart",
                weight=self.weight,
                raw_score=raw_score,
                weighted_score=weighted_score,
                details={
                    "evaluation_mode": "static_ast_fallback",
                    "static_cap": 75.0,
                    "expected_states": sorted(list(expected_states)),
                    "matched_states": sorted(list(matched_states)),
                    "matched_actions": sorted(list(matched_actions)),
                    "paired_guards_found": paired_guards,
                    "transition_structures_found": transition_structures,
                },
                passed=(raw_score >= 60.0),
            )
        finally:
            sys.path[:] = orig_sys_path
            _purge_app_modules(app_dir=app_dir, pre_modules=pre_modules)
            if temp_dir.exists():
                shutil.rmtree(temp_dir, ignore_errors=True)

    def _safe_instantiate(self, cls: type, temp_dir: Path) -> Optional[Any]:
        """Instantiates an engine class safely using inspect.signature."""
        try:
            sig = inspect.signature(cls.__init__)
        except (ValueError, TypeError):
            try:
                return cls()
            except Exception:
                return None

        kwargs: Dict[str, Any] = {}
        known_overrides: Dict[str, Any] = {
            "data_dir": Path(temp_dir),
            "storage_dir": Path(temp_dir),
            "wal_dir": Path(temp_dir),
            "wal_path": Path(temp_dir) / "statechart.wal",
            "db_path": Path(temp_dir) / "statechart.wal",
            "log_path": Path(temp_dir) / "statechart.wal",
            "wal_filename": "statechart.wal",
            "ttl_sweep_interval": 1.0,
            "enable_background_sweeper": False,
            "node_id": "sc_node_1",
            "peers": [],
        }

        try:
            hints = typing.get_type_hints(cls.__init__)
        except Exception:
            hints = {}

        for p_name, p in sig.parameters.items():
            if p_name == "self" or p.kind in (
                inspect.Parameter.VAR_POSITIONAL,
                inspect.Parameter.VAR_KEYWORD,
            ):
                continue
            if p_name in known_overrides:
                kwargs[p_name] = known_overrides[p_name]
                continue
            if p.default is not inspect.Parameter.empty:
                continue
            ann = hints.get(p_name, p.annotation)
            kwargs[p_name] = self._synthesize_arg_value(p_name, ann, temp_dir=temp_dir)

        try:
            return cls(**kwargs)
        except Exception:
            try:
                return cls()
            except Exception:
                return None

    def _load_app_engine(
        self,
        app_dir: Path,
        transitions: List[Dict[str, Any]],
        temp_dir: Path,
    ) -> Tuple[Optional[type], Optional[Any]]:
        """Package-aware discovery and ranked instantiation of the application's statechart engine."""
        if str(app_dir) not in sys.path:
            sys.path.insert(0, str(app_dir))

        loaded_modules: List[Tuple[str, Any]] = []

        # 1. Try canonical package imports first so relative imports work cleanly
        tried_mods: Set[str] = set()
        for mod_path in self._PACKAGE_CANDIDATE_MODULES:
            tried_mods.add(mod_path)
            try:
                mod = importlib.import_module(mod_path)
                loaded_modules.append((mod_path, mod))
            except Exception:
                pass

        # 2. Scan remaining src/*.py modules via package import
        src_dir = app_dir / "src"
        if src_dir.exists():
            for py_file in sorted(src_dir.glob("*.py")):
                if py_file.name.startswith("test_") or py_file.name == "__init__.py":
                    continue
                mod_path = f"src.{py_file.stem}"
                if mod_path in tried_mods:
                    continue
                tried_mods.add(mod_path)
                try:
                    mod = importlib.import_module(mod_path)
                    loaded_modules.append((mod_path, mod))
                except Exception:
                    pass

        # 3. Scan top-level *.py files (excluding test_*.py)
        for py_file in sorted(app_dir.glob("*.py")):
            if py_file.name.startswith("test_"):
                continue
            mod_name = f"app_sc_{app_dir.name}_{py_file.stem}"
            try:
                spec = importlib.util.spec_from_file_location(mod_name, str(py_file))
                if spec and spec.loader:
                    mod = importlib.util.module_from_spec(spec)
                    sys.modules[mod_name] = mod
                    spec.loader.exec_module(mod)
                    loaded_modules.append((mod_name, mod))
            except Exception:
                pass

        action_names = {str(t.get("action")) for t in transitions if t.get("action")}
        ranked: List[Tuple[Tuple[int, int, int], type]] = []
        seen_classes: Set[type] = set()

        for mod_name, mod in loaded_modules:
            for attr_name in dir(mod):
                val = getattr(mod, attr_name, None)
                if not isinstance(val, type) or val in seen_classes:
                    continue
                if issubclass(val, (Enum, BaseException, BaseHTTPRequestHandler)):
                    continue
                cls_name = getattr(val, "__name__", "")
                if cls_name.startswith("_") or not cls_name.endswith(self._ENGINE_SUFFIXES):
                    continue
                # Ensure class belongs to loaded app modules rather than an imported library
                cls_mod = getattr(val, "__module__", "")
                if cls_mod != mod_name and not (cls_mod == "src" or cls_mod.startswith("src.") or cls_mod.startswith("app_sc_")):
                    continue

                seen_classes.add(val)
                action_hits = sum(
                    1 for act in action_names if callable(getattr(val, act, None))
                )
                is_src_engine = 1 if mod_name in ("src.engine", "src.statechart", "src.state_machine") else 0
                is_primary_suffix = 1 if cls_name.endswith(("Engine", "Store")) else 0
                ranked.append(((action_hits, is_src_engine, is_primary_suffix), val))

        ranked.sort(key=lambda item: item[0], reverse=True)
        for _, cls in ranked:
            inst = self._safe_instantiate(cls, temp_dir)
            if inst is not None:
                return cls, inst

        return None, None

    def _prepare_source_state(
        self,
        instance: Any,
        from_state: Optional[str],
        initial_state: Optional[str],
        transitions: List[Dict[str, Any]],
        temp_dir: Optional[Path] = None,
    ) -> None:
        """Reaches from_state via a valid prerequisite chain when possible, falling back to _force_set_state."""
        if not from_state:
            return
        cur = self._get_current_state(instance)
        if cur is not None and cur.upper() == str(from_state).upper():
            return

        # Try BFS over valid transitions from initial_state -> from_state
        start = cur or initial_state
        if start and start.upper() != str(from_state).upper():
            adj: Dict[str, List[Tuple[str, str]]] = {}
            for t in transitions:
                if t.get("valid", True) and t.get("from") and t.get("to") and t.get("action"):
                    f_s = str(t["from"]).upper()
                    t_s = str(t["to"]).upper()
                    adj.setdefault(f_s, []).append((t_s, str(t["action"])))

            target_upper = str(from_state).upper()
            queue: deque[Tuple[str, List[str]]] = deque([(start.upper(), [])])
            visited: Set[str] = {start.upper()}
            found_chain: Optional[List[str]] = None

            while queue:
                state_node, path = queue.popleft()
                if state_node == target_upper:
                    found_chain = path
                    break
                if len(path) >= 6:
                    continue
                for nxt_state, act in adj.get(state_node, []):
                    if nxt_state not in visited:
                        visited.add(nxt_state)
                        queue.append((nxt_state, path + [act]))

            if found_chain:
                chain_ok = True
                for act in found_chain:
                    fn = getattr(instance, act, None)
                    if fn is None:
                        chain_ok = False
                        break
                    try:
                        self._invoke_action(fn, act, temp_dir=temp_dir)
                    except Exception:
                        chain_ok = False
                        break
                new_cur = self._get_current_state(instance)
                if chain_ok and (new_cur is None or new_cur.upper() == target_upper):
                    return

        self._force_set_state(instance, from_state)

    def _assign_state_attr(self, holder: Any, attr_name: str, state_val: str) -> None:
        cur = getattr(holder, attr_name, None)
        target_val: Any = state_val
        if isinstance(cur, Enum):
            enum_cls = type(cur)
            for member in enum_cls:
                if member.name.upper() == str(state_val).upper() or str(member.value).upper() == str(state_val).upper():
                    target_val = member
                    break
        try:
            setattr(holder, attr_name, target_val)
            return
        except AttributeError:
            # Handle read-only @property descriptors by falling back to backing attributes
            for backing in (f"_{attr_name}", "_state", "_current_state"):
                if hasattr(holder, backing):
                    try:
                        setattr(holder, backing, target_val)
                        return
                    except AttributeError:
                        continue

    def _force_set_state(self, instance: Any, state_val: Optional[str]) -> None:
        """Sets internal state to specified state value if supported, preserving Enum types."""
        if state_val is None:
            return
        if hasattr(instance, "state"):
            st = getattr(instance, "state")
            if hasattr(st, "current_state"):
                self._assign_state_attr(st, "current_state", state_val)
                return
            if hasattr(st, "state"):
                self._assign_state_attr(st, "state", state_val)
                return
            if isinstance(st, (str, Enum)):
                self._assign_state_attr(instance, "state", state_val)
                return
        if hasattr(instance, "current_state"):
            self._assign_state_attr(instance, "current_state", state_val)
            return
        if hasattr(instance, "role"):
            self._assign_state_attr(instance, "role", state_val)

    def _extract_state_str(self, val: Any) -> Optional[str]:
        if val is None:
            return None
        if isinstance(val, Enum):
            return val.name
        return str(val)

    def _get_current_state(self, instance: Any) -> Optional[str]:
        """Reads internal state string from instance (handling Enum values cleanly)."""
        if hasattr(instance, "state"):
            st = getattr(instance, "state")
            if hasattr(st, "current_state"):
                return self._extract_state_str(st.current_state)
            if hasattr(st, "state"):
                return self._extract_state_str(st.state)
            if isinstance(st, (str, Enum)):
                return self._extract_state_str(st)
        if hasattr(instance, "current_state"):
            return self._extract_state_str(getattr(instance, "current_state"))
        if hasattr(instance, "role"):
            return self._extract_state_str(getattr(instance, "role"))
        return None

    def _unwrap_annotation_name(self, annotation: Any) -> str:
        """Normalizes type annotations (including Optional/Union/PEP 563 strings) to a canonical lowercase hint."""
        if annotation is inspect.Parameter.empty or annotation is Any:
            return ""

        origin = typing.get_origin(annotation)
        if origin is not None:
            union_types = (typing.Union, types.UnionType)
            if origin in union_types:
                args = [a for a in typing.get_args(annotation) if a is not type(None)]
                if args:
                    return self._unwrap_annotation_name(args[0])
                return ""
            return self._unwrap_annotation_name(origin)

        if isinstance(annotation, type):
            if annotation is bool:
                return "bool"
            if annotation is int:
                return "int"
            if annotation is float:
                return "float"
            if annotation is str:
                return "str"
            if annotation is bytes:
                return "bytes"
            if annotation is dict or issubclass(annotation, Mapping):
                return "dict"
            if annotation is list or (issubclass(annotation, Sequence) and annotation not in (str, bytes, bytearray)):
                return "list"
            if annotation is set or issubclass(annotation, AbstractSet):
                return "set"
            if annotation is Path:
                return "path"
            return annotation.__name__.lower()

        text = str(annotation).strip()
        if text.startswith("typing."):
            text = text[7:]
        # Handle stringified Optional[T] / Union[T, None] / T | None
        if text.startswith("Optional[") and text.endswith("]"):
            text = text[9:-1].strip()
        elif "|" in text:
            parts = [part.strip() for part in text.split("|") if part.strip() != "None"]
            if parts:
                text = parts[0]
        elif text.startswith("Union[") and text.endswith("]"):
            inner = text[6:-1]
            parts = [part.strip() for part in inner.split(",") if part.strip() != "None"]
            if parts:
                text = parts[0]

        low = text.lower()
        for prefix in ("dict", "mapping"):
            if low == prefix or low.startswith(f"{prefix}["):
                return "dict"
        for prefix in ("list", "sequence", "tuple"):
            if low == prefix or low.startswith(f"{prefix}["):
                return "list"
        for prefix in ("set", "frozenset"):
            if low == prefix or low.startswith(f"{prefix}["):
                return "set"
        if low in ("path", "pathlib.path", "os.pathlike"):
            return "path"
        if low in ("bool", "int", "float", "str", "bytes"):
            return low
        return low

    def _synthesize_arg_value(
        self,
        param_name: str,
        annotation: Any,
        temp_dir: Optional[Path] = None,
    ) -> Any:
        """Synthesizes a type-aware argument value for a required parameter without a default."""
        type_hint = self._unwrap_annotation_name(annotation)

        if type_hint == "bool":
            return True
        if type_hint == "int":
            return 1
        if type_hint == "float":
            return 1.0
        if type_hint == "dict":
            return {}
        if type_hint == "list":
            return []
        if type_hint == "set":
            return set()
        if type_hint == "path":
            return (temp_dir / "test_path") if temp_dir else Path(".")
        if type_hint == "bytes":
            return b"test_bytes"

        # Apply parameter name heuristics for untyped or str-typed parameters
        lname = param_name.lower()
        if lname in ("tx_id", "workflow_id", "session_id", "client_id", "element_id", "job_id", "doc_id", "node_id", "key", "k"):
            return "test_id_1"
        if lname in ("path", "file_path", "data_dir", "wal_path"):
            return str(temp_dir / "test_path") if temp_dir else "/test"

        if type_hint == "str":
            return "test_arg"

        if lname in ("timeout", "interval", "delay", "rate", "weight", "ratio", "threshold", "ttl"):
            return 1.0
        if lname in ("ttl_seconds", "clock"):
            return 10
        if lname in ("limit", "port", "retries", "max_retries", "term", "index", "count", "size", "capacity", "burst", "version", "epoch", "step"):
            return 1
        if lname in ("enabled", "force", "strict", "flag", "dry_run") or lname.startswith(("is_", "has_", "allow_")):
            return True
        if lname in ("config", "headers", "metadata", "params", "options", "rules_map", "payload"):
            return {}
        if lname in ("data", "value"):
            return "test_val"
        if lname in ("tasks_data", "tasks", "new_rules", "incoming_elements", "items", "peers", "nodes", "entries", "rules"):
            return []

        return "test_arg"

    def _invoke_action(
        self,
        method: Any,
        action_name: str,
        temp_dir: Optional[Path] = None,
    ) -> Any:
        """Invokes engine method with type-aware parameters, respecting parameter defaults first (VULN-CAL-08)."""
        sig = inspect.signature(method)
        try:
            hints = typing.get_type_hints(method)
        except Exception:
            hints = {}

        args: List[Any] = []
        kwargs: Dict[str, Any] = {}

        for p in sig.parameters.values():
            if p.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
                continue
            # Respect defaults first: omit optional parameters so method defaults take effect
            if p.default is not inspect.Parameter.empty:
                continue

            ann = hints.get(p.name, p.annotation)
            val = self._synthesize_arg_value(p.name, ann, temp_dir=temp_dir)
            if p.kind == inspect.Parameter.KEYWORD_ONLY:
                kwargs[p.name] = val
            else:
                args.append(val)

        return method(*args, **kwargs)

    def _inspect_ast_statecharts(
        self,
        app_dir: Path,
        expected_states: Optional[Set[str]] = None,
        expected_actions: Optional[Set[str]] = None,
    ) -> Tuple[Set[str], int, int, Set[str]]:
        """Extracts state constants, paired guard conditionals, transition structures, and actions from AST."""
        found_states: Set[str] = set()
        found_actions: Set[str] = set()
        paired_guards = 0
        transition_structures = 0
        expected_states_upper = {s.upper() for s in (expected_states or set())}

        def _is_state_identifier(name: str) -> bool:
            low = name.lower()
            return low in self._STATE_NAMES or any(tok in low for tok in ("state", "status", "phase", "role"))

        def _expr_references_state(expr: ast.AST, known_states: Set[str]) -> bool:
            for sub in ast.walk(expr):
                if isinstance(sub, ast.Name) and (_is_state_identifier(sub.id) or sub.id.upper() in known_states):
                    return True
                if isinstance(sub, ast.Attribute) and _is_state_identifier(sub.attr):
                    return True
                if isinstance(sub, ast.Constant) and isinstance(sub.value, str):
                    if sub.value.upper() in known_states or (sub.value.isupper() and len(sub.value) >= 3):
                        return True
            return False

        def _body_enforces_guard_or_transition(stmts: List[ast.stmt]) -> bool:
            for stmt in stmts:
                for sub in ast.walk(stmt):
                    if isinstance(sub, (ast.Raise, ast.Return)):
                        return True
                    if isinstance(sub, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
                        targets = sub.targets if isinstance(sub, ast.Assign) else [sub.target]
                        for tgt in targets:
                            if isinstance(tgt, ast.Name) and _is_state_identifier(tgt.id):
                                return True
                            if isinstance(tgt, ast.Attribute) and _is_state_identifier(tgt.attr):
                                return True
            return False

        for py_file in app_dir.rglob("*.py"):
            if "__pycache__" in py_file.parts:
                continue
            rel_parts = py_file.relative_to(app_dir).parts if app_dir in py_file.parents else py_file.parts
            if "tests" in rel_parts or py_file.name.startswith("test_") or py_file.name.endswith("_test.py"):
                continue

            try:
                tree = ast.parse(py_file.read_text(encoding="utf-8"))
            except Exception:
                continue

            # Pass A: collect Enum members, uppercase constants, and method names
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    is_enum = any(
                        (isinstance(b, ast.Name) and "Enum" in b.id)
                        or (isinstance(b, ast.Attribute) and "Enum" in b.attr)
                        for b in node.bases
                    )
                    if is_enum:
                        for stmt in node.body:
                            if isinstance(stmt, ast.Assign):
                                for tgt in stmt.targets:
                                    if isinstance(tgt, ast.Name) and tgt.id.isupper() and len(tgt.id) >= 3:
                                        found_states.add(tgt.id)
                            elif isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
                                if stmt.target.id.isupper() and len(stmt.target.id) >= 3:
                                    found_states.add(stmt.target.id)
                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    found_actions.add(node.name)
                elif isinstance(node, ast.Constant) and isinstance(node.value, str):
                    val = node.value
                    if val.isupper() and len(val) >= 3:
                        found_states.add(val)

            known_states_local = found_states | expected_states_upper

            # Pass B: paired guards & transition table structures
            for node in ast.walk(tree):
                if isinstance(node, ast.If):
                    if _expr_references_state(node.test, known_states_local) and (
                        _body_enforces_guard_or_transition(node.body)
                        or _body_enforces_guard_or_transition(node.orelse)
                    ):
                        paired_guards += 1
                elif isinstance(node, ast.Match):
                    if _expr_references_state(node.subject, known_states_local) and any(
                        _body_enforces_guard_or_transition(c.body) for c in node.cases
                    ):
                        paired_guards += 1
                elif isinstance(node, ast.Dict) and len(node.keys) >= 2:
                    state_refs = 0
                    for elem in list(node.keys) + list(node.values):
                        if elem is None:
                            continue
                        if isinstance(elem, ast.Constant) and isinstance(elem.value, str):
                            if elem.value.upper() in known_states_local:
                                state_refs += 1
                        elif isinstance(elem, ast.Attribute) and elem.attr.upper() in known_states_local:
                            state_refs += 1
                        elif isinstance(elem, ast.Set):
                            for sub_e in elem.elts:
                                if isinstance(sub_e, ast.Constant) and isinstance(sub_e.value, str) and sub_e.value.upper() in known_states_local:
                                    state_refs += 1
                                elif isinstance(sub_e, ast.Attribute) and sub_e.attr.upper() in known_states_local:
                                    state_refs += 1
                    if state_refs >= 2:
                        transition_structures += 1

        if expected_actions:
            matched_action_count = len(expected_actions.intersection(found_actions))
            if matched_action_count >= 2:
                transition_structures += 1

        return found_states, paired_guards, transition_structures, found_actions
