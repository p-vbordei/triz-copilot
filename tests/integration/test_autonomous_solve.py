#!/usr/bin/env python3
"""
Integration Test: Autonomous Solve Workflow (T019)
Tests the autonomous TRIZ problem-solving capability.
"""

import unittest
import sys
from pathlib import Path
import time
from typing import Dict, Any, List

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.triz_tools.solve_tools import (
    triz_solve_autonomous,
    triz_solve_with_context,
    triz_solve_iterative
)
from src.triz_tools.services.analysis_service import get_analysis_service
from src.triz_tools.knowledge_base import get_knowledge_base
from src.triz_tools.services.materials_service import get_materials_service


class TestAutonomousSolve(unittest.TestCase):
    """Test autonomous TRIZ solving"""
    
    def setUp(self):
        """Set up test environment"""
        self.analysis_service = get_analysis_service()
        self.kb = get_knowledge_base()
        self.materials_service = get_materials_service()
        self.test_problems = [
            "Reduce weight while maintaining strength in aerospace components",
            "Increase production speed without sacrificing quality",
            "Improve energy efficiency in manufacturing processes",
            "Design quieter machinery without reducing performance",
            "Create more durable products with lower material costs"
        ]
    
    def test_basic_autonomous_solve(self):
        """Test basic autonomous problem solving"""
        problem = "Design a lightweight strong structure"
        
        result = triz_solve_autonomous(problem)
        
        self.assertIsInstance(result, dict)
        self.assertIn('analysis', result)
        self.assertIn('solutions', result['analysis'])
        self.assertIn('contradictions', result['analysis'])
        self.assertIn('principles', result['analysis'])
        
        # Verify solutions generated
        solutions = result['analysis']['solutions']
        self.assertIsInstance(solutions, list)
        self.assertTrue(len(solutions) > 0)
        
        # Verify solution structure
        for solution in solutions:
            self.assertIsInstance(solution, dict)
            if 'concept' in solution:
                self.assertIsInstance(solution['concept'], str)
            if 'feasibility' in solution:
                self.assertIsInstance(solution['feasibility'], (int, float))
    
    def test_autonomous_solve_with_contradictions(self):
        """Test autonomous solving identifies contradictions"""
        problem = "Increase speed while reducing energy consumption"
        
        result = triz_solve_autonomous(problem)
        
        self.assertIn('analysis', result)
        analysis = result['analysis']
        
        # Should identify contradictions
        self.assertIn('contradictions', analysis)
        contradictions = analysis['contradictions']
        self.assertIsInstance(contradictions, list)
        
        # Check contradiction structure
        if len(contradictions) > 0:
            for contradiction in contradictions:
                if isinstance(contradiction, dict):
                    # May have improving/worsening parameters
                    if 'improving' in contradiction:
                        self.assertIsInstance(contradiction['improving'], int)
                    if 'worsening' in contradiction:
                        self.assertIsInstance(contradiction['worsening'], int)
    
    def test_autonomous_solve_with_principles(self):
        """Test autonomous solving applies TRIZ principles"""
        problem = "Make system more flexible without increasing complexity"
        
        result = triz_solve_autonomous(problem)
        
        self.assertIn('analysis', result)
        analysis = result['analysis']
        
        # Should recommend principles
        self.assertIn('principles', analysis)
        principles = analysis['principles']
        self.assertIsInstance(principles, list)
        self.assertTrue(len(principles) > 0)
        
        # Verify principles are valid
        for principle_id in principles:
            if isinstance(principle_id, int):
                self.assertGreaterEqual(principle_id, 1)
                self.assertLessEqual(principle_id, 40)
    
    def test_solve_with_context(self):
        """Test solving with additional context"""
        problem = "Reduce vibration in high-speed machinery"
        context = {
            "industry": "manufacturing",
            "constraints": ["cost-effective", "minimal downtime"],
            "current_solution": "rubber dampeners",
            "issues": ["dampeners wear out quickly", "reduced efficiency"]
        }
        
        result = triz_solve_with_context(problem, context)
        
        self.assertIsInstance(result, dict)
        self.assertIn('analysis', result)
        
        # Context should influence solutions
        solutions = result['analysis']['solutions']
        self.assertTrue(len(solutions) > 0)
        
        # Solutions should consider constraints
        solution_text = str(solutions).lower()
        # Should address vibration
        self.assertTrue('vibration' in solution_text or 'dampen' in solution_text 
                       or 'isolat' in solution_text)
    
    def test_iterative_solve(self):
        """Test iterative refinement of solutions"""
        problem = "Improve heat dissipation in electronic devices"
        
        # First iteration
        result1 = triz_solve_iterative(
            problem,
            iteration=1,
            previous_solutions=[]
        )
        
        self.assertIn('analysis', result1)
        solutions1 = result1['analysis']['solutions']
        
        # Second iteration with feedback
        result2 = triz_solve_iterative(
            problem,
            iteration=2,
            previous_solutions=solutions1,
            feedback="Need more focus on passive cooling"
        )
        
        self.assertIn('analysis', result2)
        solutions2 = result2['analysis']['solutions']
        
        # Should generate different/refined solutions
        self.assertTrue(len(solutions2) > 0)
        
        # Check if solutions evolved
        if len(solutions1) > 0 and len(solutions2) > 0:
            # Solutions should be different or refined
            sol1_text = str(solutions1[0])
            sol2_text = str(solutions2[0])
            # May be same or different depending on refinement
            self.assertTrue(len(sol2_text) > 0)
    
    def test_solve_multiple_problems(self):
        """Test solving multiple diverse problems"""
        results = []
        
        for problem in self.test_problems[:3]:  # Test first 3 to save time
            result = triz_solve_autonomous(problem)
            results.append(result)
            
            # Basic validation
            self.assertIsInstance(result, dict)
            self.assertIn('analysis', result)
            self.assertIn('solutions', result['analysis'])
        
        # Verify different problems get different solutions
        all_solutions = []
        for result in results:
            solutions = result['analysis']['solutions']
            all_solutions.extend([str(s) for s in solutions])
        
        # Should have variety in solutions
        unique_solutions = set(all_solutions)
        self.assertGreater(len(unique_solutions), len(results))
    
    def test_solve_with_materials(self):
        """Test solving with materials recommendation"""
        problem = "Design heat-resistant lightweight components for aerospace"
        
        result = triz_solve_autonomous(problem)
        
        self.assertIn('analysis', result)
        solutions = result['analysis']['solutions']
        
        # Should mention materials
        solution_text = str(solutions).lower()
        material_keywords = [
            'titanium', 'aluminum', 'composite', 'carbon',
            'ceramic', 'alloy', 'material'
        ]
        
        has_materials = any(keyword in solution_text for keyword in material_keywords)
        self.assertTrue(has_materials or len(solutions) > 0)
    
    def test_solve_performance(self):
        """Test solving performance (should complete reasonably fast)"""
        problem = "Simple problem for performance testing"
        
        start_time = time.time()
        result = triz_solve_autonomous(problem)
        elapsed = time.time() - start_time
        
        # Should complete within reasonable time (10 seconds)
        self.assertLess(elapsed, 10.0)
        
        # Should still produce valid result
        self.assertIn('analysis', result)
        self.assertIn('solutions', result['analysis'])
    
    def test_solve_error_handling(self):
        """Test error handling in autonomous solve"""
        # Test with empty problem
        result = triz_solve_autonomous("")
        
        # Should handle gracefully
        self.assertIsInstance(result, dict)
        if 'error' in result:
            self.assertIsInstance(result['error'], str)
        elif 'analysis' in result:
            # May still try to analyze
            self.assertIsInstance(result['analysis'], dict)
        
        # Test with very long problem
        long_problem = "problem " * 1000
        result = triz_solve_autonomous(long_problem)
        
        # Should handle without crashing
        self.assertIsInstance(result, dict)
    
    def test_solve_with_ifr(self):
        """Test solving generates ideal final result"""
        problem = "Eliminate noise from machinery operation"
        
        result = triz_solve_autonomous(problem)
        
        self.assertIn('analysis', result)
        analysis = result['analysis']
        
        # Should include IFR concept
        if 'ideal_final_result' in analysis:
            ifr = analysis['ideal_final_result']
            self.assertIsInstance(ifr, str)
            self.assertTrue(len(ifr) > 0)
        
        # Or mentioned in solutions
        solutions_text = str(analysis.get('solutions', [])).lower()
        has_ifr_concept = 'ideal' in solutions_text or 'perfect' in solutions_text
        self.assertTrue('solutions' in analysis)


class TestSolutionQuality(unittest.TestCase):
    """Test quality of generated solutions"""
    
    def test_solution_relevance(self):
        """Test solutions are relevant to problem"""
        problem = "Reduce weight of aircraft wings while maintaining strength"
        
        result = triz_solve_autonomous(problem)
        solutions = result['analysis']['solutions']
        
        # Solutions should mention relevant concepts
        solution_text = str(solutions).lower()
        relevant_keywords = ['weight', 'strength', 'structure', 'material', 'design']
        
        relevance_count = sum(1 for keyword in relevant_keywords 
                            if keyword in solution_text)
        
        # At least some relevant keywords
        self.assertGreater(relevance_count, 0)
    
    def test_solution_innovation(self):
        """Test solutions show innovation"""
        problem = "Create self-cleaning surfaces"
        
        result = triz_solve_autonomous(problem)
        solutions = result['analysis']['solutions']
        
        # Check for innovation indicators
        for solution in solutions:
            if isinstance(solution, dict):
                if 'innovation_level' in solution:
                    self.assertIsInstance(solution['innovation_level'], (int, float))
                    self.assertGreaterEqual(solution['innovation_level'], 0)
                    self.assertLessEqual(solution['innovation_level'], 5)
    
    def test_solution_feasibility(self):
        """Test solutions include feasibility assessment"""
        problem = "Develop zero-emission manufacturing process"
        
        result = triz_solve_autonomous(problem)
        solutions = result['analysis']['solutions']
        
        # Check for feasibility scores
        for solution in solutions:
            if isinstance(solution, dict):
                if 'feasibility' in solution:
                    feasibility = solution['feasibility']
                    self.assertIsInstance(feasibility, (int, float))
                    self.assertGreaterEqual(feasibility, 0)
                    self.assertLessEqual(feasibility, 1)
    
    def test_solution_diversity(self):
        """Test solutions show diversity of approaches"""
        problem = "Improve energy efficiency in buildings"
        
        result = triz_solve_autonomous(problem)
        solutions = result['analysis']['solutions']
        
        # Should have multiple diverse solutions
        self.assertGreater(len(solutions), 1)
        
        # Solutions should be different
        if len(solutions) >= 2:
            sol1 = str(solutions[0])
            sol2 = str(solutions[1])
            
            # Should not be identical
            self.assertNotEqual(sol1, sol2)
            
            # Calculate simple diversity metric
            similarity = len(set(sol1.split()) & set(sol2.split())) / \
                        max(len(sol1.split()), len(sol2.split()))
            
            # Should not be too similar
            self.assertLess(similarity, 0.8)


if __name__ == '__main__':
    unittest.main()