#!/usr/bin/env python3
"""
Lightweight AI API Server - Free & Permanent
A minimal Flask API that serves all AI programs with GPT4All and internet knowledge
"""

import sys
import os
import time
import threading
import json
from pathlib import Path
from flask import Flask, request, jsonify
from flask_cors import CORS

# Lightweight AI imports
try:
    from gpt4all import GPT4All
    GPT4ALL_AVAILABLE = True
    print("[API] GPT4All available")
except ImportError:
    GPT4ALL_AVAILABLE = False
    print("[API] GPT4All not available")

# Free API fallback
try:
    import requests
    REQUESTS_AVAILABLE = True
    print("[API] Requests available for free APIs")
except ImportError:
    REQUESTS_AVAILABLE = False
    print("[API] Requests not available")

# Internet knowledge
try:
    from bs4 import BeautifulSoup
    WEB_AVAILABLE = True
    print("[API] Web scraping available")
except ImportError:
    WEB_AVAILABLE = False

try:
    import wikipedia
    WIKIPEDIA_AVAILABLE = True
    print("[API] Wikipedia available")
except ImportError:
    WIKIPEDIA_AVAILABLE = False

try:
    import feedparser
    RSS_AVAILABLE = True
    print("[API] RSS feeds available")
except ImportError:
    RSS_AVAILABLE = False

class LightweightAIAPI:
    def __init__(self):
        self.app = Flask(__name__)
        CORS(self.app)  # Enable CORS for web access

        # Lightweight AI model (smaller model for speed)
        self.ai_model = None
        self.model_loaded = False

        # Conversation history (lightweight storage)
        self.conversations = {}
        self.max_history = 100  # Keep it light

        # Setup routes
        self.setup_routes()

        # Load AI model in background
        threading.Thread(target=self.load_ai_model, daemon=True).start()

    def setup_routes(self):
        @self.app.route('/health', methods=['GET'])
        def health():
            return jsonify({
                'status': 'healthy',
                'ai_loaded': self.model_loaded,
                'memory_usage': self.get_memory_usage(),
                'uptime': time.time()
            })

        @self.app.route('/chat', methods=['POST'])
        def chat():
            try:
                data = request.get_json()
                message = data.get('message', '').strip()
                session_id = data.get('session_id', 'default')

                if not message:
                    return jsonify({'error': 'No message provided'}), 400

                # Get or create conversation history
                if session_id not in self.conversations:
                    self.conversations[session_id] = []

                # Add user message
                self.conversations[session_id].append({'role': 'user', 'message': message})

                # Keep history lightweight
                if len(self.conversations[session_id]) > self.max_history:
                    self.conversations[session_id] = self.conversations[session_id][-self.max_history:]

                # Process message
                response = self.process_message(message, self.conversations[session_id])

                # Add AI response
                self.conversations[session_id].append({'role': 'ai', 'message': response})

                return jsonify({
                    'response': response,
                    'session_id': session_id,
                    'timestamp': time.time()
                })

            except Exception as e:
                print(f"[API] Chat error: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/search', methods=['POST'])
        def search():
            try:
                data = request.get_json()
                query = data.get('query', '').strip()

                if not query:
                    return jsonify({'error': 'No query provided'}), 400

                results = self.web_search(query)
                return jsonify({'results': results})

            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @self.app.route('/wikipedia', methods=['POST'])
        def wikipedia_search():
            try:
                data = request.get_json()
                query = data.get('query', '').strip()

                if not query:
                    return jsonify({'error': 'No query provided'}), 400

                result = self.wikipedia_search(query)
                return jsonify({'result': result})

            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @self.app.route('/news', methods=['POST'])
        def news():
            try:
                data = request.get_json()
                topic = data.get('topic', 'world')

                news_data = self.get_news(topic)
                return jsonify({'news': news_data})

            except Exception as e:
                return jsonify({'error': str(e)}), 500

    def load_ai_model(self):
        """Load lightweight AI model"""
        try:
            print("[API] Loading lightweight AI model...")

            if GPT4ALL_AVAILABLE:
                # Use smaller, faster model
                start_time = time.time()
                self.ai_model = GPT4All("orca-mini-3b-gguf2-q4_0.gguf", device='cpu')
                load_time = time.time() - start_time

                self.model_loaded = True
                print(f"[API] Model loaded in {load_time:.1f}s")
            else:
                print("[API] GPT4All not available, using free API fallback")
                self.model_loaded = True  # Can still work with free APIs

        except Exception as e:
            print(f"[API] Model loading failed: {e}")
            self.model_loaded = False

    def process_message(self, message, history):
        """Process message with lightweight AI"""
        try:
            # Check for internet knowledge requests first
            internet_response = self.handle_internet_request(message)
            if internet_response:
                return internet_response

            # Use AI model if available
            if self.model_loaded and self.ai_model:
                try:
                    # Lightweight prompt
                    prompt = f"User: {message}\nAssistant:"

                    response = self.ai_model.generate(
                        prompt,
                        max_tokens=100,  # Keep it short and fast
                        temp=0.7,
                        top_k=30
                    )

                    return response.strip()

                except Exception as e:
                    print(f"[API] AI model error: {e}")

            # Free API fallback
            if REQUESTS_AVAILABLE:
                return self.get_free_api_response(message)

            # Basic fallback
            return self.get_basic_response(message)

        except Exception as e:
            print(f"[API] Processing error: {e}")
            return "Sorry, I encountered an error. Please try again."

    def handle_internet_request(self, message):
        """Handle internet knowledge requests"""
        message_lower = message.lower().strip()

        # Web search
        if any(word in message_lower for word in ['search', 'find', 'look up', 'research']):
            query = message_lower
            for prefix in ['search for', 'find', 'look up', 'research']:
                query = query.replace(prefix, '').strip()

            if query:
                return self.web_search(query)

        # Wikipedia
        if any(word in message_lower for word in ['wikipedia', 'wiki', 'encyclopedia']):
            query = message_lower
            for prefix in ['wikipedia', 'wiki', 'encyclopedia']:
                query = query.replace(prefix, '').strip()

            if query:
                return self.wikipedia_search(query)

        # News
        if any(word in message_lower for word in ['news', 'latest', 'headlines']):
            topic = 'world'
            if 'technology' in message_lower or 'tech' in message_lower:
                topic = 'technology'
            elif 'science' in message_lower:
                topic = 'science'
            elif 'business' in message_lower:
                topic = 'business'

            return self.get_news(topic)

        return None

    def web_search(self, query):
        """Lightweight web search"""
        try:
            if not WEB_AVAILABLE:
                return "Web search not available"

            search_url = f"https://duckduckgo.com/html/?q={query.replace(' ', '+')}"
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

            response = requests.get(search_url, headers=headers, timeout=5)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            results = []
            for result in soup.find_all('div', class_='result')[:2]:  # Just 2 results to keep it light
                title_elem = result.find('a', class_='result__a')
                snippet_elem = result.find('a', class_='result__snippet')

                if title_elem and snippet_elem:
                    title = title_elem.get_text().strip()
                    url = title_elem.get('href', '')
                    snippet = snippet_elem.get_text().strip()[:100] + '...'

                    results.append(f"🔍 {title}\n{snippet}\n🔗 {url}")

            if results:
                return "\n\n".join(results)
            else:
                return f"No search results found for '{query}'"

        except Exception as e:
            return f"Search failed: {str(e)}"

    def wikipedia_search(self, query):
        """Lightweight Wikipedia search"""
        try:
            if not WIKIPEDIA_AVAILABLE:
                return "Wikipedia not available"

            search_results = wikipedia.search(query, results=1)

            if not search_results:
                return f"No Wikipedia page found for '{query}'"

            page = wikipedia.page(search_results[0])
            summary = page.summary[:300] + "..." if len(page.summary) > 300 else page.summary

            return f"📚 {page.title}\n\n{summary}\n\n🔗 {page.url}"

        except Exception as e:
            return f"Wikipedia search failed: {str(e)}"

    def get_news(self, topic):
        """Lightweight news fetch"""
        try:
            if not RSS_AVAILABLE:
                return "News feeds not available"

            feeds = {
                'technology': 'https://feeds.bbci.co.uk/news/technology/rss.xml',
                'world': 'https://feeds.bbci.co.uk/news/world/rss.xml',
                'science': 'https://feeds.bbci.co.uk/news/science_and_environment/rss.xml',
                'business': 'https://feeds.bbci.co.uk/news/business/rss.xml'
            }

            feed_url = feeds.get(topic, feeds['world'])
            feed = feedparser.parse(feed_url)

            if not feed.entries:
                return "No news available"

            # Just latest 2 headlines to keep it light
            news_items = []
            for article in feed.entries[:2]:
                title = article.title
                link = article.link
                news_items.append(f"📰 {title}\n🔗 {link}")

            return "\n\n".join(news_items)

        except Exception as e:
            return f"News fetch failed: {str(e)}"

    def get_free_api_response(self, message):
        """Free API fallback"""
        try:
            api_url = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-small"
            headers = {"Content-Type": "application/json"}

            payload = {
                "inputs": message[:100],
                "parameters": {
                    "max_length": 50,
                    "temperature": 0.7,
                    "do_sample": False
                }
            }

            response = requests.post(api_url, json=payload, headers=headers, timeout=5)

            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    generated_text = result[0].get('generated_text', '')
                    if generated_text:
                        clean_response = generated_text.replace(message, '').strip()
                        return clean_response or generated_text.strip()

            return self.get_basic_response(message)

        except Exception as e:
            print(f"[API] Free API error: {e}")
            return self.get_basic_response(message)

    def get_basic_response(self, message):
        """Basic lightweight responses"""
        message_lower = message.lower().strip()

        responses = {
            'hello': "Hello! I'm your lightweight AI assistant.",
            'hi': "Hi there! How can I help you?",
            'help': "I can chat, search the web, check Wikipedia, and get news. Try 'search AI' or 'news technology'!",
            'what can you do': "I can chat, search the web, access Wikipedia, and fetch news. Ask me anything!",
            'status': f"AI loaded: {self.model_loaded}, Memory: {self.get_memory_usage()}",
        }

        for key, response in responses.items():
            if key in message_lower:
                return response

        return f"I understand you're asking about '{message[:30]}...'. I can help with chat, web search, Wikipedia, and news!"

    def get_memory_usage(self):
        """Get current memory usage"""
        try:
            import psutil
            import os
            process = psutil.Process(os.getpid())
            return f"{process.memory_info().rss / 1024 / 1024:.1f} MB"
        except:
            return "Unknown"

    def run(self, host='0.0.0.0', port=3000):
        """Run the lightweight API server"""
        print(f"🚀 Starting Lightweight AI API Server on {host}:{port}")
        print(f"🌐 Access from: http://localhost:{port}")
        print(f"📱 Local network: http://{self.get_local_ip()}:{port}")

        try:
            self.app.run(host=host, port=port, debug=False, use_reloader=False)
        except KeyboardInterrupt:
            print("\n👋 API Server stopped")
        except Exception as e:
            print(f"❌ Server error: {e}")

    def get_local_ip(self):
        """Get local IP address"""
        try:
            import socket
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except:
            return "localhost"

def main():
    """Main entry point"""
    print("🤖 Lightweight AI API Server")
    print("=" * 40)

    # Create and run API
    api = LightweightAIAPI()

    # Small delay to let model load
    print("⏳ Starting server in 3 seconds...")
    time.sleep(3)

    # Run server
    api.run()

if __name__ == "__main__":
    main()