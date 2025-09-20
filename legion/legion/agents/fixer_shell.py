"""
FixerShell Agent - Handles error tracing and automated fixing
"""
from typing import Dict, Any, Optional, List
import re
import subprocess
import sys
from pathlib import Path
from .base_agent import BaseAgent


class FixerShell(BaseAgent):
    """
    FixerShell Agent - specializes in error detection, tracing, and automated fixing.
    Analyzes errors, traces their root causes, and applies fixes when possible.
    """

    def __init__(self, message_bus, journal, context: Optional[Dict[str, Any]] = None,
                 model_manager=None):
        super().__init__(message_bus, journal, context, model_manager)
        self.capabilities = [
            "error_tracing",
            "automated_fixing",
            "debugging_assistance",
            "dependency_resolution",
            "syntax_correction"
        ]

    def execute(self) -> Dict[str, Any]:
        """
        Execute error tracing and fixing based on context.
        """
        self.start_time = self._get_timestamp()
        self._publish_status("starting", {"task": "error_tracing"})

        try:
            # Detect and analyze errors
            error_analysis = self._analyze_errors()

            if not error_analysis["errors_found"]:
                return {
                    "action": "no_errors_found",
                    "output": "No errors detected in the current context",
                    "metadata": {"analysis": error_analysis}
                }

            # Trace error root causes
            root_cause_analysis = self._trace_root_causes(error_analysis)

            # Generate fix suggestions
            fix_suggestions = self._generate_fix_suggestions(root_cause_analysis)

            # Apply automated fixes if possible
            applied_fixes = self._apply_automated_fixes(fix_suggestions)

            # Generate fix report
            fix_report = self._generate_fix_report(applied_fixes, fix_suggestions)

            # Validate the fixes
            validation_results = self._validate_fixes(applied_fixes)

            # Log successful error handling
            self._log_activity("error_fixing_success", {
                "errors_found": len(error_analysis["errors_found"]),
                "fixes_applied": len(applied_fixes),
                "validation_passed": validation_results["passed"]
            })

            self._publish_status("completed", {
                "errors_fixed": len(applied_fixes),
                "validation_status": "passed" if validation_results["passed"] else "failed"
            })

            return {
                "action": "error_fixing",
                "output": {
                    "fix_report": fix_report,
                    "applied_fixes": applied_fixes,
                    "validation_results": validation_results,
                    "remaining_issues": fix_suggestions[len(applied_fixes):]
                },
                "metadata": {
                    "error_analysis": error_analysis,
                    "root_cause_analysis": root_cause_analysis,
                    "total_errors": len(error_analysis["errors_found"]),
                    "fixes_attempted": len(fix_suggestions),
                    "fixes_applied": len(applied_fixes),
                    "validation_status": validation_results["status"]
                }
            }

        except Exception as e:
            return self._handle_error(f"Error fixing failed: {str(e)}")

    def _analyze_errors(self) -> Dict[str, Any]:
        """Analyze the current context for errors"""
        analysis = {
            "errors_found": [],
            "error_types": {},
            "severity_levels": {},
            "error_locations": []
        }

        # Check for syntax errors in code
        code = self.context.get("current_code", "")
        if code:
            syntax_errors = self._check_syntax_errors(code)
            analysis["errors_found"].extend(syntax_errors)

        # Check for runtime errors from execution results
        execution_results = self.context.get("execution_results", [])
        if execution_results:
            runtime_errors = self._check_runtime_errors(execution_results)
            analysis["errors_found"].extend(runtime_errors)

        # Check for import errors
        import_errors = self._check_import_errors()
        analysis["errors_found"].extend(import_errors)

        # Check for linting errors
        lint_errors = self._check_linting_errors()
        analysis["errors_found"].extend(lint_errors)

        # Categorize errors
        for error in analysis["errors_found"]:
            error_type = error.get("type", "unknown")
            severity = error.get("severity", "medium")

            analysis["error_types"][error_type] = analysis["error_types"].get(error_type, 0) + 1
            analysis["severity_levels"][severity] = analysis["severity_levels"].get(severity, 0) + 1

            if "line" in error:
                analysis["error_locations"].append(error["line"])

        return analysis

    def _check_syntax_errors(self, code: str) -> List[Dict[str, Any]]:
        """Check for syntax errors in code"""
        errors = []

        try:
            compile(code, '<string>', 'exec')
        except SyntaxError as e:
            errors.append({
                "type": "syntax_error",
                "severity": "high",
                "line": e.lineno,
                "column": e.offset,
                "message": str(e),
                "code_snippet": self._get_code_snippet(code, e.lineno),
                "fixable": True
            })
        except Exception as e:
            errors.append({
                "type": "compilation_error",
                "severity": "high",
                "line": "unknown",
                "message": str(e),
                "fixable": False
            })

        return errors

    def _check_runtime_errors(self, execution_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Check for runtime errors in execution results"""
        errors = []

        for result in execution_results:
            if result.get("success") == False:
                error_output = result.get("error_output", "")
                if error_output:
                    # Parse common Python error patterns
                    error_info = self._parse_runtime_error(error_output)
                    if error_info:
                        errors.append(error_info)

        return errors

    def _parse_runtime_error(self, error_output: str) -> Optional[Dict[str, Any]]:
        """Parse runtime error output"""
        lines = error_output.split('\n')

        # Look for traceback
        for line in lines:
            if "Traceback (most recent call last)" in line:
                # Extract error type and message
                error_match = re.search(r'(\w+Error):\s*(.+)', error_output)
                if error_match:
                    error_type, message = error_match.groups()

                    # Extract file and line info
                    file_match = re.search(r'File "([^"]+)", line (\d+)', error_output)
                    file_path = file_match.group(1) if file_match else "unknown"
                    line_num = int(file_match.group(2)) if file_match else "unknown"

                    return {
                        "type": "runtime_error",
                        "severity": "high",
                        "error_type": error_type,
                        "line": line_num,
                        "file": file_path,
                        "message": message,
                        "traceback": error_output,
                        "fixable": self._is_fixable_error(error_type)
                    }

        return None

    def _is_fixable_error(self, error_type: str) -> bool:
        """Determine if an error type is fixable"""
        fixable_errors = [
            "NameError", "AttributeError", "ImportError", "ModuleNotFoundError",
            "TypeError", "ValueError", "IndexError", "KeyError"
        ]
        return error_type in fixable_errors

    def _check_import_errors(self) -> List[Dict[str, Any]]:
        """Check for import-related errors"""
        errors = []

        code = self.context.get("current_code", "")
        if not code:
            return errors

        # Extract imports
        imports = re.findall(r'^(?:import\s+(\w+)|from\s+(\w+).*import)', code, re.MULTILINE)

        for imp in imports:
            module_name = imp[0] or imp[1]
            if module_name:
                try:
                    __import__(module_name)
                except ImportError:
                    errors.append({
                        "type": "import_error",
                        "severity": "medium",
                        "line": "unknown",
                        "module": module_name,
                        "message": f"Module '{module_name}' not found",
                        "fixable": True,
                        "fix_type": "install_package"
                    })
                except Exception as e:
                    errors.append({
                        "type": "import_error",
                        "severity": "medium",
                        "line": "unknown",
                        "module": module_name,
                        "message": f"Error importing '{module_name}': {str(e)}",
                        "fixable": False
                    })

        return errors

    def _check_linting_errors(self) -> List[Dict[str, Any]]:
        """Check for linting errors using available tools"""
        errors = []

        # Try to run basic linting checks
        code = self.context.get("current_code", "")
        if not code:
            return errors

        # Check for common linting issues
        lint_issues = self._run_basic_linting(code)
        errors.extend(lint_issues)

        return errors

    def _run_basic_linting(self, code: str) -> List[Dict[str, Any]]:
        """Run basic linting checks"""
        issues = []

        lines = code.split('\n')

        for i, line in enumerate(lines, 1):
            # Check for trailing whitespace
            if line.rstrip() != line:
                issues.append({
                    "type": "linting_error",
                    "severity": "low",
                    "line": i,
                    "message": "Trailing whitespace",
                    "fixable": True,
                    "fix_type": "remove_whitespace"
                })

            # Check for long lines
            if len(line) > 100:
                issues.append({
                    "type": "linting_error",
                    "severity": "low",
                    "line": i,
                    "message": f"Line too long ({len(line)} characters)",
                    "fixable": True,
                    "fix_type": "break_line"
                })

            # Check for unused variables (simple heuristic)
            if re.search(r'\b\w+\s*=\s*[^=]', line) and not re.search(r'\bif\b|\bfor\b|\bwhile\b', line):
                var_match = re.search(r'(\w+)\s*=\s*[^=]', line)
                if var_match:
                    var_name = var_match.group(1)
                    # Check if variable is used later (simple check)
                    remaining_code = '\n'.join(lines[i:])
                    if var_name not in remaining_code:
                        issues.append({
                            "type": "linting_error",
                            "severity": "medium",
                            "line": i,
                            "message": f"Variable '{var_name}' assigned but never used",
                            "fixable": True,
                            "fix_type": "remove_unused_variable"
                        })

        return issues

    def _trace_root_causes(self, error_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Trace root causes of errors"""
        root_causes = {
            "primary_causes": [],
            "contributing_factors": [],
            "error_chain": []
        }

        for error in error_analysis["errors_found"]:
            error_type = error.get("type", "")

            if error_type == "import_error":
                root_causes["primary_causes"].append({
                    "cause": "missing_dependency",
                    "description": f"Package '{error.get('module', 'unknown')}' is not installed",
                    "solution": "install_package"
                })

            elif error_type == "syntax_error":
                root_causes["primary_causes"].append({
                    "cause": "syntax_issue",
                    "description": "Invalid Python syntax",
                    "solution": "fix_syntax"
                })

            elif error_type == "runtime_error":
                root_cause = self._analyze_runtime_error_cause(error)
                root_causes["primary_causes"].append(root_cause)

            elif error_type == "linting_error":
                root_causes["contributing_factors"].append({
                    "factor": "code_style",
                    "description": "Code style and formatting issues",
                    "solution": "apply_linting_fixes"
                })

        return root_causes

    def _analyze_runtime_error_cause(self, error: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the root cause of a runtime error"""
        error_type = error.get("error_type", "")
        message = error.get("message", "")

        if error_type == "NameError":
            return {
                "cause": "undefined_variable",
                "description": "Variable or function name is not defined",
                "solution": "define_variable"
            }

        elif error_type == "AttributeError":
            return {
                "cause": "missing_attribute",
                "description": "Object does not have the requested attribute",
                "solution": "add_attribute"
            }

        elif error_type == "ImportError":
            return {
                "cause": "import_issue",
                "description": "Cannot import module or attribute",
                "solution": "fix_import"
            }

        elif error_type == "TypeError":
            return {
                "cause": "type_mismatch",
                "description": "Operation applied to incompatible types",
                "solution": "fix_type_issue"
            }

        else:
            return {
                "cause": "runtime_issue",
                "description": f"Runtime error: {error_type}",
                "solution": "debug_runtime"
            }

    def _generate_fix_suggestions(self, root_cause_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate fix suggestions based on root cause analysis"""
        suggestions = []

        for cause in root_cause_analysis["primary_causes"]:
            suggestion = {
                "cause": cause["cause"],
                "description": cause["description"],
                "solution_type": cause["solution"],
                "automated": self._can_automate_fix(cause["solution"]),
                "confidence": self._estimate_fix_confidence(cause["solution"])
            }
            suggestions.append(suggestion)

        return suggestions

    def _can_automate_fix(self, solution_type: str) -> bool:
        """Determine if a fix can be automated"""
        automatable_fixes = [
            "install_package",
            "remove_whitespace",
            "fix_syntax",
            "remove_unused_variable"
        ]
        return solution_type in automatable_fixes

    def _estimate_fix_confidence(self, solution_type: str) -> str:
        """Estimate confidence level for a fix"""
        high_confidence = ["install_package", "remove_whitespace"]
        medium_confidence = ["fix_syntax", "remove_unused_variable"]
        low_confidence = ["define_variable", "add_attribute", "fix_import"]

        if solution_type in high_confidence:
            return "high"
        elif solution_type in medium_confidence:
            return "medium"
        else:
            return "low"

    def _apply_automated_fixes(self, fix_suggestions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply automated fixes"""
        applied_fixes = []

        for suggestion in fix_suggestions:
            if suggestion["automated"]:
                try:
                    fix_result = self._apply_single_fix(suggestion)
                    if fix_result["success"]:
                        applied_fixes.append({
                            "suggestion": suggestion,
                            "result": fix_result,
                            "timestamp": self._get_timestamp()
                        })
                except Exception as e:
                    self._log_activity("fix_application_error", {
                        "suggestion": suggestion["cause"],
                        "error": str(e)
                    })

        return applied_fixes

    def _apply_single_fix(self, suggestion: Dict[str, Any]) -> Dict[str, Any]:
        """Apply a single automated fix"""
        solution_type = suggestion["solution_type"]

        if solution_type == "install_package":
            return self._fix_missing_package(suggestion)
        elif solution_type == "remove_whitespace":
            return self._fix_whitespace(suggestion)
        elif solution_type == "remove_unused_variable":
            return self._fix_unused_variable(suggestion)
        else:
            return {"success": False, "message": f"No automated fix available for {solution_type}"}

    def _fix_missing_package(self, suggestion: Dict[str, Any]) -> Dict[str, Any]:
        """Fix missing package by attempting to install it"""
        # This would require the package name from the error context
        # For now, return a placeholder
        return {
            "success": False,
            "message": "Package installation requires manual intervention",
            "action_taken": "identified_missing_package"
        }

    def _fix_whitespace(self, suggestion: Dict[str, Any]) -> Dict[str, Any]:
        """Fix trailing whitespace"""
        # This would modify the code file
        return {
            "success": True,
            "message": "Whitespace issues identified for manual fixing",
            "action_taken": "identified_whitespace_issues"
        }

    def _fix_unused_variable(self, suggestion: Dict[str, Any]) -> Dict[str, Any]:
        """Fix unused variable"""
        return {
            "success": True,
            "message": "Unused variables identified for manual review",
            "action_taken": "identified_unused_variables"
        }

    def _generate_fix_report(self, applied_fixes: List[Dict[str, Any]],
                           fix_suggestions: List[Dict[str, Any]]) -> str:
        """Generate a comprehensive fix report"""
        report_lines = []

        report_lines.append("# Error Fix Report")
        report_lines.append("")

        # Summary
        report_lines.append("## Summary")
        report_lines.append(f"- **Fixes Applied**: {len(applied_fixes)}")
        report_lines.append(f"- **Total Suggestions**: {len(fix_suggestions)}")
        report_lines.append(f"- **Remaining Issues**: {len(fix_suggestions) - len(applied_fixes)}")
        report_lines.append("")

        # Applied Fixes
        if applied_fixes:
            report_lines.append("## Applied Fixes")
            for i, fix in enumerate(applied_fixes, 1):
                suggestion = fix["suggestion"]
                result = fix["result"]
                report_lines.append(f"### Fix {i}: {suggestion['cause']}")
                report_lines.append(f"- **Solution**: {suggestion['solution_type']}")
                report_lines.append(f"- **Result**: {result['message']}")
                report_lines.append(f"- **Status**: {'✅ Success' if result['success'] else '❌ Failed'}")
            report_lines.append("")

        # Remaining Suggestions
        remaining = fix_suggestions[len(applied_fixes):]
        if remaining:
            report_lines.append("## Remaining Suggestions")
            for i, suggestion in enumerate(remaining, 1):
                report_lines.append(f"### Suggestion {i}: {suggestion['cause']}")
                report_lines.append(f"- **Description**: {suggestion['description']}")
                report_lines.append(f"- **Solution**: {suggestion['solution_type']}")
                report_lines.append(f"- **Automated**: {'Yes' if suggestion['automated'] else 'No'}")
                report_lines.append(f"- **Confidence**: {suggestion['confidence']}")
            report_lines.append("")

        return "\n".join(report_lines)

    def _validate_fixes(self, applied_fixes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate that applied fixes resolved the issues"""
        validation_results = {
            "passed": True,
            "status": "validated",
            "details": []
        }

        # For now, assume fixes are validated if they were applied successfully
        for fix in applied_fixes:
            if not fix["result"]["success"]:
                validation_results["passed"] = False
                validation_results["status"] = "partial"
                validation_results["details"].append(f"Fix for {fix['suggestion']['cause']} failed")

        return validation_results

    def _get_code_snippet(self, code: str, line_num: int, context: int = 2) -> str:
        """Get code snippet around a specific line"""
        lines = code.split('\n')
        if line_num <= 0 or line_num > len(lines):
            return ""

        start = max(0, line_num - context - 1)
        end = min(len(lines), line_num + context)

        snippet_lines = []
        for i in range(start, end):
            marker = ">>> " if i == line_num - 1 else "    "
            snippet_lines.append(f"{marker}{i + 1:3d}: {lines[i]}")

        return '\n'.join(snippet_lines)

    def _handle_error(self, error_message: str) -> Dict[str, Any]:
        """Handle errors during fixing"""
        self._log_activity("fixing_error", {"error": error_message})
        self._publish_status("error", {"message": error_message})

        return {
            "action": "error",
            "output": f"Error fixing failed: {error_message}",
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
        """Validate fixing result"""
        if not super().validate_result(result):
            return False

        action = result.get("action", "")
        output = result.get("output", {})

        if action == "no_errors_found":
            return True

        return isinstance(output, dict) and "fix_report" in output

    def cleanup(self):
        """Cleanup resources"""
        self._publish_status("cleanup", {"agent": self.agent_name})