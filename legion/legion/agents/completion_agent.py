"""
Completion Agent - Handles code completion and generation tasks
"""
from typing import Dict, Any, Optional
from .base_agent import BaseAgent


class CompletionAgent(BaseAgent):
    """
    Completion Agent - specializes in code completion, generation, and implementation.
    Uses context from the ContextEngine to provide relevant completions.
    """

    def __init__(self, message_bus, journal, context: Optional[Dict[str, Any]] = None,
                 model_manager=None):
        super().__init__(message_bus, journal, context, model_manager)
        self.capabilities = [
            "code_completion",
            "function_implementation",
            "class_generation",
            "bug_fixes",
            "code_generation"
        ]

    def execute(self) -> Dict[str, Any]:
        """
        Execute code completion based on context and task requirements.
        """
        self.start_time = self._get_timestamp()
        self._publish_status("starting", {"task": "code_completion"})

        try:
            # Analyze the task and context
            task_analysis = self._analyze_task()

            # Generate completion prompt
            prompt = self._build_completion_prompt(task_analysis)

            # Generate completion using model
            self._log_activity("generating_completion", {"prompt_length": len(prompt)})
            response = self._generate_with_model(
                prompt,
                max_tokens=1500,
                temperature=0.3  # Lower temperature for more focused completions
            )

            if "error" in response:
                return self._handle_error(response["error"])

            # Extract and format the completion
            completion = self._extract_code_from_response(response["text"])
            formatted_completion = self._format_completion(completion, task_analysis)

            # Validate the result
            if not self.validate_result({"action": "complete_code", "output": formatted_completion}):
                return self._handle_error("Generated completion failed validation")

            # Log successful completion
            self._log_activity("completion_success", {
                "completion_length": len(formatted_completion),
                "model_used": response.get("provider", "unknown")
            })

            self._publish_status("completed", {
                "completion_length": len(formatted_completion),
                "model": response.get("provider", "unknown")
            })

            return {
                "action": "complete_code",
                "output": formatted_completion,
                "metadata": {
                    "model_used": response.get("provider", "unknown"),
                    "response_time": response.get("response_time", 0),
                    "completion_type": task_analysis["completion_type"],
                    "language": task_analysis["language"]
                }
            }

        except Exception as e:
            return self._handle_error(f"Completion execution failed: {str(e)}")

    def _analyze_task(self) -> Dict[str, Any]:
        """Analyze the task to determine completion requirements"""
        current_code = self.context.get("current_code", "")
        current_file = self.context.get("current_file", "")
        task_description = self.context.get("task_description", "")

        # Determine completion type
        completion_type = "general"
        if "def " in current_code or "function" in current_code:
            completion_type = "function"
        elif "class " in current_code:
            completion_type = "class"
        elif "if " in current_code or "for " in current_code or "while " in current_code:
            completion_type = "block"
        elif "import " in current_code or "from " in current_code:
            completion_type = "import"

        # Detect language
        language = self._detect_language()

        # Get user preferences
        preferences = self._get_user_preferences()

        return {
            "completion_type": completion_type,
            "language": language,
            "current_code": current_code,
            "task_description": task_description,
            "preferences": preferences,
            "related_context": self.context.get("related_code", [])
        }

    def _build_completion_prompt(self, task_analysis: Dict[str, Any]) -> str:
        """Build a sophisticated completion prompt"""
        language = task_analysis["language"]
        completion_type = task_analysis["completion_type"]
        current_code = task_analysis["current_code"]
        task_description = task_analysis["task_description"]
        related_context = task_analysis["related_context"]
        preferences = task_analysis["preferences"]

        # Build context section
        context_section = ""
        if related_context:
            context_section = "\n\nRelated code from project:\n" + "\n---\n".join(related_context[:3])

        # Build preferences section
        pref_section = ""
        if preferences:
            coding_style = preferences.get("coding_style", "concise")
            pref_section = f"\n\nCoding style: {coding_style}"

        # Build type-specific instructions
        type_instructions = self._get_type_instructions(completion_type, language)

        prompt = f"""You are an expert {language} developer. Complete the following code based on the context provided.

Task: {task_description}

Current code to complete:
```python
{current_code}
```{context_section}{pref_section}

Instructions:
{type_instructions}

Please provide only the completed code without additional explanations. Focus on:
- Following the existing code style and patterns
- Proper error handling where appropriate
- Clean, readable, and maintainable code
- Completing the logical flow of the code

Completed code:"""

        return prompt

    def _get_type_instructions(self, completion_type: str, language: str) -> str:
        """Get type-specific completion instructions"""
        instructions = {
            "function": f"""
- Complete the function implementation
- Add proper type hints if using {language}
- Include docstring if appropriate
- Handle edge cases and errors
- Return appropriate values""",

            "class": f"""
- Complete the class definition
- Add necessary methods and properties
- Implement constructor if needed
- Add proper encapsulation
- Include method docstrings""",

            "block": f"""
- Complete the code block logic
- Maintain proper indentation
- Handle conditional branches
- Add appropriate comments
- Ensure logical flow""",

            "import": f"""
- Add necessary import statements
- Follow {language} import conventions
- Avoid duplicate imports
- Organize imports properly""",

            "general": f"""
- Complete the code logically
- Follow {language} best practices
- Add necessary error handling
- Ensure code is complete and runnable"""
        }

        return instructions.get(completion_type, instructions["general"])

    def _format_completion(self, completion: str, task_analysis: Dict[str, Any]) -> str:
        """Format the completion based on task requirements"""
        language = task_analysis["language"]
        completion_type = task_analysis["completion_type"]

        # Clean up the completion
        completion = completion.strip()

        # Remove any markdown code block markers if present
        if completion.startswith("```"):
            lines = completion.split("\n")
            # Remove first and last lines if they're code block markers
            if len(lines) > 1 and lines[-1].strip() == "```":
                completion = "\n".join(lines[1:-1])
            else:
                completion = "\n".join(lines[1:])

        # Format based on completion type
        if completion_type == "function":
            completion = self._format_function_completion(completion)
        elif completion_type == "class":
            completion = self._format_class_completion(completion)

        return completion

    def _format_function_completion(self, completion: str) -> str:
        """Format function completion with proper indentation"""
        lines = completion.split("\n")
        formatted_lines = []

        for line in lines:
            # Ensure proper indentation (assuming 4 spaces)
            if line.strip() and not line.startswith(" "):
                formatted_lines.append("    " + line)
            else:
                formatted_lines.append(line)

        return "\n".join(formatted_lines)

    def _format_class_completion(self, completion: str) -> str:
        """Format class completion with proper structure"""
        # For now, just ensure consistent indentation
        lines = completion.split("\n")
        formatted_lines = []

        for line in lines:
            if line.strip() and not line.startswith(" "):
                # Check if it's a method definition
                if line.startswith("def ") or line.startswith("async def "):
                    formatted_lines.append("    " + line)
                else:
                    formatted_lines.append(line)
            else:
                formatted_lines.append(line)

        return "\n".join(formatted_lines)

    def _handle_error(self, error_message: str) -> Dict[str, Any]:
        """Handle errors during completion"""
        self._log_activity("completion_error", {"error": error_message})
        self._publish_status("error", {"message": error_message})

        return {
            "action": "error",
            "output": f"Completion failed: {error_message}",
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
        """Validate completion result"""
        if not super().validate_result(result):
            return False

        output = result.get("output", "")
        return len(output.strip()) > 0 and not output.startswith("Error:")

    def cleanup(self):
        """Cleanup resources"""
        self._publish_status("cleanup", {"agent": self.agent_name})