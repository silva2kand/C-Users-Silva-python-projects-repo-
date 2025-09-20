"""
AI Core Module for the AI Mouse Bot
Handles all AI/ML functionalities including NLP, intent recognition, and behavior prediction.
"""

import os
import json
import random
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import numpy as np
import spacy
from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer
from sentence_transformers import SentenceTransformer
import torch
from collections import defaultdict, deque

class AICore:
    def __init__(self, model_name: str = "gpt2"):
        """Initialize the AI core with pre-trained models."""
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.nlp = spacy.load("en_core_web_sm")
        self.model_name = model_name
        
        # Initialize language model
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.language_model = AutoModelForCausalLM.from_pretrained(model_name)
        self.language_model.to(self.device)
        
        # Initialize sentence transformer for semantic similarity
        self.sentence_encoder = SentenceTransformer('all-MiniLM-L6-v2')
        
        # User context and memory
        self.user_context = {
            "recent_actions": deque(maxlen=10),
            "preferences": {},
            "mood": "neutral",
            "last_interaction": None
        }
        
        # Personality traits (can be customized)
        self.personality = {
            "name": "Nova",
            "traits": {
                "friendliness": 0.8,
                "humor": 0.6,
                "helpfulness": 0.9,
                "energy": 0.7
            },
            "mood": "neutral",
            "mood_weights": {
                "happy": ["excited", "joyful", "playful"],
                "neutral": ["calm", "focused", "attentive"],
                "sad": ["tired", "disappointed", "bored"]
            }
        }
        
        # Load or create user data
        self.user_data_path = os.path.join(os.path.expanduser("~"), ".ai_mouse_bot", "user_data.json")
        self.load_user_data()

    def process_input(self, text: str) -> Dict:
        """Process user input and return intent and entities."""
        # Update interaction time
        self.user_context["last_interaction"] = datetime.now().isoformat()
        
        # Basic NLP processing
        doc = self.nlp(text.lower())
        
        # Extract entities and intent
        entities = [{"text": ent.text, "label": ent.label_} for ent in doc.ents]
        intent = self._classify_intent(text)
        
        # Update context
        self.user_context["recent_actions"].append({
            "text": text,
            "intent": intent,
            "entities": entities,
            "timestamp": datetime.now().isoformat()
        })
        
        return {
            "intent": intent,
            "entities": entities,
            "response": self._generate_response(text, intent, entities)
        }
    
    def _classify_intent(self, text: str) -> str:
        """Classify user intent using semantic similarity."""
        # Example intents - can be expanded
        intents = {
            "greeting": ["hello", "hi", "hey", "greetings"],
            "farewell": ["bye", "goodbye", "see you", "farewell"],
            "thanks": ["thanks", "thank you", "appreciate it"],
            "help": ["help", "what can you do", "how to use"],
            "mood": ["how are you", "how do you feel", "what's up"],
            "command": ["follow", "stop", "go to", "click", "type", "scroll"],
            "joke": ["tell me a joke", "make me laugh"],
            "time": ["what time is it", "current time", "what's the time"]
        }
        
        # Encode input and compare with intent examples
        input_embedding = self.sentence_encoder.encode(text, convert_to_tensor=True)
        best_score = -1
        best_intent = "unknown"
        
        for intent, examples in intents.items():
            for example in examples:
                example_embedding = self.sentence_encoder.encode(example, convert_to_tensor=True)
                similarity = torch.nn.functional.cosine_similarity(
                    input_embedding.unsqueeze(0), 
                    example_embedding.unsqueeze(0)
                )
                if similarity > best_score:
                    best_score = similarity
                    best_intent = intent
        
        return best_intent if best_score > 0.5 else "unknown"
    
    def _generate_response(self, text: str, intent: str, entities: List[Dict]) -> str:
        """Generate a contextual response based on intent and entities."""
        # Update mood based on interaction
        self._update_mood(text)
        
        # Generate response based on intent
        responses = {
            "greeting": [
                f"Hi there! {self._get_mood_phrase('greeting')}",
                "Hello! How can I assist you today?",
                f"{self._time_based_greeting()}! I'm {self.personality['name']}. {self._get_mood_phrase('greeting')}"
            ],
            "farewell": [
                "Goodbye! Have a great day!",
                "See you later! Don't hesitate to return if you need anything.",
                "Farewell! It was nice interacting with you!"
            ],
            "thanks": [
                "You're welcome! Happy to help!",
                "Anytime! That's what I'm here for.",
                "No problem! Let me know if you need anything else."
            ],
            "help": [
                "I can help you with various tasks like navigating your computer, opening applications, ",
                "or answering questions. Just let me know what you need!",
                "I'm here to assist with tasks, answer questions, or just chat. What would you like to do?"
            ],
            "mood": [
                f"I'm feeling {self.personality['mood']} today! {self._get_mood_phrase('status')}",
                f"I'm doing {self.personality['mood']}, thanks for asking! {self._get_mood_phrase('status')}",
                f"I'm in a {self.personality['mood']} mood right now. {self._get_mood_phrase('status')}"
            ],
            "joke": [
                "Why don't scientists trust atoms? Because they make up everything!",
                "Did you hear about the mathematician who's afraid of negative numbers? He'll stop at nothing to avoid them!",
                "Why don't skeletons fight each other? They don't have the guts!"
            ],
            "time": [
                f"The current time is {datetime.now().strftime('%I:%M %p')}.",
                f"It's {datetime.now().strftime('%I:%M %p')} right now.",
                f"The clock shows {datetime.now().strftime('%I:%M %p')} at the moment."
            ]
        }
        
        # Default response for unknown intents
        default_responses = [
            "I'm not sure I understand. Could you rephrase that?",
            "I'm still learning! Could you try saying that differently?",
            "I didn't catch that. Could you explain in another way?"
        ]
        
        # Select response based on intent
        if intent in responses:
            return random.choice(responses[intent])
        return random.choice(default_responses)
    
    def _update_mood(self, text: str) -> None:
        """Update the AI's mood based on interaction."""
        # Simple mood detection based on keywords
        positive_words = ["great", "awesome", "amazing", "love", "happy"]
        negative_words = ["sad", "angry", "frustrated", "hate", "terrible"]
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            self.personality["mood"] = "happy"
        elif negative_count > positive_count:
            self.personality["mood"] = "sad"
        # Otherwise, keep the current mood
    
    def _get_mood_phrase(self, context: str) -> str:
        """Get a phrase based on current mood and context."""
        mood = self.personality["mood"]
        mood_phrases = {
            "happy": {
                "greeting": ["So glad to see you!", "What a wonderful time to chat!", "I'm excited to help!"],
                "status": ["Everything seems brighter today!", "I'm ready to take on the world!"]
            },
            "neutral": {
                "greeting": ["How can I assist you today?", "What can I do for you?"],
                "status": ["Ready to help with whatever you need!", "I'm here and ready to assist."]
            },
            "sad": {
                "greeting": ["Hello... I'm here to help.", "Hi... what can I do for you?"],
                "status": ["I could use some cheering up...", "Not my best day, but I'm here to help."]
            }
        }
        
        if mood not in mood_phrases or context not in mood_phrases[mood]:
            return ""
        return random.choice(mood_phrases[mood][context])
    
    def _time_based_greeting(self) -> str:
        """Return a greeting based on the time of day."""
        hour = datetime.now().hour
        if 5 <= hour < 12:
            return "Good morning"
        elif 12 <= hour < 17:
            return "Good afternoon"
        elif 17 <= hour < 22:
            return "Good evening"
        return "Good night"
    
    def predict_next_action(self) -> str:
        """Predict the user's next action based on history."""
        # Simple prediction based on recent actions
        if not self.user_context["recent_actions"]:
            return "waiting"
            
        last_action = self.user_context["recent_actions"][-1]
        if last_action["intent"] == "greeting":
            return "respond_to_greeting"
        return "waiting"
    
    def save_user_data(self) -> None:
        """Save user data to a file."""
        os.makedirs(os.path.dirname(self.user_data_path), exist_ok=True)
        with open(self.user_data_path, 'w') as f:
            json.dump({
                "user_context": self.user_context,
                "personality": self.personality,
                "last_updated": datetime.now().isoformat()
            }, f, indent=2)
    
    def load_user_data(self) -> None:
        """Load user data from a file."""
        if os.path.exists(self.user_data_path):
            try:
                with open(self.user_data_path, 'r') as f:
                    data = json.load(f)
                    self.user_context.update(data.get("user_context", {}))
                    self.personality.update(data.get("personality", self.personality))
            except (json.JSONDecodeError, IOError):
                # If there's an error loading, start fresh
                pass

    def __del__(self):
        """Save user data when the AI core is destroyed."""
        self.save_user_data()

# Example usage
if __name__ == "__main__":
    ai = AICore()
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("AI: Goodbye!")
            break
        
        response = ai.process_input(user_input)
        print(f"AI: {response['response']}")
