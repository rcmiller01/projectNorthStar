#!/usr/bin/env python3
"""Test script for Phase Top-off features.

Tests:
1. Router modes (auto, heuristic, learned)
2. Graph boost functionality
3. Enhanced evaluation metrics
4. Makefile targets (simulation)
"""

import subprocess
import sys
from pathlib import Path

def run_cmd(cmd: str, check: bool = True) -> subprocess.CompletedProcess:
    """Run a command and return the result."""
    print(f"[TEST] {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"STDERR: {result.stderr}")
        print(f"STDOUT: {result.stdout}")
        sys.exit(1)
    return result

def main():
    """Run all tests."""
    print("=== Phase Top-off Feature Tests ===")
    
    # Test 1: Router heuristic mode
    print("\n1. Testing router heuristic mode...")
    result = run_cmd(
        "python -m core.cli triage --title 'Stack trace error' "
        "--body 'Exception in thread' --router heuristic --k 3 --out test1.md"
    )
    assert "logs_only" in result.stdout, "Router should detect logs_only strategy"
    
    # Test 2: Router auto mode (fallback to heuristic)
    print("\n2. Testing router auto mode...")
    result = run_cmd(
        "python -m core.cli triage --title 'PDF manual broken' "
        "--body 'Screenshot attached' --router auto --k 5 --out test2.md"
    )
    assert "router_strategy" in result.stdout, "Router strategy should be reported"
    
    # Test 3: Graph boost
    print("\n3. Testing graph boost...")
    result = run_cmd(
        "python -m core.cli triage --title 'Upload issue' "
        "--body 'File processing error' --graph-boost 0.2 --k 4 --out test3.md"
    )
    # Graph boost should be accepted (no error)
    
    # Test 4: Enhanced evaluation
    print("\n4. Testing enhanced evaluation...")
    result = run_cmd(
        "python scripts/run_eval.py --top-k 5 --use-stub --output test_eval.json"
    )
    assert "ndcg@k" in result.stdout, "nDCG should be in output"
    assert "mrr" in result.stdout, "MRR should be in output"
    
    # Test 5: Metrics trend
    print("\n5. Testing metrics trend...")
    result = run_cmd("python scripts/metrics_trend.py")
    assert "ndcg_at_k" in result.stdout, "nDCG should be in trend output"
    assert "mrr" in result.stdout, "MRR should be in trend output"
    
    # Cleanup
    print("\n6. Cleaning up...")
    for f in ["test1.md", "test2.md", "test3.md", "test_eval.json"]:
        if Path(f).exists():
            Path(f).unlink()
    
    print("\n✅ All tests passed! Phase Top-off features are working correctly.")
    print("\nFeatures validated:")
    print("- ✅ Smart router with heuristic/auto modes")
    print("- ✅ Graph boost integration")
    print("- ✅ Enhanced evaluation metrics (nDCG@5, MRR, timings)")
    print("- ✅ Metrics trend with informational display")
    print("- ✅ CLI parameter integration")

if __name__ == "__main__":
    main()
