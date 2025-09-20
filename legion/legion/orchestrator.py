"""
Orchestrator - Intelligent agent chaining and task distribution
"""
import re
from typing import List, Dict, Any, Optional
from pathlib import Path


class Orchestrator:
    """
    Orchestrator for Legion - determines optimal agent chains for tasks.
    Analyzes task requirements and context to select the best sequence of agents.
    """

    def __init__(self):
        # Agent capabilities and their triggers
        self.agent_capabilities = {
            "context_agent": {
                "triggers": [
                    r"context", r"related", r"similar", r"find", r"search",
                    r"understand", r"explore", r"analyze", r"examine"
                ],
                "priority": 10,
                "description": "Gathers relevant project context"
            },
            "completion_agent": {
                "triggers": [
                    r"complete", r"finish", r"implement", r"write", r"create",
                    r"generate", r"add", r"insert", r"fix", r"correct"
                ],
                "priority": 8,
                "description": "Code completion and generation"
            },
            "refactor_agent": {
                "triggers": [
                    r"refactor", r"restructure", r"improve", r"optimize",
                    r"clean", r"simplify", r"extract", r"rename", r"move"
                ],
                "priority": 7,
                "description": "Code refactoring and structural improvements"
            },
            "test_gen_agent": {
                "triggers": [
                    r"test", r"spec", r"unit", r"integration", r"coverage",
                    r"assert", r"verify", r"validate", r"check"
                ],
                "priority": 6,
                "description": "Test generation and validation"
            },
            "review_agent": {
                "triggers": [
                    r"review", r"audit", r"inspect", r"check", r"validate",
                    r"quality", r"standards", r"best.practice", r"lint"
                ],
                "priority": 5,
                "description": "Code review and quality assessment"
            },
            "narrator_agent": {
                "triggers": [
                    r"narrate", r"explain", r"describe", r"tell", r"voice",
                    r"audio", r"speak", r"announce", r"report"
                ],
                "priority": 3,
                "description": "Voice narration and explanations"
            },
            "fixer_shell": {
                "triggers": [
                    r"debug", r"trace", r"error", r"exception", r"fix",
                    r"resolve", r"diagnose", r"investigate", r"troubleshoot"
                ],
                "priority": 9,
                "description": "Error tracing and fixing"
            }
        }

        # Task type mappings
        self.task_mappings = {
            "completion": ["context_agent", "completion_agent", "review_agent"],
            "refactoring": ["context_agent", "refactor_agent", "test_gen_agent", "review_agent"],
            "debugging": ["context_agent", "fixer_shell", "completion_agent"],
            "testing": ["context_agent", "test_gen_agent", "review_agent"],
            "documentation": ["context_agent", "narrator_agent"],
            "review": ["context_agent", "review_agent", "narrator_agent"],
            "exploration": ["context_agent", "narrator_agent"]
        }

    def determine_agent_chain(self, task: str, context: Dict[str, Any]) -> List[str]:
        """
        Determine the optimal sequence of agents for a given task.

        Args:
            task: Task description
            context: Context information including code, file, preferences

        Returns:
            List of agent names in execution order
        """
        task_lower = task.lower()

        # 1. Try to match task to predefined patterns
        chain = self._match_task_pattern(task_lower)
        if chain:
            return self._optimize_chain(chain, context)

        # 2. Analyze task keywords to determine required agents
        required_agents = self._analyze_task_keywords(task_lower)

        # 3. Consider context factors
        context_agents = self._analyze_context_factors(context)

        # 4. Combine and prioritize agents
        final_chain = self._combine_agents(required_agents, context_agents)

        # 5. Add always-useful agents if not already included
        final_chain = self._add_utility_agents(final_chain, task_lower)

        return final_chain

    def _match_task_pattern(self, task: str) -> Optional[List[str]]:
        """Match task to predefined patterns"""
        # Code completion patterns
        if any(word in task for word in ["complete", "finish", "implement", "write", "generate"]):
            return self.task_mappings["completion"]

        # Refactoring patterns
        if any(word in task for word in ["refactor", "restructure", "improve", "optimize", "clean"]):
            return self.task_mappings["refactoring"]

        # Debugging patterns
        if any(word in task for word in ["debug", "fix", "error", "exception", "trace"]):
            return self.task_mappings["debugging"]

        # Testing patterns
        if any(word in task for word in ["test", "spec", "unit", "integration"]):
            return self.task_mappings["testing"]

        # Documentation patterns
        if any(word in task for word in ["document", "explain", "describe", "comment"]):
            return self.task_mappings["documentation"]

        # Review patterns
        if any(word in task for word in ["review", "audit", "inspect", "check"]):
            return self.task_mappings["review"]

        return None

    def _analyze_task_keywords(self, task: str) -> List[str]:
        """Analyze task keywords to determine required agents"""
        agents_scores = {}

        for agent_name, capabilities in self.agent_capabilities.items():
            score = 0
            for trigger in capabilities["triggers"]:
                if re.search(r'\b' + trigger + r'\b', task, re.IGNORECASE):
                    score += capabilities["priority"]

            if score > 0:
                agents_scores[agent_name] = score

        # Sort agents by score (highest first)
        sorted_agents = sorted(agents_scores.items(), key=lambda x: x[1], reverse=True)
        return [agent for agent, score in sorted_agents]

    def _analyze_context_factors(self, context: Dict[str, Any]) -> List[str]:
        """Analyze context to determine additional agents needed"""
        agents = []

        # Check if we have current code
        if context.get("current_code"):
            agents.append("context_agent")  # Always useful when we have code

        # Check file type
        current_file = context.get("current_file", "")
        if current_file:
            file_ext = Path(current_file).suffix.lower()

            # For test files, prioritize test generation
            if "test" in current_file.lower():
                agents.append("test_gen_agent")

            # For configuration files, might need different handling
            if file_ext in [".json", ".yaml", ".yml", ".toml", ".xml"]:
                agents.append("review_agent")  # Configuration review

        # Check user preferences
        preferences = context.get("preferences", {})
        if preferences.get("voice_enabled", False):
            agents.append("narrator_agent")

        if preferences.get("strict_mode", False):
            agents.append("review_agent")

        return list(set(agents))  # Remove duplicates

    def _combine_agents(self, keyword_agents: List[str], context_agents: List[str]) -> List[str]:
        """Combine agents from different sources with proper ordering"""
        all_agents = list(set(keyword_agents + context_agents))

        # Define execution order preferences
        order_preferences = {
            "context_agent": 1,      # Always first - gathers context
            "fixer_shell": 2,        # Early - debugging
            "completion_agent": 3,   # Core functionality
            "refactor_agent": 4,     # Structural changes
            "test_gen_agent": 5,     # Generate tests
            "review_agent": 6,       # Quality check
            "narrator_agent": 7      # Last - reporting
        }

        # Sort by execution order
        def sort_key(agent):
            return order_preferences.get(agent, 99)  # Unknown agents go last

        return sorted(all_agents, key=sort_key)

    def _add_utility_agents(self, chain: List[str], task: str) -> List[str]:
        """Add utility agents that are always useful"""
        # Always include context_agent if not present (unless it's a very simple task)
        if "context_agent" not in chain and len(task.split()) > 3:
            chain.insert(0, "context_agent")

        # Add narrator_agent for complex tasks or if voice is mentioned
        if "narrator_agent" not in chain and ("explain" in task or "describe" in task):
            chain.append("narrator_agent")

        # Add review_agent for code modification tasks
        if ("review_agent" not in chain and
            any(word in task for word in ["write", "create", "implement", "fix", "refactor"])):
            chain.append("review_agent")

        return chain

    def _optimize_chain(self, chain: List[str], context: Dict[str, Any]) -> List[str]:
        """Optimize agent chain based on context and efficiency"""
        optimized_chain = chain.copy()

        # Remove redundant agents
        if "context_agent" in optimized_chain and len(optimized_chain) > 1:
            # Context agent is only needed once at the beginning
            if optimized_chain.count("context_agent") > 1:
                # Keep only the first occurrence
                first_context_idx = optimized_chain.index("context_agent")
                optimized_chain = [agent for i, agent in enumerate(optimized_chain)
                                 if agent != "context_agent" or i == first_context_idx]

        # Skip review_agent for very simple tasks
        if (len(context.get("current_code", "")) < 50 and
            "review_agent" in optimized_chain and
            len(optimized_chain) > 2):
            optimized_chain.remove("review_agent")

        # Skip test generation for non-code files
        current_file = context.get("current_file", "")
        if (current_file and
            Path(current_file).suffix.lower() not in [".py", ".js", ".ts", ".java", ".cpp", ".c", ".cs"] and
            "test_gen_agent" in optimized_chain):
            optimized_chain.remove("test_gen_agent")

        return optimized_chain

    def get_agent_info(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific agent"""
        return self.agent_capabilities.get(agent_name)

    def get_available_agents(self) -> List[str]:
        """Get list of all available agents"""
        return list(self.agent_capabilities.keys())

    def explain_chain(self, chain: List[str]) -> str:
        """Provide human-readable explanation of an agent chain"""
        explanations = []
        for agent in chain:
            info = self.get_agent_info(agent)
            if info:
                explanations.append(f"{agent}: {info['description']}")

        return "\n".join(explanations)

    def validate_chain(self, chain: List[str]) -> Dict[str, Any]:
        """Validate an agent chain for potential issues"""
        issues = []
        warnings = []

        # Check for missing critical agents
        if not any(agent in ["completion_agent", "refactor_agent", "fixer_shell"] for agent in chain):
            warnings.append("No primary action agent (completion, refactor, or fixer) in chain")

        # Check for inefficient ordering
        if "review_agent" in chain and chain.index("review_agent") < len(chain) - 1:
            warnings.append("Review agent should typically be last in the chain")

        # Check for redundant agents
        agent_counts = {}
        for agent in chain:
            agent_counts[agent] = agent_counts.get(agent, 0) + 1

        for agent, count in agent_counts.items():
            if count > 1:
                issues.append(f"Agent '{agent}' appears {count} times (redundant)")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "chain_length": len(chain)
        }