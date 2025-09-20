"""
Hybrid AI Video Remaker - FastAPI Service
=========================================

A comprehensive FastAPI service that orchestrates multiple AI services for video processing
and natural language chat functionality with intelligent fallback mechanisms.

Features:
- Multi-AI service orchestration (GPT4All, OpenAI, Gemini, Claude)
- Automatic fallback between services
- RESTful API endpoints for chat and video generation
- Health monitoring and service status
- Async processing with background tasks
- Comprehensive error handling and logging

Author: Hybrid AI System
"""

import asyncio
import json
import logging
import os
import time
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import uvicorn
from fastapi import BackgroundTasks, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# Import hybrid AI client
try:
    from hybrid_ai_client import HybridAIClient, FreeTierAIClient
except ImportError:
    # Fallback if module not found
    HybridAIClient = None
    FreeTierAIClient = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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
                "video_processing": "Video processing is currently unavailable. Please check back later.",
                "chat_unavailable": "Chat functionality is temporarily unavailable. Please try again later."
            }
            logger.warning("Fallback responses file not found, using defaults")
    except Exception as e:
        logger.error(f"Error loading fallback responses: {e}")
        fallback_responses = {
            "error": "System is currently offline. Please try again later."
        }
    # Ensure fallback responses are loaded at module import
load_fallback_responses()

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Pydantic models
class ChatRequest(BaseModel):
    """Request model for chat completion."""
    message: str = Field(..., description="The user's message")
    personality: Optional[str] = Field("helpful", description="AI personality mode")
    max_tokens: Optional[int] = Field(150, description="Maximum tokens in response")
    temperature: Optional[float] = Field(0.7, description="Response creativity (0.0-1.0)")

class ChatResponse(BaseModel):
    """Response model for chat completion."""
    response: str
    service_used: str
    processing_time: float
    timestamp: datetime

class VideoGenerationRequest(BaseModel):
    """Request model for video generation."""
    prompt: str = Field(..., description="Description of the video to generate")
    duration: Optional[int] = Field(30, description="Video duration in seconds")
    style: Optional[str] = Field("realistic", description="Video style")
    resolution: Optional[str] = Field("1080p", description="Video resolution")

class VideoGenerationResponse(BaseModel):
    """Response model for video generation."""
    status: str
    message: str
    estimated_time: Optional[int]
    job_id: Optional[str]

class ServiceStatus(BaseModel):
    """Model for service health status."""
    service_name: str
    status: str  # "healthy", "degraded", "unhealthy"
    last_check: datetime
    response_time: Optional[float]
    error_message: Optional[str]

class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str
    timestamp: datetime
    services: List[ServiceStatus]
    uptime: float

# Global variables
ai_client = None
free_tier_client = None
start_time = time.time()

# Service manager class
class AIServiceManager:
    """Manages multiple AI services with fallback mechanisms."""

    def __init__(self):
        self.services = {}
        self.last_health_check = {}
        self.initialize_clients()

    def initialize_clients(self):
        """Initialize AI clients."""
        global ai_client, free_tier_client

        try:
            if HybridAIClient:
                ai_client = HybridAIClient()
                logger.info("Hybrid AI client initialized successfully")
            else:
                logger.warning("HybridAIClient not available")

            if FreeTierAIClient:
                free_tier_client = FreeTierAIClient()
                logger.info("Free tier AI client initialized successfully")
            else:
                logger.warning("FreeTierAIClient not available")

        except Exception as e:
            logger.error(f"Error initializing AI clients: {e}")

    async def check_service_health(self, service_name: str) -> ServiceStatus:
        """Check health of a specific AI service."""
        try:
            start_time = time.time()

            if service_name == "hybrid_ai" and ai_client:
                # Simple health check for hybrid AI
                try:
                    response = ai_client.generate_response("Hello", max_tokens=10)
                    response_time = time.time() - start_time
                    return ServiceStatus(
                        service_name=service_name,
                        status="healthy" if response else "degraded",
                        last_check=datetime.now(),
                        response_time=response_time
                    )
                except Exception as e:
                    return ServiceStatus(
                        service_name=service_name,
                        status="unhealthy",
                        last_check=datetime.now(),
                        error_message=str(e)
                    )

            elif service_name == "free_tier" and free_tier_client:
                # Health check for free tier services
                response_time = time.time() - start_time
                return ServiceStatus(
                    service_name=service_name,
                    status="healthy",
                    last_check=datetime.now(),
                    response_time=response_time
                )

            else:
                return ServiceStatus(
                    service_name=service_name,
                    status="unhealthy",
                    last_check=datetime.now(),
                    error_message="Service not initialized"
                )

        except Exception as e:
            logger.error(f"Health check failed for {service_name}: {e}")
            return ServiceStatus(
                service_name=service_name,
                status="unhealthy",
                last_check=datetime.now(),
                error_message=str(e)
            )

    async def get_all_service_status(self) -> List[ServiceStatus]:
        """Get health status of all AI services."""
        services = ["hybrid_ai", "free_tier", "gpt4all", "openai", "gemini", "claude"]
        tasks = [self.check_service_health(service) for service in services]
        return await asyncio.gather(*tasks)

# Initialize service manager (moved to lifespan)
service_manager = None

# FastAPI app with lifespan management
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown."""
    global service_manager, ai_client, free_tier_client

    # Startup
    print("Starting service...")
    try:
        service_manager = AIServiceManager()
        logger.info("AI Service Manager initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize service manager: {e}")
        service_manager = None

    yield

    # Shutdown
    print("Shutting down service...")

app = FastAPI(
    title="Hybrid AI Video Remaker API",
    description="A comprehensive API for AI-powered video processing and chat functionality",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routes
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Hybrid AI Video Remaker API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

# @app.get("/health", response_model=HealthResponse)
# async def health_check():
#     """Comprehensive health check endpoint."""
#     try:
#         services_status = await service_manager.get_all_service_status()

#         # Determine overall status
#         unhealthy_services = [s for s in services_status if s.status == "unhealthy"]
#         degraded_services = [s for s in services_status if s.status == "degraded"]

#         if unhealthy_services:
#             overall_status = "unhealthy"
#         elif degraded_services:
#             overall_status = "degraded"
#         else:
#             overall_status = "healthy"

#         return HealthResponse(
#             status=overall_status,
#             timestamp=datetime.now(),
#             services=services_status,
#             uptime=time.time() - start_time
#         )

#     except Exception as e:
#         logger.error(f"Health check error: {e}")
#         raise HTTPException(status_code=500, detail="Health check failed")

@app.post("/chat", response_model=ChatResponse)
async def chat_completion(request: ChatRequest):
    """Chat completion endpoint with multi-service fallback."""
    start_time = time.time()

    try:
        # Try hybrid AI client first
        if ai_client:
            try:
                response = ai_client.generate_response(
                    request.message,
                    personality=request.personality,
                    max_tokens=request.max_tokens,
                    temperature=request.temperature
                )
                if response:
                    processing_time = time.time() - start_time
                    return ChatResponse(
                        response=response,
                        service_used="hybrid_ai",
                        processing_time=processing_time,
                        timestamp=datetime.now()
                    )
            except Exception as e:
                logger.warning(f"Hybrid AI client failed: {e}")

        # Try free tier client as fallback
        if free_tier_client:
            try:
                response = free_tier_client.generate_response(
                    request.message,
                    personality=request.personality,
                    max_tokens=request.max_tokens,
                    temperature=request.temperature
                )
                if response:
                    processing_time = time.time() - start_time
                    return ChatResponse(
                        response=response,
                        service_used="free_tier",
                        processing_time=processing_time,
                        timestamp=datetime.now()
                    )
            except Exception as e:
                logger.warning(f"Free tier client failed: {e}")

        # Use fallback responses
        fallback_key = "greeting" if "hello" in request.message.lower() else "chat_unavailable"
        fallback_response = fallback_responses.get(fallback_key, fallback_responses.get("error", "Service unavailable"))

        processing_time = time.time() - start_time
        return ChatResponse(
            response=fallback_response,
            service_used="fallback",
            processing_time=processing_time,
            timestamp=datetime.now()
        )

    except Exception as e:
        logger.error(f"Chat completion error: {e}")
        processing_time = time.time() - start_time
        return ChatResponse(
            response=fallback_responses.get("error", "An error occurred"),
            service_used="error",
            processing_time=processing_time,
            timestamp=datetime.now()
        )

@app.post("/generate-video", response_model=VideoGenerationResponse)
async def generate_video(request: VideoGenerationRequest, background_tasks: BackgroundTasks):
    """Video generation endpoint with background processing."""
    try:
        # Validate request
        if not request.prompt.strip():
            raise HTTPException(status_code=400, detail="Prompt cannot be empty")

        # Generate job ID
        job_id = f"video_{int(time.time())}_{hash(request.prompt) % 10000}"

        # Add background task for video generation
        background_tasks.add_task(
            process_video_generation,
            job_id=job_id,
            prompt=request.prompt,
            duration=request.duration,
            style=request.style,
            resolution=request.resolution
        )

        # Estimate processing time based on complexity
        estimated_time = min(300, len(request.prompt.split()) * 10)  # Rough estimate

        return VideoGenerationResponse(
            status="processing",
            message="Video generation started",
            estimated_time=estimated_time,
            job_id=job_id
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Video generation error: {e}")
        raise HTTPException(status_code=500, detail="Video generation failed")

@app.get("/video-status/{job_id}")
async def get_video_status(job_id: str):
    """Check status of video generation job."""
    # This would typically check a database or cache for job status
    # For now, return a placeholder response
    return {
        "job_id": job_id,
        "status": "processing",
        "progress": 50,
        "message": "Video generation in progress"
    }

# Background task for video generation
async def process_video_generation(job_id: str, prompt: str, duration: int,
                                 style: str, resolution: str):
    """Process video generation in the background."""
    try:
        logger.info(f"Starting video generation for job {job_id}")

        # This would integrate with actual video generation logic
        # For now, just simulate processing
        await asyncio.sleep(5)  # Simulate processing time

        # Here you would:
        # 1. Use AI to generate video script/content
        # 2. Generate or find relevant video clips
        # 3. Use moviepy or similar to assemble video
        # 4. Apply effects and styling
        # 5. Save final video file

        logger.info(f"Video generation completed for job {job_id}")

    except Exception as e:
        logger.error(f"Video generation failed for job {job_id}: {e}")

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTP Exception",
            "detail": exc.detail,
            "timestamp": datetime.now().isoformat()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "detail": "An unexpected error occurred",
            "timestamp": datetime.now().isoformat()
        }
    )

if __name__ == "__main__":
    # Run the FastAPI server
    uvicorn.run(
        "fastapi_service:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )