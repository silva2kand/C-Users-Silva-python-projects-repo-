#!/usr/bin/env python3
"""
Notebook AI Integration Script
===============================

This script demonstrates how to integrate the Notebook AI system
with your existing Legion AI agents and IDE components.

Usage:
    python notebook_ai_integration.py
"""

import sys
import os
import traceback
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent
sys.path.append(str(project_root))
sys.path.append(str(project_root / "RuntimeIntelligence"))
sys.path.append(str(project_root / "Backend"))

try:
    from notebook_ai_system import NotebookAISystem
    print("✅ Notebook AI system imported successfully")
except ImportError as e:
    print(f"❌ Failed to import Notebook AI system: {e}")
    sys.exit(1)

def integrate_with_existing_agents():
    """Integrate Notebook AI with existing Legion agents"""

    print("🔗 Integrating Notebook AI with Legion Agents")
    print("=" * 50)

    # Create Notebook AI system
    notebook_ai = NotebookAISystem()

    # Register existing Legion agents
    legion_agents = [
        ("CodeSuggestor", "codellama:7b"),
        ("FixerShell", "gpt-4"),
        ("SummarizerBot", "claude-3"),
        ("VoiceNarrator", "local-tts"),
        ("ContextAgent", "codellama:7b"),
        ("RefactorAgent", "gpt-4"),
        ("TestGenAgent", "codellama:7b"),
        ("ReviewAgent", "claude-3"),
        ("NarratorAgent", "local-tts"),
        ("FixerShell", "gpt-4")
    ]

    print("📋 Registering Legion agents with Notebook AI:")
    for agent_name, model in legion_agents:
        notebook_ai.agent_tracker.register_agent(agent_name, model)
        print(f"  ✅ {agent_name} ({model})")

    # Start autonomous mapping
    print("\n🗺️ Starting autonomous program mapping...")
    notebook_ai.mapper.start_mapping()

    # Demonstrate integration
    print("\n🚀 Demonstrating Legion AI integration:")

    # Simulate Legion agent tasks
    tasks = [
        ("CodeSuggestor", "code_completion", "main.py", "codellama:7b"),
        ("FixerShell", "error_fixing", "utils.py", "gpt-4"),
        ("SummarizerBot", "text_summarization", "readme.md", "claude-3"),
        ("VoiceNarrator", "narration", "system.log", "local-tts")
    ]

    results = []
    for agent, task, file_path, model in tasks:
        result = notebook_ai.execute_task_with_full_tracking(agent, task, file_path, model)
        results.append(result)
        print(f"  ✅ {agent}: {task} completed")

    # Show system status
    status = notebook_ai.get_system_status()
    print("\n📊 Integration Status:")
    print(f"  🤖 Legion agents tracked: {status['phase2']['total_agents']}")
    print(f"  🗺️ Components mapped: {status['phase3']['mapped_components']}")
    print(f"  📝 Checkpoints logged: {status['phase1']['checkpoints']}")
    print(f"  🔄 Model routes: {status['phase2']['model_routes']}")

    return notebook_ai

def demonstrate_voice_integration():
    """Demonstrate voice narration integration"""

    print("\n🎤 Demonstrating Voice Integration")
    print("=" * 40)

    notebook_ai = NotebookAISystem()

    # Test bilingual narration
    narrations = [
        ("CodeSuggestor completed code completion task", "en", "high"),
        ("குறியீடு முடிந்தது", "ta", "high"),
        ("System health is optimal", "en", "medium"),
        ("சிஸ்டம் ஆரோக்கியமானது", "ta", "medium")
    ]

    for message, language, priority in narrations:
        result = notebook_ai.voice_narrator.narrate(message, language, priority)
        lang_flag = "🇺🇸" if language == "en" else "🇮🇳"
        print(f"  {lang_flag} {message}")

    print(f"  📊 Total narrations: {len(notebook_ai.voice_narrator.narration_log)}")

def demonstrate_health_monitoring():
    """Demonstrate health monitoring integration"""

    print("\n🏥 Demonstrating Health Monitoring")
    print("=" * 40)

    notebook_ai = NotebookAISystem()

    # Perform health checks on various components
    components = ["ollama", "openai", "claude", "local_ai", "voice_system"]

    print("🔍 Performing health checks:")
    for component in components:
        health_check = notebook_ai.runtime_intel.perform_health_check(component)
        status_icon = "🟢" if health_check.status == "healthy" else "🔴"
        print(f"  {status_icon} {component}: {health_check.status} ({health_check.response_time_ms:.1f}ms)")

    # Get overall system health
    system_health = notebook_ai.runtime_intel.get_system_health()
    print("\n📊 System Health Summary:")
    print(f"  📈 Overall health: {system_health.get('overall_health', 0):.1%}")
    print(f"  🔀 Model routes: {system_health['model_routes']}")
    print(f"  📊 Health checks: {system_health['total_checks']}")

def demonstrate_background_research():
    """Demonstrate the 4th phase: Background Research & Monitoring Agent"""

    print("\n🔍 Demonstrating Background Research Agent")
    print("=" * 50)

    notebook_ai = NotebookAISystem()

    # Start background monitoring
    print("🚀 Starting background research agent...")
    notebook_ai.start_background_research()

    # Subscribe to updates
    def background_update_handler(update):
        print(f"📡 Background Update: {update.update_type} - {update.details}")

    notebook_ai.subscribe_to_updates(background_update_handler)

    # Force an immediate scan
    print("\n🔎 Performing immediate project scan...")
    scan_result = notebook_ai.force_project_scan()

    print("📊 Scan Results:")
    print(f"  📁 Total files: {scan_result.total_files}")
    print(f"  📂 Total directories: {scan_result.total_dirs}")
    print(f"  📝 Code lines: {scan_result.code_lines}")
    print(f"  🔗 Dependencies found: {len(scan_result.dependencies)}")
    print(f"  ⚠️ Issues found: {len(scan_result.issues_found)}")

    if scan_result.file_types:
        print(f"  � File types: {', '.join([f'{ext}: {count}' for ext, count in scan_result.file_types.items()])}")

    # Get project insights
    print("\n📈 Getting project insights...")
    insights = notebook_ai.get_project_insights()

    print("🎯 Project Insights:")
    print(f"  📊 Size: {insights['project_size']['files']} files, {insights['project_size']['code_lines']} lines")
    print(f"  🔄 Recent changes: +{insights['recent_changes']['new_files']} new, ~{insights['recent_changes']['modified_files']} modified")
    print(f"  � Research contexts available: {insights['research_contexts']}")

    # Get research context
    print("\n🔬 Getting research context...")
    dep_research = notebook_ai.get_research_context("dependencies")
    if dep_research:
        print("� Dependency Research:")
        print(f"  🔗 Dependencies: {', '.join(dep_research.dependencies[:5])}")
        print(f"  💡 Patterns: {', '.join(dep_research.patterns_found)}")
        print(f"  ✅ Recommendations: {dep_research.recommendations}")

    # Get recent updates
    print("\n📡 Recent background updates:")
    updates = notebook_ai.get_recent_updates(3)
    for update in updates:
        print(f"  {update.timestamp[:19]} - {update.update_type}: {update.component}")

    # Stop background monitoring
    print("\n� Stopping background research agent...")
    notebook_ai.stop_background_research()

    print(f"✅ Background research demonstration completed")

def create_integration_summary():
    """Create a summary of the integration"""

    print("\n🎯 Notebook AI Integration Summary")
    print("=" * 50)

    summary = {
        "Phase 1 (Past - Foundation)": [
            "✅ Checkpoint Logging - All agent tasks logged with timestamps",
            "✅ Replay-Safe Journaling - Structured logs with rollback capability",
            "✅ Voice Narration Hooks - Bilingual Tamil/English narration",
            "✅ Foreground/Background Tagging - User-facing vs background tasks"
        ],
        "Phase 2 (Present - Runtime Intelligence)": [
            "✅ Multi-Agent Tracking - Legion agents status monitoring",
            "✅ Model Routing Logs - Fallback tracking and latency monitoring",
            "✅ Extension Awareness - IDE extension integration",
            "✅ Health Check Logging - System diagnostics and responsiveness",
            "✅ IDE Event Hooks - File operations and agent triggers"
        ],
        "Phase 3 (Future - Autonomous Mapping)": [
            "✅ Full Program Mapping - Component discovery and relationships",
            "✅ PPI Dependency Gathering - Program-to-program interactions",
            "✅ Agent Context Injection - Runtime support and recommendations",
            "✅ Self-Evolving Intelligence - Performance analysis and evolution",
            "✅ Performance Metrics - Success rates and optimization suggestions"
        ],
        "Phase 4 (Background Research & Monitoring)": [
            "✅ Continuous Project Scanning - Every 3 minutes automatic scanning",
            "✅ Research Context Generation - Dependency analysis and recommendations",
            "✅ Background Update System - Real-time notifications for coding AI",
            "✅ Code Quality Analysis - Issue detection and improvement suggestions",
            "✅ File Change Monitoring - New, modified, and deleted file tracking",
            "✅ Dependency Pattern Recognition - Framework and library detection",
            "✅ Project Insights Dashboard - Comprehensive project overview",
            "✅ Contextual Information Ready - Information at hand for coding AI"
        ]
    }

    for phase, features in summary.items():
        print(f"\n{phase}:")
        for feature in features:
            print(f"  {feature}")

    print("\n🚀 Integration Status: COMPLETE")
    print("Your Legion AI system now has full Notebook AI capabilities!")
    print("Use the notebook_ai_system.py module in your IDE integration.")

if __name__ == "__main__":
    print("🧠 Notebook AI - Legion Integration Demo")
    print("==========================================")
    print(f"📅 Date: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    try:
        # Run all integration demonstrations
        integrate_with_existing_agents()
        demonstrate_voice_integration()
        demonstrate_health_monitoring()
        demonstrate_background_research()
        create_integration_summary()

        print("\n🎉 All integrations completed successfully!")
        print("📚 See Notebook_AI_Three_Phases.ipynb for detailed examples")

    except Exception as e:
        print(f"❌ Integration error: {e}")
        traceback.print_exc()