#!/usr/bin/env python3
"""
Performance Analysis and Optimization Module

Provides comprehensive performance monitoring, analysis, and optimization
capabilities for the TRIZ Engineering Co-Pilot system.
"""

from .optimizer import (
    PerformanceOptimizer,
    PerformanceMonitor,
    MemoryProfiler,
    CacheOptimizer,
    PerformanceMetrics,
    SystemProfile,
    PerformanceContext,
    performance_monitor,
    monitor_performance,
    get_performance_optimizer,
    get_performance_summary,
    clear_performance_data,
    export_performance_report,
    optimize_triz_system
)

__all__ = [
    # Main classes
    'PerformanceOptimizer',
    'PerformanceMonitor', 
    'MemoryProfiler',
    'CacheOptimizer',
    
    # Data classes
    'PerformanceMetrics',
    'SystemProfile',
    'PerformanceContext',
    
    # Decorators
    'performance_monitor',
    
    # Functions
    'monitor_performance',
    'get_performance_optimizer',
    'get_performance_summary',
    'clear_performance_data',
    'export_performance_report',
    'optimize_triz_system'
]