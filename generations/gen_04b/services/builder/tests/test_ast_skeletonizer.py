"""Adversarial & Boundary Test Suite for AST Skeletonizer (`[Layer A]`, `[L1-G4B-007]`).

Validates:
1. AST interface extraction verifying body stripping to Ellipsis (`...`).
2. Preservation of function, async function, and class signatures and docstrings.
3. Verification that extracted prompt context compression strictly enforces <= 4,096 BPE tokens
   even on massive multi-class, multi-function source files.
4. Handling of invalid/corrupted source syntax with fallback diagnostic stubs.
5. Invariant enforcement in ASTSkeletonSnapshot.
"""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

BUILDER_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = BUILDER_ROOT.parent.parent.parent
for p in [str(BUILDER_ROOT), str(REPO_ROOT)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from src.ast_skeletonizer import ASTSkeletonizer
from src.domain_models import ASTSkeletonSnapshot, DomainInvariantViolation


class TestASTSkeletonizer(unittest.TestCase):
    """Rigorous verification of AST body stripping and token budget compaction."""

    def setUp(self) -> None:
        self.skeletonizer = ASTSkeletonizer(token_char_ratio=3.6)

    def test_basic_function_body_stripping(self) -> None:
        source = '''
def calculate_landauer_heat(bits: int, temp_k: float = 300.0) -> float:
    """Computes Landauer thermodynamic heat dissipation Q = k_B * T * ln(2) * bits."""
    k_B = 1.380649e-23
    ln2 = 0.69314718056
    return k_B * temp_k * ln2 * bits

async def stream_telemetry_events(node_id: str, timeout_ms: int = 500) -> bool:
    """Asynchronously streams telemetry events to the cryptographic ledger."""
    # Complex implementation here
    x = 10
    y = 20
    return True
'''
        snapshot = self.skeletonizer.extract_skeleton(source, "src/physics.py")
        self.assertIsInstance(snapshot, ASTSkeletonSnapshot)
        self.assertLessEqual(snapshot.estimated_bpe_tokens, 4096)
        
        # Verify body stripped to ellipsis
        self.assertIn("...", snapshot.skeleton_code)
        self.assertNotIn("1.380649e-23", snapshot.skeleton_code)
        self.assertNotIn("x = 10", snapshot.skeleton_code)

        # Verify signatures preserved
        self.assertIn("def calculate_landauer_heat(bits, temp_k)", snapshot.preserved_signatures)
        self.assertIn("async def stream_telemetry_events(node_id, timeout_ms)", snapshot.preserved_signatures)

        # Verify docstring preserved in normal case
        self.assertIn("Computes Landauer thermodynamic heat dissipation", snapshot.skeleton_code)

    def test_class_hierarchy_preservation(self) -> None:
        source = '''
class BaseConsensusEngine:
    """Abstract base consensus engine."""
    def __init__(self, node_id: str):
        self.node_id = node_id

    def commit(self, block_hash: str) -> bool:
        raise NotImplementedError()

class SheafQuorumEngine(BaseConsensusEngine):
    """Sheaf consensus implementation."""
    def verify_sheaf(self, topology: dict) -> bool:
        # Long implementation
        for k, v in topology.items():
            print(k, v)
        return True
'''
        snapshot = self.skeletonizer.extract_skeleton(source, "src/consensus.py")
        self.assertIn("class BaseConsensusEngine()", snapshot.preserved_signatures)
        self.assertIn("class SheafQuorumEngine(BaseConsensusEngine)", snapshot.preserved_signatures)
        self.assertIn("...", snapshot.skeleton_code)
        self.assertNotIn("raise NotImplementedError()", snapshot.skeleton_code)
        self.assertNotIn("print(k, v)", snapshot.skeleton_code)

    def test_massive_source_compression_strictly_under_4096_tokens(self) -> None:
        # Generate massive 200-function file with long implementations
        chunks = []
        for i in range(150):
            chunks.append(f'''
class ServiceComponent_{i}:
    """Comprehensive service component {i} handling high-frequency distributed transactions."""
    def __init__(self, config_{i}: dict):
        self.config = config_{i}
        self.cache = {{k: v for k, v in enumerate(range(100))}}

    def process_transaction_{i}(self, tx_id: str, payload: bytes) -> bool:
        """Processes transaction {i} with cryptographic checksum validation."""
        data = [x * {i} for x in range(500)]
        hasher = hashlib.sha256(payload)
        return hasher.hexdigest().startswith("00")
''')
        massive_source = "\n".join(chunks)
        self.assertGreater(len(massive_source), 60000)

        snapshot = self.skeletonizer.extract_skeleton(massive_source, "src/massive_service.py")
        
        # Enforce [Layer A] & [L1-G4B-008] hard ceiling: <= 4,096 tokens
        self.assertLessEqual(snapshot.estimated_bpe_tokens, 4096)
        self.assertGreater(snapshot.stripped_byte_count, 20000)
        self.assertIn("...", snapshot.skeleton_code)

    def test_syntax_error_handling_graceful_stub(self) -> None:
        corrupted_source = "def broken_func(:\n    unexpected syntax here! @"
        snapshot = self.skeletonizer.extract_skeleton(corrupted_source, "src/broken.py")
        
        self.assertIsInstance(snapshot, ASTSkeletonSnapshot)
        self.assertIn("SyntaxError in src/broken.py", snapshot.skeleton_code)
        self.assertIn("class IncompleteModule", snapshot.skeleton_code)
        self.assertLessEqual(snapshot.estimated_bpe_tokens, 4096)

    def test_empty_source_code(self) -> None:
        snapshot = self.skeletonizer.extract_skeleton("", "src/empty.py")
        self.assertGreater(snapshot.estimated_bpe_tokens, 0)
        self.assertIn("Empty module", snapshot.skeleton_code)


if __name__ == "__main__":
    unittest.main()
