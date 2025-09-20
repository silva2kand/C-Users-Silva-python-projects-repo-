# HoloB1.5 Voice Desktop - Enhanced Floating AI with Voice Conversation
# Advanced version with speech recognition and natural language AI

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName System.Speech
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

# Global Variables
$Global:HoloForm = $null
$Global:VoiceChatForm = $null
$Global:MouseTimer = $null
$Global:ChatVisible = $false
$Global:BotSize = 60
$Global:SpeechRecognizer = $null
$Global:SpeechSynthesizer = $null
$Global:IsListening = $false
$Global:ConversationMemory = @{
    Topics = @()
    Tasks = @()
    Notes = @()
    Jokes = @()
    Context = ""
    Mood = "friendly"
    Language = "auto"
    DetectedLanguage = "en-US"
}

# AI Personality and Multilingual Responses
$Global:HoloPersonality = @{
    Name = "Holo"
    Traits = @("friendly", "helpful", "witty", "curious", "supportive", "multilingual")
    
    # Multilingual Responses
    Responses = @{
        # English (US/UK)
        "en-US" = @{
            Greeting = @(
                "Hey there! I'm Holo, your multilingual AI companion. What's on your mind?",
                "Hello! Ready for some interesting conversation in any language? Just talk to me!",
                "Hi! I speak English, Tamil, and Jaffna Tamil. What would you like to do?"
            )
            TaskAcknowledge = @(
                "Got it! I've added that to your task list.",
                "Consider it noted! I'll help you remember that.",
                "Task added! I'm keeping track of everything for you."
            )
            NoteAcknowledge = @(
                "Noted! I'll remember that for you.",
                "I've got that written down in your notes.",
                "Perfect! That's now in your personal notes."
            )
            JokeSetup = @(
                "Oh, you want a joke? I've got just the thing!",
                "Time for some humor! Here's one for you:",
                "Let me brighten your day with this one:"
            )
            LanguageSwitch = @(
                "Switching to English. How can I help you?",
                "Now speaking English. What's on your mind?",
                "English mode activated. Ready to chat!"
            )
        }
        
        # Tamil
        "ta-IN" = @{
            Greeting = @(
                "வணக்கம்! நான் ஹோலோ, உங்கள் பல்மொழி AI துணையாளர். உங்கள் மனதில் என்ன இருக்கிறது?",
                "வணக்கம்! சுவாரசியமான உரையாடலுக்கு தயாரா? என்னிடம் பேசுங்கள்!",
                "வணக்கம்! நான் ஆங்கிலம், தமிழ், யாழ்ப்பாண தமிழ் பேசுவேன். என்ன செய்ய விரும்புகிறீர்கள்?"
            )
            TaskAcknowledge = @(
                "சரி! உங்கள் பணி பட்டியலில் சேர்த்துவிட்டேன்.",
                "கவனத்தில் கொண்டுள்ளேன்! அதை நினைவில் வைக்க உதவுவேன்.",
                "பணி சேர்க்கப்பட்டது! உங்களுக்காக எல்லாவற்றையும் கண்காணித்துக்கொண்டிருக்கிறேன்."
            )
            NoteAcknowledge = @(
                "குறிப்பிடப்பட்டது! உங்களுக்காக அதை நினைவில் வைத்துக்கொள்வேன்.",
                "உங்கள் குறிப்புகளில் எழுதிவைத்துவிட்டேன்.",
                "சரியாக! இப்போது அது உங்கள் தனிப்பட்ட குறிப்புகளில் உள்ளது."
            )
            JokeSetup = @(
                "ஓ, நீங்கள் ஒரு நகைச்சுவை வேண்டுமா? என்னிடம் சரியான விஷயம் உள்ளது!",
                "நகைச்சுவையின் நேரம்! இது உங்களுக்காக:",
                "உங்கள் நாளை பிரகாசமாக்க இதைக் கேளுங்கள்:"
            )
            LanguageSwitch = @(
                "தமிழுக்கு மாறுகிறேன். நான் எப்படி உதவ முடியும்?",
                "இப்போது தமிழில் பேசுகிறேன். உங்கள் மனதில் என்ன?",
                "தமிழ் பயன்முறை இயக்கப்பட்டது. அரட்டைக்கு தயார்!"
            )
        }
        
        # Jaffna Tamil (Northern Sri Lankan Tamil)
        "ta-LK" = @{
            Greeting = @(
                "வணக்கம்! நான் ஹோலோ, உங்களின் பல்மொழி AI துணைவர். உங்கட மனசுல என்ன இருக்கு?",
                "வணக்கம்! சுவாரஸ்யமான கதைப்பாட்டுக்கு ரெடியா? என்கிட்ட பேசுங்கோ!",
                "வணக்கம்! நான் ஆங்கிலம், தமிழ், யாழ்ப்பாண தமிழ் பேசுவேன். என்ன பண்ண விரும்புறீங்கோ?"
            )
            TaskAcknowledge = @(
                "ரைட்! உங்கட டாஸ்க் லிஸ்ட்ல சேர்த்துட்டேன்.",
                "நோட் பண்ணிட்டேன்! அதை நினைப்பில வைக்க ஹெல்ப் பண்ணுவேன்.",
                "டாஸ்க் ஆட் பண்ணிட்டேன்! உங்களுக்காக எல்லாத்தையும் ட்ராக் பண்ணிக்கிட்டிருக்கேன்."
            )
            NoteAcknowledge = @(
                "நோட் பண்ணிட்டேன்! உங்களுக்காக அதை நினைப்பில வைக்குவேன்.",
                "உங்கட நோட்ஸ்ல எழுதிவைச்சிட்டேன்.",
                "பர்ஃபெக்ட்! இப்ப அது உங்கட பர்சனல் நோட்ஸ்ல இருக்கு."
            )
            JokeSetup = @(
                "ஓ, உங்களுக்கு ஒரு ஜோக் வேணுமா? என்கிட்ட சரியான விஷயம் இருக்கு!",
                "ஹ்யூமர் டைம்! இது உங்களுக்காக:",
                "உங்கட நாளை பிரைட் பண்ண இதை கேளுங்கோ:"
            )
            LanguageSwitch = @(
                "யாழ்ப்பாண தமிழுக்கு சேஞ்ச் பண்றேன். நான் எப்படி ஹெல்ப் பண்ணலாம்?",
                "இப்ப யாழ்ப்பாண தமிழ்ல பேசறேன். உங்கட மனசுல என்ன?",
                "யாழ்ப்பாண தமிழ் மோட் ஆக்டிவேட் பண்ணிட்டேன். சாட்டுக்கு ரெடி!"
            )
        }
        
        # UK English
        "en-GB" = @{
            Greeting = @(
                "Hello there! I'm Holo, your multilingual AI companion. What's on your mind?",
                "Good day! Fancy a spot of conversation in any language? Do chat with me!",
                "Greetings! I speak English, Tamil, and Jaffna Tamil. What would you like to do?"
            )
            TaskAcknowledge = @(
                "Right! I've popped that onto your task list.",
                "Noted! I'll help you remember that, no worries.",
                "Task added! I'm keeping tabs on everything for you."
            )
            NoteAcknowledge = @(
                "Noted! I'll remember that for you, mate.",
                "I've jotted that down in your notes.",
                "Brilliant! That's now in your personal notes."
            )
            JokeSetup = @(
                "Oh, fancy a joke? I've got just the ticket!",
                "Time for a bit of humour! Here's one for you:",
                "Let me brighten your day with this little gem:"
            )
            LanguageSwitch = @(
                "Switching to British English. How may I assist?",
                "Now speaking Queen's English. What's on your mind?",
                "British English mode activated. Ready for a chat!"
            )
        }
    }
    
    # Multilingual Jokes
    Jokes = @{
        "en-US" = @(
            "Why don't scientists trust atoms? Because they make up everything!",
            "I told my computer a joke about UDP... but it didn't get it.",
            "Why do programmers prefer dark mode? Because light attracts bugs!",
            "What do you call a fish wearing a bowtie? Sofishticated!"
        )
        "en-GB" = @(
            "Why don't scientists trust atoms? Because they make up everything!",
            "I told my computer a joke about TCP... but it kept asking if I got it.",
            "Why do British programmers prefer tea? Because proper tea is theft!",
            "What's a computer's favourite biscuit? A chocolate chip cookie!"
        )
        "ta-IN" = @(
            "கணினி ஏன் டாக்டரிடம் போனது? அதற்கு வைரஸ் பிரச்சனை இருந்தது!",
            "ஏன் ரோபோட் எப்போதும் அமைதியாக இருக்கும்? அதற்கு நல்ல அல்காரிதம் இருக்கிறது!",
            "கணினி என்ன சாப்பிட விரும்பும்? மைக்ரோ சிப்ஸ்!",
            "ப்ரோகிராமர் ஏன் இருட்டை விரும்புகிறார்? ஒளி பிழைகளை கவரும்!"
        )
        "ta-LK" = @(
            "கம்ப்யூட்டர் ஏன் டாக்டர்கிட்ட போனது? அதுக்கு வைரஸ் ப்ராப்ளம் இருந்தது!",
            "ஏன் ரோபோட் எப்பவும் கூல்லா இருக்கும்? அதுக்கு நல்ல அல்காரிதம் இருக்கு!",
            "கம்ப்யூட்டர் என்ன சாப்பிட லைக் பண்ணும்? மைக்ரோ சிப்ஸ்!",
            "ப்ரோகிராமர் ஏன் டார்க்னெஸ் லைக் பண்றார்? லைட் பக்ஸை அட்ராக்ட் பண்ணும்!"
        )
    }
    
    # Language detection patterns
    LanguagePatterns = @{
        "ta-IN" = @("வணக்கம்", "தமிழ்", "என்ன", "எப்படி", "நான்", "நீங்கள்", "அது", "இது")
        "ta-LK" = @("வணக்கம்", "என்ன", "எப்படி", "நான்", "நீங்கோ", "அது", "இது", "என்கிட்ட", "உங்கட")
        "en-GB" = @("colour", "favour", "realise", "whilst", "amongst", "brilliant", "fancy", "proper")
        "en-US" = @("color", "favor", "realize", "while", "among", "awesome", "want", "real")
    }
}

function Initialize-VoiceSystem {
    try {
        # Initialize Speech Recognition
        $Global:SpeechRecognizer = New-Object System.Speech.Recognition.SpeechRecognitionEngine
        $Global:SpeechRecognizer.SetInputToDefaultAudioDevice()
        
        # Initialize Speech Synthesis
        $Global:SpeechSynthesizer = New-Object System.Speech.Synthesis.SpeechSynthesizer
        $Global:SpeechSynthesizer.Rate = 0  # Normal speed
        $Global:SpeechSynthesizer.Volume = 80
        
        Write-Host "✅ Voice system initialized successfully!" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "❌ Voice system initialization failed: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

function Get-MousePosition {
    $point = New-Object Win32+POINT
    [Win32]::GetCursorPos([ref]$point) | Out-Null
    return @{ X = $point.x; Y = $point.y }
}

function Update-BotPosition {
    if ($Global:HoloForm -and !$Global:ChatVisible) {
        $mousePos = Get-MousePosition
        
        # Position bot slightly offset from cursor
        $botX = $mousePos.X + 25
        $botY = $mousePos.Y - 25
        
        # Keep bot within screen bounds
        $screen = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
        if ($botX + $Global:BotSize -gt $screen.Width) { $botX = $screen.Width - $Global:BotSize }
        if ($botY -lt 0) { $botY = 0 }
        
        $Global:HoloForm.Location = New-Object System.Drawing.Point($botX, $botY)
    }
}

function Speak-Text {
    param([string]$Text)
    
    if ($Global:SpeechSynthesizer -and $Text) {
        try {
            $Global:SpeechSynthesizer.SpeakAsync($Text) | Out-Null
            Write-Host "🗣️ Holo: $Text" -ForegroundColor Cyan
        } catch {
            Write-Host "🔇 Speech synthesis error: $($_.Exception.Message)" -ForegroundColor Yellow
        }
    }
}

function Detect-Language {
    param([string]$Input)
    
    $detectedLang = "en-US"  # Default
    $maxMatches = 0
    
    foreach ($lang in $Global:HoloPersonality.LanguagePatterns.Keys) {
        $patterns = $Global:HoloPersonality.LanguagePatterns[$lang]
        $matchCount = 0
        
        foreach ($pattern in $patterns) {
            if ($Input -match $pattern) {
                $matchCount++
            }
        }
        
        if ($matchCount -gt $maxMatches) {
            $maxMatches = $matchCount
            $detectedLang = $lang
        }
    }
    
    # Update global language preference
    $Global:ConversationMemory.DetectedLanguage = $detectedLang
    
    return $detectedLang
}

function Get-MultilingualResponse {
    param([string]$Category, [string]$Language = "")
    
    if ([string]::IsNullOrEmpty($Language)) {
        $Language = $Global:ConversationMemory.DetectedLanguage
    }
    
    # Fallback to English if language not supported
    if (-not $Global:HoloPersonality.Responses.ContainsKey($Language)) {
        $Language = "en-US"
    }
    
    $responses = $Global:HoloPersonality.Responses[$Language][$Category]
    if ($responses -and $responses.Count -gt 0) {
        return $responses | Get-Random
    }
    
    # Ultimate fallback
    return "I understand! Let me help you with that."
}

function Get-MultilingualJoke {
    param([string]$Language = "")
    
    if ([string]::IsNullOrEmpty($Language)) {
        $Language = $Global:ConversationMemory.DetectedLanguage
    }
    
    # Fallback to English if language not supported
    if (-not $Global:HoloPersonality.Jokes.ContainsKey($Language)) {
        $Language = "en-US"
    }
    
    $jokes = $Global:HoloPersonality.Jokes[$Language]
    if ($jokes -and $jokes.Count -gt 0) {
        return $jokes | Get-Random
    }
    
    # Ultimate fallback
    return "Why did the multilingual AI cross the road? To get to the other language!"
}

function Process-NaturalLanguage {
    param([string]$Input)
    
    # Detect language first
    $detectedLang = Detect-Language $Input
    $lowerInput = $Input.ToLower()
    
    # Update conversation memory
    $Global:ConversationMemory.Context = $Input
    $Global:ConversationMemory.Topics += $Input
    
    Write-Host "[LANG] Detected: $detectedLang" -ForegroundColor Magenta
    
    # Language switching commands
    if ($lowerInput -match "(switch to|change to|speak|talk in) (english|tamil|jaffna|யாழ்ப்பாண|தமிழ்)") {
        if ($lowerInput -match "(jaffna|யாழ்ப்பாண)") {
            $Global:ConversationMemory.DetectedLanguage = "ta-LK"
            return Get-MultilingualResponse "LanguageSwitch" "ta-LK"
        } elseif ($lowerInput -match "(tamil|தமிழ்)") {
            $Global:ConversationMemory.DetectedLanguage = "ta-IN"
            return Get-MultilingualResponse "LanguageSwitch" "ta-IN"
        } elseif ($lowerInput -match "british|uk|queen") {
            $Global:ConversationMemory.DetectedLanguage = "en-GB"
            return Get-MultilingualResponse "LanguageSwitch" "en-GB"
        } else {
            $Global:ConversationMemory.DetectedLanguage = "en-US"
            return Get-MultilingualResponse "LanguageSwitch" "en-US"
        }
    }
    
    # Greeting detection (multilingual)
    $greetingPatterns = @(
        "(hello|hi|hey|good morning|good afternoon|good evening)",
        "(வணக்கம்|வந்தனம்)",
        "(கூட்மார்निंग|குड் ஈவ்னிங்)"
    )
    foreach ($pattern in $greetingPatterns) {
        if ($lowerInput -match $pattern -or $Input -match $pattern) {
            return Get-MultilingualResponse "Greeting" $detectedLang
        }
    }
    
    # Task management (multilingual)
    $taskPatterns = @(
        "(add task|todo|remind me|don't forget|task:|need to)",
        "(பணி சேர்|காரியம்|நினைவூட்ட|மறக்காதே|task|todo)",
        "(டாஸ்க்|வேலை|பண்ண)"
    )
    foreach ($pattern in $taskPatterns) {
        if ($lowerInput -match $pattern -or $Input -match $pattern) {
            $task = Extract-Task $Input
            $Global:ConversationMemory.Tasks += $task
            return (Get-MultilingualResponse "TaskAcknowledge" $detectedLang) + " Task: '$task'"
        }
    }
    
    # Note taking (multilingual)
    $notePatterns = @(
        "(take a note|remember this|write down|note:|keep in mind)",
        "(குறிப்பு|நினைவில் வை|எழுது|note|குறிப்பு எடு)",
        "(நோட்|மறக்காம)"
    )
    foreach ($pattern in $notePatterns) {
        if ($lowerInput -match $pattern -or $Input -match $pattern) {
            $note = Extract-Note $Input
            $Global:ConversationMemory.Notes += $note
            return (Get-MultilingualResponse "NoteAcknowledge" $detectedLang) + " Note: '$note'"
        }
    }
    
    # Joke request (multilingual)
    $jokePatterns = @(
        "(joke|funny|laugh|humor|make me smile)",
        "(நகைச்சுவை|சிரிப்பு|கலகல|மகிழ்ச்சி|ஜோக்)",
        "(ஃபன்னி|லாஃப்)"
    )
    foreach ($pattern in $jokePatterns) {
        if ($lowerInput -match $pattern -or $Input -match $pattern) {
            $joke = Get-MultilingualJoke $detectedLang
            $Global:ConversationMemory.Jokes += $joke
            return (Get-MultilingualResponse "JokeSetup" $detectedLang) + "`n`n$joke"
        }
    }
    
    # Memory recall (multilingual)
    $memoryPatterns = @(
        "(what did i|remember when|my tasks|my notes|what tasks)",
        "(என்ன சொன்னேன்|நினைவில்|என் பணிகள்|என் குறிப்புகள்)",
        "(என் டாஸ்க்|என் நோட்ஸ்)"
    )
    foreach ($pattern in $memoryPatterns) {
        if ($lowerInput -match $pattern -or $Input -match $pattern) {
            return Recall-Memory $lowerInput $detectedLang
        }
    }
    
    # Smart AI IDE help (multilingual)
    $idePatterns = @(
        "(smart ai|ide|development|code|programming)",
        "(ஸ்மார்ட் ஏஐ|ஐடிஇ|டெவலப்மென்ட்|கோட்|புரோகிராமிங்)",
        "(கம்ப்யூட்டர்|சாஃப்ட்வேர்)"
    )
    foreach ($pattern in $idePatterns) {
        if ($lowerInput -match $pattern -or $Input -match $pattern) {
            if ($detectedLang -eq "ta-IN") {
                return "நான் உங்கள் ஸ்மார்ட் ஏஐ ஐடிஇயுடன் உதவ முடியும்! இதில் உரையாடல் ஏஐ, சூப்பர் ஏஜென்ட்கள், மற்றும் அனைத்து டெவலப்மென்ட் கருவிகளும் உள்ளன. எந்த குறிப்பிட்ட அம்சத்தை விளக்க வேண்டும்?"
            } elseif ($detectedLang -eq "ta-LK") {
                return "நான் உங்கட ஸ்மார்ட் ஏஐ ஐடிஇ கூட ஹெல்ப் பண்ண முடியும்! இத்துல கன்வர்சேஷன் ஏஐ, சூப்பர் ஏஜென்ட்ஸ், அப்பறம் எல்லா டெவலப்மென்ட் டூல்ஸும் இருக்கு. எந்த ஸ்பெசிபிக் ஃபீச்சர் எக்ஸ்ப்ளெயின் பண்ணணும்?"
            } elseif ($detectedLang -eq "en-GB") {
                return "I can help with your Smart AI IDE! It's got conversation AI, super agents, and all the development tools you'll need. Fancy me explaining any particular feature?"
            } else {
                return "I can help with your Smart AI IDE! It has conversation AI, super agents, and all the development tools you need. Want me to explain any specific feature?"
            }
        }
    }
    
    # Conversational response (multilingual)
    return Generate-ContextualResponse $Input $detectedLang
}

function Get-RandomResponse {
    param([string]$Category, [string]$Language = "")
    return Get-MultilingualResponse $Category $Language
}

function Extract-Task {
    param([string]$Input)
    
    $patterns = @(
        "add task:?\s*(.*)",
        "remind me to\s*(.*)",
        "don't forget to\s*(.*)",
        "i need to\s*(.*)",
        "todo:?\s*(.*)"
    )
    
    foreach ($pattern in $patterns) {
        if ($Input -match $pattern) {
            return $matches[1].Trim()
        }
    }
    
    return $Input
}

function Extract-Note {
    param([string]$Input)
    
    $patterns = @(
        "take a note:?\s*(.*)",
        "remember this:?\s*(.*)", 
        "write down:?\s*(.*)",
        "note:?\s*(.*)"
    )
    
    foreach ($pattern in $patterns) {
        if ($Input -match $pattern) {
            return $matches[1].Trim()
        }
    }
    
    return $Input
}

function Recall-Memory {
    param([string]$Input, [string]$Language = "")
    
    if ([string]::IsNullOrEmpty($Language)) {
        $Language = $Global:ConversationMemory.DetectedLanguage
    }
    
    if ($Input -match "(tasks|பணிகள்|டாஸ்க்)") {
        if ($Global:ConversationMemory.Tasks.Count -eq 0) {
            if ($Language -eq "ta-IN") {
                return "உங்களிடம் இன்னும் பணிகள் இல்லை. சில சேர்க்க விரும்புகிறீர்களா?"
            } elseif ($Language -eq "ta-LK") {
                return "உங்கட்ட இன்னும் டாஸ்க்ஸ் இல்லை. கொஞ்சம் ஆட் பண்ண விரும்புறீங்களா?"
            } elseif ($Language -eq "en-GB") {
                return "You haven't got any tasks yet. Fancy adding some?"
            } else {
                return "You don't have any tasks yet. Want to add some?"
            }
        }
        $taskList = $Global:ConversationMemory.Tasks | ForEach-Object { "• $_" }
        if ($Language -eq "ta-IN") {
            return "இங்கே உங்கள் பணிகள்:`n" + ($taskList -join "`n")
        } elseif ($Language -eq "ta-LK") {
            return "இங்கே உங்கட டாஸ்க்ஸ்:`n" + ($taskList -join "`n")
        } elseif ($Language -eq "en-GB") {
            return "Here are your tasks:`n" + ($taskList -join "`n")
        } else {
            return "Here are your tasks:`n" + ($taskList -join "`n")
        }
    }
    
    if ($Input -match "(notes|குறிப்புகள்|நோட்ஸ்)") {
        if ($Global:ConversationMemory.Notes.Count -eq 0) {
            if ($Language -eq "ta-IN") {
                return "இன்னும் குறிப்புகள் சேமிக்கப்படவில்லை. உங்களிடம் சொல்லும் எதையும் நினைவில் வைக்க தயாராக இருக்கிறேன்!"
            } elseif ($Language -eq "ta-LK") {
                return "இன்னும் நோட்ஸ் சேவ் பண்ணல்லை. நீங்கோ எதுவும் சொன்னா நான் ரெமெம்பர் பண்ண ரெடியா இருக்கேன்!"
            } elseif ($Language -eq "en-GB") {
                return "No notes saved yet. I'm ready to remember anything you tell me!"
            } else {
                return "No notes saved yet. I'm ready to remember anything you tell me!"
            }
        }
        $notesList = $Global:ConversationMemory.Notes | ForEach-Object { "• $_" }
        if ($Language -eq "ta-IN") {
            return "உங்கள் குறிப்புகள்:`n" + ($notesList -join "`n")
        } elseif ($Language -eq "ta-LK") {
            return "உங்கட நோட்ஸ்:`n" + ($notesList -join "`n")
        } elseif ($Language -eq "en-GB") {
            return "Your notes:`n" + ($notesList -join "`n")
        } else {
            return "Your notes:`n" + ($notesList -join "`n")
        }
    }
    
    if ($Input -match "(jokes|நகைச்சுவை|ஜோக்)") {
        if ($Global:ConversationMemory.Jokes.Count -eq 0) {
            if ($Language -eq "ta-IN") {
                return "நாம் இன்னும் நகைச்சுவைகள் பகிரவில்லை! ஒன்று கேட்க விரும்புகிறீர்களா?"
            } elseif ($Language -eq "ta-LK") {
                return "நாம இன்னும் ஜோக்ஸ் ஷேர் பண்ணல்லை! ஒண்ணு கேக்க விரும்புறீங்களா?"
            } elseif ($Language -eq "en-GB") {
                return "We haven't shared any jokes yet! Fancy hearing one?"
            } else {
                return "We haven't shared any jokes yet! Want to hear one?"
            }
        }
        if ($Language -eq "ta-IN") {
            return "முன்பு நான் சொன்ன நகைச்சுவை:`n" + $Global:ConversationMemory.Jokes[-1]
        } elseif ($Language -eq "ta-LK") {
            return "அப்ப நான் சொன்ன ஜோக்:`n" + $Global:ConversationMemory.Jokes[-1]
        } elseif ($Language -eq "en-GB") {
            return "Here's a joke I told you earlier:`n" + $Global:ConversationMemory.Jokes[-1]
        } else {
            return "Here's a joke I told you earlier:`n" + $Global:ConversationMemory.Jokes[-1]
        }
    }
    
    if ($Language -eq "ta-IN") {
        return "நான் நினைவில் வைத்திருப்பது: " + ($Global:ConversationMemory.Topics[-3..-1] -join ", ")
    } elseif ($Language -eq "ta-LK") {
        return "நான் ரெமெம்பர் பண்ணிருக்கிறது: " + ($Global:ConversationMemory.Topics[-3..-1] -join ", ")
    } elseif ($Language -eq "en-GB") {
        return "I remember we've chatted about: " + ($Global:ConversationMemory.Topics[-3..-1] -join ", ")
    } else {
        return "I remember we've talked about: " + ($Global:ConversationMemory.Topics[-3..-1] -join ", ")
    }
}

function Generate-ContextualResponse {
    param([string]$Input, [string]$Language = "")
    
    if ([string]::IsNullOrEmpty($Language)) {
        $Language = $Global:ConversationMemory.DetectedLanguage
    }
    
    $responses = @{}
    
    if ($Language -eq "ta-IN") {
        $responses = @(
            "அது விலையற்ற விஷயம்! உங்கள் '$Input' பற்றிச் சொன்னீர்கள். ஆனதினால் அதை நினைத்தீர்கள்?",
            "அது வினோதமான விஷயம். அதற்றைப் பற்றி கொஞ்சம் கூட சொல்ல முடியுமா?",
            "அதைஎன்னிடம் பகிர்ந்ததற்கு நன்றி! அது உங்களுக்கு முக்கியமான விஷயமாக தோன்றுகிறது.",
            "அது சரியான கருத்து! நமது உரையாடலிலிருந்து நான் றொம்ப கற்றுக்கொண்டிருக்கிறேன்!",
            "உங்கள் என்ன விதத்தில் யோசிக்கிறீர்கள் நமக்குப் பிடிக்குது!",
            "நான் நமது பேச்சை ரொம்ப ரசிக்கிறேன்! உங்கள் மனதில் இன்னும் என்ன இருக்கிறது?"
        )
    } elseif ($Language -eq "ta-LK") {
        $responses = @(
            "அது வெரி இன்டரெஸ்டிங்! நீங்கோ '$Input' பத்தி சொன்னேங்கோ. ஏன் அதை நினைச்சேங்கோ?",
            "நான் நெரைய இன்டரெஸ்டிங்கா ஃபீல் பண்றேன். அதை கூட டிடேல் சொல்ல முடியும்?",
            "அதை என்னகிட்ட ஷேர் பண்ணதுக்கு தாங்க்ஸ்! அது உங்களுக்கு இம்பொர்டன்டா இருக்க வேணும்.",
            "நல்ல போயின்ட்! நமது கன்வர்சேஷன்ல இருந்து நான் லொட் கத்துக்கிட்டிருக்கேன்!",
            "நீங்கோ எந்த விதத்தில் யோசிக்குறீங்கோ நெனொ நல்லா இருக்கு!",
            "நான் நமது சாட்டை ரொம்ப என்ஜொய் பண்றேன்! உங்கட மைண்ட்ல இன்னும் என்ன?"
        )
    } elseif ($Language -eq "en-GB") {
        $responses = @(
            "That's quite fascinating! You mentioned '$Input'. What made you think of that?",
            "I find that rather interesting. Could you tell me a bit more about it?",
            "Thanks for sharing that with me! It sounds quite important to you.",
            "That's a brilliant point. I'm learning loads from our chat!",
            "I love how you think about things! What's your take on this?",
            "That reminds me of something... actually, what's your experience with that?",
            "You've always got such unique perspectives! Do carry on.",
            "I'm really enjoying our conversation. What else is on your mind?"
        )
    } else {
        $responses = @(
            "That's fascinating! You mentioned '$Input'. What made you think of that?",
            "I find that really interesting. Can you tell me more about it?",
            "Thanks for sharing that with me! It sounds important to you.",
            "That's a great point. I'm learning so much from our conversation!",
            "I love how you think about things! What's your take on this?",
            "That reminds me of something... actually, what's your experience with that?",
            "You always have such unique perspectives! Keep going.",
            "I'm really enjoying our chat. What else is on your mind?"
        )
    }
    
    return $responses | Get-Random
}

function Start-VoiceListening {
    if ($Global:SpeechRecognizer -and !$Global:IsListening) {
        try {
            # Create grammar for open-ended recognition
            $grammar = New-Object System.Speech.Recognition.DictationGrammar
            $Global:SpeechRecognizer.LoadGrammar($grammar)
            
            # Event handlers
            $Global:SpeechRecognizer.add_SpeechRecognized({
                param($sender, $e)
                $recognizedText = $e.Result.Text
                Write-Host "👂 You said: $recognizedText" -ForegroundColor Yellow
                
                # Process the input and generate response
                $response = Process-NaturalLanguage $recognizedText
                Speak-Text $response
            })
            
            $Global:SpeechRecognizer.add_SpeechRecognitionRejected({
                Write-Host "❓ Sorry, I didn't catch that. Could you repeat?" -ForegroundColor Gray
                Speak-Text "Sorry, I didn't catch that. Could you repeat?"
            })
            
            $Global:SpeechRecognizer.RecognizeAsync([System.Speech.Recognition.RecognizeMode]::Multiple)
            $Global:IsListening = $true
            Write-Host "🎤 Voice recognition started - I'm listening!" -ForegroundColor Green
            Speak-Text "Hello! I'm listening. You can talk to me naturally!"
            
        } catch {
            Write-Host "🔇 Failed to start voice recognition: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
}

function Stop-VoiceListening {
    if ($Global:SpeechRecognizer -and $Global:IsListening) {
        try {
            $Global:SpeechRecognizer.RecognizeAsyncStop()
            $Global:IsListening = $false
            Write-Host "🔇 Voice recognition stopped" -ForegroundColor Yellow
        } catch {
            Write-Host "Error stopping voice recognition: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
}

function Show-VoiceChat {
    if ($Global:VoiceChatForm) {
        $Global:VoiceChatForm.Close()
    }
    
    $Global:ChatVisible = $true
    
    # Position chat at top-right of screen
    $screen = [System.Windows.Forms.Screen]::PrimaryScreen.WorkingArea
    $chatX = $screen.Width - 450
    $chatY = 50
    
    $Global:VoiceChatForm = New-Object System.Windows.Forms.Form
    $Global:VoiceChatForm.Text = "HoloB1.5 Voice Assistant"
    $Global:VoiceChatForm.Size = New-Object System.Drawing.Size(440, 500)
    $Global:VoiceChatForm.Location = New-Object System.Drawing.Point($chatX, $chatY)
    $Global:VoiceChatForm.TopMost = $true
    $Global:VoiceChatForm.FormBorderStyle = [System.Windows.Forms.FormBorderStyle]::FixedToolWindow
    $Global:VoiceChatForm.BackColor = [System.Drawing.Color]::FromArgb(240, 240, 255)
    
    # Chat header with voice status
    $header = New-Object System.Windows.Forms.Panel
    $header.Size = New-Object System.Drawing.Size(430, 60)
    $header.Location = New-Object System.Drawing.Point(5, 5)
    $header.BackColor = [System.Drawing.Color]::FromArgb(100, 150, 255)
    $Global:VoiceChatForm.Controls.Add($header)
    
    $titleLabel = New-Object System.Windows.Forms.Label
    $titleLabel.Text = "🎤 Holo Voice Assistant"
    $titleLabel.Size = New-Object System.Drawing.Size(300, 25)
    $titleLabel.Location = New-Object System.Drawing.Point(10, 10)
    $titleLabel.ForeColor = [System.Drawing.Color]::White
    $titleLabel.Font = New-Object System.Drawing.Font("Arial", 12, [System.Drawing.FontStyle]::Bold)
    $header.Controls.Add($titleLabel)
    
    $statusLabel = New-Object System.Windows.Forms.Label
    $statusLabel.Text = if ($Global:IsListening) { "🔴 Listening..." } else { "⚪ Click to start voice" }
    $statusLabel.Size = New-Object System.Drawing.Size(200, 20)
    $statusLabel.Location = New-Object System.Drawing.Point(10, 35)
    $statusLabel.ForeColor = [System.Drawing.Color]::LightYellow
    $statusLabel.Font = New-Object System.Drawing.Font("Arial", 9)
    $header.Controls.Add($statusLabel)
    
    # Voice control buttons
    $voiceBtn = New-Object System.Windows.Forms.Button
    $voiceBtn.Text = if ($Global:IsListening) { "🔇 Stop" } else { "🎤 Listen" }
    $voiceBtn.Size = New-Object System.Drawing.Size(80, 50)
    $voiceBtn.Location = New-Object System.Drawing.Point(340, 10)
    $voiceBtn.BackColor = if ($Global:IsListening) { [System.Drawing.Color]::IndianRed } else { [System.Drawing.Color]::LimeGreen }
    $voiceBtn.ForeColor = [System.Drawing.Color]::White
    $voiceBtn.Font = New-Object System.Drawing.Font("Arial", 10, [System.Drawing.FontStyle]::Bold)
    $voiceBtn.Add_Click({
        if ($Global:IsListening) {
            Stop-VoiceListening
            $voiceBtn.Text = "🎤 Listen"
            $voiceBtn.BackColor = [System.Drawing.Color]::LimeGreen
            $statusLabel.Text = "⚪ Click to start voice"
        } else {
            Start-VoiceListening
            $voiceBtn.Text = "🔇 Stop"
            $voiceBtn.BackColor = [System.Drawing.Color]::IndianRed
            $statusLabel.Text = "🔴 Listening..."
        }
    })
    $header.Controls.Add($voiceBtn)
    
    # Chat output area
    $chatOutput = New-Object System.Windows.Forms.RichTextBox
    $chatOutput.Size = New-Object System.Drawing.Size(420, 300)
    $chatOutput.Location = New-Object System.Drawing.Point(10, 75)
    $chatOutput.BackColor = [System.Drawing.Color]::White
    $chatOutput.Font = New-Object System.Drawing.Font("Consolas", 10)
    $chatOutput.ReadOnly = $true
    $chatOutput.ScrollBars = "Vertical"
    $Global:VoiceChatForm.Controls.Add($chatOutput)
    
    # Memory display
    $memoryPanel = New-Object System.Windows.Forms.Panel
    $memoryPanel.Size = New-Object System.Drawing.Size(420, 80)
    $memoryPanel.Location = New-Object System.Drawing.Point(10, 385)
    $memoryPanel.BackColor = [System.Drawing.Color]::FromArgb(245, 245, 245)
    $memoryPanel.BorderStyle = [System.Windows.Forms.BorderStyle]::FixedSingle
    $Global:VoiceChatForm.Controls.Add($memoryPanel)
    
    $memoryTitle = New-Object System.Windows.Forms.Label
    $memoryTitle.Text = "📝 Memory Summary"
    $memoryTitle.Size = New-Object System.Drawing.Size(200, 20)
    $memoryTitle.Location = New-Object System.Drawing.Point(5, 5)
    $memoryTitle.Font = New-Object System.Drawing.Font("Arial", 9, [System.Drawing.FontStyle]::Bold)
    $memoryPanel.Controls.Add($memoryTitle)
    
    $memoryText = New-Object System.Windows.Forms.Label
    $taskCount = $Global:ConversationMemory.Tasks.Count
    $noteCount = $Global:ConversationMemory.Notes.Count
    $jokeCount = $Global:ConversationMemory.Jokes.Count
    $memoryText.Text = "Tasks: $taskCount | Notes: $noteCount | Jokes: $jokeCount"
    $memoryText.Size = New-Object System.Drawing.Size(300, 20)
    $memoryText.Location = New-Object System.Drawing.Point(5, 25)
    $memoryText.Font = New-Object System.Drawing.Font("Arial", 8)
    $memoryPanel.Controls.Add($memoryText)
    
    # Memory buttons
    $showTasksBtn = New-Object System.Windows.Forms.Button
    $showTasksBtn.Text = "📋 Tasks"
    $showTasksBtn.Size = New-Object System.Drawing.Size(60, 25)
    $showTasksBtn.Location = New-Object System.Drawing.Point(5, 50)
    $showTasksBtn.Add_Click({
        $tasks = Recall-Memory "my tasks"
        Speak-Text $tasks
        $chatOutput.AppendText("🤖 Holo: $tasks`n`n")
        $chatOutput.ScrollToCaret()
    })
    $memoryPanel.Controls.Add($showTasksBtn)
    
    $showNotesBtn = New-Object System.Windows.Forms.Button
    $showNotesBtn.Text = "📝 Notes"
    $showNotesBtn.Size = New-Object System.Drawing.Size(60, 25)
    $showNotesBtn.Location = New-Object System.Drawing.Point(75, 50)
    $showNotesBtn.Add_Click({
        $notes = Recall-Memory "my notes"
        Speak-Text $notes
        $chatOutput.AppendText("🤖 Holo: $notes`n`n")
        $chatOutput.ScrollToCaret()
    })
    $memoryPanel.Controls.Add($showNotesBtn)
    
    $jokeBtn = New-Object System.Windows.Forms.Button
    $jokeBtn.Text = "😄 Joke"
    $jokeBtn.Size = New-Object System.Drawing.Size(60, 25)
    $jokeBtn.Location = New-Object System.Drawing.Point(145, 50)
    $jokeBtn.Add_Click({
        $joke = $Global:HoloPersonality.Jokes | Get-Random
        $response = (Get-RandomResponse "JokeSetup") + "`n`n$joke"
        Speak-Text $response
        $chatOutput.AppendText("🤖 Holo: $response`n`n")
        $chatOutput.ScrollToCaret()
    })
    $memoryPanel.Controls.Add($jokeBtn)
    
    # Close button
    $closeBtn = New-Object System.Windows.Forms.Button
    $closeBtn.Text = "✕"
    $closeBtn.Size = New-Object System.Drawing.Size(30, 30)
    $closeBtn.Location = New-Object System.Drawing.Point(380, 50)
    $closeBtn.BackColor = [System.Drawing.Color]::IndianRed
    $closeBtn.ForeColor = [System.Drawing.Color]::White
    $closeBtn.Font = New-Object System.Drawing.Font("Arial", 12, [System.Drawing.FontStyle]::Bold)
    $closeBtn.Add_Click({
        Stop-VoiceListening
        $Global:VoiceChatForm.Close()
        $Global:ChatVisible = $false
    })
    $memoryPanel.Controls.Add($closeBtn)
    
    # Welcome message
    $welcome = "[MIC] HoloB1.5 Multilingual Voice Assistant Ready!`n`n" +
               "[STAR] I understand natural conversation in multiple languages`n" +
               "[NOTE] I'll remember your tasks and notes`n" +
               "[SMILE] I can tell jokes and chat casually`n" +
               "[TOOL] I know about your Smart AI IDE`n" +
               "[LANG] Languages: English (US/UK), Tamil, Jaffna Tamil`n`n" +
               "Click the microphone button to start talking!`n" +
               "Language Commands:`n" +
               "• 'Switch to Tamil' / 'தமிழுக்கு மாறு'`n" +
               "• 'Switch to Jaffna Tamil' / 'யாழ்ப்பாணத்துக்கு மாறு'`n" +
               "• 'Switch to English'`n`n" +
               "Sample Commands:`n" +
               "• 'Take a note: meeting at 3pm'`n" +
               "• 'பணி சேர்: project முடிக்க வேண்டும்'`n" +
               "• 'Tell me a joke' / 'ஒரு joke சொல்லு'`n" +
               "• 'What are my tasks?' / 'என் tasks என்ன?'`n`n"
    
    $chatOutput.AppendText($welcome)
    
    # Form closed event
    $Global:VoiceChatForm.Add_FormClosed({
        Stop-VoiceListening
        $Global:ChatVisible = $false
    })
    
    $Global:VoiceChatForm.Show()
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
    
    # Create the bot visual with voice indication
    $botPanel = New-Object System.Windows.Forms.Panel
    $botPanel.Size = New-Object System.Drawing.Size($Global:BotSize, $Global:BotSize)
    $botPanel.Location = New-Object System.Drawing.Point(0, 0)
    $botPanel.BackColor = [System.Drawing.Color]::Transparent
    
    # Bot circle with voice visualization
    $botPanel.Add_Paint({
        param($sender, $e)
        $g = $e.Graphics
        $rect = New-Object System.Drawing.Rectangle(3, 3, $Global:BotSize-6, $Global:BotSize-6)
        
        # Choose color based on voice state
        $color1 = if ($Global:IsListening) { [System.Drawing.Color]::FromArgb(255, 100, 100) } else { [System.Drawing.Color]::FromArgb(100, 150, 255) }
        $color2 = if ($Global:IsListening) { [System.Drawing.Color]::FromArgb(255, 150, 150) } else { [System.Drawing.Color]::FromArgb(150, 200, 255) }
        
        # Create gradient brush
        $brush = New-Object System.Drawing.Drawing2D.LinearGradientBrush(
            $rect, $color1, $color2,
            [System.Drawing.Drawing2D.LinearGradientMode]::Diagonal
        )
        
        # Draw main circle
        $g.FillEllipse($brush, $rect)
        
        # Draw border
        $borderColor = if ($Global:IsListening) { [System.Drawing.Color]::Red } else { [System.Drawing.Color]::White }
        $pen = New-Object System.Drawing.Pen($borderColor, 2)
        $g.DrawEllipse($pen, $rect)
        
        # Draw voice icon
        $iconRect = New-Object System.Drawing.Rectangle(18, 18, 24, 24)
        $iconBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::White)
        $g.FillEllipse($iconBrush, $iconRect)
        
        # Draw microphone or speaker icon
        $iconColor = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::Black)
        if ($Global:IsListening) {
            # Draw microphone lines
            $g.FillRectangle($iconColor, 28, 25, 4, 10)
            $g.FillEllipse($iconColor, 26, 22, 8, 6)
        } else {
            # Draw speaker/face
            $g.FillEllipse($iconColor, 24, 24, 3, 3)
            $g.FillEllipse($iconColor, 33, 24, 3, 3)
            $g.DrawArc((New-Object System.Drawing.Pen($iconColor, 2)), 26, 30, 8, 6, 0, 180)
        }
        
        # Cleanup
        $brush.Dispose()
        $pen.Dispose()
        $iconBrush.Dispose()
        $iconColor.Dispose()
    })
    
    # Bot click event
    $botPanel.Add_Click({
        Show-VoiceChat
    })
    
    # Hover effects
    $botPanel.Add_MouseEnter({
        $Global:HoloForm.Size = New-Object System.Drawing.Size($Global:BotSize + 15, $Global:BotSize + 15)
        $botPanel.Size = New-Object System.Drawing.Size($Global:BotSize + 15, $Global:BotSize + 15)
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

function Start-HoloVoiceDesktop {
    Write-Host "===============================================" -ForegroundColor Magenta
    Write-Host "🎤 HoloB1.5 Voice Desktop - Advanced AI" -ForegroundColor Cyan
    Write-Host "===============================================" -ForegroundColor Magenta
    Write-Host ""
    
    # Initialize voice system
    Write-Host "🔧 Initializing voice system..." -ForegroundColor Yellow
    $voiceInitialized = Initialize-VoiceSystem
    
    Write-Host "🔹 Creating enhanced floating AI bot..." -ForegroundColor Green
    
    # Create the bot
    $bot = Create-HoloBot
    $bot.Show()
    
    # Start mouse tracking timer with visual updates
    $Global:MouseTimer = New-Object System.Windows.Forms.Timer
    $Global:MouseTimer.Interval = 50 # Update every 50ms for smooth following
    $Global:MouseTimer.Add_Tick({ 
        Update-BotPosition
        # Refresh bot appearance to show voice state changes
        if ($Global:HoloForm) {
            $Global:HoloForm.Refresh()
        }
    })
    $Global:MouseTimer.Start()
    
    Write-Host "✅ HoloB1.5 Voice Desktop is now running!" -ForegroundColor Green
    Write-Host "• Move your mouse - the bot will follow" -ForegroundColor Yellow
    Write-Host "• Click the bot to open voice chat interface" -ForegroundColor Yellow
    Write-Host "• Talk naturally - I understand conversation!" -ForegroundColor Yellow
    Write-Host "• I can take notes, manage tasks, and tell jokes" -ForegroundColor Yellow
    if ($voiceInitialized) {
        Write-Host "🎤 Voice capabilities: ENABLED" -ForegroundColor Green
    } else {
        Write-Host "🔇 Voice capabilities: DISABLED (text-only mode)" -ForegroundColor Yellow
    }
    Write-Host "• Press Ctrl+C to exit" -ForegroundColor Yellow
    
    # Keep the script running
    try {
        while ($true) {
            [System.Windows.Forms.Application]::DoEvents()
            Start-Sleep -Milliseconds 100
        }
    }
    catch {
        Write-Host "`n🔹 HoloB1.5 Voice Desktop shutting down..." -ForegroundColor Yellow
    }
    finally {
        # Cleanup
        if ($Global:MouseTimer) { $Global:MouseTimer.Stop() }
        Stop-VoiceListening
        if ($Global:VoiceChatForm) { $Global:VoiceChatForm.Close() }
        if ($Global:HoloForm) { $Global:HoloForm.Close() }
        if ($Global:SpeechSynthesizer) { $Global:SpeechSynthesizer.Dispose() }
        if ($Global:SpeechRecognizer) { $Global:SpeechRecognizer.Dispose() }
        Write-Host "[WAVE] HoloB1.5 Voice Desktop stopped." -ForegroundColor Cyan
    }
}

# Start the enhanced voice desktop version
Start-HoloVoiceDesktop