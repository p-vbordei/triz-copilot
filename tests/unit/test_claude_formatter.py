"""
Unit Tests for Claude Response Formatter (TASK-030)
"""

import pytest
from triz_tools.models import TRIZToolResponse, WorkflowStage
from claude_tools.formatter import ClaudeResponseFormatter


class TestClaudeResponseFormatter:
    """Test suite for Claude response formatting"""

    def test_format_error_response(self):
        """Test formatting error response"""
        response = TRIZToolResponse(
            success=False,
            message="Something went wrong",
            data={}
        )

        formatted = ClaudeResponseFormatter.format_tool_response(response)

        assert "❌ Error" in formatted
        assert "Something went wrong" in formatted

    def test_format_workflow_response(self):
        """Test formatting workflow response"""
        response = TRIZToolResponse(
            success=True,
            message="Workflow started",
            data={
                "next_prompt": "Please describe your problem",
                "available_commands": ["continue", "reset"]
            },
            session_id="test-123",
            stage=WorkflowStage.PROBLEM_DEFINITION
        )

        formatted = ClaudeResponseFormatter.format_tool_response(response)

        assert "TRIZ Workflow" in formatted
        assert "Problem Definition" in formatted
        assert "Step 1 of 6" in formatted
        assert "test-123" in formatted
        assert "Please describe your problem" in formatted

    def test_format_principle_response_single(self):
        """Test formatting single principle response"""
        response = TRIZToolResponse(
            success=True,
            message="Principle retrieved",
            data={
                "principle": {
                    "number": 15,
                    "name": "Dynamics",
                    "description": "Allow characteristics to change",
                    "examples": ["Adjustable steering wheel", "Flexible hose"],
                    "sub_principles": [
                        {"name": "A", "description": "Make it adjustable"}
                    ]
                }
            }
        )

        formatted = ClaudeResponseFormatter.format_tool_response(response)

        assert "Principle 15: Dynamics" in formatted
        assert "Allow characteristics to change" in formatted
        assert "Adjustable steering wheel" in formatted
        assert "Make it adjustable" in formatted

    def test_format_principle_response_multiple(self):
        """Test formatting multiple principles response"""
        response = TRIZToolResponse(
            success=True,
            message="Principles found",
            data={
                "principles": [
                    {
                        "number": 1,
                        "name": "Segmentation",
                        "description": "Divide object into parts"
                    },
                    {
                        "number": 2,
                        "name": "Taking Out",
                        "description": "Extract troubling part"
                    }
                ]
            }
        )

        formatted = ClaudeResponseFormatter.format_tool_response(response)

        assert "Recommended TRIZ Principles" in formatted
        assert "1. Segmentation" in formatted
        assert "2. Taking Out" in formatted

    def test_format_solve_response(self):
        """Test formatting solve response"""
        response = TRIZToolResponse(
            success=True,
            message="Analysis complete",
            data={
                "problem_summary": "Reduce weight while maintaining strength",
                "contradictions": [
                    {"description": "Weight vs Strength"}
                ],
                "recommended_principles": [
                    {
                        "number": 1,
                        "name": "Segmentation",
                        "description": "Divide the object" * 10
                    }
                ],
                "solutions": [
                    {
                        "title": "Hollow Structure",
                        "description": "Use hollow tubes",
                        "principle": 1
                    }
                ]
            }
        )

        formatted = ClaudeResponseFormatter.format_tool_response(response)

        assert "TRIZ Solution Analysis" in formatted
        assert "Problem Summary" in formatted
        assert "Identified Contradictions" in formatted
        assert "Recommended TRIZ Principles" in formatted
        assert "Solution Concepts" in formatted
        assert "Hollow Structure" in formatted

    def test_format_help_text(self):
        """Test formatting help text"""
        help_text = ClaudeResponseFormatter.format_help_text()

        assert "TRIZ Co-Pilot Commands" in help_text
        assert "Workflow Mode" in help_text
        assert "Autonomous Solve Mode" in help_text
        assert "Direct Tool Access" in help_text
        assert "/triz-workflow" in help_text
        assert "/triz-solve" in help_text
        assert "/triz-tool get-principle" in help_text

    def test_get_stage_number(self):
        """Test getting stage numbers"""
        assert ClaudeResponseFormatter._get_stage_number(
            WorkflowStage.PROBLEM_DEFINITION
        ) == 1
        assert ClaudeResponseFormatter._get_stage_number(
            WorkflowStage.CONTRADICTION_ANALYSIS
        ) == 2
        assert ClaudeResponseFormatter._get_stage_number(
            WorkflowStage.EVALUATION
        ) == 5

    def test_get_stage_title(self):
        """Test getting stage titles"""
        title = ClaudeResponseFormatter._get_stage_title(
            WorkflowStage.PROBLEM_DEFINITION
        )
        assert title == "Problem Definition"

        title = ClaudeResponseFormatter._get_stage_title(
            WorkflowStage.SOLUTION_GENERATION
        )
        assert title == "Solution Generation"
