"""
Hybrid AI Client
================

A comprehensive AI client that seamlessly integrates multiple AI services with intelligent
fallback mechanisms for maximum reliability and performance.

Features:
- GPT4All integration for local AI processing
- OpenAI API integration for GPT models
- Google Gemini integration
- Anthropic Claude integration
- Automatic service fallback based on availability and performance
- Personality-based response generation
- Async processing for concurrent requests
- Comprehensive error handling and logging

Author: Hybrid AI System
"""

import asyncio
import json
import logging
import os
import random
import time
from typing import Any, Dict, List, Optional, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    logger.warning("python-dotenv not available, environment variables must be set manually")

# AI Service SDK imports with fallbacks
try:
    import gpt4all
    GPT4ALL_AVAILABLE = True
except ImportError:
    GPT4ALL_AVAILABLE = False
    logger.warning("GPT4All not available")

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI SDK not available")

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("Google Generative AI not available")

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    logger.warning("Anthropic SDK not available")

# Load fallback responses
FALLBACK_RESPONSES_FILE = "fallback_responses.json"
fallback_responses = {}

def load_fallback_responses():
    """Load fallback responses for offline functionality."""
    global fallback_responses
    try:
        if os.path.exists(FALLBACK_RESPONSES_FILE):
            with open(FALLBACK_RESPONSES_FILE, 'r') as f:
                fallback_responses = json.load(f)
            logger.info(f"Loaded {len(fallback_responses)} fallback responses")
        else:
            fallback_responses = {
                "greeting": "Hello! I'm your AI assistant. How can I help you today?",
                "error": "I'm experiencing some technical difficulties. Please try again later.",
                "unavailable": "The AI service is currently unavailable. Please try again later.",
                "busy": "I'm currently processing other requests. Please try again in a moment."
            }
    except Exception as e:
        logger.error(f"Error loading fallback responses: {e}")

class HybridAIClient:
    """
    Main AI client that orchestrates multiple AI services with intelligent fallback.
    """

    def __init__(self):
        """Initialize the hybrid AI client."""
        self.services = {}
        self.service_performance = {}
        self.last_used_service = None
        self.initialize_services()
        load_fallback_responses()

    def initialize_services(self):
        """Initialize all available AI services."""
        logger.info("Initializing AI services...")

        # Initialize GPT4All
        if GPT4ALL_AVAILABLE:
            try:
                self.services['gpt4all'] = GPT4AllService()
                logger.info("GPT4All service initialized")
            except Exception as e:
                logger.error(f"Failed to initialize GPT4All: {e}")

        # Initialize OpenAI
        if OPENAI_AVAILABLE:
            try:
                self.services['openai'] = OpenAIService()
                logger.info("OpenAI service initialized")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI: {e}")

        # Initialize Gemini
        if GEMINI_AVAILABLE:
            try:
                self.services['gemini'] = GeminiService()
                logger.info("Gemini service initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini: {e}")

        # Initialize Claude
        if ANTHROPIC_AVAILABLE:
            try:
                self.services['claude'] = ClaudeService()
                logger.info("Claude service initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Claude: {e}")

        logger.info(f"Initialized {len(self.services)} AI services")

    def select_best_service(self, personality: str = "helpful") -> str:
        """
        Select the best available service based on performance and availability.

        Args:
            personality: Desired personality mode

        Returns:
            Name of the selected service
        """
        available_services = [name for name, service in self.services.items()
                            if service.is_available()]

        if not available_services:
            return None

        # Prioritize based on personality and performance
        if personality == "creative" and "gemini" in available_services:
            return "gemini"
        elif personality == "analytical" and "claude" in available_services:
            return "claude"
        elif personality == "fast" and "openai" in available_services:
            return "openai"

        # Use last successful service if available
        if self.last_used_service in available_services:
            return self.last_used_service

        # Default priority: GPT4All (local) > OpenAI > Gemini > Claude
        priority_order = ["gpt4all", "openai", "gemini", "claude"]
        for service in priority_order:
            if service in available_services:
                return service

        # Fallback to random selection
        return random.choice(available_services)

    def generate_response(self, message: str, personality: str = "helpful",
                         max_tokens: int = 150, temperature: float = 0.7) -> Optional[str]:
        """
        Generate a response using the best available AI service.

        Args:
            message: User's input message
            personality: AI personality mode
            max_tokens: Maximum tokens in response
            temperature: Response creativity (0.0-1.0)

        Returns:
            Generated response or None if all services fail
        """
        service_name = self.select_best_service(personality)

        if not service_name:
            logger.error("No AI services available")
            return fallback_responses.get("unavailable")

        service = self.services[service_name]
        start_time = time.time()

        try:
            logger.info(f"Using {service_name} service for response generation")
            response = service.generate_response(
                message=message,
                personality=personality,
                max_tokens=max_tokens,
                temperature=temperature
            )

            if response:
                processing_time = time.time() - start_time
                self.service_performance[service_name] = processing_time
                self.last_used_service = service_name
                logger.info(".2f")
                return response
            else:
                logger.warning(f"{service_name} service returned empty response")
                return self._try_fallback_service(message, personality, max_tokens, temperature, service_name)

        except Exception as e:
            logger.error(f"Error with {service_name} service: {e}")
            return self._try_fallback_service(message, personality, max_tokens, temperature, service_name)

    def _try_fallback_service(self, message: str, personality: str,
                            max_tokens: int, temperature: float, exclude_service: str) -> Optional[str]:
        """Try fallback services if primary service fails."""
        available_services = [name for name in self.services.keys()
                            if name != exclude_service and self.services[name].is_available()]

        for service_name in available_services:
            try:
                logger.info(f"Trying fallback service: {service_name}")
                service = self.services[service_name]
                response = service.generate_response(
                    message=message,
                    personality=personality,
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                if response:
                    self.last_used_service = service_name
                    return response
            except Exception as e:
                logger.warning(f"Fallback service {service_name} also failed: {e}")
                continue

        # All services failed, use fallback response
        return fallback_responses.get("error")

    async def generate_response_async(self, message: str, personality: str = "helpful",
                                    max_tokens: int = 150, temperature: float = 0.7) -> Optional[str]:
        """Async version of generate_response."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.generate_response,
            message,
            personality,
            max_tokens,
            temperature
        )

class FreeTierAIClient:
    """
    Client for free tier AI services with rate limiting and usage tracking.
    """

    def __init__(self):
        """Initialize free tier AI client."""
        self.usage_count = {}
        self.last_request_time = {}
        self.rate_limits = {
            "openai": 3,  # requests per minute
            "gemini": 15,
            "claude": 5
        }
        self.initialize_services()

    def initialize_services(self):
        """Initialize free tier services."""
        self.services = {}

        if OPENAI_AVAILABLE:
            self.services['openai_free'] = OpenAIService(free_tier=True)

        if GEMINI_AVAILABLE:
            self.services['gemini_free'] = GeminiService(free_tier=True)

        if ANTHROPIC_AVAILABLE:
            self.services['claude_free'] = ClaudeService(free_tier=True)

    def _check_rate_limit(self, service_name: str) -> bool:
        """Check if service is within rate limits."""
        if service_name not in self.rate_limits:
            return True

        current_time = time.time()
        last_time = self.last_request_time.get(service_name, 0)
        usage_count = self.usage_count.get(service_name, 0)

        # Reset counter if more than a minute has passed
        if current_time - last_time > 60:
            self.usage_count[service_name] = 0
            usage_count = 0

        return usage_count < self.rate_limits[service_name]

    def generate_response(self, message: str, personality: str = "helpful",
                         max_tokens: int = 150, temperature: float = 0.7) -> Optional[str]:
        """Generate response using free tier services with rate limiting."""
        available_services = [name for name, service in self.services.items()
                            if service.is_available() and self._check_rate_limit(name)]

        if not available_services:
            logger.warning("No free tier services available or rate limited")
            return fallback_responses.get("busy")

        # Try services in order
        for service_name in available_services:
            try:
                service = self.services[service_name]
                response = service.generate_response(
                    message=message,
                    personality=personality,
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                if response:
                    self.usage_count[service_name] = self.usage_count.get(service_name, 0) + 1
                    self.last_request_time[service_name] = time.time()
                    return response
            except Exception as e:
                logger.warning(f"Free tier service {service_name} failed: {e}")
                continue

        return fallback_responses.get("unavailable")

    async def generate_response_async(self, message: str, personality: str = "helpful",
                                    max_tokens: int = 150, temperature: float = 0.7) -> Optional[str]:
        """Async version of generate_response."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.generate_response,
            message,
            personality,
            max_tokens,
            temperature
        )

# Individual AI Service Classes
class GPT4AllService:
    """GPT4All local AI service."""

    def __init__(self):
        """Initialize GPT4All service."""
        self.model = None
        self.available = False

        if GPT4ALL_AVAILABLE:
            try:
                model_path = os.getenv("GPT4ALL_MODEL_PATH", "models/orca-mini-3b.ggmlv3.q4_0.bin")
                self.model = gpt4all.GPT4All(model_path)
                self.available = True
                logger.info("GPT4All model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load GPT4All model: {e}")

    def is_available(self) -> bool:
        """Check if GPT4All service is available."""
        return self.available and self.model is not None

    def generate_response(self, message: str, personality: str = "helpful",
                         max_tokens: int = 150, temperature: float = 0.7) -> Optional[str]:
        """Generate response using GPT4All."""
        if not self.is_available():
            return None

        try:
            # Add personality context
            personality_prompts = {
                "helpful": "You are a helpful AI assistant. ",
                "creative": "You are a creative AI assistant. ",
                "analytical": "You are an analytical AI assistant. ",
                "funny": "You are a funny AI assistant. "
            }

            prompt = personality_prompts.get(personality, "") + message

            response = self.model.generate(
                prompt=prompt,
                max_tokens=max_tokens,
                temp=temperature
            )

            return response.strip() if response else None

        except Exception as e:
            logger.error(f"GPT4All generation error: {e}")
            return None

class OpenAIService:
    """OpenAI API service."""

    def __init__(self, free_tier: bool = False):
        """Initialize OpenAI service."""
        self.available = False
        self.free_tier = free_tier

        if OPENAI_AVAILABLE:
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                openai.api_key = api_key
                self.available = True
                self.model = "gpt-3.5-turbo" if free_tier else "gpt-4"
                logger.info(f"OpenAI service initialized (model: {self.model})")
            else:
                logger.warning("OpenAI API key not found")

    def is_available(self) -> bool:
        """Check if OpenAI service is available."""
        return self.available

    def generate_response(self, message: str, personality: str = "helpful",
                         max_tokens: int = 150, temperature: float = 0.7) -> Optional[str]:
        """Generate response using OpenAI."""
        if not self.is_available():
            return None

        try:
            # Add personality context
            personality_context = self._get_personality_context(personality)

            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": personality_context},
                    {"role": "user", "content": message}
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"OpenAI generation error: {e}")
            return None

    def _get_personality_context(self, personality: str) -> str:
        """Get personality context for OpenAI."""
        contexts = {
            "helpful": "You are a helpful AI assistant.",
            "creative": "You are a creative AI assistant who thinks outside the box.",
            "analytical": "You are an analytical AI assistant who provides detailed analysis.",
            "funny": "You are a funny AI assistant who uses humor in responses."
        }
        return contexts.get(personality, "You are a helpful AI assistant.")

class GeminiService:
    """Google Gemini service."""

    def __init__(self, free_tier: bool = False):
        """Initialize Gemini service."""
        self.available = False
        self.model = None

        if GEMINI_AVAILABLE:
            api_key = os.getenv("GOOGLE_API_KEY")
            if api_key:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel('gemini-pro')
                self.available = True
                logger.info("Gemini service initialized")
            else:
                logger.warning("Google API key not found")

    def is_available(self) -> bool:
        """Check if Gemini service is available."""
        return self.available and self.model is not None

    def generate_response(self, message: str, personality: str = "helpful",
                         max_tokens: int = 150, temperature: float = 0.7) -> Optional[str]:
        """Generate response using Gemini."""
        if not self.is_available():
            return None

        try:
            # Configure generation parameters
            generation_config = genai.types.GenerationConfig(
                max_output_tokens=max_tokens,
                temperature=temperature
            )

            # Add personality context
            personality_context = self._get_personality_context(personality)
            prompt = f"{personality_context}\n\nUser: {message}"

            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )

            return response.text.strip() if response.text else None

        except Exception as e:
            logger.error(f"Gemini generation error: {e}")
            return None

    def _get_personality_context(self, personality: str) -> str:
        """Get personality context for Gemini."""
        contexts = {
            "helpful": "You are a helpful AI assistant.",
            "creative": "You are a creative AI assistant who generates innovative ideas.",
            "analytical": "You are an analytical AI assistant who provides thorough analysis.",
            "funny": "You are a funny AI assistant who adds humor to conversations."
        }
        return contexts.get(personality, "You are a helpful AI assistant.")

class ClaudeService:
    """Anthropic Claude service."""

    def __init__(self, free_tier: bool = False):
        """Initialize Claude service."""
        self.available = False
        self.client = None

        if ANTHROPIC_AVAILABLE:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if api_key:
                self.client = anthropic.Anthropic(api_key=api_key)
                self.available = True
                logger.info("Claude service initialized")
            else:
                logger.warning("Anthropic API key not found")

    def is_available(self) -> bool:
        """Check if Claude service is available."""
        return self.available and self.client is not None

    def generate_response(self, message: str, personality: str = "helpful",
                         max_tokens: int = 150, temperature: float = 0.7) -> Optional[str]:
        """Generate response using Claude."""
        if not self.is_available():
            return None

        try:
            # Add personality context
            personality_context = self._get_personality_context(personality)

            response = self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=max_tokens,
                temperature=temperature,
                system=personality_context,
                messages=[
                    {"role": "user", "content": message}
                ]
            )

            return response.content[0].text.strip()

        except Exception as e:
            logger.error(f"Claude generation error: {e}")
            return None

    def _get_personality_context(self, personality: str) -> str:
        """Get personality context for Claude."""
        contexts = {
            "helpful": "You are a helpful AI assistant.",
            "creative": "You are a creative AI assistant who excels at generating innovative solutions.",
            "analytical": "You are an analytical AI assistant who provides detailed, logical analysis.",
            "funny": "You are a funny AI assistant who brings humor and wit to conversations."
        }
        return contexts.get(personality, "You are a helpful AI assistant.")

# Utility functions
def get_available_services() -> List[str]:
    """Get list of available AI services."""
    services = []
    if GPT4ALL_AVAILABLE:
        services.append("gpt4all")
    if OPENAI_AVAILABLE and os.getenv("OPENAI_API_KEY"):
        services.append("openai")
    if GEMINI_AVAILABLE and os.getenv("GOOGLE_API_KEY"):
        services.append("gemini")
    if ANTHROPIC_AVAILABLE and os.getenv("ANTHROPIC_API_KEY"):
        services.append("claude")
    return services

def test_service_availability() -> Dict[str, bool]:
    """Test availability of all AI services."""
    availability = {}

    # Test GPT4All
    if GPT4ALL_AVAILABLE:
        try:
            test_service = GPT4AllService()
            availability["gpt4all"] = test_service.is_available()
        except:
            availability["gpt4all"] = False
    else:
        availability["gpt4all"] = False

    # Test OpenAI
    if OPENAI_AVAILABLE and os.getenv("OPENAI_API_KEY"):
        try:
            test_service = OpenAIService()
            availability["openai"] = test_service.is_available()
        except:
            availability["openai"] = False
    else:
        availability["openai"] = False

    # Test Gemini
    if GEMINI_AVAILABLE and os.getenv("GOOGLE_API_KEY"):
        try:
            test_service = GeminiService()
            availability["gemini"] = test_service.is_available()
        except:
            availability["gemini"] = False
    else:
        availability["gemini"] = False

    # Test Claude
    if ANTHROPIC_AVAILABLE and os.getenv("ANTHROPIC_API_KEY"):
        try:
            test_service = ClaudeService()
            availability["claude"] = test_service.is_available()
        except:
            availability["claude"] = False
    else:
        availability["claude"] = False

    return availability

if __name__ == "__main__":
    # Test the hybrid AI client
    print("Testing Hybrid AI Client...")
    print(f"Available services: {get_available_services()}")
    print(f"Service availability: {test_service_availability()}")

    client = HybridAIClient()
    if client.services:
        print("\nTesting response generation...")
        test_message = "Hello! Can you tell me about artificial intelligence?"
        response = client.generate_response(test_message)
        print(f"Response: {response}")
    else:
        print("No AI services available for testing")