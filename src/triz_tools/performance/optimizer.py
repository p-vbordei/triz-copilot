#!/usr/bin/env python3
"""
Performance Optimizer (T063)

Analyzes system performance and provides optimization recommendations.
"""

import time
import psutil
import gc
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
import threading
from functools import wraps
import cProfile
import pstats
import io

import logging
logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Performance metrics for a specific operation."""
    operation_name: str
    execution_time: float
    memory_usage_mb: float
    cpu_percent: float
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "operation_name": self.operation_name,
            "execution_time": self.execution_time,
            "memory_usage_mb": self.memory_usage_mb,
            "cpu_percent": self.cpu_percent,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }


@dataclass
class SystemProfile:
    """System performance profile."""
    total_memory_mb: float
    available_memory_mb: float
    cpu_count: int
    cpu_percent: float
    disk_usage_percent: float
    python_version: str
    process_memory_mb: float
    thread_count: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_memory_mb": self.total_memory_mb,
            "available_memory_mb": self.available_memory_mb,
            "cpu_count": self.cpu_count,
            "cpu_percent": self.cpu_percent,
            "disk_usage_percent": self.disk_usage_percent,
            "python_version": self.python_version,
            "process_memory_mb": self.process_memory_mb,
            "thread_count": self.thread_count
        }


class PerformanceMonitor:
    """Monitor system and application performance."""
    
    def __init__(self):
        self.metrics: List[PerformanceMetrics] = []
        self.start_time = time.time()
        self.initial_memory = self._get_memory_usage()
        self._lock = threading.Lock()
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        import os
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / 1024 / 1024
    
    def _get_cpu_percent(self) -> float:
        """Get current CPU usage percent."""
        try:
            return psutil.cpu_percent(interval=0.1)
        except:
            return 0.0
    
    def record_metric(self, operation_name: str, execution_time: float, **metadata):
        """Record a performance metric."""
        metric = PerformanceMetrics(
            operation_name=operation_name,
            execution_time=execution_time,
            memory_usage_mb=self._get_memory_usage(),
            cpu_percent=self._get_cpu_percent(),
            metadata=metadata
        )
        
        with self._lock:
            self.metrics.append(metric)
    
    def get_system_profile(self) -> SystemProfile:
        """Get current system profile."""
        import os
        
        virtual_memory = psutil.virtual_memory()
        disk_usage = psutil.disk_usage('/')
        process = psutil.Process(os.getpid())
        
        return SystemProfile(
            total_memory_mb=virtual_memory.total / 1024 / 1024,
            available_memory_mb=virtual_memory.available / 1024 / 1024,
            cpu_count=psutil.cpu_count(),
            cpu_percent=psutil.cpu_percent(interval=0.1),
            disk_usage_percent=disk_usage.percent,
            python_version=sys.version,
            process_memory_mb=process.memory_info().rss / 1024 / 1024,
            thread_count=threading.active_count()
        )
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of recorded metrics."""
        if not self.metrics:
            return {"message": "No metrics recorded"}
        
        # Group by operation
        by_operation: Dict[str, List[PerformanceMetrics]] = {}
        for metric in self.metrics:
            if metric.operation_name not in by_operation:
                by_operation[metric.operation_name] = []
            by_operation[metric.operation_name].append(metric)
        
        summary = {}
        for operation, metrics in by_operation.items():
            times = [m.execution_time for m in metrics]
            memory = [m.memory_usage_mb for m in metrics]
            
            summary[operation] = {
                "count": len(metrics),
                "avg_time": sum(times) / len(times),
                "min_time": min(times),
                "max_time": max(times),
                "avg_memory": sum(memory) / len(memory),
                "total_time": sum(times)
            }
        
        return summary
    
    def clear_metrics(self):
        """Clear recorded metrics."""
        with self._lock:
            self.metrics.clear()


# Global performance monitor instance
_performance_monitor = PerformanceMonitor()


def performance_monitor(operation_name: Optional[str] = None):
    """Decorator to monitor function performance."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            op_name = operation_name or f"{func.__module__}.{func.__name__}"
            
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                execution_time = time.time() - start_time
                _performance_monitor.record_metric(
                    op_name,
                    execution_time,
                    args_count=len(args),
                    kwargs_count=len(kwargs)
                )
        return wrapper
    return decorator


class MemoryProfiler:
    """Memory usage profiler and optimizer."""
    
    def __init__(self):
        self.snapshots: List[Dict[str, Any]] = []
    
    def take_snapshot(self, label: str = ""):
        """Take a memory snapshot."""
        import os
        
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        
        snapshot = {
            "label": label,
            "timestamp": datetime.now().isoformat(),
            "rss_mb": memory_info.rss / 1024 / 1024,
            "vms_mb": memory_info.vms / 1024 / 1024,
            "percent": process.memory_percent(),
            "num_threads": process.num_threads(),
            "num_fds": getattr(process, 'num_fds', lambda: 0)(),
            "gc_counts": gc.get_count()
        }
        
        self.snapshots.append(snapshot)
        return snapshot
    
    def analyze_memory_growth(self) -> Dict[str, Any]:
        """Analyze memory growth over time."""
        if len(self.snapshots) < 2:
            return {"error": "Need at least 2 snapshots"}
        
        first = self.snapshots[0]
        last = self.snapshots[-1]
        
        growth = {
            "rss_growth_mb": last["rss_mb"] - first["rss_mb"],
            "vms_growth_mb": last["vms_mb"] - first["vms_mb"],
            "percent_growth": last["percent"] - first["percent"],
            "time_span": len(self.snapshots),
            "avg_growth_per_snapshot": (last["rss_mb"] - first["rss_mb"]) / len(self.snapshots)
        }
        
        return growth
    
    def suggest_optimizations(self) -> List[str]:
        """Suggest memory optimizations."""
        suggestions = []
        
        if not self.snapshots:
            return ["Take memory snapshots first"]
        
        latest = self.snapshots[-1]
        
        # High memory usage
        if latest["rss_mb"] > 500:
            suggestions.append("High memory usage detected (>500MB). Consider:")
            suggestions.append("  - Enable caching with size limits")
            suggestions.append("  - Use generators instead of lists for large datasets")
            suggestions.append("  - Implement object pooling for frequently created objects")
        
        # Memory growth
        if len(self.snapshots) > 5:
            growth = self.analyze_memory_growth()
            if growth.get("rss_growth_mb", 0) > 100:
                suggestions.append("Significant memory growth detected. Check for:")
                suggestions.append("  - Memory leaks in long-running operations")
                suggestions.append("  - Unclosed file handles or database connections")
                suggestions.append("  - Circular references preventing garbage collection")
        
        # High thread count
        if latest["num_threads"] > 10:
            suggestions.append("High thread count. Consider:")
            suggestions.append("  - Using thread pools instead of creating threads on demand")
            suggestions.append("  - Asynchronous programming patterns")
        
        # Garbage collection
        gc_total = sum(latest["gc_counts"])
        if gc_total > 1000:
            suggestions.append("High garbage collection activity. Consider:")
            suggestions.append("  - Reducing object creation in hot paths")
            suggestions.append("  - Using __slots__ for frequently created classes")
            suggestions.append("  - Manual garbage collection for batch operations")
        
        return suggestions if suggestions else ["Memory usage appears optimal"]


class CacheOptimizer:
    """Optimize caching strategies."""
    
    def __init__(self):
        self.cache_stats: Dict[str, Dict[str, int]] = {}
    
    def record_cache_access(self, cache_name: str, hit: bool):
        """Record cache hit/miss."""
        if cache_name not in self.cache_stats:
            self.cache_stats[cache_name] = {"hits": 0, "misses": 0}
        
        if hit:
            self.cache_stats[cache_name]["hits"] += 1
        else:
            self.cache_stats[cache_name]["misses"] += 1
    
    def get_cache_efficiency(self) -> Dict[str, float]:
        """Get cache hit rates."""
        efficiency = {}
        
        for cache_name, stats in self.cache_stats.items():
            total = stats["hits"] + stats["misses"]
            if total > 0:
                efficiency[cache_name] = stats["hits"] / total
            else:
                efficiency[cache_name] = 0.0
        
        return efficiency
    
    def suggest_cache_optimizations(self) -> List[str]:
        """Suggest cache optimizations."""
        suggestions = []
        efficiency = self.get_cache_efficiency()
        
        for cache_name, hit_rate in efficiency.items():
            if hit_rate < 0.5:
                suggestions.append(f"Low hit rate for {cache_name} ({hit_rate:.1%}). Consider:")
                suggestions.append(f"  - Adjusting cache size for {cache_name}")
                suggestions.append(f"  - Reviewing cache key strategy for {cache_name}")
                suggestions.append(f"  - Implementing cache warming for {cache_name}")
            elif hit_rate > 0.95:
                suggestions.append(f"Excellent hit rate for {cache_name} ({hit_rate:.1%})")
        
        return suggestions


class PerformanceOptimizer:
    """Main performance optimization coordinator."""
    
    def __init__(self):
        self.monitor = _performance_monitor
        self.memory_profiler = MemoryProfiler()
        self.cache_optimizer = CacheOptimizer()
        self.profiling_enabled = False
        self.profile_data: Optional[Dict[str, Any]] = None
    
    def start_profiling(self):
        """Start detailed profiling."""
        self.profiling_enabled = True
        self.memory_profiler.take_snapshot("profiling_start")
        logger.info("Performance profiling started")
    
    def stop_profiling(self):
        """Stop profiling and generate report."""
        self.profiling_enabled = False
        self.memory_profiler.take_snapshot("profiling_end")
        logger.info("Performance profiling stopped")
    
    def run_performance_analysis(self) -> Dict[str, Any]:
        """Run comprehensive performance analysis."""
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "system_profile": self.monitor.get_system_profile().to_dict(),
            "metrics_summary": self.monitor.get_metrics_summary(),
            "memory_analysis": self.memory_profiler.analyze_memory_growth(),
            "cache_efficiency": self.cache_optimizer.get_cache_efficiency(),
            "recommendations": self._generate_recommendations()
        }
        
        return analysis
    
    def _generate_recommendations(self) -> List[str]:
        """Generate optimization recommendations."""
        recommendations = []
        
        # System-level recommendations
        system_profile = self.monitor.get_system_profile()
        
        if system_profile.available_memory_mb < 1000:
            recommendations.append("Low available memory (<1GB). Consider increasing system RAM.")
        
        if system_profile.cpu_percent > 80:
            recommendations.append("High CPU usage (>80%). Consider optimizing algorithms or adding CPU cores.")
        
        if system_profile.process_memory_mb > 1000:
            recommendations.append("High process memory (>1GB). Consider memory optimization.")
        
        # Add memory profiler suggestions
        memory_suggestions = self.memory_profiler.suggest_optimizations()
        recommendations.extend(memory_suggestions)
        
        # Add cache optimizer suggestions
        cache_suggestions = self.cache_optimizer.suggest_cache_optimizations()
        recommendations.extend(cache_suggestions)
        
        # Performance metrics recommendations
        metrics_summary = self.monitor.get_metrics_summary()
        for operation, stats in metrics_summary.items():
            if isinstance(stats, dict):
                avg_time = stats.get("avg_time", 0)
                if "tool" in operation.lower() and avg_time > 2.0:
                    recommendations.append(f"Tool operation {operation} exceeds 2s target ({avg_time:.2f}s)")
                elif "solve" in operation.lower() and avg_time > 10.0:
                    recommendations.append(f"Solve operation {operation} exceeds 10s target ({avg_time:.2f}s)")
        
        return recommendations if recommendations else ["System performance appears optimal"]
    
    def optimize_system(self) -> Dict[str, Any]:
        """Apply automatic optimizations where possible."""
        optimizations_applied = []
        
        # Force garbage collection
        collected = gc.collect()
        if collected > 0:
            optimizations_applied.append(f"Garbage collection freed {collected} objects")
        
        # Clear performance metrics if too many
        if len(self.monitor.metrics) > 1000:
            self.monitor.clear_metrics()
            optimizations_applied.append("Cleared old performance metrics")
        
        # Take memory snapshot for tracking
        self.memory_profiler.take_snapshot("optimization_applied")
        
        return {
            "optimizations_applied": optimizations_applied,
            "timestamp": datetime.now().isoformat()
        }
    
    def profile_function(self, func: Callable, *args, **kwargs) -> Dict[str, Any]:
        """Profile a specific function call."""
        profiler = cProfile.Profile()
        
        start_memory = self.memory_profiler.take_snapshot("function_start")
        
        profiler.enable()
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
        finally:
            execution_time = time.time() - start_time
            profiler.disable()
        
        end_memory = self.memory_profiler.take_snapshot("function_end")
        
        # Capture profiler output
        s = io.StringIO()
        ps = pstats.Stats(profiler, stream=s)
        ps.sort_stats('cumulative')
        ps.print_stats(20)  # Top 20 functions
        
        return {
            "execution_time": execution_time,
            "memory_delta_mb": end_memory["rss_mb"] - start_memory["rss_mb"],
            "profile_output": s.getvalue(),
            "result_available": result is not None
        }
    
    def export_performance_data(self, file_path: Path) -> bool:
        """Export performance data to file."""
        try:
            data = {
                "export_timestamp": datetime.now().isoformat(),
                "system_profile": self.monitor.get_system_profile().to_dict(),
                "metrics": [m.to_dict() for m in self.monitor.metrics[-100:]],  # Last 100
                "memory_snapshots": self.memory_profiler.snapshots[-20:],  # Last 20
                "cache_stats": self.cache_optimizer.cache_stats,
                "analysis": self.run_performance_analysis()
            }
            
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Performance data exported to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export performance data: {e}")
            return False


# Global optimizer instance
_performance_optimizer = PerformanceOptimizer()


def get_performance_optimizer() -> PerformanceOptimizer:
    """Get global performance optimizer instance."""
    return _performance_optimizer


def optimize_triz_system() -> Dict[str, Any]:
    """Run complete TRIZ system optimization."""
    optimizer = get_performance_optimizer()
    
    print("Starting TRIZ system performance optimization...")
    
    # Start profiling
    optimizer.start_profiling()
    
    try:
        # Test key system operations
        from src.triz_tools.direct_tools import triz_tool_get_principle
        from src.triz_tools.solve_tools import triz_solve_autonomous
        
        # Profile tool operations
        for principle_id in [1, 15, 40]:
            with performance_monitor(f"tool_test_{principle_id}"):
                triz_tool_get_principle(principle_id)
        
        # Profile solve operation
        with performance_monitor("solve_test"):
            triz_solve_autonomous("Test optimization problem")
        
        # Apply optimizations
        optimization_result = optimizer.optimize_system()
        
        # Generate analysis
        analysis = optimizer.run_performance_analysis()
        
        return {
            "optimization_result": optimization_result,
            "performance_analysis": analysis,
            "status": "completed"
        }
        
    except Exception as e:
        logger.error(f"Optimization failed: {e}")
        return {
            "error": str(e),
            "status": "failed"
        }
    finally:
        optimizer.stop_profiling()


class PerformanceContext:
    """Context manager for performance monitoring."""
    
    def __init__(self, operation_name: str, optimizer: Optional[PerformanceOptimizer] = None):
        self.operation_name = operation_name
        self.optimizer = optimizer or get_performance_optimizer()
        self.start_time = None
        self.start_memory = None
    
    def __enter__(self):
        self.start_time = time.time()
        if self.optimizer.profiling_enabled:
            self.start_memory = self.optimizer.memory_profiler.take_snapshot(f"{self.operation_name}_start")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        execution_time = time.time() - self.start_time
        
        if self.optimizer.profiling_enabled and self.start_memory:
            end_memory = self.optimizer.memory_profiler.take_snapshot(f"{self.operation_name}_end")
            memory_delta = end_memory["rss_mb"] - self.start_memory["rss_mb"]
            
            self.optimizer.monitor.record_metric(
                self.operation_name,
                execution_time,
                memory_delta_mb=memory_delta,
                had_exception=exc_type is not None
            )
        else:
            self.optimizer.monitor.record_metric(
                self.operation_name,
                execution_time,
                had_exception=exc_type is not None
            )


# Convenience functions
def monitor_performance(operation_name: str):
    """Context manager for performance monitoring."""
    return PerformanceContext(operation_name)


def get_performance_summary() -> Dict[str, Any]:
    """Get performance summary."""
    return _performance_optimizer.run_performance_analysis()


def clear_performance_data():
    """Clear all performance data."""
    _performance_optimizer.monitor.clear_metrics()
    _performance_optimizer.memory_profiler.snapshots.clear()
    _performance_optimizer.cache_optimizer.cache_stats.clear()


def export_performance_report(file_path: str) -> bool:
    """Export performance report to file."""
    return _performance_optimizer.export_performance_data(Path(file_path))