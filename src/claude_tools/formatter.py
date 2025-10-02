"""
Response Formatter (TASK-007)
Format TRIZ responses for Claude CLI display
"""

from typing import Dict, Any, List
from src.triz_tools.models import TRIZToolResponse, WorkflowStage


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
        """Format autonomous solve response with deep research provenance (TASK-020)"""
        data = response.data

        output = f"""## 🔬 Deep TRIZ Research Analysis

### Problem Summary
{data.get('problem_summary', 'N/A')}

"""

        # Research Depth Metrics
        if "research_depth" in data:
            rd = data["research_depth"]
            output += f"""### 📊 Research Depth
- **Findings Collected**: {rd.get('total_findings', 0)}
- **Sources Consulted**: {rd.get('sources_consulted', 0)}
- **Queries Executed**: {rd.get('queries_executed', 0)}
- **Confidence Score**: {data.get('confidence_score', 0.0):.0%}

"""

        # Ideal Final Result
        if "ideal_final_result" in data:
            output += f"""### 🎯 Ideal Final Result
{data['ideal_final_result']}

"""

        # Contradictions with sources
        if "contradictions" in data and data["contradictions"]:
            output += "### ⚡ Identified Contradictions\n"
            for i, contradiction in enumerate(data["contradictions"][:5], 1):
                output += f"{i}. **{contradiction.get('improving', 'N/A')}** vs **{contradiction.get('worsening', 'N/A')}**\n"
                output += f"   - {contradiction.get('description', 'N/A')}\n"
                if contradiction.get('source') and contradiction['source'] != 'analysis':
                    output += f"   - *Source: {contradiction['source']}*\n"
            output += "\n"

        # Recommended principles with rich metadata
        if "recommended_principles" in data and data["recommended_principles"]:
            output += "### 💡 Recommended TRIZ Principles\n\n"
            for principle in data["recommended_principles"][:5]:
                p_num = principle.get('number', 'N/A')
                p_name = principle.get('name', 'Unknown')
                p_score = principle.get('relevance_score', 0.0)

                output += f"#### Principle {p_num}: {p_name}\n"
                output += f"**Relevance**: {p_score:.0%} | "
                output += f"**Usage**: {principle.get('usage_frequency', 'medium').title()} | "
                output += f"**Innovation Level**: {principle.get('innovation_level', 3)}/5\n\n"

                output += f"{principle.get('description', 'No description')[:200]}...\n\n"

                # Show sources where this principle was found
                if principle.get('sources'):
                    sources = principle['sources'][:3]  # Limit to 3
                    output += f"*Found in: {', '.join(sources)}*\n\n"

                # Show domains
                if principle.get('domains'):
                    output += f"*Applicable domains: {', '.join(principle['domains'][:3])}*\n\n"

                # Show examples
                if principle.get('examples'):
                    output += f"**Example**: {principle['examples'][0]}\n\n"

                output += "---\n\n"

        # Cross-Domain Analogies
        if "cross_domain_analogies" in data and data["cross_domain_analogies"]:
            output += "### 🌐 Cross-Domain Insights\n\n"
            for i, analogy in enumerate(data["cross_domain_analogies"][:3], 1):
                output += f"{i}. **From {analogy.get('source_domain', 'Unknown').title()}**\n"
                output += f"   {analogy.get('description', 'N/A')[:150]}...\n"
                output += f"   *Relevance: {analogy.get('relevance_score', 0.0):.0%}*\n"
                if analogy.get('source_reference'):
                    output += f"   *Source: {analogy['source_reference']}*\n"
                output += "\n"

        # Solution concepts with full research provenance
        if "solutions" in data and data["solutions"]:
            output += "### 🎨 Solution Concepts (Research-Based)\n\n"
            for i, solution in enumerate(data["solutions"], 1):
                output += f"#### Solution {i}: {solution.get('title', 'Untitled')}\n\n"

                # Confidence and feasibility
                conf = solution.get('confidence', 0.5)
                feas = solution.get('feasibility_score', 0.7)
                output += f"**Confidence**: {conf:.0%} | **Feasibility**: {feas:.0%}\n\n"

                # Description
                output += f"{solution.get('description', 'No description')}\n\n"

                # Applied principles
                if solution.get('principle_names'):
                    output += f"**Applied Principles**: {', '.join(solution['principle_names'])}\n\n"

                # Research Support - THIS IS THE KEY INNOVATION
                if solution.get('research_support'):
                    output += "**📚 Research Support**:\n"
                    for support in solution['research_support'][:3]:
                        output += f"- *{support.get('source', 'Unknown')}*: \"{support.get('excerpt', 'N/A')[:100]}...\"\n"
                        output += f"  (Relevance: {support.get('relevance', 0.0):.0%})\n"
                    output += "\n"

                # Cross-domain insights for this solution
                if solution.get('cross_domain_insights'):
                    output += "**🔗 Cross-Domain Insights**:\n"
                    for insight in solution['cross_domain_insights'][:2]:
                        domain = insight.get('domain', 'unknown')
                        desc = insight.get('insight', 'N/A')[:80]
                        output += f"- From {domain}: {desc}...\n"
                    output += "\n"

                # Pros and Cons
                if solution.get('pros'):
                    output += "**Pros**:\n"
                    for pro in solution['pros'][:3]:
                        output += f"- {pro}\n"
                    output += "\n"

                if solution.get('cons'):
                    output += "**Cons**:\n"
                    for con in solution['cons'][:3]:
                        output += f"- {con}\n"
                    output += "\n"

                # Implementation Hints
                if solution.get('implementation_hints'):
                    output += "**Implementation Hints**:\n"
                    for hint in solution['implementation_hints'][:3]:
                        output += f"- {hint}\n"
                    output += "\n"

                # Citations
                if solution.get('citations'):
                    citations = solution['citations'][:5]
                    output += f"**Citations**: {', '.join(citations)}\n\n"

                output += "---\n\n"

        # Knowledge Gaps (if any)
        if "research_depth" in data and data["research_depth"].get('knowledge_gaps'):
            gaps = data["research_depth"]['knowledge_gaps']
            if gaps:
                output += "### 🔍 Knowledge Gaps Identified\n"
                for gap in gaps[:3]:
                    output += f"- {gap}\n"
                output += "\n*Consider additional research in these areas*\n\n"

        # Fallback mode indicator
        if data.get('fallback_mode'):
            output += "---\n\n"
            output += "⚠️ *Note: Deep research unavailable, using fallback analysis*\n"

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
