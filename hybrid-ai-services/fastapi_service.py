from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
import os
from contextlib import asynccontextmanager
from hybrid_ai_client import HybridAIClient

# Load fallback responses at module level
FALLBACK_RESPONSES_FILE = "fallback_responses.json"

def load_fallback_responses():
    if os.path.exists(FALLBACK_RESPONSES_FILE):
        with open(FALLBACK_RESPONSES_FILE, 'r') as f:
            return json.load(f)
    return []

fallback_responses = load_fallback_responses()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global service_manager
    service_manager = HybridAIClient()
    yield
    # Shutdown
    pass

app = FastAPI(lifespan=lifespan)

class ChatRequest(BaseModel):
    prompt: str

@app.get("/")
async def root():
    return {"message": "Hybrid AI Video Remaker API", "status": "running"}

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        response = await service_manager.generate_response(request.prompt)
        return {"response": response, "source": "ai"}
    except Exception as e:
        # Fallback to random response
        if fallback_responses:
            import random
            fallback = random.choice(fallback_responses)
            return {"response": fallback, "source": "fallback", "error": str(e)}
        return {"response": "Sorry, I'm unable to generate a response right now.", "source": "error", "error": str(e)}