"""
Response Formatter (TASK-007)
Format TRIZ responses for Claude CLI display
"""

from typing import Dict, Any, List
from triz_tools.models import TRIZToolResponse, WorkflowStage


class ClaudeResponseFormatter:
    """Format TRIZ tool responses for Claude CLI"""

    @staticmethod
    def format_tool_response(response: TRIZToolResponse) -> str:
        """
        Format a TRIZToolResponse for display in Claude

        Args:
            response: TRIZToolResponse from TRIZ tools

        Returns:
            Formatted markdown string
        """
        if not response.success:
            return ClaudeResponseFormatter._format_error(response)

        # Route to specific formatter based on response type
        if response.session_id and response.stage:
            return ClaudeResponseFormatter._format_workflow_response(response)
        elif "principles" in response.data:
            return ClaudeResponseFormatter._format_principle_response(response)
        elif "solutions" in response.data or "analysis" in response.data:
            return ClaudeResponseFormatter._format_solve_response(response)
        else:
            return ClaudeResponseFormatter._format_generic_response(response)

    @staticmethod
    def _format_error(response: TRIZToolResponse) -> str:
        """Format error response"""
        return f"""## ❌ Error

{response.message}

Please check your input and try again."""

    @staticmethod
    def _format_workflow_response(response: TRIZToolResponse) -> str:
        """Format workflow stage response (TASK-016)"""
        stage = response.stage
        data = response.data

        # Progress indicator
        stage_number = ClaudeResponseFormatter._get_stage_number(stage)
        progress = f"**Step {stage_number} of 6**"

        # Stage title
        stage_title = ClaudeResponseFormatter._get_stage_title(stage)

        output = f"""## 🎯 TRIZ Workflow - {stage_title}

{progress}

{response.message}

"""

        # Add next prompt if available
        if "next_prompt" in data:
            output += f"""### Next Action
{data['next_prompt']}

"""

        # Add session info
        if response.session_id:
            output += f"""---
**Session ID**: `{response.session_id}`
**Stage**: {stage.value if hasattr(stage, 'value') else stage}
"""

        # Add suggestions if available in data
        if data.get('suggestions'):
            output += f"\n**Suggestions**: {', '.join(data['suggestions'])}\n"

        return output

    @staticmethod
    def _format_principle_response(response: TRIZToolResponse) -> str:
        """Format principle lookup response"""
        data = response.data

        if "principle" in data:
            # Single principle
            p = data["principle"]
            output = f"""## 📚 TRIZ Principle {p.get('number', 'N/A')}: {p.get('name', 'Unknown')}

### Description
{p.get('description', 'No description available')}

"""
            # Add examples if available
            if p.get('examples'):
                output += "### Examples\n"
                for i, example in enumerate(p['examples'], 1):
                    output += f"{i}. {example}\n"
                output += "\n"

            # Add sub-principles if available
            if p.get('sub_principles'):
                output += "### Sub-Principles\n"
                for sp in p['sub_principles']:
                    output += f"- **{sp.get('name', 'Unknown')}**: {sp.get('description', '')}\n"
                output += "\n"

        elif "principles" in data:
            # Multiple principles (from contradiction matrix)
            output = f"""## 🔍 Recommended TRIZ Principles

Based on your contradiction analysis:

"""
            for p in data["principles"]:
                output += f"### {p.get('number', 'N/A')}. {p.get('name', 'Unknown')}\n"
                output += f"{p.get('description', 'No description')}\n\n"

        else:
            output = response.message

        return output

    @staticmethod
    def _format_solve_response(response: TRIZToolResponse) -> str:
        """Format autonomous solve response (TASK-020)"""
        data = response.data

        output = f"""## 🚀 TRIZ Solution Analysis

### Problem Summary
{data.get('problem_summary', 'N/A')}

"""

        # Contradictions
        if "contradictions" in data and data["contradictions"]:
            output += "### Identified Contradictions\n"
            for i, contradiction in enumerate(data["contradictions"], 1):
                output += f"{i}. {contradiction.get('description', 'N/A')}\n"
            output += "\n"

        # Recommended principles
        if "recommended_principles" in data and data["recommended_principles"]:
            output += "### Recommended TRIZ Principles\n"
            for principle in data["recommended_principles"][:5]:
                output += f"- **#{principle.get('number', 'N/A')} - {principle.get('name', 'Unknown')}**: "
                output += f"{principle.get('description', 'No description')[:150]}...\n"
            output += "\n"

        # Solution concepts
        if "solutions" in data and data["solutions"]:
            output += "### Solution Concepts\n"
            for i, solution in enumerate(data["solutions"], 1):
                output += f"\n#### Solution {i}: {solution.get('title', 'Untitled')}\n"
                output += f"{solution.get('description', 'No description')}\n"
                if "principle" in solution:
                    output += f"*Based on Principle #{solution['principle']}*\n"

        return output

    @staticmethod
    def _format_generic_response(response: TRIZToolResponse) -> str:
        """Format generic response"""
        output = f"""## ✅ {response.message}

"""
        if response.data:
            output += "### Response Data\n```json\n"
            import json
            output += json.dumps(response.data, indent=2)
            output += "\n```\n"

        return output

    @staticmethod
    def _get_stage_number(stage: WorkflowStage) -> int:
        """Get numeric stage number"""
        stage_map = {
            WorkflowStage.PROBLEM_DEFINITION: 1,
            WorkflowStage.CONTRADICTION_ANALYSIS: 2,
            WorkflowStage.PRINCIPLE_SELECTION: 3,
            WorkflowStage.SOLUTION_GENERATION: 4,
            WorkflowStage.EVALUATION: 5,
            WorkflowStage.COMPLETED: 6,
        }
        return stage_map.get(stage, 0)

    @staticmethod
    def _get_stage_title(stage: WorkflowStage) -> str:
        """Get human-readable stage title"""
        stage_titles = {
            WorkflowStage.PROBLEM_DEFINITION: "Problem Definition",
            WorkflowStage.CONTRADICTION_ANALYSIS: "Contradiction Analysis",
            WorkflowStage.PRINCIPLE_SELECTION: "Principle Selection",
            WorkflowStage.SOLUTION_GENERATION: "Solution Generation",
            WorkflowStage.EVALUATION: "Solution Evaluation",
            WorkflowStage.COMPLETED: "Completed",
        }
        return stage_titles.get(stage, "Unknown Stage")

    @staticmethod
    def format_help_text() -> str:
        """Format help text for TRIZ commands"""
        return """## 🛠️ TRIZ Co-Pilot Commands

### Workflow Mode (Guided Step-by-Step)
```
/triz-workflow
```
Start a guided TRIZ problem-solving session

### Autonomous Solve Mode
```
/triz-solve [problem description]
```
Get a complete TRIZ analysis for your problem

### Direct Tool Access
```
/triz-tool get-principle [1-40]
/triz-tool contradiction-matrix --improving [1-39] --worsening [1-39]
/triz-tool brainstorm --principle [1-40] --context "your problem"
```

### Examples
```
/triz-workflow
/triz-solve reduce weight while maintaining strength
/triz-tool get-principle 15
/triz-tool contradiction-matrix --improving 2 --worsening 14
```

For more information, visit: https://github.com/yourusername/triz-copilot
"""
