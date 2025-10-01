#!/usr/bin/env python3
"""
Quickstart Validation Runner

Executes all validation scenarios from quickstart.md and reports results.
"""

import sys
from pathlib import Path
import subprocess
import time
from typing import Dict, Any, List

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

def check_prerequisites() -> Dict[str, bool]:
    """Check if all prerequisites are met."""
    print("Checking prerequisites...")
    
    checks = {}
    
    # Check Python modules
    try:
        import src.triz_tools
        checks['python_modules'] = True
        print("✅ Python modules available")
    except ImportError as e:
        checks['python_modules'] = False
        print(f"❌ Python modules missing: {e}")
    
    # Check if we can import core functions
    try:
        from src.triz_tools.direct_tools import triz_tool_get_principle
        from src.triz_tools.solve_tools import triz_solve_autonomous
        checks['core_functions'] = True
        print("✅ Core functions available")
    except ImportError as e:
        checks['core_functions'] = False
        print(f"❌ Core functions missing: {e}")
    
    # Check data files
    data_dir = Path(__file__).parent.parent / "src" / "data"
    if data_dir.exists():
        checks['data_files'] = True
        print("✅ Data directory exists")
    else:
        checks['data_files'] = False
        print("❌ Data directory missing")
    
    return checks

def run_health_checks() -> bool:
    """Run system health checks."""
    print("\nRunning health checks...")
    
    try:
        from src.triz_tools.health_checks import HealthChecker
        
        checker = HealthChecker()
        results = checker.check_all(verbose=False)
        
        all_healthy = True
        for component, status in results.items():
            if status.is_healthy:
                print(f"✅ {component}: {status.message}")
            else:
                print(f"⚠️  {component}: {status.message}")
                if component in ['knowledge_base', 'sessions']:  # Critical components
                    all_healthy = False
        
        return all_healthy
        
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def run_validation_tests() -> bool:
    """Run the validation test suite."""
    print("\nRunning validation tests...")
    
    try:
        # Import and run validation tests
        test_file = Path(__file__).parent.parent / "tests" / "validation" / "test_quickstart_scenarios.py"
        
        if not test_file.exists():
            print(f"❌ Validation test file not found: {test_file}")
            return False
        
        # Run the validation
        result = subprocess.run([
            sys.executable, str(test_file)
        ], capture_output=True, text=True, timeout=300)  # 5 minute timeout
        
        print("Validation output:")
        print("-" * 40)
        print(result.stdout)
        
        if result.stderr:
            print("Errors:")
            print(result.stderr)
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("❌ Validation tests timed out (5 minutes)")
        return False
    except Exception as e:
        print(f"❌ Error running validation tests: {e}")
        return False

def run_performance_benchmarks() -> Dict[str, float]:
    """Run performance benchmarks from quickstart scenarios."""
    print("\nRunning performance benchmarks...")
    
    benchmarks = {}
    
    try:
        from src.triz_tools.direct_tools import triz_tool_get_principle
        from src.triz_tools.solve_tools import triz_solve_autonomous
        
        # Test tool query performance (should be <2s)
        start_time = time.time()
        result = triz_tool_get_principle(1)
        tool_time = time.time() - start_time
        benchmarks['tool_query'] = tool_time
        
        if result.get('success'):
            print(f"✅ Tool query: {tool_time:.3f}s (target: <2s)")
        else:
            print(f"❌ Tool query failed: {result.get('message', 'Unknown error')}")
        
        # Test autonomous solve performance (should be <10s)
        start_time = time.time()
        result = triz_solve_autonomous("Performance test problem")
        solve_time = time.time() - start_time
        benchmarks['autonomous_solve'] = solve_time
        
        if 'analysis' in result:
            print(f"✅ Autonomous solve: {solve_time:.2f}s (target: <10s)")
        else:
            print(f"❌ Autonomous solve failed")
        
        # Test batch operations
        start_time = time.time()
        for i in range(1, 6):  # Test 5 principles
            triz_tool_get_principle(i)
        batch_time = time.time() - start_time
        avg_time = batch_time / 5
        benchmarks['batch_average'] = avg_time
        
        print(f"✅ Batch operations: {avg_time:.3f}s average (target: <2s)")
        
    except Exception as e:
        print(f"❌ Performance benchmark failed: {e}")
    
    return benchmarks

def validate_quickstart_examples() -> Dict[str, bool]:
    """Validate specific examples from quickstart.md."""
    print("\nValidating quickstart examples...")
    
    validations = {}
    
    try:
        from src.triz_tools.direct_tools import (
            triz_tool_get_principle,
            triz_tool_contradiction_matrix,
            triz_tool_brainstorm
        )
        from src.triz_tools.solve_tools import triz_solve_autonomous
        from src.triz_tools.workflow_tools import triz_workflow_start
        
        # Example 1: Principle 15 (Dynamics)
        result = triz_tool_get_principle(15)
        validations['principle_15'] = (
            result.get('success', False) and 
            result.get('data', {}).get('name') == 'Dynamics'
        )
        print(f"{'✅' if validations['principle_15'] else '❌'} Principle 15 lookup")
        
        # Example 2: Contradiction matrix (Weight vs Strength)
        result = triz_tool_contradiction_matrix(1, 14)
        validations['matrix_1_14'] = (
            result.get('success', False) and
            'recommended_principles' in result.get('data', {})
        )
        print(f"{'✅' if validations['matrix_1_14'] else '❌'} Matrix lookup (1,14)")
        
        # Example 3: Brainstorming with Principle 40
        result = triz_tool_brainstorm(40, "Solar panel efficiency improvement")
        validations['brainstorm_40'] = (
            result.get('success', False) and
            'solutions' in result.get('data', {})
        )
        print(f"{'✅' if validations['brainstorm_40'] else '❌'} Brainstorming with Principle 40")
        
        # Example 4: Autonomous solve (aircraft wing)
        result = triz_solve_autonomous(
            "Reduce aircraft wing weight while maintaining structural strength"
        )
        validations['autonomous_aircraft'] = (
            'analysis' in result and
            len(result['analysis'].get('solutions', [])) >= 3
        )
        print(f"{'✅' if validations['autonomous_aircraft'] else '❌'} Autonomous solve (aircraft)")
        
        # Example 5: Workflow start
        result = triz_workflow_start()
        validations['workflow_start'] = (
            result.get('success', False) and
            'session_id' in result
        )
        print(f"{'✅' if validations['workflow_start'] else '❌'} Workflow start")
        
    except Exception as e:
        print(f"❌ Example validation failed: {e}")
        validations['exception'] = False
    
    return validations

def generate_validation_report(
    prerequisites: Dict[str, bool],
    health_status: bool,
    test_results: bool,
    benchmarks: Dict[str, float],
    examples: Dict[str, bool]
) -> None:
    """Generate comprehensive validation report."""
    
    print("\n" + "=" * 60)
    print("QUICKSTART VALIDATION REPORT")
    print("=" * 60)
    
    # Prerequisites
    print("\n📋 Prerequisites:")
    all_prereqs = all(prerequisites.values())
    for check, status in prerequisites.items():
        print(f"  {'✅' if status else '❌'} {check}")
    print(f"  Overall: {'✅ PASS' if all_prereqs else '❌ FAIL'}")
    
    # Health Status
    print(f"\n🏥 Health Status: {'✅ HEALTHY' if health_status else '⚠️  ISSUES'}")
    
    # Test Results
    print(f"\n🧪 Test Suite: {'✅ PASS' if test_results else '❌ FAIL'}")
    
    # Performance Benchmarks
    print("\n⚡ Performance Benchmarks:")
    if benchmarks:
        for test, time_taken in benchmarks.items():
            if test == 'tool_query':
                status = "✅ PASS" if time_taken < 2.0 else "❌ SLOW"
                print(f"  {status} Tool query: {time_taken:.3f}s (target: <2s)")
            elif test == 'autonomous_solve':
                status = "✅ PASS" if time_taken < 10.0 else "❌ SLOW"
                print(f"  {status} Autonomous solve: {time_taken:.2f}s (target: <10s)")
            elif test == 'batch_average':
                status = "✅ PASS" if time_taken < 2.0 else "❌ SLOW"
                print(f"  {status} Batch average: {time_taken:.3f}s (target: <2s)")
    else:
        print("  ❌ No benchmarks available")
    
    # Example Validations
    print("\n📝 Example Validations:")
    all_examples = all(examples.values()) if examples else False
    for example, status in examples.items():
        if example != 'exception':
            print(f"  {'✅' if status else '❌'} {example}")
    print(f"  Overall: {'✅ PASS' if all_examples else '❌ FAIL'}")
    
    # Final Assessment
    print("\n" + "=" * 60)
    overall_success = (
        all_prereqs and 
        health_status and 
        test_results and 
        all_examples and
        all(t < 2.0 for k, t in benchmarks.items() if k == 'tool_query') and
        all(t < 10.0 for k, t in benchmarks.items() if k == 'autonomous_solve')
    )
    
    if overall_success:
        print("🎉 QUICKSTART VALIDATION: SUCCESS")
        print("\nThe TRIZ Engineering Co-Pilot is fully functional!")
        print("All quickstart scenarios work as documented.")
        print("\nNext steps:")
        print("  • Review the CLI usage guide: docs/cli_usage.md")
        print("  • Check the API reference: docs/api_reference.md")
        print("  • Explore advanced features and customization")
    else:
        print("❌ QUICKSTART VALIDATION: FAILED")
        print("\nSome issues were found. Please review the output above.")
        print("Common solutions:")
        print("  • Ensure all dependencies are installed")
        print("  • Check that data files are properly loaded")
        print("  • Verify system resources are adequate")
        print("  • Run individual tests for more detailed debugging")
    
    print("=" * 60)

def main():
    """Main validation runner."""
    print("TRIZ Engineering Co-Pilot - Quickstart Validation")
    print("This script validates all scenarios from quickstart.md")
    print()
    
    # Run validation steps
    prerequisites = check_prerequisites()
    health_status = run_health_checks()
    
    # Only run tests if prerequisites are met
    if all(prerequisites.values()):
        test_results = run_validation_tests()
        benchmarks = run_performance_benchmarks()
        examples = validate_quickstart_examples()
    else:
        print("\n❌ Prerequisites not met. Skipping tests.")
        test_results = False
        benchmarks = {}
        examples = {}
    
    # Generate report
    generate_validation_report(
        prerequisites,
        health_status,
        test_results,
        benchmarks,
        examples
    )
    
    # Return success status
    overall_success = (
        all(prerequisites.values()) and
        health_status and
        test_results and
        all(examples.values())
    )
    
    return 0 if overall_success else 1

if __name__ == '__main__':
    sys.exit(main())