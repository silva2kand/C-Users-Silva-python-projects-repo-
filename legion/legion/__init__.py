"""
Legion - AI Agent Swarm for Code Intelligence

A comprehensive system for AI-powered code analysis, generation, and refactoring
using a swarm of specialized agents.
"""

__version__ = "1.0.0"
__author__ = "Legion Development Team"
__description__ = "AI Agent Swarm for Code Intelligence"

# Import main components for easy access
from .core import LegionCore
from .cli import main as cli_main

__all__ = [
    "LegionCore",
    "cli_main",
    "__version__",
    "__author__",
    "__description__"
]