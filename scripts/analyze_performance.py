#!/usr/bin/env python3
"""
Performance Analysis Script (T063)

Comprehensive performance analysis and optimization for TRIZ system.
"""

import sys
import time
import json
from pathlib import Path
from typing import Dict, Any, List
import argparse

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from src.triz_tools.performance import (
    get_performance_optimizer,
    optimize_triz_system,
    get_performance_summary,
    monitor_performance,
    export_performance_report
)


def run_baseline_tests() -> Dict[str, Any]:
    """Run baseline performance tests."""
    print("Running baseline performance tests...")
    
    results = {}
    
    try:
        from src.triz_tools.direct_tools import (
            triz_tool_get_principle,
            triz_tool_contradiction_matrix,
            triz_tool_brainstorm
        )
        from src.triz_tools.solve_tools import triz_solve_autonomous
        from src.triz_tools.workflow_tools import triz_workflow_start
        
        # Test 1: Tool queries (target: <2s each)
        print("  Testing tool queries...")
        tool_times = []
        
        with monitor_performance("baseline_tool_queries"):
            for principle_id in [1, 5, 10, 15, 20, 25, 30, 35, 40]:
                start_time = time.time()
                result = triz_tool_get_principle(principle_id)
                query_time = time.time() - start_time
                tool_times.append(query_time)
                
                if not result.get('success'):
                    print(f"    ⚠️  Principle {principle_id} query failed")
        
        results['tool_queries'] = {
            'times': tool_times,
            'avg_time': sum(tool_times) / len(tool_times),
            'max_time': max(tool_times),
            'min_time': min(tool_times),
            'target_met': all(t < 2.0 for t in tool_times)
        }
        
        print(f"    Average tool query time: {results['tool_queries']['avg_time']:.3f}s")
        
        # Test 2: Matrix lookups
        print("  Testing matrix lookups...")
        matrix_times = []
        
        test_pairs = [(1, 14), (2, 11), (5, 18), (9, 21), (12, 35)]
        
        with monitor_performance("baseline_matrix_lookups"):
            for improving, worsening in test_pairs:
                start_time = time.time()
                result = triz_tool_contradiction_matrix(improving, worsening)
                lookup_time = time.time() - start_time
                matrix_times.append(lookup_time)
        
        results['matrix_lookups'] = {
            'times': matrix_times,
            'avg_time': sum(matrix_times) / len(matrix_times),
            'target_met': all(t < 2.0 for t in matrix_times)
        }
        
        print(f"    Average matrix lookup time: {results['matrix_lookups']['avg_time']:.3f}s")
        
        # Test 3: Brainstorming
        print("  Testing brainstorming...")
        brainstorm_times = []
        
        contexts = [
            "automotive efficiency",
            "aerospace materials", 
            "renewable energy",
            "manufacturing optimization"
        ]
        
        with monitor_performance("baseline_brainstorming"):
            for i, context in enumerate(contexts):
                principle = (i * 10) + 1  # Use principles 1, 11, 21, 31
                start_time = time.time()
                result = triz_tool_brainstorm(principle, context)
                brainstorm_time = time.time() - start_time
                brainstorm_times.append(brainstorm_time)
        
        results['brainstorming'] = {
            'times': brainstorm_times,
            'avg_time': sum(brainstorm_times) / len(brainstorm_times),
            'target_met': all(t < 2.0 for t in brainstorm_times)
        }
        
        print(f"    Average brainstorming time: {results['brainstorming']['avg_time']:.3f}s")
        
        # Test 4: Autonomous solve (target: <10s)
        print("  Testing autonomous solve...")
        solve_times = []
        
        test_problems = [
            "Reduce weight while maintaining strength",
            "Increase speed without increasing energy consumption",
            "Improve reliability without increasing cost"
        ]
        
        with monitor_performance("baseline_autonomous_solve"):
            for problem in test_problems:
                start_time = time.time()
                result = triz_solve_autonomous(problem)
                solve_time = time.time() - start_time
                solve_times.append(solve_time)
                
                if 'analysis' not in result:
                    print(f"    ⚠️  Solve failed for: {problem[:30]}...")
        
        results['autonomous_solve'] = {
            'times': solve_times,
            'avg_time': sum(solve_times) / len(solve_times),
            'target_met': all(t < 10.0 for t in solve_times)
        }
        
        print(f"    Average autonomous solve time: {results['autonomous_solve']['avg_time']:.2f}s")
        
        # Test 5: Workflow operations
        print("  Testing workflow operations...")
        workflow_times = []
        
        with monitor_performance("baseline_workflow"):
            # Test workflow start
            start_time = time.time()
            result = triz_workflow_start()
            workflow_times.append(time.time() - start_time)
            
            if result.get('success'):
                session_id = result['session_id']
                
                # Test workflow continue
                from src.triz_tools.workflow_tools import triz_workflow_continue
                start_time = time.time()
                triz_workflow_continue(session_id, "Test workflow problem")
                workflow_times.append(time.time() - start_time)
        
        results['workflow'] = {
            'times': workflow_times,
            'avg_time': sum(workflow_times) / len(workflow_times),
            'target_met': all(t < 1.0 for t in workflow_times)  # 1s target for workflow
        }
        
        print(f"    Average workflow operation time: {results['workflow']['avg_time']:.3f}s")
        
    except Exception as e:
        print(f"    ❌ Baseline test failed: {e}")
        results['error'] = str(e)
    
    return results


def run_stress_tests() -> Dict[str, Any]:
    """Run stress tests to identify performance bottlenecks."""
    print("Running stress tests...")
    
    results = {}
    
    try:
        from src.triz_tools.direct_tools import triz_tool_get_principle
        from src.triz_tools.solve_tools import triz_solve_autonomous
        
        # Stress Test 1: Rapid tool queries
        print("  Stress testing rapid tool queries...")
        
        with monitor_performance("stress_rapid_queries"):
            start_time = time.time()
            
            for i in range(100):  # 100 rapid queries
                principle = (i % 40) + 1
                result = triz_tool_get_principle(principle)
                
                if not result.get('success'):
                    print(f"    ⚠️  Query {i} failed")
            
            total_time = time.time() - start_time
        
        results['rapid_queries'] = {
            'total_time': total_time,
            'queries_per_second': 100 / total_time,
            'avg_time_per_query': total_time / 100
        }
        
        print(f"    100 queries in {total_time:.2f}s ({results['rapid_queries']['queries_per_second']:.1f} QPS)")
        
        # Stress Test 2: Concurrent-like operations
        print("  Stress testing concurrent-like operations...")
        
        with monitor_performance("stress_concurrent"):
            start_time = time.time()
            
            # Simulate concurrent workload
            for batch in range(10):  # 10 batches
                for i in range(5):  # 5 operations per batch
                    principle = (batch * 5 + i) % 40 + 1
                    triz_tool_get_principle(principle)
            
            total_time = time.time() - start_time
        
        results['concurrent_like'] = {
            'total_time': total_time,
            'operations': 50,
            'avg_time_per_operation': total_time / 50
        }
        
        print(f"    50 concurrent-like operations in {total_time:.2f}s")
        
        # Stress Test 3: Memory pressure
        print("  Stress testing memory pressure...")
        
        optimizer = get_performance_optimizer()
        initial_snapshot = optimizer.memory_profiler.take_snapshot("stress_start")
        
        with monitor_performance("stress_memory_pressure"):
            # Generate multiple solve operations
            for i in range(10):
                problem = f"Stress test problem {i} with additional context and complexity"
                result = triz_solve_autonomous(problem)
        
        final_snapshot = optimizer.memory_profiler.take_snapshot("stress_end")
        
        results['memory_pressure'] = {
            'initial_memory_mb': initial_snapshot['rss_mb'],
            'final_memory_mb': final_snapshot['rss_mb'],
            'memory_increase_mb': final_snapshot['rss_mb'] - initial_snapshot['rss_mb'],
            'operations': 10
        }
        
        print(f"    Memory increase: {results['memory_pressure']['memory_increase_mb']:.1f}MB for 10 operations")
        
    except Exception as e:
        print(f"    ❌ Stress test failed: {e}")
        results['error'] = str(e)
    
    return results


def analyze_bottlenecks() -> Dict[str, Any]:
    """Analyze potential performance bottlenecks."""
    print("Analyzing performance bottlenecks...")
    
    bottlenecks = {}
    
    try:
        # Get performance summary
        performance_data = get_performance_summary()
        
        # Analyze metrics
        metrics_summary = performance_data.get('metrics_summary', {})
        
        for operation, stats in metrics_summary.items():
            if isinstance(stats, dict):
                avg_time = stats.get('avg_time', 0)
                max_time = stats.get('max_time', 0)
                count = stats.get('count', 0)
                
                issues = []
                
                # Check for slow operations
                if 'tool' in operation.lower() and avg_time > 1.0:
                    issues.append(f"Slow tool operation (avg: {avg_time:.2f}s)")
                elif 'solve' in operation.lower() and avg_time > 5.0:
                    issues.append(f"Slow solve operation (avg: {avg_time:.2f}s)")
                
                # Check for inconsistent performance
                if max_time > avg_time * 3:
                    issues.append(f"Inconsistent performance (max: {max_time:.2f}s vs avg: {avg_time:.2f}s)")
                
                # Check for high frequency operations
                if count > 50 and avg_time > 0.5:
                    issues.append(f"High frequency slow operation ({count} calls)")
                
                if issues:
                    bottlenecks[operation] = {
                        'issues': issues,
                        'stats': stats
                    }
        
        # Memory analysis
        memory_analysis = performance_data.get('memory_analysis', {})
        memory_growth = memory_analysis.get('rss_growth_mb', 0)
        
        if memory_growth > 50:
            bottlenecks['memory_growth'] = {
                'issues': [f"High memory growth: {memory_growth:.1f}MB"],
                'growth_data': memory_analysis
            }
        
        # System profile analysis
        system_profile = performance_data.get('system_profile', {})
        
        if system_profile.get('available_memory_mb', 0) < 500:
            bottlenecks['system_memory'] = {
                'issues': ['Low system memory available'],
                'available_mb': system_profile.get('available_memory_mb')
            }
        
        if system_profile.get('cpu_percent', 0) > 70:
            bottlenecks['system_cpu'] = {
                'issues': ['High CPU usage'],
                'cpu_percent': system_profile.get('cpu_percent')
            }
        
    except Exception as e:
        print(f"    ❌ Bottleneck analysis failed: {e}")
        bottlenecks['analysis_error'] = str(e)
    
    if bottlenecks:
        print("    Found potential bottlenecks:")
        for component, data in bottlenecks.items():
            for issue in data.get('issues', []):
                print(f"      - {component}: {issue}")
    else:
        print("    No significant bottlenecks detected")
    
    return bottlenecks


def generate_optimization_recommendations() -> List[str]:
    """Generate specific optimization recommendations."""
    print("Generating optimization recommendations...")
    
    recommendations = []
    
    try:
        # Get current performance data
        optimizer = get_performance_optimizer()
        analysis = optimizer.run_performance_analysis()
        
        # System-level recommendations
        system_profile = analysis.get('system_profile', {})
        
        process_memory = system_profile.get('process_memory_mb', 0)
        if process_memory > 1000:
            recommendations.append("HIGH PRIORITY: Process using >1GB memory")
            recommendations.append("  - Implement memory-mapped file access for large data")
            recommendations.append("  - Use lazy loading for knowledge base components")
            recommendations.append("  - Add memory cleanup after batch operations")
        
        available_memory = system_profile.get('available_memory_mb', 0)
        if available_memory < 1000:
            recommendations.append("MEDIUM PRIORITY: Low system memory")
            recommendations.append("  - Reduce vector dimensions from 768 to 384")
            recommendations.append("  - Implement aggressive caching cleanup")
            recommendations.append("  - Use swap space if available")
        
        # Performance-specific recommendations
        metrics = analysis.get('metrics_summary', {})
        
        for operation, stats in metrics.items():
            if isinstance(stats, dict):
                avg_time = stats.get('avg_time', 0)
                
                if 'tool' in operation.lower() and avg_time > 1.0:
                    recommendations.append(f"OPTIMIZATION: {operation} slow ({avg_time:.2f}s)")
                    recommendations.append("  - Add result caching for principle lookups")
                    recommendations.append("  - Preload frequently accessed principles")
                    recommendations.append("  - Optimize knowledge base search indexing")
                
                if 'solve' in operation.lower() and avg_time > 8.0:
                    recommendations.append(f"OPTIMIZATION: {operation} slow ({avg_time:.2f}s)")
                    recommendations.append("  - Implement parallel contradiction analysis")
                    recommendations.append("  - Cache intermediate analysis results")
                    recommendations.append("  - Optimize solution generation algorithms")
        
        # Cache-specific recommendations
        cache_efficiency = analysis.get('cache_efficiency', {})
        
        for cache_name, hit_rate in cache_efficiency.items():
            if hit_rate < 0.7:
                recommendations.append(f"CACHE OPTIMIZATION: {cache_name} low hit rate ({hit_rate:.1%})")
                recommendations.append(f"  - Increase cache size for {cache_name}")
                recommendations.append(f"  - Improve cache key strategy for {cache_name}")
                recommendations.append(f"  - Implement cache warming for {cache_name}")
        
        # General recommendations
        recommendations.extend([
            "",
            "GENERAL OPTIMIZATIONS:",
            "  - Enable compression for cached embeddings",
            "  - Use connection pooling for database operations", 
            "  - Implement request batching for external services",
            "  - Add performance monitoring to production",
            "  - Configure garbage collection tuning",
            "  - Use memory profiling in development"
        ])
        
    except Exception as e:
        recommendations.append(f"Error generating recommendations: {e}")
    
    return recommendations


def main():
    """Main performance analysis function."""
    parser = argparse.ArgumentParser(description="TRIZ System Performance Analysis")
    parser.add_argument('--baseline', action='store_true', help='Run baseline tests')
    parser.add_argument('--stress', action='store_true', help='Run stress tests')
    parser.add_argument('--analyze', action='store_true', help='Analyze bottlenecks')
    parser.add_argument('--optimize', action='store_true', help='Run optimizations')
    parser.add_argument('--all', action='store_true', help='Run all analyses')
    parser.add_argument('--export', type=str, help='Export results to file')
    
    args = parser.parse_args()
    
    if not any([args.baseline, args.stress, args.analyze, args.optimize, args.all]):
        args.all = True  # Default to all if nothing specified
    
    print("=" * 60)
    print("TRIZ Engineering Co-Pilot - Performance Analysis")
    print("=" * 60)
    
    results = {
        'timestamp': time.time(),
        'analysis_type': 'comprehensive' if args.all else 'partial'
    }
    
    # Initialize optimizer
    optimizer = get_performance_optimizer()
    optimizer.start_profiling()
    
    try:
        if args.baseline or args.all:
            results['baseline_tests'] = run_baseline_tests()
        
        if args.stress or args.all:
            results['stress_tests'] = run_stress_tests()
        
        if args.analyze or args.all:
            results['bottleneck_analysis'] = analyze_bottlenecks()
        
        if args.optimize or args.all:
            print("Running system optimization...")
            results['optimization'] = optimize_triz_system()
        
        # Always generate recommendations
        results['recommendations'] = generate_optimization_recommendations()
        
        # Get final performance summary
        results['performance_summary'] = get_performance_summary()
        
    finally:
        optimizer.stop_profiling()
    
    # Print recommendations
    print("\n" + "=" * 60)
    print("OPTIMIZATION RECOMMENDATIONS")
    print("=" * 60)
    
    for recommendation in results.get('recommendations', []):
        print(recommendation)
    
    # Export if requested
    if args.export:
        export_file = Path(args.export)
        with open(export_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"\n📄 Results exported to: {export_file}")
    
    # Summary
    print("\n" + "=" * 60)
    print("PERFORMANCE ANALYSIS COMPLETE")
    print("=" * 60)
    
    # Check if performance targets are met
    baseline = results.get('baseline_tests', {})
    targets_met = []
    
    if 'tool_queries' in baseline:
        targets_met.append(baseline['tool_queries'].get('target_met', False))
    if 'autonomous_solve' in baseline:
        targets_met.append(baseline['autonomous_solve'].get('target_met', False))
    
    if all(targets_met) and targets_met:
        print("🎉 All performance targets met!")
    elif any(targets_met):
        print("⚠️  Some performance targets not met - review recommendations")
    else:
        print("❌ Performance targets not achieved - optimization needed")
    
    return 0 if (all(targets_met) and targets_met) else 1


if __name__ == '__main__':
    sys.exit(main())