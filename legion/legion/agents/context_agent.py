"""
Context Agent - Gathers and analyzes project-wide context for other agents
"""
from typing import Dict, Any, Optional, List
from pathlib import Path
import re
from .base_agent import BaseAgent


class ContextAgent(BaseAgent):
    """
    Context Agent - specializes in gathering and analyzing project-wide context.
    Provides relevant code snippets, dependencies, and project structure information
    to other agents for better decision making.
    """

    def __init__(self, message_bus, journal, context: Optional[Dict[str, Any]] = None,
                 model_manager=None):
        super().__init__(message_bus, journal, context, model_manager)
        self.capabilities = [
            "context_gathering",
            "code_analysis",
            "dependency_analysis",
            "project_structure",
            "semantic_search"
        ]

    def execute(self) -> Dict[str, Any]:
        """
        Gather comprehensive context for the current task.
        """
        self.start_time = self._get_timestamp()
        self._publish_status("starting", {"task": "context_gathering"})

        try:
            # Analyze the current context and task
            task_analysis = self._analyze_context_task()

            # Gather different types of context
            context_data = {
                "file_context": self._gather_file_context(task_analysis),
                "project_context": self._gather_project_context(task_analysis),
                "dependency_context": self._gather_dependency_context(task_analysis),
                "semantic_context": self._gather_semantic_context(task_analysis)
            }

            # Analyze and prioritize the gathered context
            prioritized_context = self._prioritize_context(context_data, task_analysis)

            # Format the context for other agents
            formatted_context = self._format_context(prioritized_context, task_analysis)

            # Validate the result
            if not self.validate_result({"action": "gather_context", "output": formatted_context}):
                return self._handle_error("Context gathering failed validation")

            # Log successful context gathering
            self._log_activity("context_gathered", {
                "context_items": len(formatted_context.get("related_code", [])),
                "files_analyzed": len(context_data["file_context"])
            })

            self._publish_status("completed", {
                "context_items": len(formatted_context.get("related_code", [])),
                "files_analyzed": len(context_data["file_context"])
            })

            return {
                "action": "gather_context",
                "output": formatted_context,
                "metadata": {
                    "context_types": list(context_data.keys()),
                    "total_files": len(context_data["file_context"]),
                    "semantic_matches": len(context_data["semantic_context"])
                }
            }

        except Exception as e:
            return self._handle_error(f"Context gathering failed: {str(e)}")

    def _analyze_context_task(self) -> Dict[str, Any]:
        """Analyze the context gathering task"""
        current_file = self.context.get("current_file", "")
        task_description = self.context.get("task_description", "")
        current_code = self.context.get("current_code", "")

        # Determine what kind of context is needed
        context_needs = self._determine_context_needs(task_description, current_code)

        # Get project structure
        project_root = self._find_project_root(current_file)

        return {
            "current_file": current_file,
            "task_description": task_description,
            "current_code": current_code,
            "context_needs": context_needs,
            "project_root": project_root
        }

    def _determine_context_needs(self, task_description: str, current_code: str) -> List[str]:
        """Determine what types of context are needed"""
        needs = []

        # Analyze task description for keywords
        task_lower = task_description.lower()

        if any(word in task_lower for word in ["import", "dependency", "module"]):
            needs.append("dependencies")

        if any(word in task_lower for word in ["class", "function", "method", "structure"]):
            needs.append("code_structure")

        if any(word in task_lower for word in ["similar", "related", "example"]):
            needs.append("similar_code")

        if any(word in task_lower for word in ["error", "bug", "fix", "debug"]):
            needs.append("error_patterns")

        if any(word in task_lower for word in ["test", "testing", "unit"]):
            needs.append("test_patterns")

        # Default to general context if no specific needs identified
        if not needs:
            needs = ["general"]

        return needs

    def _gather_file_context(self, task_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Gather context from relevant files"""
        current_file = task_analysis["current_file"]
        project_root = task_analysis["project_root"]
        context_needs = task_analysis["context_needs"]

        file_context = []

        if not project_root:
            return file_context

        # Find relevant files based on context needs
        relevant_files = self._find_relevant_files(project_root, context_needs, current_file)

        for file_path in relevant_files[:10]:  # Limit to 10 most relevant files
            try:
                file_info = self._analyze_file(file_path, context_needs)
                if file_info:
                    file_context.append(file_info)
            except Exception as e:
                self._log_activity("file_analysis_error", {
                    "file": str(file_path),
                    "error": str(e)
                })

        return file_context

    def _find_relevant_files(self, project_root: Path, context_needs: List[str],
                           current_file: str) -> List[Path]:
        """Find files relevant to the current task"""
        relevant_files = []

        # Get all Python files in the project
        python_files = list(project_root.rglob("*.py"))

        # Score files based on relevance
        file_scores = {}
        current_path = Path(current_file) if current_file else None

        for file_path in python_files:
            score = 0

            # Same directory gets higher score
            if current_path and file_path.parent == current_path.parent:
                score += 10

            # Similar filename gets higher score
            if current_path and file_path.stem in current_path.stem:
                score += 5

            # Check for context-specific keywords in filename
            filename_lower = file_path.name.lower()
            for need in context_needs:
                if need in filename_lower:
                    score += 3

            # Check file content for relevance
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                content_lower = content.lower()

                # Look for similar patterns or keywords
                if current_path:
                    current_content = current_path.read_text(encoding='utf-8', errors='ignore')
                    current_words = set(re.findall(r'\b\w+\b', current_content.lower()))
                    file_words = set(re.findall(r'\b\w+\b', content_lower))

                    # Calculate word overlap
                    overlap = len(current_words.intersection(file_words))
                    score += min(overlap, 10)  # Cap at 10

                for need in context_needs:
                    if need in content_lower:
                        score += 2

            except Exception:
                pass

            file_scores[file_path] = score

        # Sort by score and return top files
        sorted_files = sorted(file_scores.items(), key=lambda x: x[1], reverse=True)
        return [file for file, score in sorted_files if score > 0]

    def _analyze_file(self, file_path: Path, context_needs: List[str]) -> Optional[Dict[str, Any]]:
        """Analyze a single file for relevant context"""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')

            # Extract relevant code snippets
            relevant_snippets = self._extract_relevant_snippets(content, context_needs)

            if not relevant_snippets:
                return None

            return {
                "file_path": str(file_path),
                "file_name": file_path.name,
                "snippets": relevant_snippets,
                "imports": self._extract_imports(content),
                "classes": self._extract_classes(content),
                "functions": self._extract_functions(content)
            }

        except Exception as e:
            self._log_activity("file_analysis_error", {
                "file": str(file_path),
                "error": str(e)
            })
            return None

    def _extract_relevant_snippets(self, content: str, context_needs: List[str]) -> List[str]:
        """Extract relevant code snippets based on context needs"""
        snippets = []
        lines = content.split('\n')

        for i, line in enumerate(lines):
            line_lower = line.lower().strip()

            # Check if line matches any context need
            for need in context_needs:
                if need in line_lower:
                    # Extract snippet around this line
                    start = max(0, i - 2)
                    end = min(len(lines), i + 3)
                    snippet = '\n'.join(lines[start:end])
                    snippets.append(snippet)
                    break

        return snippets[:5]  # Limit to 5 snippets per file

    def _extract_imports(self, content: str) -> List[str]:
        """Extract import statements"""
        imports = []
        lines = content.split('\n')

        for line in lines:
            line = line.strip()
            if line.startswith('import ') or line.startswith('from '):
                imports.append(line)

        return imports

    def _extract_classes(self, content: str) -> List[str]:
        """Extract class definitions"""
        classes = []
        lines = content.split('\n')

        for line in lines:
            line = line.strip()
            if line.startswith('class '):
                classes.append(line)

        return classes

    def _extract_functions(self, content: str) -> List[str]:
        """Extract function definitions"""
        functions = []
        lines = content.split('\n')

        for line in lines:
            line = line.strip()
            if line.startswith('def ') or line.startswith('async def '):
                functions.append(line)

        return functions

    def _gather_project_context(self, task_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Gather project-level context"""
        project_root = task_analysis["project_root"]

        if not project_root:
            return {}

        try:
            # Get project structure
            structure = self._get_project_structure(project_root)

            # Get main entry points
            entry_points = self._find_entry_points(project_root)

            # Get configuration files
            config_files = self._find_config_files(project_root)

            return {
                "structure": structure,
                "entry_points": entry_points,
                "config_files": config_files
            }

        except Exception as e:
            self._log_activity("project_context_error", {"error": str(e)})
            return {}

    def _get_project_structure(self, project_root: Path) -> Dict[str, Any]:
        """Get basic project structure"""
        structure = {}

        for item in project_root.rglob("*"):
            if item.is_file():
                relative_path = item.relative_to(project_root)
                parts = str(relative_path).split('/')
                current = structure

                for part in parts[:-1]:
                    if part not in current:
                        current[part] = {}
                    current = current[part]

                if parts[-1] not in current:
                    current[parts[-1]] = "file"

        return structure

    def _find_entry_points(self, project_root: Path) -> List[str]:
        """Find main entry points"""
        entry_points = []

        # Look for common entry point files
        common_entries = ["main.py", "app.py", "__main__.py", "run.py"]

        for entry in common_entries:
            if (project_root / entry).exists():
                entry_points.append(entry)

        return entry_points

    def _find_config_files(self, project_root: Path) -> List[str]:
        """Find configuration files"""
        config_files = []

        # Look for common config files
        config_patterns = ["*.json", "*.yaml", "*.yml", "*.toml", "*.ini", "*.cfg"]

        for pattern in config_patterns:
            for config_file in project_root.glob(pattern):
                config_files.append(str(config_file.relative_to(project_root)))

        return config_files

    def _gather_dependency_context(self, task_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Gather dependency information"""
        project_root = task_analysis["project_root"]

        if not project_root:
            return {}

        dependencies = {}

        # Check for requirements.txt
        req_file = project_root / "requirements.txt"
        if req_file.exists():
            try:
                with open(req_file, 'r', encoding='utf-8') as f:
                    dependencies["requirements"] = [line.strip() for line in f if line.strip()]
            except Exception:
                pass

        # Check for setup.py
        setup_file = project_root / "setup.py"
        if setup_file.exists():
            try:
                content = setup_file.read_text(encoding='utf-8')
                # Extract install_requires if present
                if "install_requires" in content:
                    dependencies["setup_py"] = "setup.py contains dependencies"
            except Exception:
                pass

        return dependencies

    def _gather_semantic_context(self, task_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Gather semantic context using advanced analysis"""
        # This would integrate with the ContextEngine for vector similarity
        # For now, return basic semantic matches
        return []

    def _prioritize_context(self, context_data: Dict[str, Any],
                          task_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Prioritize and organize the gathered context"""
        prioritized = {
            "high_priority": [],
            "medium_priority": [],
            "low_priority": []
        }

        # Prioritize file context
        for file_info in context_data["file_context"][:5]:  # Top 5 files
            prioritized["high_priority"].append(file_info)

        # Add project context
        if context_data["project_context"]:
            prioritized["medium_priority"].append(context_data["project_context"])

        # Add dependency context
        if context_data["dependency_context"]:
            prioritized["low_priority"].append(context_data["dependency_context"])

        return prioritized

    def _format_context(self, prioritized_context: Dict[str, Any],
                       task_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Format the context for other agents"""
        formatted = {
            "related_code": [],
            "project_info": {},
            "dependencies": {},
            "recommendations": []
        }

        # Format high priority context
        for item in prioritized_context["high_priority"]:
            if "snippets" in item:
                formatted["related_code"].extend(item["snippets"])

        # Format project info
        for item in prioritized_context["medium_priority"]:
            if "structure" in item:
                formatted["project_info"]["structure"] = item["structure"]
            if "entry_points" in item:
                formatted["project_info"]["entry_points"] = item["entry_points"]

        # Format dependencies
        for item in prioritized_context["low_priority"]:
            formatted["dependencies"].update(item)

        # Add recommendations based on context
        formatted["recommendations"] = self._generate_recommendations(formatted, task_analysis)

        return formatted

    def _generate_recommendations(self, formatted_context: Dict[str, Any],
                                task_analysis: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on gathered context"""
        recommendations = []

        # Check for missing imports
        if formatted_context["dependencies"].get("requirements"):
            recommendations.append("Consider checking if all required dependencies are installed")

        # Check for similar patterns
        if len(formatted_context["related_code"]) > 0:
            recommendations.append(f"Found {len(formatted_context['related_code'])} related code patterns to reference")

        # Check project structure
        if formatted_context["project_info"].get("entry_points"):
            recommendations.append("Project has clear entry points defined")

        return recommendations

    def _find_project_root(self, current_file: str) -> Optional[Path]:
        """Find the project root directory"""
        if not current_file:
            return None

        current_path = Path(current_file)
        project_root = current_path.parent

        # Look for common project markers
        markers = ["requirements.txt", "setup.py", ".git", "pyproject.toml"]

        while project_root.parent != project_root:
            if any((project_root / marker).exists() for marker in markers):
                return project_root
            project_root = project_root.parent

        return None

    def _handle_error(self, error_message: str) -> Dict[str, Any]:
        """Handle errors during context gathering"""
        self._log_activity("context_error", {"error": error_message})
        self._publish_status("error", {"message": error_message})

        return {
            "action": "error",
            "output": f"Context gathering failed: {error_message}",
            "metadata": {
                "error": True,
                "error_message": error_message
            }
        }

    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()

    def validate_result(self, result: Dict[str, Any]) -> bool:
        """Validate context gathering result"""
        if not super().validate_result(result):
            return False

        output = result.get("output", {})
        return isinstance(output, dict) and len(output) > 0

    def cleanup(self):
        """Cleanup resources"""
        self._publish_status("cleanup", {"agent": self.agent_name})