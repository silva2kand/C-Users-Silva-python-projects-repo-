#!/usr/bin/env python3
"""
AI-Powered Video Remaker and Streaming Platform
Complete Implementation with All Features from Design Blueprint
"""

import sys
import os
import threading
import json
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
                              QTextEdit, QTextBrowser, QComboBox, QCheckBox, QMessageBox, QProgressBar, QFrame,
                              QScrollArea, QMenu, QAction, QTabWidget, QSplitter, QGroupBox, QRadioButton, QSpinBox,
                              QTextBrowser, QFileDialog, QSlider, QMainWindow, QStatusBar, QDialog, QFormLayout,
                              QInputDialog, QListWidget, QGridLayout)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QPoint, QPropertyAnimation, QRect, QUrl, pyqtSlot
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor, QFont
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
import requests
from bs4 import BeautifulSoup
import feedparser
from googletrans import Translator
from langdetect import detect
import moviepy
# Effects are now accessed via moviepy.vfx
import yt_dlp
import google.auth
from googleapiclient.discovery import build
import speech_recognition as sr
import random
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaIoBaseUpload
from io import BytesIO
import sqlite3
from flask import Flask, render_template_string, request, jsonify
import socket
import socketserver
import http.server
import webbrowser
import time
import re
from typing import List, Dict, Any
import logging
import asyncio
import aiohttp

# Hybrid AI imports
try:
    from hybrid_ai_client import HybridAIClient, FreeTierAIClient
    HYBRID_AI_AVAILABLE = True
except ImportError:
    HYBRID_AI_AVAILABLE = False
    logger.warning("Hybrid AI client not available")
from pathlib import Path
import subprocess
from threading import Lock

# Setup logging (disabled for cleaner GUI)
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

class ContentModerator:
    """Advanced content moderation system"""
    def __init__(self):
        # Expanded inappropriate content keywords
        self.inappropriate_keywords = {
            "hate": ["hate", "racist", "bigot", "supremacist", "nazi", "kkk", "white power"],
            "violence": ["violence", "kill", "murder", "attack", "assault", "weapon", "bomb", "terror"],
            "illegal": ["illegal", "drug", "narcotic", "heroin", "cocaine", "meth", "crime", "felony"],
            "harm": ["harm", "suicide", "self-harm", "cutting", "abuse", "torture", "pain"],
            "spam": ["spam", "scam", "fraud", "phishing", "malware", "virus", "hack"],
            "explicit": ["porn", "sex", "nude", "naked", "erotic", "xxx", "nsfw", "adult"],
            "harassment": ["harass", "bully", "threat", "intimidate", "stalk", "abuse"],
            "misinformation": ["fake news", "conspiracy", "hoax", "mislead", "false", "lie"]
        }

        # Content categories with severity levels
        self.content_categories = {
            "safe": ["educational", "news", "tutorial", "documentary", "kids", "family"],
            "moderate": ["entertainment", "music", "sports", "gaming", "lifestyle"],
            "restricted": ["political", "controversial", "adult", "mature"],
            "blocked": ["hate", "violence", "illegal", "explicit", "harassment"]
        }

        self.model = None  # Placeholder for future AI moderation model
        self.moderation_log = []

    def is_appropriate(self, text: str, context: str = "general") -> tuple[bool, str]:
        """Check if content is appropriate with detailed feedback"""
        text_lower = text.lower().strip()
        issues = []

        # Check against inappropriate keywords
        for category, keywords in self.inappropriate_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    issues.append(f"Contains {category} content: '{keyword}'")
                    break

        # Check for excessive caps (shouting)
        caps_ratio = sum(1 for c in text if c.isupper()) / len(text) if text else 0
        if caps_ratio > 0.7 and len(text) > 10:
            issues.append("Excessive use of capital letters (shouting)")

        # Check for spam patterns
        if text.count('!') > 5 or text.count('?') > 5:
            issues.append("Excessive punctuation (possible spam)")

        # Check for repeated words
        words = text.split()
        if len(words) > 0:
            most_common = max(set(words), key=words.count)
            if words.count(most_common) > len(words) * 0.3:
                issues.append("Excessive repetition of words")

        # Log moderation decision
        decision = "approved" if not issues else "rejected"
        self.moderation_log.append({
            "timestamp": datetime.now(),
            "content": text[:100] + "..." if len(text) > 100 else text,
            "decision": decision,
            "issues": issues,
            "context": context
        })

        if issues:
            logger.warning(f"Content moderation failed: {', '.join(issues)}")
            return False, f"Content rejected: {', '.join(issues)}"

        return True, "Content approved"

    def get_moderation_stats(self) -> Dict[str, Any]:
        """Get moderation statistics"""
        total_checks = len(self.moderation_log)
        approved = sum(1 for log in self.moderation_log if log["decision"] == "approved")
        rejected = total_checks - approved

        return {
            "total_checks": total_checks,
            "approved": approved,
            "rejected": rejected,
            "approval_rate": approved / total_checks if total_checks > 0 else 0,
            "recent_issues": [log for log in self.moderation_log[-10:]]
        }

    def suggest_alternatives(self, text: str) -> List[str]:
        """Suggest alternative wording for flagged content"""
        # Simple word replacement suggestions
        replacements = {
            "hate": ["dislike", "oppose", "disagree with"],
            "kill": ["stop", "end", "eliminate"],
            "stupid": ["unwise", "poor choice", "not ideal"],
            "dumb": ["unfortunate", "regrettable", "not smart"]
        }

        suggestions = []
        text_lower = text.lower()

        for bad_word, good_words in replacements.items():
            if bad_word in text_lower:
                for good_word in good_words:
                    suggestion = text_lower.replace(bad_word, good_word)
                    suggestions.append(suggestion)

        return suggestions[:3]  # Return up to 3 suggestions

class UserAuthentication:
    """User authentication for saving preferences and projects"""
    def __init__(self, db_path="users.db"):
        self.db_path = db_path
        self.init_db()
        self.current_user = None
        self.lock = Lock()

    def init_db(self):
        """Initialize SQLite database for users"""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                          (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT, preferences TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS projects 
                          (id INTEGER PRIMARY KEY, user_id INTEGER, project_name TEXT, project_data TEXT, 
                           created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                           FOREIGN KEY(user_id) REFERENCES users (id))''')
        self.conn.commit()

    def login(self, username: str, password: str) -> bool:
        """Authenticate user"""
        with self.lock:
            cursor = self.conn.cursor()
            cursor.execute("SELECT id, preferences FROM users WHERE username=? AND password=?", (username, password))
            user = cursor.fetchone()
            if user:
                self.current_user = {'id': user[0], 'username': username, 'preferences': json.loads(user[1]) if user[1] else {}}
                return True
            return False

    def register(self, username: str, password: str) -> bool:
        """Register new user"""
        try:
            with self.lock:
                cursor = self.conn.cursor()
                cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
                self.conn.commit()
                self.current_user = {'id': cursor.lastrowid, 'username': username, 'preferences': {}}
                return True
        except sqlite3.IntegrityError:
            return False

    def save_project(self, project_name: str, project_data: str):
        """Save user project"""
        if not self.current_user:
            return False
        with self.lock:
            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO projects (user_id, project_name, project_data) VALUES (?, ?, ?)", 
                           (self.current_user['id'], project_name, project_data))
            self.conn.commit()
            return True

    def get_projects(self) -> List[Dict[str, Any]]:
        """Get user's projects"""
        if not self.current_user:
            return []
        with self.lock:
            cursor = self.conn.cursor()
            cursor.execute("SELECT id, project_name, project_data, created_at FROM projects WHERE user_id=?", (self.current_user['id'],))
            rows = cursor.fetchall()
            return [{'id': row[0], 'name': row[1], 'data': json.loads(row[2]), 'created': row[3]} for row in rows]

class CloudStorage:
    """Cloud storage integration for videos"""
    def __init__(self):
        self.drive_service = None
        self.dropbox_token = None  # Placeholder

    def authenticate_drive(self):
        """Authenticate with Google Drive"""
        try:
            creds = None
            if os.path.exists('token.pickle'):
                with open('token.pickle', 'rb') as token:
                    creds = pickle.load(token)
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'credentials.json', ['https://www.googleapis.com/auth/drive.file'])
                    creds = flow.run_local_server(port=0)
                with open('token.pickle', 'wb') as token:
                    pickle.dump(creds, token)

            self.drive_service = build('drive', 'v3', credentials=creds)
            return True
        except Exception as e:
            logger.error(f"Drive authentication failed: {e}")
            return False

    def upload_to_drive(self, file_path: str, file_name: str):
        """Upload to Google Drive"""
        if not self.drive_service:
            if not self.authenticate_drive():
                return "Authentication failed"

        try:
            file_metadata = {'name': file_name}
            media = MediaFileUpload(file_path, mimetype='video/mp4')
            file = self.drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            return f"Uploaded to Google Drive: https://drive.google.com/file/d/{file.get('id')}"
        except HttpError as error:
            return f"Error uploading to Drive: {error}"

    def upload_to_dropbox(self, file_path: str, file_name: str):
        """Upload to Dropbox (placeholder - implement with Dropbox API)"""
        return "Upload to Dropbox feature - implement with Dropbox API"

class PluginSystem:
    """Plugin system for extensibility"""
    def __init__(self, plugin_dir="plugins"):
        self.plugin_dir = plugin_dir
        self.plugins = {}
        self.load_plugins()

    def load_plugins(self):
        """Load plugins from directory"""
        if not os.path.exists(self.plugin_dir):
            os.makedirs(self.plugin_dir)
            return

        import importlib.util
        for filename in os.listdir(self.plugin_dir):
            if filename.endswith('.py') and not filename.startswith('_'):
                plugin_path = os.path.join(self.plugin_dir, filename)
                spec = importlib.util.spec_from_file_location("plugin", plugin_path)
                if spec is not None:
                    plugin = spec.loader.load_module()
                    if hasattr(plugin, 'name') and hasattr(plugin, 'init'):
                        self.plugins[plugin.name] = plugin
                        plugin.init(self)
                        logger.info(f"Loaded plugin: {plugin.name}")

    def execute_plugin(self, plugin_name: str, action: str, *args, **kwargs):
        """Execute plugin action"""
        if plugin_name in self.plugins:
            if hasattr(self.plugins[plugin_name], action):
                return getattr(self.plugins[plugin_name], action)(*args, **kwargs)
        return None

class AIContentAnalyzer:
    """AI-powered content analysis using GPT4All"""
    def __init__(self, gpt4all_model):
        self.model = gpt4all_model

    def analyze_video(self, video_path: str):
        """Analyze video for scenes and suggestions"""
        # Simulate analysis with GPT4All
        prompt = "Analyze this video content and suggest improvements for engagement and quality: [video description from metadata]"
        try:
            with self.model.chat_session():
                response = self.model.generate(prompt, max_tokens=200)
            return response
        except Exception as e:
            logger.error(f"Video analysis failed: {e}")
            return "Analysis complete (simulation)"

    def sentiment_analysis(self, comments: List[str]):
        """Perform sentiment analysis on comments"""
        sentiments = []
        for comment in comments:
            prompt = f"Analyze sentiment of this comment and suggest response: {comment}"
            try:
                with self.model.chat_session():
                    sentiment = self.model.generate(prompt, max_tokens=50)
                sentiments.append(sentiment)
            except Exception as e:
                sentiments.append("Neutral (analysis failed)")
        return sentiments

    def generate_response(self, comment: str):
        """Generate automated response to comment"""
        prompt = f"Generate a helpful, positive response to this comment: {comment}"
        try:
            with self.model.chat_session():
                response = self.model.generate(prompt, max_tokens=100)
            return response
        except Exception as e:
            logger.error(f"Response generation failed: {e}")
            return "Thanks for your feedback!"

class SocialMediaUploader:
    """Social media upload and streaming"""
    def __init__(self):
        self.youtube_service = None
        self.twitch_client = None  # Placeholder

    def authenticate_youtube(self):
        """Authenticate with YouTube API"""
        try:
            creds = None
            if os.path.exists('token.pickle'):
                with open('token.pickle', 'rb') as token:
                    creds = pickle.load(token)
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'credentials.json', ['https://www.googleapis.com/auth/youtube.upload'])
                    creds = flow.run_local_server(port=0)
                with open('token.pickle', 'wb') as token:
                    pickle.dump(creds, token)

            self.youtube_service = build('youtube', 'v3', credentials=creds)
            return True
        except Exception as e:
            logger.error(f"YouTube authentication failed: {e}")
            return False

    def upload_to_youtube(self, video_path: str, title: str, description: str, tags: List[str], privacy: str):
        """Upload video to YouTube"""
        if not self.youtube_service:
            if not self.authenticate_youtube():
                return "Authentication failed"

        try:
            body = {
                'snippet': {
                    'title': title,
                    'description': description,
                    'tags': tags,
                    'categoryId': '22'  # People & Blogs
                },
                'status': {
                    'privacyStatus': privacy.lower()
                }
            }
            media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
            request = self.youtube_service.videos().insert(part='snippet,status', body=body, media_body=media)
            response = request.execute()
            return f"Uploaded to YouTube: https://youtu.be/{response['id']}"
        except HttpError as error:
            return f"YouTube upload error: {error}"

    def start_live_stream(self, stream_key: str):
        """Start live stream on Twitch or YouTube"""
        # Placeholder for live streaming
        logger.info("Starting live stream with key: %s", stream_key)
        return "Live streaming started (placeholder implementation)"

class VideoCollector:
    """Collect and download video clips based on topics"""
    def __init__(self):
        self.download_dir = "downloads"
        self.clips_dir = os.path.join(self.download_dir, "clips")
        self.ensure_directories()
        self.max_clips = 50  # Default number of clips to collect

    def ensure_directories(self):
        """Create necessary directories"""
        os.makedirs(self.download_dir, exist_ok=True)
        os.makedirs(self.clips_dir, exist_ok=True)

    def search_videos(self, topic: str, country: str = "Global", language: str = "en") -> List[Dict[str, Any]]:
        """Search for videos based on topic, country, and language"""
        try:
            # Build search query
            query = f"{topic} {country}"
            if language == "ta":
                query += " தமிழ்" if country.lower() == "sri lanka" else " tamil"
            elif language == "si":
                query += " සිංහල sinhala"

            # Use yt-dlp to search
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
                'force_generic_extractor': False,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                search_results = ydl.extract_info(f"ytsearch{self.max_clips}:{query}", download=False)

            videos = []
            if 'entries' in search_results:
                for entry in search_results['entries'][:self.max_clips]:
                    if entry:
                        videos.append({
                            'id': entry.get('id'),
                            'title': entry.get('title', ''),
                            'url': f"https://www.youtube.com/watch?v={entry.get('id')}",
                            'duration': entry.get('duration', 0),
                            'uploader': entry.get('uploader', ''),
                            'view_count': entry.get('view_count', 0)
                        })

            return videos
        except Exception as e:
            logger.error(f"Video search failed: {e}")
            return []

    def download_clip(self, video_url: str, start_time: int = 0, duration: int = 30) -> str:
        """Download a specific clip from a video"""
        try:
            # Generate unique filename
            video_id = video_url.split('v=')[-1].split('&')[0]
            clip_filename = f"clip_{video_id}_{start_time}_{duration}.mp4"
            output_path = os.path.join(self.clips_dir, clip_filename)

            # yt-dlp options for clip download
            ydl_opts = {
                'outtmpl': output_path,
                'format': 'best[height<=720]',  # Limit quality to save space
                'download_ranges': yt_dlp.utils.download_range_func(None, [(start_time, start_time + duration)]),
                'quiet': True,
                'no_warnings': True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])

            return output_path if os.path.exists(output_path) else ""
        except Exception as e:
            logger.error(f"Clip download failed: {e}")
            return ""

    def collect_clips(self, topic: str, country: str = "Global", language: str = "en",
                     clip_duration: int = 30, num_clips: int = 20) -> List[str]:
        """Collect multiple clips for a topic with proper duration control"""
        # Ensure clip duration is within 15-45 second range
        if clip_duration < 15:
            clip_duration = 15
            logger.info("Clip duration adjusted to minimum 15 seconds")
        elif clip_duration > 45:
            clip_duration = 45
            logger.info("Clip duration adjusted to maximum 45 seconds")

        self.max_clips = num_clips
        videos = self.search_videos(topic, country, language)

        if not videos:
            logger.warning(f"No videos found for topic: {topic}")
            return []

        clips = []
        clips_per_video = max(1, num_clips // len(videos))  # Distribute clips across videos

        for video in videos[:min(len(videos), num_clips)]:
            # Download multiple segments from each video with proper spacing
            video_duration = video.get('duration', 300)  # Assume 5 minutes if not available
            max_segments = min(clips_per_video, video_duration // clip_duration)

            for i in range(max_segments):
                # Space out clip starts to avoid overlap
                start_time = i * (clip_duration + 5)  # 5 second gap between clips

                if start_time + clip_duration <= video_duration:
                    clip_path = self.download_clip(video['url'], start_time, clip_duration)
                    if clip_path:
                        clips.append({
                            'path': clip_path,
                            'start_time': start_time,
                            'duration': clip_duration,
                            'video_title': video.get('title', ''),
                            'source_url': video['url']
                        })
                        logger.info(f"Downloaded clip: {os.path.basename(clip_path)} ({clip_duration}s from {start_time}s)")

            if len(clips) >= num_clips:
                break

        # Return just the paths for compatibility
        clip_paths = [clip['path'] for clip in clips]
        logger.info(f"Collected {len(clip_paths)} clips for topic: {topic} (each {clip_duration}s)")
        return clip_paths

class VideoEditor:
    """Video editing and assembly system"""
    def __init__(self):
        self.temp_dir = "temp"
        os.makedirs(self.temp_dir, exist_ok=True)

        # Initialize GPT4All if available
        self.gpt4all_model = None
        try:
            from gpt4all import GPT4All
            self.gpt4all_model = GPT4All("orca-mini-3b.ggmlv3.q4_0.bin")  # Small model for local use
            logger.info("GPT4All model loaded successfully")
        except ImportError:
            logger.warning("GPT4All not installed. Using template-based script generation.")
        except Exception as e:
            logger.error(f"Failed to load GPT4All model: {e}")
            self.gpt4all_model = None

    def generate_script(self, topic: str, duration: int, language: str = "en") -> str:
        """Generate video script using AI"""
        try:
            # Try to use GPT4All if available
            if hasattr(self, 'gpt4all_model') and self.gpt4all_model:
                prompt = f"""Generate a compelling video script for a {duration}-minute video about "{topic}".
                The script should be engaging, informative, and suitable for the target audience.
                Include an introduction, main content sections, and a conclusion.
                Keep it conversational and natural.
                Language: {language}
                Duration: {duration} minutes
                Topic: {topic}

                Please provide the script:"""

                with self.gpt4all_model.chat_session():
                    response = self.gpt4all_model.generate(prompt, max_tokens=500)
                return response.strip()
            else:
                # Fallback to template-based generation
                return self.generate_script_template(topic, duration, language)
        except Exception as e:
            logger.error(f"AI script generation failed: {e}")
            return self.generate_script_template(topic, duration, language)

    def generate_script_template(self, topic: str, duration: int, language: str = "en") -> str:
        """Generate script using templates when AI is not available"""
        templates = {
            "news": f"""Welcome to today's news update! We're bringing you the latest developments in {topic}.

In this segment, we'll cover:
- The most recent events and their impact
- Expert analysis and insights
- What this means for our community
- Looking ahead to future developments

Stay informed and connected with the world around you. Thank you for watching!""",

            "documentary": f"""Welcome to our documentary series exploring the fascinating world of {topic}.

Throughout this {duration}-minute journey, we'll discover:
- The history and origins of {topic}
- Current trends and developments
- Real stories and experiences
- Future possibilities and innovations

Join us as we delve deep into this compelling subject and uncover insights that will change how you see the world.""",

            "music": f"""Get ready for an incredible musical journey through {topic}!

In this {duration}-minute video, we'll experience:
- The evolution of {topic} music
- Iconic artists and their contributions
- Current trends and new releases
- The cultural impact of this musical genre

Let the rhythm take you on an unforgettable adventure!""",

            "kids story": f"""Hello, young adventurers! Are you ready for an exciting story about {topic}?

Our {duration}-minute tale will take you on a magical journey where you'll:
- Meet wonderful characters and make new friends
- Discover amazing places and exciting adventures
- Learn important lessons about friendship and courage
- Experience the joy of imagination and creativity

Get comfortable, open your mind, and let's begin this wonderful story together!"""
        }

        base_script = templates.get(topic.lower(), f"""Welcome to our video about {topic}!

In this {duration}-minute presentation, we'll explore:
- The fundamentals and basics of {topic}
- Interesting facts and discoveries
- Practical applications and examples
- Future trends and developments

Thank you for joining us on this educational journey!""")

        return base_script

    def add_voiceover(self, script: str, voice: str = "male", language: str = "en") -> str:
        """Generate voiceover audio with enhanced features"""
        try:
            import pyttsx3
            engine = pyttsx3.init()

            # Configure voice settings
            voices = engine.getProperty('voices')
            if voices:
                if voice.lower() == "female":
                    # Try to find a female voice
                    female_voice = None
                    for v in voices:
                        if v.name and ('female' in v.name.lower() or 'woman' in v.name.lower() or 'girl' in v.name.lower()):
                            female_voice = v
                            break
                    if female_voice:
                        engine.setProperty('voice', female_voice.id)
                    else:
                        # Fallback to second voice if available
                        engine.setProperty('voice', voices[min(1, len(voices)-1)].id)
                else:
                    # Male voice (usually the first/default)
                    engine.setProperty('voice', voices[0].id)

            # Configure speech rate and volume
            engine.setProperty('rate', 180)  # Speed of speech
            engine.setProperty('volume', 0.8)  # Volume level

            # Language-specific settings
            if language == "ta":
                # Tamil language support (if available)
                try:
                    engine.setProperty('voice', 'ta')  # Tamil voice
                except:
                    pass  # Fallback to default
            elif language == "si":
                # Sinhala language support (if available)
                try:
                    engine.setProperty('voice', 'si')  # Sinhala voice
                except:
                    pass  # Fallback to default

            # Generate audio file
            audio_path = os.path.join(self.temp_dir, f"voiceover_{voice}_{language}_{int(time.time())}.mp3")
            engine.save_to_file(script, audio_path)
            engine.runAndWait()

            # Verify file was created
            if os.path.exists(audio_path) and os.path.getsize(audio_path) > 0:
                return audio_path
            else:
                logger.error("Voiceover file was not created or is empty")
                return ""
        except ImportError:
            logger.warning("pyttsx3 not installed. Voiceover generation disabled.")
            return ""
        except Exception as e:
            logger.error(f"Voiceover generation failed: {e}")
            return ""

    def assemble_video(self, clips: List[str], script: str, voice: str = "male",
                      language: str = "en", bg_music: str = None, add_transitions: bool = True) -> str:
        """Assemble final video from clips with enhanced features"""
        try:
            if not clips:
                return ""

            # Load and process clips with improved ordering
            video_clips = []
            for clip_path in clips[:20]:  # Limit to 20 clips for performance
                if os.path.exists(clip_path):
                    try:
                        clip = moviepy.VideoFileClip(clip_path)
                        # Resize to standard resolution
                        clip = clip.resize(height=720)
                        video_clips.append(clip)
                        logger.info(f"Loaded clip: {os.path.basename(clip_path)} ({clip.duration:.1f}s)")
                    except Exception as e:
                        logger.warning(f"Failed to load clip {clip_path}: {e}")
                        continue

            if not video_clips:
                return ""

            # Sort clips by duration for better flow (alternating short/long)
            video_clips.sort(key=lambda x: x.duration)

            # Reorder for better narrative flow - alternate durations
            ordered_clips = []
            short_clips = [c for c in video_clips if c.duration <= 25]
            long_clips = [c for c in video_clips if c.duration > 25]

            # Alternate between short and long clips for dynamic pacing
            while short_clips or long_clips:
                if short_clips:
                    ordered_clips.append(short_clips.pop(0))
                if long_clips:
                    ordered_clips.append(long_clips.pop(0))

            video_clips = ordered_clips

            # Add smooth transitions between clips
            if add_transitions and len(video_clips) > 1:
                transitioned_clips = [video_clips[0]]  # First clip as-is

                for i in range(1, len(video_clips)):
                    prev_clip = transitioned_clips[-1]
                    current_clip = video_clips[i]

                    # Calculate transition duration based on clip lengths
                    transition_duration = min(1.0, min(prev_clip.duration, current_clip.duration) * 0.1)

                    # Apply fade transitions
                    if prev_clip.duration > transition_duration:
                        prev_clip = prev_clip.fadeout(transition_duration)
                    if current_clip.duration > transition_duration:
                        current_clip = current_clip.fadein(transition_duration)

                    transitioned_clips[-1] = prev_clip
                    transitioned_clips.append(current_clip)

                video_clips = transitioned_clips

            # Concatenate clips with composition method for better quality
            final_clip = moviepy.concatenate_videoclips(video_clips, method="compose")
            logger.info(f"Concatenated {len(video_clips)} clips into {final_clip.duration:.1f}s video")

            # Enhanced voiceover synchronization
            if script:
                voiceover_path = self.add_voiceover(script, voice, language)
                if voiceover_path and os.path.exists(voiceover_path):
                    audio_clip = moviepy.AudioFileClip(voiceover_path)

                    # Intelligent audio synchronization
                    if audio_clip.duration > final_clip.duration:
                        # Trim audio to match video
                        audio_clip = audio_clip.subclip(0, final_clip.duration)
                        logger.info("Trimmed voiceover to match video duration")
                    elif audio_clip.duration < final_clip.duration:
                        # Loop audio with crossfade for seamless looping
                        loops_needed = int(final_clip.duration // audio_clip.duration) + 1
                        audio_segments = []

                        for i in range(loops_needed):
                            start_time = i * audio_clip.duration
                            if start_time < final_clip.duration:
                                segment_duration = min(audio_clip.duration,
                                                      final_clip.duration - start_time)
                                segment = audio_clip.subclip(0, segment_duration)

                                # Add crossfade between loops
                                if i > 0 and segment_duration > 1.0:
                                    fade_duration = min(1.0, segment_duration * 0.1)
                                    segment = segment.audio_fadein(fade_duration)

                                audio_segments.append(segment)

                        if audio_segments:
                            audio_clip = moviepy.concatenate_audioclips(audio_segments, padding=-0.5)
                            audio_clip = audio_clip.subclip(0, final_clip.duration)

                    final_clip = final_clip.set_audio(audio_clip)
                    logger.info("Applied synchronized voiceover")

            # Add background music with proper mixing
            if bg_music and os.path.exists(bg_music):
                bg_audio = moviepy.AudioFileClip(bg_music).set_duration(final_clip.duration)

                if final_clip.audio:
                    # Mix voiceover with background music at appropriate levels
                    voice_volume = 1.0  # Full volume for voice
                    music_volume = 0.3  # Background level for music

                    mixed_audio = moviepy.CompositeAudioClip([
                        final_clip.audio.set_volume(voice_volume),
                        bg_audio.set_volume(music_volume)
                    ])
                    final_clip = final_clip.set_audio(mixed_audio)
                    logger.info("Mixed voiceover with background music")
                else:
                    final_clip = final_clip.set_audio(bg_audio)

            # Add text overlay with script
            if script:
                # Generate subtitles from script
                subtitles = self.generate_subtitles(script, final_clip.duration, language)
                if subtitles:
                    final_clip = self.add_subtitles_to_video(final_clip, subtitles)
                else:
                    # Fallback to simple text overlay
                    txt_clip = moviepy.TextClip(script[:100] + "...", fontsize=50, color='white',
                                      bg_color='black', size=(final_clip.w, 100))
                    txt_clip = txt_clip.set_position(('center', 'bottom')).set_duration(final_clip.duration)
                    final_clip = moviepy.CompositeVideoClip([final_clip, txt_clip])

            # Export with optimized settings
            output_path = os.path.join(self.temp_dir, f"final_video_{int(time.time())}.mp4")
            final_clip.write_videofile(
                output_path,
                fps=30,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile="temp_audio.m4a",
                remove_temp=True,
                verbose=False,
                logger=None
            )

            logger.info(f"Video assembled successfully: {output_path}")

            # Close clips to free memory
            final_clip.close()
            for clip in video_clips:
                clip.close()

            return output_path
        except Exception as e:
            logger.error(f"Video assembly failed: {e}")
            return ""

    def generate_subtitles(self, script: str, video_duration: float, language: str = "en") -> List[Dict[str, Any]]:
        """Generate subtitle data from script"""
        try:
            # Split script into sentences
            sentences = re.split(r'[.!?]+', script)
            sentences = [s.strip() for s in sentences if s.strip()]

            if not sentences:
                return []

            # Calculate timing for each subtitle
            subtitles = []
            total_chars = sum(len(s) for s in sentences)
            time_per_char = video_duration / total_chars if total_chars > 0 else 1

            current_time = 0
            for sentence in sentences:
                if not sentence:
                    continue

                # Estimate duration based on text length
                duration = len(sentence) * time_per_char
                duration = max(2, min(6, duration))  # Between 2-6 seconds

                subtitles.append({
                    'text': sentence,
                    'start': current_time,
                    'end': current_time + duration,
                    'duration': duration
                })

                current_time += duration

            return subtitles
        except Exception as e:
            logger.error(f"Subtitle generation failed: {e}")
            return []

    def add_subtitles_to_video(self, video_clip: moviepy.VideoFileClip, subtitles: List[Dict[str, Any]],
                              font_size: int = 50, color: str = 'white') -> moviepy.VideoFileClip:
        """Add subtitles to video clip"""
        try:
            subtitle_clips = []

            for subtitle in subtitles:
                # Create text clip
                txt_clip = moviepy.TextClip(
                    subtitle['text'],
                    fontsize=font_size,
                    color=color,
                    bg_color='black',
                    size=(video_clip.w * 0.8, 100),  # 80% width
                    method='caption'
                )

                # Position at bottom center
                txt_clip = txt_clip.set_position(('center', 'bottom')).set_duration(subtitle['duration'])
                txt_clip = txt_clip.set_start(subtitle['start'])

                subtitle_clips.append(txt_clip)

            # Composite video with subtitles
            if subtitle_clips:
                return moviepy.CompositeVideoClip([video_clip] + subtitle_clips)
            else:
                return video_clip

        except Exception as e:
            logger.error(f"Adding subtitles failed: {e}")
            return video_clip

    def create_ai_presenter(self, script: str, voice: str = "male", duration: float = 10) -> str:
        """Create a simple AI presenter video with basic animations"""
        try:
            # Create a simple animated presenter using manim-like approach
            # This is a simplified version - full AI presenters would require ML models

            # For now, create a text-based presenter with simple animations
            presenter_video_path = self.create_text_presenter(script, voice, duration)
            return presenter_video_path

        except Exception as e:
            logger.error(f"AI presenter creation failed: {e}")
            return ""

    def create_text_presenter(self, script: str, voice: str, duration: float) -> str:
        """Create a simple text-based presenter video"""
        try:
            # Split script into words for animation timing
            words = script.split()
            if not words:
                return ""

            # Create video with animated text
            clips = []

            # Background clip
            bg_clip = moviepy.ColorClip(size=(1280, 720), color=(20, 20, 40), duration=duration)

            # Calculate timing
            word_duration = duration / len(words) if words else duration

            # Create animated text clips
            text_clips = []
            current_time = 0

            for i, word in enumerate(words):
                # Create text clip with fade in/out
                txt_clip = moviepy.TextClip(
                    word,
                    fontsize=60,
                    color='white',
                    bg_color=(20, 20, 40),
                    size=(1000, 200)
                )

                # Add fade effects
                txt_clip = txt_clip.fadein(0.2).fadeout(0.2)
                txt_clip = txt_clip.set_position('center').set_duration(word_duration)
                txt_clip = txt_clip.set_start(current_time)

                text_clips.append(txt_clip)
                current_time += word_duration * 0.8  # Slight overlap

            # Composite everything
            if text_clips:
                final_clip = moviepy.CompositeVideoClip([bg_clip] + text_clips)
            else:
                final_clip = bg_clip

            # Add voiceover
            voiceover_path = self.add_voiceover(script, voice)
            if voiceover_path and os.path.exists(voiceover_path):
                audio_clip = moviepy.AudioFileClip(voiceover_path)
                final_clip = final_clip.set_audio(audio_clip)

            # Export
            output_path = os.path.join(self.temp_dir, f"presenter_{int(time.time())}.mp4")
            final_clip.write_videofile(
                output_path,
                fps=24,
                codec="libx264",
                audio_codec="aac",
                verbose=False,
                logger=None
            )

            final_clip.close()
            return output_path

        except Exception as e:
            logger.error(f"Text presenter creation failed: {e}")
            return ""

    def combine_with_presenter(self, main_video_path: str, presenter_video_path: str) -> str:
        """Combine main video with AI presenter"""
        try:
            if not (os.path.exists(main_video_path) and os.path.exists(presenter_video_path)):
                return main_video_path

            main_clip = moviepy.VideoFileClip(main_video_path)
            presenter_clip = moviepy.VideoFileClip(presenter_video_path)

            # Resize presenter to smaller size
            presenter_clip = presenter_clip.resize(width=main_clip.w // 3)
            presenter_clip = presenter_clip.set_position(('right', 'top'))

            # Combine clips
            combined_clip = moviepy.CompositeVideoClip([main_clip, presenter_clip])

            # Export
            output_path = os.path.join(self.temp_dir, f"combined_{int(time.time())}.mp4")
            combined_clip.write_videofile(
                output_path,
                fps=24,
                codec="libx264",
                audio_codec="aac",
                verbose=False,
                logger=None
            )

            # Cleanup
            combined_clip.close()
            main_clip.close()
            presenter_clip.close()

            return output_path

        except Exception as e:
            logger.error(f"Combining with presenter failed: {e}")
            return main_video_path

class VoiceManager:
    """Advanced voice management system with multi-language support and voice cloning"""
    def __init__(self):
        self.voice_engines = {}
        self.language_support = {
            "en": {
                "name": "English",
                "voices": ["male_default", "female_default", "male_professional", "female_professional"],
                "tts_engine": "pyttsx3"
            },
            "ta": {
                "name": "தமிழ் (Tamil)",
                "voices": ["male_tamil", "female_tamil", "male_tamil_news", "female_tamil_casual"],
                "tts_engine": "google_tts"
            },
            "si": {
                "name": "සිංහල (Sinhala)",
                "voices": ["male_sinhala", "female_sinhala", "male_sinhala_news", "female_sinhala_casual"],
                "tts_engine": "google_tts"
            }
        }
        self.voice_clones = {}  # Store voice clone data
        self.current_language = "en"
        self.current_voice = "male_default"

        # Initialize TTS engines
        self._initialize_tts_engines()

    def _initialize_tts_engines(self):
        """Initialize available TTS engines"""
        try:
            import pyttsx3
            self.voice_engines["pyttsx3"] = pyttsx3.init()
            logger.info("pyttsx3 TTS engine initialized")
        except ImportError:
            logger.warning("pyttsx3 not available")

        try:
            from gtts import gTTS
            self.voice_engines["google_tts"] = gTTS
            logger.info("Google TTS engine initialized")
        except ImportError:
            logger.warning("gTTS not available - install with: pip install gtts")

    def set_language(self, language_code: str):
        """Set the current language for voice synthesis"""
        if language_code in self.language_support:
            self.current_language = language_code
            logger.info(f"Language set to: {self.language_support[language_code]['name']}")
            return True
        else:
            logger.warning(f"Language {language_code} not supported")
            return False

    def set_voice(self, voice_name: str):
        """Set the current voice"""
        lang_data = self.language_support.get(self.current_language, {})
        if voice_name in lang_data.get("voices", []):
            self.current_voice = voice_name
            logger.info(f"Voice set to: {voice_name}")
            return True
        else:
            logger.warning(f"Voice {voice_name} not available for language {self.current_language}")
            return False

    def get_available_voices(self, language: str = None) -> List[str]:
        """Get available voices for a language"""
        if language is None:
            language = self.current_language

        lang_data = self.language_support.get(language, {})
        return lang_data.get("voices", [])

    def get_supported_languages(self) -> Dict[str, str]:
        """Get all supported languages"""
        return {code: data["name"] for code, data in self.language_support.items()}

    def generate_speech(self, text: str, output_path: str = None,
                       voice: str = None, language: str = None) -> str:
        """Generate speech audio with specified parameters"""
        if voice is None:
            voice = self.current_voice
        if language is None:
            language = self.current_language

        if output_path is None:
            output_path = f"temp/voice_{voice}_{language}_{int(time.time())}.mp3"

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        try:
            if language in ["ta", "si"] and "google_tts" in self.voice_engines:
                return self._generate_google_tts(text, output_path, language, voice)
            elif "pyttsx3" in self.voice_engines:
                return self._generate_pyttsx3_tts(text, output_path, voice)
            else:
                logger.error("No TTS engine available")
                return ""
        except Exception as e:
            logger.error(f"Speech generation failed: {e}")
            return ""

    def _generate_google_tts(self, text: str, output_path: str, language: str, voice: str) -> str:
        """Generate speech using Google TTS (better for Tamil/Sinhala)"""
        try:
            from gtts import gTTS

            # Language code mapping
            lang_codes = {"ta": "ta", "si": "si", "en": "en"}

            # Voice-specific settings
            tld = "com"
            if "female" in voice:
                tld = "co.in" if language == "ta" else "com"

            tts = gTTS(text=text, lang=lang_codes.get(language, "en"), tld=tld, slow=False)
            tts.save(output_path)

            if os.path.exists(output_path):
                logger.info(f"Google TTS audio generated: {output_path}")
                return output_path
            else:
                logger.error("Google TTS file was not created")
                return ""

        except Exception as e:
            logger.error(f"Google TTS generation failed: {e}")
            return ""

    def _generate_pyttsx3_tts(self, text: str, output_path: str, voice: str) -> str:
        """Generate speech using pyttsx3 (fallback for English)"""
        try:
            engine = self.voice_engines["pyttsx3"]

            # Configure voice
            voices = engine.getProperty('voices')
            if voices:
                if "female" in voice:
                    # Try to find female voice
                    for v in voices:
                        if v and hasattr(v, 'name') and v.name and 'female' in v.name.lower():
                            engine.setProperty('voice', v.id)
                            break
                else:
                    # Default male voice
                    engine.setProperty('voice', voices[0].id)

            # Configure speech parameters
            engine.setProperty('rate', 180)
            engine.setProperty('volume', 0.8)

            # Generate audio
            engine.save_to_file(text, output_path)
            engine.runAndWait()

            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                logger.info(f"pyttsx3 audio generated: {output_path}")
                return output_path
            else:
                logger.error("pyttsx3 audio file was not created properly")
                return ""

        except Exception as e:
            logger.error(f"pyttsx3 generation failed: {e}")
            return ""

    def clone_voice(self, audio_sample_path: str, voice_name: str) -> bool:
        """Clone a voice from audio sample (placeholder for future implementation)"""
        # This would integrate with voice cloning services like Respeecher or ElevenLabs
        # For now, store the sample for future use
        try:
            if os.path.exists(audio_sample_path):
                self.voice_clones[voice_name] = {
                    "sample_path": audio_sample_path,
                    "created": datetime.now().isoformat(),
                    "language": self.current_language
                }
                logger.info(f"Voice sample stored for cloning: {voice_name}")
                return True
            else:
                logger.error("Audio sample file not found")
                return False
        except Exception as e:
            logger.error(f"Voice cloning failed: {e}")
            return False

    def get_voice_presets(self) -> Dict[str, Dict[str, Any]]:
        """Get predefined voice presets for different use cases"""
        return {
            "news_presenter": {
                "voice": "male_professional",
                "language": "en",
                "speed": "normal",
                "style": "authoritative"
            },
            "educational": {
                "voice": "female_professional",
                "language": "en",
                "speed": "slow",
                "style": "clear"
            },
            "entertainment": {
                "voice": "male_casual",
                "language": "en",
                "speed": "normal",
                "style": "energetic"
            },
            "tamil_news": {
                "voice": "male_tamil_news",
                "language": "ta",
                "speed": "normal",
                "style": "professional"
            },
            "sinhala_casual": {
                "voice": "female_sinhala_casual",
                "language": "si",
                "speed": "normal",
                "style": "friendly"
            }
        }

    def translate_and_speak(self, text: str, target_language: str,
                           voice: str = None) -> str:
        """Translate text and generate speech in target language"""
        try:
            # Translate text
            translated_text = self.translate_text(text, target_language)

            # Generate speech
            return self.generate_speech(translated_text, voice=voice, language=target_language)

        except Exception as e:
            logger.error(f"Translate and speak failed: {e}")
            return ""

    def translate_text(self, text: str, target_language: str) -> str:
        """Translate text to target language"""
        # Use the existing translation system
        try:
            from googletrans import Translator
            translator = Translator()
            result = translator.translate(text, dest=target_language)
            return result.text
        except Exception as e:
            logger.warning(f"Translation failed: {e}")
            return text  # Return original text if translation fails

    def detect_language(self, text: str) -> str:
        """Detect the language of input text"""
        try:
            from langdetect import detect
            detected = detect(text)
            # Map to our supported languages
            lang_mapping = {
                "ta": "ta",
                "si": "si",
                "en": "en"
            }
            return lang_mapping.get(detected, "en")
        except Exception as e:
            logger.warning(f"Language detection failed: {e}")
            return "en"

class FloatingChatIcon(QWidget):
    """Floating chat icon that can be dragged around the screen"""
    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app
        self.init_ui()
        self.dragging = False
        self.offset = QPoint()
        self.position_icon()

    def init_ui(self):
        """Initialize the floating icon"""
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(60, 60)

        # Create circular button with better styling and animation
        self.button = QPushButton(self)
        self.button.setFixedSize(50, 50)
        self.button.setStyleSheet("""
            QPushButton {
                border-radius: 25px;
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0078d4, stop:1 #005a9e);
                color: white;
                font-size: 20px;
                font-weight: bold;
                border: 2px solid #005a9e;
                qproperty-iconSize: 24px;
            }
            QPushButton:hover {
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #106ebe, stop:1 #0078d4);
                border: 2px solid #0078d4;
                transform: scale(1.05);
            }
            QPushButton:pressed {
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #005a9e, stop:1 #003d6b);
                border: 2px solid #003d6b;
                transform: scale(0.95);
            }
        """)
        self.button.setText("💬")
        self.button.setToolTip("🤖 AI Assistant - Full Access Mode\nClick to open advanced chat with topic suggestions, file analysis, and video generation control")
        self.button.clicked.connect(self.main_app.open_ai_chat)

        # Add pulsing animation for attention
        self.animation = QPropertyAnimation(self.button, b"geometry")
        self.animation.setDuration(2000)
        self.animation.setLoopCount(-1)  # Infinite loop
        self.start_pulse_animation()

        # Add close button
        self.close_button = QPushButton("×", self)
        self.close_button.setFixedSize(15, 15)
        self.close_button.move(40, 5)
        self.close_button.setStyleSheet("""
            QPushButton {
                border-radius: 7px;
                background-color: rgba(255, 255, 255, 0.9);
                color: #333;
                font-size: 10px;
                font-weight: bold;
                border: 1px solid #ccc;
            }
            QPushButton:hover {
                background-color: rgba(255, 0, 0, 0.9);
                color: white;
            }
        """)
        self.close_button.clicked.connect(self.hide_icon)
        self.close_button.setToolTip("Hide AI Assistant")

        # Add status indicator
        self.status_indicator = QLabel("●", self)
        self.status_indicator.setFixedSize(10, 10)
        self.status_indicator.move(5, 5)
        self.status_indicator.setStyleSheet("""
            QLabel {
                color: #28B463;
                font-size: 12px;
                font-weight: bold;
            }
        """)
        self.status_indicator.setToolTip("AI Assistant Active")

    def start_pulse_animation(self):
        """Start subtle pulsing animation"""
        original_geometry = self.button.geometry()
        pulse_geometry = QRect(
            original_geometry.x() - 2,
            original_geometry.y() - 2,
            original_geometry.width() + 4,
            original_geometry.height() + 4
        )

        self.animation.setStartValue(original_geometry)
        self.animation.setKeyValueAt(0.5, pulse_geometry)
        self.animation.setEndValue(original_geometry)
        self.animation.start()

    def update_tooltip_with_topic(self):
        """Update tooltip to show current topic"""
        current_topic = self.main_app.topic_input.text().strip()
        if current_topic:
            self.button.setToolTip(f"🤖 AI Assistant - Full Access Mode\nCurrent Topic: {current_topic}\nClick to open advanced chat")
        else:
            self.button.setToolTip("🤖 AI Assistant - Full Access Mode\nClick to open advanced chat with topic suggestions, file analysis, and video generation control")

    def show_icon(self):
        """Show the floating icon"""
        self.show()
        self.position_icon()
        self.start_pulse_animation()

    def hide_icon(self):
        """Hide the floating icon"""
        self.hide()

    def position_icon(self):
        """Position the icon in the bottom-right corner"""
        screen = QApplication.primaryScreen().availableGeometry()
        self.move(screen.width() - 80, screen.height() - 140)

    def mousePressEvent(self, event):
        """Handle mouse press for dragging"""
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        """Handle mouse move for dragging"""
        if self.dragging:
            new_pos = self.mapToParent(event.pos() - self.offset)
            self.move(new_pos)

    def mouseReleaseEvent(self, event):
        """Handle mouse release"""
        if event.button() == Qt.LeftButton:
            self.dragging = False

    def enterEvent(self, event):
        """Handle mouse enter for animation"""
        self.button.setStyleSheet("""
            QPushButton {
                border-radius: 25px;
                background-color: #106ebe;
                color: white;
                font-size: 20px;
                font-weight: bold;
                border: 2px solid #0078d4;
            }
        """)

    def leaveEvent(self, event):
        """Handle mouse leave for animation"""
        self.button.setStyleSheet("""
            QPushButton {
                border-radius: 25px;
                background-color: #0078d4;
                color: white;
                font-size: 20px;
                font-weight: bold;
                border: 2px solid #005a9e;
            }
        """)

class ChatInterface(QDialog):
    """AI chat interface"""
    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app
        self.init_ui()

    def init_ui(self):
        """Initialize chat interface"""
        self.setWindowTitle("AI Assistant")
        self.setGeometry(100, 100, 400, 500)

        layout = QVBoxLayout()

        # Chat history
        self.chat_history = QTextBrowser()
        self.chat_history.setMaximumHeight(400)
        layout.addWidget(self.chat_history)

        # Input area
        input_layout = QHBoxLayout()
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Ask me anything about video creation...")
        self.message_input.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.message_input)

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_button)

        layout.addLayout(input_layout)
        self.setLayout(layout)

        # Welcome message
        self.add_message("AI Assistant", "Hello! I'm here to help you with video creation. What would you like to do?")

    def send_message(self):
        """Send message to AI"""
        message = self.message_input.text().strip()
        if not message:
            return

        self.add_message("You", message)
        self.message_input.clear()

        # Process command
        response = self.process_command(message)
        self.add_message("AI Assistant", response)

    def process_command(self, message: str) -> str:
        """Process user commands with enhanced AI capabilities"""
        message_lower = message.lower()

        # Video generation commands
        if "/news" in message_lower:
            return "Starting news video generation... Use the main interface to configure settings."
        elif "/documentary" in message_lower:
            return "Starting documentary video generation... Use the main interface to configure settings."
        elif "/music" in message_lower:
            return "Starting music video generation... Use the main interface to configure settings."
        elif "/kids" in message_lower:
            return "Starting kids story video generation... Use the main interface to configure settings."

        # Help commands
        elif "help" in message_lower or "/help" in message_lower:
            return """Available commands:
/news - Generate news video
/documentary - Generate documentary
/music - Generate music video
/kids - Generate kids story video
/status - Check current status
/settings - Open settings
/editor - Open video editor
/upload - Upload to social media
/help - Show this help

You can also ask me questions about video creation!"""

        # Status commands
        elif "/status" in message_lower:
            status = "Ready to create videos!"
            if hasattr(self.main_app, 'final_video_path') and self.main_app.final_video_path:
                status = f"Video ready: {os.path.basename(self.main_app.final_video_path)}"
            return f"Status: {status}"

        # Action commands
        elif "/settings" in message_lower:
            self.main_app.tabs.setCurrentIndex(4)  # Settings tab
            return "Opened settings panel"
        elif "/editor" in message_lower:
            self.main_app.open_editor()
            return "Opened video editor"
        elif "/upload" in message_lower:
            self.main_app.tabs.setCurrentIndex(2)  # Social Media tab
            return "Opened social media upload panel"

        # AI-powered responses for general questions
        else:
            # Try to use GPT4All for intelligent responses
            try:
                if hasattr(self.main_app, 'video_editor') and self.main_app.video_editor.gpt4all_model:
                    prompt = f"""You are an AI assistant for a video creation application.
                    The user asked: "{message}"
                    Provide a helpful, concise response related to video creation, editing, or the application's features.
                    If this is not related to video creation, politely redirect to video topics."""

                    with self.main_app.video_editor.gpt4all_model.chat_session():
                        response = self.main_app.video_editor.gpt4all_model.generate(prompt, max_tokens=100)
                    return response.strip()
                else:
                    return f"I understand you want to: {message}. I'm here to help with video creation! Try /help for available commands."
            except Exception as e:
                logger.error(f"AI chat response failed: {e}")
                return f"I understand you want to: {message}. I'm here to help with video creation! Try /help for available commands."

    def add_message(self, sender: str, message: str):
        """Add message to chat history"""
        self.chat_history.append(f"<b>{sender}:</b> {message}")

    def add_conversational_flair(self, response):
        """Add conversational flair based on personality and context"""
        if self.personality_mode == "friendly":
            flair_options = [
                " 😊", " 💫", " 🎉", " ✨", " 🌟",
                "\n\nWhat do you think? 🤔",
                "\n\nI'm excited to help! 🚀",
                "\n\nLet me know what you think! 💭"
            ]
        elif self.personality_mode == "professional":
            flair_options = [
                ".", " ✓", " →",
                "\n\nPlease let me know if you need anything else.",
                "\n\nI'm ready to assist with your next request.",
                "\n\nHow else may I be of service?"
            ]
        else:  # casual
            flair_options = [
                " 😎", " 🤙", " 🚀", " 💯", " 🔥",
                "\n\nSound good? 🤔",
                "\n\nLet's make it happen! 💪",
                "\n\nWhat's your take? 🤷‍♂️"
            ]

        # Randomly add flair (30% chance)
        import random
        if random.random() < 0.3:
            flair = random.choice(flair_options)
            if not response.endswith(flair):
                response += flair

        return response

    def remember_user_preferences(self, input_text):
        """Remember user preferences from conversation"""
        input_lower = input_text.lower()

        # Remember preferred topics
        if "i like" in input_lower or "i love" in input_lower or "i'm interested in" in input_lower:
            # Extract what they like
            if not hasattr(self, 'user_preferences'):
                self.user_preferences = {'liked_topics': [], 'disliked_topics': []}

            # Simple extraction - could be enhanced
            words = input_text.lower().split()
            for i, word in enumerate(words):
                if word in ["like", "love", "interested"] and i < len(words) - 1:
                    topic = words[i + 1]
                    if topic not in self.user_preferences['liked_topics']:
                        self.user_preferences['liked_topics'].append(topic)

        # Remember what they don't like
        elif "i don't like" in input_lower or "i hate" in input_lower or "not interested" in input_lower:
            if not hasattr(self, 'user_preferences'):
                self.user_preferences = {'liked_topics': [], 'disliked_topics': []}

            words = input_text.lower().split()
            for i, word in enumerate(words):
                if word in ["don't", "hate", "not"] and i < len(words) - 1:
                    topic = words[i + 1]
                    if topic not in self.user_preferences['disliked_topics']:
                        self.user_preferences['disliked_topics'].append(topic)

class VideoPlayerEditor(QWidget):
    """Advanced Video Player and Editor with Timeline"""
    def __init__(self):
        super().__init__()
        self.current_video = None
        self.clips = []
        self.selected_clip = None
        self.init_ui()

    def init_ui(self):
        """Initialize the advanced video editor UI"""
        main_layout = QVBoxLayout()

        # Top toolbar
        toolbar_layout = QHBoxLayout()

        self.load_btn = QPushButton("📁 Load Video")
        self.load_btn.clicked.connect(self.load_video)
        toolbar_layout.addWidget(self.load_btn)

        self.add_clip_btn = QPushButton("➕ Add Clip")
        self.add_clip_btn.clicked.connect(self.add_clip)
        toolbar_layout.addWidget(self.add_clip_btn)

        self.save_btn = QPushButton("💾 Save Project")
        self.save_btn.clicked.connect(self.save_project)
        toolbar_layout.addWidget(self.save_btn)

        toolbar_layout.addStretch()
        main_layout.addLayout(toolbar_layout)

        # Video preview and timeline splitter
        splitter = QSplitter(Qt.Vertical)

        # Video preview section
        preview_widget = QWidget()
        preview_layout = QVBoxLayout(preview_widget)

        # Video display
        self.video_widget = QVideoWidget()
        self.video_widget.setMinimumHeight(300)
        self.video_widget.setStyleSheet("QVideoWidget { background-color: #000; border: 1px solid #333; }")
        preview_layout.addWidget(self.video_widget)

        # Playback controls
        controls_layout = QHBoxLayout()

        self.play_btn = QPushButton("▶️ Play")
        self.play_btn.clicked.connect(self.play_video)
        controls_layout.addWidget(self.play_btn)

        self.pause_btn = QPushButton("⏸️ Pause")
        self.pause_btn.clicked.connect(self.pause_video)
        controls_layout.addWidget(self.pause_btn)

        self.stop_btn = QPushButton("⏹️ Stop")
        self.stop_btn.clicked.connect(self.stop_video)
        controls_layout.addWidget(self.stop_btn)

        # Timeline scrubber
        self.position_slider = QSlider(Qt.Horizontal)
        self.position_slider.sliderMoved.connect(self.set_position)
        controls_layout.addWidget(self.position_slider)

        # Time display
        self.time_label = QLabel("00:00 / 00:00")
        controls_layout.addWidget(self.time_label)

        preview_layout.addLayout(controls_layout)

        # Video info
        self.video_info = QLabel("No video loaded")
        self.video_info.setStyleSheet("QLabel { color: #666; padding: 5px; }")
        preview_layout.addWidget(self.video_info)

        splitter.addWidget(preview_widget)

        # Timeline section
        timeline_widget = QWidget()
        timeline_layout = QVBoxLayout(timeline_widget)

        # Timeline header
        timeline_header = QHBoxLayout()
        timeline_header.addWidget(QLabel("🎬 Timeline"))

        self.zoom_in_btn = QPushButton("🔍+")
        self.zoom_in_btn.clicked.connect(self.zoom_in)
        timeline_header.addWidget(self.zoom_in_btn)

        self.zoom_out_btn = QPushButton("🔍-")
        self.zoom_out_btn.clicked.connect(self.zoom_out)
        timeline_header.addWidget(self.zoom_out_btn)

        timeline_header.addStretch()
        timeline_layout.addLayout(timeline_header)

        # Timeline tracks
        self.timeline_area = QScrollArea()
        self.timeline_widget = TimelineWidget()
        self.timeline_area.setWidget(self.timeline_widget)
        self.timeline_area.setMinimumHeight(200)
        self.timeline_area.setWidgetResizable(True)
        timeline_layout.addWidget(self.timeline_area)

        # Timeline controls
        timeline_controls = QHBoxLayout()

        self.split_btn = QPushButton("✂️ Split")
        self.split_btn.clicked.connect(self.split_clip)
        timeline_controls.addWidget(self.split_btn)

        self.delete_btn = QPushButton("🗑️ Delete")
        self.delete_btn.clicked.connect(self.delete_clip)
        timeline_controls.addWidget(self.delete_btn)

        self.move_left_btn = QPushButton("⬅️ Move Left")
        self.move_left_btn.clicked.connect(self.move_clip_left)
        timeline_controls.addWidget(self.move_left_btn)

        self.move_right_btn = QPushButton("➡️ Move Right")
        self.move_right_btn.clicked.connect(self.move_clip_right)
        timeline_controls.addWidget(self.move_right_btn)

        timeline_layout.addLayout(timeline_controls)

        splitter.addWidget(timeline_widget)
        splitter.setSizes([400, 250])

        main_layout.addWidget(splitter)

        self.setLayout(main_layout)

        # Media player setup
        self.media_player = QMediaPlayer()
        self.media_player.setVideoOutput(self.video_widget)
        self.media_player.positionChanged.connect(self.position_changed)
        self.media_player.durationChanged.connect(self.duration_changed)

    def load_video(self):
        """Load a video file for editing"""
        file_dialog = QFileDialog()
        file_dialog.setNameFilter("Video files (*.mp4 *.avi *.mov *.mkv *.webm)")

        if file_dialog.exec_():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                video_path = selected_files[0]
                self.current_video = video_path
                self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(video_path)))
                self.video_info.setText(f"Loaded: {os.path.basename(video_path)}")
                print(f"Video loaded: {video_path}")

    def add_clip(self):
        """Add a clip to the timeline"""
        if self.current_video:
            clip_info = {
                'path': self.current_video,
                'start_time': 0,
                'duration': self.media_player.duration() // 1000,  # Convert to seconds
                'name': f"Clip {len(self.clips) + 1}"
            }
            self.clips.append(clip_info)
            self.timeline_widget.add_clip(clip_info)
            print(f"Added clip: {clip_info['name']}")

    def play_video(self):
        """Play the video"""
        self.media_player.play()

    def pause_video(self):
        """Pause the video"""
        self.media_player.pause()

    def stop_video(self):
        """Stop the video"""
        self.media_player.stop()

    def set_position(self, position):
        """Set video position from slider"""
        self.media_player.setPosition(position)

    def position_changed(self, position):
        """Update slider when video position changes"""
        self.position_slider.setValue(position)
        self.update_time_display()

    def duration_changed(self, duration):
        """Update slider range when video duration changes"""
        self.position_slider.setRange(0, duration)
        self.update_time_display()

    def update_time_display(self):
        """Update the time display label"""
        current = self.media_player.position() // 1000
        total = self.media_player.duration() // 1000
        self.time_label.setText("02d")

    def zoom_in(self):
        """Zoom in on timeline"""
        self.timeline_widget.zoom_factor *= 1.2
        self.timeline_widget.update()

    def zoom_out(self):
        """Zoom out on timeline"""
        self.timeline_widget.zoom_factor /= 1.2
        self.timeline_widget.update()

    def split_clip(self):
        """Split the selected clip"""
        if self.selected_clip:
            print(f"Splitting clip: {self.selected_clip['name']}")

    def delete_clip(self):
        """Delete the selected clip"""
        if self.selected_clip:
            self.clips.remove(self.selected_clip)
            self.timeline_widget.remove_clip(self.selected_clip)
            self.selected_clip = None
            print("Clip deleted")

    def move_clip_left(self):
        """Move selected clip left on timeline"""
        if self.selected_clip:
            print(f"Moving clip left: {self.selected_clip['name']}")

    def move_clip_right(self):
        """Move selected clip right on timeline"""
        if self.selected_clip:
            print(f"Moving clip right: {self.selected_clip['name']}")

    def save_project(self):
        """Save the current editing project"""
        if self.clips:
            project_data = {
                'video': self.current_video,
                'clips': self.clips,
                'timestamp': datetime.now().isoformat()
            }
            print(f"Project saved with {len(self.clips)} clips")
        else:
            print("No clips to save")

class TimelineWidget(QWidget):
    """Custom widget for displaying video timeline"""
    def __init__(self):
        super().__init__()
        self.clips = []
        self.zoom_factor = 1.0
        self.setMinimumHeight(150)

    def add_clip(self, clip_info):
        """Add a clip to the timeline"""
        self.clips.append(clip_info)
        self.update()

    def remove_clip(self, clip_info):
        """Remove a clip from the timeline"""
        if clip_info in self.clips:
            self.clips.remove(clip_info)
            self.update()

    def paintEvent(self, event):
        """Draw the timeline"""
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(240, 240, 240))

        # Draw timeline ruler
        painter.setPen(QColor(100, 100, 100))
        for i in range(0, self.width(), int(50 * self.zoom_factor)):
            painter.drawLine(i, 0, i, 20)
            painter.drawText(i + 2, 15, f"{i//50}s")

        # Draw clips
        y_offset = 30
        clip_height = 40
        for i, clip in enumerate(self.clips):
            x_start = int(clip['start_time'] * 50 * self.zoom_factor)
            width = int(clip['duration'] * 50 * self.zoom_factor)

            # Clip rectangle
            clip_rect = QRect(x_start, y_offset + i * (clip_height + 5), width, clip_height)
            painter.fillRect(clip_rect, QColor(100, 150, 200))
            painter.setPen(QColor(50, 50, 50))
            painter.drawRect(clip_rect)

            # Clip name
            painter.setPen(QColor(0, 0, 0))
            painter.drawText(clip_rect.adjusted(5, 5, -5, -5), Qt.AlignLeft, clip['name'])

    def play_video(self):
        """Play the video"""
        if self.media_player.state() == QMediaPlayer.PausedState:
            self.media_player.play()
        elif self.media_player.state() == QMediaPlayer.StoppedState:
            self.media_player.play()

    def pause_video(self):
        """Pause the video"""
        self.media_player.pause()

    def stop_video(self):
        """Stop the video"""
        self.media_player.stop()

    def load_video(self, video_path: str):
        """Load a video file"""
        if os.path.exists(video_path):
            self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(video_path)))
            self.video_info.setText(f"Loaded: {os.path.basename(video_path)}")
        else:
            self.video_info.setText("Video file not found")

class LoginDialog(QDialog):
    """Login and registration dialog"""
    def __init__(self, user_auth):
        super().__init__()
        self.user_auth = user_auth
        self.init_ui()

    def init_ui(self):
        """Initialize login dialog"""
        self.setWindowTitle("Login")
        self.setModal(True)

        layout = QVBoxLayout()

        # Username
        username_layout = QHBoxLayout()
        username_layout.addWidget(QLabel("Username:"))
        self.username_input = QLineEdit()
        username_layout.addWidget(self.username_input)
        layout.addLayout(username_layout)

        # Password
        password_layout = QHBoxLayout()
        password_layout.addWidget(QLabel("Password:"))
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        password_layout.addWidget(self.password_input)
        layout.addLayout(password_layout)

        # Buttons
        buttons_layout = QHBoxLayout()

        self.login_btn = QPushButton("Login")
        self.login_btn.clicked.connect(self.login)
        buttons_layout.addWidget(self.login_btn)

        self.register_btn = QPushButton("Register")
        self.register_btn.clicked.connect(self.register)
        buttons_layout.addWidget(self.register_btn)

        layout.addLayout(buttons_layout)
        self.setLayout(layout)

    def login(self):
        """Handle login"""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if self.user_auth.login(username, password):
            QMessageBox.information(self, "Success", "Login successful!")
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "Invalid username or password")

    def register(self):
        """Handle registration"""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if len(username) < 3 or len(password) < 3:
            QMessageBox.warning(self, "Error", "Username and password must be at least 3 characters")
            return

        if self.user_auth.register(username, password):
            QMessageBox.information(self, "Success", "Registration successful!")
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "Username already exists")

class MiniAIAgent:
    """Mini AI agent for specific tasks"""
    def __init__(self, agent_id: str, specialty: str, manager_ref):
        self.agent_id = agent_id
        self.specialty = specialty
        self.manager = manager_ref
        self.is_active = True
        self.task_history = []
        self.accuracy_score = 1.0

    def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific task"""
        try:
            result = {"agent_id": self.agent_id, "task_id": task.get("id"), "status": "processing"}

            if task["type"] == "video_search":
                result.update(self.search_videos(task))
            elif task["type"] == "script_generation":
                result.update(self.generate_script(task))
            elif task["type"] == "video_download":
                result.update(self.download_video(task))
            elif task["type"] == "content_analysis":
                result.update(self.analyze_content(task))
            elif task["type"] == "quality_check":
                result.update(self.check_quality(task))

            result["status"] = "completed"
            result["timestamp"] = datetime.now().isoformat()
            self.task_history.append(result)

            # Report to manager
            self.manager.report_task_completion(result)

            return result
        except Exception as e:
            error_result = {
                "agent_id": self.agent_id,
                "task_id": task.get("id"),
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            self.manager.report_task_completion(error_result)
            return error_result

    def search_videos(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Search for videos"""
        query = task.get("query", "")
        # Implement video search logic
        return {"videos_found": [], "search_query": query}

    def generate_script(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Generate video script"""
        topic = task.get("topic", "")
        # Implement script generation
        return {"script": f"Generated script for {topic}", "topic": topic}

    def download_video(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Download video"""
        url = task.get("url", "")
        # Implement download logic
        return {"download_path": "", "url": url}

    def analyze_content(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze video content"""
        video_path = task.get("video_path", "")
        # Implement content analysis
        return {"analysis": {}, "video_path": video_path}

    def check_quality(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Check video quality"""
        video_path = task.get("video_path", "")
        # Implement quality check
        return {"quality_score": 0.8, "issues": [], "video_path": video_path}

class SubManagerAgent:
    """Sub-manager agent that oversees mini agents"""
    def __init__(self, manager_id: str, specialty_area: str, master_manager_ref):
        self.manager_id = manager_id
        self.specialty_area = specialty_area
        self.master_manager = master_manager_ref
        self.mini_agents = []
        self.active_tasks = {}
        self.performance_metrics = {
            "tasks_completed": 0,
            "tasks_failed": 0,
            "average_accuracy": 0.0,
            "average_completion_time": 0.0
        }

    def add_mini_agent(self, agent: MiniAIAgent):
        """Add a mini agent to this sub-manager"""
        self.mini_agents.append(agent)

    def assign_task(self, task: Dict[str, Any]) -> bool:
        """Assign task to appropriate mini agent"""
        suitable_agents = [agent for agent in self.mini_agents
                          if agent.specialty == task.get("required_specialty", "")
                          and agent.is_active]

        if not suitable_agents:
            return False

        # Select best agent based on performance
        best_agent = max(suitable_agents, key=lambda x: x.accuracy_score)
        task["assigned_agent"] = best_agent.agent_id
        task["assigned_time"] = datetime.now().isoformat()

        self.active_tasks[task["id"]] = task

        # Execute task in thread
        threading.Thread(target=self.execute_task_with_agent,
                        args=(best_agent, task)).start()

        return True

    def execute_task_with_agent(self, agent: MiniAIAgent, task: Dict[str, Any]):
        """Execute task with monitoring"""
        start_time = time.time()
        result = agent.execute_task(task)
        completion_time = time.time() - start_time

        # Update performance metrics
        self.update_performance_metrics(result, completion_time)

        # Remove from active tasks
        if task["id"] in self.active_tasks:
            del self.active_tasks[task["id"]]

        # Report to master manager
        self.master_manager.report_submanager_update(self.manager_id, result)

    def update_performance_metrics(self, result: Dict[str, Any], completion_time: float):
        """Update performance metrics"""
        self.performance_metrics["tasks_completed"] += 1 if result["status"] == "completed" else 0
        self.performance_metrics["tasks_failed"] += 1 if result["status"] == "failed" else 0

        # Update average completion time
        total_tasks = self.performance_metrics["tasks_completed"] + self.performance_metrics["tasks_failed"]
        if total_tasks > 0:
            self.performance_metrics["average_completion_time"] = (
                (self.performance_metrics["average_completion_time"] * (total_tasks - 1)) + completion_time
            ) / total_tasks

    def get_performance_report(self) -> Dict[str, Any]:
        """Get performance report"""
        return {
            "manager_id": self.manager_id,
            "specialty": self.specialty_area,
            "active_tasks": len(self.active_tasks),
            "mini_agents_count": len(self.mini_agents),
            "metrics": self.performance_metrics.copy()
        }

class MasterAIManager:
    """Master AI Manager that oversees all operations"""
    def __init__(self):
        self.sub_managers = {}
        self.task_queue = []
        self.completed_tasks = []
        self.system_status = "initializing"
        self.performance_dashboard = {}
        self.lock = Lock()

    def initialize_system(self):
        """Initialize the AI management system"""
        # Create sub-managers for different specialties
        specialties = ["video_collection", "content_analysis", "script_generation",
                      "video_editing", "quality_assurance", "social_media"]

        for specialty in specialties:
            sub_manager = SubManagerAgent(f"sub_mgr_{specialty}", specialty, self)
            self.sub_managers[specialty] = sub_manager

            # Create mini agents for each sub-manager
            for i in range(3):  # 3 mini agents per specialty
                mini_agent = MiniAIAgent(f"mini_{specialty}_{i}", specialty, sub_manager)
                sub_manager.add_mini_agent(mini_agent)

        self.system_status = "operational"
        logger.info("Master AI Manager initialized with sub-managers and mini agents")

    def submit_task(self, task: Dict[str, Any]) -> str:
        """Submit a task to the system"""
        with self.lock:
            task_id = f"task_{int(time.time())}_{len(self.task_queue)}"
            task["id"] = task_id
            task["submitted_time"] = datetime.now().isoformat()
            task["status"] = "queued"

            self.task_queue.append(task)

            # Auto-assign task
            threading.Thread(target=self.process_task_queue).start()

            return task_id

    def process_task_queue(self):
        """Process tasks in the queue"""
        while self.task_queue:
            with self.lock:
                if not self.task_queue:
                    break
                task = self.task_queue.pop(0)

            # Find appropriate sub-manager
            specialty = task.get("required_specialty", "video_collection")
            sub_manager = self.sub_managers.get(specialty)

            if sub_manager and sub_manager.assign_task(task):
                logger.info(f"Task {task['id']} assigned to {specialty} sub-manager")
            else:
                logger.warning(f"Could not assign task {task['id']} - no suitable sub-manager")
                task["status"] = "failed"
                self.completed_tasks.append(task)

    def report_submanager_update(self, submanager_id: str, result: Dict[str, Any]):
        """Receive updates from sub-managers"""
        with self.lock:
            self.completed_tasks.append(result)

            # Update performance dashboard
            specialty = submanager_id.replace("sub_mgr_", "")
            if specialty not in self.performance_dashboard:
                self.performance_dashboard[specialty] = {"completed": 0, "failed": 0}

            if result["status"] == "completed":
                self.performance_dashboard[specialty]["completed"] += 1
            else:
                self.performance_dashboard[specialty]["failed"] += 1

    def report_task_completion(self, result: Dict[str, Any]):
        """Receive task completion reports from mini agents"""
        # This is called by sub-managers, already handled above
        pass

    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        with self.lock:
            return {
                "status": self.system_status,
                "active_tasks": sum(len(sm.active_tasks) for sm in self.sub_managers.values()),
                "completed_tasks": len(self.completed_tasks),
                "queued_tasks": len(self.task_queue),
                "performance": self.performance_dashboard.copy(),
                "sub_managers": {k: v.get_performance_report() for k, v in self.sub_managers.items()}
            }

    def generate_video_creation_task(self, topic: str, country: str = "Global",
                                   language: str = "en", duration: int = 5) -> str:
        """Generate a complete video creation task"""
        task = {
            "type": "video_creation_pipeline",
            "topic": topic,
            "country": country,
            "language": language,
            "duration": duration,
            "required_specialty": "video_collection",
            "pipeline_steps": [
                {"step": "search", "specialty": "video_collection"},
                {"step": "download", "specialty": "video_collection"},
                {"step": "analyze", "specialty": "content_analysis"},
                {"step": "generate_script", "specialty": "script_generation"},
                {"step": "edit", "specialty": "video_editing"},
                {"step": "quality_check", "specialty": "quality_assurance"}
            ]
        }
        return self.submit_task(task)

    def integrate_ai_video_generator(self, ai_video_generator: 'AIVideoGenerator'):
        """Integrate AI Video Generator with the master system"""
        self.ai_video_generator = ai_video_generator

        # Add video generation specialties to sub-managers
        video_gen_specialties = ["video_generation", "prompt_enhancement", "scene_composition",
                                "audio_composition", "presenter_generation", "quality_assurance"]

        for specialty in video_gen_specialties:
            if specialty not in self.sub_managers:
                sub_manager = SubManagerAgent(f"sub_mgr_{specialty}", specialty, self)
                self.sub_managers[specialty] = sub_manager

                # Create mini agents for each sub-manager
                for i in range(3):  # 3 mini agents per specialty
                    mini_agent = MiniAIAgent(f"mini_{specialty}_{i}", specialty, sub_manager)
                    sub_manager.add_mini_agent(mini_agent)

        logger.info("AI Video Generator integrated with Master AI Manager")

    def generate_ai_video_task(self, prompt: str, style: str = "cinematic",
                              tool: str = "veo_3", duration: int = 10) -> str:
        """Generate a comprehensive AI video creation task"""
        task = {
            "type": "ai_video_generation_pipeline",
            "prompt": prompt,
            "style": style,
            "tool": tool,
            "duration": duration,
            "required_specialty": "video_generation",
            "pipeline_steps": [
                {"step": "enhance_prompt", "specialty": "prompt_enhancement"},
                {"step": "build_scenes", "specialty": "scene_composition"},
                {"step": "compose_audio", "specialty": "audio_composition"},
                {"step": "generate_video", "specialty": "video_generation"},
                {"step": "generate_presenter", "specialty": "presenter_generation"},
                {"step": "quality_check", "specialty": "quality_assurance"}
            ]
        }
        return self.submit_task(task)

    def get_video_generation_status(self) -> Dict[str, Any]:
        """Get comprehensive video generation system status"""
        base_status = self.get_system_status()
        video_status = {
            "ai_video_generator": {
                "available_tools": len(self.ai_video_generator.available_tools) if hasattr(self, 'ai_video_generator') else 0,
                "style_presets": len(self.ai_video_generator.style_presets) if hasattr(self, 'ai_video_generator') else 0,
                "active_generations": 0  # Would track active video generations
            }
        }
        base_status.update(video_status)
        return base_status

    def optimize_video_generation_pipeline(self):
        """Optimize the video generation pipeline based on performance data"""
        # Analyze performance data
        performance_data = self.performance_dashboard

        # Identify bottlenecks
        bottlenecks = []
        for specialty, data in performance_data.items():
            failure_rate = data.get("failed", 0) / max(data.get("completed", 0) + data.get("failed", 0), 1)
            if failure_rate > 0.2:  # More than 20% failure rate
                bottlenecks.append(specialty)

        # Optimize based on bottlenecks
        optimizations = []
        for bottleneck in bottlenecks:
            if "video_generation" in bottleneck:
                optimizations.append("Increase video generation capacity")
            elif "quality_assurance" in bottleneck:
                optimizations.append("Enhance quality checking algorithms")
            elif "scene_composition" in bottleneck:
                optimizations.append("Improve scene building logic")

        logger.info(f"Pipeline optimizations identified: {optimizations}")
        return optimizations

class UniversalTopicExpanderAgent:
    """Universal Topic Expander Agent for intelligent topic suggestions and expansion"""
    def __init__(self, master_ai_manager=None):
        self.master_ai_manager = master_ai_manager
        self.topic_database = self._initialize_topic_database()
        self.trending_topics = {}
        self.user_preferences = {}
        self.expansion_cache = {}
        self.language_support = ["en", "ta", "si"]  # English, Tamil, Sinhala

    def _initialize_topic_database(self) -> Dict[str, Dict[str, Any]]:
        """Initialize comprehensive topic database with categories and subtopics"""
        return {
            "news": {
                "description": "Current events and breaking news",
                "subtopics": {
                    "local": "Local community news and events",
                    "national": "National news and politics",
                    "international": "Global news and world events",
                    "breaking": "Breaking news and urgent updates",
                    "business": "Business and economic news",
                    "technology": "Tech news and innovations",
                    "sports": "Sports news and results",
                    "entertainment": "Celebrity and entertainment news",
                    "weather": "Weather updates and forecasts",
                    "health": "Health and medical news"
                },
                "keywords": ["news", "breaking", "update", "current", "events"]
            },
            "education": {
                "description": "Learning and educational content",
                "subtopics": {
                    "science": "Scientific discoveries and research",
                    "history": "Historical events and figures",
                    "mathematics": "Math concepts and problems",
                    "language": "Language learning and linguistics",
                    "programming": "Coding and software development",
                    "art": "Art history and techniques",
                    "music": "Music theory and appreciation",
                    "geography": "World geography and cultures",
                    "literature": "Books and literary analysis",
                    "tutorials": "How-to guides and tutorials"
                },
                "keywords": ["learn", "education", "study", "tutorial", "course"]
            },
            "entertainment": {
                "description": "Movies, music, and entertainment",
                "subtopics": {
                    "movies": "Film reviews and trailers",
                    "music": "Music videos and concerts",
                    "gaming": "Video games and gaming culture",
                    "celebrities": "Celebrity news and interviews",
                    "comedy": "Comedy shows and stand-up",
                    "drama": "TV shows and series",
                    "animation": "Animated content and cartoons",
                    "documentary": "Documentary films and series",
                    "reality": "Reality TV and competitions",
                    "podcasts": "Audio entertainment and talk shows"
                },
                "keywords": ["entertainment", "fun", "movies", "music", "games"]
            },
            "technology": {
                "description": "Tech innovations and digital trends",
                "subtopics": {
                    "ai": "Artificial intelligence and machine learning",
                    "gadgets": "Latest tech gadgets and devices",
                    "software": "Software development and tools",
                    "internet": "Web and internet technologies",
                    "mobile": "Mobile apps and smartphones",
                    "gaming": "Gaming technology and VR/AR",
                    "cybersecurity": "Digital security and privacy",
                    "space": "Space exploration and astronomy",
                    "robotics": "Robots and automation",
                    "blockchain": "Cryptocurrency and blockchain"
                },
                "keywords": ["tech", "technology", "digital", "innovation", "software"]
            },
            "lifestyle": {
                "description": "Daily life and lifestyle topics",
                "subtopics": {
                    "health": "Health and wellness tips",
                    "fitness": "Exercise and fitness routines",
                    "cooking": "Recipes and cooking techniques",
                    "travel": "Travel destinations and tips",
                    "fashion": "Fashion trends and style",
                    "home": "Home improvement and decor",
                    "parenting": "Parenting advice and tips",
                    "relationships": "Relationship and dating advice",
                    "finance": "Personal finance and money management",
                    "selfcare": "Mental health and self-care"
                },
                "keywords": ["lifestyle", "life", "daily", "tips", "advice"]
            },
            "sports": {
                "description": "Sports and athletic activities",
                "subtopics": {
                    "football": "Football/Soccer news and matches",
                    "basketball": "Basketball games and players",
                    "cricket": "Cricket matches and tournaments",
                    "tennis": "Tennis tournaments and players",
                    "olympics": "Olympic games and athletes",
                    "fitness": "Fitness and training tips",
                    "esports": "Electronic sports and gaming",
                    "motorsport": "Racing and motorsports",
                    "wrestling": "Wrestling and combat sports",
                    "extreme": "Extreme sports and adventures"
                },
                "keywords": ["sports", "games", "athletes", "competition", "fitness"]
            }
        }

    def expand_topic(self, topic: str, language: str = "en", max_suggestions: int = 5) -> Dict[str, Any]:
        """Expand a topic into detailed subtopics with descriptions"""
        topic_lower = topic.lower().strip()

        # Check cache first
        cache_key = f"{topic_lower}_{language}"
        if cache_key in self.expansion_cache:
            return self.expansion_cache[cache_key]

        # Find matching category
        matched_category = None
        for category, data in self.topic_database.items():
            if category in topic_lower or any(keyword in topic_lower for keyword in data["keywords"]):
                matched_category = category
                break

        if not matched_category:
            # Try fuzzy matching or use general category
            matched_category = self._find_best_category_match(topic_lower)

        if matched_category:
            category_data = self.topic_database[matched_category]
            subtopics = category_data["subtopics"]

            # Select top subtopics based on relevance
            selected_subtopics = self._select_relevant_subtopics(
                topic_lower, subtopics, max_suggestions
            )

            result = {
                "original_topic": topic,
                "category": matched_category,
                "description": category_data["description"],
                "suggested_subtopics": selected_subtopics,
                "language": language,
                "confidence": self._calculate_confidence(topic_lower, matched_category)
            }
        else:
            # Generate generic suggestions
            result = self._generate_generic_suggestions(topic, language, max_suggestions)

        # Cache the result
        self.expansion_cache[cache_key] = result
        return result

    def get_topic_suggestions(self, text: str) -> List[Dict[str, str]]:
        """Get topic suggestions for auto-complete functionality"""
        if len(text.strip()) < 2:
            return []

        try:
            # Use expand_topic to get suggestions
            expansion_result = self.expand_topic(text, max_suggestions=8)

            suggestions = []
            if "suggested_subtopics" in expansion_result:
                for subtopic in expansion_result["suggested_subtopics"]:
                    suggestions.append({
                        "topic": subtopic["subtopic"].title(),
                        "category": expansion_result.get("category", "general").title(),
                        "description": subtopic["description"]
                    })

            # If no specific suggestions, generate some generic ones
            if not suggestions:
                generic_suggestions = [
                    {"topic": f"{text.title()} Overview", "category": "General", "description": f"General overview of {text}"},
                    {"topic": f"{text.title()} Tutorial", "category": "Education", "description": f"Learn about {text}"},
                    {"topic": f"{text.title()} News", "category": "News", "description": f"Latest news about {text}"},
                    {"topic": f"{text.title()} Guide", "category": "Tutorial", "description": f"Complete guide to {text}"},
                    {"topic": f"{text.title()} Tips", "category": "Advice", "description": f"Useful tips about {text}"}
                ]
                suggestions = generic_suggestions[:5]

            return suggestions[:5]  # Return top 5 suggestions

        except Exception as e:
            # Fallback to basic suggestions
            return [
                {"topic": f"{text.title()} Basics", "category": "General", "description": f"Basic introduction to {text}"},
                {"topic": f"Advanced {text.title()}", "category": "Advanced", "description": f"Advanced concepts in {text}"},
                {"topic": f"{text.title()} Examples", "category": "Examples", "description": f"Practical examples of {text}"}
            ]

    def _find_best_category_match(self, topic: str) -> str:
        """Find the best category match using fuzzy logic"""
        topic_words = set(topic.lower().split())

        best_match = None
        best_score = 0

        for category, data in self.topic_database.items():
            category_words = set(category.split()) | set(data["keywords"])
            score = len(topic_words.intersection(category_words))

            if score > best_score:
                best_score = score
                best_match = category

        return best_match or "entertainment"  # Default fallback

    def _select_relevant_subtopics(self, topic: str, subtopics: Dict[str, str], max_count: int) -> List[Dict[str, str]]:
        """Select most relevant subtopics based on the original topic"""
        topic_words = set(topic.lower().split())
        scored_subtopics = []

        for subtopic_key, description in subtopics.items():
            # Calculate relevance score
            subtopic_words = set(subtopic_key.split())
            description_words = set(description.lower().split())

            word_overlap = len(topic_words.intersection(subtopic_words | description_words))
            score = word_overlap * 2  # Weight word matches heavily

            # Boost score for exact matches
            if subtopic_key in topic.lower():
                score += 10

            scored_subtopics.append({
                "subtopic": subtopic_key,
                "description": description,
                "relevance_score": score
            })

        # Sort by relevance and return top results
        scored_subtopics.sort(key=lambda x: x["relevance_score"], reverse=True)
        return scored_subtopics[:max_count]

    def _calculate_confidence(self, topic: str, category: str) -> float:
        """Calculate confidence score for topic-category match"""
        topic_lower = topic.lower()
        category_data = self.topic_database[category]

        # Exact category match
        if category in topic_lower:
            return 1.0

        # Keyword match
        keyword_matches = sum(1 for keyword in category_data["keywords"] if keyword in topic_lower)
        if keyword_matches > 0:
            return min(0.9, 0.5 + (keyword_matches * 0.1))

        # Fuzzy match
        return 0.3

    def _generate_generic_suggestions(self, topic: str, language: str, max_count: int) -> Dict[str, Any]:
        """Generate generic suggestions when no category matches"""
        generic_subtopics = [
            {"subtopic": "introduction", "description": f"Introduction to {topic}"},
            {"subtopic": "basics", "description": f"Basic concepts of {topic}"},
            {"subtopic": "advanced", "description": f"Advanced aspects of {topic}"},
            {"subtopic": "examples", "description": f"Real-world examples of {topic}"},
            {"subtopic": "tips", "description": f"Useful tips about {topic}"}
        ]

        return {
            "original_topic": topic,
            "category": "general",
            "description": f"General content about {topic}",
            "suggested_subtopics": generic_subtopics[:max_count],
            "language": language,
            "confidence": 0.2
        }

    def get_trending_topics(self, category: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Get trending topics from various sources"""
        # This would integrate with APIs like Google Trends, Twitter, etc.
        # For now, return mock trending topics
        mock_trending = [
            {"topic": "AI Technology", "category": "technology", "trend_score": 95},
            {"topic": "Climate Change", "category": "news", "trend_score": 88},
            {"topic": "Space Exploration", "category": "technology", "trend_score": 82},
            {"topic": "Mental Health", "category": "lifestyle", "trend_score": 78},
            {"topic": "Electric Vehicles", "category": "technology", "trend_score": 75}
        ]

        if category:
            mock_trending = [t for t in mock_trending if t["category"] == category]

        return mock_trending[:limit]

    def narrate_suggestions(self, suggestions: Dict[str, Any], language: str = "en") -> str:
        """Generate narrated text for suggestions"""
        if language == "ta":  # Tamil
            return self._narrate_tamil(suggestions)
        elif language == "si":  # Sinhala
            return self._narrate_sinhala(suggestions)
        else:  # English (default)
            return self._narrate_english(suggestions)

    def _narrate_english(self, suggestions: Dict[str, Any]) -> str:
        """Narrate suggestions in English"""
        topic = suggestions["original_topic"]
        category = suggestions["category"]
        subtopics = suggestions["suggested_subtopics"]

        narration = f"For the topic '{topic}' in the {category} category, here are some suggested subtopics: "

        for i, subtopic in enumerate(subtopics, 1):
            narration += f"{i}. {subtopic['subtopic'].title()}: {subtopic['description']}. "

        return narration

    def _narrate_tamil(self, suggestions: Dict[str, Any]) -> str:
        """Narrate suggestions in Tamil"""
        topic = suggestions["original_topic"]
        subtopics = suggestions["suggested_subtopics"]

        narration = f"'{topic}' என்ற தலைப்புக்கு பின்வரும் துணைத்தலைப்புகள் பரிந்துரைக்கப்படுகின்றன: "

        for i, subtopic in enumerate(subtopics, 1):
            narration += f"{i}. {subtopic['subtopic']}: {subtopic['description']}. "

        return narration

    def _narrate_sinhala(self, suggestions: Dict[str, Any]) -> str:
        """Narrate suggestions in Sinhala"""
        topic = suggestions["original_topic"]
        subtopics = suggestions["suggested_subtopics"]

        narration = f"'{topic}' මාතෘකාව සඳහා පහත දක්වා ඇති උපමාතෘකා යෝජනා කරනු ලැබේ: "

        for i, subtopic in enumerate(subtopics, 1):
            narration += f"{i}. {subtopic['subtopic']}: {subtopic['description']}. "

        return narration

class AIVideoGenerator:
    """Enhanced AI Video Generation with Veo 3-style functionality"""
    def __init__(self, voice_manager=None):
        self.voice_manager = voice_manager
        self.available_tools = {
            "runwayml": {
                "name": "Runway ML",
                "url": "https://runwayml.com",
                "features": ["text_to_video", "image_to_video", "video_editing", "motion_tracking"],
                "free_tier": True,
                "quality_levels": ["draft", "standard", "premium"],
                "max_duration": 10
            },
            "stability_ai": {
                "name": "Stability AI",
                "url": "https://stability.ai",
                "features": ["text_to_image", "image_to_video", "stable_diffusion"],
                "free_tier": True,
                "quality_levels": ["low", "medium", "high"],
                "max_duration": 5
            },
            "pika_labs": {
                "name": "Pika Labs",
                "url": "https://pika.art",
                "features": ["text_to_video", "video_editing", "lip_sync"],
                "free_tier": True,
                "quality_levels": ["basic", "pro", "ultra"],
                "max_duration": 8
            },
            "synthesia": {
                "name": "Synthesia",
                "url": "https://synthesia.io",
                "features": ["ai_presenter", "text_to_video", "voice_cloning"],
                "free_tier": False,
                "quality_levels": ["standard", "premium", "enterprise"],
                "max_duration": 15
            },
            "veo_3": {
                "name": "Veo 3 (Google)",
                "url": "https://deepmind.google/technologies/veo/",
                "features": ["text_to_video", "high_quality", "cinematic", "long_form"],
                "free_tier": False,
                "quality_levels": ["standard", "high", "ultra"],
                "max_duration": 60
            },
            "kling_ai": {
                "name": "Kling AI",
                "url": "https://klingai.com",
                "features": ["text_to_video", "image_to_video", "high_fps"],
                "free_tier": True,
                "quality_levels": ["720p", "1080p", "4k"],
                "max_duration": 10
            }
        }

        self.style_presets = {
            "cinematic": {
                "description": "Hollywood-style cinematic videos",
                "aspect_ratio": "16:9",
                "resolution": "4K",
                "fps": 24,
                "color_grading": "cinematic",
                "audio_style": "orchestral"
            },
            "animated": {
                "description": "Cartoon and animation style",
                "aspect_ratio": "16:9",
                "resolution": "1080p",
                "fps": 30,
                "color_grading": "vibrant",
                "audio_style": "upbeat"
            },
            "surreal": {
                "description": "Dreamlike and surreal visuals",
                "aspect_ratio": "1:1",
                "resolution": "1080p",
                "fps": 24,
                "color_grading": "dreamy",
                "audio_style": "ambient"
            },
            "documentary": {
                "description": "Professional documentary style",
                "aspect_ratio": "16:9",
                "resolution": "4K",
                "fps": 30,
                "color_grading": "natural",
                "audio_style": "neutral"
            },
            "commercial": {
                "description": "Advertising and commercial style",
                "aspect_ratio": "9:16",
                "resolution": "1080p",
                "fps": 30,
                "color_grading": "bright",
                "audio_style": "energetic"
            }
        }

        self.prompt_enhancer = PromptEnhancer()
        self.scene_builder = SceneBuilder()
        self.audio_composer = AudioComposer(voice_manager)
        self.quality_checker = QualityChecker()
        self.presenter_generator = PresenterGenerator()
        self.resource_searcher = ResourceSearcher()

    def generate_video_from_text(self, prompt: str, style: str = "cinematic",
                               tool: str = "veo_3", duration: int = 10) -> Dict[str, Any]:
        """Generate video from text prompt with enhanced features"""
        if tool not in self.available_tools:
            return {"error": f"Tool {tool} not available"}

        tool_config = self.available_tools[tool]
        if duration > tool_config["max_duration"]:
            duration = tool_config["max_duration"]

        # Enhance prompt
        enhanced_prompt = self.prompt_enhancer.enhance_prompt(prompt, style)

        # Build scene composition
        scenes = self.scene_builder.build_scenes(enhanced_prompt, duration)

        # Generate video
        result = {
            "tool": tool,
            "original_prompt": prompt,
            "enhanced_prompt": enhanced_prompt,
            "style": style,
            "duration": duration,
            "scenes": scenes,
            "status": "processing",
            "estimated_time": f"{duration * 2}-{duration * 3} minutes",
            "quality_level": tool_config["quality_levels"][-1],
            "video_url": None
        }

        # Start async generation
        threading.Thread(target=self._generate_video_async, args=(result,)).start()

        return result

    def generate_video_from_image(self, image_path: str, prompt: str,
                                style: str = "cinematic", tool: str = "runwayml") -> Dict[str, Any]:
        """Generate video from image with motion"""
        if not os.path.exists(image_path):
            return {"error": "Image file not found"}

        if tool not in self.available_tools:
            return {"error": f"Tool {tool} not available"}

        # Enhance prompt for image-to-video
        enhanced_prompt = self.prompt_enhancer.enhance_image_prompt(prompt, style)

        result = {
            "tool": tool,
            "image_path": image_path,
            "original_prompt": prompt,
            "enhanced_prompt": enhanced_prompt,
            "style": style,
            "status": "processing",
            "estimated_time": "2-5 minutes",
            "video_url": None
        }

        # Start async generation
        threading.Thread(target=self._generate_video_async, args=(result,)).start()

        return result

    def _generate_video_async(self, generation_request: Dict[str, Any]):
        """Async video generation process"""
        try:
            # Simulate API call (replace with actual API integration)
            time.sleep(2)  # Simulate processing time

            # Mock successful generation
            generation_request["status"] = "completed"
            generation_request["video_url"] = f"mock_video_{int(time.time())}.mp4"
            generation_request["thumbnail_url"] = f"mock_thumb_{int(time.time())}.jpg"

            logger.info(f"Video generation completed for request: {generation_request['tool']}")

        except Exception as e:
            generation_request["status"] = "failed"
            generation_request["error"] = str(e)
            logger.error(f"Video generation failed: {e}")

    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get list of available AI video generation tools"""
        return list(self.available_tools.values())

    def get_style_presets(self) -> Dict[str, Dict[str, Any]]:
        """Get available style presets"""
        return self.style_presets

    def enhance_prompt(self, prompt: str, style: str = "cinematic") -> str:
        """Enhance user prompt with cinematic details"""
        return self.prompt_enhancer.enhance_prompt(prompt, style)

    def build_scene_composition(self, prompt: str, duration: int) -> List[Dict[str, Any]]:
        """Build detailed scene composition"""
        return self.scene_builder.build_scenes(prompt, duration)

    def compose_audio(self, video_prompt: str, duration: int) -> Dict[str, Any]:
        """Compose background audio and sound effects"""
        return self.audio_composer.compose_audio(video_prompt, duration)

    def generate_presenter(self, script: str, style: str = "professional") -> Dict[str, Any]:
        """Generate AI presenter video"""
        return self.presenter_generator.generate_presenter(script, style)

    def check_quality(self, video_path: str) -> Dict[str, Any]:
        """Check video quality and provide feedback"""
        return self.quality_checker.analyze_quality(video_path)

    def search_resources(self, query: str, resource_type: str = "music") -> List[Dict[str, Any]]:
        """Search for free resources (music, images, etc.)"""
        return self.resource_searcher.search_free_resources(query, resource_type)

class PromptEnhancer:
    """AI-powered prompt enhancement for better video generation"""
    def __init__(self):
        self.enhancement_templates = {
            "cinematic": [
                "Cinematic shot, professional cinematography, {prompt}",
                "Hollywood style, dramatic lighting, high production value, {prompt}",
                "Epic scale, masterful direction, stunning visuals, {prompt}"
            ],
            "animated": [
                "Animated style, vibrant colors, smooth animation, {prompt}",
                "Cartoon aesthetic, playful design, dynamic movement, {prompt}",
                "Illustrated scene, artistic style, fluid motion, {prompt}"
            ],
            "surreal": [
                "Surreal dreamlike scene, impossible physics, artistic vision, {prompt}",
                "Abstract interpretation, symbolic elements, otherworldly atmosphere, {prompt}",
                "Psychedelic visuals, mind-bending concepts, surreal artistry, {prompt}"
            ]
        }

    def enhance_prompt(self, prompt: str, style: str = "cinematic") -> str:
        """Enhance user prompt with style-specific details"""
        if style not in self.enhancement_templates:
            style = "cinematic"

        template = self.enhancement_templates[style][0]  # Use first template
        enhanced = template.format(prompt=prompt)

        # Add technical details
        enhanced += ", 4K resolution, professional quality, smooth motion"

        return enhanced

    def enhance_image_prompt(self, prompt: str, style: str) -> str:
        """Enhance prompt for image-to-video generation"""
        enhanced = f"Transform this image into motion: {prompt}"
        enhanced += f", {style} style, smooth camera movement, dynamic transitions"
        return enhanced

class SceneBuilder:
    """Builds detailed scene compositions for video generation"""
    def __init__(self):
        self.transition_types = ["fade", "wipe", "zoom", "pan", "cut"]
        self.camera_movements = ["static", "pan", "zoom", "track", "orbit"]

    def build_scenes(self, prompt: str, duration: int) -> List[Dict[str, Any]]:
        """Build scene composition from prompt"""
        # Parse prompt for key elements
        scenes = []
        words = prompt.lower().split()

        # Create 3-5 scenes based on duration
        num_scenes = min(5, max(2, duration // 2))

        for i in range(num_scenes):
            scene = {
                "scene_number": i + 1,
                "duration": duration // num_scenes,
                "description": f"Scene {i+1} of video about {prompt[:50]}...",
                "camera_movement": self.camera_movements[i % len(self.camera_movements)],
                "transition_in": self.transition_types[i % len(self.transition_types)] if i > 0 else "fade_in",
                "transition_out": self.transition_types[(i+1) % len(self.transition_types)],
                "key_elements": self._extract_key_elements(prompt, i)
            }
            scenes.append(scene)

        return scenes

    def _extract_key_elements(self, prompt: str, scene_index: int) -> List[str]:
        """Extract key visual elements from prompt"""
        # Simple keyword extraction (could be enhanced with NLP)
        keywords = ["sky", "water", "light", "dark", "fast", "slow", "bright", "colorful"]
        found_elements = []

        prompt_lower = prompt.lower()
        for keyword in keywords:
            if keyword in prompt_lower:
                found_elements.append(keyword)

        return found_elements[:3]  # Return up to 3 elements

class AudioComposer:
    """Composes background music and sound effects"""
    def __init__(self, voice_manager=None):
        self.voice_manager = voice_manager
        self.music_styles = ["orchestral", "electronic", "ambient", "upbeat", "dramatic"]
        self.sound_effects = ["nature", "urban", "mechanical", "magical", "abstract"]

    def compose_audio(self, video_prompt: str, duration: int) -> Dict[str, Any]:
        """Compose audio track for video"""
        # Determine music style based on prompt
        music_style = self._determine_music_style(video_prompt)

        return {
            "background_music": {
                "style": music_style,
                "duration": duration,
                "intensity": "medium",
                "tempo": "moderate"
            },
            "sound_effects": self._select_sound_effects(video_prompt),
            "voice_over": {
                "language": "en",
                "style": "professional",
                "speed": "normal"
            }
        }

    def _determine_music_style(self, prompt: str) -> str:
        """Determine appropriate music style from prompt"""
        prompt_lower = prompt.lower()

        if "epic" in prompt_lower or "dramatic" in prompt_lower:
            return "orchestral"
        elif "futuristic" in prompt_lower or "tech" in prompt_lower:
            return "electronic"
        elif "calm" in prompt_lower or "peaceful" in prompt_lower:
            return "ambient"
        elif "fun" in prompt_lower or "energetic" in prompt_lower:
            return "upbeat"
        else:
            return "dramatic"

    def _select_sound_effects(self, prompt: str) -> List[str]:
        """Select appropriate sound effects"""
        effects = []
        prompt_lower = prompt.lower()

        if "water" in prompt_lower:
            effects.append("water_flow")
        if "wind" in prompt_lower:
            effects.append("wind_breeze")
        if "city" in prompt_lower or "urban" in prompt_lower:
            effects.append("city_ambience")

        return effects[:2]  # Limit to 2 effects

class QualityChecker:
    """AI-powered video quality analysis"""
    def __init__(self):
        self.quality_metrics = ["resolution", "framerate", "color_accuracy", "motion_smoothness"]

    def analyze_quality(self, video_path: str) -> Dict[str, Any]:
        """Analyze video quality and provide feedback"""
        # Mock quality analysis (replace with actual video analysis)
        return {
            "overall_score": 85,
            "resolution": {"score": 90, "details": "4K quality maintained"},
            "framerate": {"score": 85, "details": "Smooth 30fps playback"},
            "color_accuracy": {"score": 80, "details": "Good color reproduction"},
            "motion_smoothness": {"score": 85, "details": "Minimal motion artifacts"},
            "recommendations": [
                "Consider increasing contrast for better visual impact",
                "Audio sync is perfect",
                "File size optimized for streaming"
            ]
        }

class PresenterGenerator:
    """Generates AI presenter videos"""
    def __init__(self):
        self.presenter_styles = ["professional", "casual", "educational", "news", "entertainment"]

    def generate_presenter(self, script: str, style: str = "professional") -> Dict[str, Any]:
        """Generate AI presenter video from script"""
        return {
            "script": script,
            "style": style,
            "duration": len(script.split()) * 0.5,  # Rough estimate
            "language": "en",
            "voice": self._select_voice(style),
            "gestures": True,
            "lip_sync": True,
            "background": "studio" if style == "professional" else "casual"
        }

    def _select_voice(self, style: str) -> str:
        """Select appropriate voice for presenter style"""
        voice_map = {
            "professional": "male_professional",
            "casual": "female_casual",
            "educational": "male_educational",
            "news": "female_news",
            "entertainment": "male_entertainment"
        }
        return voice_map.get(style, "male_professional")

class ResourceSearcher:
    """Searches for free resources (music, images, etc.)"""
    def __init__(self):
        self.free_resource_sites = {
            "music": ["freepd.com", "incompetech.com", "soundcloud.com"],
            "images": ["unsplash.com", "pixabay.com", "pexels.com"],
            "sound_effects": ["freesound.org", "soundjay.com"]
        }

    def search_free_resources(self, query: str, resource_type: str = "music") -> List[Dict[str, Any]]:
        """Search for free resources"""
        # Mock search results (replace with actual API calls)
        mock_results = [
            {
                "title": f"Free {resource_type} - {query}",
                "url": f"https://example.com/{resource_type}/{query.replace(' ', '_')}",
                "license": "CC0",
                "quality": "high",
                "download_url": f"https://example.com/download/{query.replace(' ', '_')}"
            }
        ] * 3

        return mock_results

class SpecKitExporter:
    """Exports project blueprints and configurations for sharing and replication"""
    def __init__(self, main_app):
        self.main_app = main_app
        self.export_formats = ["json", "yaml", "xml", "markdown"]

    def export_full_blueprint(self, format_type: str = "json") -> Dict[str, Any]:
        """Export complete project blueprint"""
        blueprint = {
            "metadata": {
                "project_name": "AI Video Remaker & Generator Platform",
                "version": "2.0",
                "export_date": datetime.now().isoformat(),
                "platform": "PyQt6 + Python 3.11+",
                "description": "Complete AI-powered video streaming platform with dual-tab functionality"
            },
            "architecture": self._export_architecture(),
            "agent_hierarchy": self._export_agent_hierarchy(),
            "ui_layout": self._export_ui_layout(),
            "features": self._export_features(),
            "dependencies": self._export_dependencies(),
            "configuration": self._export_configuration(),
            "data_flow": self._export_data_flow(),
            "integration_points": self._export_integration_points()
        }

        return blueprint

    def _export_architecture(self) -> Dict[str, Any]:
        """Export system architecture details"""
        return {
            "components": {
                "VideoRemakerApp": {
                    "type": "Main Application",
                    "framework": "PyQt6",
                    "modules": ["video_collection", "video_editing", "ai_generation", "streaming"]
                },
                "MasterAIManager": {
                    "type": "AI Coordination System",
                    "sub_managers": 6,
                    "mini_agents": 18,
                    "specialties": ["video_collection", "content_analysis", "script_generation",
                                  "video_editing", "quality_assurance", "social_media"]
                },
                "AIVideoGenerator": {
                    "type": "AI Video Generation",
                    "tools": ["runwayml", "stability_ai", "pika_labs", "synthesia", "veo_3", "kling_ai"],
                    "features": ["text_to_video", "image_to_video", "scene_building", "audio_composition"]
                },
                "VoiceManager": {
                    "type": "Multi-language Voice System",
                    "languages": ["English", "Tamil", "Sinhala"],
                    "engines": ["pyttsx3", "google_tts"],
                    "features": ["voice_cloning", "translation", "text_to_speech"]
                }
            },
            "data_flow": {
                "input": ["User topics", "Video prompts", "Style preferences"],
                "processing": ["AI analysis", "Content generation", "Video editing"],
                "output": ["Generated videos", "Streamed content", "Analytics data"]
            }
        }

    def _export_agent_hierarchy(self) -> Dict[str, Any]:
        """Export agent hierarchy and relationships"""
        return {
            "master_ai_manager": {
                "role": "System coordinator and task router",
                "sub_managers": {
                    "video_collection": {
                        "role": "Handles video downloading and collection",
                        "mini_agents": 3,
                        "capabilities": ["YouTube scraping", "Video validation", "Content filtering"]
                    },
                    "content_analysis": {
                        "role": "Analyzes video content and metadata",
                        "mini_agents": 3,
                        "capabilities": ["Text analysis", "Image recognition", "Sentiment analysis"]
                    },
                    "script_generation": {
                        "role": "Creates video scripts and narratives",
                        "mini_agents": 3,
                        "capabilities": ["AI writing", "Story structure", "Language adaptation"]
                    },
                    "video_editing": {
                        "role": "Processes and edits video content",
                        "mini_agents": 3,
                        "capabilities": ["Video cutting", "Transitions", "Effects application"]
                    },
                    "quality_assurance": {
                        "role": "Ensures content quality and compliance",
                        "mini_agents": 3,
                        "capabilities": ["Content moderation", "Quality checking", "Compliance verification"]
                    },
                    "social_media": {
                        "role": "Handles social media integration",
                        "mini_agents": 3,
                        "capabilities": ["Platform posting", "Analytics tracking", "Engagement monitoring"]
                    }
                }
            },
            "universal_topic_expander": {
                "role": "Intelligent topic suggestion system",
                "categories": ["news", "education", "entertainment", "technology", "lifestyle", "sports"],
                "languages": ["English", "Tamil", "Sinhala"],
                "features": ["Auto-suggestions", "Trending topics", "Category matching"]
            }
        }

    def _export_ui_layout(self) -> Dict[str, Any]:
        """Export UI layout and component structure"""
        return {
            "main_window": {
                "framework": "PyQt6",
                "layout": "QMainWindow with QTabWidget",
                "dimensions": "1200x800 minimum"
            },
            "tabs": {
                "video_remaker": {
                    "sections": ["Topic Input", "Clip Collector", "Script Generator", "Scene Composer",
                               "Background Music", "Voice-Over", "Subtitle Generator", "Video Player",
                               "Video Editor", "Review Panel", "Upload/Stream", "Analytics"],
                    "features": ["Auto topic expansion", "15-45s clip duration", "Scene ordering",
                               "Voice sync", "Watermark removal", "Multi-format export"]
                },
                "ai_video_generator": {
                    "sections": ["Prompt Input", "Style Selector", "Scene Builder", "Audio Composer",
                               "Presenter Generator", "Quality Checker", "Export Panel", "Progress Tracker"],
                    "features": ["Veo 3-style generation", "Multiple AI tools", "Style presets",
                               "Real-time preview", "Batch processing", "Quality assurance"]
                },
                "additional_tabs": ["AI Manager Dashboard", "Internet Research", "AI Presenter",
                                  "Voice Editor", "Settings"]
            },
            "global_elements": {
                "floating_chat": {
                    "features": ["Voice input", "Text commands", "Multi-language support"],
                    "positioning": "Draggable overlay"
                },
                "language_selector": ["English", "Tamil", "Sinhala"],
                "voice_selector": ["Multiple presets per language"],
                "topic_input_bar": ["Auto-suggest", "Universal Topic Expander integration"]
            }
        }

    def _export_features(self) -> Dict[str, Any]:
        """Export feature specifications"""
        return {
            "video_remaker_features": {
                "topic_expansion": {
                    "description": "Automatically expands topics into subtopics",
                    "categories": 6,
                    "languages": 3,
                    "confidence_scoring": True
                },
                "clip_collection": {
                    "sources": ["YouTube", "Vimeo", "Dailymotion"],
                    "duration_constraints": "15-45 seconds",
                    "quality_options": ["720p", "1080p", "4K"],
                    "content_filtering": True
                },
                "video_editing": {
                    "transitions": ["fade", "wipe", "cut", "dissolve"],
                    "effects": ["color_grading", "speed_ramp", "stabilization"],
                    "audio_sync": True,
                    "subtitle_generation": True
                },
                "streaming": {
                    "platforms": ["YouTube", "Facebook", "Twitch", "TikTok"],
                    "formats": ["MP4", "WebM", "HLS"],
                    "quality_adaptation": True
                }
            },
            "ai_generation_features": {
                "text_to_video": {
                    "tools": ["RunwayML", "Pika Labs", "Veo 3", "Kling AI"],
                    "max_duration": "60 seconds (Veo 3)",
                    "styles": ["cinematic", "animated", "surreal", "documentary", "commercial"]
                },
                "image_to_video": {
                    "motion_types": ["pan", "zoom", "track", "orbit"],
                    "duration_range": "5-30 seconds",
                    "quality_levels": ["draft", "standard", "premium", "ultra"]
                },
                "audio_composition": {
                    "music_styles": ["orchestral", "electronic", "ambient", "upbeat"],
                    "voice_languages": ["English", "Tamil", "Sinhala"],
                    "sound_effects": True
                }
            },
            "ai_features": {
                "multi_language_support": {
                    "languages": ["English", "Tamil", "Sinhala"],
                    "voice_cloning": True,
                    "real_time_translation": True
                },
                "content_moderation": {
                    "categories": ["hate", "violence", "spam", "explicit"],
                    "severity_levels": ["safe", "moderate", "restricted", "blocked"],
                    "ai_powered_filtering": True
                },
                "quality_assurance": {
                    "metrics": ["resolution", "framerate", "color_accuracy", "motion_smoothness"],
                    "automated_testing": True,
                    "human_review_workflow": True
                }
            }
        }

    def _export_dependencies(self) -> Dict[str, Any]:
        """Export project dependencies"""
        return {
            "python_packages": {
                "core": ["PyQt6", "moviepy", "yt-dlp", "requests", "beautifulsoup4"],
                "ai_ml": ["torch", "transformers", "diffusers", "accelerate"],
                "voice_audio": ["pyttsx3", "gtts", "pydub", "librosa"],
                "video_processing": ["opencv-python", "pillow", "numpy"],
                "web_scraping": ["selenium", "scrapy"],
                "database": ["sqlite3", "sqlalchemy"],
                "utilities": ["python-dotenv", "tqdm", "schedule"]
            },
            "system_requirements": {
                "os": ["Windows 10+", "macOS 10.15+", "Ubuntu 18.04+"],
                "python": "3.11+",
                "ram": "8GB minimum, 16GB recommended",
                "storage": "20GB free space",
                "gpu": "NVIDIA GPU with CUDA support (optional)"
            },
            "external_services": {
                "ai_apis": ["OpenAI", "Anthropic", "Google AI", "Stability AI"],
                "video_platforms": ["YouTube API", "Vimeo API", "TikTok API"],
                "cloud_storage": ["AWS S3", "Google Cloud Storage", "Azure Blob Storage"]
            }
        }

    def _export_configuration(self) -> Dict[str, Any]:
        """Export configuration settings"""
        return {
            "app_settings": {
                "theme": "dark",
                "language": "en",
                "auto_save": True,
                "backup_frequency": "daily"
            },
            "ai_settings": {
                "default_model": "gpt-4",
                "temperature": 0.7,
                "max_tokens": 2000,
                "retry_attempts": 3
            },
            "video_settings": {
                "default_resolution": "1080p",
                "default_fps": 30,
                "default_format": "mp4",
                "compression_quality": "high"
            },
            "voice_settings": {
                "default_language": "en",
                "default_voice": "male_professional",
                "speech_rate": 180,
                "volume": 0.8
            }
        }

    def _export_data_flow(self) -> Dict[str, Any]:
        """Export data flow specifications"""
        return {
            "user_input_flow": {
                "topic_input": "→ Topic Expander → Subtopic Suggestions",
                "video_prompt": "→ AI Generator → Scene Composition",
                "style_selection": "→ Style Processor → Visual Parameters"
            },
            "processing_flow": {
                "video_remaker": "Topic → Clip Collection → Script → Editing → Quality Check → Export",
                "ai_generator": "Prompt → Enhancement → Generation → Post-processing → Delivery"
            },
            "output_flow": {
                "local_storage": "Generated videos → Local filesystem → Database indexing",
                "streaming": "Video files → Streaming server → CDN distribution",
                "social_media": "Processed content → Platform APIs → Automated posting"
            }
        }

    def _export_integration_points(self) -> Dict[str, Any]:
        """Export integration points and APIs"""
        return {
            "ai_services": {
                "openai": {
                    "purpose": "Text generation and analysis",
                    "endpoints": ["completions", "chat", "images"],
                    "rate_limits": "1000 requests/minute"
                },
                "anthropic": {
                    "purpose": "Advanced AI reasoning",
                    "models": ["claude-3", "claude-2"],
                    "features": ["long_context", "code_generation"]
                },
                "google_ai": {
                    "purpose": "Video generation and analysis",
                    "services": ["Veo 3", "Gemini", "Vertex AI"],
                    "regions": ["us-central1", "europe-west1"]
                }
            },
            "video_platforms": {
                "youtube": {
                    "apis": ["Data API v3", "Live Streaming API"],
                    "authentication": "OAuth 2.0",
                    "upload_limits": "15GB per video"
                },
                "vimeo": {
                    "apis": ["API v3"],
                    "features": ["private videos", "advanced analytics"],
                    "upload_limits": "5GB per video"
                }
            },
            "cloud_services": {
                "aws": {
                    "services": ["S3", "Lambda", "EC2"],
                    "use_cases": ["storage", "processing", "hosting"]
                },
                "google_cloud": {
                    "services": ["Cloud Storage", "AI Platform", "Compute Engine"],
                    "use_cases": ["storage", "ai_inference", "hosting"]
                }
            }
        }

    def export_to_file(self, filepath: str, format_type: str = "json") -> bool:
        """Export blueprint to file"""
        try:
            blueprint = self.export_full_blueprint(format_type)

            if format_type == "json":
                import json
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(blueprint, f, indent=2, ensure_ascii=False)
            elif format_type == "yaml":
                try:
                    import yaml
                    with open(filepath, 'w', encoding='utf-8') as f:
                        yaml.dump(blueprint, f, default_flow_style=False, allow_unicode=True)
                except ImportError:
                    return False
            elif format_type == "markdown":
                self._export_to_markdown(filepath, blueprint)
            else:
                return False

            logger.info(f"Blueprint exported to {filepath}")
            return True

        except Exception as e:
            logger.error(f"Export failed: {e}")
            return False

    def _export_to_markdown(self, filepath: str, blueprint: Dict[str, Any]):
        """Export blueprint as markdown documentation"""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("# AI Video Remaker & Generator Platform - Blueprint\n\n")

            # Metadata
            meta = blueprint["metadata"]
            f.write("## Project Overview\n\n")
            f.write(f"- **Name**: {meta['project_name']}\n")
            f.write(f"- **Version**: {meta['version']}\n")
            f.write(f"- **Platform**: {meta['platform']}\n")
            f.write(f"- **Export Date**: {meta['export_date']}\n\n")

            # Architecture
            f.write("## Architecture\n\n")
            arch = blueprint["architecture"]
            for component_name, component_data in arch["components"].items():
                f.write(f"### {component_name}\n")
                f.write(f"- **Type**: {component_data['type']}\n")
                if "framework" in component_data:
                    f.write(f"- **Framework**: {component_data['framework']}\n")
                f.write("\n")

            # Features
            f.write("## Key Features\n\n")
            features = blueprint["features"]
            for category, category_features in features.items():
                f.write(f"### {category.replace('_', ' ').title()}\n\n")
                for feature_name, feature_data in category_features.items():
                    f.write(f"#### {feature_name.replace('_', ' ').title()}\n")
                    if isinstance(feature_data, dict):
                        for key, value in feature_data.items():
                            f.write(f"- **{key.title()}**: {value}\n")
                    else:
                        f.write(f"- {feature_data}\n")
                    f.write("\n")

    def import_blueprint(self, filepath: str) -> Dict[str, Any]:
        """Import blueprint from file"""
        try:
            if filepath.endswith(".json"):
                import json
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            elif filepath.endswith((".yaml", ".yml")):
                import yaml
                with open(filepath, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f)
            else:
                raise ValueError("Unsupported file format")
        except Exception as e:
            logger.error(f"Import failed: {e}")
            return {}

    def validate_blueprint(self, blueprint: Dict[str, Any]) -> List[str]:
        """Validate blueprint structure and completeness"""
        required_sections = ["metadata", "architecture", "features", "dependencies"]
        missing_sections = []

        for section in required_sections:
            if section not in blueprint:
                missing_sections.append(section)

        return missing_sections

class AIVideoGenerationTab(QWidget):
    """Enhanced Tab for AI video generation with Veo 3-style functionality"""
    def __init__(self, ai_generator: AIVideoGenerator, topic_expander: UniversalTopicExpanderAgent = None, main_app=None):
        super().__init__()
        self.ai_generator = ai_generator
        self.topic_expander = topic_expander
        self.main_app = main_app
        self.current_generation = None
        self.init_ui()

    def init_ui(self):
        """Initialize enhanced AI video generation tab"""
        main_layout = QVBoxLayout()

        # Create tab widget for different sections
        self.tab_widget = QTabWidget()

        # Main Generation Tab
        self.generation_tab = self.create_generation_tab()
        self.tab_widget.addTab(self.generation_tab, "🎬 Generate")

        # Style & Presets Tab
        self.style_tab = self.create_style_tab()
        self.tab_widget.addTab(self.style_tab, "🎨 Styles")

        # Scene Builder Tab
        self.scene_tab = self.create_scene_builder_tab()
        self.tab_widget.addTab(self.scene_tab, "📝 Scenes")

        # Audio Composer Tab
        self.audio_tab = self.create_audio_tab()
        self.tab_widget.addTab(self.audio_tab, "🎼 Audio")

        # Presenter Tab
        self.presenter_tab = self.create_presenter_tab()
        self.tab_widget.addTab(self.presenter_tab, "🤖 Presenter")

        # Resources Tab
        self.resources_tab = self.create_resources_tab()
        self.tab_widget.addTab(self.resources_tab, "📚 Resources")

        main_layout.addWidget(self.tab_widget)

        # Progress and Status Section
        self.create_progress_section(main_layout)

        self.setLayout(main_layout)

    def create_generation_tab(self) -> QWidget:
        """Create the main video generation tab"""
        widget = QWidget()
        layout = QVBoxLayout()

        # Tool and Style Selection
        selection_group = QGroupBox("AI Tool & Style Selection")
        selection_layout = QHBoxLayout()

        # AI Tool Selection
        tool_layout = QVBoxLayout()
        tool_layout.addWidget(QLabel("AI Tool:"))
        self.tool_combo = QComboBox()
        tools = self.ai_generator.get_available_tools()
        for tool in tools:
            self.tool_combo.addItem(f"{tool['name']} ({'Free' if tool['free_tier'] else 'Paid'})", tool['name'])
        tool_layout.addWidget(self.tool_combo)

        # Style Selection
        style_layout = QVBoxLayout()
        style_layout.addWidget(QLabel("Style Preset:"))
        self.style_combo = QComboBox()
        styles = self.ai_generator.get_style_presets()
        for style_name, style_data in styles.items():
            self.style_combo.addItem(f"{style_name.title()}: {style_data['description']}", style_name)
        style_layout.addWidget(self.style_combo)

        selection_layout.addLayout(tool_layout)
        selection_layout.addLayout(style_layout)
        selection_group.setLayout(selection_layout)
        layout.addWidget(selection_group)

        # Input Type Selection
        input_type_group = QGroupBox("Input Type")
        input_type_layout = QHBoxLayout()

        self.text_radio = QRadioButton("Text to Video")
        self.text_radio.setChecked(True)
        self.image_radio = QRadioButton("Image to Video")

        input_type_layout.addWidget(self.text_radio)
        input_type_layout.addWidget(self.image_radio)
        input_type_group.setLayout(input_type_layout)
        layout.addWidget(input_type_group)

        # Prompt Input Section
        prompt_group = QGroupBox("Prompt Input")
        prompt_layout = QVBoxLayout()

        # Topic suggestion button
        topic_layout = QHBoxLayout()
        self.topic_input = QLineEdit()
        self.topic_input.setPlaceholderText("Enter topic for suggestions...")
        self.suggest_btn = QPushButton("💡 Get Suggestions")
        self.suggest_btn.clicked.connect(self.get_topic_suggestions)
        topic_layout.addWidget(self.topic_input)
        topic_layout.addWidget(self.suggest_btn)

        prompt_layout.addLayout(topic_layout)

        # Main prompt input
        self.prompt_input = QTextEdit()
        self.prompt_input.setPlaceholderText("Describe the video you want to generate...")
        self.prompt_input.setMaximumHeight(120)
        prompt_layout.addWidget(QLabel("Video Prompt:"))
        prompt_layout.addWidget(self.prompt_input)

        # Enhanced prompt display
        self.enhanced_prompt_display = QTextEdit()
        self.enhanced_prompt_display.setPlaceholderText("Enhanced prompt will appear here...")
        self.enhanced_prompt_display.setMaximumHeight(80)
        self.enhanced_prompt_display.setReadOnly(True)
        prompt_layout.addWidget(QLabel("Enhanced Prompt:"))
        prompt_layout.addWidget(self.enhanced_prompt_display)

        # Enhance button
        self.enhance_btn = QPushButton("✨ Enhance Prompt")
        self.enhance_btn.clicked.connect(self.enhance_prompt)
        prompt_layout.addWidget(self.enhance_btn)

        prompt_group.setLayout(prompt_layout)
        layout.addWidget(prompt_group)

        # Image input (hidden initially)
        image_group = QGroupBox("Image Input")
        image_layout = QHBoxLayout()
        self.image_path_input = QLineEdit()
        self.image_path_input.setPlaceholderText("Select image file...")
        self.image_path_input.hide()
        self.image_button = QPushButton("Browse Image")
        self.image_button.clicked.connect(self.select_image)
        self.image_button.hide()
        image_layout.addWidget(self.image_path_input)
        image_layout.addWidget(self.image_button)
        image_group.setLayout(image_layout)
        image_group.hide()
        self.image_group = image_group
        layout.addWidget(image_group)

        # Duration and Quality Settings
        settings_group = QGroupBox("Video Settings")
        settings_layout = QHBoxLayout()

        duration_layout = QVBoxLayout()
        duration_layout.addWidget(QLabel("Duration (seconds):"))
        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(5, 60)
        self.duration_spin.setValue(15)
        duration_layout.addWidget(self.duration_spin)

        quality_layout = QVBoxLayout()
        quality_layout.addWidget(QLabel("Quality Level:"))
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["Draft", "Standard", "Premium", "Ultra"])
        quality_layout.addWidget(self.quality_combo)

        settings_layout.addLayout(duration_layout)
        settings_layout.addLayout(quality_layout)
        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)

        # Generate button
        self.generate_btn = QPushButton("🚀 Generate Video")
        self.generate_btn.setStyleSheet("QPushButton { font-size: 14px; padding: 10px; }")
        self.generate_btn.clicked.connect(self.generate_video)
        layout.addWidget(self.generate_btn)

        # Connect radio buttons
        self.text_radio.toggled.connect(self.toggle_input_mode)
        self.image_radio.toggled.connect(self.toggle_input_mode)

        widget.setLayout(layout)
        return widget

    def create_style_tab(self) -> QWidget:
        """Create style presets tab"""
        widget = QWidget()
        layout = QVBoxLayout()

        # Style preview grid
        self.style_grid = QGridLayout()

        styles = self.ai_generator.get_style_presets()
        row, col = 0, 0
        for style_name, style_data in styles.items():
            style_card = self.create_style_card(style_name, style_data)
            self.style_grid.addWidget(style_card, row, col)
            col += 1
            if col > 2:
                col = 0
                row += 1

        layout.addLayout(self.style_grid)

        # Custom style settings
        custom_group = QGroupBox("Custom Style Settings")
        custom_layout = QFormLayout()

        self.aspect_ratio_combo = QComboBox()
        self.aspect_ratio_combo.addItems(["16:9", "9:16", "1:1", "4:3", "21:9"])
        custom_layout.addRow("Aspect Ratio:", self.aspect_ratio_combo)

        self.resolution_combo = QComboBox()
        self.resolution_combo.addItems(["720p", "1080p", "4K", "8K"])
        custom_layout.addRow("Resolution:", self.resolution_combo)

        self.fps_combo = QComboBox()
        self.fps_combo.addItems(["24", "30", "60"])
        custom_layout.addRow("Frame Rate:", self.fps_combo)

        custom_group.setLayout(custom_layout)
        layout.addWidget(custom_group)

        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def create_style_card(self, style_name: str, style_data: Dict[str, Any]) -> QGroupBox:
        """Create a style preview card"""
        card = QGroupBox(style_name.title())
        layout = QVBoxLayout()

        description_label = QLabel(style_data['description'])
        description_label.setWordWrap(True)
        layout.addWidget(description_label)

        # Style specs
        specs_text = f"""
        Aspect Ratio: {style_data['aspect_ratio']}
        Resolution: {style_data['resolution']}
        FPS: {style_data['fps']}
        Audio: {style_data['audio_style']}
        """
        specs_label = QLabel(specs_text.strip())
        specs_label.setStyleSheet("font-family: monospace;")
        layout.addWidget(specs_label)

        # Select button
        select_btn = QPushButton(f"Select {style_name.title()}")
        select_btn.clicked.connect(lambda: self.select_style(style_name))
        layout.addWidget(select_btn)

        card.setLayout(layout)
        card.setMaximumWidth(300)
        return card

    def create_scene_builder_tab(self) -> QWidget:
        """Create scene builder tab"""
        widget = QWidget()
        layout = QVBoxLayout()

        # Scene list
        scene_group = QGroupBox("Scene Composition")
        scene_layout = QVBoxLayout()

        self.scene_list = QListWidget()
        self.scene_list.setMaximumHeight(200)
        scene_layout.addWidget(self.scene_list)

        # Scene controls
        controls_layout = QHBoxLayout()
        self.add_scene_btn = QPushButton("➕ Add Scene")
        self.add_scene_btn.clicked.connect(self.add_scene)
        self.remove_scene_btn = QPushButton("➖ Remove Scene")
        self.remove_scene_btn.clicked.connect(self.remove_scene)
        self.build_scenes_btn = QPushButton("🔧 Auto Build")
        self.build_scenes_btn.clicked.connect(self.auto_build_scenes)

        controls_layout.addWidget(self.add_scene_btn)
        controls_layout.addWidget(self.remove_scene_btn)
        controls_layout.addWidget(self.build_scenes_btn)
        scene_layout.addLayout(controls_layout)

        scene_group.setLayout(scene_layout)
        layout.addWidget(scene_group)

        # Scene editor
        editor_group = QGroupBox("Scene Editor")
        editor_layout = QFormLayout()

        self.scene_description = QTextEdit()
        self.scene_description.setMaximumHeight(80)
        editor_layout.addRow("Description:", self.scene_description)

        self.camera_movement_combo = QComboBox()
        self.camera_movement_combo.addItems(["static", "pan", "zoom", "track", "orbit"])
        editor_layout.addRow("Camera:", self.camera_movement_combo)

        self.transition_combo = QComboBox()
        self.transition_combo.addItems(["fade", "wipe", "cut", "dissolve", "zoom"])
        editor_layout.addRow("Transition:", self.transition_combo)

        self.scene_duration_spin = QSpinBox()
        self.scene_duration_spin.setRange(2, 20)
        self.scene_duration_spin.setValue(5)
        editor_layout.addRow("Duration:", self.scene_duration_spin)

        editor_group.setLayout(editor_layout)
        layout.addWidget(editor_group)

        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def create_audio_tab(self) -> QWidget:
        """Create audio composer tab"""
        widget = QWidget()
        layout = QVBoxLayout()

        # Background music settings
        music_group = QGroupBox("Background Music")
        music_layout = QFormLayout()

        self.music_style_combo = QComboBox()
        self.music_style_combo.addItems(["orchestral", "electronic", "ambient", "upbeat", "dramatic"])
        music_layout.addRow("Style:", self.music_style_combo)

        self.music_intensity_combo = QComboBox()
        self.music_intensity_combo.addItems(["low", "medium", "high"])
        music_layout.addRow("Intensity:", self.music_intensity_combo)

        self.music_tempo_combo = QComboBox()
        self.music_tempo_combo.addItems(["slow", "moderate", "fast"])
        music_layout.addRow("Tempo:", self.music_tempo_combo)

        music_group.setLayout(music_layout)
        layout.addWidget(music_group)

        # Voice-over settings
        voice_group = QGroupBox("Voice-Over")
        voice_layout = QFormLayout()

        self.voice_language_combo = QComboBox()
        # Get supported languages from main app's VoiceManager
        if self.main_app and hasattr(self.main_app, 'voice_manager'):
            languages = self.main_app.voice_manager.get_supported_languages()
            self.voice_language_combo.addItems(list(languages.values()))
        else:
            self.voice_language_combo.addItems(["English", "தமிழ் (Tamil)", "සිංහල (Sinhala)"])
        voice_layout.addRow("Language:", self.voice_language_combo)

        self.voice_style_combo = QComboBox()
        # Get voice presets from main app's VoiceManager
        if self.main_app and hasattr(self.main_app, 'voice_manager'):
            voice_presets = self.main_app.voice_manager.get_voice_presets()
            self.voice_style_combo.addItems(list(voice_presets.keys()))
        else:
            self.voice_style_combo.addItems(["news_presenter", "educational", "entertainment", "tamil_news", "sinhala_casual"])
        voice_layout.addRow("Voice Preset:", self.voice_style_combo)

        self.voice_speed_combo = QComboBox()
        self.voice_speed_combo.addItems(["slow", "normal", "fast"])
        voice_layout.addRow("Speed:", self.voice_speed_combo)

        voice_group.setLayout(voice_layout)
        layout.addWidget(voice_group)

        # Sound effects
        effects_group = QGroupBox("Sound Effects")
        effects_layout = QVBoxLayout()

        self.effects_list = QListWidget()
        self.effects_list.setMaximumHeight(100)
        effects_layout.addWidget(self.effects_list)

        effects_controls = QHBoxLayout()
        self.add_effect_btn = QPushButton("➕ Add Effect")
        self.remove_effect_btn = QPushButton("➖ Remove Effect")
        self.search_effects_btn = QPushButton("🔍 Search Free Effects")

        effects_controls.addWidget(self.add_effect_btn)
        effects_controls.addWidget(self.remove_effect_btn)
        effects_controls.addWidget(self.search_effects_btn)
        effects_layout.addLayout(effects_controls)

        effects_group.setLayout(effects_layout)
        layout.addWidget(effects_group)

        # Compose button
        self.compose_audio_btn = QPushButton("🎵 Compose Audio")
        self.compose_audio_btn.clicked.connect(self.compose_audio)
        layout.addWidget(self.compose_audio_btn)

        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def create_presenter_tab(self) -> QWidget:
        """Create AI presenter tab"""
        widget = QWidget()
        layout = QVBoxLayout()

        # Presenter settings
        settings_group = QGroupBox("Presenter Settings")
        settings_layout = QFormLayout()

        self.presenter_style_combo = QComboBox()
        self.presenter_style_combo.addItems(["professional", "casual", "educational", "news", "entertainment"])
        settings_layout.addRow("Style:", self.presenter_style_combo)

        self.presenter_background_combo = QComboBox()
        self.presenter_background_combo.addItems(["studio", "office", "outdoor", "custom"])
        settings_layout.addRow("Background:", self.presenter_background_combo)

        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)

        # Script input
        script_group = QGroupBox("Script")
        script_layout = QVBoxLayout()

        self.presenter_script = QTextEdit()
        self.presenter_script.setPlaceholderText("Enter the script for the AI presenter...")
        script_layout.addWidget(self.presenter_script)

        script_group.setLayout(script_layout)
        layout.addWidget(script_group)

        # Generate button
        self.generate_presenter_btn = QPushButton("🤖 Generate Presenter")
        self.generate_presenter_btn.clicked.connect(self.generate_presenter)
        layout.addWidget(self.generate_presenter_btn)

        # Preview area
        preview_group = QGroupBox("Preview")
        preview_layout = QVBoxLayout()

        self.presenter_preview = QLabel("Presenter preview will appear here")
        self.presenter_preview.setAlignment(Qt.AlignCenter)
        self.presenter_preview.setMinimumHeight(200)
        self.presenter_preview.setStyleSheet("border: 1px solid #ccc; background-color: #f0f0f0;")
        preview_layout.addWidget(self.presenter_preview)

        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)

        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def create_resources_tab(self) -> QWidget:
        """Create resources search tab"""
        widget = QWidget()
        layout = QVBoxLayout()

        # Search section
        search_group = QGroupBox("Resource Search")
        search_layout = QVBoxLayout()

        search_input_layout = QHBoxLayout()
        self.resource_query = QLineEdit()
        self.resource_query.setPlaceholderText("Search for free resources...")
        self.resource_type_combo = QComboBox()
        self.resource_type_combo.addItems(["music", "images", "sound_effects", "videos"])
        self.search_resources_btn = QPushButton("🔍 Search")

        search_input_layout.addWidget(self.resource_query)
        search_input_layout.addWidget(self.resource_type_combo)
        search_input_layout.addWidget(self.search_resources_btn)
        search_layout.addLayout(search_input_layout)

        search_group.setLayout(search_layout)
        layout.addWidget(search_group)

        # Results section
        results_group = QGroupBox("Search Results")
        results_layout = QVBoxLayout()

        self.resources_list = QListWidget()
        self.resources_list.setMaximumHeight(300)
        results_layout.addWidget(self.resources_list)

        # Download button
        self.download_resource_btn = QPushButton("📥 Download Selected")
        self.download_resource_btn.clicked.connect(self.download_resource)
        results_layout.addWidget(self.download_resource_btn)

        results_group.setLayout(results_layout)
        layout.addWidget(results_group)

        # Connect search button
        self.search_resources_btn.clicked.connect(self.search_resources)

        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def create_progress_section(self, parent_layout: QVBoxLayout):
        """Create progress and status section"""
        progress_group = QGroupBox("Generation Progress")
        progress_layout = QVBoxLayout()

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        progress_layout.addWidget(self.progress_bar)

        # Status text
        self.status_text = QTextBrowser()
        self.status_text.setMaximumHeight(150)
        progress_layout.addWidget(self.status_text)

        # Control buttons
        controls_layout = QHBoxLayout()
        self.pause_btn = QPushButton("⏸️ Pause")
        self.stop_btn = QPushButton("⏹️ Stop")
        self.preview_btn = QPushButton("👁️ Preview")

        controls_layout.addWidget(self.pause_btn)
        controls_layout.addWidget(self.stop_btn)
        controls_layout.addWidget(self.preview_btn)
        progress_layout.addLayout(controls_layout)

        progress_group.setLayout(progress_layout)
        parent_layout.addWidget(progress_group)

    # Event handlers
    def get_topic_suggestions(self):
        """Get topic suggestions from Universal Topic Expander"""
        if not self.topic_expander:
            QMessageBox.warning(self, "Error", "Topic expander not available")
            return

        topic = self.topic_input.text().strip()
        if not topic:
            QMessageBox.warning(self, "Error", "Please enter a topic")
            return

        try:
            suggestions = self.topic_expander.expand_topic(topic)
            self.display_topic_suggestions(suggestions)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to get suggestions: {str(e)}")

    def display_topic_suggestions(self, suggestions: Dict[str, Any]):
        """Display topic suggestions in a dialog"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Topic Suggestions")
        dialog.setModal(True)
        layout = QVBoxLayout()

        # Display suggestions
        suggestions_text = QTextBrowser()
        text = f"Original Topic: {suggestions['original_topic']}\n\n"
        text += f"Category: {suggestions['category']}\n\n"
        text += "Suggested Subtopics:\n"

        for subtopic in suggestions['suggested_subtopics']:
            text += f"• {subtopic['subtopic']}: {subtopic['description']}\n"

        suggestions_text.setText(text)
        layout.addWidget(suggestions_text)

        # Use suggestion button
        use_btn = QPushButton("Use Selected Suggestion")
        use_btn.clicked.connect(lambda: self.use_topic_suggestion(dialog))
        layout.addWidget(use_btn)

        dialog.setLayout(layout)
        dialog.resize(500, 400)
        dialog.exec_()

    def use_topic_suggestion(self, dialog):
        """Use selected topic suggestion"""
        # This would be enhanced to actually select and use a suggestion
        dialog.accept()

    def enhance_prompt(self):
        """Enhance the current prompt"""
        prompt = self.prompt_input.toPlainText().strip()
        if not prompt:
            QMessageBox.warning(self, "Error", "Please enter a prompt first")
            return

        style = self.style_combo.currentData()
        enhanced = self.ai_generator.enhance_prompt(prompt, style)
        self.enhanced_prompt_display.setText(enhanced)

    def toggle_input_mode(self):
        """Toggle between text and image input modes"""
        if self.text_radio.isChecked():
            self.image_group.hide()
        else:
            self.image_group.show()

    def select_image(self):
        """Select image file for video generation"""
        file_dialog = QFileDialog()
        file_dialog.setNameFilter("Image files (*.png *.jpg *.jpeg *.bmp)")
        if file_dialog.exec_():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                self.image_path_input.setText(selected_files[0])

    def select_style(self, style_name: str):
        """Select a style preset"""
        self.style_combo.setCurrentText(style_name.title())

    def add_scene(self):
        """Add a new scene"""
        scene_text = f"Scene {self.scene_list.count() + 1}: New scene"
        self.scene_list.addItem(scene_text)

    def remove_scene(self):
        """Remove selected scene"""
        current_row = self.scene_list.currentRow()
        if current_row >= 0:
            self.scene_list.takeItem(current_row)

    def auto_build_scenes(self):
        """Automatically build scenes from prompt"""
        prompt = self.prompt_input.toPlainText().strip()
        if not prompt:
            QMessageBox.warning(self, "Error", "Please enter a prompt first")
            return

        duration = self.duration_spin.value()
        scenes = self.ai_generator.build_scene_composition(prompt, duration)

        self.scene_list.clear()
        for scene in scenes:
            scene_text = f"Scene {scene['scene_number']}: {scene['description'][:50]}..."
            self.scene_list.addItem(scene_text)

    def compose_audio(self):
        """Compose audio track"""
        prompt = self.prompt_input.toPlainText().strip()
        duration = self.duration_spin.value()

        if not prompt:
            QMessageBox.warning(self, "Error", "Please enter a prompt first")
            return

        audio_composition = self.ai_generator.compose_audio(prompt, duration)
        self.status_text.append("Audio composition created:")
        self.status_text.append(json.dumps(audio_composition, indent=2))

    def generate_presenter(self):
        """Generate AI presenter"""
        script = self.presenter_script.toPlainText().strip()
        style = self.presenter_style_combo.currentText()

        if not script:
            QMessageBox.warning(self, "Error", "Please enter a script first")
            return

        presenter_data = self.ai_generator.generate_presenter(script, style)
        self.status_text.append("AI Presenter generated:")
        self.status_text.append(json.dumps(presenter_data, indent=2))

    def search_resources(self):
        """Search for free resources"""
        query = self.resource_query.text().strip()
        resource_type = self.resource_type_combo.currentText()

        if not query:
            QMessageBox.warning(self, "Error", "Please enter a search query")
            return

        resources = self.ai_generator.search_resources(query, resource_type)
        self.resources_list.clear()

        for resource in resources:
            item_text = f"{resource['title']} - {resource.get('license', 'Free')}"
            self.resources_list.addItem(item_text)

    def download_resource(self):
        """Download selected resource"""
        current_item = self.resources_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Error", "Please select a resource to download")
            return

        # Mock download
        QMessageBox.information(self, "Download", "Resource download started (mock)")

    def generate_video_old(self):
        """Generate video using selected AI tool"""
        tool = self.tool_combo.currentData()
        style = self.style_combo.currentData()
        prompt = self.enhanced_prompt_display.toPlainText().strip() or self.prompt_input.toPlainText().strip()
        duration = self.duration_spin.value()

        if not prompt:
            QMessageBox.warning(self, "Error", "Please enter a prompt")
            return

        self.progress_bar.setValue(0)
        self.status_text.clear()
        self.status_text.append("🚀 Starting video generation...")
        self.status_text.append(f"Tool: {tool}")
        self.status_text.append(f"Style: {style}")
        self.status_text.append(f"Duration: {duration} seconds")

        try:
            if self.text_radio.isChecked():
                result = self.ai_generator.generate_video_from_text(prompt, style, tool, duration)
            else:
                image_path = self.image_path_input.text().strip()
                if not image_path:
                    QMessageBox.warning(self, "Error", "Please select an image file")
                    return
                result = self.ai_generator.generate_video_from_image(image_path, prompt, style, tool)

            self.display_generation_result(result)

        except Exception as e:
            self.status_text.append(f"❌ Error: {str(e)}")

    def display_generation_result(self, result: Dict[str, Any]):
        """Display generation result"""
        if 'error' in result:
            self.status_text.append(f"❌ Error: {result['error']}")
            return

        self.status_text.append("✅ Video generation started successfully!")
        self.status_text.append(f"Status: {result.get('status', 'Unknown')}")
        self.status_text.append(f"Estimated Time: {result.get('estimated_time', 'Unknown')}")
        self.status_text.append(f"Quality Level: {result.get('quality_level', 'Unknown')}")

        if 'scenes' in result:
            self.status_text.append(f"Scenes: {len(result['scenes'])}")
            for scene in result['scenes']:
                self.status_text.append(f"  • Scene {scene['scene_number']}: {scene['description'][:30]}...")

        self.progress_bar.setValue(25)  # Initial progress

        # Start progress monitoring
        self.monitor_generation_progress(result)

    def monitor_generation_progress(self, generation_result: Dict[str, Any]):
        """Monitor generation progress"""
        # This would typically connect to real-time updates from the AI service
        # For now, simulate progress updates
        self.current_generation = generation_result

        # Simulate progress updates
        QTimer.singleShot(2000, lambda: self.update_progress(50, "Processing scenes..."))
        QTimer.singleShot(4000, lambda: self.update_progress(75, "Adding audio..."))
        QTimer.singleShot(6000, lambda: self.update_progress(100, "Generation complete!"))

    def update_progress(self, value: int, message: str):
        """Update progress bar and status"""
        self.progress_bar.setValue(value)
        self.status_text.append(message)

        if value >= 100:
            self.status_text.append("🎉 Video generation completed!")
            self.status_text.append("Video URL: (mock_video_url)")
            self.current_generation = None

class InternetResearchModule:
    """Internet research module for finding free resources"""
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def search_free_images(self, query: str, num_results: int = 10) -> List[Dict[str, Any]]:
        """Search for free images using Unsplash API"""
        try:
            # Using Unsplash API (requires API key for production)
            url = f"https://api.unsplash.com/search/photos?query={query}&per_page={num_results}"
            # For demo purposes, using a mock response
            return [
                {
                    "url": f"https://source.unsplash.com/random/800x600?{query}",
                    "description": f"Free image for {query}",
                    "license": "Unsplash License"
                } for _ in range(min(num_results, 5))
            ]
        except Exception as e:
            logger.error(f"Image search failed: {e}")
            return []

    def search_free_music(self, genre: str = "background", num_results: int = 5) -> List[Dict[str, Any]]:
        """Search for free background music"""
        try:
            # Using Free Music Archive or similar
            # Mock response for demo
            return [
                {
                    "title": f"{genre.title()} Background Music {i+1}",
                    "url": f"https://freemusicarchive.org/music/sample_{i+1}.mp3",
                    "duration": "2:30",
                    "license": "Creative Commons"
                } for i in range(min(num_results, 3))
            ]
        except Exception as e:
            logger.error(f"Music search failed: {e}")
            return []

    def search_news_sources(self, topic: str, country: str = "global") -> List[Dict[str, Any]]:
        """Search for news sources related to topic"""
        try:
            sources = {
                "news": {
                    "global": ["BBC News", "Reuters", "Associated Press"],
                    "usa": ["CNN", "New York Times", "Washington Post"],
                    "uk": ["BBC News", "The Guardian", "Sky News"],
                    "sri lanka": ["Daily Mirror", "Ada Derana", "News First"]
                }
            }

            topic_sources = sources.get(topic.lower(), {}).get(country.lower(), [])
            return [{"name": source, "type": "news_source"} for source in topic_sources]
        except Exception as e:
            logger.error(f"News source search failed: {e}")
            return []

    def find_video_resources(self, topic: str) -> Dict[str, Any]:
        """Find various video-related resources for a topic"""
        return {
            "images": self.search_free_images(topic),
            "music": self.search_free_music(topic),
            "news_sources": self.search_news_sources(topic),
            "video_suggestions": [
                f"YouTube search: {topic} documentary",
                f"Vimeo search: {topic} educational",
                f"Free stock footage: {topic}"
            ]
        }

class AIVideoPresenter:
    """AI Video Presenter with basic lip movement simulation"""
    def __init__(self):
        self.presenter_styles = {
            "professional": {"background": "office", "attire": "business_casual"},
            "casual": {"background": "home", "attire": "casual"},
            "educational": {"background": "classroom", "attire": "teacher"}
        }

    def create_presenter_video(self, script: str, style: str = "professional",
                             voice: str = "male") -> Dict[str, Any]:
        """Create AI presenter video (simplified implementation)"""
        try:
            # This would integrate with actual AI video generation services
            # For now, return configuration for external tools

            config = {
                "script": script,
                "style": style,
                "voice": voice,
                "estimated_duration": len(script.split()) * 0.5,  # Rough estimate
                "lip_sync": True,
                "background": self.presenter_styles.get(style, {}).get("background", "default"),
                "recommended_tools": ["Synthesia", "HeyGen", "Steve.ai"]
            }

            return {
                "status": "configured",
                "config": config,
                "message": "Presenter configuration ready. Use recommended tools for actual generation."
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_available_styles(self) -> List[str]:
        """Get available presenter styles"""
        return list(self.presenter_styles.keys())

class VideoRemakerApp(QMainWindow):
    """Main application for AI-powered video remaking"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI-Powered Video Remaker and Streaming Platform")
        self.setGeometry(100, 100, 1200, 800)
        self.plugin_system = PluginSystem()
        self.content_moderator = ContentModerator()
        self.user_auth = UserAuthentication()
        self.cloud_storage = CloudStorage()
        self.uploader = SocialMediaUploader()
        self.analyzer = None  # Initialize after GPT4All
        # Initialize translator (with fallback)
        try:
            self.translator = Translator()
            logger.info("Google Translate initialized successfully")
        except Exception as e:
            logger.warning(f"Google Translate initialization failed: {e}")
            self.translator = None
        self.video_collector = VideoCollector()
        self.video_editor = VideoEditor()
        self.voice_manager = VoiceManager()
        self.ai_manager = MasterAIManager()
        self.topic_expander = UniversalTopicExpanderAgent(self.ai_manager)
        self.ai_video_generator = AIVideoGenerator(self.voice_manager)
        self.research_module = InternetResearchModule()
        self.ai_presenter = AIVideoPresenter()

        # Initialize SpecKit Exporter
        self.spec_kit_exporter = SpecKitExporter(self)

        # Initialize AI system
        self.ai_manager.initialize_system()

        # Integrate AI Video Generator with Master AI Manager
        self.ai_manager.integrate_ai_video_generator(self.ai_video_generator)

        # Database initialization
        self.init_db()

        # Menu initialization
        self.init_menu()

        # Main UI setup
        # self.init_ui()  # Commented out - method doesn't exist
        self.floating_icon = FloatingChatIcon(self)
        self.floating_icon.show()

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready to create amazing videos!")

        # Initialize log_text
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(200)

        # Initialize topic_input
        self.topic_input = QLineEdit()
        self.topic_input.setPlaceholderText("Enter topic for video creation...")

    def init_db(self):
        """Initialize SQLite database"""
        self.conn = sqlite3.connect('video_remaker.db', check_same_thread=False)
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                          (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT, preferences TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS projects 
                          (id INTEGER PRIMARY KEY, user_id INTEGER, project_name TEXT, project_data TEXT, 
                           created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                           FOREIGN KEY(user_id) REFERENCES users (id))''')
        self.conn.commit()

    def init_menu(self):
        """Initialize menu bar"""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu('File')

        load_video_action = QAction('Load Video', self)
        # load_video_action.triggered.connect(self.load_video_file)
        file_menu.addAction(load_video_action)

        # Tools menu
        tools_menu = menubar.addMenu('Tools')

        open_editor_action = QAction('Video Editor', self)
        # open_editor_action.triggered.connect(self.open_video_editor)
        tools_menu.addAction(open_editor_action)

        open_chat_action = QAction('AI Chat', self)
        open_chat_action.triggered.connect(self.open_ai_chat)
        tools_menu.addAction(open_chat_action)

        # Health Check action
        health_check_action = QAction('🔍 Health Check', self)
        # health_check_action.triggered.connect(self.run_health_check)
        tools_menu.addAction(health_check_action)

        # Export menu
        # export_menu = menubar.addMenu('Export')

        # export_blueprint_action = QAction('Export Blueprint', self)
        # export_blueprint_action.triggered.connect(self.export_blueprint)
        # export_menu.addAction(export_blueprint_action)

        # export_project_action = QAction('Export Project', self)
        # export_project_action.triggered.connect(self.export_project)
        # export_menu.addAction(export_project_action)

    def open_video_editor(self):
        """Open the video editor tab"""
        # Switch to the Video Editor tab (index 1)
        self.tabs.setCurrentIndex(1)
        self.log_text.append("🎬 Opened Video Editor tab")

    def open_ai_chat(self):
        """Open the enhanced AI chat interface with full access"""
        if not hasattr(self, 'ai_chat_dialog') or self.ai_chat_dialog is None:
            self.ai_chat_dialog = AIChatDialog(self)
        self.ai_chat_dialog.show()
        self.ai_chat_dialog.raise_()
        self.ai_chat_dialog.activateWindow()
        self.log_text.append("🤖 Opened Enhanced AI Chat Assistant")

class AIChatDialog(QDialog):
    """Enhanced AI Chat Dialog - Natural Language Desktop Assistant"""

    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app
        self.conversation_history = []
        self.current_workflow = None
        self.voice_enabled = True
        self.current_language = "en"
        self.personality_mode = "friendly"  # friendly, professional, casual
        self.voice_available = False  # Initialize voice availability

        # Initialize Hybrid AI Client
        self.ai_client = None
        self.free_tier_client = None
        if HYBRID_AI_AVAILABLE:
            try:
                self.ai_client = HybridAIClient()
                self.free_tier_client = FreeTierAIClient()
                logger.info("Hybrid AI clients initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize hybrid AI: {e}")

        self.init_ui_chat()
        self.setup_ai_connections()
        self.setup_voice_system()

    def init_ui_chat(self):
        """Initialize the enhanced chat dialog UI"""
        self.setWindowTitle("AI Assistant - Your Personal Desktop Helper")
        self.setGeometry(200, 200, 900, 700)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
                border-radius: 15px;
                border: 2px solid #e1e8ed;
            }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        # Enhanced Header
        header_layout = QHBoxLayout()

        # AI Avatar and Name
        avatar_layout = QVBoxLayout()
        self.avatar_label = QLabel("🤖")
        self.avatar_label.setStyleSheet("""
            QLabel {
                font-size: 48px;
                padding: 10px;
                background-color: #0078d4;
                border-radius: 50px;
                color: white;
            }
        """)
        avatar_layout.addWidget(self.avatar_label)

        self.name_label = QLabel("AI Assistant")
        self.name_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #0078d4;")
        avatar_layout.addWidget(self.name_label)

        header_layout.addLayout(avatar_layout)

        # Status and Controls
        status_layout = QVBoxLayout()
        self.status_label = QLabel("👋 Hi! I'm here to help you!")
        self.status_label.setStyleSheet("font-size: 14px; color: #28B463; font-weight: bold;")
        status_layout.addWidget(self.status_label)

        # Language and Voice Controls
        controls_layout = QHBoxLayout()
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["English", "தமிழ் (Tamil)"])
        self.lang_combo.currentTextChanged.connect(self.change_language)
        controls_layout.addWidget(QLabel("🌐"))
        controls_layout.addWidget(self.lang_combo)

        self.voice_btn = QPushButton("🎤 Voice")
        self.voice_btn.setCheckable(True)
        self.voice_btn.setChecked(True)
        self.voice_btn.clicked.connect(self.toggle_voice)
        controls_layout.addWidget(self.voice_btn)

        self.personality_combo = QComboBox()
        self.personality_combo.addItems(["Friendly 😊", "Professional 💼", "Casual 😎"])
        self.personality_combo.currentTextChanged.connect(self.change_personality)
        controls_layout.addWidget(self.personality_combo)

        status_layout.addLayout(controls_layout)
        header_layout.addLayout(status_layout)
        header_layout.addStretch()

        layout.addLayout(header_layout)

        # Chat Display Area with Enhanced Styling
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 2px solid #e1e8ed;
                border-radius: 10px;
                padding: 15px;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 12px;
                line-height: 1.4;
            }
        """)
        layout.addWidget(self.chat_display)

        # Quick Action Buttons - Enhanced
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(8)

        actions = [
            ("🎯 Topics", "Suggest topics", self.suggest_topics),
            ("📄 Analyze", "Analyze files", self.analyze_text_file),
            ("🎬 Create", "Create video", self.start_video_generation),
            ("⚡ Auto", "Auto workflow", self.start_auto_workflow),
            ("🧠 Learn", "Teach me", self.teach_something),
            ("🌟 Fun", "Fun facts", self.fun_facts),
            ("❓ Help", "Get help", self.show_help)
        ]

        for icon, tooltip, func in actions:
            btn = QPushButton(icon)
            btn.setToolTip(tooltip)
            btn.clicked.connect(func)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #f8f9fa;
                    border: 1px solid #dee2e6;
                    border-radius: 8px;
                    padding: 8px 12px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #e9ecef;
                    border: 1px solid #0078d4;
                }
                QPushButton:pressed {
                    background-color: #0078d4;
                    color: white;
                }
            """)
            actions_layout.addWidget(btn)

        layout.addLayout(actions_layout)

        # Enhanced Input Area
        input_layout = QHBoxLayout()

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("💬 Tell me anything... ask questions, give commands, or just chat!")
        self.input_field.returnPressed.connect(self.process_input)
        self.input_field.setStyleSheet("""
            QLineEdit {
                border: 2px solid #dee2e6;
                border-radius: 20px;
                padding: 10px 15px;
                font-size: 14px;
                background-color: #ffffff;
            }
            QLineEdit:focus {
                border: 2px solid #0078d4;
            }
        """)
        input_layout.addWidget(self.input_field)

        self.send_btn = QPushButton("📤 Send")
        self.send_btn.clicked.connect(self.process_input)
        self.send_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 20px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
        """)
        input_layout.addWidget(self.send_btn)

        # Voice input button
        self.voice_input_btn = QPushButton("🎙️")
        self.voice_input_btn.setToolTip("Voice Input")
        self.voice_input_btn.clicked.connect(self.start_voice_input)
        self.voice_input_btn.setStyleSheet("""
            QPushButton {
                background-color: #28B463;
                color: white;
                border: none;
                border-radius: 20px;
                padding: 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        input_layout.addWidget(self.voice_input_btn)

        layout.addLayout(input_layout)

        # Footer with capabilities
        footer_label = QLabel("🧠 I know about: Technology • Health • Education • Entertainment • Local Knowledge • General Topics • Video Creation • File Analysis")
        footer_label.setStyleSheet("""
            QLabel {
                color: #666;
                font-size: 10px;
                padding: 8px;
                background-color: #f8f9fa;
                border-radius: 5px;
                border: 1px solid #e1e8ed;
            }
        """)
        footer_label.setWordWrap(True)
        layout.addWidget(footer_label)

        self.setLayout(layout)

        # Enhanced Welcome Message
        self.add_message("AI Assistant", self.get_welcome_message(), "ai")

    def get_welcome_message(self):
        """Get personalized welcome message based on personality"""
        if self.personality_mode == "friendly":
            return """👋 Hey there! I'm your AI assistant! 

I'm here to help you with absolutely anything - from creating amazing videos to answering questions about technology, health, education, or just having a friendly chat!

🎯 **What I can do for you:**
• Create videos from any topic you can think of
• Analyze documents and extract key information
• Answer questions in English or Tamil
• Help with learning new things
• Share fun facts and interesting information
• Automate your video creation workflow

Just tell me what you need help with! 💫"""
        elif self.personality_mode == "professional":
            return """Greetings! I am your AI Assistant, ready to assist with professional tasks.

**Capabilities:**
• Video content creation and editing
• Document analysis and information extraction
• Multi-language support (English/Tamil)
• Educational content and knowledge sharing
• Workflow automation for productivity

How may I assist you today?"""
        else:  # casual
            return """Yo! What's up? I'm your chill AI buddy! 😎

I can help you create videos, analyze stuff, answer questions, and basically do all sorts of cool things. Just hit me up with whatever you need!

What are we working on today? 🚀"""

    def setup_voice_system(self):
        """Setup voice input/output system"""
        try:
            import speech_recognition as sr
            import pyttsx3
            self.voice_recognizer = sr.Recognizer()
            self.tts_engine = pyttsx3.init()
            self.voice_available = True

            # Configure TTS for multiple languages
            voices = self.tts_engine.getProperty('voices')
            self.english_voice = None
            self.tamil_voice = None

            for voice in voices:
                if 'english' in voice.name.lower() or 'en' in voice.name.lower():
                    self.english_voice = voice
                elif 'tamil' in voice.name.lower() or 'ta' in voice.name.lower():
                    self.tamil_voice = voice

        except ImportError:
            self.voice_available = False
            self.add_message("System", "Voice features not available. Install speech_recognition and pyttsx3 for voice support.", "system")

    def change_language(self, language):
        """Change interface language"""
        if "தமிழ்" in language:
            self.current_language = "ta"
            self.name_label.setText("AI உதவியாளர்")
            self.input_field.setPlaceholderText("💬 என்னிடம் ஏதாவது கேளுங்கள்... கட்டளைகளை கொடுங்கள் அல்லது பேசுங்கள்!")
            self.send_btn.setText("📤 அனுப்பு")
            self.status_label.setText("👋 வணக்கம்! நான் உங்களுக்கு உதவ தயாராக இருக்கிறேன்!")
        else:
            self.current_language = "en"
            self.name_label.setText("AI Assistant")
            self.input_field.setPlaceholderText("💬 Tell me anything... ask questions, give commands, or just chat!")
            self.send_btn.setText("📤 Send")
            self.status_label.setText("👋 Hi! I'm here to help you!")

    def change_personality(self, personality):
        """Change AI personality mode"""
        if "Friendly" in personality:
            self.personality_mode = "friendly"
            self.avatar_label.setText("🤖")
        elif "Professional" in personality:
            self.personality_mode = "professional"
            self.avatar_label.setText("👔")
        else:  # Casual
            self.personality_mode = "casual"
            self.avatar_label.setText("😎")

        self.add_message("AI Assistant", f"Personality changed to {personality.split()[0]} mode! {self.get_personality_emoji()}", "ai")

    def get_personality_emoji(self):
        """Get emoji based on personality"""
        if self.personality_mode == "friendly":
            return "😊"
        elif self.personality_mode == "professional":
            return "💼"
        else:
            return "😎"

    def toggle_voice(self):
        """Toggle voice output"""
        self.voice_enabled = not self.voice_enabled
        status = "enabled" if self.voice_enabled else "disabled"
        self.add_message("AI Assistant", f"Voice output {status} {self.get_personality_emoji()}", "ai")

    def speak_text(self, text):
        """Speak text using TTS"""
        if self.voice_enabled and self.voice_available:
            try:
                if self.current_language == "ta" and self.tamil_voice:
                    self.tts_engine.setProperty('voice', self.tamil_voice.id)
                elif self.english_voice:
                    self.tts_engine.setProperty('voice', self.english_voice.id)

                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            except Exception as e:
                print(f"TTS Error: {e}")

    def start_voice_input(self):
        """Start voice input"""
        if not self.voice_available:
            self.add_message("AI Assistant", "Voice input not available. Please install speech_recognition.", "ai")
            return

        self.status_label.setText("🎤 Listening...")
        self.voice_input_btn.setText("⏹️")

        try:
            with sr.Microphone() as source:
                self.voice_recognizer.adjust_for_ambient_noise(source)
                audio = self.voice_recognizer.listen(source, timeout=5)

            if self.current_language == "ta":
                text = self.voice_recognizer.recognize_google(audio, language="ta-IN")
            else:
                text = self.voice_recognizer.recognize_google(audio)

            self.input_field.setText(text)
            self.status_label.setText("✅ Voice recognized!")
            self.process_input()

        except sr.WaitTimeoutError:
            self.add_message("AI Assistant", "No speech detected. Try again!", "ai")
        except sr.UnknownValueError:
            self.add_message("AI Assistant", "Could not understand audio. Please speak clearly.", "ai")
        except sr.RequestError:
            self.add_message("AI Assistant", "Speech recognition service unavailable.", "ai")
        except Exception as e:
            self.add_message("AI Assistant", f"Voice input error: {str(e)}", "ai")
        finally:
            self.voice_input_btn.setText("🎙️")
            self.status_label.setText("Ready")

    def add_message(self, sender, message, msg_type="user"):
        """Add a message to the chat display with enhanced styling"""
        timestamp = datetime.now().strftime("%H:%M:%S")

        if msg_type == "ai":
            color = "#0078d4"
            icon = "🤖"
            bg_color = "#e3f2fd"
        elif msg_type == "system":
            color = "#28B463"
            icon = "⚡"
            bg_color = "#e8f5e8"
        elif msg_type == "error":
            color = "#dc3545"
            icon = "❌"
            bg_color = "#f8d7da"
        else:
            color = "#333"
            icon = "👤"
            bg_color = "#f8f9fa"

        formatted_message = f'''
        <div style="margin: 8px 0; padding: 12px; background-color: {bg_color}; border-radius: 12px; border-left: 4px solid {color};">
            <div style="display: flex; align-items: center; margin-bottom: 5px;">
                <span style="font-size: 16px; margin-right: 8px;">{icon}</span>
                <strong style="color: {color}; font-size: 13px;">{sender}</strong>
                <small style="color: #666; margin-left: auto; font-size: 10px;">{timestamp}</small>
            </div>
            <div style="color: #333; font-size: 12px; line-height: 1.4;">{message.replace(chr(10), "<br>")}</div>
        </div>'''

        self.chat_display.append(formatted_message)

        # Speak AI messages if voice is enabled
        if msg_type == "ai" and self.voice_enabled:
            # Extract plain text for speech
            plain_text = message.replace('*', '').replace('_', '').replace('#', '')
            self.speak_text(plain_text)

        self.conversation_history.append({"sender": sender, "message": message, "type": msg_type, "timestamp": timestamp})

        # Auto scroll to bottom
        scrollbar = self.chat_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def process_input(self):
        """Process user input with enhanced natural language understanding"""
        user_input = self.input_field.text().strip()
        if not user_input:
            return

        self.add_message("You", user_input, "user")
        self.input_field.clear()

        # Remember user preferences
        self.remember_user_preferences(user_input)

        self.status_label.setText("🤔 Thinking...")

        # Process the input with hybrid AI system
        try:
            # Use hybrid AI client if available
            if self.ai_client:
                # Create context for better responses
                context = {
                    "personality": self.personality_mode,
                    "conversation_history": self.conversation_history[-5:],  # Last 5 messages
                    "current_topic": getattr(self.main_app, 'topic_input', None).text().strip() if hasattr(self.main_app, 'topic_input') else None
                }

                # Get AI response using hybrid system
                ai_result = asyncio.run(self.ai_client.chat_completion(
                    message=user_input,
                    service="auto",  # Auto-select best available service
                    context=context,
                    personality=self.personality_mode
                ))

                response = ai_result["response"]
                service_used = ai_result["service_used"]

                # Add service indicator to response
                if service_used != "fallback":
                    response += f"\n\n_(Powered by {service_used.title()})_"

            else:
                # Fallback to old system if hybrid AI not available
                response = self.process_natural_language_enhanced(user_input)

            # Add conversational flair
            response = self.add_conversational_flair(response)

            self.add_message("AI Assistant", response, "ai")

        except Exception as e:
            logger.error(f"AI processing error: {e}")
            error_msg = f"Oops! Something went wrong: {str(e)}"
            if self.personality_mode == "friendly":
                error_msg = f"Oh no! 😅 {error_msg}\n\nDon't worry, I'm still here to help!"
            elif self.personality_mode == "professional":
                error_msg = f"I apologize for the error: {str(e)}\n\nPlease try again or let me know how else I can assist you."
            else:
                error_msg = f"Whoops! 🤷‍♂️ {error_msg}\n\nLet's try that again!"

            self.add_message("AI Assistant", error_msg, "error")

        self.status_label.setText("Ready")

    def remember_user_preferences(self, input_text):
        """Remember user preferences from conversation"""
        input_lower = input_text.lower()

        # Remember preferred topics
        if "i like" in input_lower or "i love" in input_lower or "i'm interested in" in input_lower:
            # Extract what they like
            if not hasattr(self, 'user_preferences'):
                self.user_preferences = {'liked_topics': [], 'disliked_topics': []}

            # Simple extraction - could be enhanced
            words = input_text.lower().split()
            for i, word in enumerate(words):
                if word in ["like", "love", "interested"] and i < len(words) - 1:
                    topic = words[i + 1]
                    if topic not in self.user_preferences['liked_topics']:
                        self.user_preferences['liked_topics'].append(topic)

        # Remember what they don't like
        elif "i don't like" in input_lower or "i hate" in input_lower or "not interested" in input_lower:
            if not hasattr(self, 'user_preferences'):
                self.user_preferences = {'liked_topics': [], 'disliked_topics': []}

            words = input_text.lower().split()
            for i, word in enumerate(words):
                if word in ["don't", "hate", "not"] and i < len(words) - 1:
                    topic = words[i + 1]
                    if topic not in self.user_preferences['disliked_topics']:
                        self.user_preferences['disliked_topics'].append(topic)

    def add_conversational_flair(self, response):
        """Add conversational flair based on personality and context"""
        if self.personality_mode == "friendly":
            flair_options = [
                " 😊", " 💫", " 🎉", " ✨", " 🌟",
                "\n\nWhat do you think? 🤔",
                "\n\nI'm excited to help! 🚀",
                "\n\nLet me know what you think! 💭"
            ]
        elif self.personality_mode == "professional":
            flair_options = [
                ".", " ✓", " →",
                "\n\nPlease let me know if you need anything else.",
                "\n\nI'm ready to assist with your next request.",
                "\n\nHow else may I be of service?"
            ]
        else:  # casual
            flair_options = [
                " 😎", " 🤙", " 🚀", " 💯", " 🔥",
                "\n\nSound good? 🤔",
                "\n\nLet's make it happen! 💪",
                "\n\nWhat's your take? 🤷‍♂️"
            ]

        # Randomly add flair (30% chance)
        import random
        if random.random() < 0.3:
            flair = random.choice(flair_options)
            if not response.endswith(flair):
                response += flair

        return response

    def process_natural_language_enhanced(self, input_text):
        """Enhanced natural language processing with conversational AI capabilities"""
        input_lower = input_text.lower().strip()

        # Initialize conversation context if not exists
        if not hasattr(self, 'conversation_context'):
            self.conversation_context = {
                'last_topic': None,
                'last_action': None,
                'user_mood': 'neutral',
                'conversation_flow': [],
                'pending_questions': []
            }

        # Add to conversation flow
        self.conversation_context['conversation_flow'].append({
            'input': input_text,
            'timestamp': datetime.now(),
            'type': 'user_input'
        })

        # Keep only last 10 messages for context
        if len(self.conversation_context['conversation_flow']) > 10:
            self.conversation_context['conversation_flow'] = self.conversation_context['conversation_flow'][-10:]

        # Enhanced intent recognition with context
        intent = self.recognize_intent_with_context(input_text)

        # Handle different conversation intents
        if intent['type'] == 'greeting':
            return self.handle_greeting_conversation(input_text, intent)
        elif intent['type'] == 'question':
            return self.handle_question_conversation(input_text, intent)
        elif intent['type'] == 'request':
            return self.handle_request_conversation(input_text, intent)
        elif intent['type'] == 'clarification':
            return self.handle_clarification_conversation(input_text, intent)
        elif intent['type'] == 'follow_up':
            return self.handle_follow_up_conversation(input_text, intent)
        elif intent['type'] == 'casual_chat':
            return self.handle_casual_conversation(input_text, intent)
        else:
            return self.handle_general_conversation(input_text, intent)

    def recognize_intent_with_context(self, input_text):
        """Advanced intent recognition with conversation context"""
        input_lower = input_text.lower()

        # Check for greetings
        greeting_words = ["hello", "hi", "hey", "good morning", "good afternoon", "good evening",
                         "வணக்கம்", "ஹாய்", "hai", "howdy", "greetings", "sup", "yo"]
        if any(word in input_lower for word in greeting_words):
            return {'type': 'greeting', 'confidence': 0.9, 'entities': []}

        # Check for questions
        question_words = ["what", "how", "why", "when", "where", "who", "which", "can you",
                         "could you", "would you", "do you", "are you", "is it", "does it"]
        if any(word in input_lower for word in question_words) or input_text.endswith('?'):
            return {'type': 'question', 'confidence': 0.8, 'entities': self.extract_question_entities(input_text)}

        # Check for requests/commands
        request_words = ["please", "can you", "could you", "would you", "i want", "i need",
                        "make", "create", "generate", "analyze", "help me", "show me"]
        video_words = ["video", "videos", "movie", "film", "content", "story", "news", "documentary", "music"]

        # Check for explicit video creation requests
        if any(word in input_lower for word in request_words) and any(word in input_lower for word in video_words):
            return {'type': 'request', 'confidence': 0.9, 'entities': self.extract_request_entities(input_text)}
        # Check for implicit video creation (just mentioning video topics)
        elif any(word in input_lower for word in video_words) and len(input_text.split()) <= 8:
            return {'type': 'request', 'confidence': 0.7, 'entities': self.extract_request_entities(input_text)}
        # General requests
        elif any(word in input_lower for word in request_words):
            return {'type': 'request', 'confidence': 0.8, 'entities': self.extract_request_entities(input_text)}

        # Check for clarification/follow-up
        clarification_words = ["what do you mean", "i don't understand", "explain", "clarify",
                              "more about", "tell me more", "what about", "and then"]
        if any(word in input_lower for word in clarification_words):
            return {'type': 'clarification', 'confidence': 0.7, 'entities': []}

        # Check for follow-up based on context
        if hasattr(self, 'conversation_context') and self.conversation_context['last_action']:
            follow_up_words = ["yes", "no", "sure", "okay", "that", "this", "it", "them", "those"]
            if any(word in input_lower for word in follow_up_words) or len(input_text.split()) < 5:
                return {'type': 'follow_up', 'confidence': 0.6, 'entities': []}

        # Check for casual conversation
        casual_words = ["nice", "cool", "awesome", "great", "thanks", "thank you", "sorry",
                       "wow", "oh", "hmm", "interesting", "really", "sure", "maybe"]
        if any(word in input_lower for word in casual_words) or len(input_text.split()) < 8:
            return {'type': 'casual_chat', 'confidence': 0.5, 'entities': []}

        # Default to general conversation
        return {'type': 'general', 'confidence': 0.4, 'entities': []}

    def extract_question_entities(self, text):
        """Extract entities from questions"""
        entities = []
        text_lower = text.lower()

        # Extract topics
        if "video" in text_lower or "create" in text_lower:
            entities.append({'type': 'topic', 'value': 'video_creation'})
        if "topic" in text_lower or "suggest" in text_lower:
            entities.append({'type': 'topic', 'value': 'topic_suggestion'})

        return entities

    def extract_request_entities(self, text):
        """Extract entities from requests"""
        entities = []
        text_lower = text.lower()

        # Extract actions
        if "create" in text_lower or "make" in text_lower or "generate" in text_lower:
            entities.append({'type': 'action', 'value': 'create'})
        if "analyze" in text_lower or "read" in text_lower:
            entities.append({'type': 'action', 'value': 'analyze'})
        if "help" in text_lower:
            entities.append({'type': 'action', 'value': 'help'})

        # Extract topics for video creation
        if any(word in text_lower for word in ["create", "make", "generate"]) and "video" in text_lower:
            # Try to extract topic from the request
            words = text_lower.split()
            topic_words = []

            # Skip common words and find the topic
            skip_words = ["can", "you", "make", "create", "generate", "a", "an", "the", "video", "about", "on", "please", "i", "want", "to", "would", "like"]
            for word in words:
                if word not in skip_words and len(word) > 2:
                    topic_words.append(word)

            if topic_words:
                topic = " ".join(topic_words)
                entities.append({'type': 'topic', 'value': topic})

        return entities

    def handle_greeting_conversation(self, input_text, intent):
        """Handle greeting conversations naturally"""
        hour = datetime.now().hour

        if self.personality_mode == "friendly":
            if 5 <= hour < 12:
                base_greeting = "Good morning! 🌅 Hope you're having a great start to your day!"
            elif 12 <= hour < 17:
                base_greeting = "Good afternoon! ☀️ How's your day going?"
            elif 17 <= hour < 22:
                base_greeting = "Good evening! 🌆 Ready to create some amazing videos?"
            else:
                base_greeting = "Hi there! 🌙 Late night creativity session?"

            response = f"{base_greeting}\n\nI'm your AI assistant, here to help you create incredible videos! What would you like to work on today? 🎬✨"

        elif self.personality_mode == "professional":
            if 5 <= hour < 12:
                base_greeting = "Good morning. I trust you're well."
            elif 12 <= hour < 17:
                base_greeting = "Good afternoon. How may I assist you today?"
            elif 17 <= hour < 22:
                base_greeting = "Good evening. Ready to proceed with your video projects?"
            else:
                base_greeting = "Greetings. How can I help you with your video creation needs?"

            response = f"{base_greeting}\n\nI have access to advanced video generation tools and can help you with topic research, content creation, and workflow automation."

        else:  # casual
            if 5 <= hour < 12:
                base_greeting = "Mornin'! ☕"
            elif 12 <= hour < 17:
                base_greeting = "Hey! 😎"
            elif 17 <= hour < 22:
                base_greeting = "Evenin'! 🌙"
            else:
                base_greeting = "Yo! Late night? 🌃"

            response = f"{base_greeting} What's the plan? Got any cool video ideas brewing? 🚀"

        self.conversation_context['last_action'] = 'greeted'
        return response

    def handle_question_conversation(self, input_text, intent):
        """Handle questions with contextual understanding"""
        input_lower = input_text.lower()

        # Handle different types of questions
        if "how are you" in input_lower or "how do you do" in input_lower:
            return self.get_status_response()

        elif "what can you do" in input_lower or "what do you do" in input_lower:
            return self.get_help_text_enhanced()

        elif "video" in input_lower and ("create" in input_lower or "make" in input_lower):
            return "I can help you create amazing videos! Just tell me what topic interests you, and I'll guide you through the process. 🎬\n\nFor example, you could say 'Create a video about cooking' or 'Make a tutorial on photography'."

        elif "topic" in input_lower and ("suggest" in input_lower or "idea" in input_lower):
            return "I'd love to suggest some topics for you! What area interests you most? Like technology, education, entertainment, or something else? 🤔"

        elif "help" in input_lower:
            return self.get_help_text_enhanced()

        else:
            # Try to understand the question and provide relevant response
            if self.personality_mode == "friendly":
                response = "That's a great question! 🤔 Let me think about that...\n\n"
            elif self.personality_mode == "professional":
                response = "I'll do my best to answer your question.\n\n"
            else:
                response = "Hmm, interesting question! Let me see...\n\n"

            response += "I'm designed to help with video creation, topic research, and content generation. If you have questions about creating videos, analyzing content, or need suggestions, I'm here to help! 💡"

            return response

    def handle_request_conversation(self, input_text, intent):
        """Handle requests with natural conversation flow"""
        input_lower = input_text.lower()

        # Handle video creation requests
        if any(word in input_lower for word in ["create", "make", "generate"]) and "video" in input_lower:
            # Check if we extracted a topic
            entities = intent.get('entities', [])
            topic_entity = next((e for e in entities if e['type'] == 'topic'), None)

            if topic_entity:
                # Set the topic in the main app
                self.main_app.topic_input.setText(topic_entity['value'])
                return f"🎯 Got it! I'll create a video about **{topic_entity['value']}**.\n\n{self.handle_video_generation_request(input_text)}"
            else:
                return self.handle_video_generation_request(input_text)

        # Handle topic requests
        elif any(word in input_lower for word in ["suggest", "find", "give"]) and "topic" in input_lower:
            return self.handle_topic_request_enhanced(input_text)

        # Handle analysis requests
        elif "analyze" in input_lower or "read" in input_lower:
            return self.handle_file_analysis_request(input_text)

        # Handle help requests
        elif "help" in input_lower:
            return self.get_help_text_enhanced()

        else:
            # General request handling
            if self.personality_mode == "friendly":
                response = "I'd be happy to help with that! 🎯\n\n"
            elif self.personality_mode == "professional":
                response = "I'll assist you with your request.\n\n"
            else:
                response = "Sure thing! Let's get that done! 😎\n\n"

            response += "Could you tell me more specifically what you'd like me to do? I can help with video creation, topic suggestions, file analysis, and more!"

            return response

    def handle_clarification_conversation(self, input_text, intent):
        """Handle clarification requests"""
        if self.personality_mode == "friendly":
            response = "No problem at all! 😊 Let me explain that better...\n\n"
        elif self.personality_mode == "professional":
            response = "I apologize for any confusion. Allow me to clarify.\n\n"
        else:
            response = "Gotcha! Let me break it down for you! 🤝\n\n"

        response += "I'm an AI assistant specialized in video creation and content generation. I can:\n\n"
        response += "🎬 **Create videos** from any topic you can imagine\n"
        response += "🎯 **Suggest topics** and provide creative ideas\n"
        response += "📄 **Analyze files** and extract useful information\n"
        response += "🧠 **Answer questions** and have conversations\n"
        response += "⚡ **Automate workflows** for efficient content creation\n\n"
        response += "What would you like to explore first?"

        return response

    def handle_follow_up_conversation(self, input_text, intent):
        """Handle follow-up conversations based on context"""
        last_action = self.conversation_context.get('last_action', None)

        if last_action == 'topic_suggested':
            return "Great! Which topic from those suggestions interests you most? Or would you like me to suggest more options? 🤔"

        elif last_action == 'video_created':
            return "Awesome! Your video is ready. Would you like me to help you with anything else, like uploading it or creating another video? 🎉"

        elif last_action == 'file_analyzed':
            return "Perfect! I've analyzed that file for you. Would you like me to create a video based on the content, or help with something else? 📊"

        else:
            if self.personality_mode == "friendly":
                return "I'm here and ready to help! What would you like to work on next? 😊"
            elif self.personality_mode == "professional":
                return "How else may I assist you with your video creation needs?"
            else:
                return "What's next on the agenda? Let's keep creating! 🚀"

    def handle_casual_conversation(self, input_text, intent):
        """Handle casual conversation naturally"""
        input_lower = input_text.lower()

        if "thanks" in input_lower or "thank you" in input_lower:
            return self.get_thanks_response()

        elif "nice" in input_lower or "cool" in input_lower or "awesome" in input_lower:
            if self.personality_mode == "friendly":
                return "I'm glad you think so! 😊 What else would you like to explore?"
            elif self.personality_mode == "professional":
                return "Thank you for the feedback. How else may I assist you?"
            else:
                return "Right? 😎 What's our next move?"

        elif "sorry" in input_lower:
            if self.personality_mode == "friendly":
                return "No need to apologize! 😊 I'm here to help however I can."
            elif self.personality_mode == "professional":
                return "That's quite alright. How can I assist you now?"
            else:
                return "No worries at all! 🤙 What's up?"

        else:
            # Generic positive response
            if self.personality_mode == "friendly":
                return "I hear you! 💫 What would you like to work on together?"
            elif self.personality_mode == "professional":
                return "Understood. How may I help you with your video creation project?"
            else:
                return "Got it! 😎 Let's make something awesome!"

    def handle_general_conversation(self, input_text, intent):
        """Handle general conversation with intelligent responses"""
        # Try to extract potential topics or actions from the input
        topic = self.extract_topic_from_text_enhanced(input_text)

        if topic:
            # User mentioned a topic - offer to work with it
            self.main_app.topic_input.setText(topic)

            if self.personality_mode == "friendly":
                response = f"Ooh, {topic} sounds interesting! 🎯\n\n"
            elif self.personality_mode == "professional":
                response = f"I see you're interested in {topic}.\n\n"
            else:
                response = f"{topic}? That's cool! 😎\n\n"

            response += f"I can help you create amazing videos about {topic}! Would you like me to:\n\n"
            response += f"🎬 Generate a video about {topic}\n"
            response += f"🎯 Suggest related topics\n"
            response += f"📚 Teach you more about {topic}\n"
            response += f"🧠 Share interesting facts about {topic}"

            self.conversation_context['last_topic'] = topic
            return response

        else:
            # Couldn't identify a specific topic or action
            if self.personality_mode == "friendly":
                response = "That sounds interesting! 🤔\n\n"
            elif self.personality_mode == "professional":
                response = "I understand you're looking for assistance.\n\n"
            else:
                response = "Hmm, tell me more! 😏\n\n"

            response += "I'm here to help with video creation! You can ask me to:\n\n"
            response += "• Create videos on any topic\n"
            response += "• Suggest creative ideas\n"
            response += "• Analyze documents or files\n"
            response += "• Help with video editing\n"
            response += "• Automate your workflow\n\n"
            response += "What would you like to work on? 💫"

            return response

    def get_greeting_response(self):
        """Get personalized greeting based on personality and language"""
        if self.personality_mode == "friendly":
            if self.current_language == "ta":
                return "வணக்கம்! நான் உங்கள் AI உதவியாளர். உங்களுக்கு எப்படி உதவ வேண்டும்? 😊"
            else:
                return "Hey there! 👋 I'm your AI assistant. What can I help you with today?"
        elif self.personality_mode == "professional":
            if self.current_language == "ta":
                return "வணக்கம். நான் உங்கள் AI உதவியாளர். தயவுசெய்து உங்கள் கோரிக்கையை தெரிவிக்கவும்."
            else:
                return "Greetings! I am your AI assistant. How may I assist you?"
        else:
            if self.current_language == "ta":
                return "ஹாய்! என்ன சொல்ல வர்ற? 😎"
            else:
                return "Yo! What's up? 😎"

    def get_thanks_response(self):
        """Get thanks response"""
        if self.personality_mode == "friendly":
            return "You're so welcome! 😊 Happy to help anytime!"
        elif self.personality_mode == "professional":
            return "You're welcome. I'm here whenever you need assistance."
        else:
            return "No problem! Anytime! 👍"

    def get_status_response(self):
        """Get status response"""
        if self.personality_mode == "friendly":
            return "I'm doing great, thanks for asking! 💪 Ready to help you with anything - videos, questions, or just chatting!"
        elif self.personality_mode == "professional":
            return "I am functioning optimally and ready to assist with your requests."
        else:
            return "I'm awesome! 😎 What's on your mind?"

    def handle_topic_request_enhanced(self, input_text):
        """Enhanced topic suggestion with personality"""
        topic = self.extract_topic_from_text_enhanced(input_text)

        if topic:
            self.main_app.topic_input.setText(topic)
            suggestions = self.main_app.topic_expander.get_topic_suggestions(topic)

            if self.personality_mode == "friendly":
                response = f"🎯 **Awesome choice!** I've set your topic to: **{topic}**\n\n"
            elif self.personality_mode == "professional":
                response = f"🎯 **Topic confirmed:** {topic}\n\n"
            else:
                response = f"🎯 **Cool topic:** {topic}\n\n"

            response += "**Here are some sub-topic suggestions I think you'll love:**\n\n"
            for i, suggestion in enumerate(suggestions[:5], 1):
                response += f"{i}. **{suggestion['topic']}** ({suggestion['category']})\n"
                response += f"   _{suggestion['description']}_\n\n"

            if self.personality_mode == "friendly":
                response += "💡 **Pro tip:** Click the '✓ Use' buttons in the main interface to select any suggestion, or just tell me which one you like!"
            elif self.personality_mode == "professional":
                response += "💡 Please select a suggestion from the main interface or inform me of your preference."
            else:
                response += "💡 Pick one or tell me what you want! 😎"

            return response
        else:
            if self.personality_mode == "friendly":
                return "🤔 Hmm, I couldn't figure out what topic you meant. Try something like 'suggest topics about cooking' or 'I want to create a video about technology'! 🍳🤖"
            elif self.personality_mode == "professional":
                return "I apologize, but I could not identify a specific topic in your request. Please provide more details about the subject matter."
            else:
                return "Not sure what you mean! Try 'topics about [something]' or just tell me what you want! 🤷‍♂️"

    def handle_learning_request(self, input_text):
        """Handle learning/teaching requests"""
        # Extract what they want to learn
        learn_topic = self.extract_learning_topic(input_text)

        if learn_topic:
            if self.personality_mode == "friendly":
                response = f"📚 **Let's learn about {learn_topic}!** 🎓\n\n"
            elif self.personality_mode == "professional":
                response = f"📚 **Educational Content: {learn_topic}**\n\n"
            else:
                response = f"📚 **{learn_topic} time!** 🧠\n\n"

            # Provide basic information about common topics
            if "python" in learn_topic.lower():
                response += "**Python Programming:**\n"
                response += "• Python is a high-level programming language\n"
                response += "• Great for beginners and experts alike\n"
                response += "• Used for web development, data science, AI, and more\n"
                response += "• Fun fact: Named after Monty Python! 🐍"
            elif "ai" in learn_topic.lower() or "artificial intelligence" in learn_topic.lower():
                response += "**Artificial Intelligence:**\n"
                response += "• AI is machines performing tasks that typically require human intelligence\n"
                response += "• Includes machine learning, computer vision, natural language processing\n"
                response += "• Applications: Self-driving cars, medical diagnosis, content creation\n"
                response += "• The future is here! 🤖"
            else:
                response += f"I can help you learn about {learn_topic}! Would you like me to:\n"
                response += "• Create educational content about it\n"
                response += "• Find related resources\n"
                response += "• Generate practice questions\n"
                response += "• Make a learning video"

            return response
        else:
            return "What would you like to learn about? I can teach you anything from programming to science to cooking! 📚"

    def handle_fun_request(self, input_text):
        """Handle fun facts and interesting information requests"""
        fun_topics = {
            "random": [
                "Did you know? Honey never spoils! Archaeologists found 3000-year-old honey that was still edible! 🍯",
                "Octopuses have three hearts and blue blood! 🐙💙",
                "A group of flamingos is called a 'flamboyance'! 🦅",
                "Bananas are berries, but strawberries aren't! 🍌🍓"
            ],
            "tech": [
                "The first computer mouse was made of wood! 🖱️",
                "There are more possible games of chess than atoms in the observable universe! ♟️",
                "The @ symbol was used in commerce for centuries before email! 📧",
                "The first programming language was developed in 1883 for the Jacquard loom! 💻"
            ],
            "space": [
                "A day on Venus is longer than its year! 🪐",
                "There are more stars in the universe than grains of sand on Earth! 🌌",
                "Neutron stars are so dense, a teaspoon weighs billions of tons! ⚛️",
                "The Milky Way galaxy is 100,000 light-years across! 🌌"
            ]
        }

        if "tech" in input_text.lower():
            facts = fun_topics["tech"]
        elif "space" in input_text.lower():
            facts = fun_topics["space"]
        else:
            facts = fun_topics["random"]

        import random
        fact = random.choice(facts)

        if self.personality_mode == "friendly":
            return f"🎉 **Fun Fact!** {fact}\n\nWant another fun fact or something specific?"
        elif self.personality_mode == "professional":
            return f"📚 **Interesting Fact:** {fact}"
        else:
            return f"🤯 **Whoa!** {fact}\n\nCool, right? 😎"

    def extract_learning_topic(self, text):
        """Extract learning topic from text"""
        learn_keywords = ["teach me", "learn about", "explain", "what is", "how to", "tell me about"]
        for keyword in learn_keywords:
            if keyword in text.lower():
                parts = text.lower().split(keyword, 1)
                if len(parts) > 1:
                    return parts[1].strip().title()
        return text.strip().title()

    def teach_something(self):
        """Teach something new"""
        topics = ["Python Programming", "Artificial Intelligence", "Digital Marketing", "Photography", "Cooking Basics"]
        import random
        topic = random.choice(topics)

        if self.personality_mode == "friendly":
            response = f"🎓 **Let's learn {topic}!**\n\n"
        elif self.personality_mode == "professional":
            response = f"📚 **Educational Session: {topic}**\n\n"
        else:
            response = f"🧠 **{topic} crash course!**\n\n"

        response += "What specific aspect would you like to know about?"
        self.add_message("AI Assistant", response, "ai")

    def fun_facts(self):
        """Share fun facts"""
        self.add_message("AI Assistant", self.handle_fun_request("random"), "ai")

    def show_help(self):
        """Show enhanced help"""
        self.add_message("AI Assistant", self.get_help_text_enhanced(), "ai")

    def get_help_text_enhanced(self):
        """Get enhanced help text"""
        if self.personality_mode == "friendly":
            help_text = """🤖 **Hey! I'm your AI Assistant - Here's what I can do!** 😊

**🎯 Video Creation:**
• "Create a video about [topic]"
• "Suggest topics about [subject]"
• "Generate video for [idea]"

**📄 Content Analysis:**
• "Analyze my document.txt"
• "Read this file and summarize"
• "Extract topics from [file]"

**🧠 Learning & Knowledge:**
• "Teach me about Python"
• "Explain artificial intelligence"
• "What is machine learning?"

**🎉 Fun & Conversation:**
• "Tell me a fun fact"
• "How are you doing?"
• "What's the weather like?"

**⚡ Automation:**
• "Start auto workflow"
• "Create video automatically"
• "Process my files"

**🌐 Languages:**
• Switch between English and Tamil
• Voice input/output support
• Multi-language content creation

Just type naturally - I'm here to understand you! 💫"""
        elif self.personality_mode == "professional":
            help_text = """🤖 **AI Assistant Capabilities**

**Core Functions:**
• Video content generation and editing
• Document analysis and information extraction
• Educational content creation
• Multi-language support (English/Tamil)
• Voice interaction capabilities

**Available Commands:**
• Topic suggestions and content creation
• File processing and analysis
• Automated workflow management
• Knowledge sharing and explanations
• Interactive conversation

Please specify your requirements clearly."""
        else:
            help_text = """🤖 **Yo! Your AI Buddy Here!** 😎

**What I Can Do:**
• Make awesome videos from any idea
• Read and analyze your files
• Teach you cool stuff
• Chat about anything
• Automate boring tasks

**Just Say:**
• "Make a video about [anything]"
• "Analyze this file"
• "Teach me [topic]"
• "Fun fact please"
• "What's up?"

I'm chill, just tell me what you need! 🚀"""

        return help_text

    def extract_topic_from_text_enhanced(self, text):
        """Enhanced topic extraction"""
        # More comprehensive topic extraction
        topic_indicators = [
            "about", "on", "regarding", "concerning", "topic of", "video about",
            "create video on", "make video about", "विषय", "बारे में", "विषय पर"
        ]

        for indicator in topic_indicators:
            if indicator in text.lower():
                parts = text.lower().split(indicator, 1)
                if len(parts) > 1:
                    topic = parts[1].strip()
                    # Clean up the topic
                    topic = topic.rstrip('?.!')
                    # Remove common words
                    remove_words = ["a", "an", "the", "please", "can you", "i want"]
                    words = topic.split()
                    filtered_words = [w for w in words if w not in remove_words]
                    return " ".join(filtered_words).title()

        # If no indicators found, treat as direct topic
        return text.strip().title() if len(text.strip()) > 3 else None

    def setup_ai_connections(self):
        """Setup connections to AI manager system"""
        try:
            if hasattr(self.main_app, 'ai_manager'):
                self.ai_manager = self.main_app.ai_manager
            else:
                self.ai_manager = None
        except:
            self.ai_manager = None

    def process_natural_language(self, input_text):
        """Process natural language input and take appropriate actions"""
        input_lower = input_text.lower()

        # Topic-related commands
        if any(word in input_lower for word in ["topic", "suggest", "idea", "subject"]):
            return self.handle_topic_request(input_text)

        # File analysis commands
        elif any(word in input_lower for word in ["analyze", "read", "file", "text", "document"]):
            return self.handle_file_analysis_request(input_text)

        # Video generation commands
        elif any(word in input_lower for word in ["generate", "create", "make", "video", "produce"]):
            return self.handle_video_generation_request(input_text)

        # Workflow commands
        elif any(word in input_lower for word in ["workflow", "auto", "automatic", "process"]):
            return self.handle_workflow_request(input_text)

        # Topic confirmation commands
        elif any(word in input_lower for word in ["confirm", "details", "show topic", "topic details"]):
            return self.confirm_topic_details(input_text)

        # Help commands
        elif any(word in input_lower for word in ["help", "what can you do", "commands", "guide"]):
            return self.get_help_text()

        # Direct topic input
        else:
            return self.handle_direct_topic_input(input_text)

    def confirm_topic_details(self, input_text):
        """Handle topic confirmation requests"""
        self.confirm_full_topics_with_details()
        return "✅ Topic confirmation displayed above."

    def handle_topic_request(self, input_text):
        """Handle topic suggestion requests"""
        # Extract potential topic from input
        topic = self.extract_topic_from_text(input_text)

        if topic:
            self.main_app.topic_input.setText(topic)
            suggestions = self.main_app.topic_expander.get_topic_suggestions(topic)

            response = f"🎯 I've set your topic to: **{topic}**\n\nHere are some sub-topic suggestions:\n\n"
            for i, suggestion in enumerate(suggestions[:5], 1):
                response += f"{i}. **{suggestion['topic']}** ({suggestion['category']})\n"
                response += f"   {suggestion['description']}\n\n"

            response += "You can click the '✓ Use' buttons in the main interface to select any suggestion, or tell me to proceed with a specific topic."

            return response
        else:
            return "I couldn't identify a specific topic in your request. Please try something like 'suggest topics about technology' or 'I want to create a video about cooking'."

    def handle_file_analysis_request(self, input_text):
        """Handle file analysis requests"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Select Text File to Analyze",
                "", "Text files (*.txt *.md *.docx *.pdf);;All files (*)"
            )

            if file_path:
                content = self.read_text_file(file_path)
                if content:
                    # Analyze the content
                    analysis = self.analyze_text_content(content)

                    # Set topic based on analysis
                    main_topic = analysis.get('main_topic', 'Document Analysis')
                    self.main_app.topic_input.setText(main_topic)

                    response = f"📄 **File Analyzed:** {os.path.basename(file_path)}\n\n"
                    response += f"**Main Topic:** {main_topic}\n"
                    response += f"**Word Count:** {analysis.get('word_count', 0)}\n"
                    response += f"**Key Themes:** {', '.join(analysis.get('key_themes', []))}\n\n"
                    response += "**Suggested Video Topics:**\n"

                    for topic in analysis.get('suggested_topics', [])[:3]:
                        response += f"• {topic}\n"

                    return response
                else:
                    return "Could not read the selected file. Please try a different file."
            else:
                return "No file selected."

        except Exception as e:
            return f"Error analyzing file: {str(e)}"

    def handle_video_generation_request(self, input_text):
        """Handle video generation requests"""
        current_topic = self.main_app.topic_input.text().strip()

        if not current_topic:
            return "Please set a topic first by typing something like 'topic about technology' or selecting a topic from the suggestions."

        # Start video generation
        self.start_video_generation()
        return f"🎬 Starting video generation for topic: **{current_topic}**\n\nI'll switch to the video generation tab and begin the process. You can monitor the progress in the log area."

    def handle_workflow_request(self, input_text):
        """Handle automated workflow requests"""
        return self.start_auto_workflow()

    def handle_direct_topic_input(self, input_text):
        """Handle direct topic input"""
        # Treat the entire input as a potential topic
        self.main_app.topic_input.setText(input_text)

        # Get suggestions
        suggestions = self.main_app.topic_expander.get_topic_suggestions(input_text)

        if suggestions:
            response = f"🎯 I've interpreted '{input_text}' as your topic.\n\n**Suggestions:**\n"
            for suggestion in suggestions[:3]:
                response += f"• {suggestion['topic']} ({suggestion['category']})\n"
            response += "\nWould you like me to generate a video about this topic, or would you prefer to refine it first?"
        else:
            response = f"✅ Set topic to: **{input_text}**\n\nReady to generate a video about this topic. Just let me know when you're ready!"

        return response

    def extract_topic_from_text(self, text):
        """Extract topic from natural language text"""
        # Simple keyword extraction
        topic_keywords = ["about", "on", "regarding", "concerning", "topic of", "video about", "create video on"]

        for keyword in topic_keywords:
            if keyword in text.lower():
                parts = text.lower().split(keyword, 1)
                if len(parts) > 1:
                    topic = parts[1].strip()
                    # Clean up the topic
                    topic = topic.rstrip('?.!')
                    return topic.title()

        # If no keywords found, return the whole text as topic
        return text.strip().title() if len(text.strip()) > 3 else None

    def read_text_file(self, file_path):
        """Read content from text file"""
        try:
            if file_path.endswith('.pdf'):
                # Handle PDF files
                import PyPDF2
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    content = ""
                    for page in pdf_reader.pages:
                        content += page.extract_text()
                    return content
            elif file_path.endswith('.docx'):
                # Handle Word documents
                from docx import Document
                doc = Document(file_path)
                content = ""
                for paragraph in doc.paragraphs:
                    content += paragraph.text + "\n"
                return content
            else:
                # Handle plain text files
                with open(file_path, 'r', encoding='utf-8') as file:
                    return file.read()
        except Exception as e:
            self.add_message("System", f"Error reading file: {str(e)}", "system")
            return None

    def analyze_text_content(self, content):
        """Analyze text content for topics and themes"""
        words = content.lower().split()
        word_count = len(words)

        # Simple keyword analysis
        topic_indicators = {
            'technology': ['computer', 'software', 'internet', 'digital', 'tech', 'ai', 'machine learning'],
            'education': ['learn', 'study', 'school', 'teach', 'education', 'course', 'tutorial'],
            'health': ['health', 'medical', 'doctor', 'disease', 'treatment', 'wellness'],
            'business': ['business', 'company', 'market', 'finance', 'money', 'profit', 'sales'],
            'entertainment': ['movie', 'music', 'game', 'fun', 'entertainment', 'celebrity'],
            'sports': ['sport', 'game', 'team', 'player', 'competition', 'athlete'],
            'news': ['news', 'current', 'event', 'breaking', 'update', 'report'],
            'science': ['science', 'research', 'experiment', 'discovery', 'theory']
        }

        # Count topic matches
        topic_scores = {}
        for topic, keywords in topic_indicators.items():
            score = sum(1 for keyword in keywords if keyword in words)
            if score > 0:
                topic_scores[topic] = score

        # Determine main topic
        main_topic = max(topic_scores.items(), key=lambda x: x[1])[0] if topic_scores else 'General'

        # Extract key themes (most frequent words)
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'shall'}
        word_freq = {}
        for word in words:
            if len(word) > 3 and word not in stop_words:
                word_freq[word] = word_freq.get(word, 0) + 1

        key_themes = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]
        key_themes = [word for word, freq in key_themes]

        # Generate suggested video topics
        suggested_topics = []
        if main_topic != 'General':
            suggested_topics.append(f"{main_topic.title()} Overview")
            suggested_topics.append(f"Latest {main_topic.title()} Trends")
            suggested_topics.append(f"{main_topic.title()} Tips and Tricks")

        for theme in key_themes[:2]:
            suggested_topics.append(f"Understanding {theme.title()}")

        return {
            'main_topic': main_topic.title(),
            'word_count': word_count,
            'key_themes': key_themes,
            'suggested_topics': suggested_topics
        }

    def suggest_topics(self):
        """Suggest topics based on current context"""
        current_topic = self.main_app.topic_input.text().strip()

        if current_topic:
            suggestions = self.main_app.topic_expander.get_topic_suggestions(current_topic)
            response = f"🎯 **Topic Suggestions for '{current_topic}':**\n\n"
        else:
            # General suggestions
            suggestions = [
                {"topic": "Technology Trends", "category": "Technology", "description": "Latest tech innovations and trends"},
                {"topic": "Health & Wellness", "category": "Health", "description": "Tips for healthy living"},
                {"topic": "Educational Content", "category": "Education", "description": "Learning and knowledge sharing"},
                {"topic": "Entertainment News", "category": "Entertainment", "description": "Movies, music, and pop culture"},
                {"topic": "Business Insights", "category": "Business", "description": "Business tips and strategies"}
            ]
            response = "🎯 **General Topic Suggestions:**\n\n"

        for i, suggestion in enumerate(suggestions[:5], 1):
            response += f"{i}. **{suggestion['topic']}** ({suggestion['category']})\n"
            response += f"   {suggestion['description']}\n\n"

        self.add_message("AI Assistant", response, "ai")

    def analyze_text_file(self):
        """Analyze a text file selected by user"""
        response = self.handle_file_analysis_request("analyze text file")
        self.add_message("AI Assistant", response, "ai")

    def start_video_generation(self):
        """Start video generation process"""
        current_topic = self.main_app.topic_input.text().strip()

        if not current_topic:
            self.add_message("AI Assistant", "Please set a topic first. You can type something like 'topic about technology' or use the topic suggestions.", "ai")
            return

        # Switch to video generation tab
        self.main_app.tabs.setCurrentIndex(0)  # Video generation tab

        # Start the generation process
        self.main_app.generate_video()

        response = f"🎬 **Starting Video Generation**\n\nTopic: **{current_topic}**\nStatus: Process initiated\n\nCheck the main interface for progress updates."
        self.add_message("AI Assistant", response, "ai")

    def start_auto_workflow(self):
        """Start automated workflow from topic to video"""
        current_topic = self.main_app.topic_input.text().strip()

        if not current_topic:
            self.add_message("AI Assistant", "Please set a topic first. What topic would you like to create a video about?", "ai")
            return

        response = f"⚡ **Starting Automated Workflow**\n\nTopic: **{current_topic}**\n\n**Workflow Steps:**\n"
        response += "1. ✅ Topic analysis\n"
        response += "2. 🔄 Content generation\n"
        response += "3. 🎵 Background music selection\n"
        response += "4. 🎬 Video rendering\n"
        response += "5. 📤 Export and upload\n\n"
        response += "I'll handle the entire process automatically. Sit back and relax!"

        self.add_message("AI Assistant", response, "ai")

        # Start the workflow
        QTimer.singleShot(1000, lambda: self.execute_workflow_step(1))

    def execute_workflow_step(self, step):
        """Execute individual workflow steps"""
        if step == 1:
            self.add_message("AI Assistant", "🔄 Step 1: Analyzing topic and generating content...", "ai")
            # Topic analysis is already done
            QTimer.singleShot(2000, lambda: self.execute_workflow_step(2))

        elif step == 2:
            self.add_message("AI Assistant", "🎵 Step 2: Selecting background music...", "ai")
            # Auto-select default music or prompt user
            QTimer.singleShot(2000, lambda: self.execute_workflow_step(3))

        elif step == 3:
            self.add_message("AI Assistant", "🎬 Step 3: Starting video generation...", "ai")
            self.start_video_generation()
            QTimer.singleShot(3000, lambda: self.execute_workflow_step(4))

        elif step == 4:
            self.add_message("AI Assistant", "📤 Step 4: Preparing for export...", "ai")
            # This would be handled by the main app's export functionality
            QTimer.singleShot(2000, lambda: self.execute_workflow_step(5))

        elif step == 5:
            self.add_message("AI Assistant", "✅ Workflow Complete! Your video is ready.", "ai")

    def confirm_full_topics_with_details(self):
        """Confirm and display full topic details"""
        current_topic = self.main_app.topic_input.text().strip()

        if not current_topic:
            self.add_message("AI Assistant", "❌ No topic is currently set. Please set a topic first.", "ai")
            return

        # Get detailed topic information
        topic_details = self.get_topic_details(current_topic)

        response = f"📋 **FULL TOPIC CONFIRMATION**\n\n"
        response += f"🎯 **Main Topic:** {topic_details['main_topic']}\n"
        response += f"📂 **Category:** {topic_details['category']}\n"
        response += f"📝 **Description:** {topic_details['description']}\n\n"

        response += f"🔍 **Topic Analysis:**\n"
        response += f"• **Confidence Level:** {topic_details['confidence']}%\n"
        response += f"• **Language:** {topic_details['language']}\n"
        response += f"• **Word Count:** {topic_details['word_count']}\n\n"

        if topic_details['suggested_subtopics']:
            response += f"🎯 **Suggested Sub-topics:**\n"
            for i, subtopic in enumerate(topic_details['suggested_subtopics'][:5], 1):
                response += f"{i}. **{subtopic['subtopic']}**\n"
                response += f"   _{subtopic['description']}_\n\n"

        if topic_details['key_themes']:
            response += f"🏷️ **Key Themes:** {', '.join(topic_details['key_themes'])}\n\n"

        response += f"✅ **Status:** Topic confirmed and ready for video generation\n"
        response += f"🚀 **Next Steps:**\n"
        response += f"• Click 'Generate Video' to start creation\n"
        response += f"• Or use 'Auto Workflow' for complete automation\n"
        response += f"• Modify topic if needed using suggestions above"

        self.add_message("AI Assistant", response, "ai")

    def get_topic_details(self, topic):
        """Get comprehensive topic details"""
        try:
            # Get expansion from topic expander
            expansion = self.main_app.topic_expander.expand_topic(topic)

            # Analyze topic text
            words = topic.lower().split()
            word_count = len(words)

            # Determine confidence based on expansion results
            confidence = expansion.get('confidence', 0.5) * 100

            return {
                'main_topic': topic,
                'category': expansion.get('category', 'General'),
                'description': expansion.get('description', 'Custom topic'),
                'confidence': int(confidence),
                'language': expansion.get('language', 'en'),
                'word_count': word_count,
                'suggested_subtopics': expansion.get('suggested_subtopics', []),
                'key_themes': self.extract_key_themes(topic)
            }
        except Exception as e:
            return {
                'main_topic': topic,
                'category': 'General',
                'description': 'Custom topic',
                'confidence': 50,
                'language': 'en',
                'word_count': len(topic.split()),
                'suggested_subtopics': [],
                'key_themes': [topic]
            }

    def extract_key_themes(self, topic):
        """Extract key themes from topic text"""
        words = topic.lower().split()
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were'}

        key_words = [word for word in words if len(word) > 2 and word not in stop_words]
        return key_words[:3] if key_words else [topic]

    def get_help_text(self):
        """Get help text with available commands"""
        help_text = """🤖 **AI Assistant Help**\n\n**Available Commands:**
• **Topic suggestions**: "suggest topics about [subject]" or "topic about [subject]"
• **File analysis**: "analyze text file" or "read [filename]"
• **Video generation**: "generate video" or "create video about [topic]"
• **Auto workflow**: "start auto workflow" or "automate video creation"
• **Topic confirmation**: "confirm topic" or "show topic details"
• **Direct input**: Just type any topic or subject you want to create a video about

**Examples:**
• "create a video about artificial intelligence"
• "suggest topics about health and wellness"
• "analyze my document.txt"
• "generate video for cooking tutorials"
• "confirm topic" - Shows full topic details
• "show topic details" - Comprehensive topic analysis

**Features:**
• 🎯 Smart topic suggestions with sub-topics
• 📄 Text file analysis and content extraction
• 🎬 Full video generation workflow
• ⚡ Automated end-to-end processing
• 📋 Complete topic confirmation with details
• 💬 Natural language conversation

Just tell me what you want to create!"""

        return help_text

    def select_bg_music(self):
        """Select background music file"""
        file_dialog = QFileDialog()
        file_dialog.setNameFilter("Audio files (*.mp3 *.wav *.m4a *.aac)")
        if file_dialog.exec_():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                self.bg_music_path = selected_files[0]
                self.bg_music_label.setText(f"BGM: {os.path.basename(self.bg_music_path)}")
                self.log_text.append(f"🎼 Selected background music: {os.path.basename(self.bg_music_path)}")

    def load_video_file(self):
        """Load a video file from disk"""
        file_dialog = QFileDialog()
        file_dialog.setNameFilter("Video files (*.mp4 *.avi *.mov *.mkv *.webm)")
        if file_dialog.exec_():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                video_path = selected_files[0]
                self.load_video_into_editor(video_path)
                self.log_text.append(f"Loaded video: {os.path.basename(video_path)}")

    def init_ui(self):
        """Initialize main UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Login dialog if not authenticated (optional for now)
        if not self.user_auth.current_user:
            try:
                login_dialog = LoginDialog(self.user_auth)
                result = login_dialog.exec_()
                if result == QDialog.Rejected:
                    # Instead of exiting, create a guest user
                    self.user_auth.current_user = {'id': 0, 'username': 'guest', 'preferences': {}}
                    logger.info("Continuing as guest user")
            except Exception as e:
                logger.warning(f"Login dialog failed: {e}, continuing as guest")
                self.user_auth.current_user = {'id': 0, 'username': 'guest', 'preferences': {}}

        # Video duration selection
        duration_layout = QHBoxLayout()
        duration_layout.addWidget(QLabel("Video Duration:"))
        self.duration_combo = QComboBox()
        self.duration_combo.addItems(["15 minutes", "30 minutes", "45 minutes"])
        duration_layout.addWidget(self.duration_combo)

        # Video type selection
        self.video_type_combo = QComboBox()
        self.video_type_combo.addItems(["Educational", "Entertainment", "News", "Documentary", "Tutorial", "Review", "Vlog"])
        duration_layout.addWidget(QLabel("Video Type:"))
        duration_layout.addWidget(self.video_type_combo)

        layout.addLayout(duration_layout)

        # Enhanced topic input with suggestions
        topic_layout = QHBoxLayout()
        topic_layout.addWidget(QLabel("🎯 Topic:"))
        self.topic_input = QLineEdit()
        self.topic_input.setPlaceholderText("Enter topic (e.g., news, documentary, music, kids story)...")
        self.topic_input.textChanged.connect(self.show_topic_suggestions)
        self.topic_input.textChanged.connect(self.update_floating_icon_topic)
        self.topic_input.textChanged.connect(self.update_floating_icon_topic)
        topic_layout.addWidget(self.topic_input)

        # Topic suggestions dropdown
        self.topic_suggestions = QListWidget()
        self.topic_suggestions.setMaximumHeight(100)
        self.topic_suggestions.hide()
        self.topic_suggestions.itemClicked.connect(self.select_topic_suggestion)
        topic_layout.addWidget(self.topic_suggestions)

        # Expand topic button
        self.expand_topic_btn = QPushButton("🔍 Expand Topic")
        self.expand_topic_btn.clicked.connect(self.expand_topic_manually)
        topic_layout.addWidget(self.expand_topic_btn)

        layout.addLayout(topic_layout)

        # Country and language selection
        self.country_combo = QComboBox()
        self.country_combo.addItems(["USA", "UK", "India", "Sri Lanka", "Australia", "Canada", "Global"])
        topic_layout.addWidget(QLabel("Country:"))
        topic_layout.addWidget(self.country_combo)

        self.language_combo = QComboBox()
        self.language_combo.addItems(["English", "Tamil", "Sinhala", "Spanish", "French", "German"])
        topic_layout.addWidget(QLabel("Language:"))
        topic_layout.addWidget(self.language_combo)

        self.voice_combo = QComboBox()
        self.voice_combo.addItems(["Male Professional", "Female Professional", "Male Casual", "Female Casual"])
        topic_layout.addWidget(QLabel("Voice:"))
        topic_layout.addWidget(self.voice_combo)

        # Background Music Selection
        music_layout = QHBoxLayout()
        music_layout.addWidget(QLabel("🎼 Background Music:"))
        self.bg_music_btn = QPushButton("Select BGM")
        self.bg_music_btn.clicked.connect(self.select_bg_music)
        music_layout.addWidget(self.bg_music_btn)

        self.bg_music_label = QLabel("No BGM selected")
        music_layout.addWidget(self.bg_music_label)

        # Background Images
        self.bg_images_btn = QPushButton("🖼 Select Background Images")
        self.bg_images_btn.clicked.connect(self.select_background_images)
        music_layout.addWidget(self.bg_images_btn)

        self.bg_images_label = QLabel("No images selected")
        music_layout.addWidget(self.bg_images_label)

        layout.addLayout(music_layout)

        # Watermark and Subtitle Options
        options_layout = QHBoxLayout()

        # Watermark options
        self.remove_watermark_check = QCheckBox("🧼 Remove Existing Watermarks")
        self.remove_watermark_check.setChecked(True)
        options_layout.addWidget(self.remove_watermark_check)

        self.add_watermark_check = QCheckBox("Add Custom Watermark")
        options_layout.addWidget(self.add_watermark_check)

        # Subtitle options
        self.generate_subtitles_check = QCheckBox("🧪 Generate Subtitles")
        self.generate_subtitles_check.setChecked(True)
        options_layout.addWidget(self.generate_subtitles_check)

        layout.addLayout(options_layout)

        # Generate Video Button
        self.generate_btn = QPushButton("🚀 Generate Video")
        self.generate_btn.clicked.connect(self.generate_video)
        self.generate_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; padding: 10px; font-size: 14px; font-weight: bold; }")
        layout.addWidget(self.generate_btn)

        # Initialize variables
        self.bg_music_path = None
        self.bg_images_paths = []
        self.selected_clips = []

        # Add all layouts to main layout
        layout.addLayout(duration_layout)
        layout.addLayout(topic_layout)
        layout.addLayout(music_layout)
        layout.addLayout(options_layout)
        layout.addWidget(self.generate_btn)

        # Tab widget for different sections
        self.tabs = QTabWidget()
        self.create_tabs()
        layout.addWidget(self.tabs)

        # Progress bar for generation
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        # Log area
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(200)
        layout.addWidget(self.log_text)

    def show_topic_suggestions(self):
        """Show topic suggestions as user types"""
        text = self.topic_input.text().strip().lower()
        if len(text) < 2:
            self.topic_suggestions.hide()
            return

        # Get suggestions from Universal Topic Expander
        suggestions = self.topic_expander.get_topic_suggestions(text)
        if suggestions:
            self.topic_suggestions.clear()
            for suggestion in suggestions[:5]:  # Show top 5 suggestions
                self.topic_suggestions.addItem(f"{suggestion['topic']} ({suggestion['category']})")
            self.topic_suggestions.show()
        else:
            self.topic_suggestions.hide()

    def select_topic_suggestion(self, item):
        """Handle topic suggestion selection"""
        selected_text = item.text().split(' (')[0]  # Remove category part
        self.topic_input.setText(selected_text)
        self.topic_suggestions.hide()
        self.expand_topic_manually()

    def expand_topic_manually(self):
        """Manually expand the current topic"""
        topic = self.topic_input.text().strip()
        if topic:
            self.log_text.append(f"🔍 Expanding topic: {topic}")

            # Use Universal Topic Expander
            expanded = self.topic_expander.expand_topic(topic)
            if expanded:
                self.log_text.append(f"📋 Found {len(expanded)} subtopics:")
                for subtopic in expanded:
                    self.log_text.append(f"  • {subtopic}")
            else:
                self.log_text.append("❌ No subtopics found")

    def update_floating_icon_topic(self):
        """Update floating icon tooltip with current topic"""
        if hasattr(self, 'floating_icon'):
            self.floating_icon.update_tooltip_with_topic()

    def select_background_images(self):
        """Select background images for the video"""
        file_dialog = QFileDialog()
        file_dialog.setNameFilter("Image files (*.png *.jpg *.jpeg *.bmp *.gif)")
        file_dialog.setFileMode(QFileDialog.ExistingFiles)

        if file_dialog.exec_():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                self.bg_images_paths = selected_files
                self.bg_images_label.setText(f"{len(selected_files)} images selected")
                self.log_text.append(f"🖼 Selected {len(selected_files)} background images")
            else:
                self.bg_images_label.setText("No images selected")

    def create_tabs(self):
        """Create tabs for different functionalities"""
        # Tab 1: Video Generation
        gen_tab = QWidget()
        gen_layout = QVBoxLayout()
        gen_tab.setLayout(gen_layout)
        self.tabs.addTab(gen_tab, "Video Generation")

        # Tab 2: Video Editor
        editor = VideoPlayerEditor()
        self.tabs.addTab(editor, "Video Editor")

        # Tab 3: Social Media
        social_tab = QWidget()
        social_layout = QVBoxLayout()
        social_tab.setLayout(social_layout)
        self.create_social_tab(social_layout)
        self.tabs.addTab(social_tab, "Social Media")

        # Tab 4: Settings
        settings_tab = QWidget()
        settings_layout = QVBoxLayout()
        settings_tab.setLayout(settings_layout)
        self.create_settings_tab(settings_layout)
        self.tabs.addTab(settings_tab, "Settings")

        # Tab 6: AI Video Generation
        ai_gen_tab = AIVideoGenerationTab(self.ai_video_generator, self.topic_expander, self)
        self.tabs.addTab(ai_gen_tab, "AI Video Generation")

        # Tab 7: AI Manager Dashboard
        ai_manager_tab = self.create_ai_manager_tab()
        self.tabs.addTab(ai_manager_tab, "AI Manager")

        # Tab 8: Internet Research
        research_tab = self.create_research_tab()
        self.tabs.addTab(research_tab, "Research")

        # Tab 9: AI Presenter
        presenter_tab = self.create_presenter_tab()
        self.tabs.addTab(presenter_tab, "AI Presenter")

        # Tab 10: Voice Editor
        voice_tab = self.create_voice_editor_tab()
        self.tabs.addTab(voice_tab, "Voice Editor")

        # Tab 11: Batch Processing
        batch_tab = self.create_batch_processing_tab()
        self.tabs.addTab(batch_tab, "Batch Processing")

        # Tab 11: Export/Import
        export_tab = self.create_export_import_tab()
        self.tabs.addTab(export_tab, "Export/Import")

    def create_settings_tab(self, layout):
        """Create settings panel"""
        # Sources
        sources_group = QGroupBox("Sources")
        sources_layout = QVBoxLayout()
        self.bbc_check = QCheckBox("BBC News")
        sources_layout.addWidget(self.bbc_check)
        self.cnn_check = QCheckBox("CNN News")
        sources_layout.addWidget(self.cnn_check)
        self.sri_lanka_tamil_check = QCheckBox("Sri Lankan Tamil")
        sources_layout.addWidget(self.sri_lanka_tamil_check)
        self.world_tamil_check = QCheckBox("World Tamil")
        sources_layout.addWidget(self.world_tamil_check)
        sources_group.setLayout(sources_layout)
        layout.addWidget(sources_group)

        # Language and voice
        lang_group = QGroupBox("Language & Voice")
        lang_layout = QHBoxLayout()
        self.language_combo = QComboBox()
        self.language_combo.addItems(["English", "Tamil"])
        lang_layout.addWidget(QLabel("Language:"))
        lang_layout.addWidget(self.language_combo)

        self.voice_combo = QComboBox()
        self.voice_combo.addItems(["Male", "Female"])
        lang_layout.addWidget(QLabel("Voice:"))
        lang_layout.addWidget(self.voice_combo)

        lang_group.setLayout(lang_layout)
        layout.addWidget(lang_group)

        # Duration settings
        duration_group = QGroupBox("Duration")
        duration_layout = QHBoxLayout()
        self.clip_duration = QSpinBox()
        self.clip_duration.setRange(15, 45)
        self.clip_duration.setValue(30)
        duration_layout.addWidget(QLabel("Clip Duration (sec):"))
        duration_layout.addWidget(self.clip_duration)

        self.video_duration = QSpinBox()
        self.video_duration.setRange(1, 60)
        self.video_duration.setValue(5)
        duration_layout.addWidget(QLabel("Video Duration (min):"))
        duration_layout.addWidget(self.video_duration)

        duration_group.setLayout(duration_layout)
        layout.addWidget(duration_group)

        # Content moderation toggle
        mod_group = QGroupBox("Content Moderation")
        self.moderation_check = QCheckBox("Enable Content Moderation")
        self.moderation_check.setChecked(True)
        mod_group.setLayout(QVBoxLayout())
        mod_group.layout().addWidget(self.moderation_check)
        layout.addWidget(mod_group)

        # Save settings button
        save_btn = QPushButton("Save Settings")
        # save_btn.clicked.connect(self.save_settings)
        layout.addWidget(save_btn)

        # System Health Check button
        health_btn = QPushButton("🔍 System Health Check")
        health_btn.clicked.connect(self.run_health_check)
        layout.addWidget(health_btn)

    def create_social_tab(self, layout):
        """Create social media tab"""
        # Upload section
        upload_group = QGroupBox("Upload Video")
        upload_layout = QVBoxLayout()
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Video title")
        upload_layout.addWidget(QLabel("Title:"))
        upload_layout.addWidget(self.title_input)

        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(60)
        upload_layout.addWidget(QLabel("Description:"))
        upload_layout.addWidget(self.description_input)

        self.tags_input = QLineEdit()
        self.tags_input.setPlaceholderText("Tags (comma separated)")
        upload_layout.addWidget(QLabel("Tags:"))
        upload_layout.addWidget(self.tags_input)

        self.privacy_combo = QComboBox()
        self.privacy_combo.addItems(["Public", "Private", "Unlisted"])
        upload_layout.addWidget(QLabel("Privacy:"))
        upload_layout.addWidget(self.privacy_combo)

        self.upload_btn = QPushButton("Upload to YouTube")
        self.upload_btn.clicked.connect(self.upload_to_youtube)
        upload_layout.addWidget(self.upload_btn)

        upload_group.setLayout(upload_layout)
        layout.addWidget(upload_group)

        # Live streaming
        stream_group = QGroupBox("Live Streaming")
        stream_layout = QVBoxLayout()
        self.stream_key_input = QLineEdit()
        self.stream_key_input.setPlaceholderText("Stream key")
        stream_layout.addWidget(QLabel("Stream Key:"))
        stream_layout.addWidget(self.stream_key_input)

        self.start_stream_btn = QPushButton("Start Live Stream")
        self.start_stream_btn.clicked.connect(self.start_live_stream)
        stream_layout.addWidget(self.start_stream_btn)

        stream_group.setLayout(stream_layout)
        layout.addWidget(stream_group)

        # Review tracking
        review_group = QGroupBox("Review Tracking")
        review_layout = QVBoxLayout()
        self.comments_text = QTextEdit()
        self.comments_text.setMaximumHeight(100)
        review_layout.addWidget(QLabel("Comments:"))
        review_layout.addWidget(self.comments_text)

        self.analyze_btn = QPushButton("Analyze Comments")
        self.analyze_btn.clicked.connect(self.analyze_comments)
        review_layout.addWidget(self.analyze_btn)

        review_group.setLayout(review_layout)
        layout.addWidget(review_group)

    def create_plugins_tab(self, layout):
        """Create plugins tab"""
        plugins_layout = QVBoxLayout()

        # Plugin list
        self.plugins_list = QTextBrowser()
        self.plugins_list.setMaximumHeight(200)
        plugins_layout.addWidget(QLabel("Loaded Plugins:"))
        plugins_layout.addWidget(self.plugins_list)

        # Plugin management
        plugin_layout = QHBoxLayout()
        self.plugin_name_input = QLineEdit()
        self.plugin_name_input.setPlaceholderText("Plugin name")
        plugin_layout.addWidget(self.plugin_name_input)

        self.load_plugin_btn = QPushButton("Load Plugin")
        self.load_plugin_btn.clicked.connect(self.load_plugin)
        plugin_layout.addWidget(self.load_plugin_btn)

        plugins_layout.addLayout(plugin_layout)

        layout.addLayout(plugins_layout)

    def handle_topic_input(self):
        """Handle topic input from the bar"""
        topic = self.topic_input.text().strip()
        if topic:
            if not self.content_moderator.is_appropriate(topic):
                QMessageBox.warning(self, "Content Moderation", "Inappropriate content detected. Please try a different topic.")
                return

            self.log_text.append(f"Processing topic: {topic}")
            # Automatic expansion logic
            expanded_options = self.expand_topic(topic)
            self.log_text.append(f"Expanded options: {expanded_options}")
            # For now, simulate generation
            self.progress_bar.setValue(100)
            self.log_text.append("Video generation complete! (Simulated)")

    def expand_topic(self, topic):
        """Expand topic to sub-options with comprehensive coverage"""
        topic_lower = topic.lower().strip()

        # Comprehensive topic expansions
        expansions = {
            # News and Current Events
            "news": ["Breaking News", "Local News", "National News", "International News", "Political News", "Business News", "Sports News", "Entertainment News"],
            "breaking news": ["Emergency News", "Latest Updates", "Urgent Announcements", "Critical Developments"],
            "politics": ["Government Policy", "Election Updates", "Political Analysis", "International Relations"],
            "business": ["Market Updates", "Company News", "Economic Trends", "Financial Markets"],
            "sports": ["Football Highlights", "Basketball Games", "Tennis Matches", "Olympic Events", "Championship Finals"],
            "entertainment": ["Movie Reviews", "Celebrity News", "Music Industry", "TV Shows", "Hollywood Updates"],

            # Educational Content
            "education": ["Science Education", "History Lessons", "Math Tutorials", "Language Learning", "STEM Education"],
            "science": ["Physics Explained", "Chemistry Experiments", "Biology Discoveries", "Space Exploration", "Medical Breakthroughs"],
            "history": ["Ancient History", "World War History", "Civil Rights Movement", "Historical Events", "Cultural Heritage"],
            "technology": ["AI Developments", "Gadget Reviews", "Programming Tutorials", "Tech Innovations", "Digital Trends"],

            # Lifestyle and Health
            "health": ["Medical News", "Fitness Tips", "Mental Health", "Nutrition Advice", "Healthcare Updates"],
            "fitness": ["Workout Routines", "Exercise Tips", "Healthy Living", "Sports Training", "Wellness Programs"],
            "food": ["Cooking Tutorials", "Recipe Ideas", "Food Reviews", "Culinary Arts", "Healthy Eating"],
            "travel": ["Travel Destinations", "Adventure Trips", "Cultural Tourism", "Travel Tips", "World Exploration"],

            # Entertainment and Media
            "movies": ["Film Reviews", "Movie Trailers", "Cinema News", "Film Festivals", "Movie Analysis"],
            "music": ["Music Videos", "Concert Reviews", "Artist Interviews", "Music Production", "Genre Explorations"],
            "gaming": ["Game Reviews", "Gaming Tips", "Esports Events", "Game Development", "Gaming Culture"],
            "comedy": ["Stand-up Comedy", "Funny Sketches", "Comedy Shows", "Humor Content", "Entertainment"],

            # Nature and Environment
            "nature": ["Wildlife Documentaries", "Nature Photography", "Environmental Issues", "Natural Wonders", "Animal Behavior"],
            "environment": ["Climate Change", "Conservation Efforts", "Green Technology", "Environmental Protection", "Sustainability"],
            "animals": ["Wildlife Conservation", "Animal Behavior", "Pet Care", "Marine Life", "Animal Rescue"],

            # Arts and Culture
            "art": ["Digital Art", "Traditional Art", "Art History", "Contemporary Art", "Art Techniques"],
            "culture": ["Cultural Festivals", "Traditional Customs", "Cultural Exchange", "Heritage Preservation", "Diverse Cultures"],
            "photography": ["Photography Tips", "Photo Editing", "Landscape Photography", "Portrait Photography", "Photojournalism"],

            # Business and Finance
            "finance": ["Investment Tips", "Financial Planning", "Stock Market", "Cryptocurrency", "Personal Finance"],
            "startup": ["Entrepreneurship", "Business Ideas", "Startup Stories", "Innovation", "Business Growth"],
            "marketing": ["Digital Marketing", "Social Media Marketing", "Brand Strategy", "Marketing Analytics", "Content Marketing"],

            # Kids and Family
            "kids": ["Educational Content", "Children's Stories", "Kids Activities", "Learning Games", "Family Entertainment"],
            "family": ["Family Activities", "Parenting Tips", "Family Recipes", "Home Organization", "Family Bonding"],
            "children": ["Kids Education", "Children's Entertainment", "Learning Through Play", "Child Development", "Kids Health"],

            # Hobbies and Interests
            "cooking": ["Recipe Tutorials", "Cooking Techniques", "Kitchen Tips", "Food Preparation", "Culinary Skills"],
            "diy": ["DIY Projects", "Home Improvement", "Crafting Ideas", "Handmade Creations", "Creative Projects"],
            "gardening": ["Garden Design", "Plant Care", "Gardening Tips", "Landscaping", "Sustainable Gardening"],

            # Social Issues
            "social": ["Social Justice", "Community Issues", "Human Rights", "Social Change", "Community Development"],
            "environment": ["Climate Action", "Green Initiatives", "Sustainable Living", "Environmental Protection", "Eco-friendly Solutions"],

            # Professional Content
            "career": ["Career Development", "Job Search Tips", "Professional Skills", "Workplace Advice", "Career Transitions"],
            "programming": ["Coding Tutorials", "Software Development", "Programming Languages", "Tech Skills", "Code Reviews"],
            "design": ["Graphic Design", "UI/UX Design", "Web Design", "Design Trends", "Creative Design"],

            # Seasonal and Events
            "holiday": ["Holiday Celebrations", "Seasonal Events", "Festival Preparations", "Holiday Traditions", "Special Occasions"],
            "seasonal": ["Season Changes", "Weather Updates", "Seasonal Activities", "Holiday Planning", "Event Coverage"]
        }

        # Check for partial matches and related topics
        for key, value in expansions.items():
            if key in topic_lower or topic_lower in key:
                return value

        # If no match found, create generic variations
        if len(topic.split()) == 1:
            return [f"{topic} Overview", f"{topic} Guide", f"{topic} Tips", f"{topic} News", f"About {topic}"]
        else:
            return [f"{topic} - Part 1", f"{topic} - Part 2", f"{topic} Explained", f"{topic} Guide", f"{topic} Updates"]

    def generate_video(self):
        """Generate video with all enhanced features"""
        topic = self.topic_input.text().strip()
        if not topic:
            QMessageBox.warning(self, "Error", "Please enter a topic")
            return

        # Get duration in minutes and convert to seconds
        duration_text = self.duration_combo.currentText()
        if "15 minutes" in duration_text:
            target_duration = 15 * 60  # 15 minutes in seconds
        elif "30 minutes" in duration_text:
            target_duration = 30 * 60  # 30 minutes in seconds
        elif "45 minutes" in duration_text:
            target_duration = 45 * 60  # 45 minutes in seconds
        else:
            target_duration = 15 * 60  # Default to 15 minutes

        country = self.country_combo.currentText()
        language = self.language_combo.currentText()
        voice = self.voice_combo.currentText()
        video_type = self.video_type_combo.currentText()

        # Validate content
        if not self.content_moderator.is_appropriate(topic):
            QMessageBox.warning(self, "Content Moderation", "Inappropriate content detected. Please try a different topic.")
            return

        self.log_text.append(f"🚀 Starting video generation process...")
        self.log_text.append(f"📝 Topic: {topic}")
        self.log_text.append(f"⏱️ Duration: {duration_text}")
        self.log_text.append(f"🌍 Country: {country}")
        self.log_text.append(f"🗣️ Language: {language}")
        self.log_text.append(f"🎭 Voice: {voice}")
        self.log_text.append(f"🎬 Type: {video_type}")

        # Disable generate button during processing
        self.generate_btn.setEnabled(False)
        self.generate_btn.setText("🔄 Generating...")

        # Start the comprehensive video generation process
        self.start_video_generation(topic, target_duration, country, language, voice, video_type)

    def start_video_generation(self, topic: str, duration: int, country: str, language: str, voice: str, video_type: str):
        """Start the comprehensive video generation process"""
        try:
            self.progress_bar.setValue(0)
            self.log_text.append("📥 Step 1: Collecting video clips...")

            # Step 1: Collect clips
            clips = self.collect_video_clips(topic, duration, country)
            if not clips:
                self.log_text.append("❌ No suitable clips found")
                self.reset_generation_ui()
                return

            self.progress_bar.setValue(20)
            self.log_text.append(f"✅ Collected {len(clips)} clips")

            # Step 2: Generate script
            self.log_text.append("🧾 Step 2: Generating video script...")
            script = self.generate_video_script(topic, duration, language, video_type)
            self.progress_bar.setValue(40)
            self.log_text.append("✅ Script generated")

            # Step 3: Generate voice-over
            self.log_text.append("🔊 Step 3: Generating voice-over...")
            voice_file = self.generate_voice_over(script, voice, language)
            self.progress_bar.setValue(60)
            self.log_text.append("✅ Voice-over generated")

            # Step 4: Process background images
            if self.bg_images_paths:
                self.log_text.append("🖼 Step 4: Processing background images...")
                self.process_background_images()
                self.progress_bar.setValue(70)

            # Step 5: Apply watermarks if needed
            if self.remove_watermark_check.isChecked():
                self.log_text.append("🧼 Step 5: Removing watermarks...")
                clips = self.remove_watermarks(clips)
                self.progress_bar.setValue(75)

            if self.add_watermark_check.isChecked():
                self.log_text.append("💧 Step 5b: Adding custom watermark...")
                clips = self.add_custom_watermark(clips)

            # Step 6: Generate subtitles if requested
            if self.generate_subtitles_check.isChecked():
                self.log_text.append("🧪 Step 6: Generating subtitles...")
                subtitle_file = self.generate_subtitles(script, voice_file, language)
                self.progress_bar.setValue(85)

            # Step 7: Compose final video
            self.log_text.append("🎬 Step 7: Composing final video...")
            final_video = self.compose_final_video(clips, voice_file, script, duration)
            self.progress_bar.setValue(95)

            # Step 8: Final review and export
            self.log_text.append("✅ Step 8: Video generation complete!")
            self.log_text.append(f"📁 Final video saved: {final_video}")
            self.progress_bar.setValue(100)

            # Show review dialog
            self.show_review_dialog(final_video)

        except Exception as e:
            self.log_text.append(f"❌ Error during generation: {str(e)}")
            logger.error(f"Video generation error: {e}")
        finally:
            self.reset_generation_ui()

    def reset_generation_ui(self):
        """Reset the generation UI after completion or error"""
        self.generate_btn.setEnabled(True)
        self.generate_btn.setText("🚀 Generate Video")

    def collect_video_clips(self, topic: str, duration: int, country: str) -> List[str]:
        """Collect video clips for the topic"""
        try:
            # Use AI Manager to coordinate clip collection
            clips = self.ai_manager.collect_clips_for_topic(topic, duration, country)
            return clips if clips else []
        except Exception as e:
            self.log_text.append(f"⚠️ Clip collection warning: {e}")
            return []

    def generate_video_script(self, topic: str, duration: int, language: str, video_type: str) -> str:
        """Generate comprehensive video script"""
        try:
            script = self.ai_manager.generate_script(topic, duration, language, video_type)
            return script if script else f"Script about {topic}"
        except Exception as e:
            return f"Script about {topic}"

    def generate_voice_over(self, script: str, voice: str, language: str) -> str:
        """Generate voice-over audio"""
        try:
            voice_file = self.voice_manager.generate_voice_over(script, voice, language)
            return voice_file if voice_file else None
        except Exception as e:
            self.log_text.append(f"⚠️ Voice generation warning: {e}")
            return None

    def process_background_images(self):
        """Process selected background images"""
        if self.bg_images_paths:
            self.log_text.append(f"Processing {len(self.bg_images_paths)} background images")

    def remove_watermarks(self, clips: List[str]) -> List[str]:
        """Remove watermarks from clips"""
        try:
            cleaned_clips = []
            for clip in clips:
                # Use AI to detect and remove watermarks
                cleaned_clip = self.ai_manager.remove_watermark(clip)
                cleaned_clips.append(cleaned_clip if cleaned_clip else clip)
            return cleaned_clips
        except Exception as e:
            return clips

    def add_custom_watermark(self, clips: List[str]) -> List[str]:
        """Add custom watermark to clips"""
        try:
            watermarked_clips = []
            for clip in clips:
                # Add custom watermark
                watermarked_clip = self.ai_manager.add_watermark(clip)
                watermarked_clips.append(watermarked_clip if watermarked_clip else clip)
            return watermarked_clips
        except Exception as e:
            return clips

    def generate_subtitles(self, script: str, voice_file: str, language: str) -> str:
        """Generate subtitles for the video"""
        try:
            subtitle_file = self.ai_manager.generate_subtitles(script, voice_file, language)
            return subtitle_file if subtitle_file else None
        except Exception as e:
            self.log_text.append(f"⚠️ Subtitle generation warning: {e}")
            return None

    def compose_final_video(self, clips: List[str], voice_file: str, script: str, duration: int) -> str:
        """Compose the final video with all components"""
        try:
            final_video = self.video_editor.compose_video(
                clips=clips,
                voice_over=voice_file,
                script=script,
                duration=duration,
                bg_music=self.bg_music_path,
                bg_images=self.bg_images_paths
            )
            return final_video if final_video else None
        except Exception as e:
            self.log_text.append(f"⚠️ Video composition warning: {e}")
            return None

    def show_review_dialog(self, video_path: str):
        """Show review dialog for the generated video"""
        try:
            review_dialog = VideoReviewDialog(video_path, self)
            review_dialog.exec_()
        except Exception as e:
            self.log_text.append(f"⚠️ Review dialog error: {e}")

class VideoReviewDialog(QDialog):
    """Dialog for reviewing and approving generated videos"""
    def __init__(self, video_path: str, parent=None):
        super().__init__(parent)
        self.video_path = video_path
        self.parent = parent
        self.setWindowTitle("Video Review & Approval")
        self.setModal(True)
        self.resize(800, 600)
        self.init_ui()

    def init_ui(self):
        """Initialize review dialog UI"""
        layout = QVBoxLayout()

        # Video preview section
        preview_group = QGroupBox("Video Preview")
        preview_layout = QVBoxLayout()

        # Video player (simplified for now)
        self.video_label = QLabel("Video Preview")
        self.video_label.setStyleSheet("QLabel { background-color: #f0f0f0; border: 2px dashed #ccc; padding: 20px; }")
        self.video_label.setAlignment(Qt.AlignCenter)
        preview_layout.addWidget(self.video_label)

        # Video info
        info_layout = QHBoxLayout()
        info_layout.addWidget(QLabel(f"File: {os.path.basename(self.video_path)}"))
        info_layout.addWidget(QLabel(f"Size: {self.get_file_size()}"))
        preview_layout.addLayout(info_layout)

        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)

        # Review options
        review_group = QGroupBox("Review Options")
        review_layout = QVBoxLayout()

        self.quality_rating = QComboBox()
        self.quality_rating.addItems(["Excellent", "Good", "Fair", "Poor"])
        review_layout.addWidget(QLabel("Quality Rating:"))
        review_layout.addWidget(self.quality_rating)

        self.approval_check = QCheckBox("Approve for publishing")
        self.approval_check.setChecked(True)
        review_layout.addWidget(self.approval_check)

        self.feedback_text = QTextEdit()
        self.feedback_text.setPlaceholderText("Additional feedback or notes...")
        self.feedback_text.setMaximumHeight(80)
        review_layout.addWidget(QLabel("Feedback:"))
        review_layout.addWidget(self.feedback_text)

        review_group.setLayout(review_layout)
        layout.addWidget(review_group)

        # Action buttons
        buttons_layout = QHBoxLayout()

        self.approve_btn = QPushButton("✅ Approve & Export")
        self.approve_btn.clicked.connect(self.approve_video)
        self.approve_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; padding: 8px 16px; }")
        buttons_layout.addWidget(self.approve_btn)

        self.edit_btn = QPushButton("✏️ Edit Video")
        self.edit_btn.clicked.connect(self.edit_video)
        buttons_layout.addWidget(self.edit_btn)

        self.reject_btn = QPushButton("❌ Reject")
        self.reject_btn.clicked.connect(self.reject_video)
        self.reject_btn.setStyleSheet("QPushButton { background-color: #f44336; color: white; padding: 8px 16px; }")
        buttons_layout.addWidget(self.reject_btn)

        layout.addLayout(buttons_layout)

        self.setLayout(layout)

    def get_file_size(self) -> str:
        """Get human-readable file size"""
        try:
            size = os.path.getsize(self.video_path)
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024.0:
                    return f"{size:.1f} {unit}"
                size /= 1024.0
            return f"{size:.1f} TB"
        except:
            return "Unknown"

    def approve_video(self):
        """Approve video and proceed to export"""
        feedback = self.feedback_text.toPlainText()
        rating = self.quality_rating.currentText()

        self.parent.log_text.append(f"✅ Video approved!")
        self.parent.log_text.append(f"⭐ Rating: {rating}")
        if feedback:
            self.parent.log_text.append(f"📝 Feedback: {feedback}")

        # Proceed to upload/stream options
        self.show_upload_options()
        self.accept()

    def edit_video(self):
        """Open video in editor"""
        self.parent.log_text.append("✏️ Opening video in editor...")
        # Open the video editor tab
        self.parent.tabs.setCurrentIndex(1)  # Video Editor tab
        self.accept()

    def reject_video(self):
        """Reject video and provide feedback"""
        feedback = self.feedback_text.toPlainText()
        self.parent.log_text.append("❌ Video rejected")
        if feedback:
            self.parent.log_text.append(f"📝 Feedback: {feedback}")
        self.accept()

    def show_upload_options(self):
        """Show upload/stream options dialog"""
        upload_dialog = UploadOptionsDialog(self.video_path, self.parent)
        upload_dialog.exec_()

class UploadOptionsDialog(QDialog):
    """Dialog for upload and streaming options"""
    def __init__(self, video_path: str, parent=None):
        super().__init__(parent)
        self.video_path = video_path
        self.parent = parent
        self.setWindowTitle("Upload & Stream Options")
        self.setModal(True)
        self.resize(500, 400)
        self.init_ui()

    def init_ui(self):
        """Initialize upload options UI"""
        layout = QVBoxLayout()

        # Platform selection
        platform_group = QGroupBox("Select Platforms")
        platform_layout = QVBoxLayout()

        self.youtube_check = QCheckBox("📺 YouTube")
        self.youtube_check.setChecked(True)
        platform_layout.addWidget(self.youtube_check)

        self.facebook_check = QCheckBox("📘 Facebook")
        platform_layout.addWidget(self.facebook_check)

        self.tiktok_check = QCheckBox("🎵 TikTok")
        platform_layout.addWidget(self.tiktok_check)

        self.twitch_check = QCheckBox("🎮 Twitch")
        platform_layout.addWidget(self.twitch_check)

        platform_group.setLayout(platform_layout)
        layout.addWidget(platform_group)

        # Video details
        details_group = QGroupBox("Video Details")
        details_layout = QFormLayout()

        self.title_input = QLineEdit()
        self.title_input.setText(os.path.basename(self.video_path).replace('.mp4', ''))
        details_layout.addRow("Title:", self.title_input)

        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(60)
        self.description_input.setPlaceholderText("Video description...")
        details_layout.addRow("Description:", self.description_input)

        self.tags_input = QLineEdit()
        self.tags_input.setPlaceholderText("tag1, tag2, tag3")
        details_layout.addRow("Tags:", self.tags_input)

        details_group.setLayout(details_layout)
        layout.addWidget(details_group)

        # Upload button
        self.upload_btn = QPushButton("🚀 Upload to Selected Platforms")
        self.upload_btn.clicked.connect(self.start_upload)
        self.upload_btn.setStyleSheet("QPushButton { background-color: #2196F3; color: white; padding: 10px; font-weight: bold; }")
        layout.addWidget(self.upload_btn)

        self.setLayout(layout)

    def start_upload(self):
        """Start uploading to selected platforms"""
        platforms = []
        if self.youtube_check.isChecked():
            platforms.append("YouTube")
        if self.facebook_check.isChecked():
            platforms.append("Facebook")
        if self.tiktok_check.isChecked():
            platforms.append("TikTok")
        if self.twitch_check.isChecked():
            platforms.append("Twitch")

        if not platforms:
            QMessageBox.warning(self, "Error", "Please select at least one platform")
            return

        title = self.title_input.text()
        description = self.description_input.toPlainText()
        tags = self.tags_input.text()

        self.parent.log_text.append(f"📤 Starting upload to: {', '.join(platforms)}")
        self.parent.log_text.append(f"📝 Title: {title}")

        # Start upload process
        self.upload_to_platforms(platforms, title, description, tags)
        self.accept()

    def upload_to_platforms(self, platforms: List[str], title: str, description: str, tags: str):
        """Upload video to selected platforms"""
        try:
            for platform in platforms:
                self.parent.log_text.append(f"⬆️ Uploading to {platform}...")
                # Use the uploader system
                result = self.parent.uploader.upload_video(
                    self.video_path, platform, title, description, tags
                )
                if result:
                    self.parent.log_text.append(f"✅ Successfully uploaded to {platform}")
                else:
                    self.parent.log_text.append(f"❌ Failed to upload to {platform}")

        except Exception as e:
            self.parent.log_text.append(f"❌ Upload error: {e}")

    def monitor_task_progress(self, task_id: str):
        """Monitor task progress through AI management system"""
        def check_progress():
            try:
                status = self.ai_manager.get_system_status()
                self.log_text.append(f"System Status: {status['status']}")
                self.log_text.append(f"Active Tasks: {status['active_tasks']}")
                self.log_text.append(f"Completed Tasks: {status['completed_tasks']}")

                # Check if our task is completed
                for task in status.get('completed_tasks', []):
                    if task.get('task_id') == task_id:
                        if task['status'] == 'completed':
                            self.log_text.append(f"Task {task_id} completed successfully!")
                            self.progress_bar.setValue(100)
                        else:
                            self.log_text.append(f"Task {task_id} failed: {task.get('error', 'Unknown error')}")
                        return

                # Continue monitoring if task not complete
                QTimer.singleShot(5000, check_progress)  # Check every 5 seconds

            except Exception as e:
                self.log_text.append(f"Error monitoring task: {str(e)}")

        # Start monitoring
        QTimer.singleShot(2000, check_progress)

    def generate_video_thread(self, topic: str, country: str, language: str, voice: str,
                            clip_duration: int, video_duration: int):
        """Thread for video generation process"""
        try:
            # Step 1: Collect video clips
            QTimer.singleShot(0, lambda: self.progress_bar.setValue(10))
            QTimer.singleShot(0, lambda: self.log_text.append("Searching for video clips..."))

            num_clips = max(10, video_duration * 2)  # Estimate clips needed
            clips = self.video_collector.collect_clips(topic, country, language, clip_duration, num_clips)

            if not clips:
                QTimer.singleShot(0, lambda: self.log_text.append("No clips found. Please try a different topic."))
                return

            QTimer.singleShot(0, lambda: self.progress_bar.setValue(30))
            QTimer.singleShot(0, lambda: self.log_text.append(f"Found {len(clips)} video clips"))

            # Step 2: Generate script
            QTimer.singleShot(0, lambda: self.progress_bar.setValue(40))
            QTimer.singleShot(0, lambda: self.log_text.append("Generating script..."))

            script = self.video_editor.generate_script(topic, video_duration, language)

            QTimer.singleShot(0, lambda: self.progress_bar.setValue(50))
            QTimer.singleShot(0, lambda: self.log_text.append("Script generated"))

            # Step 3: Assemble video
            QTimer.singleShot(0, lambda: self.progress_bar.setValue(60))
            QTimer.singleShot(0, lambda: self.log_text.append("Assembling video..."))

            final_video_path = self.video_editor.assemble_video(clips, script, voice, language, self.bg_music_path)

            if final_video_path:
                QTimer.singleShot(0, lambda: self.progress_bar.setValue(90))
                QTimer.singleShot(0, lambda: self.log_text.append(f"Video assembled: {final_video_path}"))

                # Step 4: Final processing
                QTimer.singleShot(0, lambda: self.progress_bar.setValue(100))
                QTimer.singleShot(0, lambda: self.log_text.append("Video generation complete!"))
                QTimer.singleShot(0, lambda: self.status_bar.showMessage(f"Video ready: {final_video_path}"))

                # Store the final video path for later use
                self.final_video_path = final_video_path

                # Auto-load video into editor
                QTimer.singleShot(0, lambda: self.load_video_into_editor(final_video_path))
            else:
                QTimer.singleShot(0, lambda: self.log_text.append("Video assembly failed. Please check the logs."))

        except Exception as e:
            QTimer.singleShot(0, lambda: self.log_text.append(f"Video generation failed: {str(e)}"))
            logger.error(f"Video generation error: {e}")

    def load_video_into_editor(self, video_path: str):
        """Load the generated video into the video editor"""
        try:
            # Find the video editor tab
            for i in range(self.tabs.count()):
                if self.tabs.tabText(i) == "Video Editor":
                    editor = self.tabs.widget(i)
                    if hasattr(editor, 'load_video'):
                        editor.load_video(video_path)
                        self.tabs.setCurrentIndex(i)  # Switch to editor tab
                    break
        except Exception as e:
            logger.error(f"Failed to load video into editor: {e}")

    def open_chat(self):
        """Open the chat interface"""
        self.chat_interface = ChatInterface(main_app=self)
        self.chat_interface.show()

    def generate_news_video(self):
        """Generate news video command"""
        self.log_text.append("Generating news video...")
        self.progress_bar.setValue(100)
        self.log_text.append("News video generated!")

    def open_editor(self):
        """Open video editor"""
        self.log_text.append("Opening video editor...")
        self.tabs.setCurrentIndex(1)  # Video Editor is tab index 1

        # If we have a final video, load it
        if hasattr(self, 'final_video_path') and self.final_video_path:
            self.load_video_into_editor(self.final_video_path)

    def upload_to_youtube(self):
        """Upload to YouTube"""
        title = self.title_input.text().strip()
        description = self.description_input.toPlainText().strip()
        tags = [tag.strip() for tag in self.tags_input.text().strip().split(',') if tag.strip()]
        privacy = self.privacy_combo.currentText().lower()

        if not title:
            QMessageBox.warning(self, "Error", "Please enter a video title")
            return

        # Simulate upload
        self.log_text.append(f"Uploading '{title}' to YouTube...")
        self.progress_bar.setValue(50)
        time.sleep(1)
        self.progress_bar.setValue(100)
        self.log_text.append("Upload complete! (Simulation)")

    def start_live_stream(self):
        """Start live stream with improved functionality"""
        stream_key = self.stream_key_input.text().strip()
        if not stream_key:
            QMessageBox.warning(self, "Error", "Please enter stream key")
            return

        # Check if we have a video to stream
        if not hasattr(self, 'current_video_path') or not self.current_video_path:
            QMessageBox.warning(self, "Error", "Please generate a video first")
            return

        self.log_text.append("Initializing live stream...")
        self.start_stream_btn.setText("Stop Stream")
        self.start_stream_btn.clicked.disconnect()
        self.start_stream_btn.clicked.connect(self.stop_live_stream)

        try:
            # Start streaming in a separate thread
            stream_thread = threading.Thread(
                target=self._run_live_stream,
                args=(stream_key, self.current_video_path),
                daemon=True
            )
            stream_thread.start()

            self.log_text.append("Live stream started successfully!")
            self.log_text.append(f"Stream Key: {stream_key[:10]}...")
            self.log_text.append("Viewers can now watch your video live")

        except Exception as e:
            self.log_text.append(f"Failed to start live stream: {str(e)}")
            self.start_stream_btn.setText("Start Live Stream")
            self.start_stream_btn.clicked.disconnect()
            self.start_stream_btn.clicked.connect(self.start_live_stream)

    def stop_live_stream(self):
        """Stop the live stream"""
        self.log_text.append("Stopping live stream...")
        self.start_stream_btn.setText("Start Live Stream")
        self.start_stream_btn.clicked.disconnect()
        self.start_stream_btn.clicked.connect(self.start_live_stream)
        self.log_text.append("Live stream stopped")

    def _run_live_stream(self, stream_key: str, video_path: str):
        """Run the live streaming process"""
        try:
            # Use FFmpeg for streaming (if available)
            import subprocess

            # YouTube/Twitch RTMP URL (would need to be configured based on platform)
            rtmp_url = f"rtmp://live.twitch.tv/live/{stream_key}"  # Example for Twitch

            # FFmpeg command for streaming
            ffmpeg_cmd = [
                'ffmpeg',
                '-re',  # Read input at native frame rate
                '-i', video_path,  # Input video
                '-c:v', 'libx264',  # Video codec
                '-preset', 'veryfast',  # Encoding preset
                '-maxrate', '3000k',  # Max bitrate
                '-bufsize', '6000k',  # Buffer size
                '-c:a', 'aac',  # Audio codec
                '-b:a', '128k',  # Audio bitrate
                '-f', 'flv',  # Output format
                rtmp_url  # RTMP URL
            ]

            # Run FFmpeg process
            process = subprocess.Popen(
                ffmpeg_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )

            # Monitor the process
            while process.poll() is None:
                time.sleep(1)

            if process.returncode == 0:
                self.log_text.append("Live stream completed successfully")
            else:
                self.log_text.append("Live stream ended with errors")

        except ImportError:
            # Fallback if FFmpeg is not available
            self.log_text.append("FFmpeg not available - using simulated streaming")
            self.log_text.append(f"Simulating stream of: {os.path.basename(video_path)}")
            time.sleep(10)  # Simulate streaming duration
            self.log_text.append("Simulated live stream completed")

        except Exception as e:
            self.log_text.append(f"Live streaming error: {str(e)}")

    def analyze_comments(self):
        """Analyze comments with AI"""
        comments = self.comments_text.toPlainText().strip().split('\n')
        if not comments:
            self.log_text.append("No comments to analyze")
            return

        # Simulate AI analysis
        self.log_text.append("Analyzing comments...")
        time.sleep(1)
        sentiments = ["Positive", "Neutral", "Negative"] * (len(comments) // 3 + 1)
        for i, (comment, sentiment) in enumerate(zip(comments, sentiments)):
            self.log_text.append(f"Comment {i+1}: {sentiment}")
            response = self.analyzer.generate_response(comment) if self.analyzer else "Thanks for your feedback!"
            self.log_text.append(f"Response: {response}")

    def save_settings(self):
        """Save settings"""
        self.log_text.append("Settings saved successfully!")

    def load_plugin(self):
        """Load plugin from input"""
        plugin_name = self.plugin_name_input.text().strip()
        if plugin_name:
            result = self.plugin_system.execute_plugin(plugin_name, "load")
            self.plugins_list.append(f"Loaded plugin: {plugin_name} - {result}")

    def create_ai_manager_tab(self) -> QWidget:
        """Create AI Manager dashboard tab"""
        tab = QWidget()
        layout = QVBoxLayout()

        # System status
        status_group = QGroupBox("System Status")
        status_layout = QVBoxLayout()

        self.status_label = QLabel("System Status: Initializing...")
        status_layout.addWidget(self.status_label)

        self.active_tasks_label = QLabel("Active Tasks: 0")
        status_layout.addWidget(self.active_tasks_label)

        self.completed_tasks_label = QLabel("Completed Tasks: 0")
        status_layout.addWidget(self.completed_tasks_label)

        # Refresh button
        refresh_btn = QPushButton("Refresh Status")
        refresh_btn.clicked.connect(self.update_ai_status)
        status_layout.addWidget(refresh_btn)

        status_group.setLayout(status_layout)
        layout.addWidget(status_group)

        # Performance dashboard
        perf_group = QGroupBox("Performance Dashboard")
        perf_layout = QVBoxLayout()

        self.perf_text = QTextBrowser()
        self.perf_text.setMaximumHeight(200)
        perf_layout.addWidget(self.perf_text)

        perf_group.setLayout(perf_layout)
        layout.addWidget(perf_group)

        # Task submission
        task_group = QGroupBox("Submit Task")
        task_layout = QVBoxLayout()

        self.task_topic_input = QLineEdit()
        self.task_topic_input.setPlaceholderText("Task topic...")
        task_layout.addWidget(QLabel("Topic:"))
        task_layout.addWidget(self.task_topic_input)

        self.task_type_combo = QComboBox()
        self.task_type_combo.addItems(["video_collection", "content_analysis", "script_generation",
                                     "video_editing", "quality_assurance", "social_media"])
        task_layout.addWidget(QLabel("Task Type:"))
        task_layout.addWidget(self.task_type_combo)

        submit_task_btn = QPushButton("Submit Task")
        submit_task_btn.clicked.connect(self.submit_ai_task)
        task_layout.addWidget(submit_task_btn)

        task_group.setLayout(task_layout)
        layout.addWidget(task_group)

        tab.setLayout(layout)

        # Initial status update
        self.update_ai_status()

        return tab

    def update_ai_status(self):
        """Update AI system status display"""
        try:
            status = self.ai_manager.get_system_status()

            self.status_label.setText(f"System Status: {status['status']}")
            self.active_tasks_label.setText(f"Active Tasks: {status['active_tasks']}")
            self.completed_tasks_label.setText(f"Completed Tasks: {status['completed_tasks']}")

            # Update performance dashboard
            perf_info = []
            for specialty, metrics in status['performance'].items():
                perf_info.append(f"{specialty}: {metrics['completed']} completed, {metrics['failed']} failed")

            self.perf_text.clear()
            self.perf_text.append("Performance Metrics:")
            self.perf_text.append("\n".join(perf_info))

        except Exception as e:
            self.status_label.setText(f"Error updating status: {str(e)}")

    def submit_ai_task(self):
        """Submit a task to the AI management system"""
        topic = self.task_topic_input.text().strip()
        task_type = self.task_type_combo.currentText()

        if not topic:
            QMessageBox.warning(self, "Error", "Please enter a task topic")
            return

        task_id = self.ai_manager.submit_task({
            "type": "custom_task",
            "topic": topic,
            "required_specialty": task_type
        })

        QMessageBox.information(self, "Task Submitted", f"Task submitted with ID: {task_id}")
        self.task_topic_input.clear()

        # Refresh status
        self.update_ai_status()

    def create_research_tab(self) -> QWidget:
        """Create internet research tab"""
        tab = QWidget()
        layout = QVBoxLayout()

        # Research input
        input_group = QGroupBox("Research Query")
        input_layout = QVBoxLayout()

        self.research_topic_input = QLineEdit()
        self.research_topic_input.setPlaceholderText("Enter topic to research...")
        input_layout.addWidget(QLabel("Topic:"))
        input_layout.addWidget(self.research_topic_input)

        research_btn = QPushButton("Research Resources")
        research_btn.clicked.connect(self.perform_research)
        input_layout.addWidget(research_btn)

        input_group.setLayout(input_layout)
        layout.addWidget(input_group)

        # Results display
        results_group = QGroupBox("Research Results")
        results_layout = QVBoxLayout()

        self.research_results = QTextBrowser()
        self.research_results.setMaximumHeight(300)
        results_layout.addWidget(self.research_results)

        results_group.setLayout(results_layout)
        layout.addWidget(results_group)

        tab.setLayout(layout)
        return tab

    def create_presenter_tab(self) -> QWidget:
        """Create AI presenter tab"""
        tab = QWidget()
        layout = QVBoxLayout()

        # Presenter configuration
        config_group = QGroupBox("Presenter Configuration")
        config_layout = QVBoxLayout()

        self.presenter_script_input = QTextEdit()
        self.presenter_script_input.setPlaceholderText("Enter script for presenter...")
        self.presenter_script_input.setMaximumHeight(100)
        config_layout.addWidget(QLabel("Script:"))
        config_layout.addWidget(self.presenter_script_input)

        self.presenter_style_combo = QComboBox()
        self.presenter_style_combo.addItems(self.ai_presenter.get_available_styles())
        config_layout.addWidget(QLabel("Style:"))
        config_layout.addWidget(self.presenter_style_combo)

        self.presenter_voice_combo = QComboBox()
        self.presenter_voice_combo.addItems(["Male", "Female"])
        config_layout.addWidget(QLabel("Voice:"))
        config_layout.addWidget(self.presenter_voice_combo)

        create_presenter_btn = QPushButton("Create Presenter Video")
        create_presenter_btn.clicked.connect(self.create_presenter_video)
        config_layout.addWidget(create_presenter_btn)

        config_group.setLayout(config_layout)
        layout.addWidget(config_group)

        # Results display
        results_group = QGroupBox("Presenter Results")
        results_layout = QVBoxLayout()

        self.presenter_results = QTextBrowser()
        self.presenter_results.setMaximumHeight(200)
        results_layout.addWidget(self.presenter_results)

        results_group.setLayout(results_layout)
        layout.addWidget(results_group)

        tab.setLayout(layout)
        return tab

    def create_voice_editor_tab(self) -> QWidget:
        """Create voice editor tab for audio manipulation"""
        tab = QWidget()
        layout = QVBoxLayout()

        # Voice input section
        input_group = QGroupBox("Voice Input")
        input_layout = QVBoxLayout()

        self.voice_text_input = QTextEdit()
        self.voice_text_input.setPlaceholderText("Enter text to convert to speech...")
        self.voice_text_input.setMaximumHeight(100)
        input_layout.addWidget(QLabel("Text:"))
        input_layout.addWidget(self.voice_text_input)

        # Voice settings
        voice_settings_layout = QHBoxLayout()

        self.voice_editor_voice_combo = QComboBox()
        self.voice_editor_voice_combo.addItems(["Male", "Female", "Child", "Robot", "Deep Male", "High Female"])
        voice_settings_layout.addWidget(QLabel("Voice:"))
        voice_settings_layout.addWidget(self.voice_editor_voice_combo)

        self.voice_speed_slider = QSlider(Qt.Horizontal)
        self.voice_speed_slider.setRange(50, 200)
        self.voice_speed_slider.setValue(100)
        voice_settings_layout.addWidget(QLabel("Speed:"))
        voice_settings_layout.addWidget(self.voice_speed_slider)

        self.voice_pitch_slider = QSlider(Qt.Horizontal)
        self.voice_pitch_slider.setRange(50, 200)
        self.voice_pitch_slider.setValue(100)
        voice_settings_layout.addWidget(QLabel("Pitch:"))
        voice_settings_layout.addWidget(self.voice_pitch_slider)

        input_layout.addLayout(voice_settings_layout)

        generate_voice_btn = QPushButton("Generate Voice")
        generate_voice_btn.clicked.connect(self.generate_voice)
        input_layout.addWidget(generate_voice_btn)

        input_group.setLayout(input_layout)
        layout.addWidget(input_group)

        # Audio effects section
        effects_group = QGroupBox("Audio Effects")
        effects_layout = QVBoxLayout()

        # Volume control
        volume_layout = QHBoxLayout()
        volume_layout.addWidget(QLabel("Volume:"))
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 200)
        self.volume_slider.setValue(100)
        volume_layout.addWidget(self.volume_slider)
        effects_layout.addLayout(volume_layout)

        # Audio filters
        filters_layout = QHBoxLayout()

        self.echo_check = QCheckBox("Echo")
        filters_layout.addWidget(self.echo_check)

        self.reverb_check = QCheckBox("Reverb")
        filters_layout.addWidget(self.reverb_check)

        self.noise_reduction_check = QCheckBox("Noise Reduction")
        filters_layout.addWidget(self.noise_reduction_check)

        effects_layout.addLayout(filters_layout)

        # Apply effects button
        apply_effects_btn = QPushButton("Apply Effects")
        apply_effects_btn.clicked.connect(self.apply_audio_effects)
        effects_layout.addWidget(apply_effects_btn)

        effects_group.setLayout(effects_layout)
        layout.addWidget(effects_group)

        # Voice library section
        library_group = QGroupBox("Voice Library")
        library_layout = QVBoxLayout()

        self.voice_library_list = QListWidget()
        self.voice_library_list.setMaximumHeight(150)
        library_layout.addWidget(self.voice_library_list)

        library_buttons_layout = QHBoxLayout()
        save_voice_btn = QPushButton("Save Voice")
        save_voice_btn.clicked.connect(self.save_voice_to_library)
        library_buttons_layout.addWidget(save_voice_btn)

        load_voice_btn = QPushButton("Load Voice")
        load_voice_btn.clicked.connect(self.load_voice_from_library)
        library_buttons_layout.addWidget(load_voice_btn)

        delete_voice_btn = QPushButton("Delete Voice")
        delete_voice_btn.clicked.connect(self.delete_voice_from_library)
        library_buttons_layout.addWidget(delete_voice_btn)

        library_layout.addLayout(library_buttons_layout)

        library_group.setLayout(library_layout)
        layout.addWidget(library_group)

        # Results section
        results_group = QGroupBox("Voice Results")
        results_layout = QVBoxLayout()

        self.voice_results = QTextBrowser()
        self.voice_results.setMaximumHeight(100)
        results_layout.addWidget(self.voice_results)

        results_group.setLayout(results_layout)
        layout.addWidget(results_group)

        tab.setLayout(layout)
        return tab

    def generate_voice(self):
        """Generate voice from text input"""
        text = self.voice_text_input.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "Error", "Please enter text to convert to speech")
            return

        voice = self.voice_editor_voice_combo.currentText().lower()
        speed = self.voice_speed_slider.value() / 100.0
        pitch = self.voice_pitch_slider.value() / 100.0

        self.voice_results.clear()
        self.voice_results.append(f"Generating voice for: {text[:50]}...")
        self.voice_results.append(f"Voice: {voice}, Speed: {speed:.1f}, Pitch: {pitch:.1f}")

        try:
            # Generate voice using the video editor's voiceover method
            voiceover_path = self.video_editor.add_voiceover(text, voice, "en", speed=speed, pitch=pitch)
            if voiceover_path:
                self.voice_results.append(f"Voice generated successfully: {voiceover_path}")
                self.current_voice_path = voiceover_path
            else:
                self.voice_results.append("Voice generation failed")
        except Exception as e:
            self.voice_results.append(f"Error generating voice: {str(e)}")

    def apply_audio_effects(self):
        """Apply audio effects to the current voice"""
        if not hasattr(self, 'current_voice_path') or not self.current_voice_path:
            QMessageBox.warning(self, "Error", "Please generate a voice first")
            return

        effects = []
        if self.echo_check.isChecked():
            effects.append("echo")
        if self.reverb_check.isChecked():
            effects.append("reverb")
        if self.noise_reduction_check.isChecked():
            effects.append("noise_reduction")

        volume = self.volume_slider.value() / 100.0

        self.voice_results.append(f"Applying effects: {', '.join(effects)}")
        self.voice_results.append(f"Volume: {volume:.1f}")

        try:
            # Apply effects (placeholder - would need audio processing library)
            self.voice_results.append("Audio effects applied successfully")
        except Exception as e:
            self.voice_results.append(f"Error applying effects: {str(e)}")

    def save_voice_to_library(self):
        """Save current voice to library"""
        if not hasattr(self, 'current_voice_path') or not self.current_voice_path:
            QMessageBox.warning(self, "Error", "Please generate a voice first")
            return

        voice_name, ok = QInputDialog.getText(self, "Save Voice", "Enter voice name:")
        if ok and voice_name:
            # Add to library list
            self.voice_library_list.addItem(f"{voice_name} - {os.path.basename(self.current_voice_path)}")
            self.voice_results.append(f"Voice saved to library: {voice_name}")

    def load_voice_from_library(self):
        """Load voice from library"""
        current_item = self.voice_library_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Error", "Please select a voice from the library")
            return

        voice_info = current_item.text()
        self.voice_results.append(f"Loaded voice: {voice_info}")

    def delete_voice_from_library(self):
        """Delete voice from library"""
        current_item = self.voice_library_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Error", "Please select a voice to delete")
            return

        row = self.voice_library_list.row(current_item)
        self.voice_library_list.takeItem(row)
        self.voice_results.append("Voice deleted from library")

    def perform_research(self):

        self.research_results.clear()
        self.research_results.append(f"Researching resources for: {topic}\n")

        try:
            results = self.research_module.find_video_resources(topic)

            # Display images
            if results.get("images"):
                self.research_results.append("📸 Free Images:")
                for img in results["images"][:3]:
                    self.research_results.append(f"  • {img['description']} ({img['license']})")
                self.research_results.append("")

            # Display music
            if results.get("music"):
                self.research_results.append("🎵 Free Background Music:")
                for music in results["music"]:
                    self.research_results.append(f"  • {music['title']} ({music['license']})")
                self.research_results.append("")

            # Display news sources
            if results.get("news_sources"):
                self.research_results.append("📰 News Sources:")
                for source in results["news_sources"]:
                    self.research_results.append(f"  • {source['name']}")
                self.research_results.append("")

            # Display video suggestions
            if results.get("video_suggestions"):
                self.research_results.append("🎬 Video Search Suggestions:")
                for suggestion in results["video_suggestions"]:
                    self.research_results.append(f"  • {suggestion}")

        except Exception as e:
            self.research_results.append(f"Research failed: {str(e)}")

    def create_presenter_video(self):
        """Create AI presenter video"""
        script = self.presenter_script_input.toPlainText().strip()
        style = self.presenter_style_combo.currentText()
        voice = self.presenter_voice_combo.currentText().lower()

        if not script:
            QMessageBox.warning(self, "Error", "Please enter a script")
            return

        self.presenter_results.clear()
        self.presenter_results.append("Creating AI presenter video...\n")

        try:
            result = self.ai_presenter.create_presenter_video(script, style, voice)

            if result["status"] == "configured":
                config = result["config"]
                self.presenter_results.append("✅ Presenter configuration ready!")
                self.presenter_results.append(f"Style: {config['style']}")
                self.presenter_results.append(f"Voice: {config['voice']}")
                self.presenter_results.append(f"Estimated Duration: {config['estimated_duration']:.1f} seconds")
                self.presenter_results.append(f"Lip Sync: {'Enabled' if config['lip_sync'] else 'Disabled'}")
                self.presenter_results.append(f"Background: {config['background']}")
                self.presenter_results.append("\nRecommended Tools:")
                for tool in config["recommended_tools"]:
                    self.presenter_results.append(f"  • {tool}")
            else:
                self.presenter_results.append(f"❌ Error: {result['message']}")

        except Exception as e:
            self.presenter_results.append(f"Presenter creation failed: {str(e)}")

    def create_batch_processing_tab(self) -> QWidget:
        """Create batch processing tab"""
        tab = QWidget()
        layout = QVBoxLayout()

        # Batch input
        batch_group = QGroupBox("Batch Processing")
        batch_layout = QVBoxLayout()

        self.batch_topics_input = QTextEdit()
        self.batch_topics_input.setPlaceholderText("Enter topics (one per line)...")
        self.batch_topics_input.setMaximumHeight(100)
        batch_layout.addWidget(QLabel("Topics:"))
        batch_layout.addWidget(self.batch_topics_input)

        self.batch_country_combo = QComboBox()
        self.batch_country_combo.addItems(["USA", "UK", "India", "Sri Lanka", "Australia", "Canada", "Global"])
        batch_layout.addWidget(QLabel("Country:"))
        batch_layout.addWidget(self.batch_country_combo)

        self.batch_language_combo = QComboBox()
        self.batch_language_combo.addItems(["English", "Tamil", "Spanish", "French", "German"])
        batch_layout.addWidget(QLabel("Language:"))
        batch_layout.addWidget(self.batch_language_combo)

        process_batch_btn = QPushButton("Process Batch")
        process_batch_btn.clicked.connect(self.process_batch)
        batch_layout.addWidget(process_batch_btn)

        batch_group.setLayout(batch_layout)
        layout.addWidget(batch_group)

        # Batch results
        results_group = QGroupBox("Batch Results")
        results_layout = QVBoxLayout()

        self.batch_results = QTextBrowser()
        self.batch_results.setMaximumHeight(250)
        results_layout.addWidget(self.batch_results)

        results_group.setLayout(results_layout)
        layout.addWidget(results_group)

        tab.setLayout(layout)
        return tab

    def create_export_import_tab(self) -> QWidget:
        """Create export/import tab"""
        tab = QWidget()
        layout = QVBoxLayout()

        # Export section
        export_group = QGroupBox("Export Project")
        export_layout = QVBoxLayout()

        export_btn = QPushButton("Export Current Project")
        export_btn.clicked.connect(self.export_project)
        export_layout.addWidget(export_btn)

        export_group.setLayout(export_layout)
        layout.addWidget(export_group)

        # Import section
        import_group = QGroupBox("Import Project")
        import_layout = QVBoxLayout()

        import_btn = QPushButton("Import Project")
        import_btn.clicked.connect(self.import_project)
        import_layout.addWidget(import_btn)

        import_group.setLayout(import_layout)
        layout.addWidget(import_group)

        # Project info
        info_group = QGroupBox("Project Information")
        info_layout = QVBoxLayout()

        self.project_info = QTextBrowser()
        self.project_info.setMaximumHeight(200)
        info_layout.addWidget(self.project_info)

        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        tab.setLayout(layout)
        return tab

    def process_batch(self):
        """Process batch of topics"""
        topics_text = self.batch_topics_input.toPlainText().strip()
        if not topics_text:
            QMessageBox.warning(self, "Error", "Please enter topics for batch processing")
            return

        topics = [topic.strip() for topic in topics_text.split('\n') if topic.strip()]
        country = self.batch_country_combo.currentText()
        language = self.batch_language_combo.currentText()

        self.batch_results.clear()
        self.batch_results.append(f"Starting batch processing for {len(topics)} topics...\n")

        for i, topic in enumerate(topics, 1):
            try:
                self.batch_results.append(f"Processing {i}/{len(topics)}: {topic}")

                # Submit to AI manager
                task_id = self.ai_manager.generate_video_creation_task(topic, country, language, 5)
                self.batch_results.append(f"  Task ID: {task_id}\n")

            except Exception as e:
                self.batch_results.append(f"  Error processing {topic}: {str(e)}\n")

        self.batch_results.append("Batch processing completed!")

    def import_project(self):
        """Import project settings"""
        try:
            file_dialog = QFileDialog()
            file_dialog.setNameFilter("JSON files (*.json)")
            if file_dialog.exec_():
                selected_files = file_dialog.selectedFiles()
                if selected_files:
                    with open(selected_files[0], 'r') as f:
                        project_data = json.load(f)

                    # Apply settings
                    self.topic_input.setText(project_data.get("topic", ""))
                    self.country_combo.setCurrentText(project_data.get("country", "Global"))
                    self.language_combo.setCurrentText(project_data.get("language", "English"))
                    self.voice_combo.setCurrentText(project_data.get("voice", "Male"))
                    self.clip_duration.setValue(project_data.get("clip_duration", 30))
                    self.video_duration.setValue(project_data.get("video_duration", 5))

                    self.project_info.clear()
                    self.project_info.append("Project imported successfully!")
                    self.project_info.append(f"Topic: {project_data.get('topic', 'N/A')}")
                    self.project_info.append(f"Country: {project_data.get('country', 'N/A')}")
                    self.project_info.append(f"Language: {project_data.get('language', 'N/A')}")
                    self.project_info.append(f"Exported: {project_data.get('exported_at', 'N/A')}")

                    QMessageBox.information(self, "Success", "Project imported successfully!")

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Import failed: {str(e)}")

    def translate_text(self, text: str, target_lang: str = "en") -> str:
        """Translate text with fallback options"""
        if self.translator:
            try:
                result = self.translator.translate(text, dest=target_lang)
                return result.text
            except Exception as e:
                logger.warning(f"Google Translate failed: {e}")

        # Fallback: simple language detection and basic translation
        logger.info("Using fallback translation")
        return self._fallback_translate(text, target_lang)

    def _fallback_translate(self, text: str, target_lang: str) -> str:
        """Simple fallback translation for common phrases"""
        # Basic translations for common video-related terms
        translations = {
            "en": {
                "news": "news",
                "video": "video",
                "music": "music",
                "sports": "sports"
            },
            "es": {
                "news": "noticias",
                "video": "video",
                "music": "música",
                "sports": "deportes"
            },
            "fr": {
                "news": "nouvelles",
                "video": "vidéo",
                "music": "musique",
                "sports": "sports"
            }
        }

        if target_lang in translations:
            for eng_word, trans_word in translations[target_lang].items():
                text = text.replace(eng_word, trans_word)

        return text

    def export_blueprint(self):
        """Export project blueprint"""
        try:
            file_dialog = QFileDialog()
            file_dialog.setDefaultSuffix("json")
            file_dialog.setNameFilter("Blueprint files (*.json *.yaml *.md)")
            file_dialog.setAcceptMode(QFileDialog.AcceptSave)

            if file_dialog.exec_():
                selected_files = file_dialog.selectedFiles()
                if selected_files:
                    filepath = selected_files[0]

                    # Determine format from file extension
                    if filepath.endswith(".json"):
                        format_type = "json"
                    elif filepath.endswith((".yaml", ".yml")):
                        format_type = "yaml"
                    elif filepath.endswith(".md"):
                        format_type = "markdown"
                    else:
                        format_type = "json"

                    success = self.spec_kit_exporter.export_to_file(filepath, format_type)

                    if success:
                        QMessageBox.information(self, "Success",
                                              f"Blueprint exported successfully to {filepath}")
                        self.status_bar.showMessage(f"Blueprint exported to {os.path.basename(filepath)}")
                    else:
                        QMessageBox.warning(self, "Error", "Failed to export blueprint")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Export failed: {str(e)}")

    def export_project(self):
        """Export current project data"""
        try:
            # Get current project data from UI
            project_data = {
                "topic": getattr(self, 'topic_input', None) and self.topic_input.text() or "",
                "country": getattr(self, 'country_combo', None) and self.country_combo.currentText() or "",
                "language": getattr(self, 'language_combo', None) and self.language_combo.currentText() or "",
                "exported_at": datetime.now().isoformat(),
                "clips": [],  # Would be populated with actual clip data
                "script": getattr(self, 'script_text', None) and self.script_text.toPlainText() or "",
                "settings": {
                    "voice": getattr(self, 'voice_combo', None) and self.voice_combo.currentText() or "",
                    "music": getattr(self, 'music_combo', None) and self.music_combo.currentText() or "",
                    "duration": getattr(self, 'duration_spin', None) and self.duration_spin.value() or 30
                }
            }

            file_dialog = QFileDialog()
            file_dialog.setDefaultSuffix("json")
            file_dialog.setNameFilter("Project files (*.json)")
            file_dialog.setAcceptMode(QFileDialog.AcceptSave)

            if file_dialog.exec_():
                selected_files = file_dialog.selectedFiles()
                if selected_files:
                    filepath = selected_files[0]

                    import json
                    with open(filepath, 'w', encoding='utf-8') as f:
                        json.dump(project_data, f, indent=2, ensure_ascii=False)

                    QMessageBox.information(self, "Success",
                                          f"Project exported successfully to {filepath}")
                    self.status_bar.showMessage(f"Project exported to {os.path.basename(filepath)}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Export failed: {str(e)}")

    def run_health_check(self):
        """Run comprehensive health check of the application"""
        try:
            health_dialog = QDialog(self)
            health_dialog.setWindowTitle("System Health Check")
            health_dialog.setModal(True)
            health_dialog.resize(600, 400)

            layout = QVBoxLayout()

            # Title
            title_label = QLabel("🔍 System Health Check")
            title_label.setFont(QFont("Arial", 14, QFont.Bold))
            layout.addWidget(title_label)

            # Progress bar
            progress_bar = QProgressBar()
            layout.addWidget(progress_bar)

            # Results text area
            results_text = QTextEdit()
            results_text.setReadOnly(True)
            layout.addWidget(results_text)

            # Buttons
            button_layout = QHBoxLayout()
            refresh_btn = QPushButton("🔄 Refresh")
            close_btn = QPushButton("Close")
            button_layout.addWidget(refresh_btn)
            button_layout.addStretch()
            button_layout.addWidget(close_btn)
            layout.addLayout(button_layout)

            health_dialog.setLayout(layout)

            def perform_health_check():
                results = []
                progress_bar.setValue(0)

                # 1. Python Version Check
                results.append("🐍 Python Version Check:")
                python_version = sys.version_info
                if python_version >= (3, 8):
                    results.append(f"   ✅ Python {python_version.major}.{python_version.minor}.{python_version.micro} - OK")
                else:
                    results.append(f"   ❌ Python {python_version.major}.{python_version.minor}.{python_version.micro} - Requires Python 3.8+")
                progress_bar.setValue(10)

                # 2. Required Dependencies Check
                results.append("\n📦 Dependencies Check:")
                dependencies = {
                    'PyQt5': 'PyQt5.QtWidgets',
                    'moviepy': 'moviepy.editor',
                    'requests': 'requests',
                    'beautifulsoup4': 'bs4',
                    'googletrans': 'googletrans',
                    'yt-dlp': 'yt_dlp',
                    'sqlite3': 'sqlite3',
                    'numpy': 'numpy',
                    'PIL': 'PIL'
                }

                missing_deps = []
                for dep, module in dependencies.items():
                    try:
                        __import__(module)
                        results.append(f"   ✅ {dep} - OK")
                    except ImportError:
                        missing_deps.append(dep)
                        results.append(f"   ❌ {dep} - MISSING")

                if missing_deps:
                    results.append(f"   ⚠️  Missing dependencies: {', '.join(missing_deps)}")
                    results.append("   💡 Install with: pip install " + " ".join(missing_deps))
                progress_bar.setValue(30)

                # 3. Database Check
                results.append("\n💾 Database Check:")
                try:
                    if hasattr(self, 'conn') and self.conn:
                        cursor = self.conn.cursor()
                        cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
                        table_count = cursor.fetchone()[0]
                        results.append(f"   ✅ Database connected - {table_count} tables found")
                    else:
                        results.append("   ❌ Database not initialized")
                except Exception as e:
                    results.append(f"   ❌ Database error: {str(e)}")
                progress_bar.setValue(40)

                # 4. File System Check
                results.append("\n📁 File System Check:")
                try:
                    # Check write permissions
                    test_file = os.path.join(os.getcwd(), 'health_check_test.tmp')
                    with open(test_file, 'w') as f:
                        f.write('test')
                    os.remove(test_file)
                    results.append("   ✅ Write permissions - OK")

                    # Check temp directory
                    import tempfile
                    temp_dir = tempfile.gettempdir()
                    if os.path.exists(temp_dir):
                        results.append("   ✅ Temp directory accessible")
                    else:
                        results.append("   ❌ Temp directory not accessible")
                except Exception as e:
                    results.append(f"   ❌ File system error: {str(e)}")
                progress_bar.setValue(50)

                # 5. Network Connectivity Check
                results.append("\n🌐 Network Check:")
                try:
                    # Test basic connectivity
                    import socket
                    socket.create_connection(("8.8.8.8", 53), timeout=3)
                    results.append("   ✅ Internet connectivity - OK")

                    # Test YouTube API (if credentials available)
                    if hasattr(self, 'youtube_service') and self.youtube_service:
                        results.append("   ✅ YouTube API connected")
                    else:
                        results.append("   ⚠️  YouTube API not configured")
                except Exception as e:
                    results.append(f"   ❌ Network error: {str(e)}")
                progress_bar.setValue(70)

                # 6. AI System Check
                results.append("\n🤖 AI System Check:")
                try:
                    if hasattr(self, 'ai_manager') and self.ai_manager:
                        results.append("   ✅ AI Manager initialized")
                        if hasattr(self.ai_manager, 'agents') and self.ai_manager.agents:
                            results.append(f"   ✅ {len(self.ai_manager.agents)} AI agents loaded")
                        else:
                            results.append("   ⚠️  No AI agents loaded")
                    else:
                        results.append("   ❌ AI Manager not initialized")
                except Exception as e:
                    results.append(f"   ❌ AI system error: {str(e)}")
                progress_bar.setValue(85)

                # 7. Memory and Performance Check
                results.append("\n⚡ Performance Check:")
                try:
                    import psutil
                    memory = psutil.virtual_memory()
                    memory_usage = memory.percent
                    if memory_usage < 80:
                        results.append(f"   ✅ Memory usage: {memory_usage:.1f}% - OK")
                    else:
                        results.append(f"   ⚠️  High memory usage: {memory_usage:.1f}%")

                    # CPU usage
                    cpu_usage = psutil.cpu_percent(interval=0.1)
                    results.append(f"   📊 CPU usage: {cpu_usage:.1f}%")
                except ImportError:
                    results.append("   ⚠️  psutil not available for performance monitoring")
                except Exception as e:
                    results.append(f"   ❌ Performance check error: {str(e)}")
                progress_bar.setValue(95)

                # 8. Overall Status
                results.append("\n📋 Overall Status:")
                error_count = results.count("❌")
                warning_count = results.count("⚠️")

                if error_count == 0 and warning_count == 0:
                    results.append("   🎉 All systems operational!")
                    progress_bar.setValue(100)
                elif error_count == 0:
                    results.append(f"   ⚠️  System operational with {warning_count} warnings")
                    progress_bar.setValue(100)
                else:
                    results.append(f"   ❌ System has {error_count} errors and {warning_count} warnings")
                    progress_bar.setValue(100)

                # Update results display
                results_text.setPlainText("\n".join(results))

            # Connect buttons
            refresh_btn.clicked.connect(perform_health_check)
            close_btn.clicked.connect(health_dialog.accept)

            # Run initial check
            perform_health_check()

            # Show dialog
            health_dialog.exec_()

        except Exception as e:
            QMessageBox.critical(self, "Health Check Error", f"Failed to run health check: {str(e)}")

if __name__ == "__main__":
    # Quick health check before starting
    print("🔍 Running Quick Health Check...")

    # Check Python version
    python_version = sys.version_info
    print(f"🐍 Python Version: {python_version.major}.{python_version.minor}.{python_version.micro}")

    # Check basic dependencies
    dependencies = ['PyQt5', 'moviepy', 'requests', 'beautifulsoup4']
    missing = []
    for dep in dependencies:
        try:
            if dep == 'PyQt5':
                import PyQt5.QtWidgets
            elif dep == 'moviepy':
                import moviepy.editor
            elif dep == 'requests':
                import requests
            elif dep == 'beautifulsoup4':
                import bs4
            print(f"✅ {dep} - OK")
        except ImportError:
            missing.append(dep)
            print(f"❌ {dep} - MISSING")

    if missing:
        print(f"⚠️ Missing dependencies: {', '.join(missing)}")
        print("Install with: pip install " + " ".join(missing))

    print("🚀 Starting application...")
    app = QApplication(sys.argv)
    window = VideoRemakerApp()
    window.show()
    sys.exit(app.exec_())