"""
Unit Tests for Claude Command Parser (TASK-029)
"""

import pytest
from claude_tools.parser import ClaudeCommandParser, ParsedCommand


class TestClaudeCommandParser:
    """Test suite for Claude command parsing"""

    def test_parse_workflow_start(self):
        """Test parsing workflow start command"""
        result = ClaudeCommandParser.parse("/triz-workflow")

        assert result.is_valid
        assert result.tool_name == "triz_workflow_start"
        assert result.parameters == {}
        assert result.error_message is None

    def test_parse_workflow_continue(self):
        """Test parsing workflow continue command"""
        result = ClaudeCommandParser.parse(
            "/triz-workflow continue abc-123 my problem description"
        )

        assert result.is_valid
        assert result.tool_name == "triz_workflow_continue"
        assert result.parameters["session_id"] == "abc-123"
        assert result.parameters["user_input"] == "my problem description"

    def test_parse_solve_command(self):
        """Test parsing solve command"""
        problem = "reduce weight while maintaining strength"
        result = ClaudeCommandParser.parse(f"/triz-solve {problem}")

        assert result.is_valid
        assert result.tool_name == "triz_solve"
        assert result.parameters["problem"] == problem

    def test_parse_solve_command_too_long(self):
        """Test parsing solve command with problem too long"""
        problem = "x" * 2001
        result = ClaudeCommandParser.parse(f"/triz-solve {problem}")

        assert not result.is_valid
        assert "exceeds 2000 character limit" in result.error_message

    def test_parse_get_principle(self):
        """Test parsing get principle command"""
        result = ClaudeCommandParser.parse("/triz-tool get-principle 15")

        assert result.is_valid
        assert result.tool_name == "triz_get_principle"
        assert result.parameters["principle_number"] == 15

    def test_parse_get_principle_invalid_range(self):
        """Test parsing get principle with invalid number"""
        result = ClaudeCommandParser.parse("/triz-tool get-principle 41")

        assert not result.is_valid
        assert "must be between 1 and 40" in result.error_message

    def test_parse_contradiction_matrix(self):
        """Test parsing contradiction matrix command"""
        result = ClaudeCommandParser.parse(
            "/triz-tool contradiction-matrix --improving 2 --worsening 14"
        )

        assert result.is_valid
        assert result.tool_name == "triz_contradiction_matrix"
        assert result.parameters["improving_parameter"] == 2
        assert result.parameters["worsening_parameter"] == 14

    def test_parse_contradiction_matrix_invalid(self):
        """Test parsing contradiction matrix with invalid parameters"""
        result = ClaudeCommandParser.parse(
            "/triz-tool contradiction-matrix --improving 50 --worsening 14"
        )

        assert not result.is_valid
        assert "must be between 1 and 39" in result.error_message

    def test_parse_brainstorm(self):
        """Test parsing brainstorm command"""
        result = ClaudeCommandParser.parse(
            '/triz-tool brainstorm --principle 15 --context "improve flexibility"'
        )

        assert result.is_valid
        assert result.tool_name == "triz_brainstorm"
        assert result.parameters["principle_number"] == 15
        assert result.parameters["context"] == "improve flexibility"

    def test_parse_unknown_command(self):
        """Test parsing unknown command"""
        result = ClaudeCommandParser.parse("/triz-unknown-command")

        assert not result.is_valid
        assert result.tool_name == "unknown"
        assert "Unrecognized command" in result.error_message

    def test_suggest_correction_workflow(self):
        """Test command correction suggestion for workflow"""
        suggestion = ClaudeCommandParser.suggest_correction("/triz workflow")

        assert suggestion == "/triz-workflow"

    def test_suggest_correction_principle(self):
        """Test command correction suggestion for principle"""
        suggestion = ClaudeCommandParser.suggest_correction("get principle 15")

        assert "/triz-tool get-principle" in suggestion

    def test_validate_parameters_get_principle(self):
        """Test parameter validation for get_principle"""
        valid, error = ClaudeCommandParser.validate_parameters(
            "triz_get_principle",
            {"principle_number": 15}
        )

        assert valid
        assert error is None

        valid, error = ClaudeCommandParser.validate_parameters(
            "triz_get_principle",
            {"principle_number": 50}
        )

        assert not valid
        assert "between 1 and 40" in error

    def test_validate_parameters_solve(self):
        """Test parameter validation for solve"""
        valid, error = ClaudeCommandParser.validate_parameters(
            "triz_solve",
            {"problem": "my problem"}
        )

        assert valid
        assert error is None

        valid, error = ClaudeCommandParser.validate_parameters(
            "triz_solve",
            {"problem": "x" * 2001}
        )

        assert not valid
        assert "exceeds 2000 character limit" in error
