"""
Model Manager - LLM provider management with intelligent fallback
"""
import os
import time
import requests
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import json


class ModelManager:
    """
    Model Manager for Legion - handles multiple LLM providers with intelligent fallback.
    Prioritizes local models, falls back to cloud providers based on availability and cost.
    """

    def __init__(self):
        self.providers = {}
        self.model_priorities = []
        self._load_configuration()
        self._initialize_providers()

    def _load_configuration(self):
        """Load model configuration from config files"""
        config_dir = Path(__file__).parent.parent / "config"
        config_dir.mkdir(exist_ok=True)

        # Default model priorities (local-first approach)
        self.model_priorities = [
            "ollama",           # Local Ollama models (free, fast, private)
            "lmstudio",         # Local LM Studio models
            "gpt4all",          # Local GPT4All models
            "openai",           # Cloud OpenAI (paid, reliable)
            "anthropic",        # Cloud Anthropic/Claude (paid, good)
            "google",           # Cloud Google/Gemini (free tier available)
            "openrouter",       # Cloud OpenRouter (multiple models, paid)
            "together",         # Cloud Together AI (paid)
        ]

        # Load custom configuration if available
        config_file = config_dir / "model_priorities.yaml"
        if config_file.exists():
            try:
                import yaml
                with open(config_file, 'r') as f:
                    custom_config = yaml.safe_load(f)
                    if custom_config.get('priorities'):
                        self.model_priorities = custom_config['priorities']
            except ImportError:
                print("Warning: PyYAML not installed, using default model priorities")
            except Exception as e:
                print(f"Warning: Could not load custom model config: {e}")

    def _initialize_providers(self):
        """Initialize all configured providers"""
        self.providers = {
            "ollama": OllamaProvider(),
            "lmstudio": LMStudioProvider(),
            "gpt4all": GPT4AllProvider(),
            "openai": OpenAIProvider(),
            "anthropic": AnthropicProvider(),
            "google": GoogleProvider(),
            "openrouter": OpenRouterProvider(),
            "together": TogetherProvider(),
        }

    def generate(self, prompt: str, context: Optional[Dict[str, Any]] = None,
                max_tokens: int = 1000, temperature: float = 0.7) -> Dict[str, Any]:
        """
        Generate text using the best available model.

        Args:
            prompt: The prompt to generate from
            context: Additional context for model selection
            max_tokens: Maximum tokens to generate
            temperature: Creativity/randomness factor

        Returns:
            Dictionary with generated text and metadata
        """
        start_time = time.time()

        # Try providers in priority order
        for provider_name in self.model_priorities:
            provider = self.providers.get(provider_name)
            if not provider:
                continue

            try:
                # Check if provider is available
                if not provider.is_available():
                    continue

                # Generate text
                result = provider.generate(
                    prompt=prompt,
                    context=context,
                    max_tokens=max_tokens,
                    temperature=temperature
                )

                # Add metadata
                result.update({
                    "provider": provider_name,
                    "response_time": time.time() - start_time,
                    "fallback_used": provider_name != self.model_priorities[0]
                })

                return result

            except Exception as e:
                print(f"Warning: {provider_name} failed: {e}")
                continue

        # All providers failed
        return {
            "error": "All model providers failed",
            "text": "",
            "provider": "none",
            "response_time": time.time() - start_time,
            "fallback_used": False
        }

    def get_available_providers(self) -> List[str]:
        """Get list of currently available providers"""
        available = []
        for name, provider in self.providers.items():
            try:
                if provider.is_available():
                    available.append(name)
            except:
                continue
        return available

    def get_provider_status(self) -> Dict[str, Any]:
        """Get status of all providers"""
        status = {}
        for name, provider in self.providers.items():
            try:
                status[name] = {
                    "available": provider.is_available(),
                    "priority": self.model_priorities.index(name) if name in self.model_priorities else 999,
                    "type": provider.get_type()
                }
            except Exception as e:
                status[name] = {
                    "available": False,
                    "error": str(e),
                    "priority": 999,
                    "type": "unknown"
                }
        return status

    def set_provider_priority(self, provider_name: str, priority: int):
        """Set priority for a specific provider"""
        if provider_name in self.model_priorities:
            self.model_priorities.remove(provider_name)

        if priority < len(self.model_priorities):
            self.model_priorities.insert(priority, provider_name)
        else:
            self.model_priorities.append(provider_name)


# Base Provider Class
class BaseProvider:
    """Base class for all model providers"""

    def __init__(self, name: str):
        self.name = name
        self.base_url = ""
        self.api_key = None
        self.timeout = 30

    def is_available(self) -> bool:
        """Check if the provider is available"""
        return False

    def generate(self, prompt: str, context: Optional[Dict[str, Any]] = None,
                max_tokens: int = 1000, temperature: float = 0.7) -> Dict[str, Any]:
        """Generate text using this provider"""
        raise NotImplementedError

    def get_type(self) -> str:
        """Get provider type (local/cloud)"""
        return "unknown"

    def _make_request(self, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Make HTTP request to provider"""
        try:
            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"

            response = requests.post(
                f"{self.base_url}{endpoint}",
                json=payload,
                headers=headers,
                timeout=self.timeout
            )

            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"HTTP {response.status_code}: {response.text}")

        except requests.RequestException as e:
            raise Exception(f"Request failed: {e}")


# Local Providers
class OllamaProvider(BaseProvider):
    def __init__(self):
        super().__init__("ollama")
        self.base_url = "http://localhost:11434"

    def is_available(self) -> bool:
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False

    def generate(self, prompt: str, context: Optional[Dict[str, Any]] = None,
                max_tokens: int = 1000, temperature: float = 0.7) -> Dict[str, Any]:
        payload = {
            "model": "llama2",  # Default model
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }

        response = self._make_request("/api/generate", payload)
        return {
            "text": response.get("response", ""),
            "usage": {"total_tokens": len(response.get("response", "").split())},
            "finish_reason": "stop"
        }

    def get_type(self) -> str:
        return "local"


class LMStudioProvider(BaseProvider):
    def __init__(self):
        super().__init__("lmstudio")
        self.base_url = "http://localhost:1234"

    def is_available(self) -> bool:
        try:
            response = requests.get(f"{self.base_url}/v1/models", timeout=5)
            return response.status_code == 200
        except:
            return False

    def generate(self, prompt: str, context: Optional[Dict[str, Any]] = None,
                max_tokens: int = 1000, temperature: float = 0.7) -> Dict[str, Any]:
        payload = {
            "model": "local-model",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature
        }

        response = self._make_request("/v1/chat/completions", payload)
        choice = response.get("choices", [{}])[0]
        return {
            "text": choice.get("message", {}).get("content", ""),
            "usage": response.get("usage", {}),
            "finish_reason": choice.get("finish_reason", "stop")
        }

    def get_type(self) -> str:
        return "local"


class GPT4AllProvider(BaseProvider):
    def __init__(self):
        super().__init__("gpt4all")
        self.base_url = "http://localhost:4891"

    def is_available(self) -> bool:
        try:
            response = requests.get(f"{self.base_url}/v1/models", timeout=5)
            return response.status_code == 200
        except:
            return False

    def generate(self, prompt: str, context: Optional[Dict[str, Any]] = None,
                max_tokens: int = 1000, temperature: float = 0.7) -> Dict[str, Any]:
        payload = {
            "model": "gpt4all-model",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature
        }

        response = self._make_request("/v1/chat/completions", payload)
        choice = response.get("choices", [{}])[0]
        return {
            "text": choice.get("message", {}).get("content", ""),
            "usage": response.get("usage", {}),
            "finish_reason": choice.get("finish_reason", "stop")
        }

    def get_type(self) -> str:
        return "local"


# Cloud Providers
class OpenAIProvider(BaseProvider):
    def __init__(self):
        super().__init__("openai")
        self.base_url = "https://api.openai.com"
        self.api_key = os.getenv("OPENAI_API_KEY")

    def is_available(self) -> bool:
        return bool(self.api_key)

    def generate(self, prompt: str, context: Optional[Dict[str, Any]] = None,
                max_tokens: int = 1000, temperature: float = 0.7) -> Dict[str, Any]:
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature
        }

        response = self._make_request("/v1/chat/completions", payload)
        choice = response.get("choices", [{}])[0]
        return {
            "text": choice.get("message", {}).get("content", ""),
            "usage": response.get("usage", {}),
            "finish_reason": choice.get("finish_reason", "stop")
        }

    def get_type(self) -> str:
        return "cloud"


class AnthropicProvider(BaseProvider):
    def __init__(self):
        super().__init__("anthropic")
        self.base_url = "https://api.anthropic.com"
        self.api_key = os.getenv("ANTHROPIC_API_KEY")

    def is_available(self) -> bool:
        return bool(self.api_key)

    def generate(self, prompt: str, context: Optional[Dict[str, Any]] = None,
                max_tokens: int = 1000, temperature: float = 0.7) -> Dict[str, Any]:
        payload = {
            "model": "claude-3-sonnet-20240229",
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [{"role": "user", "content": prompt}]
        }

        response = self._make_request("/v1/messages", payload)
        content = response.get("content", [{}])[0]
        return {
            "text": content.get("text", ""),
            "usage": response.get("usage", {}),
            "finish_reason": response.get("stop_reason", "stop")
        }

    def get_type(self) -> str:
        return "cloud"


class GoogleProvider(BaseProvider):
    def __init__(self):
        super().__init__("google")
        self.base_url = "https://generativelanguage.googleapis.com"
        self.api_key = os.getenv("GOOGLE_API_KEY")

    def is_available(self) -> bool:
        return bool(self.api_key)

    def generate(self, prompt: str, context: Optional[Dict[str, Any]] = None,
                max_tokens: int = 1000, temperature: float = 0.7) -> Dict[str, Any]:
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens
            }
        }

        response = self._make_request(f"/v1beta/models/gemini-pro:generateContent?key={self.api_key}", payload)
        candidate = response.get("candidates", [{}])[0]
        content = candidate.get("content", {})
        text = content.get("parts", [{}])[0].get("text", "")

        return {
            "text": text,
            "usage": {"total_tokens": len(text.split())},
            "finish_reason": candidate.get("finishReason", "stop")
        }

    def get_type(self) -> str:
        return "cloud"


class OpenRouterProvider(BaseProvider):
    def __init__(self):
        super().__init__("openrouter")
        self.base_url = "https://openrouter.ai/api"
        self.api_key = os.getenv("OPENROUTER_API_KEY")

    def is_available(self) -> bool:
        return bool(self.api_key)

    def generate(self, prompt: str, context: Optional[Dict[str, Any]] = None,
                max_tokens: int = 1000, temperature: float = 0.7) -> Dict[str, Any]:
        payload = {
            "model": "anthropic/claude-3-haiku",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature
        }

        response = self._make_request("/v1/chat/completions", payload)
        choice = response.get("choices", [{}])[0]
        return {
            "text": choice.get("message", {}).get("content", ""),
            "usage": response.get("usage", {}),
            "finish_reason": choice.get("finish_reason", "stop")
        }

    def get_type(self) -> str:
        return "cloud"


class TogetherProvider(BaseProvider):
    def __init__(self):
        super().__init__("together")
        self.base_url = "https://api.together.xyz"
        self.api_key = os.getenv("TOGETHER_API_KEY")

    def is_available(self) -> bool:
        return bool(self.api_key)

    def generate(self, prompt: str, context: Optional[Dict[str, Any]] = None,
                max_tokens: int = 1000, temperature: float = 0.7) -> Dict[str, Any]:
        payload = {
            "model": "togethercomputer/llama-2-70b-chat",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature
        }

        response = self._make_request("/v1/chat/completions", payload)
        choice = response.get("choices", [{}])[0]
        return {
            "text": choice.get("message", {}).get("content", ""),
            "usage": response.get("usage", {}),
            "finish_reason": choice.get("finish_reason", "stop")
        }

    def get_type(self) -> str:
        return "cloud"