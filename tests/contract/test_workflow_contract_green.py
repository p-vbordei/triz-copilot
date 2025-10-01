"""
Contract tests for TRIZ workflow commands - GREEN phase.
These tests should PASS with the implementation.
"""

import pytest
from typing import Dict, Any

# Import actual implementations
from src.triz_tools.workflow_tools import (
    triz_workflow_start,
    triz_workflow_continue,
    triz_workflow_reset,
)
from src.triz_tools.models import (
    TRIZToolResponse,
    WorkflowStage,
    WorkflowType,
)


class TestTRIZWorkflowContract:
    """Contract tests for /triz-workflow command - should PASS"""

    def test_workflow_start_contract(self):
        """Test /triz-workflow start command contract"""
        # ACT
        response = triz_workflow_start()

        # ASSERT - These should all pass now
        assert isinstance(response, TRIZToolResponse)
        assert response.success is True
        assert response.stage == WorkflowStage.PROBLEM_DEFINITION
        assert "session_id" in response.data
        assert len(response.data["session_id"]) > 0
        assert "next_prompt" in response.data
        assert "describe your" in response.data["next_prompt"].lower()
        assert "available_commands" in response.data
        assert "continue" in response.data["available_commands"]
        assert "reset" in response.data["available_commands"]

    def test_workflow_continue_contract(self):
        """Test /triz-workflow continue command contract"""
        # ARRANGE - First create a session
        start_response = triz_workflow_start()
        session_id = start_response.data["session_id"]
        user_input = "Design a lightweight but strong automotive component"

        # ACT
        response = triz_workflow_continue(session_id, user_input)

        # ASSERT
        assert isinstance(response, TRIZToolResponse)
        assert response.success is True
        assert response.session_id == session_id
        assert response.stage in list(WorkflowStage)
        assert "next_prompt" in response.data or response.stage == WorkflowStage.COMPLETED

    def test_workflow_reset_contract(self):
        """Test /triz-workflow reset command contract"""
        # ARRANGE - Create and advance a session
        start_response = triz_workflow_start()
        session_id = start_response.data["session_id"]
        triz_workflow_continue(session_id, "test problem")

        # ACT
        response = triz_workflow_reset(session_id)

        # ASSERT
        assert isinstance(response, TRIZToolResponse)
        assert response.success is True
        assert response.stage == WorkflowStage.PROBLEM_DEFINITION
        assert response.session_id == session_id
        assert "reset" in response.message.lower()

    def test_workflow_invalid_session(self):
        """Test handling of invalid session IDs"""
        # ARRANGE
        invalid_session_id = "non-existent-session"

        # ACT
        response = triz_workflow_continue(invalid_session_id, "test input")

        # ASSERT
        assert response.success is False
        assert "not found" in response.message.lower()

    def test_workflow_stage_progression(self):
        """Test that workflow stages progress correctly"""
        # ARRANGE
        response = triz_workflow_start()
        session_id = response.data["session_id"]
        
        # ACT & ASSERT - Progress through stages
        assert response.stage == WorkflowStage.PROBLEM_DEFINITION
        
        # Continue to next stage
        response = triz_workflow_continue(session_id, "Problem: reduce weight")
        assert response.stage == WorkflowStage.CONTRADICTION_ANALYSIS
        
        # Continue again
        response = triz_workflow_continue(session_id, "IFR: weightless but strong")
        assert response.stage == WorkflowStage.PRINCIPLE_SELECTION