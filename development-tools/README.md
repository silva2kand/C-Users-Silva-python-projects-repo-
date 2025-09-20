# Development Tools & Launchers

Collection of development environment launchers and IDE tools.

## 🚀 Launchers

### PowerShell AI IDE
- **`Launch_IDE.bat`** - Simple batch launcher for PowerShell AI IDE
- **`Launch_IDE.ps1`** - Advanced PowerShell launcher with error handling and logging

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

## 📋 Requirements

- Windows PowerShell 5.1 or PowerShell 7+
- PowerShell AI IDE installed at: `C:\Users\Silva\ide\GUI\MainWindow.ps1`

## 🎯 Usage

### Quick Launch (Batch)
```cmd
Launch_IDE.bat
```

### Advanced Launch (PowerShell)
```powershell
.\Launch_IDE.ps1
```

### Direct PowerShell Execution
```powershell
powershell -ExecutionPolicy Bypass -File "Launch_IDE.ps1"
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