# Development Tools & Launchers

Collection of development environment launchers and IDE tools.

## 🚀 Launchers

### PowerShell AI IDE
- **`Launch_IDE.bat`** - Simple batch launcher for PowerShell AI IDE
- **`Launch_IDE.ps1`** - Advanced PowerShell launcher with error handling and logging

### Smart AI IDE
- **`Smart-AI-IDE-Shortcut.bat`** - Recreates Smart AI IDE.lnk functionality  
- **`Smart-AI-IDE-Shortcut.ps1`** - PowerShell version with enhanced error handling
- **`Smart-AI-IDE-FAST.bat`** - Fast launcher with multi-API AI agent support
- **`Smart-AI-IDE-Launcher.bat`** - Main Smart AI IDE launcher
- **`launch-smart-ai-ide.ps1`** - PowerShell Smart AI IDE launcher

## 🛠️ Features

### Launch_IDE.bat
- Quick launch via batch file
- Bypasses PowerShell execution policy
- Simple pause for error viewing

### Launch_IDE.ps1  
- Comprehensive error checking
- Colored console output
- Path validation
- Detailed logging
- Graceful error handling

### Smart AI IDE Launchers
- **Smart-AI-IDE-FAST.bat**: Multi-API AI agent with 5 free tier APIs
- **Auto-switching**: Automatic failover between AI providers
- **Voice support**: Conversational AI with speech capabilities
- **Auto-fix agent**: Validates and fixes code until 100% perfect
- **Desktop GUI**: Standalone operation with AI simulation
- **Port management**: Automatic cleanup and process management

### Smart AI IDE Features
- 🤖 Multi-API AI Development Agent (5 APIs available)
- 💬 Conversational AI with voice support
- 🔍 Auto-fix agent for code validation
- 🖥️ Desktop GUI in Edge/Chrome/default browser
- ⚡ Fast mode: Skip dependency checks
- 🧹 Automatic port cleanup and process management

## 📋 Requirements

- Windows PowerShell 5.1 or PowerShell 7+
- PowerShell AI IDE installed at: `C:\Users\Silva\ide\GUI\MainWindow.ps1`
- Smart AI IDE installed at: `C:\Users\Silva\Documents\smart-ai-ide\`
- Node.js (for Smart AI IDE features)
- Modern web browser (Edge, Chrome, Firefox)

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