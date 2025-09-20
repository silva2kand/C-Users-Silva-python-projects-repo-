from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import asyncio
import logging
import json
from datetime import datetime

# AI Service integrations
try:
    from gpt4all import GPT4All
    GPT4ALL_AVAILABLE = True
except ImportError:
    GPT4ALL_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

try:
    import anthropic
    CLAUDE_AVAILABLE = True
except ImportError:
    CLAUDE_AVAILABLE = False

app = FastAPI(title="Video Remaker AI Service", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChatRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None
    personality: Optional[str] = "friendly"
    ai_service: Optional[str] = "auto"  # auto, gpt4all, openai, gemini, claude

class VideoRequest(BaseModel):
    topic: str
    duration: Optional[int] = 60
    style: Optional[str] = "educational"
    ai_service: Optional[str] = "auto"

class AIServiceManager:
    def __init__(self):
        self.services = {}
        self.initialize_services()

    def initialize_services(self):
        """Initialize all available AI services"""
        # GPT4All (Local)
        if GPT4ALL_AVAILABLE:
            try:
                self.services['gpt4all'] = GPT4All("orca-mini-3b-gguf2-q4_0.gguf")
                logger.info("GPT4All initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize GPT4All: {e}")

        # OpenAI (Free tier available)
        if OPENAI_AVAILABLE:
            try:
                # Use environment variable or free tier key
                openai.api_key = "sk-free-tier-key"  # Replace with actual free tier key
                self.services['openai'] = openai
                logger.info("OpenAI initialized")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI: {e}")

        # Google Gemini (Free tier)
        if GEMINI_AVAILABLE:
            try:
                genai.configure(api_key="free-gemini-key")  # Replace with actual key
                self.services['gemini'] = genai.GenerativeModel('gemini-pro')
                logger.info("Gemini initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini: {e}")

        # Anthropic Claude (Limited free tier)
        if CLAUDE_AVAILABLE:
            try:
                self.services['claude'] = anthropic.Anthropic(api_key="free-claude-key")
                logger.info("Claude initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Claude: {e}")

    async def chat_completion(self, message: str, service: str = "auto", **kwargs) -> str:
        """Generate chat completion using specified or auto-selected service"""
        if service == "auto":
            service = self.select_best_service()

        if service not in self.services:
            return f"AI service '{service}' not available. Available: {list(self.services.keys())}"

        try:
            if service == "gpt4all":
                return await self._gpt4all_chat(message, **kwargs)
            elif service == "openai":
                return await self._openai_chat(message, **kwargs)
            elif service == "gemini":
                return await self._gemini_chat(message, **kwargs)
            elif service == "claude":
                return await self._claude_chat(message, **kwargs)
        except Exception as e:
            logger.error(f"Error with {service}: {e}")
            # Fallback to next available service
            return await self._fallback_chat(message, **kwargs)

    def select_best_service(self) -> str:
        """Select the best available service based on priority and availability"""
        priority = ['gpt4all', 'gemini', 'openai', 'claude']
        for service in priority:
            if service in self.services:
                return service
        return 'gpt4all' if 'gpt4all' in self.services else list(self.services.keys())[0]

    async def _gpt4all_chat(self, message: str, **kwargs) -> str:
        """GPT4All chat completion"""
        with self.services['gpt4all'].chat_session():
            response = self.services['gpt4all'].generate(message, max_tokens=500)
        return response

    async def _openai_chat(self, message: str, **kwargs) -> str:
        """OpenAI chat completion"""
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": message}],
            max_tokens=500
        )
        return response.choices[0].message.content

    async def _gemini_chat(self, message: str, **kwargs) -> str:
        """Google Gemini chat completion"""
        response = self.services['gemini'].generate_content(message)
        return response.text

    async def _claude_chat(self, message: str, **kwargs) -> str:
        """Anthropic Claude chat completion"""
        response = self.services['claude'].messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=500,
            messages=[{"role": "user", "content": message}]
        )
        return response.content[0].text

    async def _fallback_chat(self, message: str, **kwargs) -> str:
        """Fallback chat using simple template responses"""
        responses = [
            "I'm here to help you create amazing videos! What would you like to work on?",
            "I can help you generate videos, analyze content, or answer questions. What do you need?",
            "Let's create something great together! What video topic interests you?",
            "I'm ready to assist with your video creation needs. How can I help today?"
        ]
        return responses[hash(message) % len(responses)]

# Global AI service manager
ai_manager = AIServiceManager()

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Video Remaker AI Service",
        "version": "1.0.0",
        "services": list(ai_manager.services.keys()),
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            service: "available" for service in ai_manager.services.keys()
        }
    }

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """Chat completion endpoint"""
    try:
        response = await ai_manager.chat_completion(
            message=request.message,
            service=request.ai_service,
            context=request.context,
            personality=request.personality
        )

        return {
            "response": response,
            "service_used": request.ai_service if request.ai_service != "auto" else ai_manager.select_best_service(),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

@app.post("/video/generate")
async def generate_video_endpoint(request: VideoRequest, background_tasks: BackgroundTasks):
    """Video generation endpoint"""
    try:
        # This would integrate with your video generation logic
        background_tasks.add_task(process_video_generation, request)

        return {
            "message": "Video generation started",
            "topic": request.topic,
            "status": "processing",
            "estimated_time": "5-15 minutes"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Video generation error: {str(e)}")

async def process_video_generation(request: VideoRequest):
    """Process video generation in background"""
    # This would contain your actual video generation logic
    logger.info(f"Processing video generation for topic: {request.topic}")

    # Simulate processing
    await asyncio.sleep(2)

    # Here you would call your video generation functions
    # video_result = await generate_video_with_ai(request.topic, request.duration, request.style)

    logger.info(f"Video generation completed for: {request.topic}")

@app.get("/services")
async def list_services():
    """List available AI services"""
    return {
        "available_services": list(ai_manager.services.keys()),
        "recommended": ai_manager.select_best_service(),
        "details": {
            "gpt4all": {
                "type": "local",
                "cost": "free",
                "speed": "fast",
                "privacy": "high"
            },
            "gemini": {
                "type": "cloud",
                "cost": "free tier available",
                "speed": "fast",
                "privacy": "medium"
            },
            "openai": {
                "type": "cloud",
                "cost": "free tier available",
                "speed": "fast",
                "privacy": "medium"
            },
            "claude": {
                "type": "cloud",
                "cost": "limited free tier",
                "speed": "fast",
                "privacy": "medium"
            }
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)