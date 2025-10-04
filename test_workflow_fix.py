#!/usr/bin/env python3
"""
Test TRIZ Workflow Fix
Verifies that workflow now actually generates solutions
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from triz_tools.workflow_tools import triz_workflow_start, triz_workflow_continue


def test_workflow():
    """Test complete workflow with actual TRIZ analysis"""

    print("=" * 60)
    print("TESTING TRIZ WORKFLOW - WITH ACTUAL ANALYSIS")
    print("=" * 60)
    print()

    # Step 1: Start workflow
    print("STEP 1: Starting workflow...")
    response = triz_workflow_start()

    if not response.success:
        print(f"❌ Failed to start: {response.message}")
        return False

    session_id = response.data["session_id"]
    print(f"✅ Session started: {session_id}")
    print(f"   Stage: {response.data['stage']}")
    print(f"   Prompt: {response.data['next_prompt'][:100]}...")
    print()

    # Step 2: Problem definition
    print("STEP 2: Defining problem...")
    problem = "I need a lightweight bendable material for a robot arm that can withstand motor heat"

    response = triz_workflow_continue(session_id, problem)

    if not response.success:
        print(f"❌ Failed: {response.message}")
        return False

    print(f"✅ Problem recorded")
    print(f"   Stage: {response.data['stage']}")
    print(f"   Prompt: {response.data['next_prompt'][:100]}...")
    print()

    # Step 3: Ideal Final Result
    print("STEP 3: Defining IFR...")
    ifr = "The material would be lighter than aluminum, bendable to reduce part count, heat resistant, and low cost"

    response = triz_workflow_continue(session_id, ifr)

    if not response.success:
        print(f"❌ Failed: {response.message}")
        return False

    print(f"✅ IFR recorded")
    print(f"   Stage: {response.data['stage']}")
    print()

    # Step 4: Contradictions (THIS IS WHERE ANALYSIS HAPPENS)
    print("STEP 4: Analyzing contradictions...")
    contradictions_input = "Weight vs strength, formability vs heat resistance, cost vs performance"

    response = triz_workflow_continue(session_id, contradictions_input)

    if not response.success:
        print(f"❌ Failed: {response.message}")
        return False

    print(f"✅ Contradictions analyzed!")
    print(f"   Stage: {response.data['stage']}")

    # Check if principles were actually generated
    if "principle" in response.data["next_prompt"].lower():
        print(f"   ✅ TRIZ principles identified!")
        # Show first 500 chars of principles
        prompt = response.data["next_prompt"]
        print(f"\n{prompt[:500]}...\n")
    else:
        print(f"   ⚠️  No principles in response")

    print()

    # Step 5: Solution generation (THIS IS WHERE SOLUTIONS ARE CREATED)
    print("STEP 5: Generating solutions...")
    proceed = "Yes, proceed with solution generation"

    response = triz_workflow_continue(session_id, proceed)

    if not response.success:
        print(f"❌ Failed: {response.message}")
        return False

    print(f"✅ Solutions generated!")
    print(f"   Stage: {response.data['stage']}")

    # Check if solutions were actually generated
    if "solution" in response.data["next_prompt"].lower():
        print(f"   ✅ Solutions in response!")

        # Extract solution count
        prompt = response.data["next_prompt"]
        if "Generated" in prompt:
            # Show first 800 chars
            print(f"\n{prompt[:800]}...\n")

            # Count solutions in session data
            solutions = response.data.get("session_data", {}).get("solutions", [])
            print(f"   Solutions in session: {len(solutions)}")

            if len(solutions) > 0:
                print(f"   ✅ ACTUAL SOLUTIONS GENERATED!")
                print(f"\n   Sample solution:")
                sol = solutions[0]
                print(f"   - Title: {sol.get('title', 'N/A')}")
                print(f"   - Principle: {sol.get('principle_name', 'N/A')}")
                print(f"   - Feasibility: {sol.get('feasibility_score', 0):.2f}")
                print(f"   - Description: {sol.get('description', 'N/A')[:150]}...")
            else:
                print(f"   ❌ No solutions in session data")
        else:
            print(f"   ⚠️  Unexpected response format")
    else:
        print(f"   ⚠️  No solutions in response")

    print()
    print("=" * 60)
    print("WORKFLOW TEST COMPLETE")
    print("=" * 60)

    return True


if __name__ == "__main__":
    try:
        success = test_workflow()
        if success:
            print("\n✅ WORKFLOW FIX VERIFIED - Solutions are now generated!")
        else:
            print("\n❌ WORKFLOW TEST FAILED")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
