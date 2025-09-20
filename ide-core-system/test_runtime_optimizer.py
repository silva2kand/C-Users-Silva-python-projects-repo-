#!/usr/bin/env python3
"""
Test script for RuntimeOptimizerAgent - Phase 5 of Notebook AI System
Tests free AI API integration and intelligent routing capabilities
"""

import os
import sys
import time
from datetime import datetime

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from notebook_ai_system import RuntimeOptimizerAgent, create_notebook_ai_system

def test_api_configuration():
    """Test API endpoint configuration"""
    print("🧪 Testing API Configuration...")
    print("=" * 50)

    optimizer = RuntimeOptimizerAgent()

    # Test endpoint configuration
    endpoints = optimizer.api_endpoints
    print(f"✅ Configured {len(endpoints)} API endpoints:")

    for name, endpoint in endpoints.items():
        has_key = name in optimizer.api_keys
        status = "✅ Configured" if has_key else "⚠️  Missing Key"
        print(f"  • {endpoint.name}: {status}")
        print(f"    URL: {endpoint.url}")
        print(f"    Model: {endpoint.model_name}")
        print(f"    Rate Limit: {endpoint.rate_limit}/min")
        print(f"    Tasks: {', '.join(endpoint.supported_tasks)}")
        print()

    return optimizer

def test_performance_monitoring(optimizer):
    """Test performance monitoring capabilities"""
    print("📊 Testing Performance Monitoring...")
    print("=" * 50)

    # Start monitoring
    optimizer.start_performance_monitoring()
    print("✅ Performance monitoring started")

    # Let it collect some data
    print("⏳ Collecting performance data...")
    time.sleep(2)

    # Get performance report
    report = optimizer.get_performance_report()

    if 'error' not in report:
        print("✅ Performance Report Generated:")
        print(f"  • CPU Usage: {report['current_metrics']['cpu_usage']:.1f}%")
        print(f"  • Memory Usage: {report['current_metrics']['memory_usage']:.1f}%")
        print(f"  • Network Latency: {report['current_metrics']['network_latency']:.3f}s")
        print(f"  • Active Threads: {report['current_metrics']['active_threads']}")
        print(f"  • Available APIs: {len(report['available_endpoints'])}")
        print(f"  • Configured Keys: {len(report['configured_keys'])}")
    else:
        print(f"⚠️ Performance Report Error: {report['error']}")

    # Stop monitoring
    optimizer.stop_performance_monitoring()
    print("✅ Performance monitoring stopped")

def test_api_routing(optimizer):
    """Test intelligent API routing"""
    print("\n🧠 Testing AI API Routing...")
    print("=" * 50)

    test_cases = [
        ("text_generation", "Write a Python function to reverse a string"),
        ("code_completion", "def calculate_fibonacci(n):"),
        ("analysis", "Analyze the complexity of this algorithm"),
        ("conversation", "Hello, how can you help me with coding?")
    ]

    for task_type, content in test_cases:
        print(f"\n🔄 Testing {task_type}...")
        result = optimizer.route_api_request(task_type, content)

        if 'error' not in result:
            print("✅ Request routed successfully:"            print(f"  • Endpoint: {result.get('endpoint', 'Unknown')}")
            print(f"  • Response Time: {result.get('response_time', 0):.2f}s")
            print(f"  • Success: {result.get('success', False)}")
            if 'generated_text' in result:
                preview = result['generated_text'][:100] + "..." if len(result['generated_text']) > 100 else result['generated_text']
                print(f"  • Response: {preview}")
        else:
            print(f"⚠️ Routing failed: {result['error']}")

def test_system_optimization(optimizer):
    """Test system optimization features"""
    print("\n🔧 Testing System Optimization...")
    print("=" * 50)

    # Perform system optimization
    optimization_result = optimizer.optimize_system_configuration()

    print("✅ System Optimization Results:")
    print(f"  • Optimizations Applied: {optimization_result['optimizations_applied']}")
    print(f"  • System Health: {optimization_result['system_health']}")

    if optimization_result['recommendations']:
        print("  • Recommendations:")
        for rec in optimization_result['recommendations']:
            print(f"    - {rec}")
    else:
        print("  • No recommendations needed")

def test_integrated_system():
    """Test the complete integrated system"""
    print("\n🎯 Testing Complete Integrated System...")
    print("=" * 50)

    # Create full system
    system = create_notebook_ai_system()
    print("✅ Full Notebook AI System created")

    # Start all phases
    system.start_background_research()
    system.start_runtime_optimization()
    print("✅ All phases started")

    # Test integrated functionality
    status = system.get_system_status()
    print("✅ System Status:"    print(f"  • Phase 1 (Foundation): {status['phase1']['checkpoints']} checkpoints")
    print(f"  • Phase 2 (Runtime Intel): {status['phase2']['total_agents']} agents")
    print(f"  • Phase 3 (Autonomous Mapping): {status['phase3']['mapped_components']} components")
    print(f"  • Phase 4 (Background Research): {status['phase4']['background_monitoring']} monitoring")
    print(f"  • Phase 5 (Runtime Optimization): {status['phase5']['performance_monitoring']} monitoring")

    # Test AI routing through integrated system
    ai_result = system.route_ai_request("text_generation", "Explain what machine learning is")
    if 'error' not in ai_result:
        print("✅ Integrated AI routing successful")
    else:
        print(f"⚠️ Integrated AI routing: {ai_result.get('error', 'Failed')}")

    # Get performance report
    perf_report = system.get_performance_report()
    print(f"✅ Performance metrics collected: {len(perf_report.get('current_metrics', {}))} metrics")

    # Stop all phases
    system.stop_background_research()
    system.stop_runtime_optimization()
    print("✅ All phases stopped")

def main():
    """Main test function"""
    print("🚀 RuntimeOptimizerAgent Test Suite")
    print("=" * 60)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    try:
        # Test individual components
        optimizer = test_api_configuration()
        test_performance_monitoring(optimizer)
        test_api_routing(optimizer)
        test_system_optimization(optimizer)

        # Test integrated system
        test_integrated_system()

        print("\n🎉 All tests completed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        print(f"\nTest completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()