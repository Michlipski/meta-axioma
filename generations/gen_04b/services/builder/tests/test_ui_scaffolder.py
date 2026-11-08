"""Empirical Test Suite for UI Scaffolder and Tactile Studio Primitives.

Enforces:
- [HERM-005]: Zero-CDN Hermeticity Invariant.
- [NEG-G1B-001]: Anti-Phantom Emission Gate.
- [L1-G3B-011]: Compositional Contract IR to Tactile UI Bijectivity.
- Coordinate Normalization & Clamping Proofs: Dragging to (-500, -500) or (9999, 9999) clamps strictly within bounding rectangle.
- Waterloo SYDE 361 Human Ergonomics (P_1): Hotkeys (Cmd+Z / Cmd+Y), narrative translation diffs.
"""

from __future__ import annotations

import os
from pathlib import Path
import re
import tempfile
import unittest

from generations.gen_04b.services.builder.src.ui_scaffolder import (
    HermeticityViolation,
    NarrativeHUDTemplate,
    StudioCSSTemplate,
    TactileCanvasTemplate,
    UIScaffolder,
    clamp_coordinates,
    format_narrative_diff,
    screen_to_spatial,
)
from generations.gen_04b.services.research.src.contract_ui import (
    ErgonomicsContract,
    LayoutArchetype,
    UIContractSpecification,
)


class TestUIScaffolder(unittest.TestCase):
    """Verifies end-to-end scaffolding, mathematical clamping, zero-CDN compliance, and ergonomics."""

    def setUp(self) -> None:
        self.scaffolder = UIScaffolder()
        self.default_contract = UIContractSpecification(
            archetype=LayoutArchetype.STUDIO_SPLIT_PANE,
            ergonomics=ErgonomicsContract(
                enable_undo_hotkeys=True,
                enable_escape_deselect=True,
                enable_space_playback=True,
                viewport_min_width=1024,
                viewport_min_height=600,
            ),
            workspace_title="Axioma Canvas Studio",
            narrative_context="Autonomous generative canvas for spatial statecharts.",
            inspector_fields=["id", "state", "entropy", "invariant_status"],
            timeline_event_types=["NODE_SPAWNED", "TRANSITION_FIRED", "CHECKPOINT_SEALED"],
        )

    # -------------------------------------------------------------------------
    # 1. Zero-CDN Compliance [HERM-005]
    # -------------------------------------------------------------------------
    def test_zero_cdn_compliance(self) -> None:
        """Verifies that emitted HTML, CSS, and JS contain zero external CDN or HTTP/HTTPS imports."""
        bundle = self.scaffolder.scaffold_studio(self.default_contract)

        external_pattern = re.compile(
            r"""(?:src|href)\s*=\s*['"]https?://[^'"]+['"]|@import\s+(?:url\(['"]?https?://|['"]https?://)""",
            re.IGNORECASE,
        )

        for filename, content in bundle.items():
            matches = external_pattern.findall(content)
            self.assertEqual(
                len(matches),
                0,
                f"File '{filename}' contains external CDN imports: {matches}",
            )

        # Assert no script tag points to remote hosts
        self.assertNotIn("https://cdn", bundle["index.html"])
        self.assertNotIn("http://cdn", bundle["index.html"])
        self.assertNotIn("unpkg.com", bundle["index.html"])
        self.assertNotIn("cdnjs.cloudflare.com", bundle["index.html"])

    def test_hermeticity_violation_rejection(self) -> None:
        """Verifies that UIScaffolder actively rejects bundles containing external links."""
        bad_bundle = {
            "index.html": '<script src="https://cdn.jsdelivr.net/npm/vue@3"></script>',
            "style.css": "body { margin: 0; }",
            "app.js": "console.log('hello');",
        }
        with self.assertRaises(HermeticityViolation):
            self.scaffolder._verify_zero_cdn_compliance(bad_bundle)

    # -------------------------------------------------------------------------
    # 2. Coordinate Clamping & Normalization Mathematical Proofs
    # -------------------------------------------------------------------------
    def test_coordinate_clamping_boundary_extremes(self) -> None:
        """Mathematically verifies that dragging to (-500, -500) or (9999, 9999) clamps within canvas."""
        canvas_w, canvas_h = 1000.0, 700.0
        node_w, node_h = 140.0, 60.0

        # Extreme negative coordinates: must clamp to (0, 0)
        clamped_neg_x, clamped_neg_y = clamp_coordinates(
            spatial_x=-500.0,
            spatial_y=-500.0,
            node_width=node_w,
            node_height=node_h,
            canvas_width=canvas_w,
            canvas_height=canvas_h,
        )
        self.assertEqual(clamped_neg_x, 0.0)
        self.assertEqual(clamped_neg_y, 0.0)

        # Extreme positive coordinates: must clamp to (canvas_w - node_w, canvas_h - node_h)
        clamped_pos_x, clamped_pos_y = clamp_coordinates(
            spatial_x=9999.0,
            spatial_y=9999.0,
            node_width=node_w,
            node_height=node_h,
            canvas_width=canvas_w,
            canvas_height=canvas_h,
        )
        self.assertEqual(clamped_pos_x, canvas_w - node_w)
        self.assertEqual(clamped_pos_y, canvas_h - node_h)
        self.assertEqual(clamped_pos_x, 860.0)
        self.assertEqual(clamped_pos_y, 640.0)

        # In-bounds coordinates: must remain untouched
        clamped_mid_x, clamped_mid_y = clamp_coordinates(
            spatial_x=250.0,
            spatial_y=150.0,
            node_width=node_w,
            node_height=node_h,
            canvas_width=canvas_w,
            canvas_height=canvas_h,
        )
        self.assertEqual(clamped_mid_x, 250.0)
        self.assertEqual(clamped_mid_y, 150.0)

    def test_coordinate_normalization_with_scale_and_offsets(self) -> None:
        """Verifies coordinate translation X_spatial = (X_screen - offset_X) / scale."""
        # Scale = 2.0 (zoomed in), Offset = (100, 50), Screen = (300, 250)
        # Spatial X = (300 - 100) / 2.0 = 100.0
        # Spatial Y = (250 - 50) / 2.0 = 100.0
        sp_x, sp_y = screen_to_spatial(
            screen_x=300.0,
            screen_y=250.0,
            offset_x=100.0,
            offset_y=50.0,
            scale=2.0,
        )
        self.assertAlmostEqual(sp_x, 100.0)
        self.assertAlmostEqual(sp_y, 100.0)

        # Scale = 0.5 (zoomed out), Offset = (0, 0), Screen = (200, 100)
        # Spatial X = 200 / 0.5 = 400.0
        # Spatial Y = 100 / 0.5 = 200.0
        sp_x2, sp_y2 = screen_to_spatial(
            screen_x=200.0,
            screen_y=100.0,
            offset_x=0.0,
            offset_y=0.0,
            scale=0.5,
        )
        self.assertAlmostEqual(sp_x2, 400.0)
        self.assertAlmostEqual(sp_y2, 200.0)

    # -------------------------------------------------------------------------
    # 3. Human Ergonomics & Hotkey Handlers Verification
    # -------------------------------------------------------------------------
    def test_hotkey_handlers_in_emitted_js(self) -> None:
        """Verifies that keydown listeners handle Cmd+Z, Cmd+Y, Escape, and Space."""
        bundle = self.scaffolder.scaffold_studio(self.default_contract)
        js = bundle["app.js"]

        # Check keydown listener attached
        self.assertIn("window.addEventListener('keydown'", js)

        # Check Undo/Redo conditions (metaKey / ctrlKey + z / y)
        self.assertIn("(e.metaKey || e.ctrlKey)", js)
        self.assertIn("e.key === 'z' || e.key === 'Z'", js)
        self.assertIn("e.key === 'y' || e.key === 'Y'", js)
        self.assertIn("executeUndo()", js)
        self.assertIn("executeRedo()", js)

        # Check Escape deselect
        self.assertIn("e.key === 'Escape'", js)
        self.assertIn("deselectAll()", js)

        # Check Space playback toggle
        self.assertIn("e.key === ' ' || e.code === 'Space'", js)
        self.assertIn("togglePlayback()", js)

    def test_ergonomics_disabled_switches(self) -> None:
        """Verifies that disabling ergonomics flags removes/disables corresponding hotkey branches."""
        custom_contract = UIContractSpecification(
            archetype=LayoutArchetype.STUDIO_SPLIT_PANE,
            ergonomics=ErgonomicsContract(
                enable_undo_hotkeys=False,
                enable_escape_deselect=False,
                enable_space_playback=False,
            ),
            workspace_title="Restricted Studio",
            narrative_context="Disabled hotkeys contract.",
        )
        bundle = self.scaffolder.scaffold_studio(custom_contract)
        js = bundle["app.js"]

        # Disabled flags should render as 'false' in conditionals
        self.assertIn("const isUndo = false", js)
        self.assertIn("if (false && e.key === 'Escape')", js)
        self.assertIn("if (false && (e.key === ' '", js)

    # -------------------------------------------------------------------------
    # 4. Narrative HUD Diff Translation
    # -------------------------------------------------------------------------
    def test_narrative_hud_diff_translation(self) -> None:
        """Verifies that state diffs ΔS = S_{t+1} - S_t translate into human-centered plain English."""
        # 1. Node Addition Diff
        diff_add = {"added": ["Queen Lifeline", "Bloodroot"]}
        narrative_1 = format_narrative_diff(diff_add, action_name="Planting Action")
        self.assertIn("Executed Planting Action.", narrative_1)
        self.assertIn("Added 2 entity/nodes", narrative_1)
        self.assertIn("Queen Lifeline", narrative_1)

        # 2. Property Update Diff
        diff_mod = {"modified": {"nectar_level": "Optimal", "drought_risk": "Eliminated"}}
        narrative_2 = format_narrative_diff(diff_mod, action_name="Eco Equilibrium")
        self.assertIn("Executed Eco Equilibrium.", narrative_2)
        self.assertIn("nectar_level -> Optimal", narrative_2)

        # 3. Empty Diff (Equilibrium)
        narrative_3 = format_narrative_diff({}, action_name="Validation Probe")
        self.assertIn("System state steady", narrative_3)

    # -------------------------------------------------------------------------
    # 5. Layout Archetypes & Inspector Data-Binding
    # -------------------------------------------------------------------------
    def test_layout_archetypes_rendering(self) -> None:
        """Verifies rendering across STUDIO_SPLIT_PANE, REACTIVE_GRID, and TIMELINE_CONSOLE."""
        for archetype in [
            LayoutArchetype.STUDIO_SPLIT_PANE,
            LayoutArchetype.REACTIVE_GRID,
            LayoutArchetype.TIMELINE_CONSOLE,
        ]:
            contract = UIContractSpecification(
                archetype=archetype,
                ergonomics=ErgonomicsContract(),
                workspace_title=f"Test {archetype.value}",
                narrative_context=f"Context for {archetype.value}",
                inspector_fields=["fieldA", "fieldB"],
            )
            bundle = self.scaffolder.scaffold_studio(contract)

            # Assert archetype appears in html body class and title
            expected_class = f"archetype-{archetype.value.lower().replace('_', '-')}"
            self.assertIn(expected_class, bundle["index.html"])
            self.assertIn(archetype.value, bundle["index.html"])

            # Assert CSS contains responsive tokens and grid
            self.assertIn("--bg-base: #0a0d14;", bundle["style.css"])
            self.assertIn(".studio-container", bundle["style.css"])

    def test_inspector_field_data_binding(self) -> None:
        """Verifies that all inspector fields specified in contract appear as DOM targets."""
        contract = UIContractSpecification(
            archetype=LayoutArchetype.STUDIO_SPLIT_PANE,
            ergonomics=ErgonomicsContract(),
            workspace_title="Field Binding Test",
            narrative_context="Testing fields.",
            inspector_fields=["entropy_score", "shannon_index", "z3_sat_proof"],
        )
        bundle = self.scaffolder.scaffold_studio(contract)
        html_code = bundle["index.html"]

        self.assertIn('id="field-entropy_score"', html_code)
        self.assertIn('id="field-shannon_index"', html_code)
        self.assertIn('id="field-z3_sat_proof"', html_code)
        self.assertIn("ENTROPY_SCORE", html_code.upper())

    # -------------------------------------------------------------------------
    # 6. Physical Disk Grounding [NEG-G1B-001]
    # -------------------------------------------------------------------------
    def test_physical_emission_to_disk(self) -> None:
        """Verifies scaffold_to_dir creates real, non-empty files on disk."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            emitted = self.scaffolder.scaffold_to_dir(self.default_contract, tmp_dir)

            self.assertEqual(len(emitted), 3)
            self.assertIn("index.html", emitted)
            self.assertIn("style.css", emitted)
            self.assertIn("app.js", emitted)

            for filename, file_path in emitted.items():
                self.assertTrue(file_path.exists())
                self.assertGreater(file_path.stat().st_size, 0)

            # Verify index.html content on disk
            html_disk = emitted["index.html"].read_text(encoding="utf-8")
            self.assertIn("Axioma Canvas Studio", html_disk)
            self.assertIn("STUDIO_SPLIT_PANE", html_disk)


if __name__ == "__main__":
    unittest.main()
