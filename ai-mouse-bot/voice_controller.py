"""
Voice Interaction Module for the AI Mouse Bot
Handles speech recognition and text-to-speech functionality.
"""

import os
import time
import queue
import threading
import speech_recognition as sr
from gtts import gTTS
import pygame
import tempfile
from typing import Callable, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum, auto

class VoiceState(Enum):
    """Current state of the voice interaction system."""
    IDLE = auto()
    LISTENING = auto()
    PROCESSING = auto()
    SPEAKING = auto()
    ERROR = auto()

@dataclass
class VoiceCommand:
    """Represents a voice command from the user."""
    text: str
    confidence: float
    timestamp: float
    raw_data: Any = None

class VoiceController:
    """Handles voice input and output for the AI Mouse Bot."""
    
    def __init__(self, 
                 language: str = "en-US",
                 energy_threshold: int = 300,
                 pause_threshold: float = 0.8,
                 dynamic_energy_threshold: bool = True):
        """Initialize the voice controller."""
        self.language = language
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = energy_threshold
        self.recognizer.pause_threshold = pause_threshold
        self.recognizer.dynamic_energy_threshold = dynamic_energy_threshold
        
        # Audio queue for text-to-speech
        self.audio_queue = queue.Queue()
        self.is_speaking = False
        self.state = VoiceState.IDLE
        
        # Initialize pygame mixer for audio playback
        pygame.mixer.init()
        
        # Callbacks
        self.on_command_callback = None
        self.on_state_change = None
        
        # Start the audio processing thread
        self._stop_event = threading.Event()
        self.audio_thread = threading.Thread(target=self._audio_worker)
        self.audio_thread.daemon = True
        self.audio_thread.start()
    
    def start_listening(self, callback: Callable[[VoiceCommand], None] = None) -> None:
        """Start listening for voice commands in a background thread."""
        if self.state != VoiceState.IDLE:
            print("Already listening or processing")
            return
        
        if callback:
            self.on_command_callback = callback
        
        self._change_state(VoiceState.LISTENING)
        
        # Start listening in a separate thread
        threading.Thread(target=self._listen_loop, daemon=True).start()
    
    def _listen_loop(self) -> None:
        """Continuously listen for voice commands."""
        with sr.Microphone() as source:
            print("Adjusting for ambient noise...")
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            print("Ready to listen")
            
            while not self._stop_event.is_set() and self.state == VoiceState.LISTENING:
                try:
                    print("Listening...")
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
                    
                    # Change to processing state
                    self._change_state(VoiceState.PROCESSING)
                    
                    try:
                        # Recognize speech using Google Web Speech API
                        text = self.recognizer.recognize_google(audio, language=self.language)
                        confidence = 0.9  # Google doesn't provide confidence, so we'll use a default
                        
                        # Create a voice command
                        command = VoiceCommand(
                            text=text,
                            confidence=confidence,
                            timestamp=time.time(),
                            raw_data=audio
                        )
                        
                        print(f"Heard: {text}")
                        
                        # Call the callback if provided
                        if self.on_command_callback:
                            self.on_command_callback(command)
                        
                    except sr.UnknownValueError:
                        print("Could not understand audio")
                    except sr.RequestError as e:
                        print(f"Could not request results; {e}")
                    
                    # Return to listening state
                    self._change_state(VoiceState.LISTENING)
                    
                except sr.WaitTimeoutError:
                    # No speech detected, continue listening
                    continue
                except Exception as e:
                    print(f"Error in listen loop: {e}")
                    self._change_state(VoiceState.ERROR)
                    break
    
    def speak(self, text: str, block: bool = False) -> None:
        """Convert text to speech and play it."""
        if not text.strip():
            return
        
        # Add to the audio queue
        self.audio_queue.put(text)
        
        # If blocking, wait for the speech to finish
        if block:
            while self.state == VoiceState.SPEAKING and not self.audio_queue.empty():
                time.sleep(0.1)
    
    def _audio_worker(self) -> None:
        """Background worker for processing the audio queue."""
        while not self._stop_event.is_set():
            try:
                # Get text from the queue with a timeout to allow checking the stop event
                try:
                    text = self.audio_queue.get(timeout=0.5)
                except queue.Empty:
                    continue
                
                self._change_state(VoiceState.SPEAKING)
                
                # Generate speech using gTTS
                tts = gTTS(text=text, lang=self.language[:2])  # Use first two chars for language code
                
                # Save to a temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as f:
                    temp_filename = f.name
                    tts.save(temp_filename)
                
                # Play the audio
                pygame.mixer.music.load(temp_filename)
                pygame.mixer.music.play()
                
                # Wait for playback to finish
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)
                
                # Clean up
                pygame.mixer.music.unload()
                try:
                    os.unlink(temp_filename)
                except:
                    pass
                
                # If queue is empty, go back to idle
                if self.audio_queue.empty():
                    self._change_state(VoiceState.IDLE)
                
            except Exception as e:
                print(f"Error in audio worker: {e}")
                self._change_state(VoiceState.ERROR)
                time.sleep(1)  # Prevent tight loop on error
    
    def stop(self) -> None:
        """Stop all voice activities and clean up."""
        self._stop_event.set()
        pygame.mixer.quit()
        self._change_state(VoiceState.IDLE)
    
    def _change_state(self, new_state: VoiceState) -> None:
        """Update the state and notify listeners."""
        old_state = self.state
        self.state = new_state
        
        if self.on_state_change:
            self.on_state_change(old_state, new_state)
    
    def is_listening(self) -> bool:
        """Check if the voice controller is currently listening."""
        return self.state == VoiceState.LISTENING
    
    def is_speaking(self) -> bool:
        """Check if the voice controller is currently speaking."""
        return self.state == VoiceState.SPEAKING

# Example usage
if __name__ == "__main__":
    import time
    
    def on_command(command: VoiceCommand):
        print(f"Command received: {command.text}")
        # Echo back what was heard
        vc.speak(f"You said: {command.text}")
    
    def on_state_change(old_state: VoiceState, new_state: VoiceState):
        print(f"Voice state changed from {old_state.name} to {new_state.name}")
    
    # Create and configure the voice controller
    vc = VoiceController()
    vc.on_command_callback = on_command
    vc.on_state_change = on_state_change
    
    try:
        print("Starting voice controller. Say something!")
        vc.start_listening()
        
        # Keep the main thread alive
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nStopping voice controller...")
        vc.stop()
