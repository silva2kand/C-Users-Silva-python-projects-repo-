"""Pytest configuration for SpecKit"""

import pytest
from speckit import PerformanceMonitor

@pytest.fixture(scope="session")
def performance_monitor():
    """Global performance monitor fixture"""
    monitor = PerformanceMonitor()
    monitor.start_monitoring()
    yield monitor
    monitor.stop_monitoring()

@pytest.fixture(autouse=True)
def clear_performance_metrics(performance_monitor):
    """Clear performance metrics before each test"""
    performance_monitor.clear_metrics()
