"""
Review Agent - Performs code quality assessment and review
"""
from typing import Dict, Any, Optional, List
import re
from .base_agent import BaseAgent


class ReviewAgent(BaseAgent):
    """
    Review Agent - specializes in comprehensive code quality assessment.
    Performs static analysis, style checking, and provides detailed feedback.
    """

    def __init__(self, message_bus, journal, context: Optional[Dict[str, Any]] = None,
                 model_manager=None):
        super().__init__(message_bus, journal, context, model_manager)
        self.capabilities = [
            "code_review",
            "quality_assessment",
            "style_checking",
            "security_analysis",
            "performance_review"
        ]

    def execute(self) -> Dict[str, Any]:
        """
        Perform comprehensive code review and quality assessment.
        """
        self.start_time = self._get_timestamp()
        self._publish_status("starting", {"task": "code_review"})

        try:
            # Perform comprehensive code analysis
            review_results = self._perform_code_review()

            # Generate review report
            review_report = self._generate_review_report(review_results)

            # Calculate quality score
            quality_score = self._calculate_quality_score(review_results)

            # Generate recommendations
            recommendations = self._generate_recommendations(review_results)

            # Validate the result
            if not self.validate_result({"action": "code_review", "output": review_report}):
                return self._handle_error("Code review failed validation")

            # Log successful review
            self._log_activity("review_success", {
                "issues_found": len(review_results["issues"]),
                "quality_score": quality_score,
                "recommendations": len(recommendations)
            })

            self._publish_status("completed", {
                "issues": len(review_results["issues"]),
                "score": quality_score
            })

            return {
                "action": "code_review",
                "output": {
                    "report": review_report,
                    "quality_score": quality_score,
                    "recommendations": recommendations,
                    "detailed_results": review_results
                },
                "metadata": {
                    "review_type": "comprehensive",
                    "issues_count": len(review_results["issues"]),
                    "warnings_count": len(review_results["warnings"]),
                    "suggestions_count": len(recommendations),
                    "review_timestamp": self._get_timestamp()
                }
            }

        except Exception as e:
            return self._handle_error(f"Code review failed: {str(e)}")

    def _perform_code_review(self) -> Dict[str, Any]:
        """Perform comprehensive code review"""
        code = self.context.get("current_code", "")
        file_path = self.context.get("current_file", "")

        review_results = {
            "issues": [],
            "warnings": [],
            "suggestions": [],
            "metrics": {},
            "security_issues": [],
            "performance_issues": [],
            "maintainability_score": 0
        }

        if not code:
            return review_results

        # Calculate basic metrics
        review_results["metrics"] = self._calculate_review_metrics(code)

        # Perform various review checks
        review_results["issues"].extend(self._check_syntax_errors(code))
        review_results["issues"].extend(self._check_import_issues(code))
        review_results["warnings"].extend(self._check_style_issues(code))
        review_results["warnings"].extend(self._check_best_practices(code))
        review_results["security_issues"].extend(self._check_security_vulnerabilities(code))
        review_results["performance_issues"].extend(self._check_performance_issues(code))
        review_results["suggestions"].extend(self._generate_improvement_suggestions(code))

        # Calculate maintainability score
        review_results["maintainability_score"] = self._calculate_maintainability_score(review_results)

        return review_results

    def _calculate_review_metrics(self, code: str) -> Dict[str, Any]:
        """Calculate code metrics for review"""
        lines = code.split('\n')
        non_empty_lines = [line for line in lines if line.strip()]

        return {
            "total_lines": len(lines),
            "code_lines": len(non_empty_lines),
            "comment_lines": len([line for line in lines if line.strip().startswith('#')]),
            "blank_lines": len(lines) - len(non_empty_lines),
            "functions": len(re.findall(r'^\s*def\s+', code, re.MULTILINE)),
            "classes": len(re.findall(r'^\s*class\s+', code, re.MULTILINE)),
            "imports": len(re.findall(r'^\s*(import|from)\s+', code, re.MULTILINE)),
            "complexity": self._calculate_cyclomatic_complexity(code),
            "average_function_length": self._calculate_average_function_length(code)
        }

    def _calculate_cyclomatic_complexity(self, code: str) -> int:
        """Calculate cyclomatic complexity"""
        complexity = 1  # Base complexity

        # Add complexity for control structures
        complexity += len(re.findall(r'\b(if|elif|for|while|case|catch)\b', code))
        complexity += len(re.findall(r'\b(and|or)\b', code))  # Boolean operators
        complexity += len(re.findall(r'except\s+', code))  # Exception handlers

        return complexity

    def _calculate_average_function_length(self, code: str) -> float:
        """Calculate average function length"""
        functions = re.findall(r'^\s*def\s+\w+.*?:(.*?)(?=\n\s*def|\n\s*class|\n\s*$)', code, re.DOTALL | re.MULTILINE)

        if not functions:
            return 0

        total_lines = sum(len(func.split('\n')) for func in functions)
        return total_lines / len(functions)

    def _check_syntax_errors(self, code: str) -> List[Dict[str, Any]]:
        """Check for syntax errors"""
        issues = []

        # Check for common syntax issues
        if 'print(' in code and 'import sys' not in code:
            # Python 2 style print without proper imports
            issues.append({
                "type": "syntax_error",
                "severity": "high",
                "line": "unknown",
                "message": "Using print() function without proper Python version handling",
                "suggestion": "Use print() for Python 3 or from __future__ import print_function"
            })

        # Check for indentation issues
        lines = code.split('\n')
        for i, line in enumerate(lines):
            if line.strip() and not line.startswith(' ') and not line.startswith('\t') and i > 0:
                # Mixed indentation
                prev_line = lines[i-1]
                if (prev_line.startswith(' ') and not line.startswith(' ')) or \
                   (prev_line.startswith('\t') and not line.startswith('\t')):
                    issues.append({
                        "type": "syntax_error",
                        "severity": "high",
                        "line": i + 1,
                        "message": "Mixed indentation (spaces and tabs)",
                        "suggestion": "Use consistent indentation (preferably 4 spaces)"
                    })
                    break

        return issues

    def _check_import_issues(self, code: str) -> List[Dict[str, Any]]:
        """Check for import-related issues"""
        issues = []

        # Check for unused imports
        lines = code.split('\n')
        imports = []
        import_usage = {}

        for line in lines:
            if line.strip().startswith('import ') or line.strip().startswith('from '):
                if 'import' in line:
                    parts = line.split('import')
                    if len(parts) > 1:
                        module = parts[1].strip().split('.')[0].split(' as ')[0]
                        imports.append(module)
            elif line.strip() and not line.strip().startswith('#'):
                # Check usage in code
                for imp in imports:
                    if imp in line and imp not in import_usage:
                        import_usage[imp] = True

        unused_imports = [imp for imp in imports if imp not in import_usage]
        for unused in unused_imports:
            issues.append({
                "type": "import_issue",
                "severity": "medium",
                "line": "unknown",
                "message": f"Unused import: {unused}",
                "suggestion": "Remove unused import or use it in the code"
            })

        return issues

    def _check_style_issues(self, code: str) -> List[Dict[str, Any]]:
        """Check for style issues"""
        warnings = []

        lines = code.split('\n')

        for i, line in enumerate(lines):
            # Check line length
            if len(line) > 100:
                warnings.append({
                    "type": "style_issue",
                    "severity": "low",
                    "line": i + 1,
                    "message": f"Line too long ({len(line)} characters)",
                    "suggestion": "Break long lines into multiple lines for better readability"
                })

            # Check for multiple statements on one line
            if line.count(';') > 1:
                warnings.append({
                    "type": "style_issue",
                    "severity": "medium",
                    "line": i + 1,
                    "message": "Multiple statements on one line",
                    "suggestion": "Put each statement on a separate line"
                })

            # Check for inconsistent naming
            if re.search(r'\b[A-Z][a-z]*[A-Z][a-z]*\b', line):  # camelCase in Python
                warnings.append({
                    "type": "style_issue",
                    "severity": "low",
                    "line": i + 1,
                    "message": "Using camelCase in Python (should use snake_case)",
                    "suggestion": "Use snake_case for variable and function names in Python"
                })

        return warnings

    def _check_best_practices(self, code: str) -> List[Dict[str, Any]]:
        """Check for best practices violations"""
        warnings = []

        # Check for global variables
        if re.search(r'\bglobal\s+', code):
            warnings.append({
                "type": "best_practice",
                "severity": "medium",
                "line": "unknown",
                "message": "Use of global variables",
                "suggestion": "Avoid global variables; pass parameters instead"
            })

        # Check for magic numbers
        magic_numbers = re.findall(r'\b\d{2,}\b', code)
        if magic_numbers:
            warnings.append({
                "type": "best_practice",
                "severity": "low",
                "line": "unknown",
                "message": f"Found {len(set(magic_numbers))} magic numbers",
                "suggestion": "Replace magic numbers with named constants"
            })

        # Check for bare except clauses
        if re.search(r'except\s*:', code):
            warnings.append({
                "type": "best_practice",
                "severity": "high",
                "line": "unknown",
                "message": "Bare except clause catches all exceptions",
                "suggestion": "Specify exception types to catch (e.g., except ValueError:)"
            })

        return warnings

    def _check_security_vulnerabilities(self, code: str) -> List[Dict[str, Any]]:
        """Check for security vulnerabilities"""
        security_issues = []

        # Check for eval usage
        if 'eval(' in code:
            security_issues.append({
                "type": "security_vulnerability",
                "severity": "high",
                "line": "unknown",
                "message": "Use of eval() function",
                "suggestion": "Avoid eval() as it can execute arbitrary code; use safer alternatives"
            })

        # Check for exec usage
        if 'exec(' in code:
            security_issues.append({
                "type": "security_vulnerability",
                "severity": "high",
                "line": "unknown",
                "message": "Use of exec() function",
                "suggestion": "Avoid exec() as it can execute arbitrary code; use safer alternatives"
            })

        # Check for SQL injection vulnerabilities
        if re.search(r'(\.execute|\.query)\s*\(\s*.*\+.*\)', code):
            security_issues.append({
                "type": "security_vulnerability",
                "severity": "high",
                "line": "unknown",
                "message": "Potential SQL injection vulnerability",
                "suggestion": "Use parameterized queries instead of string concatenation"
            })

        # Check for hardcoded secrets
        secret_patterns = [
            r'password\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']',
            r'key\s*=\s*["\'][^"\']+["\']',
            r'token\s*=\s*["\'][^"\']+["\']'
        ]

        for pattern in secret_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                security_issues.append({
                    "type": "security_vulnerability",
                    "severity": "high",
                    "line": "unknown",
                    "message": "Hardcoded secrets detected",
                    "suggestion": "Use environment variables or secure credential storage"
                })
                break

        return security_issues

    def _check_performance_issues(self, code: str) -> List[Dict[str, Any]]:
        """Check for performance issues"""
        performance_issues = []

        # Check for inefficient list operations
        if re.search(r'for\s+\w+\s+in\s+.*range\(len\(.*\)\)', code):
            performance_issues.append({
                "type": "performance_issue",
                "severity": "medium",
                "line": "unknown",
                "message": "Inefficient iteration over list with index",
                "suggestion": "Use enumerate() or iterate directly over the list"
            })

        # Check for string concatenation in loops
        if re.search(r'for\s+.*:\s*.*\+=', code):
            performance_issues.append({
                "type": "performance_issue",
                "severity": "medium",
                "line": "unknown",
                "message": "String concatenation in loop",
                "suggestion": "Use list comprehension and join() for better performance"
            })

        return performance_issues

    def _generate_improvement_suggestions(self, code: str) -> List[Dict[str, Any]]:
        """Generate improvement suggestions"""
        suggestions = []

        # Check for missing docstrings
        functions = re.findall(r'^\s*def\s+(\w+)', code, re.MULTILINE)
        for func in functions:
            # Look for docstring after function definition
            func_pattern = rf'^\s*def\s+{re.escape(func)}\s*\([^)]*\)\s*:\s*(.*?)(?=\n\s*def|\n\s*class|\n\s*$)'
            match = re.search(func_pattern, code, re.DOTALL | re.MULTILINE)
            if match:
                func_body = match.group(1)
                if not re.search(r'""".*"""', func_body, re.DOTALL):
                    suggestions.append({
                        "type": "improvement",
                        "category": "documentation",
                        "message": f"Add docstring to function {func}",
                        "suggestion": 'Add a docstring explaining the function\'s purpose, parameters, and return value'
                    })

        # Check for type hints
        if not re.search(r'->\s*\w+', code):  # No return type hints
            suggestions.append({
                "type": "improvement",
                "category": "type_hints",
                "message": "Consider adding type hints",
                "suggestion": "Add type hints to function parameters and return values for better code clarity"
            })

        return suggestions

    def _calculate_maintainability_score(self, review_results: Dict[str, Any]) -> float:
        """Calculate maintainability score (0-100)"""
        base_score = 100

        # Deduct points for issues
        issues = review_results["issues"]
        warnings = review_results["warnings"]
        security_issues = review_results["security_issues"]
        performance_issues = review_results["performance_issues"]

        # Weight the deductions
        base_score -= len(issues) * 10  # High severity
        base_score -= len(security_issues) * 15  # Critical
        base_score -= len(performance_issues) * 8  # Medium severity
        base_score -= len(warnings) * 3  # Low severity

        # Factor in complexity
        complexity = review_results["metrics"].get("complexity", 1)
        if complexity > 10:
            base_score -= (complexity - 10) * 2

        # Factor in documentation
        comment_ratio = review_results["metrics"].get("comment_lines", 0) / max(1, review_results["metrics"].get("code_lines", 1))
        if comment_ratio < 0.1:
            base_score -= 10

        return max(0, min(100, base_score))

    def _generate_review_report(self, review_results: Dict[str, Any]) -> str:
        """Generate a comprehensive review report"""
        report_lines = []

        report_lines.append("# Code Review Report")
        report_lines.append("")

        # Summary
        report_lines.append("## Summary")
        report_lines.append(f"- **Quality Score**: {review_results['maintainability_score']:.1f}/100")
        report_lines.append(f"- **Issues Found**: {len(review_results['issues'])}")
        report_lines.append(f"- **Warnings**: {len(review_results['warnings'])}")
        report_lines.append(f"- **Security Issues**: {len(review_results['security_issues'])}")
        report_lines.append(f"- **Performance Issues**: {len(review_results['performance_issues'])}")
        report_lines.append("")

        # Code Metrics
        report_lines.append("## Code Metrics")
        metrics = review_results["metrics"]
        report_lines.append(f"- Total Lines: {metrics['total_lines']}")
        report_lines.append(f"- Code Lines: {metrics['code_lines']}")
        report_lines.append(f"- Comment Lines: {metrics['comment_lines']}")
        report_lines.append(f"- Functions: {metrics['functions']}")
        report_lines.append(f"- Classes: {metrics['classes']}")
        report_lines.append(f"- Cyclomatic Complexity: {metrics['complexity']}")
        report_lines.append("")

        # Issues
        if review_results["issues"]:
            report_lines.append("## Issues (High Priority)")
            for issue in review_results["issues"]:
                report_lines.append(f"- **{issue['type']}**: {issue['message']}")
                report_lines.append(f"  - Severity: {issue['severity']}")
                report_lines.append(f"  - Suggestion: {issue['suggestion']}")
            report_lines.append("")

        # Security Issues
        if review_results["security_issues"]:
            report_lines.append("## Security Issues (Critical)")
            for issue in review_results["security_issues"]:
                report_lines.append(f"- **{issue['type']}**: {issue['message']}")
                report_lines.append(f"  - Severity: {issue['severity']}")
                report_lines.append(f"  - Suggestion: {issue['suggestion']}")
            report_lines.append("")

        # Warnings
        if review_results["warnings"]:
            report_lines.append("## Warnings (Medium Priority)")
            for warning in review_results["warnings"]:
                report_lines.append(f"- **{warning['type']}**: {warning['message']}")
                report_lines.append(f"  - Severity: {warning['severity']}")
                report_lines.append(f"  - Suggestion: {warning['suggestion']}")
            report_lines.append("")

        # Performance Issues
        if review_results["performance_issues"]:
            report_lines.append("## Performance Issues")
            for issue in review_results["performance_issues"]:
                report_lines.append(f"- **{issue['type']}**: {issue['message']}")
                report_lines.append(f"  - Severity: {issue['severity']}")
                report_lines.append(f"  - Suggestion: {issue['suggestion']}")
            report_lines.append("")

        return "\n".join(report_lines)

    def _calculate_quality_score(self, review_results: Dict[str, Any]) -> float:
        """Calculate overall quality score"""
        return review_results["maintainability_score"]

    def _generate_recommendations(self, review_results: Dict[str, Any]) -> List[str]:
        """Generate prioritized recommendations"""
        recommendations = []

        # Add suggestions from review results
        for suggestion in review_results["suggestions"]:
            recommendations.append(suggestion["suggestion"])

        # Add general recommendations based on score
        score = review_results["maintainability_score"]
        if score < 50:
            recommendations.append("Major refactoring recommended - consider breaking down complex functions and improving error handling")
        elif score < 70:
            recommendations.append("Moderate improvements needed - focus on code documentation and style consistency")
        elif score < 85:
            recommendations.append("Minor improvements suggested - consider adding type hints and optimizing performance")

        return recommendations

    def _handle_error(self, error_message: str) -> Dict[str, Any]:
        """Handle errors during code review"""
        self._log_activity("review_error", {"error": error_message})
        self._publish_status("error", {"message": error_message})

        return {
            "action": "error",
            "output": f"Code review failed: {error_message}",
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
        """Validate code review result"""
        if not super().validate_result(result):
            return False

        output = result.get("output", {})
        return isinstance(output, dict) and "report" in output

    def cleanup(self):
        """Cleanup resources"""
        self._publish_status("cleanup", {"agent": self.agent_name})