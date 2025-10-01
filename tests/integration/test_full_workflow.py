#!/usr/bin/env python3
"""
Integration Test: Complete TRIZ Workflow (T018)
Tests the complete TRIZ problem-solving workflow from start to finish.
"""

import unittest
import sys
from pathlib import Path
import tempfile
import shutil
from typing import List, Dict, Any

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.triz_tools.workflow_tools import (
    triz_workflow_start,
    triz_workflow_continue,
    triz_workflow_reset,
    triz_workflow_status
)
from src.triz_tools.session_manager import get_session_manager
from src.triz_tools.knowledge_base import get_knowledge_base
from src.triz_tools.contradiction_matrix import get_matrix_lookup
from src.triz_tools.services.analysis_service import get_analysis_service


class TestCompleteWorkflow(unittest.TestCase):
    """Test complete TRIZ workflow integration"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.session_manager = get_session_manager(
            storage_dir=Path(self.temp_dir),
            reset=True
        )
        self.kb = get_knowledge_base()
        self.matrix = get_matrix_lookup()
        self.analysis_service = get_analysis_service()
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_workflow_start(self):
        """Test starting a new workflow"""
        result = triz_workflow_start()
        
        self.assertIsInstance(result, dict)
        self.assertIn('session_id', result)
        self.assertIn('stage', result)
        self.assertIn('message', result)
        self.assertIn('next_step', result)
        self.assertEqual(result['stage'], 'problem_definition')
    
    def test_complete_workflow_execution(self):
        """Test executing complete workflow from start to finish"""
        # Start workflow
        start_result = triz_workflow_start()
        session_id = start_result['session_id']
        
        # Step 1: Define problem
        problem_result = triz_workflow_continue(
            session_id=session_id,
            user_input="Design a lightweight but strong aircraft component that can withstand high temperatures"
        )
        self.assertEqual(problem_result['stage'], 'ideal_final_result')
        self.assertIn('problem_statement', problem_result)
        
        # Step 2: Define IFR
        ifr_result = triz_workflow_continue(
            session_id=session_id,
            user_input="The component has zero weight, infinite strength, and is completely heat resistant"
        )
        self.assertEqual(ifr_result['stage'], 'contradiction_analysis')
        self.assertIn('ideal_final_result', ifr_result)
        
        # Step 3: Identify contradictions
        contradiction_result = triz_workflow_continue(
            session_id=session_id,
            user_input="Weight vs Strength, Temperature resistance vs Material properties"
        )
        self.assertEqual(contradiction_result['stage'], 'principle_selection')
        self.assertIn('contradictions', contradiction_result)
        self.assertIsInstance(contradiction_result['contradictions'], list)
        
        # Step 4: Select principles
        principle_result = triz_workflow_continue(
            session_id=session_id,
            user_input="Use recommended principles"
        )
        self.assertEqual(principle_result['stage'], 'solution_generation')
        self.assertIn('selected_principles', principle_result)
        self.assertIsInstance(principle_result['selected_principles'], list)
        
        # Step 5: Generate solutions
        solution_result = triz_workflow_continue(
            session_id=session_id,
            user_input="Generate innovative solutions"
        )
        self.assertEqual(solution_result['stage'], 'evaluation')
        self.assertIn('solutions', solution_result)
        self.assertIsInstance(solution_result['solutions'], list)
        self.assertTrue(len(solution_result['solutions']) > 0)
        
        # Step 6: Evaluate solutions
        eval_result = triz_workflow_continue(
            session_id=session_id,
            user_input="Evaluate based on feasibility and innovation"
        )
        self.assertIn('evaluation_complete', eval_result)
        self.assertIn('ranked_solutions', eval_result)
    
    def test_workflow_status_check(self):
        """Test checking workflow status"""
        # Start workflow
        start_result = triz_workflow_start()
        session_id = start_result['session_id']
        
        # Add some data
        triz_workflow_continue(
            session_id=session_id,
            user_input="Test problem for status check"
        )
        
        # Check status
        status = triz_workflow_status(session_id)
        
        self.assertIsInstance(status, dict)
        self.assertIn('session_id', status)
        self.assertIn('current_stage', status)
        self.assertIn('progress', status)
        self.assertIn('has_problem', status)
        self.assertTrue(status['has_problem'])
    
    def test_workflow_reset(self):
        """Test resetting workflow"""
        # Start and populate workflow
        start_result = triz_workflow_start()
        session_id = start_result['session_id']
        
        triz_workflow_continue(
            session_id=session_id,
            user_input="Problem before reset"
        )
        
        # Reset
        reset_result = triz_workflow_reset(session_id)
        
        self.assertIsInstance(reset_result, dict)
        self.assertIn('success', reset_result)
        self.assertTrue(reset_result['success'])
        self.assertIn('stage', reset_result)
        self.assertEqual(reset_result['stage'], 'problem_definition')
        
        # Verify reset
        status = triz_workflow_status(session_id)
        self.assertFalse(status['has_problem'])
    
    def test_workflow_with_contradictions(self):
        """Test workflow with specific contradictions"""
        start_result = triz_workflow_start()
        session_id = start_result['session_id']
        
        # Define problem
        triz_workflow_continue(
            session_id=session_id,
            user_input="Increase production speed while maintaining quality"
        )
        
        # Skip to contradiction analysis
        session = self.session_manager.get_session_data(session_id)
        self.session_manager.update_session(
            session_id,
            stage='contradiction_analysis',
            data={'ideal_final_result': 'Instant production with perfect quality'}
        )
        
        # Analyze contradictions
        result = triz_workflow_continue(
            session_id=session_id,
            user_input="Speed (9) vs Quality (28), Productivity (39) vs Precision (29)"
        )
        
        self.assertIn('contradictions', result)
        contradictions = result['contradictions']
        self.assertTrue(len(contradictions) > 0)
        
        # Verify principles are recommended
        if 'recommended_principles' in result:
            self.assertIsInstance(result['recommended_principles'], list)
    
    def test_workflow_persistence(self):
        """Test workflow persistence across sessions"""
        # Start workflow
        start_result = triz_workflow_start()
        session_id = start_result['session_id']
        
        # Add data
        triz_workflow_continue(
            session_id=session_id,
            user_input="Persistent problem statement"
        )
        
        # Clear manager cache
        self.session_manager = get_session_manager(
            storage_dir=Path(self.temp_dir),
            reset=True
        )
        
        # Continue workflow with new manager
        result = triz_workflow_continue(
            session_id=session_id,
            user_input="Persistent IFR"
        )
        
        self.assertEqual(result['stage'], 'contradiction_analysis')
        self.assertEqual(result['problem_statement'], "Persistent problem statement")
        self.assertEqual(result['ideal_final_result'], "Persistent IFR")
    
    def test_workflow_error_handling(self):
        """Test workflow error handling"""
        # Try to continue non-existent session
        result = triz_workflow_continue(
            session_id="non-existent-session-id",
            user_input="Test input"
        )
        
        self.assertIn('error', result)
        self.assertIsInstance(result['error'], str)
        
        # Try to reset non-existent session
        reset_result = triz_workflow_reset("non-existent-session-id")
        self.assertIn('error', reset_result)
    
    def test_workflow_stage_validation(self):
        """Test stage-appropriate input validation"""
        start_result = triz_workflow_start()
        session_id = start_result['session_id']
        
        # Try empty input at problem definition
        result = triz_workflow_continue(
            session_id=session_id,
            user_input=""
        )
        
        # Should handle gracefully
        self.assertIsInstance(result, dict)
        if 'error' in result:
            self.assertIn('problem', result['error'].lower())
    
    def test_workflow_with_materials(self):
        """Test workflow with materials recommendation"""
        start_result = triz_workflow_start()
        session_id = start_result['session_id']
        
        # Define problem with materials context
        triz_workflow_continue(
            session_id=session_id,
            user_input="Design heat-resistant lightweight structural component"
        )
        
        # Progress through workflow
        triz_workflow_continue(
            session_id=session_id,
            user_input="Component withstands 1000°C with minimal weight"
        )
        
        # Get to solution generation
        self.session_manager.update_session(
            session_id,
            stage='solution_generation',
            data={
                'contradictions': [{'improving': 1, 'worsening': 17}],
                'selected_principles': [40, 26]  # Composite materials
            }
        )
        
        result = triz_workflow_continue(
            session_id=session_id,
            user_input="Recommend materials"
        )
        
        self.assertIn('solutions', result)
        
        # Check if materials are mentioned in solutions
        solutions_text = str(result['solutions'])
        material_keywords = ['composite', 'titanium', 'ceramic', 'carbon']
        has_materials = any(keyword in solutions_text.lower() 
                          for keyword in material_keywords)
        self.assertTrue(has_materials or len(result['solutions']) > 0)


class TestWorkflowIntegration(unittest.TestCase):
    """Test workflow integration with other components"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.session_manager = get_session_manager(
            storage_dir=Path(self.temp_dir),
            reset=True
        )
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_workflow_with_knowledge_base(self):
        """Test workflow integration with knowledge base"""
        kb = get_knowledge_base()
        
        start_result = triz_workflow_start()
        session_id = start_result['session_id']
        
        # Progress to principle selection
        self.session_manager.update_session(
            session_id,
            stage='principle_selection',
            data={
                'problem_statement': 'Test problem',
                'contradictions': [{'improving': 1, 'worsening': 14}]
            }
        )
        
        result = triz_workflow_continue(
            session_id=session_id,
            user_input="Select principles 1, 8, 15"
        )
        
        # Verify principles are from knowledge base
        if 'selected_principles' in result:
            for principle_id in result['selected_principles']:
                principle = kb.get_principle(principle_id)
                self.assertIsNotNone(principle)
    
    def test_workflow_with_contradiction_matrix(self):
        """Test workflow integration with contradiction matrix"""
        matrix = get_matrix_lookup()
        
        start_result = triz_workflow_start()
        session_id = start_result['session_id']
        
        # Set up for contradiction analysis
        self.session_manager.update_session(
            session_id,
            stage='contradiction_analysis',
            data={
                'problem_statement': 'Weight vs strength problem',
                'ideal_final_result': 'Zero weight, infinite strength'
            }
        )
        
        result = triz_workflow_continue(
            session_id=session_id,
            user_input="Parameter 1 improving, parameter 14 worsening"
        )
        
        # Verify matrix lookup was used
        if 'contradictions' in result:
            contradiction = matrix.lookup(1, 14)
            self.assertIsNotNone(contradiction)
            
            if 'recommended_principles' in result:
                matrix_principles = contradiction.recommended_principles
                for principle in matrix_principles:
                    self.assertIn(principle, result['recommended_principles'])
    
    def test_workflow_with_analysis_service(self):
        """Test workflow integration with analysis service"""
        analysis = get_analysis_service()
        
        start_result = triz_workflow_start()
        session_id = start_result['session_id']
        
        # Set up for solution generation
        self.session_manager.update_session(
            session_id,
            stage='solution_generation',
            data={
                'problem_statement': 'Reduce vibration in machinery',
                'selected_principles': [2, 13, 35],
                'contradictions': [{'improving': 10, 'worsening': 18}]
            }
        )
        
        result = triz_workflow_continue(
            session_id=session_id,
            user_input="Generate solutions using analysis service"
        )
        
        self.assertIn('solutions', result)
        self.assertTrue(len(result['solutions']) > 0)
        
        # Verify solution structure
        for solution in result['solutions']:
            self.assertIsInstance(solution, dict)
            if 'principle_id' in solution:
                self.assertIn(solution['principle_id'], [2, 13, 35])


if __name__ == '__main__':
    unittest.main()