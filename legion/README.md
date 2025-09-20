# 🧠 Legion - AI Agent Swarm for Code Intelligence

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/legion-ai/legion)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-red.svg)](https://opensource.org/licenses/MIT)

**Legion is not a monolith. It's an orchestrator for a swarm of single-purpose, lightweight AI agents that perform discrete coding tasks and are destroyed after completion.**

## ✨ Features

- 🤖 **Agent Swarm Architecture** - Specialized agents for different coding tasks
- 🧠 **Multi-Provider LLM Support** - Ollama, OpenAI, Anthropic, Google with automatic fallback
- 📊 **Real-time Dashboard** - Web-based monitoring interface with live updates
- 🎯 **Context-Aware Intelligence** - Project-wide code understanding with vector search
- 🔄 **Centralized Journaling** - Complete audit trail with rollback capabilities
- 🎤 **Voice Narration** - Optional TTS feedback for important events
- ⚡ **Offline-First** - Works with local models, cloud as fallback
- 🛠️ **CLI Interface** - Command-line access to all functionality
- 🔧 **Extensible Plugin System** - Easy to add new agents and capabilities

## 🏗️ Architecture

```
legion/
├── __init__.py                 # Package initialization
├── cli.py                      # Command Line Interface
├── core.py                     # LegionCore - Main orchestrator
├── model_manager.py            # Unified LLM API abstraction
├── context_engine.py           # Project-wide context management
├── journal.py                  # Centralized logging & narration
├── message_bus.py              # Inter-agent communication
├── orchestrator.py             # Agent chain orchestration
├── agents/                     # Agent implementations
│   ├── __init__.py
│   ├── base_agent.py           # Abstract base agent
│   ├── completion_agent.py     # Code completion specialist
│   ├── context_agent.py        # Context gathering specialist
│   ├── refactor_agent.py       # Refactoring specialist
│   ├── testgen_agent.py        # Test generation specialist
│   ├── review_agent.py         # Code review specialist
│   ├── narrator_agent.py       # Voice feedback specialist
│   └── fixer_shell.py          # Error fixing specialist
├── config/                     # Configuration management
│   └── default.yaml            # Default settings
├── dashboard/                  # Web monitoring interface
│   ├── app.py                  # Flask application
│   └── templates/
│       └── index.html          # Dashboard template
└── utils/                      # Utility functions
    └── helpers.py
```

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/legion-ai/legion.git
cd legion

# Install dependencies
pip install -r requirements.txt

# Or install as a package
pip install -e .
```

### 2. Initialize Legion in Your Project

```bash
# Navigate to your project
cd /path/to/your/project

# Initialize Legion
legion init
```

### 3. Configure Your Environment

Edit `~/.legion/config.yaml`:

```yaml
models:
  ollama:
    enabled: true
    host: "http://localhost:11434"
    model: "codellama:7b"
  openai:
    enabled: false
    api_key: "your-openai-key"
```

### 4. Start Using Legion

```bash
# Complete code
legion complete_code --file src/app.py --code "def get_user(id):"

# Refactor code
legion refactor_code --file utils/helpers.py

# Review code quality
legion review_code --file app.py

# Generate tests
legion generate_tests --file calculator.py

# Explain code
legion explain_code --file complex_module.py --line 42
```

## 🎯 Available Tasks

| Task | Description | Example |
|------|-------------|---------|
| `complete_code` | Generate code completions | `legion complete_code --file app.py --code "def "` |
| `refactor_code` | Improve code structure | `legion refactor_code --file utils.py` |
| `review_code` | Quality assessment | `legion review_code --file main.py` |
| `generate_tests` | Create unit tests | `legion generate_tests --file calculator.py` |
| `explain_code` | Code explanation | `legion explain_code --file complex.py --line 15` |
| `find_bugs` | Bug detection | `legion find_bugs --file app.py` |
| `fix_errors` | Error correction | `legion fix_errors --file broken.py` |

## 🔧 Configuration

### Default Configuration (`config/default.yaml`)

```yaml
# Model Configuration
models:
  ollama:
    enabled: true
    host: "http://localhost:11434"
    model: "codellama:7b"
  openai:
    enabled: false
    model: "gpt-4"
  anthropic:
    enabled: false
    model: "claude-3-sonnet-20240229"
  google:
    enabled: false
    model: "gemini-pro"

# Journal Configuration
journal:
  enabled: true
  path: "./.legion/logs"
  max_entries: 10000

# Context Engine
context_engine:
  vector_db: "chromadb"
  index_all_files: true
  max_context_length: 4000

# Dashboard
dashboard:
  enabled: false
  host: "localhost"
  port: 8080
```

### User Profile (`~/.legion/user_profile.yaml`)

```yaml
coding_style: "concise"
language: "en"
experience_level: "intermediate"
preferred_languages: ["python", "javascript"]
auto_apply_suggestions: false
```

## 📊 Dashboard

Start the real-time monitoring dashboard:

```bash
legion dashboard
```

Then open http://localhost:8080 in your browser.

Features:
- ✅ Live activity feed
- ✅ Active agents monitoring
- ✅ System status overview
- ✅ Real-time metrics
- ✅ WebSocket-based updates

## 🧪 Agent Development

### Creating a New Agent

1. Create a new file in `legion/agents/`
2. Inherit from `BaseAgent`
3. Implement the `execute()` method

```python
from .base_agent import BaseAgent

class MyCustomAgent(BaseAgent):
    def __init__(self, message_bus, journal, context=None, model_manager=None):
        super().__init__(message_bus, journal, context, model_manager)
        self.capabilities = ["my_custom_task"]

    def execute(self) -> Dict[str, Any]:
        # Your agent logic here
        result = {"action": "my_custom_task", "output": "Task completed"}
        return result
```

4. Register the agent in the orchestrator

## 🔌 API Integration

### Programmatic Usage

```python
from legion import LegionCore

# Initialize Legion
legion = LegionCore(project_root="/path/to/project", config=my_config)

# Execute a task
result = await legion.request("complete_code", {
    "file_path": "src/app.py",
    "code": "def hello():",
    "task_description": "Complete the hello function"
})

print(result)
```

### REST API

```python
from fastapi import FastAPI
from legion import LegionCore

app = FastAPI()
legion = LegionCore()

@app.post("/api/execute")
async def execute_task(task: str, context: dict):
    result = await legion.request(task, context)
    return result
```

## 🎤 Voice Features

Enable voice narration for important events:

```yaml
# In config
narration:
  enabled: true
  language: "en"
  voice_speed: 1.0
  voice_pitch: 1.0
```

## 🔒 Security & Privacy

- **Local-First**: All code analysis happens locally
- **No Data Transmission**: Code never leaves your machine
- **API Key Management**: Secure storage of cloud API keys
- **Audit Trail**: Complete logging of all operations

## 📈 Performance

- **Lazy Loading**: Agents loaded only when needed
- **Connection Pooling**: Efficient LLM API management
- **Caching**: Context and model responses cached
- **Async Operations**: Non-blocking task execution

## 🛠️ Development

### Running Tests

```bash
pytest tests/
```

### Code Quality

```bash
# Format code
black legion/

# Lint code
flake8 legion/

# Type checking
mypy legion/
```

### Building Documentation

```bash
sphinx-build docs/ docs/_build/
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

### Adding New Agents

1. Follow the agent development guide above
2. Add comprehensive tests
3. Update documentation
4. Add to the CLI task mapping

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with inspiration from modern AI agent architectures
- Uses best practices from software engineering and AI research
- Community contributions and feedback welcome

## 📞 Support

- 📧 Email: legion@example.com
- 🐛 Issues: [GitHub Issues](https://github.com/legion-ai/legion/issues)
- 📖 Documentation: [Read the Docs](https://legion-ai.readthedocs.io/)

---

**Ready to revolutionize your coding workflow? Join the Legion swarm! 🚀**
- Local LLM (Ollama recommended)
- Vector database (ChromaDB)

## License
MIT License - See LICENSE file for details