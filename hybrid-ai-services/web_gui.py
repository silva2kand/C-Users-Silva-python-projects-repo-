from fastapi import FastAPI, Request, Form, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import json
import os
import uvicorn
from pydantic import BaseModel
from hybrid_ai_client import LightweightAIClient
import shutil
from pathlib import Path

# Create directories
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

app = FastAPI(title="🎬 Hybrid AI Video Remaker Web GUI", version="1.0.0")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="templates")

# Initialize AI client
ai_client = LightweightAIClient()

class ChatRequest(BaseModel):
    message: str

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/chat")
async def chat_api(chat_request: ChatRequest):
    try:
        response = await ai_client.generate_response(chat_request.message)
        return {"response": response, "status": "success"}
    except Exception as e:
        return {"response": "Sorry, I encountered an error.", "status": "error", "error": str(e)}

@app.post("/api/upload")
async def upload_video(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(('.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv')):
        return JSONResponse(
            {"error": "Invalid file type. Please upload a video file."},
            status_code=400
        )

    file_path = UPLOAD_DIR / file.filename
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        file_size = file_path.stat().st_size
        return {
            "filename": file.filename,
            "size": file_size,
            "path": str(file_path),
            "status": "uploaded"
        }
    except Exception as e:
        return JSONResponse(
            {"error": f"Failed to upload file: {str(e)}"},
            status_code=500
        )

@app.get("/api/videos")
async def list_videos():
    videos = []
    for file_path in UPLOAD_DIR.glob("*"):
        if file_path.suffix.lower() in ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv']:
            videos.append({
                "name": file_path.name,
                "size": file_path.stat().st_size,
                "path": str(file_path)
            })
    return {"videos": videos}

@app.post("/api/process")
async def process_video(request: Request):
    data = await request.json()
    filename = data.get("filename")
    options = data.get("options", {})

    if not filename:
        return JSONResponse({"error": "No filename provided"}, status_code=400)

    # Simulate video processing
    import asyncio
    await asyncio.sleep(2)  # Simulate processing time

    return {
        "status": "processed",
        "filename": filename,
        "options": options,
        "message": f"Video '{filename}' processed successfully with options: {options}"
    }

if __name__ == "__main__":
    print("🎬 Starting Hybrid AI Video Remaker Web GUI...")
    print("🌐 Open your browser to: http://localhost:8001")
    print("📱 Access the web interface for video processing!")
    uvicorn.run(app, host="0.0.0.0", port=8001)