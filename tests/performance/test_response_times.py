#!/usr/bin/env python3
"""
Performance Tests: TRIZ Tool Response Times (T020 & T021)
Tests that tool queries complete within 2 seconds and autonomous solve within 10 seconds.
"""

import unittest
import time
import sys
from pathlib import Path
from typing import Any, List, Callable
import concurrent.futures
import psutil
import os

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.triz_tools.direct_tools import (
    triz_tool_get_principle,
    triz_tool_contradiction_matrix,
    triz_tool_brainstorm,
)
from src.triz_tools.solve_tools import triz_solve_autonomous


class TestToolPerformance(unittest.TestCase):
    """T020: Performance tests for tool queries (<2s requirement)"""
    
    def test_get_principle_performance(self):
        """Test that get_principle completes within 2 seconds"""
        principle_number = 1
        
        start_time = time.time()
        response = triz_tool_get_principle(principle_number)
        elapsed_time = time.time() - start_time
        
        self.assertIsNotNone(response)
        self.assertLess(elapsed_time, 2.0, 
                       f"Get principle took {elapsed_time:.2f}s (limit: 2s)")
    
    def test_contradiction_matrix_performance(self):
        """Test that contradiction matrix query completes within 2 seconds"""
        improving_param = 1
        worsening_param = 14
        
        start_time = time.time()
        response = triz_tool_contradiction_matrix(improving_param, worsening_param)
        elapsed_time = time.time() - start_time
        
        self.assertIsNotNone(response)
        self.assertLess(elapsed_time, 2.0,
                       f"Matrix query took {elapsed_time:.2f}s (limit: 2s)")
    
    def test_brainstorm_performance(self):
        """Test that brainstorm completes within 2 seconds"""
        principle_number = 15
        context = "Improve efficiency of solar panels"
        
        start_time = time.time()
        response = triz_tool_brainstorm(principle_number, context)
        elapsed_time = time.time() - start_time
        
        self.assertIsNotNone(response)
        self.assertLess(elapsed_time, 2.0,
                       f"Brainstorm took {elapsed_time:.2f}s (limit: 2s)")
    
    def test_batch_tool_queries_performance(self):
        """Test performance when running multiple tool queries"""
        queries = [
            (triz_tool_get_principle, (1,)),
            (triz_tool_get_principle, (15,)),
            (triz_tool_contradiction_matrix, (1, 14)),
            (triz_tool_contradiction_matrix, (9, 21)),
            (triz_tool_brainstorm, (40, "lightweight materials")),
        ]
        
        start_time = time.time()
        for func, args in queries:
            result = func(*args)
            self.assertIsNotNone(result)
        elapsed_time = time.time() - start_time
        
        average_time = elapsed_time / len(queries)
        self.assertLess(average_time, 2.0,
                       f"Average query time {average_time:.2f}s (limit: 2s)")
    
    def test_consistent_performance_across_principles(self):
        """Test that all principles have similar query performance"""
        principle_nums = [1, 10, 20, 30, 40]
        times = []
        
        for principle_num in principle_nums:
            start_time = time.time()
            response = triz_tool_get_principle(principle_num)
            elapsed_time = time.time() - start_time
            times.append(elapsed_time)
            
            self.assertIsNotNone(response)
            self.assertLess(elapsed_time, 2.0,
                           f"Principle {principle_num} took {elapsed_time:.2f}s")
        
        # Check consistency (no outliers > 2x average)
        avg_time = sum(times) / len(times)
        max_time = max(times)
        self.assertLess(max_time, avg_time * 2,
                       f"Performance inconsistent: max={max_time:.2f}s, avg={avg_time:.2f}s")


class TestAutonomousSolvePerformance(unittest.TestCase):
    """T021: Performance tests for autonomous solve (<10s requirement)"""
    
    def test_simple_problem_performance(self):
        """Test that simple autonomous solve completes within 10 seconds"""
        simple_problem = "Reduce weight of component while maintaining strength"
        
        start_time = time.time()
        response = triz_solve_autonomous(simple_problem)
        elapsed_time = time.time() - start_time
        
        self.assertIsNotNone(response)
        self.assertIn('analysis', response)
        self.assertLess(elapsed_time, 10.0,
                       f"Simple solve took {elapsed_time:.2f}s (limit: 10s)")
    
    def test_complex_problem_performance(self):
        """Test that complex autonomous solve completes within 10 seconds"""
        complex_problem = """
        Our manufacturing system needs to increase production speed by 50% 
        while reducing energy consumption by 30%. We also need to improve 
        product quality and reduce defects from 3% to 0.5% without adding 
        inspection steps. The system must handle 5 product variants instead 
        of 2, and maintenance downtime should decrease from 10% to 5%.
        """
        
        start_time = time.time()
        response = triz_solve_autonomous(complex_problem)
        elapsed_time = time.time() - start_time
        
        self.assertIsNotNone(response)
        self.assertIn('analysis', response)
        self.assertLess(elapsed_time, 10.0,
                       f"Complex solve took {elapsed_time:.2f}s (limit: 10s)")
    
    def test_multiple_problems_performance(self):
        """Test solving multiple problems in sequence"""
        problems = [
            "Reduce vibration in machinery",
            "Increase heat dissipation",
            "Improve material strength"
        ]
        
        total_start = time.time()
        for problem in problems:
            response = triz_solve_autonomous(problem)
            self.assertIsNotNone(response)
        total_time = time.time() - total_start
        
        # Should complete all 3 in reasonable time
        self.assertLess(total_time, 30.0,
                       f"3 problems took {total_time:.2f}s (limit: 30s)")
        
        avg_time = total_time / len(problems)
        self.assertLess(avg_time, 10.0,
                       f"Average solve time {avg_time:.2f}s (limit: 10s)")


class TestMemoryAndConcurrency(unittest.TestCase):
    """Performance tests for memory usage and concurrent access"""
    
    def test_memory_usage_constraint(self):
        """Test that system stays within 1GB memory footprint"""
        process = psutil.Process(os.getpid())
        
        # Get initial memory
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Load all principles
        for i in range(1, 41):
            response = triz_tool_get_principle(i)
            self.assertIsNotNone(response)
        
        # Load multiple matrix lookups
        for i in range(1, 10):
            for j in range(1, 10):
                triz_tool_contradiction_matrix(i, j)
        
        # Get final memory
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        self.assertLess(memory_increase, 1024,
                       f"Memory increase {memory_increase:.0f}MB (limit: 1024MB)")
    
    def test_concurrent_request_performance(self):
        """Test performance under concurrent requests"""
        def make_request(i):
            start = time.time()
            if i % 3 == 0:
                result = triz_tool_get_principle(i % 40 + 1)
            elif i % 3 == 1:
                result = triz_tool_contradiction_matrix(1, 14)
            else:
                result = triz_tool_brainstorm(15, f"context {i}")
            return time.time() - start, result
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request, i) for i in range(10)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        times = [r[0] for r in results]
        responses = [r[1] for r in results]
        
        # All requests should succeed
        for response in responses:
            self.assertIsNotNone(response)
        
        # Performance should be reasonable under load
        max_time = max(times)
        avg_time = sum(times) / len(times)
        
        self.assertLess(max_time, 3.0,
                       f"Max concurrent time {max_time:.2f}s (limit: 3s)")
        self.assertLess(avg_time, 2.0,
                       f"Avg concurrent time {avg_time:.2f}s (limit: 2s)")
    
    def test_cache_effectiveness(self):
        """Test that caching improves performance for repeated queries"""
        principle_id = 1
        
        # First call (cache miss)
        start1 = time.time()
        result1 = triz_tool_get_principle(principle_id)
        time1 = time.time() - start1
        
        # Second call (cache hit)
        start2 = time.time()
        result2 = triz_tool_get_principle(principle_id)
        time2 = time.time() - start2
        
        self.assertEqual(result1, result2)
        
        # Second call should be faster (allowing for variance)
        if time1 > 0.1:  # Only test if first call took meaningful time
            self.assertLess(time2, time1 * 1.5,
                           f"Cache not effective: first={time1:.3f}s, second={time2:.3f}s")


class TestPerformanceStress(unittest.TestCase):
    """Stress tests for sustained performance"""
    
    def test_sustained_tool_queries(self):
        """Test performance over many consecutive queries"""
        query_count = 100
        times = []
        
        for i in range(query_count):
            principle = (i % 40) + 1
            start = time.time()
            response = triz_tool_get_principle(principle)
            elapsed = time.time() - start
            times.append(elapsed)
            self.assertIsNotNone(response)
        
        # Check performance metrics
        avg_time = sum(times) / len(times)
        max_time = max(times)
        p95_time = sorted(times)[int(len(times) * 0.95)]
        
        self.assertLess(avg_time, 1.0,
                       f"Average time {avg_time:.3f}s over {query_count} queries")
        self.assertLess(p95_time, 2.0,
                       f"P95 time {p95_time:.3f}s (limit: 2s)")
        self.assertLess(max_time, 3.0,
                       f"Max time {max_time:.3f}s (limit: 3s)")
    
    def test_performance_degradation(self):
        """Test that performance doesn't degrade over time"""
        # First batch
        first_times = []
        for i in range(10):
            start = time.time()
            triz_tool_get_principle(i + 1)
            first_times.append(time.time() - start)
        
        # Run many queries
        for i in range(50):
            triz_tool_contradiction_matrix((i % 39) + 1, ((i + 10) % 39) + 1)
        
        # Last batch
        last_times = []
        for i in range(10):
            start = time.time()
            triz_tool_get_principle(i + 1)
            last_times.append(time.time() - start)
        
        first_avg = sum(first_times) / len(first_times)
        last_avg = sum(last_times) / len(last_times)
        
        # Performance should not degrade significantly
        self.assertLess(last_avg, first_avg * 2,
                       f"Performance degraded: first={first_avg:.3f}s, last={last_avg:.3f}s")


if __name__ == '__main__':
    unittest.main()