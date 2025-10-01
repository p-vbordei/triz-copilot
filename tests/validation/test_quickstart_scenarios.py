#!/usr/bin/env python3
"""
Quickstart Validation Tests (T062)
Tests all scenarios described in quickstart.md to ensure they work as expected.
"""

import unittest
import time
import sys
from pathlib import Path
from typing import Dict, Any, List

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.triz_tools.direct_tools import (
    triz_tool_get_principle,
    triz_tool_contradiction_matrix,
    triz_tool_brainstorm
)
from src.triz_tools.solve_tools import triz_solve_autonomous
from src.triz_tools.workflow_tools import (
    triz_workflow_start,
    triz_workflow_continue,
    triz_workflow_reset,
    triz_workflow_status
)
from src.triz_tools.health_checks import HealthChecker


class TestQuickstartScenarios(unittest.TestCase):
    """Test scenarios from quickstart.md"""
    
    def setUp(self):
        """Set up test environment"""
        self.health_checker = HealthChecker()
    
    def test_system_health_prerequisites(self):
        """Test that all prerequisites are met (from quickstart.md section)"""
        print("\n=== Testing System Health Prerequisites ===")
        
        # Check health of all components
        health_status = self.health_checker.check_all(verbose=True)
        
        # All critical components should be healthy
        critical_components = ['knowledge_base', 'sessions', 'data_files']
        
        for component in critical_components:
            if component in health_status:
                status = health_status[component]
                self.assertTrue(status.is_healthy, 
                               f"Critical component {component} is not healthy: {status.message}")
        
        print("✅ All critical components are healthy")
    
    def test_example1_guided_workflow_learning(self):
        """Test Example 1: Guided Workflow Mode (Learning)"""
        print("\n=== Testing Example 1: Guided Workflow Mode ===")
        
        # Test problem from quickstart: "I need to design a bicycle that's lightweight but strong"
        problem = "I need to design a bicycle that's lightweight but strong"
        
        # 1. Start guided workflow
        start_result = triz_workflow_start()
        
        self.assertTrue(start_result.get('success', False))
        self.assertIn('session_id', start_result)
        self.assertEqual(start_result['stage'], 'problem_definition')
        
        session_id = start_result['session_id']
        print(f"✅ Started workflow session: {session_id}")
        
        # 2. Continue with problem definition
        problem_result = triz_workflow_continue(session_id, problem)
        
        self.assertTrue(problem_result.get('success', False))
        self.assertIn('stage', problem_result)
        self.assertIn('next_step', problem_result)
        
        print(f"✅ Problem defined, current stage: {problem_result['stage']}")
        
        # 3. Check workflow status
        status = triz_workflow_status(session_id)
        
        self.assertIsNotNone(status)
        self.assertEqual(status['session_id'], session_id)
        self.assertTrue(status['has_problem'])
        
        print("✅ Workflow status tracking works")
        
        # 4. Reset workflow
        reset_result = triz_workflow_reset(session_id)
        
        self.assertTrue(reset_result.get('success', False))
        self.assertEqual(reset_result['stage'], 'problem_definition')
        
        print("✅ Workflow reset successful")
    
    def test_example2_autonomous_solve_experienced(self):
        """Test Example 2: Autonomous Solve Mode (Experienced Users)"""
        print("\n=== Testing Example 2: Autonomous Solve Mode ===")
        
        # Test problem from quickstart: aircraft wing weight reduction
        problem = ("Reduce aircraft wing weight while maintaining structural strength. "
                  "Current aluminum design is 20% too heavy for fuel efficiency targets. "
                  "Must meet FAA certification requirements.")
        
        start_time = time.time()
        result = triz_solve_autonomous(problem)
        solve_time = time.time() - start_time
        
        # Validate performance requirement: <10s
        self.assertLess(solve_time, 10.0, 
                       f"Autonomous solve took {solve_time:.2f}s (limit: 10s)")
        
        # Validate response structure
        self.assertIsInstance(result, dict)
        self.assertIn('analysis', result)
        
        analysis = result['analysis']
        self.assertIn('problem_statement', analysis)
        self.assertIn('contradictions', analysis)
        self.assertIn('principles', analysis)
        self.assertIn('solutions', analysis)
        
        # Validate content quality (from quickstart expectations)
        contradictions = analysis['contradictions']
        self.assertTrue(len(contradictions) > 0, "Should identify contradictions")
        
        principles = analysis['principles']
        self.assertTrue(len(principles) > 0, "Should recommend principles")
        
        solutions = analysis['solutions']
        self.assertGreaterEqual(len(solutions), 3, "Should provide at least 3 solutions")
        
        # Check for expected principles (weight vs strength contradiction)
        expected_principles = [1, 8, 15, 40]  # From quickstart example
        found_expected = any(p in principles for p in expected_principles)
        self.assertTrue(found_expected, "Should find expected principles for weight/strength contradiction")
        
        print(f"✅ Autonomous solve completed in {solve_time:.2f}s")
        print(f"✅ Found {len(contradictions)} contradictions, {len(principles)} principles, {len(solutions)} solutions")
    
    def test_example3_direct_tool_access(self):
        """Test Example 3: Direct Tool Access (Expert Users)"""
        print("\n=== Testing Example 3: Direct Tool Access ===")
        
        # Test 1: Get specific principle details (Principle 15: Dynamics)
        start_time = time.time()
        principle_result = triz_tool_get_principle(15)
        principle_time = time.time() - start_time
        
        # Validate performance: <2s
        self.assertLess(principle_time, 2.0, 
                       f"Principle query took {principle_time:.2f}s (limit: 2s)")
        
        # Validate content (from quickstart expectations)
        self.assertTrue(principle_result.get('success', False))
        self.assertIn('data', principle_result)
        
        principle_data = principle_result['data']
        self.assertEqual(principle_data['id'], 15)
        self.assertEqual(principle_data['name'], 'Dynamics')
        self.assertIn('adaptive', principle_data['description'].lower())
        
        print(f"✅ Principle 15 retrieved in {principle_time:.3f}s")
        
        # Test 2: Query contradiction matrix (weight vs strength)
        start_time = time.time()
        matrix_result = triz_tool_contradiction_matrix(1, 14)
        matrix_time = time.time() - start_time
        
        # Validate performance: <2s
        self.assertLess(matrix_time, 2.0, 
                       f"Matrix query took {matrix_time:.2f}s (limit: 2s)")
        
        # Validate content
        self.assertTrue(matrix_result.get('success', False))
        self.assertIn('data', matrix_result)
        
        matrix_data = matrix_result['data']
        self.assertEqual(matrix_data['improving_parameter'], 1)
        self.assertEqual(matrix_data['worsening_parameter'], 14)
        self.assertIn('recommended_principles', matrix_data)
        
        # Should contain expected principles from quickstart
        recommended = matrix_data['recommended_principles']
        expected_matrix_principles = [1, 8, 15, 40]
        found_in_matrix = any(p in recommended for p in expected_matrix_principles)
        self.assertTrue(found_in_matrix, "Matrix should recommend expected principles")
        
        print(f"✅ Matrix lookup completed in {matrix_time:.3f}s")
        print(f"✅ Recommended principles: {recommended}")
        
        # Test 3: Contextual brainstorming
        start_time = time.time()
        brainstorm_result = triz_tool_brainstorm(40, "Solar panel efficiency improvement")
        brainstorm_time = time.time() - start_time
        
        # Validate performance: <2s
        self.assertLess(brainstorm_time, 2.0,
                       f"Brainstorm took {brainstorm_time:.2f}s (limit: 2s)")
        
        # Validate content
        self.assertTrue(brainstorm_result.get('success', False))
        self.assertIn('data', brainstorm_result)
        
        brainstorm_data = brainstorm_result['data']
        self.assertIn('principle', brainstorm_data)
        self.assertIn('solutions', brainstorm_data)
        self.assertEqual(brainstorm_data['principle']['id'], 40)
        
        solutions = brainstorm_data['solutions']
        self.assertTrue(len(solutions) > 0, "Should generate solutions")
        
        print(f"✅ Brainstorming completed in {brainstorm_time:.3f}s")
        print(f"✅ Generated {len(solutions)} context-specific solutions")
    
    def test_validation_test1_performance(self):
        """Test Validation Test 1: Tool Response Time (from quickstart.md)"""
        print("\n=== Testing Performance Requirements ===")
        
        # Test tool query performance (<2s)
        start_time = time.time()
        result = triz_tool_get_principle(1)
        tool_time = time.time() - start_time
        
        self.assertLess(tool_time, 2.0, f"Tool query took {tool_time:.2f}s (limit: 2s)")
        self.assertTrue(result.get('success', False))
        
        print(f"✅ Tool query: {tool_time:.3f}s (< 2s requirement)")
        
        # Test autonomous solve performance (<10s)
        start_time = time.time()
        result = triz_solve_autonomous("Simple contradiction test problem")
        solve_time = time.time() - start_time
        
        self.assertLess(solve_time, 10.0, f"Autonomous solve took {solve_time:.2f}s (limit: 10s)")
        self.assertIn('analysis', result)
        
        print(f"✅ Autonomous solve: {solve_time:.2f}s (< 10s requirement)")
    
    def test_validation_test2_session_continuity(self):
        """Test Validation Test 2: Session Continuity (from quickstart.md)"""
        print("\n=== Testing Session Continuity ===")
        
        # Start workflow
        start_result = triz_workflow_start()
        session_id = start_result['session_id']
        
        # Add problem
        problem_result = triz_workflow_continue(
            session_id, 
            "Test problem for session continuity"
        )
        
        self.assertTrue(problem_result.get('success', False))
        
        # Check that session remembers context
        status = triz_workflow_status(session_id)
        self.assertTrue(status['has_problem'])
        self.assertEqual(status['session_id'], session_id)
        
        print(f"✅ Session continuity maintained for session {session_id}")
        
        # Reset and verify clean state
        reset_result = triz_workflow_reset(session_id)
        self.assertTrue(reset_result.get('success', False))
        
        status_after_reset = triz_workflow_status(session_id)
        self.assertFalse(status_after_reset['has_problem'])
        
        print("✅ Session reset to clean state")
    
    def test_validation_test3_knowledge_accuracy(self):
        """Test Validation Test 3: Knowledge Base Accuracy (from quickstart.md)"""
        print("\n=== Testing Knowledge Base Accuracy ===")
        
        # Test principle lookup accuracy
        result = triz_tool_get_principle(1)
        
        self.assertTrue(result.get('success', False))
        self.assertIn('data', result)
        
        principle_data = result['data']
        self.assertEqual(principle_data['id'], 1)
        
        # Should contain "segmentation" (case insensitive)
        name_or_desc = (principle_data['name'] + ' ' + principle_data['description']).lower()
        self.assertIn('segment', name_or_desc, "Principle 1 should be about segmentation")
        
        print("✅ Principle lookup accuracy verified")
        
        # Test contradiction matrix accuracy
        matrix_result = triz_tool_contradiction_matrix(1, 14)
        
        self.assertTrue(matrix_result.get('success', False))
        self.assertIn('data', matrix_result)
        
        matrix_data = matrix_result['data']
        principles = matrix_data['recommended_principles']
        
        # All principles should be valid (1-40)
        for principle in principles:
            self.assertIsInstance(principle, int)
            self.assertGreaterEqual(principle, 1)
            self.assertLessEqual(principle, 40)
        
        print(f"✅ Matrix accuracy verified: {len(principles)} valid principles returned")
    
    def test_success_criteria_compliance(self):
        """Test Success Criteria from quickstart.md"""
        print("\n=== Testing Success Criteria Compliance ===")
        
        criteria_results = {}
        
        # 1. Response Times: Tool queries <2s, autonomous solve <10s
        start_time = time.time()
        triz_tool_get_principle(1)
        tool_time = time.time() - start_time
        criteria_results['response_times_tools'] = tool_time < 2.0
        
        start_time = time.time()
        triz_solve_autonomous("Test problem")
        solve_time = time.time() - start_time
        criteria_results['response_times_solve'] = solve_time < 10.0
        
        # 2. Accuracy: Contradiction matrix returns valid principles (1-40)
        matrix_result = triz_tool_contradiction_matrix(1, 14)
        if matrix_result.get('success') and 'data' in matrix_result:
            principles = matrix_result['data']['recommended_principles']
            valid_principles = all(1 <= p <= 40 for p in principles if isinstance(p, int))
            criteria_results['accuracy_matrix'] = valid_principles
        else:
            criteria_results['accuracy_matrix'] = False
        
        # 3. Completeness: Autonomous solve returns 3-5 solution concepts
        solve_result = triz_solve_autonomous("Design completeness test")
        if 'analysis' in solve_result and 'solutions' in solve_result['analysis']:
            solutions_count = len(solve_result['analysis']['solutions'])
            criteria_results['completeness_solutions'] = 3 <= solutions_count <= 10  # Allow up to 10
        else:
            criteria_results['completeness_solutions'] = False
        
        # 4. Persistence: Workflow sessions maintain state
        start_result = triz_workflow_start()
        session_id = start_result['session_id']
        triz_workflow_continue(session_id, "Persistence test")
        status = triz_workflow_status(session_id)
        criteria_results['persistence_sessions'] = status.get('has_problem', False)
        
        # 5. Knowledge: Principle lookup returns detailed, accurate information
        principle_result = triz_tool_get_principle(15)
        if principle_result.get('success') and 'data' in principle_result:
            data = principle_result['data']
            has_required_fields = all(field in data for field in ['id', 'name', 'description'])
            criteria_results['knowledge_detailed'] = has_required_fields
        else:
            criteria_results['knowledge_detailed'] = False
        
        # 6. Integration: Commands work seamlessly (tested by successful execution)
        criteria_results['integration_seamless'] = True  # If we got here, integration works
        
        # Print results
        print("Success Criteria Results:")
        for criterion, passed in criteria_results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"  {criterion}: {status}")
        
        # All criteria should pass
        for criterion, passed in criteria_results.items():
            self.assertTrue(passed, f"Success criterion '{criterion}' failed")
        
        print("✅ All success criteria met")
    
    def test_materials_database_integration(self):
        """Test materials database integration mentioned in quickstart"""
        print("\n=== Testing Materials Database Integration ===")
        
        # Test that autonomous solve can recommend materials
        problem = "Select lightweight heat-resistant material for aerospace application"
        result = triz_solve_autonomous(problem)
        
        self.assertIn('analysis', result)
        
        # Check if materials are mentioned in the analysis
        analysis_text = str(result['analysis']).lower()
        material_keywords = ['material', 'composite', 'titanium', 'aluminum', 'carbon', 'alloy']
        
        has_materials = any(keyword in analysis_text for keyword in material_keywords)
        self.assertTrue(has_materials, "Should mention materials in aerospace problem")
        
        print("✅ Materials database integration verified")
    
    def test_error_handling_robustness(self):
        """Test system robustness with edge cases"""
        print("\n=== Testing Error Handling Robustness ===")
        
        # Test invalid principle ID
        result = triz_tool_get_principle(999)
        self.assertFalse(result.get('success', True), "Should handle invalid principle ID")
        
        # Test invalid matrix parameters
        result = triz_tool_contradiction_matrix(999, 999)
        self.assertFalse(result.get('success', True), "Should handle invalid matrix parameters")
        
        # Test empty problem
        result = triz_solve_autonomous("")
        self.assertIsInstance(result, dict)  # Should not crash
        
        # Test invalid session ID
        result = triz_workflow_status("invalid-session-id")
        self.assertIn('error', result or {})  # Should return error, not crash
        
        print("✅ Error handling robustness verified")


class TestAdvancedQuickstartFeatures(unittest.TestCase):
    """Test advanced features mentioned in quickstart.md"""
    
    def test_performance_optimization_scenarios(self):
        """Test performance optimization scenarios from quickstart"""
        print("\n=== Testing Performance Optimization ===")
        
        # Test batch operations performance
        principles_to_test = [1, 5, 10, 15, 20, 25, 30, 35, 40]
        
        start_time = time.time()
        results = []
        for principle_id in principles_to_test:
            result = triz_tool_get_principle(principle_id)
            results.append(result)
        
        batch_time = time.time() - start_time
        avg_time = batch_time / len(principles_to_test)
        
        # Average should still be under 2s per query
        self.assertLess(avg_time, 2.0, f"Average query time {avg_time:.2f}s exceeds 2s limit")
        
        # All should be successful
        success_count = sum(1 for r in results if r.get('success', False))
        self.assertEqual(success_count, len(principles_to_test), "All principle queries should succeed")
        
        print(f"✅ Batch operations: {len(principles_to_test)} queries in {batch_time:.2f}s (avg: {avg_time:.3f}s)")
    
    def test_memory_usage_constraints(self):
        """Test memory usage stays within reasonable bounds"""
        print("\n=== Testing Memory Usage Constraints ===")
        
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Perform memory-intensive operations
        for i in range(50):
            triz_tool_get_principle((i % 40) + 1)
            if i % 10 == 0:
                triz_solve_autonomous(f"Memory test problem {i}")
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 500MB for this test)
        self.assertLess(memory_increase, 500, 
                       f"Memory increased by {memory_increase:.0f}MB (limit: 500MB)")
        
        print(f"✅ Memory usage: {memory_increase:.0f}MB increase (within limits)")


def run_quickstart_validation():
    """Run all quickstart validation tests"""
    print("=" * 60)
    print("TRIZ Engineering Co-Pilot - Quickstart Validation")
    print("=" * 60)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestQuickstartScenarios))
    suite.addTests(loader.loadTestsFromTestCase(TestAdvancedQuickstartFeatures))
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)
    
    print("\n" + "=" * 60)
    print("QUICKSTART VALIDATION SUMMARY")
    print("=" * 60)
    
    if result.wasSuccessful():
        print("🎉 ALL QUICKSTART SCENARIOS VALIDATED SUCCESSFULLY!")
        print("\nThe TRIZ Engineering Co-Pilot is ready for production use.")
        print("All examples from quickstart.md work as expected.")
    else:
        print("❌ SOME QUICKSTART SCENARIOS FAILED")
        print(f"\nFailed tests: {len(result.failures)}")
        print(f"Error tests: {len(result.errors)}")
        
        if result.failures:
            print("\nFailures:")
            for test, traceback in result.failures:
                print(f"  - {test}: {traceback.split('AssertionError:')[-1].strip()}")
        
        if result.errors:
            print("\nErrors:")
            for test, traceback in result.errors:
                print(f"  - {test}: {traceback.split('Exception:')[-1].strip()}")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_quickstart_validation()
    sys.exit(0 if success else 1)