#!/usr/bin/env python3
"""
Test CLI Subprocess Integration
Validates that CLI executor is working correctly
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from triz_tools.services.cli_executor import get_cli_executor
from triz_tools.services.cli_config import detect_available_cli, is_cli_available
from triz_tools.research_agent import get_research_agent


def test_cli_detection():
    """Test CLI detection"""
    print("=" * 60)
    print("TEST 1: CLI Detection")
    print("=" * 60)

    detected = detect_available_cli()
    available = is_cli_available()

    print(f"✓ Detected CLI: {detected or 'None'}")
    print(f"✓ CLI Available: {available}")

    if detected:
        print(f"✅ SUCCESS: Found {detected} CLI")
    else:
        print("⚠️  WARNING: No CLI detected (will use fallback mode)")

    print()
    return detected is not None


def test_cli_executor():
    """Test CLI executor initialization"""
    print("=" * 60)
    print("TEST 2: CLI Executor")
    print("=" * 60)

    executor = get_cli_executor()

    print(f"✓ Executor Available: {executor.is_available()}")

    if executor.available:
        print(f"✓ Model: {executor.config.model}")
        print(f"✓ Command: {' '.join(executor.config.command)}")
        print(f"✓ Timeout: {executor.config.timeout}s")
        print(f"✓ Max Parallel: {executor.config.max_parallel}")
        print("✅ SUCCESS: CLI executor initialized")
    else:
        print("⚠️  WARNING: Executor not available (will use fallback)")

    print()
    return executor.is_available()


def test_simple_subprocess():
    """Test simple subprocess execution"""
    print("=" * 60)
    print("TEST 3: Simple Subprocess Execution")
    print("=" * 60)

    executor = get_cli_executor()

    if not executor.is_available():
        print("⚠️  SKIPPED: CLI not available")
        print()
        return False

    print("Testing IFR generation via subprocess...")

    result = executor.execute(
        task_type="generate_ifr",
        problem="Reduce weight of aluminum robot arm while maintaining strength",
    )

    print(f"✓ Success: {result.success}")
    print(f"✓ Execution Time: {result.execution_time:.2f}s")

    if result.success:
        print(f"✓ IFR Statement: {result.data.get('ifr_statement', 'N/A')[:100]}...")
        print("✅ SUCCESS: Subprocess execution working")
        return True
    else:
        print(f"❌ FAILED: {result.error}")
        return False

    print()


def test_research_agent_config():
    """Test research agent configuration"""
    print("=" * 60)
    print("TEST 4: Research Agent Configuration")
    print("=" * 60)

    agent = get_research_agent(reset=True)

    print(f"✓ Using Subprocess: {agent.use_subprocess}")
    print(f"✓ Max Findings: {agent.config['max_findings']}")
    print(f"✓ Chunk Size: {agent.config['chunk_size']}")
    print(f"✓ Search Limit Per Query: {agent.config['search_limit_per_query']}")
    print(f"✓ Materials Search Limit: {agent.config['materials_search_limit']}")

    if agent.use_subprocess:
        print("✅ SUCCESS: Research agent using subprocess mode")
        print("   → 10x research capacity enabled!")
    else:
        print("⚠️  INFO: Research agent using fallback mode")
        print("   → Standard capacity (CLI not available)")

    print()
    return True


def test_materials_analysis_mock():
    """Test materials analysis with mock data"""
    print("=" * 60)
    print("TEST 5: Materials Analysis (Mock Data)")
    print("=" * 60)

    executor = get_cli_executor()

    if not executor.is_available():
        print("⚠️  SKIPPED: CLI not available")
        print()
        return False

    print("Testing materials analysis with mock findings...")

    mock_findings = "\n\n".join([
        "=== FINDING 1 ===\nSource: Materials Book\nAluminum alloy 6061: density 2.7 g/cm³, tensile strength 310 MPa",
        "=== FINDING 2 ===\nSource: Materials Book\nMagnesium alloy AZ31: density 1.78 g/cm³, lighter than aluminum",
        "=== FINDING 3 ===\nSource: Materials Book\nCarbon fiber composite: high strength-to-weight ratio, expensive",
    ])

    result = executor.execute(
        task_type="materials_deep_analysis",
        count=3,
        total_chars=len(mock_findings),
        findings=mock_findings,
    )

    print(f"✓ Success: {result.success}")
    print(f"✓ Execution Time: {result.execution_time:.2f}s")

    if result.success:
        materials = result.data.get("materials", [])
        comparisons = result.data.get("comparisons", [])
        recommendations = result.data.get("recommendations", [])
        insights = result.data.get("key_insights", [])

        print(f"✓ Materials Extracted: {len(materials)}")
        print(f"✓ Comparisons Found: {len(comparisons)}")
        print(f"✓ Recommendations: {len(recommendations)}")
        print(f"✓ Key Insights: {len(insights)}")

        print("✅ SUCCESS: Materials analysis working")
        return True
    else:
        print(f"❌ FAILED: {result.error}")
        return False

    print()


def main():
    """Run all tests"""
    print("\n")
    print("=" * 60)
    print("CLI SUBPROCESS INTEGRATION - VALIDATION TESTS")
    print("=" * 60)
    print()

    results = []

    # Run tests
    results.append(("CLI Detection", test_cli_detection()))
    results.append(("CLI Executor", test_cli_executor()))
    results.append(("Simple Subprocess", test_simple_subprocess()))
    results.append(("Research Agent Config", test_research_agent_config()))
    results.append(("Materials Analysis", test_materials_analysis_mock()))

    # Summary
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")

    print()
    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("\nCLI subprocess integration is working correctly.")
        print("Research agent will use 10x capacity mode.")
    else:
        print("\n⚠️  SOME TESTS FAILED")
        print("\nIf CLI tests failed, ensure Claude or Gemini CLI is installed:")
        print("  npm install -g @anthropic-ai/claude-cli")
        print("\nSystem will fallback to standard mode (50 findings).")

    print()


if __name__ == "__main__":
    main()
