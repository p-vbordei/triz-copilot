#!/usr/bin/env python3
"""
TRIZ Co-Pilot CLI Interface (T044)
Can be used standalone or integrated with Gemini CLI.
"""

import click
import json
import sys
from pathlib import Path
from typing import Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.triz_tools.workflow_tools import (
    triz_workflow_start,
    triz_workflow_continue,
    triz_workflow_reset,
)
from src.triz_tools.direct_tools import (
    triz_tool_get_principle,
    triz_tool_contradiction_matrix,
    triz_tool_brainstorm,
)
from src.triz_tools.solve_tools import (
    triz_solve_autonomous,
)


@click.group()
@click.version_option(version="1.0.0", prog_name="TRIZ Co-Pilot")
def cli():
    """TRIZ Engineering Co-Pilot - Systematic Innovation Assistant"""
    pass


@cli.group()
def workflow():
    """Guided TRIZ workflow commands"""
    pass


@workflow.command()
def start():
    """Start a new TRIZ workflow session"""
    response = triz_workflow_start()
    
    if response.success:
        click.echo(click.style("✅ TRIZ Workflow Started", fg="green", bold=True))
        click.echo(f"Session ID: {response.data.get('session_id')}")
        click.echo(f"Stage: {response.stage.value if response.stage else 'Unknown'}")
        click.echo(f"\n{response.data.get('next_prompt', '')}")
    else:
        click.echo(click.style(f"❌ Error: {response.message}", fg="red"))


@workflow.command()
@click.argument('session_id')
@click.argument('user_input', required=False, default="")
def continue_(session_id: str, user_input: str):
    """Continue an existing TRIZ workflow session"""
    if not user_input:
        user_input = click.prompt("Your input")
    
    response = triz_workflow_continue(session_id, user_input)
    
    if response.success:
        click.echo(click.style("✅ Workflow Continued", fg="green"))
        click.echo(f"Stage: {response.stage.value if response.stage else 'Unknown'}")
        
        if "next_prompt" in response.data:
            click.echo(f"\n{response.data['next_prompt']}")
        
        if response.stage and response.stage.value == "completed":
            click.echo(click.style("\n🎉 Workflow Complete!", fg="cyan", bold=True))
    else:
        click.echo(click.style(f"❌ Error: {response.message}", fg="red"))


@workflow.command()
@click.argument('session_id')
def reset(session_id: str):
    """Reset a TRIZ workflow session"""
    response = triz_workflow_reset(session_id)
    
    if response.success:
        click.echo(click.style("✅ Session Reset", fg="green"))
        click.echo(response.message)
    else:
        click.echo(click.style(f"❌ Error: {response.message}", fg="red"))


@cli.group()
def tool():
    """Direct TRIZ tool access"""
    pass


@tool.command()
@click.argument('number', type=int)
def principle(number: int):
    """Get details about a TRIZ principle (1-40)"""
    response = triz_tool_get_principle(number)
    
    if response.success:
        data = response.data
        click.echo(click.style(f"\n📚 TRIZ Principle #{number}", fg="cyan", bold=True))
        click.echo(click.style(f"{data['principle_name']}", fg="yellow", bold=True))
        click.echo(f"\n{data['description']}")
        
        if data.get('sub_principles'):
            click.echo(click.style("\nSub-principles:", fg="cyan"))
            for sp in data['sub_principles']:
                click.echo(f"  • {sp}")
        
        if data.get('examples'):
            click.echo(click.style("\nExamples:", fg="cyan"))
            for ex in data['examples'][:3]:
                click.echo(f"  • {ex}")
    else:
        click.echo(click.style(f"❌ Error: {response.message}", fg="red"))


@tool.command()
@click.argument('improving', type=int)
@click.argument('worsening', type=int)
def matrix(improving: int, worsening: int):
    """Query the contradiction matrix (parameters 1-39)"""
    response = triz_tool_contradiction_matrix(improving, worsening)
    
    if response.success:
        data = response.data
        click.echo(click.style("\n🔍 Contradiction Matrix Result", fg="cyan", bold=True))
        click.echo(f"Improving: Parameter {improving}")
        click.echo(f"Worsening: Parameter {worsening}")
        
        if data.get('recommended_principles'):
            click.echo(click.style("\nRecommended Principles:", fg="green"))
            for p in data['recommended_principles']:
                click.echo(f"  • Principle {p}")
        
        if data.get('confidence_score'):
            score = data['confidence_score']
            color = 'green' if score > 0.7 else 'yellow' if score > 0.4 else 'red'
            click.echo(f"\nConfidence: {click.style(f'{score:.2f}', fg=color)}")
    else:
        click.echo(click.style(f"❌ Error: {response.message}", fg="red"))


@tool.command()
@click.argument('principle_number', type=int)
@click.option('--context', '-c', help='Problem context for brainstorming')
def brainstorm(principle_number: int, context: Optional[str]):
    """Brainstorm solutions using a TRIZ principle"""
    if not context:
        context = click.prompt("Describe your problem context")
    
    response = triz_tool_brainstorm(principle_number, context)
    
    if response.success:
        data = response.data
        click.echo(click.style(f"\n💡 Brainstorming with Principle {principle_number}", fg="cyan", bold=True))
        
        if data.get('ideas'):
            click.echo(click.style("\nGenerated Ideas:", fg="green"))
            for i, idea in enumerate(data['ideas'], 1):
                click.echo(click.style(f"\nIdea {i}: {idea['title']}", fg="yellow"))
                click.echo(f"{idea['description']}")
                if idea.get('how_principle_applies'):
                    click.echo(click.style("How it applies:", fg="cyan"))
                    click.echo(f"  {idea['how_principle_applies']}")
    else:
        click.echo(click.style(f"❌ Error: {response.message}", fg="red"))


@cli.command()
@click.argument('problem', required=False)
@click.option('--file', '-f', type=click.File('r'), help='Read problem from file')
@click.option('--json', 'output_json', is_flag=True, help='Output as JSON')
def solve(problem: Optional[str], file, output_json: bool):
    """Perform autonomous TRIZ analysis on a problem"""
    if file:
        problem = file.read()
    elif not problem:
        click.echo("Enter your problem description (Ctrl+D to finish):")
        problem = sys.stdin.read()
    
    if not problem.strip():
        click.echo(click.style("❌ Error: Problem description required", fg="red"))
        return
    
    response = triz_solve_autonomous(problem)
    
    if output_json:
        # JSON output for integration
        output = {
            "success": response.success,
            "message": response.message,
            "data": response.data
        }
        click.echo(json.dumps(output, indent=2))
    else:
        # Human-readable output
        if response.success:
            data = response.data
            click.echo(click.style("\n🔬 TRIZ Analysis Complete", fg="green", bold=True))
            
            # Problem Summary
            click.echo(click.style("\n📋 Problem Summary:", fg="cyan"))
            click.echo(data.get('problem_summary', 'N/A'))
            
            # Ideal Final Result
            click.echo(click.style("\n🎯 Ideal Final Result:", fg="cyan"))
            click.echo(data.get('ideal_final_result', 'N/A'))
            
            # Contradictions
            if data.get('contradictions_identified'):
                click.echo(click.style("\n⚡ Contradictions Identified:", fg="cyan"))
                for c in data['contradictions_identified']:
                    click.echo(f"  • Parameter {c['improving_parameter']} vs {c['worsening_parameter']}")
            
            # Top Principles
            if data.get('top_principles'):
                click.echo(click.style("\n🏆 Top TRIZ Principles:", fg="cyan"))
                for p in data['top_principles']:
                    score = p.get('relevance_score', 0)
                    color = 'green' if score > 0.7 else 'yellow'
                    click.echo(f"  • #{p['principle_id']}: {p['principle_name']} "
                             f"({click.style(f'{score:.2f}', fg=color)})")
            
            # Solution Concepts
            if data.get('solution_concepts'):
                click.echo(click.style("\n💡 Solution Concepts:", fg="cyan", bold=True))
                for i, concept in enumerate(data['solution_concepts'], 1):
                    click.echo(click.style(f"\nConcept {i}: {concept['concept_title']}", fg="yellow"))
                    click.echo(f"{concept['description']}")
                    
                    if concept.get('feasibility_score'):
                        score = concept['feasibility_score']
                        color = 'green' if score > 0.7 else 'yellow' if score > 0.4 else 'red'
                        click.echo(f"Feasibility: {click.style(f'{score:.2f}', fg=color)}")
                    
                    if concept.get('innovation_level'):
                        level = concept['innovation_level']
                        stars = '⭐' * level
                        click.echo(f"Innovation: {stars} ({level}/5)")
            
            # Overall Confidence
            if data.get('confidence_score'):
                score = data['confidence_score']
                color = 'green' if score > 0.7 else 'yellow' if score > 0.4 else 'red'
                click.echo(click.style(f"\n📊 Analysis Confidence: {score:.2f}", fg=color, bold=True))
        else:
            click.echo(click.style(f"❌ Error: {response.message}", fg="red"))


@cli.command()
def interactive():
    """Start interactive TRIZ session"""
    click.echo(click.style("🚀 TRIZ Co-Pilot Interactive Mode", fg="cyan", bold=True))
    click.echo("Type 'help' for commands, 'exit' to quit\n")
    
    session_id = None
    
    while True:
        try:
            command = click.prompt("TRIZ", type=str)
            
            if command.lower() in ['exit', 'quit', 'q']:
                click.echo("Goodbye! 👋")
                break
            
            elif command.lower() == 'help':
                click.echo("""
Available commands:
  start              - Start new workflow
  continue [input]   - Continue current workflow
  principle [n]      - Show principle n (1-40)
  matrix [i] [w]     - Query contradiction matrix
  solve              - Analyze a problem
  exit              - Quit
                """)
            
            elif command.lower() == 'start':
                response = triz_workflow_start()
                if response.success:
                    session_id = response.data.get('session_id')
                    click.echo(click.style("✅ Session started", fg="green"))
                    click.echo(response.data.get('next_prompt', ''))
            
            elif command.lower().startswith('continue'):
                if not session_id:
                    click.echo(click.style("No active session. Use 'start' first.", fg="red"))
                else:
                    parts = command.split(maxsplit=1)
                    user_input = parts[1] if len(parts) > 1 else click.prompt("Input")
                    response = triz_workflow_continue(session_id, user_input)
                    if response.success:
                        click.echo(response.data.get('next_prompt', 'Processing...'))
            
            elif command.lower().startswith('principle'):
                parts = command.split()
                if len(parts) > 1:
                    try:
                        num = int(parts[1])
                        response = triz_tool_get_principle(num)
                        if response.success:
                            click.echo(f"Principle {num}: {response.data['principle_name']}")
                            click.echo(response.data['description'])
                    except ValueError:
                        click.echo(click.style("Invalid principle number", fg="red"))
            
            elif command.lower() == 'solve':
                click.echo("Enter problem (Ctrl+D to finish):")
                problem = sys.stdin.read()
                response = triz_solve_autonomous(problem)
                if response.success:
                    click.echo(click.style("✅ Analysis complete", fg="green"))
                    for concept in response.data.get('solution_concepts', [])[:3]:
                        click.echo(f"• {concept['concept_title']}")
            
            else:
                click.echo(click.style(f"Unknown command: {command}", fg="red"))
                click.echo("Type 'help' for available commands")
                
        except (EOFError, KeyboardInterrupt):
            click.echo("\nGoodbye! 👋")
            break
        except Exception as e:
            click.echo(click.style(f"Error: {str(e)}", fg="red"))


if __name__ == "__main__":
    cli()