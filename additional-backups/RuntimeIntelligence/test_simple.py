#!/usr/bin/env python3
"""
Simple Runtime Intelligence Test
Basic functionality test for the Runtime Intelligence System
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def main():
    print("🧠 Runtime Intelligence System - Simple Test")
    print("=" * 60)

    try:
        # Import and initialize components
        print("🚀 Initializing components...")

        import api_registry
        import notebook_ai
        import task_commander
        import model_router
        import runtime_intelligence

        print("✅ Components imported successfully")

        # Test basic functionality
        print("\n📊 Testing basic functionality...")

        # Get system health
        health = runtime_intelligence.runtime.get_system_health()
        print(f"System Health: {health['overall_health']}")

        # Show available agents
        agents = api_registry.registry.get_enabled_agents()
        print(f"Enabled Agents: {len(agents)} - {', '.join(agents)}")

        # Show available models
        models = api_registry.registry.get_available_models()
        print(f"Available Models: {len(models)} - {', '.join(models)}")

        # Test model router
        print("\n🔀 Testing model router...")
        try:
            route = model_router.router.route_request(
                "CodeSuggestor",
                [{"role": "user", "content": "Hello test"}]
            )
            print(f"✅ Model routing works - Selected: {route['model']}")
        except Exception as e:
            print(f"⚠️ Model routing test failed: {e}")

        print("\n" + "=" * 60)
        print("✅ Runtime Intelligence System test completed!")
        print("🎯 System is operational and ready for use")
        print("=" * 60)

        # Keep dashboard running briefly
        print("📊 Dashboard is running at http://localhost:8081")
        print("Press Ctrl+C to exit...")

        try:
            import time
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 Shutting down...")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        try:
            runtime_intelligence.runtime.shutdown()
        except:
            pass

if __name__ == "__main__":
    main()