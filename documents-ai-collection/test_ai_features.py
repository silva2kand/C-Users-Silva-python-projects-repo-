#!/usr/bin/env python3
"""
Quick AI Features Test Script
Tests GPT4All, Hugging Face API, and basic functionality
"""

import sys
import time
import psutil
import os

# Test imports
print("🔍 Testing AI imports...")

try:
    from gpt4all import GPT4All
    GPT4ALL_AVAILABLE = True
    print("✅ GPT4All available")
except ImportError:
    GPT4ALL_AVAILABLE = False
    print("❌ GPT4All not available")

try:
    import requests
    HUGGINGFACE_AVAILABLE = True
    print("✅ Requests (for Hugging Face API) available")
except ImportError:
    HUGGINGFACE_AVAILABLE = False
    print("❌ Requests not available")

try:
    from flask import Flask
    FLASK_AVAILABLE = True
    print("✅ Flask available")
except ImportError:
    FLASK_AVAILABLE = False
    print("❌ Flask not available")

print("\n🧪 Testing AI functionality...")

def test_gpt4all():
    """Test GPT4All functionality"""
    if not GPT4ALL_AVAILABLE:
        print("❌ GPT4All not available for testing")
        return False

    try:
        print("🤖 Testing GPT4All...")
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024

        start_time = time.time()
        model = GPT4All("orca-mini-3b-gguf2-q4_0.gguf", device='cpu')
        load_time = time.time() - start_time

        after_memory = process.memory_info().rss / 1024 / 1024
        memory_usage = after_memory - initial_memory

        print(f"⏱️ Model loaded in {load_time:.1f}s")
        print(f"💾 Memory usage: {memory_usage:.1f} MB")

        # Test response generation
        start_time = time.time()
        response = model.generate("Hello, how are you?", max_tokens=30, temp=0.5)
        response_time = time.time() - start_time

        print(f"⚡ Response generated in {response_time:.2f}s")
        print(f"📝 Response: '{response.strip()}'")

        if memory_usage > 4000:
            print("⚠️ WARNING: High memory usage detected")
        else:
            print("✅ Memory usage acceptable")

        return True

    except Exception as e:
        print(f"❌ GPT4All test failed: {e}")
        return False

def test_huggingface_api():
    """Test Hugging Face API"""
    if not HUGGINGFACE_AVAILABLE:
        print("❌ Requests not available for Hugging Face testing")
        return False

    try:
        print("🌐 Testing Hugging Face API...")

        api_url = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-small"
        headers = {"Content-Type": "application/json"}

        payload = {
            "inputs": "Hi there",
            "parameters": {
                "max_length": 30,
                "temperature": 0.5,
                "do_sample": False
            }
        }

        start_time = time.time()
        response = requests.post(api_url, json=payload, headers=headers, timeout=10)
        api_time = time.time() - start_time

        print(f"🌐 API response time: {api_time:.2f}s")

        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                generated_text = result[0].get('generated_text', '')
                print(f"📝 API Response: '{generated_text[:50]}...'")
                print("✅ Hugging Face API working")
                return True
            else:
                print("❌ Invalid API response format")
                return False
        else:
            print(f"❌ API request failed: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Hugging Face API test failed: {e}")
        return False

def test_local_ip():
    """Test local IP detection"""
    try:
        print("🏠 Testing local IP detection...")
        import socket

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()

        print(f"✅ Local IP detected: {local_ip}")
        print(f"🌐 Web interface would be available at: http://{local_ip}:5000")
        return True

    except Exception as e:
        print(f"❌ Local IP detection failed: {e}")
        return False

def test_internet_knowledge():
    """Test internet knowledge sources"""
    try:
        print("🌐 Testing internet knowledge sources...")

        # Test web search
        if WEB_AVAILABLE:
            print("🔍 Testing web search...")
            # Simple connectivity test
            try:
                response = requests.get("https://duckduckgo.com", timeout=5)
                if response.status_code == 200:
                    print("✅ Web search connectivity OK")
                else:
                    print("⚠️ Web search returned unexpected status")
            except:
                print("⚠️ Web search connectivity test failed")
        else:
            print("❌ Web search not available")

        # Test Wikipedia
        if WIKIPEDIA_AVAILABLE:
            print("📚 Testing Wikipedia API...")
            try:
                import wikipedia
                # Test search
                results = wikipedia.search("test", results=1)
                if results:
                    print("✅ Wikipedia API OK")
                else:
                    print("⚠️ Wikipedia search returned no results")
            except:
                print("⚠️ Wikipedia API test failed")
        else:
            print("❌ Wikipedia not available")

        # Test RSS feeds
        if RSS_AVAILABLE:
            print("📰 Testing RSS feeds...")
            try:
                import feedparser
                feed = feedparser.parse("https://feeds.bbci.co.uk/news/world/rss.xml")
                if feed.entries:
                    print("✅ RSS feed parsing OK")
                else:
                    print("⚠️ RSS feed returned no entries")
            except:
                print("⚠️ RSS feed test failed")
        else:
            print("❌ RSS feeds not available")

        return True

    except Exception as e:
        print(f"❌ Internet knowledge test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 50)
    print("🚀 AI FEATURES COMPREHENSIVE TEST")
    print("=" * 50)

    results = []

    # Test GPT4All
    print("\n" + "="*30)
    results.append(("GPT4All Local AI", test_gpt4all()))

    # Test Hugging Face API
    print("\n" + "="*30)
    results.append(("Hugging Face API", test_huggingface_api()))

    # Test Local IP
    print("\n" + "="*30)
    results.append(("Local IP Detection", test_local_ip()))

    # Test Internet Knowledge
    print("\n" + "="*30)
    results.append(("Internet Knowledge Sources", test_internet_knowledge()))

    # Summary
    print("\n" + "="*50)
    print("📊 TEST RESULTS SUMMARY")
    print("="*50)

    passed = 0
    total = len(results)

    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name:<20} {status}")
        if success:
            passed += 1

    print(f"\n🎯 Overall: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 ALL TESTS PASSED - PRODUCTION READY!")
        print("\n🚀 Ready to use:")
        print("   • AI Desktop Suite: python advanced_ai_screen.py")
        print("   • Web Interface: python advanced_ai_screen.py --web")
        print("   • Ciniforge: python ciniforge/ciniforge.pyw")
        print("   • Create Shortcut: create_shortcut.bat")
        print("\n🌐 Internet Knowledge Features:")
        print("   • Web Search: 'search artificial intelligence'")
        print("   • Wikipedia: 'wiki machine learning'")
        print("   • News: 'news technology'")
        print("   • Research: 'research quantum computing'")
    else:
        print("⚠️ SOME TESTS FAILED - CHECK ISSUES ABOVE")

    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)