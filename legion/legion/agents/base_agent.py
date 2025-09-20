"""
Base Agent - Foundation class for all Legion agents
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime


class BaseAgent(ABC):
    """
    Base class for all Legion agents.
    Provides common functionality and interface.
    """

    def __init__(self, message_bus, journal, context: Optional[Dict[str, Any]] = None,
                 model_manager=None):
        self.message_bus = message_bus
        self.journal = journal
        self.context = context or {}
        self.model_manager = model_manager
        self.agent_name = self.__class__.__name__.replace('Agent', '').lower()
        self.start_time = None

    @abstractmethod
    def execute(self) -> Dict[str, Any]:
        """
        Execute the agent's primary function.
        Must be implemented by all subclasses.

        Returns:
            Dictionary containing the result of the agent's execution
        """
        pass

    def _generate_with_model(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate text using the model manager"""
        if not self.model_manager:
            return {"error": "No model manager available", "text": ""}

        return self.model_manager.generate(prompt, self.context, **kwargs)

    def _publish_status(self, status: str, details: Optional[Dict[str, Any]] = None):
        """Publish agent status to message bus"""
        from .message_bus import publish_agent_status
        publish_agent_status(self.message_bus, self.agent_name, status, details)

    def _log_activity(self, activity_type: str, data: Dict[str, Any]):
        """Log agent activity to journal"""
        self.journal.log(
            "agent_activity",
            {
                "agent": self.agent_name,
                "activity_type": activity_type,
                "data": data,
                "timestamp": datetime.now().isoformat()
            },
            agent_name=self.agent_name
        )

    def _get_user_preferences(self) -> Dict[str, Any]:
        """Get user preferences from context"""
        return self.context.get("preferences", {})

    def _get_current_file_info(self) -> Dict[str, Any]:
        """Get information about the current file"""
        return {
            "file_path": self.context.get("current_file", ""),
            "code": self.context.get("current_code", ""),
            "language": self._detect_language()
        }

    def _detect_language(self) -> str:
        """Detect programming language from file extension"""
        file_path = self.context.get("current_file", "")
        if not file_path:
            return "unknown"

        from pathlib import Path
        ext = Path(file_path).suffix.lower()

        lang_map = {
            '.py': 'python', '.js': 'javascript', '.ts': 'typescript',
            '.java': 'java', '.cpp': 'cpp', '.c': 'c', '.cs': 'csharp',
            '.php': 'php', '.rb': 'ruby', '.go': 'go', '.rs': 'rust'
        }

        return lang_map.get(ext, 'unknown')

    def _format_code_block(self, code: str, language: str = "") -> str:
        """Format code as a markdown code block"""
        if language:
            return f"```{language}\n{code}\n```"
        return f"```\n{code}\n```"

    def _extract_code_from_response(self, response: str) -> str:
        """Extract code from model response, handling markdown formatting"""
        import re

        # Look for code blocks
        code_block_pattern = r'```(?:\w+)?\n(.*?)\n```'
        matches = re.findall(code_block_pattern, response, re.DOTALL)

        if matches:
            return matches[0].strip()

        # If no code blocks, return the response as-is
        return response.strip()

    def validate_result(self, result: Dict[str, Any]) -> bool:
        """
        Validate the agent's result.
        Can be overridden by subclasses for specific validation.

        Returns:
            True if result is valid, False otherwise
        """
        return "action" in result and "output" in result

    def cleanup(self):
        """Cleanup method called when agent is destroyed"""
        pass

    def __repr__(self):
        return f"<{self.__class__.__name__}({self.agent_name})>"


class AgentRegistry:
    """
    Registry for managing agent instances and metadata.
    """

    def __init__(self):
        self.agents = {}
        self.metadata = {}

    def register(self, agent_class, name: str, description: str = "",
                capabilities: Optional[list] = None):
        """Register an agent class"""
        self.agents[name] = agent_class
        self.metadata[name] = {
            "description": description,
            "capabilities": capabilities or [],
            "registered_at": datetime.now().isoformat()
        }

    def get_agent_class(self, name: str):
        """Get agent class by name"""
        return self.agents.get(name)

    def get_agent_metadata(self, name: str) -> Optional[Dict[str, Any]]:
        """Get agent metadata"""
        return self.metadata.get(name)

    def list_agents(self) -> Dict[str, Dict[str, Any]]:
        """List all registered agents with metadata"""
        return {
            name: {
                "class": agent_class.__name__,
                **metadata
            }
            for name, (agent_class, metadata) in self.agents.items()
        }


# Global agent registry
agent_registry = AgentRegistry()