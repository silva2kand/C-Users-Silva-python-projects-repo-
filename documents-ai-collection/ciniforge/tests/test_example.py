"""Example test file using SpecKit"""

from speckit import BaseTest, MockFactory, benchmark

class TestExample(BaseTest):
    """Example test class"""
    
    def setUp(self):
        super().setUp()
        self.mock_data = MockFactory.mock_user()
    
    def test_basic_functionality(self):
        """Test basic functionality"""
        self.assertIsNotNone(self.mock_data)
        self.assertIn('username', self.mock_data)
    
    @benchmark(iterations=100)
    def test_performance_example(self):
        """Example performance test"""
        # Simulate some work
        result = sum(range(1000))
        self.assertEqual(result, 499500)
