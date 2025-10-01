#!/usr/bin/env python3
"""Non-interactive test script for TRIZ tools."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.triz_tools import (
    direct_tools,
    solve_tools,
    workflow_tools
)

def test_workflow():
    """Test the TRIZ workflow functions."""
    print("Testing TRIZ Workflow...")
    
    # Start workflow
    result = workflow_tools.triz_workflow_start()
    print(f"✓ Workflow started: {result.success}")
    session_id = result.session_id
    
    # Continue workflow with problem statement
    result = workflow_tools.triz_workflow_continue(
        session_id, 
        "Improve smartphone battery life without increasing size"
    )
    print(f"✓ Problem defined: {result.success}")
    
    # Define ideal final result
    result = workflow_tools.triz_workflow_continue(
        session_id,
        "Battery lasts a week on single charge with no size increase"
    )
    print(f"✓ IFR defined: {result.success}")
    
    # Get status
    status = workflow_tools.triz_workflow_status(session_id)
    print(f"✓ Status check: {status['success']}, Stage: {status.get('stage', 'unknown')}")
    
    # Reset workflow
    result = workflow_tools.triz_workflow_reset(session_id)
    print(f"✓ Workflow reset: {result.success}")
    
    return True

def test_direct_tools():
    """Test direct TRIZ tools."""
    print("\nTesting Direct TRIZ Tools...")
    
    # Test getting a principle
    result = direct_tools.triz_tool_get_principle(1)
    print(f"✓ Got principle 1: {result.success}")
    
    # Test contradiction matrix lookup
    result = direct_tools.triz_tool_contradiction_matrix(
        improving_param=3,  # Speed
        worsening_param=9   # Weight of moving object
    )
    print(f"✓ Matrix lookup: {result.success}")
    if result.success:
        print(f"  Found {len(result.data.get('principles', []))} principles")
    
    # Test brainstorming
    result = direct_tools.triz_tool_brainstorm(
        principle_number=35,
        context="Improve battery life"
    )
    print(f"✓ Brainstorm generated: {result.success}")
    
    return True

def test_solve_tools():
    """Test TRIZ solving tools."""
    print("\nTesting Solve Tools...")
    
    # Test autonomous solver
    result = solve_tools.triz_solve_autonomous(
        problem_description="Smartphone battery drains too quickly but cannot increase device size"
    )
    print(f"✓ Autonomous solve: {result.success}")
    if result.success:
        solutions = result.data.get('solution_concepts', [])
        print(f"  Generated {len(solutions)} solution concepts")
    
    # Test IFR generation
    ifr = solve_tools.generate_ideal_final_result(
        "Improve battery life without increasing size"
    )
    print(f"✓ IFR generated: {len(ifr) > 0}")
    
    # Test contradiction extraction
    contradictions = solve_tools.extract_contradictions(
        "Need longer battery life but cannot increase battery size"
    )
    print(f"✓ Contradictions extracted: {len(contradictions)} found")
    
    return True

def main():
    """Run all tests."""
    print("=" * 50)
    print("TRIZ Tools Test Suite")
    print("=" * 50)
    
    tests = [
        ("Workflow", test_workflow),
        ("Direct Tools", test_direct_tools),
        ("Solve Tools", test_solve_tools)
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
                print(f"✗ {name} test failed")
        except Exception as e:
            failed += 1
            print(f"✗ {name} test error: {str(e)}")
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 50)
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)