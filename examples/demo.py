#!/usr/bin/env python3
"""
TRIZ Co-Pilot Demo Script
Demonstrates various capabilities of the TRIZ system.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.triz_tools.workflow_tools import (
    triz_workflow_start,
    triz_workflow_continue,
)
from src.triz_tools.direct_tools import (
    triz_tool_get_principle,
    triz_tool_contradiction_matrix,
    triz_tool_brainstorm,
)
from src.triz_tools.solve_tools import (
    triz_solve_autonomous,
)


def print_header(title: str):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def demo_principle_lookup():
    """Demonstrate principle lookup"""
    print_header("DEMO 1: Principle Lookup")
    
    # Look up principle 1 (Segmentation)
    response = triz_tool_get_principle(1)
    
    if response.success:
        data = response.data
        print(f"\nPrinciple #{data['principle_number']}: {data['principle_name']}")
        print(f"Description: {data['description']}")
        print("\nSub-principles:")
        for sp in data['sub_principles']:
            print(f"  • {sp}")
        print("\nExamples:")
        for ex in data['examples'][:3]:
            print(f"  • {ex}")
    else:
        print(f"Error: {response.message}")


def demo_contradiction_matrix():
    """Demonstrate contradiction matrix query"""
    print_header("DEMO 2: Contradiction Matrix")
    
    # Query matrix: Weight (1) vs Strength (14)
    print("\nProblem: Reduce weight while maintaining strength")
    print("Improving: Parameter 1 (Weight of moving object)")
    print("Worsening: Parameter 14 (Strength)")
    
    response = triz_tool_contradiction_matrix(1, 14)
    
    if response.success:
        data = response.data
        print("\nRecommended TRIZ Principles:")
        for p in data['recommended_principles']:
            # Get principle name
            principle_response = triz_tool_get_principle(p)
            if principle_response.success:
                name = principle_response.data['principle_name']
                print(f"  • Principle {p}: {name}")
            else:
                print(f"  • Principle {p}")
        
        print(f"\nConfidence Score: {data['confidence_score']:.2f}")
    else:
        print(f"Error: {response.message}")


def demo_brainstorming():
    """Demonstrate brainstorming with a principle"""
    print_header("DEMO 3: Brainstorming")
    
    principle_num = 35  # Adaptability
    context = "Design a modular smartphone that can be easily upgraded"
    
    print(f"\nUsing Principle {principle_num} for brainstorming")
    print(f"Context: {context}")
    
    response = triz_tool_brainstorm(principle_num, context)
    
    if response.success:
        data = response.data
        print("\nGenerated Ideas:")
        for i, idea in enumerate(data['ideas'], 1):
            print(f"\nIdea {i}: {idea['title']}")
            print(f"  {idea['description']}")
            if idea.get('how_principle_applies'):
                print(f"  How it applies: {idea['how_principle_applies']}")
    else:
        print(f"Error: {response.message}")


def demo_autonomous_solve():
    """Demonstrate autonomous problem solving"""
    print_header("DEMO 4: Autonomous Problem Solving")
    
    problem = """
    We need to design a cooling system for electronic components that:
    - Reduces temperature by 30%
    - Doesn't increase power consumption
    - Maintains silent operation (no fans)
    - Fits in the same space as current solution
    """
    
    print(f"\nProblem: {problem}")
    print("\nAnalyzing...")
    
    response = triz_solve_autonomous(problem)
    
    if response.success:
        data = response.data
        
        print(f"\n✅ Analysis Complete!")
        print(f"\nIdeal Final Result:")
        print(f"  {data['ideal_final_result']}")
        
        print(f"\nContradictions Identified:")
        for c in data['contradictions_identified']:
            print(f"  • Parameter {c['improving_parameter']} vs {c['worsening_parameter']}")
        
        print(f"\nTop TRIZ Principles:")
        for p in data['top_principles'][:3]:
            print(f"  • #{p['principle_id']}: {p['principle_name']} (score: {p['relevance_score']:.2f})")
        
        print(f"\nSolution Concepts:")
        for i, concept in enumerate(data['solution_concepts'][:3], 1):
            print(f"\n  Concept {i}: {concept['concept_title']}")
            print(f"    {concept['description'][:200]}...")
            print(f"    Feasibility: {concept['feasibility_score']:.2f}")
            print(f"    Innovation Level: {concept['innovation_level']}/5")
        
        print(f"\nOverall Confidence: {data['confidence_score']:.2f}")
    else:
        print(f"Error: {response.message}")


def demo_workflow():
    """Demonstrate guided workflow"""
    print_header("DEMO 5: Guided Workflow")
    
    print("\nStarting TRIZ guided workflow...")
    
    # Start workflow
    start_response = triz_workflow_start()
    
    if not start_response.success:
        print(f"Error starting workflow: {start_response.message}")
        return
    
    session_id = start_response.data['session_id']
    print(f"Session ID: {session_id}")
    print(f"Stage: {start_response.stage.value}")
    print(f"\nPrompt: {start_response.data['next_prompt']}")
    
    # Continue with problem description
    problem = "Increase battery life while reducing charging time"
    print(f"\nUser Input: {problem}")
    
    continue_response = triz_workflow_continue(session_id, problem)
    
    if continue_response.success:
        print(f"Stage: {continue_response.stage.value}")
        if 'next_prompt' in continue_response.data:
            print(f"Next Prompt: {continue_response.data['next_prompt']}")
        
        # Continue with IFR
        ifr = "Battery charges instantly and lasts forever"
        print(f"\nUser Input (IFR): {ifr}")
        
        continue_response = triz_workflow_continue(session_id, ifr)
        if continue_response.success:
            print(f"Stage: {continue_response.stage.value}")
            print("Workflow progressing successfully!")
    else:
        print(f"Error: {continue_response.message}")


def main():
    """Run all demos"""
    print("\n" + "🚀" * 30)
    print("     TRIZ CO-PILOT DEMONSTRATION")
    print("🚀" * 30)
    
    demos = [
        ("Principle Lookup", demo_principle_lookup),
        ("Contradiction Matrix", demo_contradiction_matrix),
        ("Brainstorming", demo_brainstorming),
        ("Autonomous Solve", demo_autonomous_solve),
        ("Guided Workflow", demo_workflow),
    ]
    
    print("\nAvailable Demos:")
    for i, (name, _) in enumerate(demos, 1):
        print(f"  {i}. {name}")
    print(f"  {len(demos) + 1}. Run All")
    print("  0. Exit")
    
    while True:
        try:
            choice = input("\nSelect demo (0-6): ").strip()
            
            if choice == '0':
                print("Goodbye! 👋")
                break
            elif choice == str(len(demos) + 1):
                # Run all demos
                for name, demo_func in demos:
                    demo_func()
                print("\n✅ All demos complete!")
                break
            else:
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(demos):
                    name, demo_func = demos[choice_idx]
                    demo_func()
                    print(f"\n✅ {name} demo complete!")
                else:
                    print("Invalid choice. Please try again.")
        except (ValueError, IndexError):
            print("Invalid input. Please enter a number.")
        except KeyboardInterrupt:
            print("\n\nDemo interrupted. Goodbye! 👋")
            break
        except Exception as e:
            print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()