# Smart AI IDE - Unified Launcher (Simple Version)
# Single GUI interface for all services

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$Global:Services = @{
    Backend = @{ Path = "C:\Users\Silva\Desktop\smart-ai-ide-integrated\backend"; Command = "npm run dev"; Port = 3001; Process = $null }
    Frontend = @{ Path = "C:\Users\Silva\Desktop\smart-ai-ide-integrated\frontend"; Command = "pnpm dev"; Port = 3000; Process = $null }
    Security = @{ Path = "C:\Users\Silva\Desktop\smart-ai-ide-integrated\security\node"; Command = "npm start"; Port = $null; Process = $null }
}

$Global:LogBox = $null

function Write-ToLog {
    param([string]$Message)
    $timestamp = Get-Date -Format "HH:mm:ss"
    $logLine = "[$timestamp] $Message"
    
    if ($Global:LogBox) {
        $Global:LogBox.AppendText("$logLine`r`n")
        $Global:LogBox.ScrollToCaret()
    }
    Write-Host $logLine
}

function Test-ServicePort {
    param([int]$Port)
    if (!$Port) { return $false }
    try {
        $tcp = New-Object System.Net.Sockets.TcpClient
        $result = $tcp.ConnectAsync("localhost", $Port).Wait(1000)
        $tcp.Close()
        return $result
    } catch { return $false }
}

function Start-ServiceProcess {
    param([string]$ServiceName)
    
    $service = $Global:Services[$ServiceName]
    if ($service.Process -and !$service.Process.HasExited) {
        Write-ToLog "$ServiceName is already running"
        return
    }
    
    Write-ToLog "Starting $ServiceName..."
    
    try {
        $psi = New-Object System.Diagnostics.ProcessStartInfo
        $psi.FileName = "powershell.exe"
        $psi.Arguments = "-NoExit -Command `"Set-Location '$($service.Path)'; $($service.Command)`""
        $psi.UseShellExecute = $true
        $psi.WindowStyle = "Minimized"
        
        $service.Process = [System.Diagnostics.Process]::Start($psi)
        Write-ToLog "$ServiceName started (PID: $($service.Process.Id))"
        
        Start-Sleep -Seconds 2
        
        if ($service.Port -and (Test-ServicePort -Port $service.Port)) {
            Write-ToLog "$ServiceName is running on port $($service.Port)"
        }
        
    } catch {
        Write-ToLog "Failed to start $ServiceName : $($_.Exception.Message)"
    }
}

function Stop-ServiceProcess {
    param([string]$ServiceName)
    
    $service = $Global:Services[$ServiceName]
    if (!$service.Process -or $service.Process.HasExited) {
        Write-ToLog "$ServiceName is not running"
        return
    }
    
    Write-ToLog "Stopping $ServiceName..."
    try {
        $service.Process.Kill()
        $service.Process = $null
        Write-ToLog "$ServiceName stopped"
    } catch {
        Write-ToLog "Failed to stop $ServiceName : $($_.Exception.Message)"
    }
}

# Create GUI
$form = New-Object System.Windows.Forms.Form
$form.Text = "Smart AI IDE - HoloB1.5 Launcher"
$form.Size = New-Object System.Drawing.Size(900, 600)
$form.StartPosition = "CenterScreen"
$form.BackColor = [System.Drawing.Color]::LightGray

# Title
$title = New-Object System.Windows.Forms.Label
$title.Text = "Smart AI IDE - HoloB1.5 Floating AI Runtime"
$title.Size = New-Object System.Drawing.Size(850, 30)
$title.Location = New-Object System.Drawing.Point(25, 20)
$title.Font = New-Object System.Drawing.Font("Arial", 14, [System.Drawing.FontStyle]::Bold)
$title.ForeColor = [System.Drawing.Color]::DarkBlue
$form.Controls.Add($title)

# Services Panel
$servicesPanel = New-Object System.Windows.Forms.GroupBox
$servicesPanel.Text = "Services Control"
$servicesPanel.Size = New-Object System.Drawing.Size(850, 150)
$servicesPanel.Location = New-Object System.Drawing.Point(25, 60)
$form.Controls.Add($servicesPanel)

# Backend Service
$backendLabel = New-Object System.Windows.Forms.Label
$backendLabel.Text = "Backend (Smart AI IDE API) - Port 3001"
$backendLabel.Size = New-Object System.Drawing.Size(300, 20)
$backendLabel.Location = New-Object System.Drawing.Point(20, 30)
$servicesPanel.Controls.Add($backendLabel)

$backendBtn = New-Object System.Windows.Forms.Button
$backendBtn.Text = "Start Backend"
$backendBtn.Size = New-Object System.Drawing.Size(100, 30)
$backendBtn.Location = New-Object System.Drawing.Point(350, 25)
$backendBtn.Add_Click({
    if ($this.Text -eq "Start Backend") {
        Start-ServiceProcess -ServiceName "Backend"
        $this.Text = "Stop Backend"
        $this.BackColor = [System.Drawing.Color]::IndianRed
    } else {
        Stop-ServiceProcess -ServiceName "Backend"
        $this.Text = "Start Backend"
        $this.BackColor = [System.Drawing.SystemColors]::Control
    }
})
$servicesPanel.Controls.Add($backendBtn)

# Frontend Service
$frontendLabel = New-Object System.Windows.Forms.Label
$frontendLabel.Text = "Frontend (Next.js + HoloB1.5) - Port 3000"
$frontendLabel.Size = New-Object System.Drawing.Size(300, 20)
$frontendLabel.Location = New-Object System.Drawing.Point(20, 70)
$servicesPanel.Controls.Add($frontendLabel)

$frontendBtn = New-Object System.Windows.Forms.Button
$frontendBtn.Text = "Start Frontend"
$frontendBtn.Size = New-Object System.Drawing.Size(100, 30)
$frontendBtn.Location = New-Object System.Drawing.Point(350, 65)
$frontendBtn.Add_Click({
    if ($this.Text -eq "Start Frontend") {
        Start-ServiceProcess -ServiceName "Frontend"
        $this.Text = "Stop Frontend"
        $this.BackColor = [System.Drawing.Color]::IndianRed
    } else {
        Stop-ServiceProcess -ServiceName "Frontend"
        $this.Text = "Start Frontend"
        $this.BackColor = [System.Drawing.SystemColors]::Control
    }
})
$servicesPanel.Controls.Add($frontendBtn)

# Security Service
$securityLabel = New-Object System.Windows.Forms.Label
$securityLabel.Text = "Security (AI Firewall)"
$securityLabel.Size = New-Object System.Drawing.Size(300, 20)
$securityLabel.Location = New-Object System.Drawing.Point(20, 110)
$servicesPanel.Controls.Add($securityLabel)

$securityBtn = New-Object System.Windows.Forms.Button
$securityBtn.Text = "Start Security"
$securityBtn.Size = New-Object System.Drawing.Size(100, 30)
$securityBtn.Location = New-Object System.Drawing.Point(350, 105)
$securityBtn.Add_Click({
    if ($this.Text -eq "Start Security") {
        Start-ServiceProcess -ServiceName "Security"
        $this.Text = "Stop Security"
        $this.BackColor = [System.Drawing.Color]::IndianRed
    } else {
        Stop-ServiceProcess -ServiceName "Security"
        $this.Text = "Start Security"
        $this.BackColor = [System.Drawing.SystemColors]::Control
    }
})
$servicesPanel.Controls.Add($securityBtn)

# Quick Actions
$actionsPanel = New-Object System.Windows.Forms.GroupBox
$actionsPanel.Text = "Quick Actions"
$actionsPanel.Size = New-Object System.Drawing.Size(850, 80)
$actionsPanel.Location = New-Object System.Drawing.Point(25, 220)
$form.Controls.Add($actionsPanel)

# Start All Button
$startAllBtn = New-Object System.Windows.Forms.Button
$startAllBtn.Text = "Start All Services"
$startAllBtn.Size = New-Object System.Drawing.Size(120, 40)
$startAllBtn.Location = New-Object System.Drawing.Point(20, 25)
$startAllBtn.BackColor = [System.Drawing.Color]::LightGreen
$startAllBtn.Add_Click({
    Write-ToLog "Starting all services..."
    Start-ServiceProcess -ServiceName "Backend"
    Start-Sleep -Seconds 4
    Start-ServiceProcess -ServiceName "Security" 
    Start-Sleep -Seconds 2
    Start-ServiceProcess -ServiceName "Frontend"
    Write-ToLog "All services started! Visit http://localhost:3000"
})
$actionsPanel.Controls.Add($startAllBtn)

# Stop All Button
$stopAllBtn = New-Object System.Windows.Forms.Button
$stopAllBtn.Text = "Stop All Services"
$stopAllBtn.Size = New-Object System.Drawing.Size(120, 40)
$stopAllBtn.Location = New-Object System.Drawing.Point(160, 25)
$stopAllBtn.BackColor = [System.Drawing.Color]::LightCoral
$stopAllBtn.Add_Click({
    Write-ToLog "Stopping all services..."
    Stop-ServiceProcess -ServiceName "Frontend"
    Stop-ServiceProcess -ServiceName "Backend" 
    Stop-ServiceProcess -ServiceName "Security"
})
$actionsPanel.Controls.Add($stopAllBtn)

# Open Browser Button
$openBtn = New-Object System.Windows.Forms.Button
$openBtn.Text = "Open Smart IDE"
$openBtn.Size = New-Object System.Drawing.Size(120, 40)
$openBtn.Location = New-Object System.Drawing.Point(300, 25)
$openBtn.BackColor = [System.Drawing.Color]::CornflowerBlue
$openBtn.Add_Click({
    Start-Process "http://localhost:3000"
})
$actionsPanel.Controls.Add($openBtn)

# HoloB1.5 Info Button
$holoBtn = New-Object System.Windows.Forms.Button
$holoBtn.Text = "HoloB1.5 Info"
$holoBtn.Size = New-Object System.Drawing.Size(120, 40)
$holoBtn.Location = New-Object System.Drawing.Point(440, 25)
$holoBtn.BackColor = [System.Drawing.Color]::MediumOrchid
$holoBtn.Add_Click({
    $msg = "HoloB1.5 Floating AI Bot Runtime" + "`n`n" +
           "Features:" + "`n" +
           "- Mouse-following AI bot" + "`n" +
           "- Click-to-chat interface" + "`n" +
           "- 4 AI personalities" + "`n" +
           "- Smart AI IDE integration" + "`n" +
           "- Context-aware responses" + "`n`n" +
           "Visit http://localhost:3000 to see it in action!"
    [System.Windows.Forms.MessageBox]::Show($msg, "HoloB1.5 Info", "OK", "Information")
})
$actionsPanel.Controls.Add($holoBtn)

# Chat with AI Button
$chatBtn = New-Object System.Windows.Forms.Button
$chatBtn.Text = "Chat with AI"
$chatBtn.Size = New-Object System.Drawing.Size(120, 40)
$chatBtn.Location = New-Object System.Drawing.Point(580, 25)
$chatBtn.BackColor = [System.Drawing.Color]::Gold
$chatBtn.Add_Click({
    # Create simple chat dialog
    $chatForm = New-Object System.Windows.Forms.Form
    $chatForm.Text = "HoloB1.5 Chat - Desktop Version"
    $chatForm.Size = New-Object System.Drawing.Size(400, 300)
    $chatForm.StartPosition = "CenterParent"
    
    $chatOutput = New-Object System.Windows.Forms.TextBox
    $chatOutput.Multiline = $true
    $chatOutput.ScrollBars = "Vertical"
    $chatOutput.Size = New-Object System.Drawing.Size(370, 180)
    $chatOutput.Location = New-Object System.Drawing.Point(10, 10)
    $chatOutput.ReadOnly = $true
    $chatOutput.BackColor = [System.Drawing.Color]::Black
    $chatOutput.ForeColor = [System.Drawing.Color]::Lime
    $chatOutput.Font = New-Object System.Drawing.Font("Consolas", 9)
    $chatForm.Controls.Add($chatOutput)
    
    $chatInput = New-Object System.Windows.Forms.TextBox
    $chatInput.Size = New-Object System.Drawing.Size(280, 25)
    $chatInput.Location = New-Object System.Drawing.Point(10, 200)
    $chatForm.Controls.Add($chatInput)
    
    $sendBtn = New-Object System.Windows.Forms.Button
    $sendBtn.Text = "Send"
    $sendBtn.Size = New-Object System.Drawing.Size(60, 25)
    $sendBtn.Location = New-Object System.Drawing.Point(300, 200)
    $chatForm.Controls.Add($sendBtn)
    
    # Welcome message
    $chatOutput.AppendText("HoloB1.5 Desktop Chat`r`n")
    $chatOutput.AppendText("Assistant: Hello! I'm your desktop AI assistant. How can I help?`r`n`r`n")
    
    # Send button click
    $sendBtn.Add_Click({
        $userInput = $chatInput.Text.Trim()
        if ($userInput) {
            $chatOutput.AppendText("You: $userInput`r`n")
            $chatInput.Text = ""
            
            # Simple AI responses (placeholder - would connect to backend in full version)
            $responses = @(
                "That's an interesting question! Let me think about that.",
                "I can help you with that. What specific aspect would you like to explore?",
                "Based on your Smart AI IDE setup, I'd recommend checking the documentation.",
                "Great idea! The HoloB1.5 system is designed to handle that kind of task.",
                "I'm processing your request. Would you like me to break this down into steps?"
            )
            $response = $responses | Get-Random
            $chatOutput.AppendText("Assistant: $response`r`n`r`n")
            $chatOutput.ScrollToCaret()
        }
    })
    
    # Enter key support
    $chatInput.Add_KeyPress({
        if ($_.KeyChar -eq [char]13) { # Enter key
            $sendBtn.PerformClick()
        }
    })
    
    $chatForm.ShowDialog()
})
$actionsPanel.Controls.Add($chatBtn)

# Log Output
$logLabel = New-Object System.Windows.Forms.Label
$logLabel.Text = "Service Logs:"
$logLabel.Size = New-Object System.Drawing.Size(200, 20)
$logLabel.Location = New-Object System.Drawing.Point(25, 315)
$form.Controls.Add($logLabel)

$Global:LogBox = New-Object System.Windows.Forms.TextBox
$Global:LogBox.Multiline = $true
$Global:LogBox.ScrollBars = "Vertical"
$Global:LogBox.Size = New-Object System.Drawing.Size(850, 200)
$Global:LogBox.Location = New-Object System.Drawing.Point(25, 340)
$Global:LogBox.Font = New-Object System.Drawing.Font("Consolas", 9)
$Global:LogBox.BackColor = [System.Drawing.Color]::Black
$Global:LogBox.ForeColor = [System.Drawing.Color]::Lime
$Global:LogBox.ReadOnly = $true
$form.Controls.Add($Global:LogBox)

# Welcome message
Write-ToLog "Smart AI IDE Launcher ready!"
Write-ToLog "HoloB1.5 Floating AI Bot Runtime v1.5"
Write-ToLog "Click 'Start All Services' to launch everything"

# Cleanup on close
$form.Add_FormClosed({
    Write-ToLog "Shutting down services..."
    foreach ($service in $Global:Services.Values) {
        if ($service.Process -and !$service.Process.HasExited) {
            $service.Process.Kill()
        }
    }
})

# Show the form
[System.Windows.Forms.Application]::Run($form)