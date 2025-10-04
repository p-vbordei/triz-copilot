#!/usr/bin/env python3
"""
Gemini CLI MCP Server for TRIZ Co-Pilot
Provides proper MCP protocol integration with tool schemas and file persistence
"""

import asyncio
import sys
from pathlib import Path
from typing import Any, Sequence

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import logging

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from claude_tools.async_utils import run_sync
from claude_tools.formatter import ClaudeResponseFormatter
from claude_tools.workflow_handler import (
    handle_workflow_start,
    handle_workflow_continue,
)
from claude_tools.solve_handler import handle_solve
from claude_tools.direct_handler import (
    handle_get_principle,
    handle_contradiction_matrix,
    handle_brainstorm,
)

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("gemini_mcp_server")

# Create MCP server instance
app = Server("triz-copilot-gemini")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List all available TRIZ tools for Gemini"""
    return [
        Tool(
            name="triz_workflow_start",
            description="Start a guided TRIZ problem-solving workflow with step-by-step guidance through all 60 steps. This interactive workflow guides you through: problem formulation, contradiction identification (technical and physical), solution generation using TRIZ principles, materials research (if applicable - searches 44+ engineering books with 1,135 chunks), and implementation planning. The workflow adapts based on your problem type. For materials problems, it automatically performs deep research from materials engineering books with property extraction and comparison tables. ALL STEPS ARE LOGGED TO FILES for context recovery.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
        Tool(
            name="triz_workflow_continue",
            description="Continue an existing TRIZ workflow session with user input. Each step is automatically saved to a log file so sessions can be recovered even if context is lost.",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "The session ID from workflow_start",
                    },
                    "user_input": {
                        "type": "string",
                        "description": "User's response to the current workflow prompt",
                    },
                },
                "required": ["session_id", "user_input"],
            },
        ),
        Tool(
            name="triz_solve",
            description="⚠️ DEPRECATED - USE triz_research_start INSTEAD. This autonomous solver is a SHORTCUT that bypasses proper TRIZ methodology. For correct TRIZ problem solving, you MUST use triz_research_start which guides you through 60 systematic research steps.",
            inputSchema={
                "type": "object",
                "properties": {
                    "problem": {
                        "type": "string",
                        "description": "⚠️ DO NOT USE - Use triz_research_start instead for proper 60-step methodology",
                    },
                },
                "required": ["problem"],
            },
        ),
        Tool(
            name="triz_get_principle",
            description="Get detailed information about a specific TRIZ inventive principle by number",
            inputSchema={
                "type": "object",
                "properties": {
                    "principle_number": {
                        "type": "integer",
                        "description": "TRIZ principle number (1-40)",
                        "minimum": 1,
                        "maximum": 40,
                    },
                },
                "required": ["principle_number"],
            },
        ),
        Tool(
            name="triz_contradiction_matrix",
            description="Query the TRIZ contradiction matrix for principle recommendations",
            inputSchema={
                "type": "object",
                "properties": {
                    "improving_parameter": {
                        "type": "integer",
                        "description": "Parameter to improve (1-39)",
                        "minimum": 1,
                        "maximum": 39,
                    },
                    "worsening_parameter": {
                        "type": "integer",
                        "description": "Parameter that worsens (1-39)",
                        "minimum": 1,
                        "maximum": 39,
                    },
                },
                "required": ["improving_parameter", "worsening_parameter"],
            },
        ),
        Tool(
            name="triz_brainstorm",
            description="Generate contextual ideas by applying a specific TRIZ principle to a problem",
            inputSchema={
                "type": "object",
                "properties": {
                    "principle_number": {
                        "type": "integer",
                        "description": "TRIZ principle number (1-40)",
                        "minimum": 1,
                        "maximum": 40,
                    },
                    "context": {
                        "type": "string",
                        "description": "Problem context for generating ideas",
                    },
                },
                "required": ["principle_number", "context"],
            },
        ),
        Tool(
            name="triz_solve_complete",
            description="⚠️ DEPRECATED - USE triz_research_start INSTEAD. This 8-phase solver is a SHORTCUT that provides instant answers without proper research methodology. For correct academic TRIZ problem solving, you MUST use triz_research_start which guides you through 60 systematic research steps where YOU perform the research and discover the solution. This tool remains only for legacy compatibility and quick reference checking, but should NOT be used for actual problem solving. The 60-step methodology is the only acceptable approach for real TRIZ analysis.",
            inputSchema={
                "type": "object",
                "properties": {
                    "problem": {
                        "type": "string",
                        "description": "⚠️ DO NOT USE - Use triz_research_start instead for proper 60-step guided research methodology",
                    }
                },
                "required": ["problem"],
            },
        ),
        Tool(
            name="triz_research_start",
            description="✅ REQUIRED METHOD - Start guided TRIZ research session with 60-step iterative methodology. This is the ONLY acceptable way to solve TRIZ problems properly. Returns session_id and Step 1 research instructions. ALL STEPS ARE LOGGED TO FILES so you can recover from context loss.",
            inputSchema={
                "type": "object",
                "properties": {
                    "problem": {
                        "type": "string",
                        "description": "Detailed problem description. Include: what you're trying to achieve, current limitations, constraints, available resources, and success criteria.",
                    }
                },
                "required": ["problem"],
            },
        ),
        Tool(
            name="triz_research_submit",
            description="Submit research findings for current TRIZ research step and receive next step instructions (or final solution if step 60). You must provide findings dictionary matching the extract_requirements from previous step's instruction. The tool validates your findings - if validation fails, you'll receive hints and must research again. If validation succeeds, you receive next step instructions. This continues for all 60 steps. The final step (60) returns complete TRIZ solution with all evidence from your research. IMPORTANT: Findings must be a dictionary/object with keys matching the extract_requirements list from the current step instruction. EXAMPLE for Step 1 (9 Boxes): If extract_requirements is ['sub_system_past', 'sub_system_present', 'sub_system_future', 'system_past', 'system_present', 'system_future', 'super_system_past', 'super_system_present', 'super_system_future'], then findings must be: {'sub_system_past': ['Steel brackets with rivets', 'Multiple fasteners'], 'sub_system_present': ['Aluminum-CFRP hybrid', 'Bearing assemblies'], 'sub_system_future': ['Thermoplastic composites', 'Self-healing polymers'], 'system_past': ['Heavy steel assemblies'], 'system_present': ['Hybrid aluminum/CFRP assembly'], 'system_future': ['Single-piece formable composites'], 'super_system_past': ['Industrial robots'], 'super_system_present': ['Mobile household robots'], 'super_system_future': ['Autonomous home assistants']}. Each field must contain detailed, researched information as arrays or objects per the expected_output_format shown in step instructions. Each submission is logged to file for persistence and traceability.",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Session ID from triz_research_start",
                    },
                    "findings": {
                        "type": "object",
                        "description": "Research findings dictionary with keys matching extract_requirements from current step instruction. Must include all required fields with detailed information from knowledge base research. Follow the expected_output_format structure shown in step instructions exactly.",
                    },
                },
                "required": ["session_id", "findings"],
            },
        ),
        Tool(
            name="triz_health_check",
            description="Check the health and status of the TRIZ system",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> Sequence[TextContent]:
    """Handle tool invocation requests"""
    try:
        logger.info(f"Tool called: {name}", extra={"arguments": arguments})

        # Route to appropriate handler
        if name == "triz_workflow_start":
            result = await run_sync(handle_workflow_start)

        elif name == "triz_workflow_continue":
            session_id = arguments.get("session_id")
            user_input = arguments.get("user_input")
            if not session_id or not user_input:
                return [
                    TextContent(
                        type="text",
                        text="Error: session_id and user_input are required",
                    )
                ]
            result = await run_sync(handle_workflow_continue, session_id, user_input)

        elif name == "triz_solve":
            problem = arguments.get("problem")
            if not problem:
                return [
                    TextContent(
                        type="text", text="Error: problem description is required"
                    )
                ]
            result = await run_sync(handle_solve, problem)

        elif name == "triz_get_principle":
            principle_number = arguments.get("principle_number")
            if not principle_number:
                return [
                    TextContent(type="text", text="Error: principle_number is required")
                ]
            result = await run_sync(handle_get_principle, principle_number)

        elif name == "triz_contradiction_matrix":
            improving = arguments.get("improving_parameter")
            worsening = arguments.get("worsening_parameter")
            if not improving or not worsening:
                return [
                    TextContent(
                        type="text",
                        text="Error: improving_parameter and worsening_parameter are required",
                    )
                ]
            result = await run_sync(handle_contradiction_matrix, improving, worsening)

        elif name == "triz_brainstorm":
            principle_number = arguments.get("principle_number")
            context = arguments.get("context")
            if not principle_number or not context:
                return [
                    TextContent(
                        type="text",
                        text="Error: principle_number and context are required",
                    )
                ]
            result = await run_sync(handle_brainstorm, principle_number, context)

        elif name == "triz_solve_complete":
            from claude_tools.complete_handler import handle_solve_complete

            problem = arguments.get("problem")
            if not problem:
                return [
                    TextContent(
                        type="text",
                        text="Error: problem description is required",
                    )
                ]
            result = await run_sync(handle_solve_complete, problem)

        elif name == "triz_research_start":
            from claude_tools.guided_handler import handle_research_start

            problem = arguments.get("problem")
            if not problem:
                return [
                    TextContent(
                        type="text", text="Error: problem description is required"
                    )
                ]
            result = await run_sync(handle_research_start, problem)

        elif name == "triz_research_submit":
            from claude_tools.guided_handler import handle_research_submit

            session_id = arguments.get("session_id")
            findings = arguments.get("findings")
            if not session_id or not findings:
                return [
                    TextContent(
                        type="text",
                        text="Error: session_id and findings are required",
                    )
                ]
            result = await run_sync(handle_research_submit, session_id, findings)

        elif name == "triz_health_check":
            from triz_tools.health_checks import check_system_health

            result = await run_sync(check_system_health)

        else:
            return [TextContent(type="text", text=f"Error: Unknown tool '{name}'")]

        # Format and return response
        formatted = ClaudeResponseFormatter.format_tool_response(result)
        logger.info(f"Tool completed: {name}", extra={"success": result.success})

        return [TextContent(type="text", text=formatted)]

    except Exception as e:
        logger.error(f"Error calling tool {name}: {str(e)}", exc_info=True)
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def main():
    """Run the MCP server"""
    logger.info("Starting TRIZ Co-Pilot MCP Server for Gemini")

    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
