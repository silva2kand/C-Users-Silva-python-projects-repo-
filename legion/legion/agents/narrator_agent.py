"""
Narrator Agent - Provides voice feedback and narration using TTS
"""
from typing import Dict, Any, Optional, List
import re
from .base_agent import BaseAgent


class NarratorAgent(BaseAgent):
    """
    Narrator Agent - specializes in providing voice feedback and narration.
    Uses text-to-speech to communicate results, progress, and guidance.
    """

    def __init__(self, message_bus, journal, context: Optional[Dict[str, Any]] = None,
                 model_manager=None):
        super().__init__(message_bus, journal, context, model_manager)
        self.capabilities = [
            "voice_feedback",
            "progress_narration",
            "error_announcement",
            "guidance_narration",
            "status_updates"
        ]
        self.tts_enabled = True
        self.voice_speed = 1.0
        self.voice_pitch = 1.0

    def execute(self) -> Dict[str, Any]:
        """
        Provide voice narration based on the current context and task.
        """
        self.start_time = self._get_timestamp()
        self._publish_status("starting", {"task": "voice_narration"})

        try:
            # Determine what to narrate
            narration_type = self._determine_narration_type()

            # Generate narration content
            narration_content = self._generate_narration_content(narration_type)

            # Convert to speech if TTS is enabled
            if self.tts_enabled:
                audio_data = self._convert_to_speech(narration_content)
            else:
                audio_data = None

            # Generate text summary for non-voice feedback
            text_summary = self._generate_text_summary(narration_content)

            # Validate the result
            if not self.validate_result({"action": "voice_narration", "output": narration_content}):
                return self._handle_error("Voice narration failed validation")

            # Log successful narration
            self._log_activity("narration_success", {
                "type": narration_type,
                "content_length": len(narration_content),
                "tts_enabled": self.tts_enabled
            })

            self._publish_status("completed", {
                "narration_type": narration_type,
                "tts_used": self.tts_enabled
            })

            return {
                "action": "voice_narration",
                "output": {
                    "narration_text": narration_content,
                    "audio_data": audio_data,
                    "text_summary": text_summary,
                    "narration_type": narration_type
                },
                "metadata": {
                    "voice_speed": self.voice_speed,
                    "voice_pitch": self.voice_pitch,
                    "tts_provider": "system_tts",  # Could be extended to use different TTS services
                    "narration_duration_estimate": self._estimate_duration(narration_content)
                }
            }

        except Exception as e:
            return self._handle_error(f"Voice narration failed: {str(e)}")

    def _determine_narration_type(self) -> str:
        """Determine what type of narration is needed"""
        task_description = self.context.get("task_description", "").lower()
        current_code = self.context.get("current_code", "")
        agent_results = self.context.get("agent_results", [])

        # Determine narration type based on context
        if "error" in task_description or any("error" in str(result) for result in agent_results):
            return "error_feedback"
        elif "complete" in task_description or "finish" in task_description:
            return "completion_feedback"
        elif "review" in task_description or "quality" in task_description:
            return "review_feedback"
        elif "test" in task_description:
            return "test_feedback"
        elif "refactor" in task_description:
            return "refactoring_feedback"
        elif agent_results:
            return "progress_update"
        elif current_code:
            return "code_guidance"
        else:
            return "general_guidance"

    def _generate_narration_content(self, narration_type: str) -> str:
        """Generate appropriate narration content based on type"""
        content_generators = {
            "error_feedback": self._generate_error_narration,
            "completion_feedback": self._generate_completion_narration,
            "review_feedback": self._generate_review_narration,
            "test_feedback": self._generate_test_narration,
            "refactoring_feedback": self._generate_refactoring_narration,
            "progress_update": self._generate_progress_narration,
            "code_guidance": self._generate_code_guidance,
            "general_guidance": self._generate_general_guidance
        }

        generator = content_generators.get(narration_type, self._generate_general_guidance)
        return generator()

    def _generate_error_narration(self) -> str:
        """Generate narration for error feedback"""
        agent_results = self.context.get("agent_results", [])
        error_messages = []

        # Extract error messages from results
        for result in agent_results:
            if isinstance(result, dict) and result.get("action") == "error":
                error_messages.append(result.get("output", ""))

        if not error_messages:
            error_messages = ["An error has occurred during processing"]

        narration = "Attention! I've detected some errors that need your attention. "

        for i, error in enumerate(error_messages[:3], 1):  # Limit to 3 errors
            narration += f"Error {i}: {self._clean_text_for_speech(error)}. "

        narration += "Please review the error details and take appropriate action. "

        return narration

    def _generate_completion_narration(self) -> str:
        """Generate narration for task completion"""
        task_description = self.context.get("task_description", "task")

        narration = f"Great job! I've successfully completed the {task_description}. "

        # Add specific completion details
        agent_results = self.context.get("agent_results", [])
        if agent_results:
            successful_results = [r for r in agent_results if isinstance(r, dict) and r.get("action") != "error"]
            narration += f"Processed {len(successful_results)} components successfully. "

        narration += "The results are ready for your review. "

        return narration

    def _generate_review_narration(self) -> str:
        """Generate narration for code review feedback"""
        agent_results = self.context.get("agent_results", [])

        narration = "Code review complete. "

        # Extract review metrics
        quality_score = None
        issues_count = 0

        for result in agent_results:
            if isinstance(result, dict) and "quality_score" in result.get("output", {}):
                quality_score = result["output"]["quality_score"]
            if isinstance(result, dict) and "issues_count" in result.get("metadata", {}):
                issues_count = result["metadata"]["issues_count"]

        if quality_score is not None:
            narration += f"Your code quality score is {quality_score} out of 100. "

        if issues_count > 0:
            narration += f"I found {issues_count} issues that could be improved. "
        else:
            narration += "Excellent! No major issues found in your code. "

        narration += "Please check the detailed review report for specific recommendations. "

        return narration

    def _generate_test_narration(self) -> str:
        """Generate narration for test generation feedback"""
        agent_results = self.context.get("agent_results", [])

        narration = "Test generation complete. "

        # Extract test metrics
        test_cases = 0
        coverage = 0

        for result in agent_results:
            if isinstance(result, dict) and "test_cases_count" in result.get("metadata", {}):
                test_cases = result["metadata"]["test_cases_count"]
            if isinstance(result, dict) and "coverage_estimate" in result.get("metadata", {}):
                coverage = result["metadata"]["coverage_estimate"]

        if test_cases > 0:
            narration += f"Generated {test_cases} comprehensive test cases. "

        if coverage > 0:
            narration += f"Estimated test coverage is {coverage} percent. "

        narration += "Your code now has proper test coverage for validation. "

        return narration

    def _generate_refactoring_narration(self) -> str:
        """Generate narration for refactoring feedback"""
        agent_results = self.context.get("agent_results", [])

        narration = "Refactoring analysis complete. "

        # Extract refactoring metrics
        opportunities = 0

        for result in agent_results:
            if isinstance(result, dict) and "opportunities_found" in result.get("metadata", {}):
                opportunities = result["metadata"]["opportunities_found"]

        if opportunities > 0:
            narration += f"I found {opportunities} opportunities for code improvement. "
            narration += "These include simplifying complex functions, removing duplicate code, and improving naming conventions. "
        else:
            narration += "Your code structure looks good! No major refactoring needed at this time. "

        narration += "Review the suggestions to enhance your code quality. "

        return narration

    def _generate_progress_narration(self) -> str:
        """Generate narration for progress updates"""
        agent_results = self.context.get("agent_results", [])

        narration = "Progress update. "

        completed_tasks = len([r for r in agent_results if isinstance(r, dict) and r.get("action") != "error"])
        total_tasks = len(agent_results)

        if total_tasks > 0:
            completion_percentage = (completed_tasks / total_tasks) * 100
            narration += f"Completed {completed_tasks} out of {total_tasks} tasks, which is {completion_percentage:.0f} percent. "

        # Add specific progress details
        successful_agents = []
        for result in agent_results:
            if isinstance(result, dict) and result.get("action") != "error":
                # Try to identify which agent completed
                if "completion" in str(result.get("action", "")):
                    successful_agents.append("completion agent")
                elif "review" in str(result.get("action", "")):
                    successful_agents.append("review agent")
                elif "test" in str(result.get("action", "")):
                    successful_agents.append("test generation agent")

        if successful_agents:
            narration += f"Successfully completed work from: {', '.join(set(successful_agents))}. "

        narration += "Continuing with remaining tasks. "

        return narration

    def _generate_code_guidance(self) -> str:
        """Generate narration for code guidance"""
        current_code = self.context.get("current_code", "")
        task_description = self.context.get("task_description", "")

        narration = "Code guidance. "

        if current_code:
            # Analyze code for guidance
            lines_count = len(current_code.split('\n'))
            functions_count = len(re.findall(r'^\s*def\s+', current_code, re.MULTILINE))
            classes_count = len(re.findall(r'^\s*class\s+', current_code, re.MULTILINE))

            narration += f"I'm analyzing your code with {lines_count} lines, "
            if functions_count > 0:
                narration += f"{functions_count} functions, "
            if classes_count > 0:
                narration += f"and {classes_count} classes. "

        if task_description:
            narration += f"For the task: {self._clean_text_for_speech(task_description)}. "

        narration += "I can help you with code completion, refactoring, testing, or review. What would you like me to focus on? "

        return narration

    def _generate_general_guidance(self) -> str:
        """Generate general guidance narration"""
        narration = "Hello! I'm your AI coding assistant, ready to help with your development tasks. "

        narration += "I can assist you with: "
        narration += "code completion and generation, "
        narration += "code refactoring and optimization, "
        narration += "unit test generation, "
        narration += "code quality review, "
        narration += "and providing voice feedback on your progress. "

        narration += "What would you like to work on today? "

        return narration

    def _convert_to_speech(self, text: str) -> Optional[bytes]:
        """Convert text to speech audio data"""
        try:
            # Use system TTS (this is a placeholder - actual implementation would use a TTS library)
            # For now, we'll just return None and indicate TTS is not implemented
            # In a real implementation, you would use libraries like:
            # - pyttsx3 for offline TTS
            # - gTTS for Google Text-to-Speech
            # - azure-cognitiveservices-speech for Azure TTS

            self._log_activity("tts_conversion", {
                "text_length": len(text),
                "status": "placeholder_implementation"
            })

            # Placeholder return - in real implementation, return audio bytes
            return None

        except Exception as e:
            self._log_activity("tts_error", {"error": str(e)})
            return None

    def _generate_text_summary(self, narration_content: str) -> str:
        """Generate a text summary of the narration"""
        # Create a shorter text version for display/logs
        sentences = narration_content.split('. ')
        summary = '. '.join(sentences[:2])  # First 2 sentences

        if len(sentences) > 2:
            summary += '.'

        return summary

    def _clean_text_for_speech(self, text: str) -> str:
        """Clean text for better speech synthesis"""
        # Remove code snippets and special characters that don't speak well
        text = re.sub(r'```.*?```', 'code snippet', text, flags=re.DOTALL)
        text = re.sub(r'`.*?`', 'code', text)
        text = re.sub(r'[^\w\s.,!?-]', '', text)  # Remove special characters except basic punctuation

        # Limit length for speech
        if len(text) > 200:
            text = text[:197] + "..."

        return text.strip()

    def _estimate_duration(self, text: str) -> float:
        """Estimate speech duration in seconds"""
        # Rough estimate: 150 words per minute, average 5 characters per word
        words_count = len(text) / 5
        duration_seconds = (words_count / 150) * 60

        return round(duration_seconds, 1)

    def _handle_error(self, error_message: str) -> Dict[str, Any]:
        """Handle errors during narration"""
        self._log_activity("narration_error", {"error": error_message})
        self._publish_status("error", {"message": error_message})

        return {
            "action": "error",
            "output": f"Voice narration failed: {error_message}",
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
        """Validate narration result"""
        if not super().validate_result(result):
            return False

        output = result.get("output", {})
        return isinstance(output, dict) and "narration_text" in output

    def cleanup(self):
        """Cleanup resources"""
        self._publish_status("cleanup", {"agent": self.agent_name})