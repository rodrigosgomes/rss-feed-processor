import unittest
from unittest.mock import patch, MagicMock
import json
from src.utils.gemini_client import GeminiClient

class TestGeminiClient(unittest.TestCase):
    def setUp(self):
        self.api_key = "test_api_key"
        self.client = GeminiClient(self.api_key)

    @patch('src.utils.gemini_client.genai.GenerativeModel')
    def test_initialize_model_success(self, mock_model):
        # Configure mock
        mock_model.return_value = MagicMock()
        
        # Test initialization
        result = self.client.initialize_model()
        self.assertTrue(result)
        self.assertIsNotNone(self.client.model)    @patch('src.utils.gemini_client.genai.GenerativeModel')
    def test_initialize_model_with_quota_error(self, mock_model):
        # Configure mock to raise quota error for main model, then succeed with free model
        mock_instance = MagicMock()
        mock_model.side_effect = [
            Exception("429 You exceeded your current quota"),  # First call fails with quota error
            mock_instance  # Second call succeeds with free model
        ]
        mock_instance.name = 'models/gemma-3-1b-it'  # Set the name to match a free model

        # Test initialization
        result = self.client.initialize_model()
        self.assertTrue(result)
        self.assertIsNotNone(self.client.model)
        # Verify we switched to a free model
        mock_model.assert_called_with('models/gemma-3-1b-it')

    @patch('src.utils.gemini_client.genai.GenerativeModel')
    def test_generate_content_success(self, mock_model):
        # Configure mock
        mock_instance = MagicMock()
        mock_instance.generate_content.return_value = MagicMock(text="Test response")
        mock_model.return_value = mock_instance
        
        # Initialize model
        self.client.initialize_model()
        
        # Test content generation
        response = self.client.generate_content("Test prompt")
        self.assertEqual(response.text, "Test response")

    @patch('src.utils.gemini_client.genai.GenerativeModel')
    def test_generate_content_with_retry(self, mock_model):
        # Configure mock to fail once then succeed
        mock_instance = MagicMock()
        mock_instance.generate_content.side_effect = [
            Exception("500 Internal Server Error"),
            MagicMock(text="Test response")
        ]
        mock_model.return_value = mock_instance
        
        # Initialize model
        self.client.initialize_model()
        
        # Test content generation with retry
        response = self.client.generate_content("Test prompt")
        self.assertEqual(response.text, "Test response")

    def test_calculate_delay(self):
        # Test with error message containing retry delay
        error_str = '''{"error": "quota exceeded", "retry_delay": {"seconds": 30}}'''
        delay = self.client._calculate_delay(0, error_str)
        self.assertEqual(delay, 30)
        
        # Test exponential backoff
        delay = self.client._calculate_delay(0)
        self.assertEqual(delay, 5)  # Base delay
        
        delay = self.client._calculate_delay(1)
        self.assertEqual(delay, 10)  # 5 * 2^1
        
        delay = self.client._calculate_delay(2)
        self.assertEqual(delay, 20)  # 5 * 2^2

    def test_should_retry(self):
        # Test quota error
        should_retry = self.client._should_retry(Exception("429 Quota exceeded"), 0)
        self.assertTrue(should_retry)
        
        # Test server error
        should_retry = self.client._should_retry(Exception("500 Server Error"), 0)
        self.assertTrue(should_retry)
        
        # Test non-retriable error
        should_retry = self.client._should_retry(Exception("400 Bad Request"), 0)
        self.assertFalse(should_retry)
        
        # Test max retries
        should_retry = self.client._should_retry(Exception("429 Quota exceeded"), 
                                               self.client.retry_count - 1)
        self.assertFalse(should_retry)

    @patch('src.utils.gemini_client.genai.list_models')
    def test_list_models(self, mock_list_models):
        # Configure mock
        mock_list_models.return_value = [
            MagicMock(name="model1"),
            MagicMock(name="model2")
        ]
        
        # Test model listing
        models = self.client.list_models()
        self.assertEqual(len(models), 2)
        self.assertEqual(models, ["model1", "model2"])
