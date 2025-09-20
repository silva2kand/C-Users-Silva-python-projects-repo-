"""
Legion Core - The heart of the AI agent orchestration system
"""
import importlib
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

from .message_bus import MessageBus
from .journal import Journal
from .context_engine import ContextEngine
from .orchestrator import Orchestrator
from .model_manager import ModelManager


class LegionCore:
    """
    The central orchestrator for Legion's agent swarm.
    Manages agent lifecycle, communication, and task execution.
    """

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.message_bus = MessageBus()
        self.journal = Journal(self.project_root / ".legion" / "journal.jsonl")
        self.context_engine = ContextEngine(self.project_root)
        self.orchestrator = Orchestrator()
        self.model_manager = ModelManager()
        self.agent_registry: Dict[str, Any] = {}

        # Initialize core directories
        self._setup_directories()

        # Log system initialization
        self.journal.log("system", "Legion core initialized", {
            "project_root": str(self.project_root),
            "timestamp": datetime.now().isoformat()
        })

    def _setup_directories(self):
        """Create necessary directories for Legion operation"""
        legion_dir = self.project_root / ".legion"
        legion_dir.mkdir(exist_ok=True)

        # Create subdirectories
        (legion_dir / "agents").mkdir(exist_ok=True)
        (legion_dir / "cache").mkdir(exist_ok=True)
        (legion_dir / "backups").mkdir(exist_ok=True)

    def request(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point for task requests.
        Orchestrates the entire agent swarm for task completion.

        Args:
            task: Description of the task to perform
            context: Context dictionary containing user, file, code, etc.

        Returns:
            Dictionary containing the final result and metadata
        """
        start_time = time.time()

        # 1. Journal the request
        self.journal.log("task_request", {
            "task": task,
            "context": context,
            "user": context.get('user', 'unknown'),
            "timestamp": datetime.now().isoformat()
        })

        try:
            # 2. Context Engine gathers relevant codebase context
            enriched_context = self.context_engine.get_relevant_context(
                task=task,
                current_file=context.get('file', ''),
                current_code=context.get('code', ''),
                user_preferences=context.get('preferences', {})
            )

            # 3. Orchestrator determines the right agent chain
            agent_chain = self.orchestrator.determine_agent_chain(task, enriched_context)

            # 4. Deploy agents sequentially or in parallel
            results = []
            for agent_name in agent_chain:
                self.journal.log("agent_deployment", {
                    "agent": agent_name,
                    "task": task,
                    "chain_position": len(results) + 1
                })

                agent = self.spawn_agent(agent_name, enriched_context)
                result = agent.execute()

                # Journal the agent's result
                self.journal.log("agent_result", {
                    "agent": agent_name,
                    "result": result,
                    "execution_time": time.time() - start_time
                })

                results.append(result)

                # Agents are destroyed after task completion (by default)
                del agent

            # 5. Consolidate results and create rollback plan
            final_output = self._consolidate_results(results)

            # Create git stash for rollback capability
            rollback_snapshot = self._create_rollback_snapshot()

            # Log final output
            self.journal.log("task_complete", {
                "task": task,
                "final_output": final_output,
                "rollback_snapshot": rollback_snapshot,
                "total_execution_time": time.time() - start_time,
                "agents_used": agent_chain
            })

            return {
                "status": "success",
                "output": final_output,
                "metadata": {
                    "execution_time": time.time() - start_time,
                    "agents_used": agent_chain,
                    "rollback_snapshot": rollback_snapshot,
                    "journal_entries": len(results)
                }
            }

        except Exception as e:
            # Log the error
            self.journal.log("task_error", {
                "task": task,
                "error": str(e),
                "error_type": type(e).__name__,
                "execution_time": time.time() - start_time
            })

            return {
                "status": "error",
                "error": str(e),
                "metadata": {
                    "execution_time": time.time() - start_time,
                    "error_type": type(e).__name__
                }
            }

    def spawn_agent(self, agent_name: str, context: Dict[str, Any]) -> Any:
        """
        Dynamically loads and initializes an agent from the agents module.

        Args:
            agent_name: Name of the agent to spawn
            context: Context to pass to the agent

        Returns:
            Initialized agent instance
        """
        try:
            # Import the agent module dynamically
            agent_module = importlib.import_module(f"legion.agents.{agent_name}")

            # Get the agent class (assuming PascalCase naming)
            agent_class_name = agent_name.replace('_', ' ').title().replace(' ', '')
            agent_class = getattr(agent_module, agent_class_name)

            # Initialize the agent with required dependencies
            agent = agent_class(
                message_bus=self.message_bus,
                journal=self.journal,
                context=context,
                model_manager=self.model_manager
            )

            # Register the agent
            self.agent_registry[agent_name] = agent

            return agent

        except (ImportError, AttributeError) as e:
            raise ValueError(f"Failed to spawn agent '{agent_name}': {e}")

    def _consolidate_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Consolidate results from multiple agents into a final output.

        Args:
            results: List of results from individual agents

        Returns:
            Consolidated final result
        """
        if not results:
            return {"consolidated": "No results to consolidate"}

        # For now, return the last result (can be enhanced with more sophisticated logic)
        final_result = results[-1]

        # Add metadata about consolidation
        final_result["consolidation"] = {
            "total_agents": len(results),
            "agent_results": [r.get("action", "unknown") for r in results]
        }

        return final_result

    def _create_rollback_snapshot(self) -> Optional[str]:
        """
        Create a git stash for rollback capability.

        Returns:
            Stash reference if successful, None otherwise
        """
        try:
            import subprocess
            import uuid

            # Generate unique stash message
            stash_message = f"legion-auto-stash-{uuid.uuid4().hex[:8]}"

            # Create git stash
            result = subprocess.run(
                ["git", "stash", "push", "-m", stash_message],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                return stash_message
            else:
                self.journal.log("warning", f"Failed to create git stash: {result.stderr}")
                return None

        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError) as e:
            self.journal.log("warning", f"Git stash creation failed: {e}")
            return None

    def get_status(self) -> Dict[str, Any]:
        """Get current status of the Legion system"""
        return {
            "active_agents": list(self.agent_registry.keys()),
            "journal_entries": self.journal.get_entry_count(),
            "context_indexed": self.context_engine.is_indexed(),
            "project_root": str(self.project_root),
            "last_activity": self.journal.get_last_entry_time()
        }

    def shutdown(self):
        """Gracefully shutdown the Legion system"""
        self.journal.log("system", "Legion core shutting down")

        # Clean up active agents
        for agent_name, agent in self.agent_registry.items():
            try:
                if hasattr(agent, 'cleanup'):
                    agent.cleanup()
            except Exception as e:
                self.journal.log("warning", f"Error cleaning up agent {agent_name}: {e}")

        self.agent_registry.clear()

        # Final journal entry
        self.journal.log("system", "Legion core shutdown complete")