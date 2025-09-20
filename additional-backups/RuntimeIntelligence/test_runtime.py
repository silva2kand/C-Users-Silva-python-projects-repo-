#!/usr/bin/env python3
"""Quick test of Runtime Intelligence System"""

from runtime_intelligence import runtime

def test_runtime_system():
    """Test the Runtime Intelligence system"""
    print("🧪 Testing Runtime Intelligence System...")

    # Test submitting a task
    task_data = {
        'task_type': 'review',
        'content': 'print("Hello World")',
        'language': 'python'
    }

    try:
        task_id = runtime.submit_agent_task('CodeSuggestor', task_data)
        print(f"✅ Task submitted successfully: {task_id}")
        return True
    except Exception as e:
        print(f"❌ Task submission failed: {e}")
        return False

if __name__ == "__main__":
    test_runtime_system()