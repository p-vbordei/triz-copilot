"""
Contract tests for TRIZ direct tools - GREEN phase.
These tests should PASS with the implementation.
"""

import pytest
from typing import Dict, Any

# Import actual implementations
from src.triz_tools.direct_tools import (
    triz_tool_get_principle,
    triz_tool_contradiction_matrix,
    triz_tool_brainstorm,
)
from src.triz_tools.models import TRIZToolResponse


class TestTRIZToolDirectContract:
    """Contract tests for /triz-tool direct access - should PASS"""

    def test_get_principle_contract(self):
        """Test /triz-tool get-principle [number] contract"""
        # ARRANGE
        principle_number = 1  # Segmentation

        # ACT
        response = triz_tool_get_principle(principle_number)

        # ASSERT
        assert isinstance(response, TRIZToolResponse)
        assert response.success is True
        assert "principle_name" in response.data
        assert "description" in response.data
        assert "examples" in response.data
        assert response.data["principle_number"] == principle_number
        assert "segmentation" in response.data["principle_name"].lower()
        assert len(response.data["examples"]) >= 3
        assert "sub_principles" in response.data
        assert len(response.data["sub_principles"]) >= 2

    def test_get_principle_invalid_number(self):
        """Test /triz-tool get-principle with invalid number"""
        # ARRANGE
        invalid_numbers = [0, 41, 99, -1]

        # ACT & ASSERT
        for invalid_number in invalid_numbers:
            response = triz_tool_get_principle(invalid_number)
            assert response.success is False
            assert "invalid principle number" in response.message.lower()
            assert "1-40" in response.message

    def test_contradiction_matrix_contract(self):
        """Test /triz-tool contradiction-matrix contract"""
        # ARRANGE
        improving_param = 1   # Weight of moving object
        worsening_param = 14  # Strength

        # ACT
        response = triz_tool_contradiction_matrix(improving_param, worsening_param)

        # ASSERT
        assert isinstance(response, TRIZToolResponse)
        assert response.success is True
        assert "recommended_principles" in response.data
        assert isinstance(response.data["recommended_principles"], list)
        assert len(response.data["recommended_principles"]) > 0
        assert all(isinstance(p, int) for p in response.data["recommended_principles"])
        assert all(1 <= p <= 40 for p in response.data["recommended_principles"])
        assert "confidence_score" in response.data
        assert 0.0 <= response.data["confidence_score"] <= 1.0

    def test_contradiction_matrix_invalid_parameters(self):
        """Test contradiction matrix with invalid parameters"""
        # ARRANGE
        invalid_cases = [
            (0, 14),  # Invalid improving parameter
            (1, 40),  # Invalid worsening parameter  
            (1, 1),   # Same parameter (no contradiction)
            (-1, 5),  # Negative parameter
        ]

        # ACT & ASSERT
        for improving, worsening in invalid_cases:
            response = triz_tool_contradiction_matrix(improving, worsening)
            assert response.success is False
            assert "range" in response.message.lower() or "same" in response.message.lower()

    def test_brainstorm_contract(self):
        """Test /triz-tool brainstorm contract"""
        # ARRANGE
        principle_number = 15  # Dynamics
        context = "Improving solar panel efficiency while reducing manufacturing cost"

        # ACT
        response = triz_tool_brainstorm(principle_number, context)

        # ASSERT
        assert isinstance(response, TRIZToolResponse)
        assert response.success is True
        assert "ideas" in response.data
        assert isinstance(response.data["ideas"], list)
        assert len(response.data["ideas"]) >= 3
        assert "principle_application" in response.data
        
        for idea in response.data["ideas"]:
            assert "title" in idea
            assert "description" in idea
            assert "how_principle_applies" in idea

    def test_brainstorm_empty_context(self):
        """Test brainstorming with empty context"""
        # ARRANGE
        principle_number = 1
        empty_context = ""

        # ACT
        response = triz_tool_brainstorm(principle_number, empty_context)

        # ASSERT
        assert response.success is False
        assert "context" in response.message.lower()

    def test_known_contradiction_matrix_entry(self):
        """Test a known contradiction matrix entry"""
        # ARRANGE
        # Weight vs Strength is a known entry in our matrix
        improving = 1  # Weight of moving object
        worsening = 14  # Strength

        # ACT
        response = triz_tool_contradiction_matrix(improving, worsening)

        # ASSERT
        assert response.success is True
        principles = response.data["recommended_principles"]
        # Should contain principles from our matrix: [1, 8, 15, 40]
        expected = [1, 8, 15, 40]
        overlap = set(principles) & set(expected)
        assert len(overlap) >= 2, f"Expected overlap with {expected}, got {principles}"