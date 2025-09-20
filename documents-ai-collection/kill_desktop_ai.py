#!/usr/bin/env python3
"""
Script to kill any running Desktop AI Assistant processes
Run this if the application is stuck running in the background
"""

import psutil
import os
import sys

def kill_existing_instances():
    """Kill any existing Desktop AI Assistant instances"""
    current_pid = os.getpid()
    killed_count = 0

    print("🔍 Searching for running Desktop AI Assistant processes...")

    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['pid'] != current_pid and proc.info['name'] and 'python' in proc.info['name'].lower():
                cmdline = proc.info['cmdline']
                if cmdline and len(cmdline) > 1 and 'desktop_ai_assistant.py' in cmdline[-1]:
                    print(f"🛑 Found running instance (PID: {proc.info['pid']})")
                    try:
                        proc.terminate()
                        proc.wait(timeout=3)
                        print(f"✅ Successfully terminated PID: {proc.info['pid']}")
                        killed_count += 1
                    except psutil.TimeoutExpired:
                        print(f"⚠️ Force killing PID: {proc.info['pid']}")
                        proc.kill()
                        killed_count += 1
                    except Exception as e:
                        print(f"❌ Error terminating PID {proc.info['pid']}: {e}")
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    if killed_count == 0:
        print("✅ No running instances found")
    else:
        print(f"✅ Terminated {killed_count} instance(s)")

    return killed_count

if __name__ == "__main__":
    print("🛑 Desktop AI Assistant Process Killer")
    print("=" * 40)

    killed = kill_existing_instances()

    print("\n💡 Tips to prevent multiple instances:")
    print("• Always close the application properly using the X button")
    print("• Choose 'Close' when prompted to quit the application")
    print("• The application now prevents multiple instances automatically")

    if killed > 0:
        print("\n🎯 You can now start the Desktop AI Assistant normally")
    else:
        print("\n✅ No cleanup needed - application should start normally")