import requests
import json
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
import asyncio
import aiohttp

logger = logging.getLogger(__name__)

class HybridAIClient:
    """Hybrid AI client that supports multiple AI services"""

    def __init__(self, fastapi_url: str = "http://localhost:8000"):
        self.fastapi_url = fastapi_url
        self.local_services = {}
        self.initialize_local_services()

    def initialize_local_services(self):
        """Initialize local AI services as fallback"""
        try:
            from gpt4all import GPT4All
            self.local_services['gpt4all'] = GPT4All("orca-mini-3b-gguf2-q4_0.gguf")
            logger.info("Local GPT4All initialized")
        except Exception as e:
            logger.warning(f"Local GPT4All failed: {e}")

    async def chat_completion(
        self,
        message: str,
        service: str = "auto",
        context: Optional[Dict[str, Any]] = None,
        personality: str = "friendly",
        timeout: int = 30
    ) -> Dict[str, Any]:
        """Generate chat completion using hybrid approach"""

        # Try FastAPI service first
        try:
            return await self._fastapi_chat(message, service, context, personality, timeout)
        except Exception as e:
            logger.warning(f"FastAPI service failed: {e}")
            # Fallback to local service
            return await self._local_chat(message, context, personality)

    async def _fastapi_chat(
        self,
        message: str,
        service: str,
        context: Optional[Dict[str, Any]],
        personality: str,
        timeout: int
    ) -> Dict[str, Any]:
        """Chat using FastAPI service"""
        async with aiohttp.ClientSession() as session:
            payload = {
                "message": message,
                "ai_service": service,
                "context": context,
                "personality": personality
            }

            async with session.post(
                f"{self.fastapi_url}/chat",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=timeout)
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return {
                        "response": result["response"],
                        "service_used": result["service_used"],
                        "source": "fastapi",
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    raise Exception(f"FastAPI error: {response.status}")

    async def _local_chat(
        self,
        message: str,
        context: Optional[Dict[str, Any]],
        personality: str
    ) -> Dict[str, Any]:
        """Local chat fallback"""
        if 'gpt4all' in self.local_services:
            try:
                with self.local_services['gpt4all'].chat_session():
                    response = self.local_services['gpt4all'].generate(message, max_tokens=500)

                return {
                    "response": response,
                    "service_used": "gpt4all_local",
                    "source": "local",
                    "timestamp": datetime.now().isoformat()
                }
            except Exception as e:
                logger.error(f"Local GPT4All failed: {e}")

        # Final fallback - simple responses
        return {
            "response": self._get_fallback_response(message),
            "service_used": "fallback",
            "source": "fallback",
            "timestamp": datetime.now().isoformat()
        }

    def _get_fallback_response(self, message: str) -> str:
        """Get fallback response when all AI services fail"""
        fallbacks = [
            "I'm here to help you create amazing videos! What would you like to work on?",
            "I can assist with video generation, content analysis, and more. How can I help?",
            "Let's create something great together! What video topic interests you?",
            "I'm ready to help with your video creation needs. What do you need assistance with?"
        ]
        return fallbacks[hash(message) % len(fallbacks)]

    async def generate_video(
        self,
        topic: str,
        duration: int = 60,
        style: str = "educational",
        service: str = "auto"
    ) -> Dict[str, Any]:
        """Generate video using hybrid approach"""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "topic": topic,
                    "duration": duration,
                    "style": style,
                    "ai_service": service
                }

                async with session.post(
                    f"{self.fastapi_url}/video/generate",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=300)  # 5 minutes for video gen
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "status": "success",
                            "message": result["message"],
                            "source": "fastapi",
                            **result
                        }
                    else:
                        raise Exception(f"Video generation error: {response.status}")

        except Exception as e:
            logger.error(f"Video generation failed: {e}")
            return {
                "status": "error",
                "message": f"Video generation failed: {str(e)}",
                "source": "error"
            }

    async def get_service_status(self) -> Dict[str, Any]:
        """Get status of all AI services"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.fastapi_url}/services") as response:
                    if response.status == 200:
                        services = await response.json()
                        return {
                            "fastapi_status": "available",
                            "services": services,
                            "local_services": list(self.local_services.keys())
                        }
                    else:
                        raise Exception(f"Status check failed: {response.status}")
        except Exception as e:
            return {
                "fastapi_status": "unavailable",
                "error": str(e),
                "local_services": list(self.local_services.keys())
            }

class FreeTierAIClient:
    """Client for free tier AI services"""

    def __init__(self):
        self.services = {}
        self._initialize_free_services()

    def _initialize_free_services(self):
        """Initialize free tier AI services"""
        # These would use actual free tier API keys
        self.services = {
            "openai_free": {
                "api_key": "sk-free-tier-key",  # Replace with actual free tier key
                "model": "gpt-3.5-turbo",
                "rate_limit": 100,  # requests per day
                "tokens_limit": 10000  # tokens per day
            },
            "gemini_free": {
                "api_key": "free-gemini-key",  # Replace with actual free tier key
                "model": "gemini-pro",
                "rate_limit": 60,  # requests per minute
                "tokens_limit": 1000000  # tokens per month
            },
            "claude_free": {
                "api_key": "free-claude-key",  # Replace with actual free tier key
                "model": "claude-3-haiku-20240307",
                "rate_limit": 50,  # requests per minute
                "tokens_limit": 100000  # tokens per month
            }
        }

    async def chat_with_free_tier(self, message: str, service: str = "auto") -> Dict[str, Any]:
        """Chat using free tier AI services"""
        if service == "auto":
            service = self._select_best_free_service()

        if service not in self.services:
            return {
                "response": "Free tier service not available",
                "service": "none",
                "status": "error"
            }

        try:
            if "openai" in service:
                return await self._openai_free_chat(message)
            elif "gemini" in service:
                return await self._gemini_free_chat(message)
            elif "claude" in service:
                return await self._claude_free_chat(message)
        except Exception as e:
            logger.error(f"Free tier {service} failed: {e}")
            return {
                "response": f"Free tier service temporarily unavailable: {str(e)}",
                "service": service,
                "status": "error"
            }

    def _select_best_free_service(self) -> str:
        """Select best available free tier service"""
        priority = ["gemini_free", "openai_free", "claude_free"]
        for service in priority:
            if service in self.services:
                return service
        return "gemini_free"

    async def _openai_free_chat(self, message: str) -> Dict[str, Any]:
        """OpenAI free tier chat"""
        # This would use actual OpenAI free tier API
        return {
            "response": f"OpenAI Free Tier: {message[:50]}...",
            "service": "openai_free",
            "status": "success"
        }

    async def _gemini_free_chat(self, message: str) -> Dict[str, Any]:
        """Google Gemini free tier chat"""
        # This would use actual Gemini free tier API
        return {
            "response": f"Gemini Free Tier: {message[:50]}...",
            "service": "gemini_free",
            "status": "success"
        }

    async def _claude_free_chat(self, message: str) -> Dict[str, Any]:
        """Anthropic Claude free tier chat"""
        # This would use actual Claude free tier API
        return {
            "response": f"Claude Free Tier: {message[:50]}...",
            "service": "claude_free",
            "status": "success"
        }