"""
Contract tests for TRIZ autonomous solve command - GREEN phase.
These tests should PASS with the implementation.
"""

import pytest
import time
from typing import Dict, List, Any

# Import actual implementations
from src.triz_tools.solve_tools import (
    triz_solve_autonomous,
)
from src.triz_tools.models import (
    TRIZToolResponse,
    SolutionConcept,
    AnalysisReport,
)


class TestTRIZSolveContract:
    """Contract tests for /triz-solve command - should PASS"""

    def test_solve_autonomous_contract(self):
        """Test /triz-solve autonomous analysis contract"""
        # ARRANGE
        problem_description = """
        We need to reduce the weight of an aircraft wing while maintaining 
        structural strength and stiffness requirements. Current aluminum 
        design is too heavy for fuel efficiency targets.
        """

        # ACT
        response = triz_solve_autonomous(problem_description)

        # ASSERT
        assert isinstance(response, TRIZToolResponse)
        assert response.success is True
        assert "problem_summary" in response.data
        assert "ideal_final_result" in response.data
        assert "contradictions_identified" in response.data
        assert "top_principles" in response.data
        assert "solution_concepts" in response.data
        assert len(response.data["solution_concepts"]) >= 3
        assert len(response.data["solution_concepts"]) <= 5
        assert "confidence_score" in response.data
        assert 0.0 <= response.data["confidence_score"] <= 1.0

    def test_solve_solution_concept_structure(self):
        """Test that solution concepts have required structure"""
        # ARRANGE
        problem = "Reduce vibration in machinery while maintaining power output"

        # ACT
        response = triz_solve_autonomous(problem)

        # ASSERT
        assert response.success is True
        for concept in response.data["solution_concepts"]:
            assert "concept_title" in concept
            assert "description" in concept
            assert "applied_principles" in concept
            assert "pros" in concept
            assert "cons" in concept
            assert "feasibility_score" in concept
            assert "innovation_level" in concept
            assert len(concept["description"]) >= 50  # Meaningful description
            assert len(concept["pros"]) >= 2
            assert len(concept["cons"]) >= 1
            assert 0.0 <= concept["feasibility_score"] <= 1.0
            assert 1 <= concept["innovation_level"] <= 5

    def test_solve_contradiction_identification(self):
        """Test that contradictions are properly identified"""
        # ARRANGE
        problem = "Increase speed of production while reducing defects"

        # ACT
        response = triz_solve_autonomous(problem)

        # ASSERT
        assert response.success is True
        contradictions = response.data["contradictions_identified"]
        assert len(contradictions) >= 1
        for contradiction in contradictions:
            assert "improving_parameter" in contradiction
            assert "worsening_parameter" in contradiction
            assert "parameter_names" in contradiction
            assert 1 <= contradiction["improving_parameter"] <= 39
            assert 1 <= contradiction["worsening_parameter"] <= 39

    def test_solve_principle_recommendations(self):
        """Test that TRIZ principles are recommended"""
        # ARRANGE
        problem = "Make system more reliable without increasing complexity"

        # ACT
        response = triz_solve_autonomous(problem)

        # ASSERT
        assert response.success is True
        principles = response.data["top_principles"]
        assert len(principles) >= 3
        assert len(principles) <= 5
        for principle in principles:
            assert "principle_id" in principle
            assert "principle_name" in principle
            assert "relevance_score" in principle
            assert "explanation" in principle
            assert 1 <= principle["principle_id"] <= 40
            assert 0.0 <= principle["relevance_score"] <= 1.0

    def test_solve_ideal_final_result(self):
        """Test that IFR (Ideal Final Result) is identified"""
        # ARRANGE
        problem = "Eliminate noise from motor while maintaining cooling"

        # ACT
        response = triz_solve_autonomous(problem)

        # ASSERT
        assert response.success is True
        assert "ideal_final_result" in response.data
        ifr = response.data["ideal_final_result"]
        assert len(ifr) >= 50  # Meaningful IFR description
        assert "without" in ifr.lower() or "while" in ifr.lower()  # Shows contradiction

    def test_solve_performance_requirement(self):
        """Test that autonomous solve completes within 10 seconds"""
        # ARRANGE
        problem = "Simple test problem for performance validation"

        # ACT
        start_time = time.time()
        response = triz_solve_autonomous(problem)
        end_time = time.time()

        # ASSERT
        assert response.success is True
        elapsed = end_time - start_time
        assert elapsed < 10.0, f"Autonomous solve took {elapsed:.2f}s, should be < 10s"

    def test_solve_empty_problem(self):
        """Test handling of empty or invalid problem descriptions"""
        # ARRANGE
        empty_problem = ""
        short_problem = "Fix it"

        # ACT
        response1 = triz_solve_autonomous(empty_problem)
        response2 = triz_solve_autonomous(short_problem)

        # ASSERT
        assert response1.success is False
        assert "problem description" in response1.message.lower()
        
        assert response2.success is False
        assert "insufficient" in response2.message.lower() or "detailed" in response2.message.lower()

    def test_solve_complex_problem(self):
        """Test handling of complex, multi-faceted problems"""
        # ARRANGE
        complex_problem = """
        Our manufacturing line needs to increase throughput by 50% while reducing 
        energy consumption by 30%. Additionally, we need to improve product quality 
        (reduce defects from 3% to 0.5%) without adding inspection steps. The system 
        must also be more flexible to handle 5 different product variants instead of 
        the current 2, and maintenance downtime should decrease from 10% to 5%.
        """

        # ACT
        response = triz_solve_autonomous(complex_problem)

        # ASSERT
        assert response.success is True
        assert len(response.data["contradictions_identified"]) >= 3
        assert len(response.data["solution_concepts"]) >= 3
        assert response.data["confidence_score"] >= 0.6  # Complex but solvable