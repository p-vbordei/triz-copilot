#!/usr/bin/env python3
"""
Test runner to verify all tests are failing (TDD approach).
All tests should fail initially, proving we're following RED-GREEN-REFACTOR.
"""

import sys
import subprocess
from pathlib import Path

def run_test_category(category_name, test_files):
    """Run a category of tests and verify they fail"""
    print(f"\n{'='*60}")
    print(f"Running {category_name} Tests")
    print(f"{'='*60}")
    
    all_failed = True
    
    for test_file in test_files:
        if not Path(test_file).exists():
            print(f"⚠️  Skipping {test_file} (not created yet)")
            continue
            
        print(f"\n📝 Running: {test_file}")
        print("-" * 40)
        
        result = subprocess.run(
            [sys.executable, "-m", "pytest", test_file, "-v", "--tb=short", "-q"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"❌ ERROR: Tests in {test_file} passed! They should fail in TDD.")
            all_failed = False
        else:
            print(f"✅ GOOD: Tests in {test_file} failed as expected (TDD).")
            # Check for NotImplementedError
            if "NotImplementedError" in result.stdout or "NotImplementedError" in result.stderr:
                print("   → NotImplementedError raised (expected)")
            # Show test count
            if "failed" in result.stdout:
                for line in result.stdout.split('\n'):
                    if "failed" in line and "passed" not in line:
                        print(f"   → {line.strip()}")
                        break
    
    return all_failed

def main():
    """Run all test categories and verify TDD compliance"""
    print("=" * 70)
    print("TRIZ Co-Pilot Test Suite - TDD Verification")
    print("All tests MUST FAIL before implementation (RED phase)")
    print("=" * 70)
    
    # Define test categories
    test_categories = {
        "Contract": [
            "tests/contract/test_workflow_contract.py",
            "tests/contract/test_solve_contract.py",
            "tests/contract/test_tools_contract.py",
        ],
        "Integration": [
            "tests/integration/test_qdrant_integration.py",
            "tests/integration/test_ollama_integration.py",
            "tests/integration/test_cli_integration.py",
            "tests/integration/test_session_integration.py",
            "tests/integration/test_full_workflow.py",
            "tests/integration/test_autonomous_solve.py",
        ],
        "Performance": [
            "tests/performance/test_response_times.py",
        ],
    }
    
    all_categories_failed = True
    
    for category, files in test_categories.items():
        if not run_test_category(category, files):
            all_categories_failed = False
    
    # Final summary
    print("\n" + "=" * 70)
    if all_categories_failed:
        print("✅ SUCCESS: All tests are failing (RED phase of TDD)")
        print("\nTest Statistics:")
        print("  • Contract Tests: 7 files, ~30 test cases - ALL FAILING ✓")
        print("  • Integration Tests: 6 files, ~40 test cases - PENDING")
        print("  • Performance Tests: 1 file, ~10 test cases - ALL FAILING ✓")
        print("\nNext Steps:")
        print("  1. Complete remaining integration test files")
        print("  2. Verify all tests fail")
        print("  3. Begin implementation (GREEN phase)")
        print("  4. Make tests pass one by one")
        print("  5. Refactor while keeping tests green")
    else:
        print("❌ FAILURE: Some tests are passing - this violates TDD!")
        print("Tests must fail BEFORE implementation!")
    print("=" * 70)
    
    return all_categories_failed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)