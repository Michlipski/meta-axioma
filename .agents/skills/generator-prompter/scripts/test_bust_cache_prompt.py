#!/usr/bin/env python3
"""Unit tests for the bust_cache_prompt generator script."""

import unittest
from pathlib import Path
import sys

# Add scripts directory to sys.path
sys.path.insert(0, str(Path(__file__).parent))

from bust_cache_prompt import (
    PromptGenerationOptions,
    generate_cache_busting_prompt,
    generate_nonce_header,
    mutate_pitch_text,
    resolve_generator_invariants,
)


class TestBustCachePrompt(unittest.TestCase):

    def test_nonce_generation_uniqueness(self):
        nonce1 = generate_nonce_header(style="comment")
        nonce2 = generate_nonce_header(style="comment")
        self.assertNotEqual(nonce1, nonce2)
        self.assertIn("META_AXIOMA_NONCE", nonce1)
        self.assertIn("ENTROPY", nonce1)

    def test_nonce_styles(self):
        comment_style = generate_nonce_header(style="comment")
        self.assertTrue(comment_style.startswith("<!--"))

        tag_style = generate_nonce_header(style="tag")
        self.assertTrue(tag_style.startswith("[Session Dispatch Nonce"))

        header_style = generate_nonce_header(style="header")
        self.assertIn("Execution Vector", header_style)

    def test_pitch_mutation_preserves_semantics(self):
        original = "A category theory teaching application for early education inspired by Eugenia Cheng's success teaching category theory to arts students."
        mutated = mutate_pitch_text(original, mutation_level="moderate")
        # Should be mutated (different string)
        self.assertNotEqual(original, mutated)
        # Should retain key concepts like Cheng or arts or category theory
        self.assertTrue("Cheng" in mutated or "category" in mutated)

    def test_pitch_mutation_unknown_domain(self):
        original = "Xylophone zookeeper zebra."
        mutated = mutate_pitch_text(original, mutation_level="moderate")
        self.assertNotEqual(original, mutated)
        self.assertIn("zebra", mutated)

    def test_full_prompt_generation_g2b(self):
        opts = PromptGenerationOptions(
            generator="System G2b Compiler",
            pitch="A category theory teaching application for early education inspired by Eugenia Cheng's success teaching category theory to arts students.",
            mutation_level="moderate",
            include_invariants=True,
            include_execution_gate=True,
        )
        prompt = generate_cache_busting_prompt(opts)
        self.assertIn("System G2b Compiler", prompt)
        self.assertIn("Directive 3", prompt)
        self.assertIn("Multi-Tier Interlocking Gate", prompt)
        self.assertIn("ask_question", prompt)

    def test_full_prompt_generation_g1(self):
        opts = PromptGenerationOptions(
            generator="System G1 Compiler",
            pitch="A minimal task runner.",
            mutation_level="subtle",
        )
        prompt = generate_cache_busting_prompt(opts)
        self.assertIn("System G1 Compiler", prompt)
        self.assertIn("Functorial Undo/Redo", prompt)

    def test_deterministic_seed(self):
        opts1 = PromptGenerationOptions(seed=42)
        opts2 = PromptGenerationOptions(seed=42)
        prompt1 = generate_cache_busting_prompt(opts1)
        prompt2 = generate_cache_busting_prompt(opts2)
        # With identical seed, output should match
        self.assertEqual(prompt1, prompt2)


if __name__ == "__main__":
    unittest.main()
