# Development Tools & Launchers

Collection of development environment launchers and IDE tools.

## 🚀 Launchers

### PowerShell AI IDE
- **`Launch_IDE.bat`** - Simple batch launcher for PowerShell AI IDE
- **`Launch_IDE.ps1`** - Advanced PowerShell launcher with error handling and logging
- **`PowerShell-AI-IDE-Shortcut.bat`** - Recreates PowerShell AI IDE.lnk functionality

### Smart AI IDE
- **`Smart-AI-IDE-Shortcut.bat`** - Recreates Smart AI IDE.lnk functionality  
- **`Smart-AI-IDE-Shortcut.ps1`** - PowerShell version with enhanced error handling
- **`Smart-AI-IDE-FAST.bat`** - Fast launcher with multi-API AI agent support
- **`Smart-AI-IDE-Launcher.bat`** - Main Smart AI IDE launcher
- **`launch-smart-ai-ide.ps1`** - PowerShell Smart AI IDE launcher

### Smart AI IDE Integrated
- **`launch-smart-ide.ps1`** - Integrated Smart IDE launcher
- **`start-all-services.ps1`** - Launch all services at once
- **`start-smart-ide.bat`** - Batch launcher for integrated Smart IDE
- **`holo-desktop.ps1`** - HoloLens-style desktop interface
- **`holo-voice-desktop.ps1`** - Voice-enabled holo desktop

### AI Assistant
- **`AI_Assistant_Launcher.vbs`** - VBScript launcher (silent execution)
- **`Start_AI_Assistant.bat`** - Batch launcher for AI Assistant
- **`AI-Assistant-Launcher-Shortcut.bat`** - Recreates VBScript functionality

### Hybrid AI Video Remaker
- **`Launch_Video_AI.ps1`** - PowerShell launcher for video AI
- **`Hybrid-AI-Video-Remaker-Shortcut.bat`** - Recreates shortcut functionality

### Development Setup
- **`setup-smart-ai-ide.js`** - Node.js setup script for Smart AI IDE integration

## 🛠️ Features

### PowerShell AI IDE
- Quick launch via batch file
- Bypasses PowerShell execution policy
- Comprehensive error checking
- Colored console output and logging

### Smart AI IDE Family
- **Multi-API AI agent**: 5 free tier APIs with auto-switching
- **Voice support**: Conversational AI with speech capabilities
- **Auto-fix agent**: Validates and fixes code until 100% perfect
- **Desktop GUI**: Standalone operation in Edge/Chrome/default browser
- **Port management**: Automatic cleanup and process management
- **Fast mode**: Skip dependency checks for quick startup

### AI Assistant Tools
- **Silent execution**: VBScript launcher runs without console windows
- **Python integration**: Direct execution of AI assistant Python scripts
- **Error handling**: Fallback mechanisms for missing files
- **Desktop automation**: Full desktop AI assistant capabilities

### Hybrid AI Video Remaker
- **Video processing**: AI-powered video editing and enhancement
- **Streaming support**: Real-time video processing capabilities
- **File processing**: Batch video operations
- **AI generation**: AI-assisted video creation

### Smart AI IDE Integrated
- **HoloLens interface**: 3D desktop experience
- **Voice control**: Voice-enabled desktop interactions
- **Multi-service**: Launch all integrated services simultaneously
- **Gaming elements**: Halo-inspired interface components

### Development Setup
- **Project integration**: Combines multiple IDE components
- **Authentication bridge**: Unified auth across services
- **Security layer**: SuperAgent firewall integration
- **Database setup**: Automated database configuration
- **Environment config**: Automated environment variable setup

## 📋 Requirements

- Windows PowerShell 5.1 or PowerShell 7+
- Python 3.8+ (for AI Assistant and video processing)
- Node.js 16+ (for Smart AI IDE and setup scripts)
- Modern web browser (Edge, Chrome, Firefox)

### Specific Requirements by Tool:
- **PowerShell AI IDE**: `C:\Users\Silva\ide\GUI\MainWindow.ps1`
- **Smart AI IDE**: `C:\Users\Silva\Documents\smart-ai-ide\`
- **AI Assistant**: `C:\Users\Silva\Documents\desktop_ai_assistant_final.py`
- **Video Remaker**: `C:\Users\Silva\hybrid_ai_video_remaker\`
- **Smart IDE Integrated**: `C:\Users\Silva\Desktop\smart-ai-ide-integrated\`

## 🎯 Usage

### PowerShell AI IDE

#### Quick Launch (Batch)
```cmd
Launch_IDE.bat
```

#### Advanced Launch (PowerShell)
```powershell
.\Launch_IDE.ps1
```

### Smart AI IDE

#### Quick Launch (Shortcut Recreation)
```cmd
Smart-AI-IDE-Shortcut.bat
```

#### PowerShell Launch
```powershell
.\Smart-AI-IDE-Shortcut.ps1
```

#### Direct Fast Launch
```cmd
Smart-AI-IDE-FAST.bat
```

#### Advanced PowerShell Launch
```powershell
.\launch-smart-ai-ide.ps1
```

### Direct PowerShell Execution
```powershell
powershell -ExecutionPolicy Bypass -File "Launch_IDE.ps1"
powershell -ExecutionPolicy Bypass -File "Smart-AI-IDE-Shortcut.ps1"
```

## ⚙️ Configuration

Edit the launcher files to modify:
- IDE file paths
- Console colors
- Error handling behavior
- Logging preferences

## 🔧 Troubleshooting

### Common Issues:
1. **IDE file not found**: Update the path in the launcher scripts
2. **Execution policy errors**: Use the batch launcher or run as administrator
3. **Permission issues**: Check file permissions and user rights

### Solutions:
- Ensure PowerShell AI IDE is properly installed
- Verify file paths in launcher scripts
- Run launchers as administrator if needed