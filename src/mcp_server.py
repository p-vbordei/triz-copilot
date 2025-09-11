"""
MCP Server for TRIZ Co-Pilot Integration with Gemini CLI (T041-T045)
Provides TRIZ tools as MCP-compatible endpoints.
"""

import json
import asyncio
from typing import Dict, Any, List, Optional
from pathlib import Path
import sys
import logging

# Add src to path for imports
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

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TRIZMCPServer:
    """MCP Server for TRIZ Co-Pilot"""
    
    def __init__(self):
        self.commands = self._register_commands()
        self.sessions = {}  # Track active sessions
        
    def _register_commands(self) -> Dict[str, callable]:
        """Register all TRIZ commands for MCP"""
        return {
            # Workflow commands
            "triz-workflow": self.handle_workflow,
            "triz-workflow-start": self.handle_workflow_start,
            "triz-workflow-continue": self.handle_workflow_continue,
            "triz-workflow-reset": self.handle_workflow_reset,
            
            # Direct tool commands
            "triz-tool": self.handle_tool,
            "triz-tool-principle": self.handle_get_principle,
            "triz-tool-matrix": self.handle_contradiction_matrix,
            "triz-tool-brainstorm": self.handle_brainstorm,
            
            # Autonomous solve
            "triz-solve": self.handle_solve,
            
            # Help command
            "triz-help": self.handle_help,
        }
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Main request handler for MCP protocol"""
        try:
            command = request.get("command", "").lower()
            args = request.get("args", {})
            
            if command not in self.commands:
                return {
                    "success": False,
                    "error": f"Unknown command: {command}",
                    "available_commands": list(self.commands.keys())
                }
            
            # Execute command
            handler = self.commands[command]
            result = await handler(args)
            
            return {
                "success": True,
                "result": result
            }
            
        except Exception as e:
            logger.error(f"Error handling request: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def handle_workflow(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle /triz-workflow command with subcommands"""
        subcommand = args.get("subcommand", "").lower()
        
        if subcommand == "start":
            return await self.handle_workflow_start(args)
        elif subcommand == "continue":
            return await self.handle_workflow_continue(args)
        elif subcommand == "reset":
            return await self.handle_workflow_reset(args)
        else:
            return {
                "message": "Available workflow commands",
                "commands": [
                    "/triz-workflow start - Start new TRIZ session",
                    "/triz-workflow continue [session_id] [input] - Continue session",
                    "/triz-workflow reset [session_id] - Reset session"
                ]
            }
    
    async def handle_workflow_start(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Start new TRIZ workflow session"""
        response = triz_workflow_start()
        
        # Track session
        if response.success and response.session_id:
            self.sessions[response.session_id] = {
                "stage": response.stage.value if response.stage else None,
                "created": True
            }
        
        return {
            "success": response.success,
            "message": response.message,
            "data": response.data,
            "session_id": response.session_id,
            "stage": response.stage.value if response.stage else None
        }
    
    async def handle_workflow_continue(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Continue TRIZ workflow session"""
        session_id = args.get("session_id", "")
        user_input = args.get("input", "")
        
        if not session_id:
            return {
                "success": False,
                "error": "session_id required"
            }
        
        response = triz_workflow_continue(session_id, user_input)
        
        return {
            "success": response.success,
            "message": response.message,
            "data": response.data,
            "session_id": response.session_id,
            "stage": response.stage.value if response.stage else None
        }
    
    async def handle_workflow_reset(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Reset TRIZ workflow session"""
        session_id = args.get("session_id", "")
        
        if not session_id:
            return {
                "success": False,
                "error": "session_id required"
            }
        
        response = triz_workflow_reset(session_id)
        
        return {
            "success": response.success,
            "message": response.message,
            "data": response.data,
            "session_id": response.session_id,
            "stage": response.stage.value if response.stage else None
        }
    
    async def handle_tool(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle /triz-tool command with subcommands"""
        subcommand = args.get("subcommand", "").lower()
        
        if subcommand == "get-principle":
            return await self.handle_get_principle(args)
        elif subcommand == "contradiction-matrix":
            return await self.handle_contradiction_matrix(args)
        elif subcommand == "brainstorm":
            return await self.handle_brainstorm(args)
        else:
            return {
                "message": "Available tool commands",
                "commands": [
                    "/triz-tool get-principle [number] - Get TRIZ principle details",
                    "/triz-tool contradiction-matrix [improving] [worsening] - Query matrix",
                    "/triz-tool brainstorm [principle] [context] - Generate ideas"
                ]
            }
    
    async def handle_get_principle(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get TRIZ principle by number"""
        principle_number = args.get("number", 0)
        
        if not principle_number:
            return {
                "success": False,
                "error": "principle number required (1-40)"
            }
        
        try:
            principle_number = int(principle_number)
        except (ValueError, TypeError):
            return {
                "success": False,
                "error": "principle number must be an integer (1-40)"
            }
        
        response = triz_tool_get_principle(principle_number)
        
        return {
            "success": response.success,
            "message": response.message,
            "data": response.data
        }
    
    async def handle_contradiction_matrix(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Query contradiction matrix"""
        improving = args.get("improving", 0)
        worsening = args.get("worsening", 0)
        
        try:
            improving = int(improving)
            worsening = int(worsening)
        except (ValueError, TypeError):
            return {
                "success": False,
                "error": "Parameters must be integers (1-39)"
            }
        
        response = triz_tool_contradiction_matrix(improving, worsening)
        
        return {
            "success": response.success,
            "message": response.message,
            "data": response.data
        }
    
    async def handle_brainstorm(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Brainstorm using TRIZ principle"""
        principle_number = args.get("principle", 0)
        context = args.get("context", "")
        
        try:
            principle_number = int(principle_number)
        except (ValueError, TypeError):
            return {
                "success": False,
                "error": "Principle number must be an integer (1-40)"
            }
        
        response = triz_tool_brainstorm(principle_number, context)
        
        return {
            "success": response.success,
            "message": response.message,
            "data": response.data
        }
    
    async def handle_solve(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Autonomous TRIZ problem solving"""
        problem = args.get("problem", "")
        context = args.get("context", {})
        
        if not problem:
            return {
                "success": False,
                "error": "Problem description required"
            }
        
        response = triz_solve_autonomous(problem, context)
        
        return {
            "success": response.success,
            "message": response.message,
            "data": response.data
        }
    
    async def handle_help(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Show help for TRIZ commands"""
        return {
            "message": "TRIZ Co-Pilot MCP Commands",
            "commands": {
                "workflow": [
                    "/triz-workflow start - Begin guided TRIZ session",
                    "/triz-workflow continue [session_id] [input] - Continue session",
                    "/triz-workflow reset [session_id] - Reset to beginning"
                ],
                "tools": [
                    "/triz-tool get-principle [1-40] - Get principle details",
                    "/triz-tool contradiction-matrix [improving] [worsening] - Find principles",
                    "/triz-tool brainstorm [principle] [context] - Generate ideas"
                ],
                "solve": [
                    "/triz-solve [problem description] - Autonomous TRIZ analysis"
                ]
            },
            "examples": [
                "/triz-workflow start",
                "/triz-tool get-principle 1",
                "/triz-tool contradiction-matrix 1 14",
                "/triz-solve 'Reduce weight while maintaining strength'"
            ]
        }


async def run_server():
    """Run the MCP server"""
    server = TRIZMCPServer()
    logger.info("TRIZ MCP Server started")
    
    # Read from stdin, write to stdout (MCP protocol)
    while True:
        try:
            # Read JSON request from stdin
            line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
            if not line:
                break
            
            request = json.loads(line.strip())
            response = await server.handle_request(request)
            
            # Write JSON response to stdout
            print(json.dumps(response))
            sys.stdout.flush()
            
        except json.JSONDecodeError as e:
            error_response = {
                "success": False,
                "error": f"Invalid JSON: {str(e)}"
            }
            print(json.dumps(error_response))
            sys.stdout.flush()
        except KeyboardInterrupt:
            logger.info("Server shutdown requested")
            break
        except Exception as e:
            logger.error(f"Server error: {str(e)}")
            error_response = {
                "success": False,
                "error": f"Server error: {str(e)}"
            }
            print(json.dumps(error_response))
            sys.stdout.flush()


if __name__ == "__main__":
    # Run the server
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        logger.info("TRIZ MCP Server stopped")