#!/usr/bin/env python3
"""SpecKit Demo - Demonstration of SpecKit Testing Framework

This script demonstrates the key features of SpecKit:
- Basic testing with enhanced assertions
- Mock data generation
- Performance benchmarking
- GUI testing capabilities (when PyQt5 is available)
"""

import sys
import os

# Add current directory to path for importing speckit
sys.path.insert(0, '.')

from speckit import (
    BaseTest, 
    MockFactory, 
    benchmark, 
    performance_context,
    PerformanceMonitor,
    setup_project
)

def demo_mock_factory():
    """Demonstrate MockFactory capabilities"""
    print("\n🎭 MockFactory Demo")
    print("=" * 50)
    
    # Generate mock user data
    user = MockFactory.mock_user()
    print(f"Mock User: {user['username']} ({user['email']})")
    
    # Generate mock chat message
    message = MockFactory.mock_chat_message()
    print(f"Mock Message: '{message['content'][:50]}...'")
    
    # Generate mock AI response
    ai_response = MockFactory.mock_ai_response()
    print(f"Mock AI Response: '{ai_response['response'][:50]}...'")
    print(f"Confidence: {ai_response['confidence']}, Model: {ai_response['model']}")

@benchmark(iterations=1000, warmup=100)
def sample_function():
    """Sample function for performance testing"""
    return sum(range(100))

def demo_performance_testing():
    """Demonstrate performance testing capabilities"""
    print("\n⚡ Performance Testing Demo")
    print("=" * 50)
    
    # Run benchmarked function
    result = sample_function()
    
    # Get benchmark results
    if hasattr(sample_function, 'benchmark_result'):
        bench_result = sample_function.benchmark_result
        print(f"Function: {bench_result['function']}")
        print(f"Iterations: {bench_result['iterations']}")
        print(f"Average Time: {bench_result['average_time']:.6f}s")
        print(f"Min Time: {bench_result['min_time']:.6f}s")
        print(f"Max Time: {bench_result['max_time']:.6f}s")
        print(f"Memory Used: {bench_result['memory_used_mb']:.2f} MB")
    
    # Demonstrate performance context
    print("\nUsing performance_context:")
    with performance_context("demo_operation"):
        # Simulate some work
        data = [i**2 for i in range(10000)]
        result = sum(data)

def demo_performance_monitor():
    """Demonstrate continuous performance monitoring"""
    print("\n📊 Performance Monitor Demo")
    print("=" * 50)
    
    monitor = PerformanceMonitor()
    monitor.start_monitoring(interval=0.1)
    
    # Simulate some work
    import time
    for i in range(5):
        # Simulate CPU work
        _ = [j**2 for j in range(1000)]
        time.sleep(0.2)
    
    monitor.stop_monitoring()
    
    # Get results
    metrics = monitor.get_average_metrics()
    if metrics:
        print(f"Average Memory Usage: {metrics['average_memory_mb']:.2f} MB")
        print(f"Average CPU Usage: {metrics['average_cpu_percent']:.2f}%")
        print(f"Peak Memory: {metrics['peak_memory_mb']:.2f} MB")
        print(f"Samples Collected: {metrics['sample_count']}")

class DemoTestCase(BaseTest):
    """Demonstration test case using SpecKit"""
    
    def setUp(self):
        super().setUp()
        self.test_data = MockFactory.mock_user()
    
    def test_enhanced_assertions(self):
        """Demonstrate enhanced assertion methods"""
        # Test data structure
        self.assertIsNotNone(self.test_data)
        self.assertIn('username', self.test_data)
        self.assertIn('email', self.test_data)
        
        # Test email format
        email = self.test_data['email']
        self.assertIn('@', email)
        self.assertTrue(email.endswith(('.com', '.org', '.net')))
    
    def test_mock_data_consistency(self):
        """Test that mock data is consistent and valid"""
        # Generate multiple users
        users = [MockFactory.mock_user() for _ in range(5)]
        
        # Check that all users have required fields
        for user in users:
            self.assertIn('id', user)
            self.assertIn('username', user)
            self.assertIn('email', user)
            self.assertIsInstance(user['id'], int)
            self.assertIsInstance(user['username'], str)
            self.assertIsInstance(user['email'], str)
    
    @benchmark(iterations=50)
    def test_performance_benchmark(self):
        """Demonstrate performance benchmarking in tests"""
        # Simulate some processing
        data = MockFactory.mock_chat_message()
        processed = data['content'].upper().replace(' ', '_')
        self.assertIsInstance(processed, str)

def run_demo_tests():
    """Run the demonstration tests"""
    print("\n🧪 Running Demo Tests")
    print("=" * 50)
    
    import unittest
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(DemoTestCase)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

def main():
    """Main demonstration function"""
    print("🚀 SpecKit Testing Framework Demo")
    print("=" * 60)
    print("This demo showcases the key features of SpecKit:")
    print("- Mock data generation")
    print("- Performance benchmarking")
    print("- Enhanced testing capabilities")
    print("- Continuous performance monitoring")
    
    try:
        # Run demonstrations
        demo_mock_factory()
        demo_performance_testing()
        demo_performance_monitor()
        
        # Run actual tests
        success = run_demo_tests()
        
        print("\n" + "=" * 60)
        if success:
            print("✅ All demos completed successfully!")
            print("\n🎯 SpecKit is ready for use in your projects.")
            print("\nTo get started:")
            print("1. Import SpecKit: from speckit import BaseTest, MockFactory, benchmark")
            print("2. Create test classes inheriting from BaseTest")
            print("3. Use @benchmark decorator for performance tests")
            print("4. Use MockFactory for generating test data")
            print("5. Run tests with: python -m pytest")
        else:
            print("❌ Some demos failed. Check the output above.")
            
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()