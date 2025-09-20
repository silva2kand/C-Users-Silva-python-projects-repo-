"""Base test classes for SpecKit framework"""

import unittest
import asyncio
import time
from typing import Any, Dict, List, Optional
from pathlib import Path

class BaseTest(unittest.TestCase):
    """Enhanced base test class with common utilities"""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.start_time = time.time()
        self.test_data = {}
        
    def tearDown(self):
        """Clean up after each test method."""
        elapsed = time.time() - self.start_time
        print(f"Test {self._testMethodName} completed in {elapsed:.3f}s")
        
    def assert_performance(self, max_seconds: float = 1.0):
        """Assert that test completed within time limit"""
        elapsed = time.time() - self.start_time
        self.assertLess(elapsed, max_seconds, 
                       f"Test took {elapsed:.3f}s, expected < {max_seconds}s")
    
    def assert_file_exists(self, file_path: str):
        """Assert that a file exists"""
        self.assertTrue(Path(file_path).exists(), f"File {file_path} does not exist")
        
    def assert_dir_exists(self, dir_path: str):
        """Assert that a directory exists"""
        self.assertTrue(Path(dir_path).is_dir(), f"Directory {dir_path} does not exist")
        
    def create_temp_file(self, content: str = "", suffix: str = ".txt") -> Path:
        """Create a temporary file for testing"""
        import tempfile
        temp_file = Path(tempfile.mktemp(suffix=suffix))
        temp_file.write_text(content)
        return temp_file
        
    def mock_response(self, status_code: int = 200, json_data: Dict = None, text: str = ""):
        """Create a mock HTTP response"""
        class MockResponse:
            def __init__(self, status_code, json_data, text):
                self.status_code = status_code
                self._json_data = json_data or {}
                self.text = text
                
            def json(self):
                return self._json_data
                
        return MockResponse(status_code, json_data, text)

class AsyncBaseTest(BaseTest):
    """Base test class for async operations"""
    
    def setUp(self):
        super().setUp()
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
    def tearDown(self):
        self.loop.close()
        super().tearDown()
        
    def run_async(self, coro):
        """Run an async coroutine in the test loop"""
        return self.loop.run_until_complete(coro)
        
    async def assert_async_performance(self, coro, max_seconds: float = 1.0):
        """Assert that async operation completes within time limit"""
        start = time.time()
        result = await coro
        elapsed = time.time() - start
        self.assertLess(elapsed, max_seconds,
                       f"Async operation took {elapsed:.3f}s, expected < {max_seconds}s")
        return result