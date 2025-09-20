"""Mock data factory for SpecKit testing"""

import random
import string
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from unittest.mock import Mock, MagicMock

class MockFactory:
    """Factory for creating mock objects and test data"""
    
    @staticmethod
    def random_string(length: int = 10) -> str:
        """Generate a random string"""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    
    @staticmethod
    def random_email() -> str:
        """Generate a random email address"""
        username = MockFactory.random_string(8).lower()
        domain = random.choice(['gmail.com', 'yahoo.com', 'outlook.com', 'test.com'])
        return f"{username}@{domain}"
    
    @staticmethod
    def random_phone() -> str:
        """Generate a random phone number"""
        return f"+1-{random.randint(100,999)}-{random.randint(100,999)}-{random.randint(1000,9999)}"
    
    @staticmethod
    def random_date(start_days_ago: int = 365, end_days_ago: int = 0) -> datetime:
        """Generate a random date within a range"""
        start = datetime.now() - timedelta(days=start_days_ago)
        end = datetime.now() - timedelta(days=end_days_ago)
        delta = end - start
        random_days = random.randint(0, delta.days)
        return start + timedelta(days=random_days)
    
    @staticmethod
    def mock_user(user_id: Optional[int] = None) -> Dict[str, Any]:
        """Create a mock user object"""
        return {
            'id': user_id or random.randint(1, 10000),
            'username': MockFactory.random_string(8).lower(),
            'email': MockFactory.random_email(),
            'first_name': random.choice(['John', 'Jane', 'Bob', 'Alice', 'Charlie']),
            'last_name': random.choice(['Smith', 'Johnson', 'Williams', 'Brown', 'Jones']),
            'phone': MockFactory.random_phone(),
            'created_at': MockFactory.random_date().isoformat(),
            'is_active': random.choice([True, False]),
            'role': random.choice(['user', 'admin', 'moderator'])
        }
    
    @staticmethod
    def mock_chat_message(message_id: Optional[int] = None) -> Dict[str, Any]:
        """Create a mock chat message"""
        messages = [
            "Hello, how are you?",
            "What's the weather like today?",
            "Can you help me with this task?",
            "Thank you for your assistance!",
            "I need information about...",
            "Could you please explain..."
        ]
        
        return {
            'id': message_id or random.randint(1, 10000),
            'content': random.choice(messages),
            'user_id': random.randint(1, 100),
            'timestamp': MockFactory.random_date(7).isoformat(),
            'message_type': random.choice(['text', 'image', 'file', 'voice']),
            'is_read': random.choice([True, False]),
            'metadata': {
                'length': random.randint(10, 500),
                'language': random.choice(['en', 'es', 'fr', 'de'])
            }
        }
    
    @staticmethod
    def mock_ai_response() -> Dict[str, Any]:
        """Create a mock AI response"""
        responses = [
            "I understand your question. Let me help you with that.",
            "Based on the information provided, I recommend...",
            "Here's what I found regarding your query...",
            "I can assist you with this task. Here's how...",
            "That's an interesting question. The answer is..."
        ]
        
        return {
            'response': random.choice(responses),
            'confidence': round(random.uniform(0.7, 1.0), 2),
            'processing_time': round(random.uniform(0.1, 2.0), 3),
            'model': random.choice(['gpt-4', 'claude-3', 'llama-2']),
            'tokens_used': random.randint(50, 500),
            'metadata': {
                'temperature': round(random.uniform(0.1, 1.0), 1),
                'max_tokens': random.randint(100, 1000)
            }
        }
    
    @staticmethod
    def mock_http_client():
        """Create a mock HTTP client"""
        mock_client = Mock()
        
        # Mock GET request
        mock_client.get.return_value = Mock(
            status_code=200,
            json=lambda: {'status': 'success', 'data': []},
            text='Mock response text'
        )
        
        # Mock POST request
        mock_client.post.return_value = Mock(
            status_code=201,
            json=lambda: {'status': 'created', 'id': random.randint(1, 1000)}
        )
        
        return mock_client
    
    @staticmethod
    def mock_database():
        """Create a mock database connection"""
        mock_db = Mock()
        
        # Mock query results
        mock_db.execute.return_value = Mock(
            fetchall=lambda: [MockFactory.mock_user() for _ in range(3)],
            fetchone=lambda: MockFactory.mock_user(),
            rowcount=random.randint(1, 10)
        )
        
        return mock_db
    
    @staticmethod
    def mock_file_system():
        """Create a mock file system"""
        mock_fs = Mock()
        
        mock_fs.exists.return_value = True
        mock_fs.read_text.return_value = "Mock file content"
        mock_fs.write_text.return_value = None
        mock_fs.mkdir.return_value = None
        
        return mock_fs