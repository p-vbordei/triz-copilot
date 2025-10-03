"""
Comprehensive Tests for Complete 60-Step TRIZ Guided Solver

Tests all 6 phases of the complete TRIZ methodology:
    Phase 1: Understand & Scope (Steps 1-10)
    Phase 2: Define Ideal (Steps 11-16)
    Phase 3: Function Analysis (Steps 17-26)
    Phase 4: Select Tools (Steps 27-32)
    Phase 5: Generate Solutions (Steps 33-50)
    Phase 6: Rank & Implement (Steps 51-60)
"""

import pytest
from src.triz_tools.guided_triz_solver import (
    start_guided_triz_research,
    submit_research_findings,
)


class TestGuidedTRIZComplete:
    """Test complete 60-step guided TRIZ workflow"""

    @pytest.fixture
    def sample_problem(self):
        """Sample engineering problem for testing"""
        return "Design a lightweight camera stabilizer that is easy to form from sheet materials but needs to be rigid during use"

    @pytest.fixture
    def materials_problem(self):
        """Materials-specific problem to test Steps 47-49"""
        return "Need lighter alternative to aluminum 6061-T6 for aerospace brackets that maintains formability and strength"

    def test_session_start(self, sample_problem):
        """Test starting a guided TRIZ research session"""
        result = start_guided_triz_research(sample_problem)

        assert result["success"] is True
        assert "session_id" in result
        assert result["total_steps"] == 60
        assert result["current_step"] == 1
        assert result["phase"] == "UNDERSTAND_SCOPE"
        assert "instruction" in result
        assert len(result["instruction"]["search_queries"]) >= 4
        assert len(result["instruction"]["extract"]) >= 4

    def test_step_1_validation_success(self, sample_problem):
        """Test Step 1 successful validation"""
        # Start session
        start_result = start_guided_triz_research(sample_problem)
        session_id = start_result["session_id"]

        # Submit valid findings for Step 1 (9 Boxes)
        findings = {
            "sub_system_past": ["aluminum sheet", "steel frame"],
            "sub_system_present": ["aluminum 6061", "mounting brackets"],
            "sub_system_future": ["composite materials", "smart materials"],
            "system_past": ["heavy manual tripod"],
            "system_present": ["lightweight gimbal stabilizer"],
            "system_future": ["AI-powered adaptive stabilizer"],
            "super_system_past": ["professional videographers only"],
            "super_system_present": ["prosumer content creators"],
            "super_system_future": ["mass market consumers"],
        }

        result = submit_research_findings(session_id, findings)

        assert result["success"] is True
        assert result["step_completed"] == 1
        assert result["current_step"] == 2
        assert result["total_steps"] == 60
        assert "instruction" in result
        assert result["progress"] == "2/60 steps (3%)"

    def test_step_validation_failure(self, sample_problem):
        """Test validation failure with missing fields"""
        # Start session
        start_result = start_guided_triz_research(sample_problem)
        session_id = start_result["session_id"]

        # Submit incomplete findings (missing required fields)
        incomplete_findings = {
            "sub_system_past": ["aluminum sheet"],
            # Missing other required fields
        }

        result = submit_research_findings(session_id, incomplete_findings)

        assert result["success"] is False
        assert result["validation_failed"] is True
        assert "error" in result
        assert "hint" in result
        assert result["current_step"] == 1  # Still on step 1

    def test_phase_1_complete(self, sample_problem):
        """Test completing all steps in Phase 1 (Steps 1-10)"""
        # Start session
        start_result = start_guided_triz_research(sample_problem)
        session_id = start_result["session_id"]

        # Step 1: 9 Boxes
        findings_1 = {
            "sub_system_past": ["aluminum sheet", "steel frame"],
            "sub_system_present": ["aluminum 6061", "mounting brackets"],
            "sub_system_future": ["composite materials"],
            "system_past": ["heavy tripod"],
            "system_present": ["lightweight gimbal"],
            "system_future": ["adaptive stabilizer"],
            "super_system_past": ["professionals"],
            "super_system_present": ["prosumers"],
            "super_system_future": ["mass market"],
        }
        result = submit_research_findings(session_id, findings_1)
        assert result["success"] is True
        assert result["current_step"] == 2

        # Step 2: Sub-System components
        findings_2 = {
            "component_list": ["aluminum sheet", "mounting bracket", "motor", "sensor"],
            "component_materials": ["aluminum 6061-T6", "ABS plastic", "copper"],
            "component_functions": [
                "structural support",
                "mounting",
                "actuation",
                "sensing",
            ],
            "component_interactions": [
                "bracket bolts to sheet",
                "motor mounts on bracket",
            ],
        }
        result = submit_research_findings(session_id, findings_2)
        assert result["success"] is True
        assert result["current_step"] == 3

        # Continue through remaining Phase 1 steps (3-10)
        # For brevity, using generic valid findings
        for step in range(3, 11):
            findings = {
                f"field_{i}": f"data for requirement {i} in step {step}"
                for i in range(5)
            }
            result = submit_research_findings(session_id, findings)
            assert result["success"] is True
            if step < 10:
                assert result["current_step"] == step + 1

        # After step 10, should be on step 11 (Phase 2)
        assert result["current_step"] == 11
        assert result["phase"] == "DEFINE_IDEAL"

    def test_materials_steps_47_49(self, materials_problem):
        """Test materials research steps (47-49) for materials problems"""
        # Start session with materials problem
        start_result = start_guided_triz_research(materials_problem)
        session_id = start_result["session_id"]

        # Fast-forward to step 47 by submitting valid findings for steps 1-46
        # (In real test, would need actual valid data for each step)
        # For now, testing that step 47 instruction exists

        # We can at least verify the step instruction generation
        from src.triz_tools.guided_steps import phase5_generate_solutions

        # Test Step 47: DEEP materials research
        step_47_instruction = phase5_generate_solutions.generate(
            47, materials_problem, {}
        )

        assert "DEEP materials research" in step_47_instruction.task
        assert len(step_47_instruction.search_queries) >= 4
        assert "candidate_materials" in step_47_instruction.extract_requirements
        assert (
            "materials_properties_overview" in step_47_instruction.extract_requirements
        )
        assert "44+ materials engineering books" in step_47_instruction.why_this_matters

        # Test Step 48: Extract material properties
        step_48_instruction = phase5_generate_solutions.generate(
            48, materials_problem, {}
        )

        assert "density" in step_48_instruction.task.lower()
        assert "strength" in step_48_instruction.task.lower()
        assert "formability" in step_48_instruction.task.lower()

        # Test Step 49: Create comparison tables
        step_49_instruction = phase5_generate_solutions.generate(
            49, materials_problem, {}
        )

        assert "comparison" in step_49_instruction.task.lower()
        assert (
            "weight_comparison" in step_49_instruction.extract_requirements
            or "comparison_tables" in step_49_instruction.extract_requirements
        )

    def test_contradiction_steps_23_24(self, sample_problem):
        """Test contradiction identification steps"""
        from src.triz_tools.guided_steps import phase3_function_analysis

        # Test Step 23: Technical Contradictions
        step_23_instruction = phase3_function_analysis.generate(23, sample_problem, {})

        assert "Technical Contradiction" in step_23_instruction.task
        assert (
            "improving" in step_23_instruction.task.lower()
            or "worsening" in step_23_instruction.task.lower()
        )

        # Test Step 24: Physical Contradictions
        step_24_instruction = phase3_function_analysis.generate(24, sample_problem, {})

        assert "Physical Contradiction" in step_24_instruction.task

    def test_principles_steps_33_40(self, sample_problem):
        """Test principle research and application steps (33-40)"""
        from src.triz_tools.guided_steps import phase5_generate_solutions

        accumulated = {
            "step_29": {
                "recommended_principles": [1, 15, 35]
            }  # Mock from contradiction matrix
        }

        # Test Step 33: Deep research Principle #1
        step_33_instruction = phase5_generate_solutions.generate(
            33, sample_problem, accumulated
        )

        assert (
            "Principle #1" in step_33_instruction.task
            or "Principle #" in step_33_instruction.task
        )
        assert "full description" in step_33_instruction.task.lower()
        assert len(step_33_instruction.search_queries) >= 4

        # Test Step 36: Apply Principle #1
        accumulated["step_33"] = {
            "principle_number": 1,
            "principle_name": "Segmentation",
        }
        step_36_instruction = phase5_generate_solutions.generate(
            36, sample_problem, accumulated
        )

        assert "Apply Principle" in step_36_instruction.task
        assert "solution_concepts" in step_36_instruction.extract_requirements

    def test_ideality_calculation_steps(self, sample_problem):
        """Test Ideality calculation in Phase 6 (Steps 51-54)"""
        from src.triz_tools.guided_steps import phase6_rank_implement

        accumulated = {
            "step_50": {
                "complete_solutions": [
                    {"solution": "Solution 1"},
                    {"solution": "Solution 2"},
                    {"solution": "Solution 3"},
                ]
            }
        }

        # Test Step 51: Calculate Ideality for each solution
        step_51_instruction = phase6_rank_implement.generate(
            51, sample_problem, accumulated
        )

        assert "Ideality" in step_51_instruction.task
        assert (
            "ideality_scores" in step_51_instruction.extract_requirements
            or "solution_evaluations" in step_51_instruction.extract_requirements
        )

        # Test Step 55: Create Ideality Plot
        step_55_instruction = phase6_rank_implement.generate(
            55, sample_problem, accumulated
        )

        assert "Ideality Plot" in step_55_instruction.task

    def test_final_step_60(self, sample_problem):
        """Test final synthesis step (60)"""
        from src.triz_tools.guided_steps import phase6_rank_implement

        accumulated = {
            f"step_{i}": {"data": f"step {i} findings"} for i in range(1, 60)
        }

        # Test Step 60: Final synthesis
        step_60_instruction = phase6_rank_implement.generate(
            60, sample_problem, accumulated
        )

        assert (
            "final synthesis" in step_60_instruction.task.lower()
            or "FINAL" in step_60_instruction.task
        )
        assert "executive_summary" in step_60_instruction.extract_requirements
        assert (
            "evidence" in step_60_instruction.task.lower()
            or "evidence" in str(step_60_instruction.extract_requirements).lower()
        )

    def test_complete_60_step_workflow_mock(self, sample_problem):
        """Mock test of complete 60-step workflow (uses minimal data)"""
        # Start session
        start_result = start_guided_triz_research(sample_problem)
        session_id = start_result["session_id"]

        # Submit findings for all 60 steps (using generic data for speed)
        for step in range(1, 61):
            # Create minimal valid findings
            findings = {
                f"requirement_{i}": f"Research data for requirement {i} in step {step} - "
                + "x" * 50
                for i in range(5)
            }

            result = submit_research_findings(session_id, findings)

            if step < 60:
                assert result["success"] is True
                assert result["current_step"] == step + 1
                assert (
                    result["progress"]
                    == f"{step + 1}/60 steps ({int((step + 1) / 60 * 100)}%)"
                )
            else:
                # Final step
                assert result["success"] is True
                assert result["completed"] is True
                assert "final_solution" in result
                assert "session_summary" in result

    def test_session_persistence(self, sample_problem):
        """Test that sessions are saved and can be loaded"""
        # Start session
        start_result = start_guided_triz_research(sample_problem)
        session_id = start_result["session_id"]

        # Submit step 1
        findings_1 = {
            "sub_system_past": ["aluminum sheet"],
            "sub_system_present": ["aluminum 6061"],
            "sub_system_future": ["composite materials"],
            "system_past": ["heavy tripod"],
            "system_present": ["lightweight gimbal"],
            "system_future": ["adaptive stabilizer"],
            "super_system_past": ["professionals"],
            "super_system_present": ["prosumers"],
            "super_system_future": ["mass market"],
        }
        result = submit_research_findings(session_id, findings_1)
        assert result["success"] is True

        # Try to load session by submitting step 2
        findings_2 = {
            "component_list": ["aluminum sheet", "bracket"],
            "component_materials": ["aluminum 6061-T6"],
            "component_functions": ["structural support"],
            "component_interactions": ["bracket to sheet"],
        }
        result = submit_research_findings(session_id, findings_2)

        # Should successfully continue from step 2
        assert result["success"] is True
        assert result["current_step"] == 3

    def test_phase_progress_tracking(self, sample_problem):
        """Test that phase progress is tracked correctly"""
        start_result = start_guided_triz_research(sample_problem)

        # Step 1 should be in Phase 1
        assert start_result["phase"] == "UNDERSTAND_SCOPE"
        assert "Step 1 of 10 in Phase 1" in start_result["context"]["phase_progress"]

    def test_accumulated_knowledge(self, sample_problem):
        """Test that accumulated knowledge is built up across steps"""
        start_result = start_guided_triz_research(sample_problem)
        session_id = start_result["session_id"]

        # Submit step 1
        findings_1 = {
            "sub_system_past": ["aluminum sheet"],
            "sub_system_present": ["aluminum 6061"],
            "sub_system_future": ["composite materials"],
            "system_past": ["heavy tripod"],
            "system_present": ["lightweight gimbal"],
            "system_future": ["adaptive stabilizer"],
            "super_system_past": ["professionals"],
            "super_system_present": ["prosumers"],
            "super_system_future": ["mass market"],
        }
        result = submit_research_findings(session_id, findings_1)

        # Check that context includes accumulated knowledge
        assert "context" in result
        assert isinstance(result["context"], dict)
        assert "step_1" in result["context"]

    def test_error_handling_invalid_session(self):
        """Test error handling for invalid session ID"""
        result = submit_research_findings("invalid_session_id", {"data": "test"})

        assert result["success"] is False
        assert "not found" in result["error"].lower()


class TestPhaseInstructions:
    """Test individual phase instruction generators"""

    def test_phase1_all_steps(self):
        """Test all Phase 1 step instructions can be generated"""
        from src.triz_tools.guided_steps import phase1_understand_scope

        for step in range(1, 11):
            instruction = phase1_understand_scope.generate(step, "test problem", {})
            assert instruction.task
            assert len(instruction.search_queries) >= 3
            assert len(instruction.extract_requirements) >= 3
            assert instruction.validation_criteria
            assert instruction.why_this_matters

    def test_phase2_all_steps(self):
        """Test all Phase 2 step instructions can be generated"""
        from src.triz_tools.guided_steps import phase2_define_ideal

        for step in range(11, 17):
            instruction = phase2_define_ideal.generate(step, "test problem", {})
            assert instruction.task
            assert len(instruction.search_queries) >= 3
            assert len(instruction.extract_requirements) >= 3

    def test_phase3_all_steps(self):
        """Test all Phase 3 step instructions can be generated"""
        from src.triz_tools.guided_steps import phase3_function_analysis

        for step in range(17, 27):
            instruction = phase3_function_analysis.generate(step, "test problem", {})
            assert instruction.task
            assert len(instruction.search_queries) >= 3
            assert len(instruction.extract_requirements) >= 3

    def test_phase4_all_steps(self):
        """Test all Phase 4 step instructions can be generated"""
        from src.triz_tools.guided_steps import phase4_select_tools

        for step in range(27, 33):
            instruction = phase4_select_tools.generate(step, "test problem", {})
            assert instruction.task
            assert len(instruction.search_queries) >= 3
            assert len(instruction.extract_requirements) >= 3

    def test_phase5_all_steps(self):
        """Test all Phase 5 step instructions can be generated (33-50)"""
        from src.triz_tools.guided_steps import phase5_generate_solutions

        accumulated = {
            "step_29": {"recommended_principles": [1, 15, 35]},
            "step_33": {"principle_number": 1, "principle_name": "Segmentation"},
            "step_37": {"principle_number": 15, "principle_name": "Dynamism"},
        }

        for step in range(33, 51):
            instruction = phase5_generate_solutions.generate(
                step, "test problem", accumulated
            )
            assert instruction.task
            assert len(instruction.search_queries) >= 3
            assert len(instruction.extract_requirements) >= 3

    def test_phase6_all_steps(self):
        """Test all Phase 6 step instructions can be generated (51-60)"""
        from src.triz_tools.guided_steps import phase6_rank_implement

        accumulated = {
            "step_50": {
                "complete_solutions": [
                    {"solution": "Solution 1"},
                    {"solution": "Solution 2"},
                ]
            },
            "step_57": {"selected_solutions": [{"solution": "Primary Solution"}]},
        }

        for step in range(51, 61):
            instruction = phase6_rank_implement.generate(
                step, "test problem", accumulated
            )
            assert instruction.task
            assert len(instruction.search_queries) >= 3
            assert len(instruction.extract_requirements) >= 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
