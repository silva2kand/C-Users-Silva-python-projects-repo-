"""SpecKit - Advanced Testing Framework for Python Applications

SpecKit is a comprehensive testing framework that provides:
- Enhanced test discovery and execution
- GUI testing capabilities for PyQt applications
- Performance benchmarking and profiling
- Mock data generation and factories
- Advanced assertion methods
- Test reporting and analytics

Version: 1.0.0
Author: Ciniforge Development Team
"""

import os
import sys
from pathlib import Path

__version__ = "1.0.0"
__author__ = "Ciniforge Development Team"
__email__ = "dev@ciniforge.com"

# Core imports
from .base_test import BaseTest, AsyncBaseTest
from .mocks import MockFactory
from .gui_test import GUITestCase, MockGUITestCase
from .performance import (
    benchmark, 
    performance_context, 
    PerformanceMonitor, 
    LoadTester,
    memory_profiler
)

__all__ = [
    'BaseTest',
    'AsyncBaseTest', 
    'MockFactory',
    'GUITestCase',
    'MockGUITestCase',
    'benchmark',
    'performance_context',
    'PerformanceMonitor',
    'LoadTester',
    'memory_profiler',
    'setup_project'
]

def setup_project(project_path: str = None, create_structure: bool = True):
    """Set up SpecKit testing structure for a new project
    
    Args:
        project_path: Path to the project directory (defaults to current directory)
        create_structure: Whether to create the testing directory structure
    """
    if project_path is None:
        project_path = os.getcwd()
    
    project_path = Path(project_path)
    
    if create_structure:
        # Create testing directories
        test_dirs = [
            project_path / "tests",
            project_path / "tests" / "unit",
            project_path / "tests" / "integration", 
            project_path / "tests" / "gui",
            project_path / "tests" / "performance",
            project_path / "tests" / "fixtures"
        ]
        
        for test_dir in test_dirs:
            test_dir.mkdir(parents=True, exist_ok=True)
            
            # Create __init__.py files
            init_file = test_dir / "__init__.py"
            if not init_file.exists():
                init_file.write_text(f'"""Tests for {test_dir.name}"""\n')
    
    # Create sample test files
    sample_files = {
        "tests/test_example.py": '''"""Example test file using SpecKit"""

from speckit import BaseTest, MockFactory, benchmark

class TestExample(BaseTest):
    """Example test class"""
    
    def setUp(self):
        super().setUp()
        self.mock_data = MockFactory.mock_user()
    
    def test_basic_functionality(self):
        """Test basic functionality"""
        self.assertIsNotNone(self.mock_data)
        self.assertIn('username', self.mock_data)
    
    @benchmark(iterations=100)
    def test_performance_example(self):
        """Example performance test"""
        # Simulate some work
        result = sum(range(1000))
        self.assertEqual(result, 499500)
''',
        "tests/conftest.py": '''"""Pytest configuration for SpecKit"""

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
''',
        "pytest.ini": '''[tool:pytest]
addopts = -v --tb=short --strict-markers
testpaths = tests
python_files = test_*.py *_test.py
python_classes = Test*
python_functions = test_*
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    gui: marks tests as GUI tests
    performance: marks tests as performance tests
'''
    }
    
    for file_path, content in sample_files.items():
        full_path = project_path / file_path
        if not full_path.exists():
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content)
    
    print(f"✅ SpecKit project structure created at: {project_path}")
    print("\n📁 Created directories:")
    print("  - tests/unit/")
    print("  - tests/integration/")
    print("  - tests/gui/")
    print("  - tests/performance/")
    print("  - tests/fixtures/")
    print("\n📄 Created files:")
    print("  - tests/test_example.py")
    print("  - tests/conftest.py")
    print("  - pytest.ini")
    print("\n🚀 Ready to start testing with SpecKit!")
    print("\nNext steps:")
    print("  1. Install dependencies: pip install -r requirements.txt")
    print("  2. Run tests: pytest")
    print("  3. Run with coverage: pytest --cov=src")
    
    return project_path

# Auto-setup when imported in a project
if __name__ != "__main__":
    # Check if we're in a project that might benefit from auto-setup
    current_dir = Path.cwd()
    if (current_dir / "src").exists() or (current_dir / "main.py").exists():
        tests_dir = current_dir / "tests"
        if not tests_dir.exists():
            print("🔧 SpecKit detected a project without tests directory.")
            print("   Run 'from speckit import setup_project; setup_project()' to initialize testing structure.")