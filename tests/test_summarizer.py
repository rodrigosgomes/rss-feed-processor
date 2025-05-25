import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
import pytz
import os
import sys

# Add src directory to Python path
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

print("Starting imports...")
print(f"sys.path before imports: {sys.path}")

try:
    print("Importing summarizer...")
    from agents.summarizer import Summarizer
    print("Importing news_item...")
    from models.news_item import NewsItem
    print("Importing gemini_client...")
    from utils.gemini_client import GeminiClient
    print("All imports successful!")
except ImportError as e:
    print(f"Import Error: {e}")
    print(f"sys.path: {sys.path}")
    raise

class TestSummarizer(unittest.TestCase):
    def setUp(self):
        # Mock the GeminiClient class with correct path
        self.gemini_patcher = patch('agents.summarizer.GeminiClient')
        mock_gemini_class = self.gemini_patcher.start()
        
        # Create a mock instance with the generate_content method
        mock_instance = MagicMock()
        mock_instance.generate_content.return_value = MagicMock(text="Test summary")
        mock_instance.initialize_model = MagicMock()  # Mock the initialize_model method
        
        # Make the class return our configured instance
        mock_gemini_class.return_value = mock_instance
        self.mock_gemini = mock_instance
        
        self.summarizer = Summarizer()
        
        # Create test data with timezone-aware dates
        current_date = datetime.now(pytz.UTC)
        old_date = datetime(2023, 1, 1, tzinfo=pytz.UTC)
        
        self.news_items = [
            NewsItem(
                title="Today News 1",
                description="Test description 1",
                link="http://example.com/1",
                published_date=current_date,
                source="Test Source"
            ),
            NewsItem(
                title="Today News 2",
                description="Test description 2",
                link="http://example.com/2",
                published_date=current_date,
                source="Test Source"
            ),
            NewsItem(
                title="Old News",
                description="Test description 3",
                link="http://example.com/3",
                published_date=old_date,
                source="Test Source"
            ),
        ]

    def tearDown(self):
        self.gemini_patcher.stop()

    def test_summarize_current_day(self):
        """Test that only current day news items are summarized"""
        summary = self.summarizer.summarize(self.news_items)
        
        # Verify we have only one date (today) in the summary
        self.assertEqual(len(summary), 1)
        
        # Get today's date
        current_date = datetime.now(pytz.UTC).date()
        
        # Verify the summary contains today's news
        self.assertIn(current_date, summary)
        self.assertEqual(len(summary[current_date]['items']), 2)  # Should have 2 items from today
        
        # Verify the summary format
        self.assertIn('summary', summary[current_date])
        self.assertIn('items', summary[current_date])
        self.assertEqual(summary[current_date]['summary'], "Test summary")

    def test_empty_summary(self):
        """Test handling of empty news items list"""
        summary = self.summarizer.summarize([])
        self.assertEqual(summary, {})

    def test_no_current_day_news(self):
        """Test handling when there are no news items for the current day"""
        old_date = datetime(2023, 1, 1, tzinfo=pytz.UTC)
        old_news = [
            NewsItem(
                title="Old News",
                description="Test description",
                link="http://example.com/1",
                published_date=old_date,
                source="Test Source"
            )
        ]
        summary = self.summarizer.summarize(old_news)
        self.assertEqual(summary, {})

    def test_api_error_handling(self):
        """Test handling of API errors during summarization"""
        # Configure the mock to raise an exception
        self.mock_gemini.generate_content.side_effect = Exception("API Error")
        
        summarizer = Summarizer()
        current_date = datetime.now(pytz.UTC)
        news_items = [
            NewsItem(
                title="Today News",
                description="Test description",
                link="http://example.com/1",
                published_date=current_date,
                source="Test Source"
            )
        ]
        
        summary = summarizer.summarize(news_items)
        current_date = current_date.date()  # Convert to date for comparison
        self.assertIn(current_date, summary)
        self.assertIn("Error generating summary", 
                     summary[current_date]['summary'])

if __name__ == '__main__':
    unittest.main()