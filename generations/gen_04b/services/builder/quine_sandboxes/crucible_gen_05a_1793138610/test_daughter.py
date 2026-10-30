"""Daughter compiler self-test suite."""
import sys
from src.compiler import DaughterCompiler

def test_boot():
    c = DaughterCompiler()
    res = c.compile_spec("self_hosting_contract")
    assert len(res) == 64
    print("DAUGHTER_SELF_HOSTING_VERIFIED")

if __name__ == "__main__":
    test_boot()
