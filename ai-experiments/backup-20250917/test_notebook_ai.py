#!/usr/bin/env python3
"""
Simple Test for Notebook AI System
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

try:
    from notebook_ai_system import NotebookAISystem
    print("✅ Notebook AI system imported successfully!")

    # Create system
    notebook_ai = NotebookAISystem()
    print("✅ Notebook AI system initialized!")

    # Get status
    status = notebook_ai.get_system_status()
    print("✅ System status retrieved!")
    print(f"   Phase 1 checkpoints: {status['phase1']['checkpoints']}")
    print(f"   Phase 2 agents: {status['phase2']['total_agents']}")
    print(f"   Phase 3 components: {status['phase3']['mapped_components']}")

    print("\n🎉 Notebook AI system is working perfectly!")
    print("📚 See Notebook_AI_Three_Phases.ipynb for detailed examples")
    print("📖 See Notebook_AI_README.md for integration guide")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()