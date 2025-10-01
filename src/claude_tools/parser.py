"""
Command Parser (TASK-006)
Parse Claude CLI commands for TRIZ tools
"""

import re
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass


@dataclass
class ParsedCommand:
    """Parsed command structure"""
    tool_name: str
    parameters: Dict[str, Any]
    is_valid: bool
    error_message: Optional[str] = None


class ClaudeCommandParser:
    """Parse commands from Claude CLI format to TRIZ tool calls"""

    # Command patterns
    PATTERNS = {
        'workflow_start': r'^/triz-workflow$',
        'workflow_continue': r'^/triz-workflow\s+continue\s+(\S+)(?:\s+(.+))?$',
        'solve': r'^/triz-solve\s+(.+)$',
        'get_principle': r'^/triz-tool\s+get-principle\s+(\d+)$',
        'contradiction_matrix': r'^/triz-tool\s+contradiction-matrix\s+--improving\s+(\d+)\s+--worsening\s+(\d+)$',
        'brainstorm': r'^/triz-tool\s+brainstorm\s+--principle\s+(\d+)\s+--context\s+"(.+)"$',
    }

    @classmethod
    def parse(cls, command: str) -> ParsedCommand:
        """
        Parse a command string into a structured command

        Args:
            command: Command string from Claude CLI

        Returns:
            ParsedCommand with tool name and parameters
        """
        command = command.strip()

        # Try to match each pattern
        for name, pattern in cls.PATTERNS.items():
            match = re.match(pattern, command, re.DOTALL)
            if match:
                return cls._build_result(name, match)

        # No match found
        return ParsedCommand(
            tool_name="unknown",
            parameters={},
            is_valid=False,
            error_message=f"Unrecognized command: {command}"
        )

    @classmethod
    def _build_result(cls, command_name: str, match: re.Match) -> ParsedCommand:
        """Build parsed command result from regex match"""

        if command_name == 'workflow_start':
            return ParsedCommand(
                tool_name="triz_workflow_start",
                parameters={},
                is_valid=True
            )

        elif command_name == 'workflow_continue':
            session_id = match.group(1)
            user_input = match.group(2) or ""
            return ParsedCommand(
                tool_name="triz_workflow_continue",
                parameters={
                    "session_id": session_id,
                    "user_input": user_input
                },
                is_valid=True
            )

        elif command_name == 'solve':
            problem = match.group(1)
            if len(problem) > 2000:
                return ParsedCommand(
                    tool_name="triz_solve",
                    parameters={},
                    is_valid=False,
                    error_message="Problem description exceeds 2000 character limit"
                )
            return ParsedCommand(
                tool_name="triz_solve",
                parameters={"problem": problem},
                is_valid=True
            )

        elif command_name == 'get_principle':
            principle_num = int(match.group(1))
            if not 1 <= principle_num <= 40:
                return ParsedCommand(
                    tool_name="triz_get_principle",
                    parameters={},
                    is_valid=False,
                    error_message=f"Principle number must be between 1 and 40, got {principle_num}"
                )
            return ParsedCommand(
                tool_name="triz_get_principle",
                parameters={"principle_number": principle_num},
                is_valid=True
            )

        elif command_name == 'contradiction_matrix':
            improving = int(match.group(1))
            worsening = int(match.group(2))
            errors = []
            if not 1 <= improving <= 39:
                errors.append(f"Improving parameter must be between 1 and 39, got {improving}")
            if not 1 <= worsening <= 39:
                errors.append(f"Worsening parameter must be between 1 and 39, got {worsening}")

            if errors:
                return ParsedCommand(
                    tool_name="triz_contradiction_matrix",
                    parameters={},
                    is_valid=False,
                    error_message="; ".join(errors)
                )

            return ParsedCommand(
                tool_name="triz_contradiction_matrix",
                parameters={
                    "improving_parameter": improving,
                    "worsening_parameter": worsening
                },
                is_valid=True
            )

        elif command_name == 'brainstorm':
            principle_num = int(match.group(1))
            context = match.group(2)

            if not 1 <= principle_num <= 40:
                return ParsedCommand(
                    tool_name="triz_brainstorm",
                    parameters={},
                    is_valid=False,
                    error_message=f"Principle number must be between 1 and 40, got {principle_num}"
                )

            return ParsedCommand(
                tool_name="triz_brainstorm",
                parameters={
                    "principle_number": principle_num,
                    "context": context
                },
                is_valid=True
            )

        return ParsedCommand(
            tool_name="unknown",
            parameters={},
            is_valid=False,
            error_message=f"Failed to parse command: {command_name}"
        )

    @classmethod
    def suggest_correction(cls, command: str) -> Optional[str]:
        """Suggest a corrected command for common mistakes"""
        command = command.lower().strip()

        if 'workflow' in command:
            return "/triz-workflow"
        elif 'solve' in command:
            return "/triz-solve [your problem description]"
        elif 'principle' in command:
            return "/triz-tool get-principle [1-40]"
        elif 'contradiction' in command or 'matrix' in command:
            return "/triz-tool contradiction-matrix --improving [1-39] --worsening [1-39]"
        elif 'brainstorm' in command:
            return '/triz-tool brainstorm --principle [1-40] --context "your problem"'

        return None

    @classmethod
    def validate_parameters(
        cls,
        tool_name: str,
        parameters: Dict[str, Any]
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate parameters for a tool call

        Returns:
            (is_valid, error_message)
        """
        if tool_name == "triz_get_principle":
            num = parameters.get("principle_number")
            if not isinstance(num, int) or not 1 <= num <= 40:
                return False, "Principle number must be an integer between 1 and 40"

        elif tool_name == "triz_contradiction_matrix":
            improving = parameters.get("improving_parameter")
            worsening = parameters.get("worsening_parameter")
            if not isinstance(improving, int) or not 1 <= improving <= 39:
                return False, "Improving parameter must be an integer between 1 and 39"
            if not isinstance(worsening, int) or not 1 <= worsening <= 39:
                return False, "Worsening parameter must be an integer between 1 and 39"

        elif tool_name == "triz_solve":
            problem = parameters.get("problem")
            if not problem or not isinstance(problem, str):
                return False, "Problem description is required and must be a string"
            if len(problem) > 2000:
                return False, "Problem description exceeds 2000 character limit"

        elif tool_name == "triz_workflow_continue":
            session_id = parameters.get("session_id")
            user_input = parameters.get("user_input")
            if not session_id or not isinstance(session_id, str):
                return False, "Session ID is required and must be a string"
            if not user_input or not isinstance(user_input, str):
                return False, "User input is required and must be a string"

        elif tool_name == "triz_brainstorm":
            num = parameters.get("principle_number")
            context = parameters.get("context")
            if not isinstance(num, int) or not 1 <= num <= 40:
                return False, "Principle number must be an integer between 1 and 40"
            if not context or not isinstance(context, str):
                return False, "Context is required and must be a string"

        return True, None
