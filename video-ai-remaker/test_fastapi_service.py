import unittest
from fastapi.testclient import TestClient
from fastapi_service import app, fallback_responses

client = TestClient(app)

class TestAPIRoutes(unittest.TestCase):
    """Test FastAPI service endpoints."""

    def test_root_endpoint(self):
        response = client.get("/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("message", data)
        self.assertEqual(data["message"], "Hybrid AI Video Remaker API")

    def test_chat_fallback(self):
        # Without valid AI keys/services, chat should use fallback
        payload = {
            "message": "Hello, how are you?",
            "personality": "helpful",
            "max_tokens": 10,
            "temperature": 0.1
        }
        response = client.post("/chat", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("response", data)
        self.assertIn("service_used", data)
        self.assertEqual(data["service_used"], "fallback")
        # Response should be one of the known fallback messages
        self.assertIn(data["response"], list(fallback_responses.values()))

if __name__ == "__main__":
    unittest.main()
