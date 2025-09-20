"""
Message Bus - Pub/Sub system for inter-agent communication
"""
import asyncio
import json
import threading
import time
from typing import Dict, List, Callable, Any, Optional
from collections import defaultdict
from datetime import datetime


class MessageBus:
    """
    Publish-Subscribe message bus for Legion's agent communication.
    Enables loose coupling between agents and real-time event distribution.
    """

    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self.message_history: List[Dict[str, Any]] = []
        self.max_history = 1000
        self.lock = threading.Lock()
        self._running = True

    def subscribe(self, topic: str, callback: Callable[[Dict[str, Any]], None]) -> str:
        """
        Subscribe to a topic with a callback function.

        Args:
            topic: Topic to subscribe to
            callback: Function to call when messages are published to this topic

        Returns:
            Subscription ID for unsubscribing
        """
        with self.lock:
            subscription_id = f"{topic}_{id(callback)}_{time.time()}"
            self.subscribers[topic].append((subscription_id, callback))
            return subscription_id

    def unsubscribe(self, subscription_id: str):
        """
        Unsubscribe from a topic using subscription ID.

        Args:
            subscription_id: Subscription ID returned from subscribe()
        """
        with self.lock:
            for topic, subscribers in self.subscribers.items():
                self.subscribers[topic] = [
                    (sid, callback) for sid, callback in subscribers
                    if sid != subscription_id
                ]

    def publish(self, topic: str, message: Dict[str, Any], sender: Optional[str] = None):
        """
        Publish a message to a topic.

        Args:
            topic: Topic to publish to
            message: Message payload
            sender: Optional sender identifier
        """
        # Enrich message with metadata
        enriched_message = {
            "topic": topic,
            "payload": message,
            "sender": sender,
            "timestamp": datetime.now().isoformat(),
            "message_id": f"{topic}_{time.time()}_{hash(str(message))}"
        }

        # Store in history
        with self.lock:
            self.message_history.append(enriched_message)
            if len(self.message_history) > self.max_history:
                self.message_history.pop(0)

        # Notify subscribers
        self._notify_subscribers(topic, enriched_message)

    def _notify_subscribers(self, topic: str, message: Dict[str, Any]):
        """Notify all subscribers of a topic about a new message"""
        subscribers = self.subscribers.get(topic, [])

        for subscription_id, callback in subscribers:
            try:
                # Run callback in a separate thread to avoid blocking
                threading.Thread(
                    target=self._safe_callback,
                    args=(callback, message),
                    daemon=True
                ).start()
            except Exception as e:
                print(f"Error notifying subscriber {subscription_id}: {e}")

    def _safe_callback(self, callback: Callable, message: Dict[str, Any]):
        """Safely execute a callback with error handling"""
        try:
            callback(message)
        except Exception as e:
            print(f"Error in message bus callback: {e}")

    def get_topic_subscribers(self, topic: str) -> int:
        """Get the number of subscribers for a topic"""
        return len(self.subscribers.get(topic, []))

    def get_message_history(self, topic: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get recent message history, optionally filtered by topic.

        Args:
            topic: Optional topic filter
            limit: Maximum number of messages to return

        Returns:
            List of recent messages
        """
        with self.lock:
            if topic:
                messages = [msg for msg in self.message_history if msg["topic"] == topic]
            else:
                messages = self.message_history.copy()

            return messages[-limit:]

    def get_topics(self) -> List[str]:
        """Get list of all active topics"""
        return list(self.subscribers.keys())

    def clear_history(self):
        """Clear message history"""
        with self.lock:
            self.message_history.clear()

    def get_stats(self) -> Dict[str, Any]:
        """Get message bus statistics"""
        return {
            "active_topics": len(self.subscribers),
            "total_subscribers": sum(len(subs) for subs in self.subscribers.values()),
            "messages_in_history": len(self.message_history),
            "topics": list(self.subscribers.keys())
        }


# Convenience functions for common message types
def publish_agent_status(bus: MessageBus, agent_name: str, status: str, details: Optional[Dict] = None):
    """Publish agent status update"""
    bus.publish("agent.status", {
        "agent": agent_name,
        "status": status,
        "details": details or {}
    }, sender=agent_name)


def publish_task_progress(bus: MessageBus, task_id: str, progress: float, message: str):
    """Publish task progress update"""
    bus.publish("task.progress", {
        "task_id": task_id,
        "progress": progress,
        "message": message
    })


def publish_journal_entry(bus: MessageBus, entry_type: str, data: Dict[str, Any]):
    """Publish journal entry"""
    bus.publish("journal.entry", {
        "type": entry_type,
        "data": data
    })


def subscribe_to_agent_status(bus: MessageBus, callback: Callable) -> str:
    """Subscribe to agent status updates"""
    return bus.subscribe("agent.status", callback)


def subscribe_to_task_progress(bus: MessageBus, callback: Callable) -> str:
    """Subscribe to task progress updates"""
    return bus.subscribe("task.progress", callback)


def subscribe_to_journal(bus: MessageBus, callback: Callable) -> str:
    """Subscribe to journal entries"""
    return bus.subscribe("journal.entry", callback)