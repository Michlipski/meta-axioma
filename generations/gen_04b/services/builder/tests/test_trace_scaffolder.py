"""Empirical Test Suite for TraceScaffolder and TraceProtocolEmitter.

Enforces:
- [INV-G4B-TRACE-001]: TRACE-AST Bijectivity & Declarative Conformance.
- [NEG-G1B-001]: Anti-Phantom Emission Gate.
"""

from __future__ import annotations

import ast
from pathlib import Path
import tempfile
import unittest

from generations.gen_04b.services.audit.src.trace_bijective_auditor import TraceBijectiveAuditor
from generations.gen_04b.services.builder.src.trace_scaffolder import TraceScaffolder
from generations.gen_04b.services.research.src.trace_protocol_emitter import TraceProtocolEmitter


class TestTraceScaffolderAndEmitter(unittest.TestCase):
    """Verifies end-to-end pipeline from research emission to builder scaffolding and audit."""

    def test_pipeline_round_trip(self) -> None:
        """Emits a domain spec via research emitter, scaffolds via builder, and audits via micro-auditor."""
        emitter = TraceProtocolEmitter()
        scaffolder = TraceScaffolder()
        auditor = TraceBijectiveAuditor()

        domain_md = emitter.emit_domain(
            domain_name="TelemetryStream",
            related_domains=["TelemetryAudit"],
            constraints=["Monotonic event timestamps required."],
            glossary={"LogRecord": "A single immutable log entry."},
            entities={
                "LogRecord": {
                    "fields": [
                        {"name": "record_id", "type": "String"},
                        {"name": "timestamp_epoch", "type": "Integer"},
                        {"name": "message", "type": "String"},
                    ],
                    "rules": ["R1: timestamp_epoch > 0."],
                },
                "StreamMetrics": {
                    "fields": [
                        {"name": "stream_id", "type": "String"},
                        {"name": "total_records", "type": "Integer"},
                        {"name": "error_count", "type": "Integer"},
                    ],
                    "rules": ["R1: error_count <= total_records."],
                },
            },
            events={},
        )

        overview_md = emitter.emit_overview(
            app_id="axioma_logstream",
            name="Axioma LogStream",
            generation="gen_04b",
            port=8099,
            tagline="High-throughput stream engine.",
            key_capabilities=["Telemetry ingest: Sub-millisecond write latency."],
            glossary={"Stream": "Ordered event sequence."},
        )

        trace_bundle = {
            "overview.md": overview_md,
            "domains/telemetry_stream.domain.md": domain_md,
        }

        with tempfile.TemporaryDirectory() as tmp_dir:
            result = scaffolder.scaffold_app_from_trace(
                app_id="axioma_logstream",
                generation="gen_04b",
                port=8099,
                target_dir=tmp_dir,
                trace_bundle=trace_bundle,
            )

            self.assertEqual(result.app_id, "axioma_logstream")
            self.assertIn("src/domain_models.py", result.files_created)
            self.assertEqual(set(result.entities_scaffolded), {"LogRecord", "StreamMetrics"})

            # Verify bijectivity with TraceBijectiveAuditor
            py_code = (Path(tmp_dir) / "src" / "domain_models.py").read_text(encoding="utf-8")
            audit_report = auditor.audit_bijectivity(domain_md, py_code, "axioma_logstream")
            self.assertTrue(audit_report.is_bijective, f"Audit failed: {audit_report.violations}")


if __name__ == "__main__":
    unittest.main()
