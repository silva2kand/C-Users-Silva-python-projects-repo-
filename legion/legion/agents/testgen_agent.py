"""
TestGen Agent - Generates unit tests for code
"""
from typing import Dict, Any, Optional, List
import re
from .base_agent import BaseAgent


class TestGenAgent(BaseAgent):
    """
    TestGen Agent - specializes in generating comprehensive unit tests.
    Analyzes code and generates test cases covering various scenarios.
    """

    def __init__(self, message_bus, journal, context: Optional[Dict[str, Any]] = None,
                 model_manager=None):
        super().__init__(message_bus, journal, context, model_manager)
        self.capabilities = [
            "unit_test_generation",
            "test_case_design",
            "mock_generation",
            "edge_case_testing",
            "integration_test_setup"
        ]

    def execute(self) -> Dict[str, Any]:
        """
        Generate comprehensive unit tests for the given code.
        """
        self.start_time = self._get_timestamp()
        self._publish_status("starting", {"task": "test_generation"})

        try:
            # Analyze the code to understand what needs testing
            code_analysis = self._analyze_code_for_testing()

            if not code_analysis["testable_elements"]:
                return {
                    "action": "no_tests_needed",
                    "output": "No testable functions or classes found in the code",
                    "metadata": {"analysis": code_analysis}
                }

            # Generate test cases
            test_cases = self._generate_test_cases(code_analysis)

            # Generate test file content
            test_content = self._generate_test_file(test_cases, code_analysis)

            # Generate test configuration if needed
            test_config = self._generate_test_config(code_analysis)

            # Validate the generated tests
            if not self.validate_result({"action": "generate_tests", "output": test_content}):
                return self._handle_error("Generated tests failed validation")

            # Log successful test generation
            self._log_activity("test_generation_success", {
                "test_cases": len(test_cases),
                "testable_elements": len(code_analysis["testable_elements"])
            })

            self._publish_status("completed", {
                "test_cases": len(test_cases),
                "testable_elements": len(code_analysis["testable_elements"])
            })

            return {
                "action": "generate_tests",
                "output": {
                    "test_file": test_content,
                    "test_config": test_config,
                    "test_cases": test_cases
                },
                "metadata": {
                    "analysis": code_analysis,
                    "test_framework": "pytest",  # Default framework
                    "test_cases_count": len(test_cases),
                    "coverage_estimate": self._estimate_coverage(test_cases, code_analysis)
                }
            }

        except Exception as e:
            return self._handle_error(f"Test generation failed: {str(e)}")

    def _analyze_code_for_testing(self) -> Dict[str, Any]:
        """Analyze code to identify testable elements"""
        code = self.context.get("current_code", "")
        file_path = self.context.get("current_file", "")

        analysis = {
            "testable_elements": [],
            "dependencies": [],
            "imports": [],
            "language": self._detect_language(),
            "framework_suggestions": []
        }

        if not code:
            return analysis

        # Extract functions
        functions = self._extract_functions(code)
        analysis["testable_elements"].extend(functions)

        # Extract classes
        classes = self._extract_classes(code)
        analysis["testable_elements"].extend(classes)

        # Extract imports and dependencies
        analysis["imports"] = self._extract_imports(code)
        analysis["dependencies"] = self._identify_dependencies(code)

        # Suggest test frameworks
        analysis["framework_suggestions"] = self._suggest_test_frameworks(analysis["language"])

        return analysis

    def _extract_functions(self, code: str) -> List[Dict[str, Any]]:
        """Extract function definitions for testing"""
        functions = []

        # Find all function definitions
        func_pattern = r'^\s*def\s+(\w+)\s*\(([^)]*)\)\s*:(.*?)(?=\n\s*def|\n\s*class|\n\s*@|\n\s*$)'
        matches = re.finditer(func_pattern, code, re.DOTALL | re.MULTILINE)

        for match in matches:
            func_name = match.group(1)
            params = match.group(2)
            body = match.group(3)

            # Parse parameters
            param_list = self._parse_parameters(params)

            # Analyze function characteristics
            characteristics = self._analyze_function_characteristics(body)

            functions.append({
                "type": "function",
                "name": func_name,
                "parameters": param_list,
                "characteristics": characteristics,
                "body_lines": len(body.split('\n')),
                "complexity": self._estimate_complexity(body)
            })

        return functions

    def _extract_classes(self, code: str) -> List[Dict[str, Any]]:
        """Extract class definitions for testing"""
        classes = []

        # Find all class definitions
        class_pattern = r'^\s*class\s+(\w+).*?:(.*?)(?=\n\s*class|\n\s*$)'
        matches = re.finditer(class_pattern, code, re.DOTALL | re.MULTILINE)

        for match in matches:
            class_name = match.group(1)
            class_body = match.group(2)

            # Extract methods
            methods = self._extract_functions(class_body)
            for method in methods:
                method["class_name"] = class_name

            # Extract attributes
            attributes = self._extract_attributes(class_body)

            classes.append({
                "type": "class",
                "name": class_name,
                "methods": methods,
                "attributes": attributes,
                "body_lines": len(class_body.split('\n'))
            })

        return classes

    def _parse_parameters(self, params_str: str) -> List[Dict[str, Any]]:
        """Parse function parameters"""
        parameters = []

        if not params_str.strip() or params_str.strip() == "self":
            return parameters

        # Remove 'self' for instance methods
        params_str = params_str.replace("self,", "").replace("self", "")

        # Split parameters
        param_list = [p.strip() for p in params_str.split(',') if p.strip()]

        for param in param_list:
            # Handle type hints
            if ':' in param:
                name, type_hint = param.split(':', 1)
                name = name.strip()
                type_hint = type_hint.strip()
            else:
                name = param
                type_hint = "Any"

            # Handle default values
            if '=' in name:
                name, default = name.split('=', 1)
                name = name.strip()
                default = default.strip()
            else:
                default = None

            parameters.append({
                "name": name,
                "type_hint": type_hint,
                "default_value": default
            })

        return parameters

    def _analyze_function_characteristics(self, body: str) -> Dict[str, Any]:
        """Analyze function characteristics for test generation"""
        characteristics = {
            "has_return": "return" in body,
            "has_exceptions": "raise" in body or "except" in body,
            "uses_input": "input(" in body,
            "uses_random": "random" in body,
            "uses_time": "time" in body or "datetime" in body,
            "has_side_effects": self._detect_side_effects(body),
            "branches": len(re.findall(r'\b(if|elif|for|while)\b', body)),
            "external_calls": len(re.findall(r'\w+\([^)]*\)', body))
        }

        return characteristics

    def _detect_side_effects(self, body: str) -> bool:
        """Detect if function has side effects"""
        side_effect_indicators = [
            "print(",
            "write(",
            "save(",
            "delete(",
            "update(",
            "create(",
            ".append(",
            ".extend(",
            ".remove(",
            ".pop(",
            "global ",
            "nonlocal "
        ]

        return any(indicator in body for indicator in side_effect_indicators)

    def _extract_attributes(self, class_body: str) -> List[str]:
        """Extract class attributes"""
        attributes = []

        # Look for self.attribute assignments
        attr_pattern = r'self\.(\w+)\s*='
        matches = re.findall(attr_pattern, class_body)

        attributes = list(set(matches))  # Remove duplicates

        return attributes

    def _extract_imports(self, code: str) -> List[str]:
        """Extract import statements"""
        imports = []
        lines = code.split('\n')

        for line in lines:
            line = line.strip()
            if line.startswith('import ') or line.startswith('from '):
                imports.append(line)

        return imports

    def _identify_dependencies(self, code: str) -> List[str]:
        """Identify external dependencies"""
        dependencies = []

        # Look for common library usage patterns
        if 'requests' in code:
            dependencies.append('requests')
        if 'pandas' in code or 'pd.' in code:
            dependencies.append('pandas')
        if 'numpy' in code or 'np.' in code:
            dependencies.append('numpy')
        if 'os.' in code:
            dependencies.append('os')
        if 'json.' in code:
            dependencies.append('json')

        return list(set(dependencies))

    def _suggest_test_frameworks(self, language: str) -> List[str]:
        """Suggest appropriate test frameworks"""
        if language == "python":
            return ["pytest", "unittest", "nose2"]
        elif language == "javascript":
            return ["jest", "mocha", "jasmine"]
        else:
            return ["general_unit_testing"]

    def _estimate_complexity(self, body: str) -> str:
        """Estimate function complexity"""
        lines = len(body.split('\n'))
        branches = len(re.findall(r'\b(if|elif|for|while)\b', body))

        if lines > 50 or branches > 10:
            return "high"
        elif lines > 20 or branches > 5:
            return "medium"
        else:
            return "low"

    def _generate_test_cases(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate comprehensive test cases"""
        test_cases = []

        for element in analysis["testable_elements"]:
            if element["type"] == "function":
                test_cases.extend(self._generate_function_tests(element))
            elif element["type"] == "class":
                test_cases.extend(self._generate_class_tests(element))

        return test_cases

    def _generate_function_tests(self, func_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate test cases for a function"""
        test_cases = []

        func_name = func_info["name"]
        parameters = func_info["parameters"]
        characteristics = func_info["characteristics"]

        # Basic functionality test
        test_cases.append({
            "type": "function_test",
            "function": func_name,
            "test_name": f"test_{func_name}_basic",
            "description": f"Test basic functionality of {func_name}",
            "test_type": "happy_path",
            "parameters": self._generate_test_parameters(parameters),
            "expected_result": "expected_output",
            "mocks": self._generate_mocks(characteristics)
        })

        # Edge cases
        if characteristics["branches"] > 0:
            test_cases.append({
                "type": "function_test",
                "function": func_name,
                "test_name": f"test_{func_name}_edge_cases",
                "description": f"Test edge cases for {func_name}",
                "test_type": "edge_case",
                "parameters": self._generate_edge_parameters(parameters),
                "expected_result": "expected_edge_output",
                "mocks": self._generate_mocks(characteristics)
            })

        # Error handling
        if characteristics["has_exceptions"]:
            test_cases.append({
                "type": "function_test",
                "function": func_name,
                "test_name": f"test_{func_name}_error_handling",
                "description": f"Test error handling in {func_name}",
                "test_type": "error_case",
                "parameters": self._generate_error_parameters(parameters),
                "expected_exception": "ExpectedException",
                "mocks": self._generate_mocks(characteristics)
            })

        return test_cases

    def _generate_class_tests(self, class_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate test cases for a class"""
        test_cases = []

        class_name = class_info["name"]
        methods = class_info["methods"]

        # Constructor test
        test_cases.append({
            "type": "class_test",
            "class": class_name,
            "test_name": f"test_{class_name}_init",
            "description": f"Test {class_name} initialization",
            "test_type": "constructor",
            "setup": f"instance = {class_name}()",
            "assertions": ["assert instance is not None"]
        })

        # Method tests
        for method in methods:
            if method["name"] != "__init__":
                test_cases.extend(self._generate_function_tests(method))

        return test_cases

    def _generate_test_parameters(self, parameters: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate test parameters for function calls"""
        test_params = {}

        for param in parameters:
            param_name = param["name"]
            type_hint = param["type_hint"]

            # Generate appropriate test values based on type hints
            if "str" in type_hint.lower():
                test_params[param_name] = '"test_string"'
            elif "int" in type_hint.lower():
                test_params[param_name] = "42"
            elif "bool" in type_hint.lower():
                test_params[param_name] = "True"
            elif "list" in type_hint.lower():
                test_params[param_name] = "[1, 2, 3]"
            elif "dict" in type_hint.lower():
                test_params[param_name] = '{"key": "value"}'
            else:
                test_params[param_name] = '"test_value"'

        return test_params

    def _generate_edge_parameters(self, parameters: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate edge case parameters"""
        edge_params = {}

        for param in parameters:
            param_name = param["name"]
            type_hint = param["type_hint"]

            # Generate edge case values
            if "str" in type_hint.lower():
                edge_params[param_name] = '""'  # Empty string
            elif "int" in type_hint.lower():
                edge_params[param_name] = "0"  # Zero
            elif "list" in type_hint.lower():
                edge_params[param_name] = "[]"  # Empty list
            else:
                edge_params[param_name] = "None"

        return edge_params

    def _generate_error_parameters(self, parameters: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate parameters that should cause errors"""
        error_params = {}

        for param in parameters:
            param_name = param["name"]
            error_params[param_name] = "None"  # None often causes errors

        return error_params

    def _generate_mocks(self, characteristics: Dict[str, Any]) -> List[str]:
        """Generate mock objects for external dependencies"""
        mocks = []

        if characteristics["uses_random"]:
            mocks.append("mock.patch('random.random', return_value=0.5)")
        if characteristics["uses_time"]:
            mocks.append("mock.patch('time.time', return_value=1234567890)")
        if "requests" in str(characteristics):
            mocks.append("mock.patch('requests.get')")

        return mocks

    def _generate_test_file(self, test_cases: List[Dict[str, Any]],
                           analysis: Dict[str, Any]) -> str:
        """Generate the complete test file content"""
        language = analysis["language"]
        imports = analysis["imports"]
        dependencies = analysis["dependencies"]

        # Generate imports
        import_section = self._generate_test_imports(language, dependencies)

        # Generate test class/functions
        test_content = self._generate_test_content(test_cases, language)

        # Combine everything
        test_file = f'''"""
Generated unit tests
"""
{import_section}

{test_content}
'''

        return test_file

    def _generate_test_imports(self, language: str, dependencies: List[str]) -> str:
        """Generate import statements for the test file"""
        imports = []

        if language == "python":
            imports.append("import pytest")
            imports.append("from unittest import mock")

            # Import the module being tested
            imports.append("# from your_module import *  # Replace with actual imports")

            # Add dependency imports
            for dep in dependencies:
                if dep in ["os", "json", "sys"]:
                    imports.append(f"import {dep}")
                elif dep == "requests":
                    imports.append("import requests")

        return "\n".join(imports)

    def _generate_test_content(self, test_cases: List[Dict[str, Any]], language: str) -> str:
        """Generate the actual test functions/classes"""
        test_functions = []

        for test_case in test_cases:
            if test_case["type"] == "function_test":
                test_functions.append(self._generate_function_test_case(test_case))
            elif test_case["type"] == "class_test":
                test_functions.append(self._generate_class_test_case(test_case))

        return "\n\n".join(test_functions)

    def _generate_function_test_case(self, test_case: Dict[str, Any]) -> str:
        """Generate a single function test case"""
        func_name = test_case["function"]
        test_name = test_case["test_name"]
        description = test_case["description"]
        parameters = test_case["parameters"]
        mocks = test_case["mocks"]

        # Build parameter string
        param_str = ", ".join(f"{k}={v}" for k, v in parameters.items())

        # Build mock decorators
        mock_decorators = ""
        if mocks:
            mock_decorators = "\n".join(f"@{mock}" for mock in mocks)

        # Build test function
        test_function = f'''{mock_decorators}
def {test_name}():
    """{description}"""
    # Arrange
    {f"result = {func_name}({param_str})" if param_str else f"result = {func_name}()"}

    # Act
    # (Function call is in Arrange for simple cases)

    # Assert
    assert result is not None  # Replace with actual assertions
'''

        return test_function

    def _generate_class_test_case(self, test_case: Dict[str, Any]) -> str:
        """Generate a single class test case"""
        class_name = test_case["class"]
        test_name = test_case["test_name"]
        description = test_case["description"]
        setup = test_case["setup"]
        assertions = test_case["assertions"]

        # Build test function
        test_function = f'''def {test_name}():
    """{description}"""
    # Arrange
    {setup}

    # Act
    # (Setup is the action for constructor tests)

    # Assert
    {"\n    ".join(assertions)}
'''

        return test_function

    def _generate_test_config(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate test configuration"""
        return {
            "framework": "pytest",
            "test_directory": "tests",
            "coverage_target": 80,
            "markers": ["unit", "integration", "slow"],
            "dependencies": analysis["dependencies"]
        }

    def _estimate_coverage(self, test_cases: List[Dict[str, Any]],
                          analysis: Dict[str, Any]) -> float:
        """Estimate test coverage percentage"""
        testable_elements = len(analysis["testable_elements"])
        generated_tests = len(test_cases)

        if testable_elements == 0:
            return 0.0

        # Rough estimation: assume each test covers one element
        coverage = min(100.0, (generated_tests / testable_elements) * 100)

        return round(coverage, 1)

    def _handle_error(self, error_message: str) -> Dict[str, Any]:
        """Handle errors during test generation"""
        self._log_activity("test_generation_error", {"error": error_message})
        self._publish_status("error", {"message": error_message})

        return {
            "action": "error",
            "output": f"Test generation failed: {error_message}",
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
        """Validate test generation result"""
        if not super().validate_result(result):
            return False

        action = result.get("action", "")
        output = result.get("output", "")

        if action == "no_tests_needed":
            return True

        if isinstance(output, dict):
            test_file = output.get("test_file", "")
            return len(test_file.strip()) > 0

        return len(str(output)) > 0

    def cleanup(self):
        """Cleanup resources"""
        self._publish_status("cleanup", {"agent": self.agent_name})