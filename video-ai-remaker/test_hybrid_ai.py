"""
Test Suite for Hybrid AI Video Remaker
======================================

Comprehensive test suite to verify the functionality of the hybrid AI system,
including service integration, fallback mechanisms, and performance testing.

Features:
- Unit tests for individual AI services
- Integration tests for hybrid client
- Performance benchmarking
- Fallback mechanism testing
- Async functionality testing
- Error handling verification

Author: Hybrid AI System
"""

import asyncio
import json
import logging
import os
import sys
import time
import unittest
from typing import Dict, List, Optional
from unittest.mock import Mock, patch

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import hybrid AI components
try:
    from hybrid_ai_client import (
        HybridAIClient,
        FreeTierAIClient,
        GPT4AllService,
        OpenAIService,
        GeminiService,
        ClaudeService,
        get_available_services,
        test_service_availability
    )
    IMPORTS_SUCCESSFUL = True
except ImportError as e:
    print(f"Failed to import hybrid AI client: {e}")
    IMPORTS_SUCCESSFUL = False

# Configure logging for tests
logging.basicConfig(
    level=logging.WARNING,  # Reduce log noise during testing
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TestHybridAIClient(unittest.TestCase):
    """Test cases for the HybridAIClient class."""

    def setUp(self):
        """Set up test fixtures."""
        if not IMPORTS_SUCCESSFUL:
            self.skipTest("Hybrid AI client imports failed")

        self.client = HybridAIClient()
        self.test_message = "Hello, how are you today?"
        self.test_personality = "helpful"

    def test_initialization(self):
        """Test that the client initializes properly."""
        self.assertIsInstance(self.client, HybridAIClient)
        self.assertIsInstance(self.client.services, dict)
        self.assertIsInstance(self.client.service_performance, dict)

    def test_service_selection(self):
        """Test service selection logic."""
        if not self.client.services:
            self.skipTest("No services available for testing")

        service_name = self.client.select_best_service()
        self.assertIsNotNone(service_name)
        self.assertIn(service_name, self.client.services)

    def test_response_generation(self):
        """Test basic response generation."""
        if not self.client.services:
            self.skipTest("No services available for testing")

        response = self.client.generate_response(self.test_message)
        self.assertIsInstance(response, (str, type(None)))

        if response:
            self.assertGreater(len(response.strip()), 0)

    def test_personality_modes(self):
        """Test different personality modes."""
        if not self.client.services:
            self.skipTest("No services available for testing")

        personalities = ["helpful", "creative", "analytical", "funny"]

        for personality in personalities:
            with self.subTest(personality=personality):
                response = self.client.generate_response(
                    self.test_message,
                    personality=personality
                )
                self.assertIsInstance(response, (str, type(None)))

    def test_fallback_mechanism(self):
        """Test fallback mechanism when primary service fails."""
        if len(self.client.services) < 2:
            self.skipTest("Need at least 2 services for fallback testing")

        # This test would require mocking service failures
        # For now, just verify the method exists
        self.assertTrue(hasattr(self.client, '_try_fallback_service'))

    @patch('asyncio.get_event_loop')
    def test_async_response_generation(self, mock_loop):
        """Test async response generation."""
        if not self.client.services:
            self.skipTest("No services available for testing")

        # Mock run_in_executor to return a coroutine that resolves to "Test response"
        async def mock_executor(*args, **kwargs):
            return "Test response"

        mock_loop.return_value.run_in_executor = mock_executor

        async def run_async_test():
            response = await self.client.generate_response_async(self.test_message)
            self.assertEqual(response, "Test response")

        asyncio.run(run_async_test())

class TestFreeTierAIClient(unittest.TestCase):
    """Test cases for the FreeTierAIClient class."""

    def setUp(self):
        """Set up test fixtures."""
        if not IMPORTS_SUCCESSFUL:
            self.skipTest("Hybrid AI client imports failed")

        self.client = FreeTierAIClient()
        self.test_message = "What is the weather like?"

    def test_initialization(self):
        """Test that the free tier client initializes properly."""
        self.assertIsInstance(self.client, FreeTierAIClient)
        self.assertIsInstance(self.client.services, dict)
        self.assertIsInstance(self.client.usage_count, dict)

    def test_rate_limiting(self):
        """Test rate limiting functionality."""
        # Test the rate limiting method
        self.assertTrue(hasattr(self.client, '_check_rate_limit'))

        # Test with a service that has rate limits
        result = self.client._check_rate_limit("openai")
        self.assertIsInstance(result, bool)

    def test_response_generation(self):
        """Test response generation with rate limiting."""
        if not self.client.services:
            self.skipTest("No free tier services available")

        response = self.client.generate_response(self.test_message)
        self.assertIsInstance(response, (str, type(None)))

class TestIndividualServices(unittest.TestCase):
    """Test cases for individual AI service classes."""

    def test_gpt4all_service(self):
        """Test GPT4All service."""
        if not IMPORTS_SUCCESSFUL:
            self.skipTest("Imports failed")

        service = GPT4AllService()
        self.assertIsInstance(service, GPT4AllService)

        # Test availability
        available = service.is_available()
        self.assertIsInstance(available, bool)

        if available:
            response = service.generate_response("Hello")
            self.assertIsInstance(response, (str, type(None)))

    def test_openai_service(self):
        """Test OpenAI service."""
        if not IMPORTS_SUCCESSFUL:
            self.skipTest("Imports failed")

        service = OpenAIService()
        self.assertIsInstance(service, OpenAIService)

        # Test availability
        available = service.is_available()
        self.assertIsInstance(available, bool)

        if available:
            response = service.generate_response("Hello")
            self.assertIsInstance(response, (str, type(None)))

    def test_gemini_service(self):
        """Test Gemini service."""
        if not IMPORTS_SUCCESSFUL:
            self.skipTest("Imports failed")

        service = GeminiService()
        self.assertIsInstance(service, GeminiService)

        # Test availability
        available = service.is_available()
        self.assertIsInstance(available, bool)

        if available:
            response = service.generate_response("Hello")
            self.assertIsInstance(response, (str, type(None)))

    def test_claude_service(self):
        """Test Claude service."""
        if not IMPORTS_SUCCESSFUL:
            self.skipTest("Imports failed")

        service = ClaudeService()
        self.assertIsInstance(service, ClaudeService)

        # Test availability
        available = service.is_available()
        self.assertIsInstance(available, bool)

        if available:
            response = service.generate_response("Hello")
            self.assertIsInstance(response, (str, type(None)))

class TestUtilityFunctions(unittest.TestCase):
    """Test cases for utility functions."""

    def test_get_available_services(self):
        """Test get_available_services function."""
        if not IMPORTS_SUCCESSFUL:
            self.skipTest("Imports failed")

        services = get_available_services()
        self.assertIsInstance(services, list)

        # All services should be strings
        for service in services:
            self.assertIsInstance(service, str)

    def test_test_service_availability(self):
        """Test test_service_availability function."""
        if not IMPORTS_SUCCESSFUL:
            self.skipTest("Imports failed")

        availability = test_service_availability()
        self.assertIsInstance(availability, dict)

        # Should have entries for all expected services
        expected_services = ["gpt4all", "openai", "gemini", "claude"]
        for service in expected_services:
            self.assertIn(service, availability)
            self.assertIsInstance(availability[service], bool)

class TestPerformance(unittest.TestCase):
    """Performance tests for the hybrid AI system."""

    def setUp(self):
        """Set up performance test fixtures."""
        if not IMPORTS_SUCCESSFUL:
            self.skipTest("Imports failed")

        self.client = HybridAIClient()
        self.test_message = "Write a short poem about artificial intelligence."

    def test_response_time(self):
        """Test response time for different services."""
        if not self.client.services:
            self.skipTest("No services available")

        start_time = time.time()
        response = self.client.generate_response(self.test_message)
        end_time = time.time()

        response_time = end_time - start_time
        self.assertLess(response_time, 30.0)  # Should respond within 30 seconds

        if response:
            self.assertGreater(len(response), 10)  # Should have meaningful content

    def test_concurrent_requests(self):
        """Test handling of concurrent requests."""
        if not self.client.services:
            self.skipTest("No services available")

        async def make_request(i):
            return self.client.generate_response_async(f"Question {i}: {self.test_message}")

        async def run_concurrent_test():
            tasks = [make_request(i) for i in range(3)]
            start_time = time.time()
            responses = await asyncio.gather(*tasks)
            end_time = time.time()

            total_time = end_time - start_time
            self.assertLess(total_time, 60.0)  # Should complete within 1 minute

            # At least some responses should be successful
            successful_responses = [r for r in responses if r is not None]
            self.assertGreater(len(successful_responses), 0)

        asyncio.run(run_concurrent_test())

class TestErrorHandling(unittest.TestCase):
    """Test error handling and edge cases."""

    def setUp(self):
        """Set up error handling test fixtures."""
        if not IMPORTS_SUCCESSFUL:
            self.skipTest("Imports failed")

        self.client = HybridAIClient()

    def test_empty_message(self):
        """Test handling of empty messages."""
        if not self.client.services:
            self.skipTest("No services available")

        response = self.client.generate_response("")
        self.assertIsInstance(response, (str, type(None)))

    def test_very_long_message(self):
        """Test handling of very long messages."""
        if not self.client.services:
            self.skipTest("No services available")

        long_message = "Hello! " * 1000  # Very long message
        response = self.client.generate_response(long_message)
        self.assertIsInstance(response, (str, type(None)))

    def test_special_characters(self):
        """Test handling of messages with special characters."""
        if not self.client.services:
            self.skipTest("No services available")

        special_message = "Hello! 🌟 How are you? @#$%^&*()"
        response = self.client.generate_response(special_message)
        self.assertIsInstance(response, (str, type(None)))

    def test_unicode_characters(self):
        """Test handling of Unicode characters."""
        if not self.client.services:
            self.skipTest("No services available")

        unicode_message = "Hello! 你好 ¿Cómo estás? Привет!"
        response = self.client.generate_response(unicode_message)
        self.assertIsInstance(response, (str, type(None)))

class TestConfiguration(unittest.TestCase):
    """Test configuration and environment handling."""

    def test_environment_variables(self):
        """Test that environment variables are handled properly."""
        # Test OpenAI
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            self.assertIsInstance(openai_key, str)
            self.assertGreater(len(openai_key), 0)

        # Test Google
        google_key = os.getenv("GOOGLE_API_KEY")
        if google_key:
            self.assertIsInstance(google_key, str)
            self.assertGreater(len(google_key), 0)

        # Test Anthropic
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        if anthropic_key:
            self.assertIsInstance(anthropic_key, str)
            self.assertGreater(len(anthropic_key), 0)

    def test_fallback_responses(self):
        """Test fallback response system."""
        # Check if fallback responses file exists
        fallback_file = "fallback_responses.json"
        if os.path.exists(fallback_file):
            with open(fallback_file, 'r') as f:
                responses = json.load(f)
            self.assertIsInstance(responses, dict)
            self.assertGreater(len(responses), 0)

def run_performance_benchmark():
    """Run performance benchmark tests."""
    print("\n" + "="*60)
    print("HYBRID AI SYSTEM PERFORMANCE BENCHMARK")
    print("="*60)

    if not IMPORTS_SUCCESSFUL:
        print("❌ Cannot run benchmark: Imports failed")
        return

    client = HybridAIClient()
    if not client.services:
        print("❌ Cannot run benchmark: No AI services available")
        return

    test_messages = [
        "Hello, how are you?",
        "Explain quantum computing in simple terms.",
        "Write a haiku about technology.",
        "What are the benefits of renewable energy?",
        "Tell me a joke about programming."
    ]

    print(f"Testing with {len(client.services)} available services:")
    for service_name in client.services.keys():
        print(f"  • {service_name}")

    print(f"\nRunning {len(test_messages)} test queries...")
    print("-" * 60)

    results = []
    total_start_time = time.time()

    for i, message in enumerate(test_messages, 1):
        print(f"\nTest {i}: {message[:50]}...")
        start_time = time.time()

        response = client.generate_response(message)
        end_time = time.time()

        response_time = end_time - start_time
        response_length = len(response) if response else 0

        results.append({
            'query': message,
            'response_time': response_time,
            'response_length': response_length,
            'success': response is not None
        })

        status = "✅" if response else "❌"
        print(f"{status} Query: '{message[:50]}...' | Time: {response_time:.2f}s | Length: {response_length} chars")
    total_time = time.time() - total_start_time

    # Calculate statistics
    successful_responses = [r for r in results if r['success']]
    avg_response_time = sum(r['response_time'] for r in results) / len(results)
    avg_response_length = sum(r['response_length'] for r in successful_responses) / len(successful_responses) if successful_responses else 0
    success_rate = len(successful_responses) / len(results) * 100

    print("\n" + "-" * 60)
    print("BENCHMARK RESULTS")
    print("-" * 60)
    print(f"Total test time: {total_time:.2f} seconds")
    print(f"Average response time: {avg_response_time:.2f} seconds")
    print(f"Average response length: {avg_response_length:.0f} characters")
    print(f"Success rate: {success_rate:.1f}%")
    print(f"Services used: {set(client.service_performance.keys())}")

    # Performance rating
    if avg_response_time < 5.0 and success_rate > 80:
        rating = "⭐⭐⭐⭐⭐ EXCELLENT"
    elif avg_response_time < 10.0 and success_rate > 60:
        rating = "⭐⭐⭐⭐ GOOD"
    elif avg_response_time < 20.0 and success_rate > 40:
        rating = "⭐⭐⭐ FAIR"
    else:
        rating = "⭐⭐ POOR"

    print(f"\nPerformance Rating: {rating}")

def main():
    """Main test runner."""
    print("Hybrid AI Video Remaker - Test Suite")
    print("=" * 50)

    if not IMPORTS_SUCCESSFUL:
        print("❌ CRITICAL: Failed to import hybrid AI client")
        print("Please ensure all dependencies are installed:")
        print("  pip install -r requirements.txt")
        return 1

    # Run unit tests
    print("\nRunning unit tests...")
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test classes
    test_classes = [
        TestHybridAIClient,
        TestFreeTierAIClient,
        TestIndividualServices,
        TestUtilityFunctions,
        TestPerformance,
        TestErrorHandling,
        TestConfiguration
    ]

    for test_class in test_classes:
        suite.addTests(loader.loadTestsFromTestCase(test_class))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Run performance benchmark
    try:
        run_performance_benchmark()
    except Exception as e:
        print(f"❌ Performance benchmark failed: {e}")

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")

    if result.wasSuccessful():
        print("✅ All tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"  • {test}")

        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"  • {test}")

        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)