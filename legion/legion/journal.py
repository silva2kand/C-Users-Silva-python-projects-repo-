"""
Journal System - Centralized logging and audit trail for Legion
"""
import json
import threading
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from collections import defaultdict


class Journal:
    """
    Centralized journaling system for Legion.
    Provides audit trails, rollback capabilities, and real-time monitoring.
    """

    def __init__(self, journal_file: Path):
        self.journal_file = journal_file
        self.journal_file.parent.mkdir(parents=True, exist_ok=True)
        self.lock = threading.Lock()
        self.entries: List[Dict[str, Any]] = []
        self._load_journal()

    def _load_journal(self):
        """Load existing journal entries from file"""
        if self.journal_file.exists():
            try:
                with open(self.journal_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            entry = json.loads(line.strip())
                            self.entries.append(entry)
            except (json.JSONDecodeError, FileNotFoundError) as e:
                print(f"Warning: Could not load journal file: {e}")
                self.entries = []

    def log(self, event_type: str, data: Dict[str, Any], agent_name: Optional[str] = None):
        """
        Log an event to the journal.

        Args:
            event_type: Type of event (e.g., 'task_request', 'agent_result', 'system')
            data: Event data payload
            agent_name: Optional name of the agent that generated the event
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "agent_name": agent_name,
            "data": data,
            "entry_id": f"{event_type}_{int(datetime.now().timestamp() * 1000)}"
        }

        with self.lock:
            self.entries.append(entry)

            # Write to file immediately for persistence
            try:
                with open(self.journal_file, 'a', encoding='utf-8') as f:
                    json.dump(entry, f, ensure_ascii=False)
                    f.write('\n')
            except Exception as e:
                print(f"Warning: Could not write to journal: {e}")

    def get_entries(self, event_type: Optional[str] = None,
                   agent_name: Optional[str] = None,
                   limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get journal entries with optional filtering.

        Args:
            event_type: Filter by event type
            agent_name: Filter by agent name
            limit: Maximum number of entries to return

        Returns:
            List of matching journal entries
        """
        with self.lock:
            filtered_entries = self.entries.copy()

            if event_type:
                filtered_entries = [e for e in filtered_entries if e["event_type"] == event_type]

            if agent_name:
                filtered_entries = [e for e in filtered_entries if e.get("agent_name") == agent_name]

            return filtered_entries[-limit:]

    def get_entry_count(self) -> int:
        """Get total number of journal entries"""
        with self.lock:
            return len(self.entries)

    def get_last_entry_time(self) -> Optional[str]:
        """Get timestamp of the last journal entry"""
        with self.lock:
            if self.entries:
                return self.entries[-1]["timestamp"]
            return None

    def get_agent_activity(self, agent_name: str) -> Dict[str, Any]:
        """Get activity statistics for a specific agent"""
        with self.lock:
            agent_entries = [e for e in self.entries if e.get("agent_name") == agent_name]

            if not agent_entries:
                return {"agent": agent_name, "total_entries": 0}

            event_types = defaultdict(int)
            for entry in agent_entries:
                event_types[entry["event_type"]] += 1

            return {
                "agent": agent_name,
                "total_entries": len(agent_entries),
                "first_activity": agent_entries[0]["timestamp"],
                "last_activity": agent_entries[-1]["timestamp"],
                "event_breakdown": dict(event_types)
            }

    def get_task_history(self, task_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get history of task-related events"""
        with self.lock:
            task_entries = []

            for entry in self.entries:
                if entry["event_type"] in ["task_request", "task_complete", "task_error"]:
                    if task_id is None or entry.get("data", {}).get("task_id") == task_id:
                        task_entries.append(entry)

            return task_entries

    def get_system_health(self) -> Dict[str, Any]:
        """Get system health metrics from journal"""
        with self.lock:
            recent_entries = self.entries[-100:]  # Last 100 entries

            error_count = sum(1 for e in recent_entries if e["event_type"] == "task_error")
            success_count = sum(1 for e in recent_entries if e["event_type"] == "task_complete")

            agent_activity = defaultdict(int)
            for entry in recent_entries:
                if entry.get("agent_name"):
                    agent_activity[entry["agent_name"]] += 1

            return {
                "total_entries": len(self.entries),
                "recent_errors": error_count,
                "recent_successes": success_count,
                "active_agents": len(agent_activity),
                "agent_activity": dict(agent_activity),
                "last_update": self.get_last_entry_time()
            }

    def search_entries(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Search journal entries for a query string.

        Args:
            query: Search query (case-insensitive)
            limit: Maximum results to return

        Returns:
            List of matching entries
        """
        query_lower = query.lower()
        matching_entries = []

        with self.lock:
            for entry in reversed(self.entries):  # Search from most recent
                # Search in event data
                data_str = json.dumps(entry, default=str).lower()
                if query_lower in data_str:
                    matching_entries.append(entry)
                    if len(matching_entries) >= limit:
                        break

        return matching_entries

    def export_entries(self, filepath: Path, event_type: Optional[str] = None,
                      start_date: Optional[str] = None, end_date: Optional[str] = None):
        """
        Export journal entries to a file.

        Args:
            filepath: Path to export file
            event_type: Optional event type filter
            start_date: Optional start date (ISO format)
            end_date: Optional end date (ISO format)
        """
        with self.lock:
            entries_to_export = self.entries.copy()

            # Apply filters
            if event_type:
                entries_to_export = [e for e in entries_to_export if e["event_type"] == event_type]

            if start_date:
                start_dt = datetime.fromisoformat(start_date)
                entries_to_export = [e for e in entries_to_export
                                   if datetime.fromisoformat(e["timestamp"]) >= start_dt]

            if end_date:
                end_dt = datetime.fromisoformat(end_date)
                entries_to_export = [e for e in entries_to_export
                                   if datetime.fromisoformat(e["timestamp"]) <= end_dt]

        # Export to file
        with open(filepath, 'w', encoding='utf-8') as f:
            for entry in entries_to_export:
                json.dump(entry, f, ensure_ascii=False)
                f.write('\n')

    def clear_old_entries(self, days_to_keep: int = 30):
        """
        Clear journal entries older than specified days.

        Args:
            days_to_keep: Number of days of entries to keep
        """
        cutoff_date = datetime.now().timestamp() - (days_to_keep * 24 * 60 * 60)

        with self.lock:
            original_count = len(self.entries)
            self.entries = [
                entry for entry in self.entries
                if datetime.fromisoformat(entry["timestamp"]).timestamp() > cutoff_date
            ]

            removed_count = original_count - len(self.entries)

            if removed_count > 0:
                # Rewrite the journal file with remaining entries
                with open(self.journal_file, 'w', encoding='utf-8') as f:
                    for entry in self.entries:
                        json.dump(entry, f, ensure_ascii=False)
                        f.write('\n')

                self.log("system", f"Cleared {removed_count} old journal entries")

    def get_rollback_candidates(self) -> List[Dict[str, Any]]:
        """Get journal entries that have rollback snapshots"""
        with self.lock:
            candidates = []
            for entry in self.entries:
                if (entry["event_type"] == "task_complete" and
                    entry.get("data", {}).get("rollback_snapshot")):
                    candidates.append({
                        "task": entry["data"].get("task", "Unknown task"),
                        "timestamp": entry["timestamp"],
                        "rollback_snapshot": entry["data"]["rollback_snapshot"],
                        "agents_used": entry["data"].get("agents_used", [])
                    })
            return candidates[-10:]  # Return last 10 rollback candidates