r"""Adversarial Chaos Fuzzing Suite for HERM-006 Unrendered LaTeX Isolation.

Mandate 3 of Phase 2C under [INV-G4B-CAUSAL-002] and [NEG-G1B-002]:
- Probe ZeroTrustMicroAuditor.check_unrendered_latex() and audit_html_deliverable() with:
    1. Deeply nested LaTeX tags
    2. Obscure LaTeX symbols (\otimes, \oplus, \circ, \partial, \nabla, \infty, etc.)
    3. Malformed LaTeX formulas ($$ unclosed math, \( mismatched paren ], \[ unclosed bracket)
    4. JavaScript template literals with complex dollar interpolation (${Math.round($100)}, ${tokens.toLocaleString()} BPE)
    5. Text currency with commas and currency codes ($1,000,000 USD, $42.50)
    6. Escaped dollars (\$100, \$foo)
    7. Valid hermetic KaTeX markup with inline scripts and auto-render
- Verify that all true LaTeX defects are caught with rule_id="HERM-006" (severity FATAL).
- Verify that false positives on JS templates and currency are exactly 0.0%.
"""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

AUDIT_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = AUDIT_ROOT.parent.parent.parent.parent
for p in [str(AUDIT_ROOT), str(AUDIT_ROOT / "src"), str(REPO_ROOT)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from src.domain_models import AuditSeverity
from src.zero_trust_micro_auditor import ZeroTrustMicroAuditor


class TestHerm006AdversarialFuzzing(unittest.TestCase):
    """Adversarial chaos fuzzer verifying mathematical typography hermeticity (HERM-006)."""

    def setUp(self) -> None:
        self.auditor = ZeroTrustMicroAuditor(auditor_node_id="fuzz_sentry_node_herm006")

    def _wrap_html(self, body_inner: str, head_inner: str = "") -> str:
        """Wraps snippet in valid HTML document >= 100 bytes to avoid HERM-005 empty deliverable error."""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Adversarial Hermetic Deliverable Probe</title>
    {head_inner}
</head>
<body>
    <header><h1>Axioma Cluster Diagnostics</h1></header>
    <main>
        {body_inner}
    </main>
    <footer><span>SHA-256 Verified Offline Node</span></footer>
</body>
</html>"""

    # -------------------------------------------------------------------------
    # Vector 1: Deeply Nested LaTeX Tags
    # -------------------------------------------------------------------------
    def test_vector1_deeply_nested_latex_tags(self) -> None:
        """Verifies detection of LaTeX expressions buried in deeply nested DOM hierarchies."""
        nested_patterns = [
            "<div><main><section><article><p><span><code>\\( \\Delta S = 0 \\)</code></span></p></article></section></main></div>",
            "<table><tbody><tr><td><div><span><div>\\[ Q_{\\min} \\ge 10 \\]</div></span></div></td></tr></tbody></table>",
            "<aside><nav><ul><li><span>$$ \\mathcal{H} = \\sum_{i} E_i $$</span></li></ul></nav></aside>",
        ]
        for nested in nested_patterns:
            culprits = ZeroTrustMicroAuditor.check_unrendered_latex(nested)
            self.assertTrue(len(culprits) > 0, f"Failed to detect nested LaTeX: {nested}")

            html_doc = self._wrap_html(nested)
            report = self.auditor.audit_html_deliverable(html_doc, deliverable_id="deep_nesting_leaf")
            self.assertFalse(report.is_hermetic)
            herm_006_viols = [v for v in report.violations if v.rule_id == "HERM-006"]
            self.assertTrue(len(herm_006_viols) > 0)
            self.assertEqual(herm_006_viols[0].severity, AuditSeverity.FATAL)

    # -------------------------------------------------------------------------
    # Vector 2: Obscure LaTeX Symbols
    # -------------------------------------------------------------------------
    def test_vector2_obscure_latex_symbols(self) -> None:
        r"""Verifies detection of obscure LaTeX symbols: \otimes, \oplus, \circ, \partial, \nabla, \infty."""
        obscure_symbols = [
            r"\otimes",
            r"\oplus",
            r"\circ",
            r"\partial",
            r"\nabla",
            r"\infty",
            r"\forall",
            r"\exists",
            r"\approx",
            r"\subset",
            r"\emptyset",
            r"\implies",
        ]
        for sym in obscure_symbols:
            raw_text = f"<p>Quantum tensor operation: {sym} state</p>"
            culprits = ZeroTrustMicroAuditor.check_unrendered_latex(raw_text)
            self.assertTrue(len(culprits) > 0, f"Symbol {sym} escaped detection in check_unrendered_latex")
            self.assertIn(sym, culprits)

            html_doc = self._wrap_html(raw_text)
            report = self.auditor.audit_html_deliverable(html_doc, deliverable_id=f"obscure_sym_{sym.replace('\\', '')}")
            self.assertFalse(report.is_hermetic, f"Report marked hermetic despite containing {sym}")
            herm_006_viols = [v for v in report.violations if v.rule_id == "HERM-006"]
            self.assertTrue(any(v.culprit_token == sym for v in herm_006_viols))

    # -------------------------------------------------------------------------
    # Vector 3: Malformed LaTeX Formulas
    # -------------------------------------------------------------------------
    def test_vector3_malformed_latex_formulas(self) -> None:
        """Verifies detection of unclosed delimiters and mismatched parentheses."""
        malformed_snippets = [
            ("$$ unclosed math", "$$"),
            (r"\( mismatched paren ]", r"\("),
            (r"\[ unclosed bracket without closing", r"\["),
        ]
        for malformed, expected_indicator in malformed_snippets:
            culprits = ZeroTrustMicroAuditor.check_unrendered_latex(malformed)
            self.assertTrue(len(culprits) > 0, f"Malformed formula '{malformed}' escaped detection")
            self.assertTrue(any(expected_indicator in c for c in culprits))

            html_doc = self._wrap_html(f"<div>Status: {malformed}</div>")
            report = self.auditor.audit_html_deliverable(html_doc, deliverable_id="malformed_latex_leaf")
            self.assertFalse(report.is_hermetic)
            herm_006_viols = [v for v in report.violations if v.rule_id == "HERM-006"]
            self.assertTrue(len(herm_006_viols) > 0)
            self.assertEqual(herm_006_viols[0].severity, AuditSeverity.FATAL)

    # -------------------------------------------------------------------------
    # Vector 4: JavaScript Template Literals With Complex Dollar Interpolation
    # -------------------------------------------------------------------------
    def test_vector4_js_template_literals_zero_false_positives(self) -> None:
        """Verifies that JS template literals `${...}` never produce false positive HERM-006 violations."""
        js_snippets = [
            r"<script>const label = `${Math.round($100)} USD`;</script>",
            r"<script>hudTokens.innerHTML = `${tokens.toLocaleString()} BPE`;</script>",
            r"<script>const ratio = `${(n / 1000).toFixed(2)} k-ops`;</script>",
            r"<script>console.log(`${user.name} spent ${tx.cost}$`);</script>",
            r"<script>const multiline = `Result: ${Math.max(10, 20)} items`;</script>",
        ]
        for snippet in js_snippets:
            culprits = ZeroTrustMicroAuditor.check_unrendered_latex(snippet)
            self.assertEqual(len(culprits), 0, f"False positive in check_unrendered_latex for JS template: {culprits}")

            html_doc = self._wrap_html(f"<div>Interactive Telemetry</div>\n{snippet}")
            report = self.auditor.audit_html_deliverable(html_doc, deliverable_id="js_template_leaf")
            latex_violations = [v for v in report.violations if v.rule_id == "HERM-006"]
            self.assertEqual(
                len(latex_violations), 0, f"False positive HERM-006 violation raised on JS template: {latex_violations}"
            )
            self.assertTrue(report.is_hermetic)

    # -------------------------------------------------------------------------
    # Vector 5: Text Currency With Commas and Currency Codes
    # -------------------------------------------------------------------------
    def test_vector5_text_currency_zero_false_positives(self) -> None:
        """Verifies that standard currency notation ($1,000,000 USD, $42.50) never triggers HERM-006."""
        currency_snippets = [
            "<p>The total capital spend was $1,000,000 USD during Q3.</p>",
            "<p>Unit cost per BPE token execution is $42.50.</p>",
            "<p>Account balances: $100, $143,100, and $50.00 EUR.</p>",
            "<p>Micro transaction fee: $0.00025 USD.</p>",
            "<p>Budget pool capped at $500k.</p>",
        ]
        for snippet in currency_snippets:
            culprits = ZeroTrustMicroAuditor.check_unrendered_latex(snippet)
            self.assertEqual(len(culprits), 0, f"False positive on currency in check_unrendered_latex: {culprits}")

            html_doc = self._wrap_html(snippet)
            report = self.auditor.audit_html_deliverable(html_doc, deliverable_id="currency_leaf")
            latex_violations = [v for v in report.violations if v.rule_id == "HERM-006"]
            self.assertEqual(len(latex_violations), 0, f"False positive HERM-006 raised on currency: {latex_violations}")
            self.assertTrue(report.is_hermetic)

    # -------------------------------------------------------------------------
    # Vector 6: Escaped Dollars
    # -------------------------------------------------------------------------
    def test_vector6_escaped_dollars_zero_false_positives(self) -> None:
        r"""Verifies that escaped dollars (\$100, \$foo) do not trigger HERM-006."""
        escaped_snippets = [
            r"<p>Literal escaped price is \$100 only.</p>",
            r"<p>Variable name is \$foo in PHP syntax.</p>",
            r"<p>Regex matches \$([0-9]+) as a currency capture.</p>",
        ]
        for snippet in escaped_snippets:
            culprits = ZeroTrustMicroAuditor.check_unrendered_latex(snippet)
            self.assertEqual(len(culprits), 0, f"False positive on escaped dollar: {culprits}")

            html_doc = self._wrap_html(snippet)
            report = self.auditor.audit_html_deliverable(html_doc, deliverable_id="escaped_dollar_leaf")
            latex_violations = [v for v in report.violations if v.rule_id == "HERM-006"]
            self.assertEqual(len(latex_violations), 0, f"False positive on escaped dollar: {latex_violations}")
            self.assertTrue(report.is_hermetic)

    # -------------------------------------------------------------------------
    # Vector 7: Valid Hermetic KaTeX Markup With Inline Scripts & Auto-Render
    # -------------------------------------------------------------------------
    def test_vector7_valid_hermetic_katex_with_autorender_accepted(self) -> None:
        """Verifies that valid hermetic KaTeX markup with auto-render is cleanly accepted."""
        head_katex = """
    <script>/* embedded hermetic KaTeX engine v0.16.8 */</script>
    <script>
        document.addEventListener("DOMContentLoaded", function() {
            renderMathInElement(document.body, {
                delimiters: [
                    {left: '$$', right: '$$', display: true},
                    {left: '\\(', right: '\\)', display: false}
                ]
            });
        });
    </script>
"""
        body_content = """
    <p>Thermodynamic bound: \\( \\Delta S = 0 \\)</p>
    <div>Display equation: $$ H(X) = -\\sum p(x) \\log p(x) $$</div>
    <div>Limit: \\( \\lim_{n \\to \\infty} \\frac{1}{n} = 0 \\)</div>
"""
        html_doc = self._wrap_html(body_content, head_inner=head_katex)
        culprits = ZeroTrustMicroAuditor.check_unrendered_latex(html_doc)
        self.assertEqual(len(culprits), 0, f"KaTeX with auto-render should have zero culprits, got {culprits}")

        report = self.auditor.audit_html_deliverable(html_doc, deliverable_id="valid_katex_deliverable")
        latex_violations = [v for v in report.violations if v.rule_id == "HERM-006"]
        self.assertEqual(len(latex_violations), 0)
        self.assertTrue(report.is_hermetic)


if __name__ == "__main__":
    unittest.main()
