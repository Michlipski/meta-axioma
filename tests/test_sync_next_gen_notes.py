"""Unit and Subprocess Test Suite for G5 Succession Note Synchronization (`scripts/sync_next_gen_notes.py`).

Validates:
1. Subprocess CLI execution with clean exit code 0 ([NEG-G1B-002]).
2. Extraction from proposal with embedded `json:g5_succession_note` block.
3. Fallback heuristic extraction from deferred scope and adversarial risk.
4. Schema validation and path traversal defenses.
5. Splicing into existing files with idempotent in-place update.
6. Standalone RFC creation from template and atomic README.md indexing.
7. `--dry-run` output preview without disk mutation.
8. `--undo` snapshot restoration restoring bit-for-bit original state.
9. `--check` verification mode.
"""

from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

REPO_ROOT = Path(__file__).resolve().parent.parent
SYNC_SCRIPT = REPO_ROOT / "scripts" / "sync_next_gen_notes.py"

# Add scripts directory to path for unit tests
sys.path.insert(0, str(REPO_ROOT / "scripts"))
import sync_next_gen_notes as syncer


SAMPLE_PROPOSAL_WITH_JSON = """# Axioma Test Proposals
## Detailed Dynamic Project Proposals Dossier (`project_proposals.md`)

---

### Option 1: Lightweight CLI Script (RECOMMENDED)

#### A. Target Persona & JTBD Fit
Compiler Architect.

#### B. Token Budget
- Total Unified BPE Tokens: 40,000

#### D. Included Scope
- CLI utility and unit tests.

#### E. Deliberately Deferred / Cut Scope
- Cut distributed WireGuard mesh.

#### G. Adversarial Risk & Red Team Critique
- Attack Vector: Single host bottleneck.

```json:g5_succession_note
{
  "note_id": "g5-research-socratic-council",
  "source_proposal_option": "Option 1: Lightweight CLI Script",
  "scope_type": "service",
  "target_relative_path": "services/research.md",
  "target_service": "research",
  "title": "Autonomous Socratic Research Council",
  "friction_summary": [
    "Synchronous single-agent research bottleneck in Gen 4b",
    "Static invariant checking lacks dynamic lemma synthesis"
  ],
  "desired_capabilities": [
    "Autonomous Socratic debate between Thesis, Antithesis, and Synthesis agents",
    "Decentralized literature grounding"
  ],
  "proposed_invariants": [
    "[L1-G5-RES-001] Multi-agent Nash equilibrium quorum before RFC emission",
    "[NEG-G5-RES-001] Prohibition on monolithic un-critiqued research deliverables"
  ],
  "research_spikes": [
    "Evaluate SMT solver integration inside dialectical debate loops"
  ]
}
```

---

### Option 2: Full Distributed Engine

#### A. Target Persona
Distributed engineer.

#### E. Deliberately Deferred / Cut Scope
- Cut eBPF probe telemetry.
"""

SAMPLE_PROPOSAL_HEURISTIC_ONLY = """# Axioma Test Proposals
## Detailed Dynamic Project Proposals Dossier

---

### Option 1: Minimal Headless Runner

#### A. Target Persona & JTBD Fit
Systems Architect.

#### E. Deliberately Deferred / Cut Scope
- Cut distributed telemetry mesh event streaming.
- Cut real-time Landauer heat gauge meters.
- Technical Rationale: Too complex for Gen 4b single-workstation architecture.

#### G. Adversarial Risk & Red Team Critique
- Attack Vector: Local single-machine socket saturation under high-frequency events.
- Dialectical Negative Constraint: [NEG-G5-TEL-001] Avoid centralized telemetry proxy bottlenecks.
"""

SAMPLE_EXISTING_RESEARCH_MD = """# Generation 5 Sovereign Research Service Dossier (`services/research.md`)

> **Enclave Target:** `services/research/` (192.168.40.10)  
> **Status:** Active Evolution Notes  

---

## 1. Context & Generation 4b Baseline
Baseline research services.

---

## 2. Generation 4b Friction Points & Limitations
- Existing friction 1.

---

## 3. Generation 5 Desired Capabilities & Aspirations
- Existing capability 1.

---

## 4. Formal Invariants & Negative Constraints
- Existing invariant 1.

---

## 6. Open Questions & Research Spikes
- Existing spike 1.
"""

SAMPLE_README_MD = """# Generation 5 ($G_5$) Successor Charter & Generational Planning Hub (`next_gen/`)

## 3. Quick Links & Reading Order

### Generational Level (Cross-Cutting Architecture)
1. **[Audit Triage & Generational Streams](general/audit_triage_and_next_steps.md)**: Master triage.
2. **[Core Thesis & Paradigm Shifts](general/thesis_and_paradigm.md)**: Paradigm shifts.

### Per-Service Level (Specialized Evolution)
- **[Research Service Evolution](services/research.md)**: Research notes.
"""


class TestSyncNextGenNotes(unittest.TestCase):
    """Unit and functional tests for sync_next_gen_notes.py."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.mkdtemp(prefix="test_next_gen_sync_")
        self.temp_path = Path(self.temp_dir)
        self.next_gen_dir = self.temp_path / "generations" / "gen_04b" / "next_gen"
        self.next_gen_dir.mkdir(parents=True, exist_ok=True)
        (self.next_gen_dir / "services").mkdir(parents=True, exist_ok=True)
        (self.next_gen_dir / "general").mkdir(parents=True, exist_ok=True)
        (self.next_gen_dir / "templates").mkdir(parents=True, exist_ok=True)

        # Copy evolution_note_template.md
        tmpl_src = REPO_ROOT / "generations" / "gen_04b" / "next_gen" / "templates" / "evolution_note_template.md"
        if tmpl_src.exists():
            shutil.copy2(tmpl_src, self.next_gen_dir / "templates" / "evolution_note_template.md")
        else:
            (self.next_gen_dir / "templates" / "evolution_note_template.md").write_text(
                "# [Topic / Service / Feature Name] Evolution Note (`evolution_note_template.md`)\n\n"
                "## 2. Friction Points & Architectural Limitations\n...\n"
                "## 3. Generation 5 Desired Capabilities & Specification\n...\n"
                "## 4. Formal Invariants & Negative Constraints\n...\n"
                "## 6. Open Questions & Research Spikes\n...\n",
                encoding="utf-8",
            )

        # Write sample research.md and README.md
        (self.next_gen_dir / "services" / "research.md").write_text(
            SAMPLE_EXISTING_RESEARCH_MD, encoding="utf-8"
        )
        (self.next_gen_dir / "README.md").write_text(
            SAMPLE_README_MD, encoding="utf-8"
        )

        # Write sample proposals
        self.proposal_with_json = self.temp_path / "proposals_json.md"
        self.proposal_with_json.write_text(SAMPLE_PROPOSAL_WITH_JSON, encoding="utf-8")

        self.proposal_heuristic = self.temp_path / "proposals_heuristic.md"
        self.proposal_heuristic.write_text(SAMPLE_PROPOSAL_HEURISTIC_ONLY, encoding="utf-8")

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_json_block_extraction(self) -> None:
        """Verifies deterministic parsing of embedded json:g5_succession_note block."""
        options = syncer.parse_proposal_options(SAMPLE_PROPOSAL_WITH_JSON)
        self.assertEqual(len(options), 2)
        opt_key, opt_title, opt_body = options[0]
        self.assertEqual(opt_key, "1")
        self.assertIn("Lightweight CLI", opt_title)

        note = syncer.extract_note_from_option(opt_key, opt_title, opt_body)
        self.assertIsNotNone(note)
        self.assertEqual(note.note_id, "g5-research-socratic-council")
        self.assertEqual(note.target_service, "research")
        self.assertEqual(note.target_relative_path, "services/research.md")
        self.assertEqual(len(note.friction_summary), 2)
        self.assertEqual(len(note.desired_capabilities), 2)
        self.assertEqual(len(note.proposed_invariants), 2)
        self.assertEqual(len(note.research_spikes), 1)

        errs = note.validate()
        self.assertEqual(errs, [])

    def test_heuristic_fallback_extraction(self) -> None:
        """Verifies fallback heuristic parsing from Deferred Scope and Adversarial Risk."""
        options = syncer.parse_proposal_options(SAMPLE_PROPOSAL_HEURISTIC_ONLY)
        self.assertEqual(len(options), 1)
        opt_key, opt_title, opt_body = options[0]

        note = syncer.extract_note_from_option(opt_key, opt_title, opt_body)
        self.assertIsNotNone(note)
        self.assertTrue(note.note_id.startswith("g5-"))
        self.assertIn("Option 1", note.source_proposal_option)
        self.assertGreater(len(note.friction_summary), 0)
        self.assertGreater(len(note.desired_capabilities), 0)
        self.assertIn("[NEG-G5-TEL-001]", note.proposed_invariants)

        errs = note.validate()
        self.assertEqual(errs, [])

    def test_schema_validation_defenses(self) -> None:
        """Verifies path traversal detection and empty field rejection."""
        bad_note = syncer.G5SuccessionNote(
            note_id="bad/note/id",
            source_proposal_option="Option 1",
            scope_type="general",
            target_relative_path="../escaping_path.md",
            target_service="general",
            title="Bad Note",
        )
        errs = bad_note.validate()
        self.assertTrue(any("Invalid 'note_id' format" in e for e in errs))
        self.assertTrue(any("Path traversal detected" in e for e in errs))
        self.assertTrue(any("At least one of 'friction_summary'" in e for e in errs))

    def test_splicing_into_existing_file_and_idempotency(self) -> None:
        """Verifies comment-guarded insertion and in-place idempotent update."""
        target_file = self.next_gen_dir / "services" / "research.md"
        template_file = self.next_gen_dir / "templates" / "evolution_note_template.md"

        note = syncer.G5SuccessionNote(
            note_id="g5-test-sync",
            source_proposal_option="Option 1",
            scope_type="service",
            target_relative_path="services/research.md",
            target_service="research",
            title="Test Socratic Research",
            friction_summary=["Friction Alpha"],
            desired_capabilities=["Capability Beta"],
            proposed_invariants=["[L1-G5-TEST-001] Test Invariant"],
            research_spikes=["Spike Gamma"],
        )

        # 1. First sync insertion
        orig, new_content, is_new = syncer.splice_into_target(target_file, note, template_file)
        self.assertFalse(is_new)
        self.assertIn("<!-- BEGIN G5_SYNC: g5-test-sync -->", new_content)
        self.assertIn("<!-- END G5_SYNC: g5-test-sync -->", new_content)
        self.assertIn("Friction Alpha", new_content)

        # Physically write file
        target_file.write_text(new_content, encoding="utf-8")

        # 2. Second sync with updated content (same note_id)
        note.friction_summary = ["Friction Alpha Updated", "Friction Second"]
        orig2, new_content2, is_new2 = syncer.splice_into_target(target_file, note, template_file)
        self.assertFalse(is_new2)

        # Verify only ONE begin guard exists (idempotent in-place update)
        self.assertEqual(new_content2.count("<!-- BEGIN G5_SYNC: g5-test-sync -->"), 1)
        self.assertEqual(new_content2.count("<!-- END G5_SYNC: g5-test-sync -->"), 1)
        self.assertIn("Friction Alpha Updated", new_content2)
        self.assertIn("Friction Second", new_content2)

    def test_new_standalone_rfc_and_readme_indexing(self) -> None:
        """Verifies template instantiation for new RFC and atomic README.md indexing."""
        target_file = self.next_gen_dir / "general" / "test_kernel_ebpf.md"
        template_file = self.next_gen_dir / "templates" / "evolution_note_template.md"
        readme_file = self.next_gen_dir / "README.md"

        note = syncer.G5SuccessionNote(
            note_id="g5-ebpf-probes",
            source_proposal_option="Option 1",
            scope_type="general",
            target_relative_path="general/test_kernel_ebpf.md",
            target_service="general",
            title="Kernel eBPF Probes",
            friction_summary=["In-memory mocks hide true socket latency"],
            desired_capabilities=["Kernel-level eBPF packet trace capture"],
            proposed_invariants=["[L1-G5-EBPF-001] Zero userspace probe bypass"],
            research_spikes=["Evaluate Linux eBPF vs macOS dtrace"],
        )

        orig, new_content, is_new = syncer.splice_into_target(target_file, note, template_file)
        self.assertTrue(is_new)
        self.assertIn("Kernel eBPF Probes", new_content)
        self.assertIn("<!-- BEGIN G5_SYNC: g5-ebpf-probes -->", new_content)
        target_file.write_text(new_content, encoding="utf-8")

        # Update README
        orig_readme, new_readme, updated = syncer.update_readme_index(readme_file, note)
        self.assertTrue(updated)
        self.assertIn("3. **[Kernel eBPF Probes](general/test_kernel_ebpf.md)**:", new_readme)

        # Re-run index update; must be idempotent
        readme_file.write_text(new_readme, encoding="utf-8")
        _, new_readme2, updated2 = syncer.update_readme_index(readme_file, note)
        self.assertFalse(updated2)

    def test_dry_run_flag_preserves_disk(self) -> None:
        """Verifies that --dry-run prints preview diff without writing any files."""
        res = subprocess.run(
            [
                sys.executable,
                str(SYNC_SCRIPT),
                "--proposals-file",
                str(self.proposal_with_json),
                "--next-gen-dir",
                str(self.next_gen_dir),
                "--dry-run",
            ],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        )
        self.assertEqual(res.returncode, 0)
        self.assertIn("[DRY-RUN] Preview Changes", res.stdout)
        self.assertIn("<!-- BEGIN G5_SYNC: g5-research-socratic-council -->", res.stdout)

        # Assert target file was NOT modified
        content = (self.next_gen_dir / "services" / "research.md").read_text(encoding="utf-8")
        self.assertNotIn("<!-- BEGIN G5_SYNC:", content)

    def test_cli_sync_and_undo_rollback(self) -> None:
        """Verifies live sync writes disk files and --undo restores bit-for-bit pre-sync state."""
        target_file = self.next_gen_dir / "services" / "research.md"
        original_bytes = target_file.read_bytes()
        snap_dir = self.temp_path / "undo_snapshots"

        # Execute live sync
        res_sync = subprocess.run(
            [
                sys.executable,
                str(SYNC_SCRIPT),
                "--proposals-file",
                str(self.proposal_with_json),
                "--next-gen-dir",
                str(self.next_gen_dir),
                "--snapshot-dir",
                str(snap_dir),
                "--option",
                "1",
                "--yes",
            ],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        )
        self.assertEqual(res_sync.returncode, 0, f"Sync stderr: {res_sync.stderr}")
        self.assertIn("[SUCCESS]", res_sync.stdout)

        # Confirm target file is modified
        modified_bytes = target_file.read_bytes()
        self.assertNotEqual(original_bytes, modified_bytes)
        self.assertIn(b"<!-- BEGIN G5_SYNC: g5-research-socratic-council -->", modified_bytes)

        # Execute --undo
        res_undo = subprocess.run(
            [
                sys.executable,
                str(SYNC_SCRIPT),
                "--snapshot-dir",
                str(snap_dir),
                "--undo",
            ],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        )
        self.assertEqual(res_undo.returncode, 0, f"Undo stderr: {res_undo.stderr}")
        self.assertIn("[UNDO] Synchronization rollback complete.", res_undo.stdout)

        # Confirm exact bit-for-bit restoration
        restored_bytes = target_file.read_bytes()
        self.assertEqual(original_bytes, restored_bytes)

    def test_check_flag(self) -> None:
        """Verifies --check validates proposals and exits with appropriate codes."""
        # Valid proposal
        res_ok = subprocess.run(
            [
                sys.executable,
                str(SYNC_SCRIPT),
                "--proposals-file",
                str(self.proposal_with_json),
                "--check",
            ],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        )
        self.assertEqual(res_ok.returncode, 0)
        self.assertIn("[PASS]", res_ok.stdout)

        # Invalid proposal with broken json
        bad_prop = self.temp_path / "bad_proposals.md"
        bad_prop.write_text(
            "### Option 1: Broken Option\n"
            "```json:g5_succession_note\n"
            "{\"note_id\": \"\", \"title\": \"\"}\n"
            "```\n",
            encoding="utf-8",
        )
        res_bad = subprocess.run(
            [
                sys.executable,
                str(SYNC_SCRIPT),
                "--proposals-file",
                str(bad_prop),
                "--check",
            ],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        )
        self.assertEqual(res_bad.returncode, 1)
        self.assertIn("[FAIL]", res_bad.stdout)


    def test_cli_smoke_help(self) -> None:
        """Verifies that python3 scripts/sync_next_gen_notes.py --help executes cleanly ([NEG-G1B-002])."""
        res = subprocess.run(
            [sys.executable, str(SYNC_SCRIPT), "--help"],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        )
        self.assertEqual(res.returncode, 0)
        self.assertIn("--proposals-file", res.stdout)
        self.assertIn("--dry-run", res.stdout)
        self.assertIn("--undo", res.stdout)
        self.assertIn("--check", res.stdout)

    def test_cli_new_rfc_and_undo_rollback(self) -> None:
        """Verifies that creating a new RFC and updating README is fully reversible via --undo."""
        target_rfc = self.next_gen_dir / "general" / "test_reverse_rfc.md"
        readme_file = self.next_gen_dir / "README.md"
        readme_orig_bytes = readme_file.read_bytes()
        snap_dir = self.temp_path / "undo_snapshots_rfc"

        prop_file = self.temp_path / "proposal_new_rfc.md"
        prop_file.write_text(
            "### Option 1: Novel Service\n"
            "```json:g5_succession_note\n"
            "{\n"
            "  \"note_id\": \"g5-reverse-rfc\",\n"
            "  \"source_proposal_option\": \"Option 1: Novel Service\",\n"
            "  \"scope_type\": \"general\",\n"
            "  \"target_relative_path\": \"general/test_reverse_rfc.md\",\n"
            "  \"target_service\": \"general\",\n"
            "  \"title\": \"Reverse RFC Architecture\",\n"
            "  \"friction_summary\": [\"Friction A\"],\n"
            "  \"desired_capabilities\": [\"Capability B\"]\n"
            "}\n"
            "```\n",
            encoding="utf-8",
        )

        # 1. Live Sync creating new file & updating README
        res_sync = subprocess.run(
            [
                sys.executable,
                str(SYNC_SCRIPT),
                "--proposals-file",
                str(prop_file),
                "--next-gen-dir",
                str(self.next_gen_dir),
                "--snapshot-dir",
                str(snap_dir),
                "--yes",
            ],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        )
        self.assertEqual(res_sync.returncode, 0)
        self.assertTrue(target_rfc.exists())
        self.assertIn(b"test_reverse_rfc.md", readme_file.read_bytes())

        # 2. Undo rollback
        res_undo = subprocess.run(
            [
                sys.executable,
                str(SYNC_SCRIPT),
                "--snapshot-dir",
                str(snap_dir),
                "--undo",
            ],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        )
        self.assertEqual(res_undo.returncode, 0)
        # RFC file must be deleted
        self.assertFalse(target_rfc.exists())
        # README must be restored bit-for-bit
        self.assertEqual(readme_orig_bytes, readme_file.read_bytes())


if __name__ == "__main__":
    unittest.main()
