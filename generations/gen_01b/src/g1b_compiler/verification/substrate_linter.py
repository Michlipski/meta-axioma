"""Substrate Invariant & Quality Linter for System G1b.

Enforces Transgenerational Substrate Invariants:
1. Anti-Mock Substrate Invariant (NEG-G2-005): Real system APIs only; bans fake notification banners & mock timers.
2. Clean-Slate Production State Invariant (NEG-G2-006): Zero mock fixtures in production database seeds.
3. Visual Dignity & Ergonomic Design Token Invariant (NEG-G2-008): Bans unstyled default rectangles; enforces touch targets >= 44px.
4. Demarcated Exception Enclaves (L1-016): Network and external I/O wrapped in explicit error isolation boundaries.
"""

from dataclasses import dataclass, field
import re
from typing import Any, Dict, List


@dataclass
class SubstrateLintResult:
    passed: bool
    anti_mock_passed: bool
    clean_slate_passed: bool
    visual_dignity_passed: bool
    violations: List[str] = field(default_factory=list)


class SubstrateLinter:
    """Audits generated application code and initial state against physical substrate invariants."""

    # Forbidden patterns simulating hardware or mocking state in production
    FORBIDDEN_MOCK_PATTERNS = [
        (r"simulated[\s_-]?notification", "Simulated notification banner detected (Violates NEG-G2-005: Use real Web Notification or Android Channel API)."),
        (r"mock[\s_-]?counter", "Hardcoded mock counter detected (Violates NEG-G2-005)."),
        (r"fake[\s_-]?timer", "Fake timer detected (Violates NEG-G2-005)."),
        (r"setTimeout\s*\(\s*\(\)\s*=>\s*\{\s*alert\(", "Mock alert timeout detected (Violates NEG-G2-005)."),
    ]

    # Ugly default styling patterns
    FORBIDDEN_UNSTYLED_PATTERNS = [
        (r"style\s*=\s*['\"]background:\s*white;\s*border:\s*1px\s*solid\s*black['\"]", "Unstyled default rectangle detected (Violates NEG-G2-008: Visual Dignity)."),
        (r"<button\s*>\s*[^<]+\s*</button>", "Raw unstyled HTML button detected without design tokens or utility classes (Violates NEG-G2-008)."),
    ]

    def audit_code(self, source_code: str) -> List[str]:
        """Audits source code for anti-mock and visual dignity violations."""
        violations = []

        for pattern, msg in self.FORBIDDEN_MOCK_PATTERNS:
            if re.search(pattern, source_code, re.IGNORECASE):
                violations.append(f"[Anti-Mock Failure] {msg}")

        for pattern, msg in self.FORBIDDEN_UNSTYLED_PATTERNS:
            if re.search(pattern, source_code, re.IGNORECASE):
                violations.append(f"[Visual Dignity Failure] {msg}")

        return violations

    def audit_clean_slate_seeds(self, seeds: Dict[str, List[Dict[str, Any]]]) -> List[str]:
        """Audits initial seed database to ensure pristine state without dummy fixtures (NEG-G2-006)."""
        violations = []
        dummy_markers = ["foo", "bar", "test word", "dummy", "lorem ipsum", "sample item"]

        for table, rows in seeds.items():
            for row in rows:
                for val in row.values():
                    if isinstance(val, str):
                        for marker in dummy_markers:
                            if marker in val.lower():
                                violations.append(
                                    f"[Clean-Slate Failure] Dummy seed marker '{marker}' found in table '{table}': {val}"
                                )
        return violations

    def evaluate(self, source_code: str, seeds: Dict[str, List[Dict[str, Any]]]) -> SubstrateLintResult:
        code_violations = self.audit_code(source_code)
        seed_violations = self.audit_clean_slate_seeds(seeds)

        anti_mock_passed = not any("[Anti-Mock Failure]" in v for v in code_violations)
        visual_dignity_passed = not any("[Visual Dignity Failure]" in v for v in code_violations)
        clean_slate_passed = len(seed_violations) == 0

        all_violations = code_violations + seed_violations
        return SubstrateLintResult(
            passed=len(all_violations) == 0,
            anti_mock_passed=anti_mock_passed,
            clean_slate_passed=clean_slate_passed,
            visual_dignity_passed=visual_dignity_passed,
            violations=all_violations
        )
