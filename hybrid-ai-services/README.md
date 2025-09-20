# Hybrid AI Services

Multi-provider AI service integration with FastAPI backend and various client interfaces.

## 🚀 Features

- **Multi-Provider Support**: GPT4All, OpenAI, Google Gemini, Anthropic Claude
- **Fallback Mechanisms**: Automatic failover between providers
- **Multiple Interfaces**: Web GUI, Desktop GUI, FastAPI REST API
- **Docker Support**: Containerized deployment
- **Async Processing**: High-performance async request handling

## 🏗️ Architecture

```
hybrid-ai-services/
├── fastapi_service.py      # Main FastAPI backend service
├── hybrid_ai_client.py     # Multi-provider AI client
├── web_gui.py             # Web-based interface
├── desktop_gui.py         # Desktop PyQt interface
├── desktop_video_remaker.py # Video processing with AI
└── simple_desktop_launcher.py # Quick launcher
```

## 📋 Requirements

```bash
pip install fastapi uvicorn gpt4all openai anthropic google-generativeai PyQt5
```

## 🛠️ Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure API keys:
   ```bash
   export OPENAI_API_KEY="your-key"
   export ANTHROPIC_API_KEY="your-key"
   export GOOGLE_API_KEY="your-key"
   ```

3. Run the FastAPI service:
   ```bash
   python fastapi_service.py
   ```

4. Or use Docker:
   ```bash
   docker build -t hybrid-ai .
   docker run -p 8000:8000 hybrid-ai
   ```

## 🎯 Usage

### FastAPI Service
```bash
python fastapi_service.py
# API available at http://localhost:8000
```

### Web GUI
```bash
python web_gui.py
# Web interface at http://localhost:5000
```

### Desktop GUI
```bash
python desktop_gui.py
```

### Quick Launcher
```bash
python simple_desktop_launcher.py
```

## 📡 API Endpoints

- `POST /chat` - Send chat messages to AI
- `GET /health` - Service health check
- `GET /providers` - List available AI providers

## 🐋 Docker

Build and run with Docker:

```bash
docker build -t hybrid-ai-services .
docker run -p 8000:8000 -e OPENAI_API_KEY="your-key" hybrid-ai-services
```

## 🔧 Configuration

Configure providers and settings in:
- Environment variables
- `fallback_responses.json` - Fallback responses when APIs fail
- Provider-specific config files