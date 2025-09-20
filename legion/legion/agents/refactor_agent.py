"""
Refactor Agent - Handles code refactoring and structural improvements
"""
from typing import Dict, Any, Optional, List
import re
from .base_agent import BaseAgent


class RefactorAgent(BaseAgent):
    """
    Refactor Agent - specializes in code refactoring, optimization, and structural improvements.
    Analyzes code for potential improvements and applies best practices.
    """

    def __init__(self, message_bus, journal, context: Optional[Dict[str, Any]] = None,
                 model_manager=None):
        super().__init__(message_bus, journal, context, model_manager)
        self.capabilities = [
            "code_refactoring",
            "optimization",
            "best_practices",
            "code_cleanup",
            "structural_improvements"
        ]

    def execute(self) -> Dict[str, Any]:
        """
        Execute code refactoring based on context and best practices.
        """
        self.start_time = self._get_timestamp()
        self._publish_status("starting", {"task": "code_refactoring"})

        try:
            # Analyze the code for refactoring opportunities
            analysis = self._analyze_code_for_refactoring()

            if not analysis["opportunities"]:
                return {
                    "action": "no_refactoring_needed",
                    "output": "Code analysis shows no significant refactoring opportunities",
                    "metadata": {"analysis": analysis}
                }

            # Generate refactoring suggestions
            suggestions = self._generate_refactoring_suggestions(analysis)

            # Apply refactoring if auto-apply is enabled
            if self.context.get("auto_apply", False):
                refactored_code = self._apply_refactoring(suggestions)
                action = "refactor_code"
                output = refactored_code
            else:
                action = "suggest_refactoring"
                output = suggestions

            # Validate the result
            if not self.validate_result({"action": action, "output": output}):
                return self._handle_error("Refactoring failed validation")

            # Log successful refactoring
            self._log_activity("refactoring_success", {
                "opportunities_found": len(analysis["opportunities"]),
                "auto_applied": self.context.get("auto_apply", False)
            })

            self._publish_status("completed", {
                "opportunities": len(analysis["opportunities"]),
                "auto_applied": self.context.get("auto_apply", False)
            })

            return {
                "action": action,
                "output": output,
                "metadata": {
                    "analysis": analysis,
                    "suggestions_count": len(suggestions) if isinstance(suggestions, list) else 1,
                    "auto_applied": self.context.get("auto_apply", False)
                }
            }

        except Exception as e:
            return self._handle_error(f"Refactoring failed: {str(e)}")

    def _analyze_code_for_refactoring(self) -> Dict[str, Any]:
        """Analyze code for refactoring opportunities"""
        code = self.context.get("current_code", "")
        file_path = self.context.get("current_file", "")

        analysis = {
            "opportunities": [],
            "issues": [],
            "metrics": {},
            "language": self._detect_language()
        }

        if not code:
            return analysis

        # Calculate basic metrics
        analysis["metrics"] = self._calculate_code_metrics(code)

        # Check for various refactoring opportunities
        analysis["opportunities"].extend(self._check_function_length(code))
        analysis["opportunities"].extend(self._check_class_complexity(code))
        analysis["opportunities"].extend(self._check_duplicate_code(code))
        analysis["opportunities"].extend(self._check_naming_conventions(code))
        analysis["opportunities"].extend(self._check_error_handling(code))
        analysis["opportunities"].extend(self._check_code_structure(code))

        # Check for code smells
        analysis["issues"].extend(self._detect_code_smells(code))

        return analysis

    def _calculate_code_metrics(self, code: str) -> Dict[str, Any]:
        """Calculate basic code metrics"""
        lines = code.split('\n')
        non_empty_lines = [line for line in lines if line.strip()]

        return {
            "total_lines": len(lines),
            "code_lines": len(non_empty_lines),
            "functions": len(re.findall(r'^\s*def\s+', code, re.MULTILINE)),
            "classes": len(re.findall(r'^\s*class\s+', code, re.MULTILINE)),
            "imports": len(re.findall(r'^\s*(import|from)\s+', code, re.MULTILINE))
        }

    def _check_function_length(self, code: str) -> List[Dict[str, Any]]:
        """Check for functions that are too long"""
        opportunities = []

        # Find all function definitions
        functions = re.finditer(r'^\s*def\s+(\w+)\s*\([^)]*\)\s*:(.*?)(?=\n\s*def|\n\s*class|\n\s*@|\n\s*$)', code, re.DOTALL | re.MULTILINE)

        for match in functions:
            func_name = match.group(1)
            func_body = match.group(2)
            line_count = len(func_body.split('\n'))

            if line_count > 30:  # Configurable threshold
                opportunities.append({
                    "type": "long_function",
                    "function": func_name,
                    "lines": line_count,
                    "suggestion": f"Consider breaking down function '{func_name}' ({line_count} lines) into smaller functions",
                    "priority": "medium"
                })

        return opportunities

    def _check_class_complexity(self, code: str) -> List[Dict[str, Any]]:
        """Check for classes with too many responsibilities"""
        opportunities = []

        # Find all class definitions
        classes = re.finditer(r'^\s*class\s+(\w+).*?:(.*?)(?=\n\s*class|\n\s*$)', code, re.DOTALL | re.MULTILINE)

        for match in classes:
            class_name = match.group(1)
            class_body = match.group(2)

            # Count methods
            methods = len(re.findall(r'^\s*def\s+', class_body, re.MULTILINE))
            attributes = len(re.findall(r'^\s*self\.\w+\s*=', class_body, re.MULTILINE))

            if methods > 15:  # Configurable threshold
                opportunities.append({
                    "type": "large_class",
                    "class": class_name,
                    "methods": methods,
                    "attributes": attributes,
                    "suggestion": f"Consider splitting class '{class_name}' ({methods} methods) into smaller classes",
                    "priority": "high"
                })

        return opportunities

    def _check_duplicate_code(self, code: str) -> List[Dict[str, Any]]:
        """Check for duplicate code patterns"""
        opportunities = []

        lines = code.split('\n')
        duplicate_blocks = {}

        # Look for duplicate blocks of 3+ lines
        for i in range(len(lines) - 3):
            block = '\n'.join(lines[i:i+3])
            if block.strip() and len(block) > 20:  # Ignore very short blocks
                if block in duplicate_blocks:
                    duplicate_blocks[block].append(i)
                else:
                    duplicate_blocks[block] = [i]

        for block, positions in duplicate_blocks.items():
            if len(positions) > 1:
                opportunities.append({
                    "type": "duplicate_code",
                    "block": block[:50] + "..." if len(block) > 50 else block,
                    "occurrences": len(positions),
                    "positions": positions,
                    "suggestion": f"Consider extracting duplicate code block into a separate function (found {len(positions)} times)",
                    "priority": "medium"
                })

        return opportunities

    def _check_naming_conventions(self, code: str) -> List[Dict[str, Any]]:
        """Check for naming convention violations"""
        opportunities = []

        # Check function names
        functions = re.findall(r'^\s*def\s+(\w+)', code, re.MULTILINE)
        for func in functions:
            if not re.match(r'^[a-z_][a-z0-9_]*$', func):
                opportunities.append({
                    "type": "naming_violation",
                    "element": func,
                    "element_type": "function",
                    "suggestion": f"Function name '{func}' should follow snake_case convention",
                    "priority": "low"
                })

        # Check class names
        classes = re.findall(r'^\s*class\s+(\w+)', code, re.MULTILINE)
        for cls in classes:
            if not re.match(r'^[A-Z][a-zA-Z0-9]*$', cls):
                opportunities.append({
                    "type": "naming_violation",
                    "element": cls,
                    "element_type": "class",
                    "suggestion": f"Class name '{cls}' should follow PascalCase convention",
                    "priority": "low"
                })

        return opportunities

    def _check_error_handling(self, code: str) -> List[Dict[str, Any]]:
        """Check for proper error handling"""
        opportunities = []

        # Look for bare except clauses
        bare_excepts = re.findall(r'except\s*:', code)
        if bare_excepts:
            opportunities.append({
                "type": "bare_except",
                "count": len(bare_excepts),
                "suggestion": "Replace bare 'except:' clauses with specific exception types for better error handling",
                "priority": "medium"
            })

        # Look for functions without error handling
        functions = re.findall(r'^\s*def\s+(\w+)\s*\([^)]*\)\s*:(.*?)(?=\n\s*def|\n\s*class|\n\s*$)', code, re.DOTALL | re.MULTILINE)
        for func_match in functions:
            func_name = func_match[0]
            func_body = func_match[1]

            # Check if function has try-except blocks
            if 'try:' not in func_body and 'except' not in func_body:
                opportunities.append({
                    "type": "missing_error_handling",
                    "function": func_name,
                    "suggestion": f"Consider adding error handling to function '{func_name}'",
                    "priority": "low"
                })

        return opportunities

    def _check_code_structure(self, code: str) -> List[Dict[str, Any]]:
        """Check for structural improvements"""
        opportunities = []

        # Check for long lines
        lines = code.split('\n')
        long_lines = [i for i, line in enumerate(lines) if len(line) > 100]
        if long_lines:
            opportunities.append({
                "type": "long_lines",
                "count": len(long_lines),
                "lines": long_lines[:5],  # Show first 5
                "suggestion": f"Consider breaking down {len(long_lines)} long lines (>100 chars) for better readability",
                "priority": "low"
            })

        # Check for magic numbers
        magic_numbers = re.findall(r'\b\d{2,}\b', code)
        if magic_numbers:
            opportunities.append({
                "type": "magic_numbers",
                "count": len(set(magic_numbers)),  # Unique numbers
                "suggestion": "Consider replacing magic numbers with named constants",
                "priority": "low"
            })

        return opportunities

    def _detect_code_smells(self, code: str) -> List[Dict[str, Any]]:
        """Detect common code smells"""
        issues = []

        # Check for print statements in production code
        print_statements = re.findall(r'\bprint\s*\(', code)
        if print_statements:
            issues.append({
                "type": "debug_prints",
                "count": len(print_statements),
                "severity": "low",
                "message": "Found print statements that should be replaced with proper logging"
            })

        # Check for TODO comments
        todos = re.findall(r'#\s*TODO', code, re.IGNORECASE)
        if todos:
            issues.append({
                "type": "todo_comments",
                "count": len(todos),
                "severity": "info",
                "message": "Found TODO comments that should be addressed"
            })

        return issues

    def _generate_refactoring_suggestions(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate detailed refactoring suggestions"""
        suggestions = []

        for opportunity in analysis["opportunities"]:
            suggestion = {
                "type": opportunity["type"],
                "description": opportunity["suggestion"],
                "priority": opportunity["priority"],
                "impact": self._estimate_impact(opportunity),
                "effort": self._estimate_effort(opportunity)
            }

            # Add specific details based on type
            if opportunity["type"] == "long_function":
                suggestion["details"] = {
                    "function_name": opportunity["function"],
                    "current_lines": opportunity["lines"],
                    "recommended_max": 30
                }
            elif opportunity["type"] == "large_class":
                suggestion["details"] = {
                    "class_name": opportunity["class"],
                    "method_count": opportunity["methods"],
                    "recommended_max": 15
                }

            suggestions.append(suggestion)

        # Sort by priority
        priority_order = {"high": 0, "medium": 1, "low": 2}
        suggestions.sort(key=lambda x: priority_order.get(x["priority"], 3))

        return suggestions

    def _estimate_impact(self, opportunity: Dict[str, Any]) -> str:
        """Estimate the impact of a refactoring"""
        if opportunity["type"] in ["large_class", "duplicate_code"]:
            return "high"
        elif opportunity["type"] in ["long_function", "bare_except"]:
            return "medium"
        else:
            return "low"

    def _estimate_effort(self, opportunity: Dict[str, Any]) -> str:
        """Estimate the effort required for a refactoring"""
        if opportunity["type"] in ["duplicate_code", "large_class"]:
            return "high"
        elif opportunity["type"] in ["long_function", "naming_violation"]:
            return "medium"
        else:
            return "low"

    def _apply_refactoring(self, suggestions: List[Dict[str, Any]]) -> str:
        """Apply automated refactoring"""
        code = self.context.get("current_code", "")

        # For now, apply only safe, automated refactorings
        # This could be expanded with more sophisticated refactoring logic

        # Apply naming convention fixes
        for suggestion in suggestions:
            if suggestion["type"] == "naming_violation":
                details = suggestion.get("details", {})
                element_type = details.get("element_type")
                element_name = details.get("element")

                if element_type == "function":
                    # Convert to snake_case
                    new_name = re.sub(r'([A-Z])', r'_\1', element_name).lower()
                    if new_name.startswith('_'):
                        new_name = new_name[1:]

                    # Replace function name
                    pattern = rf'^\s*def\s+{re.escape(element_name)}\s*'
                    code = re.sub(pattern, f'def {new_name}', code, flags=re.MULTILINE)

        return code

    def _handle_error(self, error_message: str) -> Dict[str, Any]:
        """Handle errors during refactoring"""
        self._log_activity("refactoring_error", {"error": error_message})
        self._publish_status("error", {"message": error_message})

        return {
            "action": "error",
            "output": f"Refactoring failed: {error_message}",
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
        """Validate refactoring result"""
        if not super().validate_result(result):
            return False

        action = result.get("action", "")
        output = result.get("output", "")

        if action == "no_refactoring_needed":
            return True

        return len(str(output)) > 0

    def cleanup(self):
        """Cleanup resources"""
        self._publish_status("cleanup", {"agent": self.agent_name})