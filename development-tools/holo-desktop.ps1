# HoloB1.5 Desktop - Floating AI Bot for Windows Desktop
# Standalone desktop version that works outside the browser

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
Add-Type @"
using System;
using System.Runtime.InteropServices;
using System.Windows.Forms;
public class Win32 {
    [DllImport("user32.dll")]
    public static extern bool GetCursorPos(out POINT lpPoint);
    
    [DllImport("user32.dll")]
    public static extern IntPtr GetForegroundWindow();
    
    [DllImport("user32.dll")]
    public static extern bool SetWindowPos(IntPtr hWnd, IntPtr hWndInsertAfter, int X, int Y, int cx, int cy, uint uFlags);
    
    public static readonly IntPtr HWND_TOPMOST = new IntPtr(-1);
    public static readonly uint SWP_NOMOVE = 0x0002;
    public static readonly uint SWP_NOSIZE = 0x0001;
    
    public struct POINT {
        public int x;
        public int y;
    }
}
"@

$Global:HoloForm = $null
$Global:ChatForm = $null
$Global:MouseTimer = $null
$Global:ChatVisible = $false
$Global:BotSize = 50

function Get-MousePosition {
    $point = New-Object Win32+POINT
    [Win32]::GetCursorPos([ref]$point) | Out-Null
    return @{ X = $point.x; Y = $point.y }
}

function Update-BotPosition {
    if ($Global:HoloForm -and !$Global:ChatVisible) {
        $mousePos = Get-MousePosition
        
        # Position bot slightly offset from cursor
        $botX = $mousePos.X + 20
        $botY = $mousePos.Y - 20
        
        # Keep bot within screen bounds
        $screen = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
        if ($botX + $Global:BotSize -gt $screen.Width) { $botX = $screen.Width - $Global:BotSize }
        if ($botY -lt 0) { $botY = 0 }
        
        $Global:HoloForm.Location = New-Object System.Drawing.Point($botX, $botY)
    }
}

function Show-HoloChat {
    if ($Global:ChatForm) {
        $Global:ChatForm.Close()
    }
    
    $Global:ChatVisible = $true
    
    # Position chat at top-right of screen
    $screen = [System.Windows.Forms.Screen]::PrimaryScreen.WorkingArea
    $chatX = $screen.Width - 350
    $chatY = 50
    
    $Global:ChatForm = New-Object System.Windows.Forms.Form
    $Global:ChatForm.Text = "HoloB1.5 Desktop Chat"
    $Global:ChatForm.Size = New-Object System.Drawing.Size(340, 450)
    $Global:ChatForm.Location = New-Object System.Drawing.Point($chatX, $chatY)
    $Global:ChatForm.TopMost = $true
    $Global:ChatForm.FormBorderStyle = [System.Windows.Forms.FormBorderStyle]::FixedToolWindow
    $Global:ChatForm.BackColor = [System.Drawing.Color]::DarkSlateBlue
    
    # Chat header
    $header = New-Object System.Windows.Forms.Label
    $header.Text = "HoloB1.5 Desktop Assistant"
    $header.Size = New-Object System.Drawing.Size(300, 25)
    $header.Location = New-Object System.Drawing.Point(10, 10)
    $header.ForeColor = [System.Drawing.Color]::White
    $header.Font = New-Object System.Drawing.Font("Arial", 10, [System.Drawing.FontStyle]::Bold)
    $Global:ChatForm.Controls.Add($header)
    
    # Chat output
    $chatOutput = New-Object System.Windows.Forms.RichTextBox
    $chatOutput.Size = New-Object System.Drawing.Size(310, 300)
    $chatOutput.Location = New-Object System.Drawing.Point(10, 40)
    $chatOutput.BackColor = [System.Drawing.Color]::Black
    $chatOutput.ForeColor = [System.Drawing.Color]::Lime
    $chatOutput.Font = New-Object System.Drawing.Font("Consolas", 9)
    $chatOutput.ReadOnly = $true
    $chatOutput.ScrollBars = "Vertical"
    $Global:ChatForm.Controls.Add($chatOutput)
    
    # Input area
    $inputPanel = New-Object System.Windows.Forms.Panel
    $inputPanel.Size = New-Object System.Drawing.Size(310, 50)
    $inputPanel.Location = New-Object System.Drawing.Point(10, 350)
    $inputPanel.BackColor = [System.Drawing.Color]::Transparent
    $Global:ChatForm.Controls.Add($inputPanel)
    
    $chatInput = New-Object System.Windows.Forms.TextBox
    $chatInput.Size = New-Object System.Drawing.Size(230, 25)
    $chatInput.Location = New-Object System.Drawing.Point(0, 15)
    $chatInput.Font = New-Object System.Drawing.Font("Arial", 9)
    $inputPanel.Controls.Add($chatInput)
    
    $sendBtn = New-Object System.Windows.Forms.Button
    $sendBtn.Text = "Send"
    $sendBtn.Size = New-Object System.Drawing.Size(60, 25)
    $sendBtn.Location = New-Object System.Drawing.Point(240, 15)
    $sendBtn.BackColor = [System.Drawing.Color]::CornflowerBlue
    $sendBtn.ForeColor = [System.Drawing.Color]::White
    $inputPanel.Controls.Add($sendBtn)
    
    # Close button
    $closeBtn = New-Object System.Windows.Forms.Button
    $closeBtn.Text = "×"
    $closeBtn.Size = New-Object System.Drawing.Size(25, 25)
    $closeBtn.Location = New-Object System.Drawing.Point(305, 10)
    $closeBtn.BackColor = [System.Drawing.Color]::IndianRed
    $closeBtn.ForeColor = [System.Drawing.Color]::White
    $closeBtn.Font = New-Object System.Drawing.Font("Arial", 12, [System.Drawing.FontStyle]::Bold)
    $closeBtn.Add_Click({
        $Global:ChatForm.Close()
        $Global:ChatVisible = $false
    })
    $Global:ChatForm.Controls.Add($closeBtn)
    
    # Welcome message
    $welcome = "HoloB1.5 Desktop Assistant Ready!`n`n" +
               "🤖 I'm your floating AI assistant`n" +
               "💬 Ask me anything or give me tasks`n" +
               "🔧 I can help with your Smart AI IDE`n" +
               "✨ Type your message below`n`n"
    $chatOutput.AppendText($welcome)
    
    # Handle sending messages
    $sendMessage = {
        $userInput = $chatInput.Text.Trim()
        if ($userInput) {
            $chatOutput.AppendText("You: $userInput`n")
            $chatInput.Text = ""
            
            # AI Response logic (placeholder - could connect to backend)
            $responses = @{
                "hello" = "Hello! I'm HoloB1.5, your desktop AI assistant. How can I help you today?"
                "help" = "I can help you with:`n• Smart AI IDE questions`n• Code assistance`n• Task automation`n• General AI chat`nWhat would you like to explore?"
                "ide" = "The Smart AI IDE includes:`n• Frontend with HoloB1.5 (Port 3000)`n• Backend API (Port 3001)`n• AI Firewall Security`nUse the launcher to start all services!"
                "start" = "To start your Smart AI IDE:`n1. Run launch-smart-ide.ps1`n2. Click 'Start All Services'`n3. Visit http://localhost:3000`n4. Enjoy the floating AI bot!"
                "code" = "I can help with coding! What programming language or problem are you working on?"
                "default" = "That's interesting! Let me think about that... As your desktop AI assistant, I'm here to help with any questions about your Smart AI IDE or general assistance."
            }
            
            $response = $responses["default"]
            foreach ($key in $responses.Keys) {
                if ($userInput.ToLower().Contains($key)) {
                    $response = $responses[$key]
                    break
                }
            }
            
            $chatOutput.AppendText("Assistant: $response`n`n")
            $chatOutput.ScrollToCaret()
            $chatInput.Focus()
        }
    }
    
    $sendBtn.Add_Click($sendMessage)
    $chatInput.Add_KeyPress({
        if ($_.KeyChar -eq [char]13) { # Enter key
            & $sendMessage
        }
    })
    
    # Form closed event
    $Global:ChatForm.Add_FormClosed({
        $Global:ChatVisible = $false
    })
    
    $Global:ChatForm.Show()
    $chatInput.Focus()
}

function Create-HoloBot {
    $Global:HoloForm = New-Object System.Windows.Forms.Form
    $Global:HoloForm.Size = New-Object System.Drawing.Size($Global:BotSize, $Global:BotSize)
    $Global:HoloForm.BackColor = [System.Drawing.Color]::Magenta
    $Global:HoloForm.TransparencyKey = [System.Drawing.Color]::Magenta
    $Global:HoloForm.TopMost = $true
    $Global:HoloForm.FormBorderStyle = [System.Windows.Forms.FormBorderStyle]::None
    $Global:HoloForm.ShowInTaskbar = $false
    $Global:HoloForm.StartPosition = [System.Windows.Forms.FormStartPosition]::Manual
    
    # Create the bot visual
    $botPanel = New-Object System.Windows.Forms.Panel
    $botPanel.Size = New-Object System.Drawing.Size($Global:BotSize, $Global:BotSize)
    $botPanel.Location = New-Object System.Drawing.Point(0, 0)
    $botPanel.BackColor = [System.Drawing.Color]::Transparent
    
    # Bot circle with gradient effect
    $botPanel.Add_Paint({
        param($sender, $e)
        $g = $e.Graphics
        $rect = New-Object System.Drawing.Rectangle(2, 2, $Global:BotSize-4, $Global:BotSize-4)
        
        # Create gradient brush
        $brush = New-Object System.Drawing.Drawing2D.LinearGradientBrush(
            $rect, 
            [System.Drawing.Color]::CornflowerBlue, 
            [System.Drawing.Color]::MediumPurple, 
            [System.Drawing.Drawing2D.LinearGradientMode]::Diagonal
        )
        
        # Draw main circle
        $g.FillEllipse($brush, $rect)
        
        # Draw border
        $pen = New-Object System.Drawing.Pen([System.Drawing.Color]::White, 2)
        $g.DrawEllipse($pen, $rect)
        
        # Draw bot icon (simple representation)
        $iconRect = New-Object System.Drawing.Rectangle(15, 15, 20, 20)
        $iconBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::White)
        $g.FillEllipse($iconBrush, $iconRect)
        
        # Draw "eyes"
        $eyeBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::Black)
        $g.FillEllipse($eyeBrush, 20, 20, 4, 4)
        $g.FillEllipse($eyeBrush, 28, 20, 4, 4)
        
        # Cleanup
        $brush.Dispose()
        $pen.Dispose()
        $iconBrush.Dispose()
        $eyeBrush.Dispose()
    })
    
    # Bot click event
    $botPanel.Add_Click({
        Show-HoloChat
    })
    
    # Hover effects
    $botPanel.Add_MouseEnter({
        $Global:HoloForm.Size = New-Object System.Drawing.Size($Global:BotSize + 10, $Global:BotSize + 10)
        $botPanel.Size = New-Object System.Drawing.Size($Global:BotSize + 10, $Global:BotSize + 10)
    })
    
    $botPanel.Add_MouseLeave({
        $Global:HoloForm.Size = New-Object System.Drawing.Size($Global:BotSize, $Global:BotSize)
        $botPanel.Size = New-Object System.Drawing.Size($Global:BotSize, $Global:BotSize)
    })
    
    $Global:HoloForm.Controls.Add($botPanel)
    
    # Make form always on top
    $Global:HoloForm.Add_Shown({
        [Win32]::SetWindowPos($Global:HoloForm.Handle, [Win32]::HWND_TOPMOST, 0, 0, 0, 0, [Win32]::SWP_NOMOVE -bor [Win32]::SWP_NOSIZE)
    })
    
    return $Global:HoloForm
}

function Start-HoloDesktop {
    Write-Host "🚀 Starting HoloB1.5 Desktop..." -ForegroundColor Cyan
    Write-Host "🔹 Creating floating AI bot..." -ForegroundColor Green
    
    # Create the bot
    $bot = Create-HoloBot
    $bot.Show()
    
    # Start mouse tracking timer
    $Global:MouseTimer = New-Object System.Windows.Forms.Timer
    $Global:MouseTimer.Interval = 50 # Update every 50ms for smooth following
    $Global:MouseTimer.Add_Tick({ Update-BotPosition })
    $Global:MouseTimer.Start()
    
    Write-Host "✅ HoloB1.5 Desktop is now running!" -ForegroundColor Green
    Write-Host "• Move your mouse - the bot will follow" -ForegroundColor Yellow
    Write-Host "• Click the bot to open chat" -ForegroundColor Yellow
    Write-Host "• Press Ctrl+C to exit" -ForegroundColor Yellow
    
    # Keep the script running
    try {
        while ($true) {
            [System.Windows.Forms.Application]::DoEvents()
            Start-Sleep -Milliseconds 100
        }
    }
    catch {
        Write-Host "`n🔹 HoloB1.5 Desktop shutting down..." -ForegroundColor Yellow
    }
    finally {
        # Cleanup
        if ($Global:MouseTimer) { $Global:MouseTimer.Stop() }
        if ($Global:ChatForm) { $Global:ChatForm.Close() }
        if ($Global:HoloForm) { $Global:HoloForm.Close() }
        Write-Host "👋 HoloB1.5 Desktop stopped." -ForegroundColor Cyan
    }
}

# Show usage info
Write-Host "===============================================" -ForegroundColor Magenta
Write-Host "🔹 HoloB1.5 Desktop - Floating AI Bot" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Magenta
Write-Host ""

# Check if running with admin rights (recommended for full functionality)
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
if (!$isAdmin) {
    Write-Host "⚠️  For best experience, run as Administrator" -ForegroundColor Yellow
}

# Start the desktop version
Start-HoloDesktop