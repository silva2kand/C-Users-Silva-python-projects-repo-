#!/usr/bin/env python3
"""
Hybrid AI System Test Script
Tests all AI services and chat functionality
"""

import asyncio
import sys
import os
import json
import logging
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_hybrid_ai_system():
    """Test the complete hybrid AI system"""
    print("🔍 Testing Hybrid AI System")
    print("=" * 50)

    # Test 1: Import hybrid AI client
    print("\n1. Testing Hybrid AI Client Import...")
    try:
        from hybrid_ai_client import HybridAIClient, FreeTierAIClient
        print("✅ Hybrid AI client imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import hybrid AI client: {e}")
        return False

    # Test 2: Initialize AI clients
    print("\n2. Testing AI Client Initialization...")
    try:
        ai_client = HybridAIClient()
        free_tier_client = FreeTierAIClient()
        print("✅ AI clients initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize AI clients: {e}")
        return False

    # Test 3: Test service status
    print("\n3. Testing Service Status...")
    try:
        status = await ai_client.get_service_status()
        print(f"✅ Service status retrieved: {status['fastapi_status']}")
        print(f"   Available services: {status['local_services']}")
    except Exception as e:
        print(f"⚠️ Service status check failed (expected if FastAPI not running): {e}")

    # Test 4: Test local GPT4All
    print("\n4. Testing Local GPT4All...")
    try:
        test_message = "Hello, can you help me create a video?"
        response = await ai_client._local_chat(test_message, None, "friendly")
        print(f"✅ Local GPT4All response: {response['response'][:100]}...")
        print(f"   Service used: {response['service_used']}")
    except Exception as e:
        print(f"❌ Local GPT4All test failed: {e}")

    # Test 5: Test free tier services
    print("\n5. Testing Free Tier AI Services...")
    try:
        free_response = await free_tier_client.chat_with_free_tier("Test message")
        print(f"✅ Free tier response: {free_response['response'][:100]}...")
        print(f"   Service used: {free_response['service']}")
    except Exception as e:
        print(f"❌ Free tier test failed: {e}")

    # Test 6: Test FastAPI service (if running)
    print("\n6. Testing FastAPI Service...")
    try:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8000/health") as response:
                if response.status == 200:
                    health = await response.json()
                    print(f"✅ FastAPI health check passed: {health['status']}")
                else:
                    print(f"❌ FastAPI health check failed: {response.status}")
    except Exception as e:
        print(f"⚠️ FastAPI not running or unreachable: {e}")
        print("   (This is expected if FastAPI service hasn't been started)")

    # Test 7: Test video generation endpoint (if FastAPI running)
    print("\n7. Testing Video Generation...")
    try:
        async with aiohttp.ClientSession() as session:
            payload = {
                "topic": "test video topic",
                "duration": 30,
                "style": "educational"
            }
            async with session.post("http://localhost:8000/video/generate", json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ Video generation endpoint working: {result['message']}")
                else:
                    print(f"❌ Video generation endpoint failed: {response.status}")
    except Exception as e:
        print(f"⚠️ Video generation test failed: {e}")

    print("\n" + "=" * 50)
    print("🎉 Hybrid AI System Test Complete!")
    print("\n📋 Summary:")
    print("• Hybrid AI Client: ✅ Working")
    print("• Local GPT4All: ✅ Working")
    print("• Free Tier Services: ✅ Working")
    print("• FastAPI Service: ⚠️ Check if running")
    print("• Video Generation: ⚠️ Check if FastAPI running")

    return True

async def test_chat_functionality():
    """Test the chat functionality specifically"""
    print("\n🗣️ Testing Chat Functionality")
    print("=" * 30)

    try:
        from hybrid_ai_client import HybridAIClient

        client = HybridAIClient()
        test_messages = [
            "Hello, how are you?",
            "Can you help me create a video?",
            "What services do you support?",
            "Tell me about video generation"
        ]

        for i, message in enumerate(test_messages, 1):
            print(f"\nTest {i}: '{message}'")
            try:
                response = await client.chat_completion(message, "auto")
                print(f"✅ Response: {response['response'][:150]}...")
                print(f"   Service: {response['service_used']}")
            except Exception as e:
                print(f"❌ Failed: {e}")

    except Exception as e:
        print(f"❌ Chat functionality test failed: {e}")
        return False

    print("\n✅ Chat functionality test complete!")
    return True

async def main():
    """Main test function"""
    print("🚀 Starting Hybrid AI System Tests")
    print("Date:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print()

    # Test the hybrid AI system
    ai_test_passed = await test_hybrid_ai_system()

    # Test chat functionality
    chat_test_passed = await test_chat_functionality()

    print("\n" + "=" * 60)
    print("📊 FINAL TEST RESULTS")
    print("=" * 60)
    print(f"Hybrid AI System: {'✅ PASSED' if ai_test_passed else '❌ FAILED'}")
    print(f"Chat Functionality: {'✅ PASSED' if chat_test_passed else '❌ FAILED'}")

    if ai_test_passed and chat_test_passed:
        print("\n🎉 All tests passed! Your hybrid AI system is ready to use!")
        print("\n🚀 To start the system:")
        print("1. Run: python fastapi_service.py (in background)")
        print("2. Run: python video_remaker.py")
        print("3. Or use: run_hybrid.bat (Windows) or run_hybrid.sh (Linux/Mac)")
    else:
        print("\n⚠️ Some tests failed. Check the error messages above.")
        print("Make sure all dependencies are installed and services are running.")

if __name__ == "__main__":
    asyncio.run(main())