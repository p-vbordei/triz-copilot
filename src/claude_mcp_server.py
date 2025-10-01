#!/usr/bin/env python3
"""
Claude MCP Server for TRIZ Co-Pilot (TASK-002, TASK-003)
Main server implementing Model Context Protocol for Claude CLI integration
"""

import asyncio
import sys
from typing import Any, Sequence

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    CallToolResult,
    INVALID_PARAMS,
    INTERNAL_ERROR,
)

from claude_tools.async_utils import run_sync
from claude_tools.formatter import ClaudeResponseFormatter
from claude_tools.workflow_handler import handle_workflow_start, handle_workflow_continue
from claude_tools.solve_handler import handle_solve
from claude_tools.direct_handler import (
    handle_get_principle,
    handle_contradiction_matrix,
    handle_brainstorm,
)
from triz_tools.logging_config import setup_logging


# Setup logging
logger = setup_logging("claude_mcp_server")

# Create MCP server instance
app = Server("triz-copilot")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List all available TRIZ tools for Claude"""
    return [
        Tool(
            name="triz_workflow_start",
            description="Start a guided TRIZ problem-solving workflow with step-by-step guidance through all stages",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
        Tool(
            name="triz_workflow_continue",
            description="Continue an existing TRIZ workflow session with user input",
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
            description="Perform autonomous TRIZ analysis on a problem description and return complete solution report",
            inputSchema={
                "type": "object",
                "properties": {
                    "problem": {
                        "type": "string",
                        "description": "Technical problem description (up to 2000 characters)",
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
                return [TextContent(
                    type="text",
                    text="Error: session_id and user_input are required"
                )]
            result = await run_sync(handle_workflow_continue, session_id, user_input)

        elif name == "triz_solve":
            problem = arguments.get("problem")
            if not problem:
                return [TextContent(type="text", text="Error: problem description is required")]
            result = await run_sync(handle_solve, problem)

        elif name == "triz_get_principle":
            principle_number = arguments.get("principle_number")
            if not principle_number:
                return [TextContent(type="text", text="Error: principle_number is required")]
            result = await run_sync(handle_get_principle, principle_number)

        elif name == "triz_contradiction_matrix":
            improving = arguments.get("improving_parameter")
            worsening = arguments.get("worsening_parameter")
            if not improving or not worsening:
                return [TextContent(
                    type="text",
                    text="Error: improving_parameter and worsening_parameter are required"
                )]
            result = await run_sync(handle_contradiction_matrix, improving, worsening)

        elif name == "triz_brainstorm":
            principle_number = arguments.get("principle_number")
            context = arguments.get("context")
            if not principle_number or not context:
                return [TextContent(
                    type="text",
                    text="Error: principle_number and context are required"
                )]
            result = await run_sync(handle_brainstorm, principle_number, context)

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
    logger.info("Starting TRIZ Co-Pilot MCP Server for Claude")

    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
