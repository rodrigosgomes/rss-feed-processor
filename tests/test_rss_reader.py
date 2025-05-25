import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
import pytz
from src.agents.rss_reader import RssReader
from src.models.news_item import NewsItem
import xml.etree.ElementTree as ET
import requests

class TestRssReader(unittest.TestCase):
    def setUp(self):
        self.test_urls = ["http://example.com/feed1", "http://example.com/feed2"]
        self.rss_reader = RssReader(self.test_urls)

        # Sample RSS content with multiple items
        self.sample_rss = '''<?xml version="1.0" encoding="UTF-8"?>
        <rss version="2.0">
            <channel>
                <title>Test Feed</title>
                <link>http://example.com</link>
                <description>Test Description</description>
                <item>
                    <title>Test Article 1</title>
                    <link>http://example.com/article1</link>
                    <description>Test article description 1</description>
                    <pubDate>Thu, 23 May 2025 10:00:00 +0000</pubDate>
                </item>
                <item>
                    <title>Test Article 2</title>
                    <link>http://example.com/article2</link>
                    <description>Test article description 2</description>
                    <pubDate>Thu, 23 May 2025 11:00:00 +0000</pubDate>
                </item>
            </channel>
        </rss>'''

    @patch('src.agents.rss_reader.requests.get')
    def test_fetch_news_success(self, mock_get):
        # Configure mock response
        mock_response = MagicMock()
        mock_response.content = self.sample_rss.encode('utf-8')
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Test news fetching
        news_items = self.rss_reader.fetch_news()
        
        # Verify the results
        self.assertEqual(len(news_items), 2)  # One item per feed
        self.assertIsInstance(news_items[0], NewsItem)
        self.assertEqual(news_items[0].title, "Test Article")
        self.assertEqual(news_items[0].source, "Test Feed")
        self.assertTrue(news_items[0].published_date.tzinfo)  # Verify timezone awareness

    @patch('src.agents.rss_reader.requests.get')
    def test_fetch_news_network_error(self, mock_get):
        # Configure mock to raise an exception
        mock_get.side_effect = requests.exceptions.RequestException("Network error")

        # Test error handling
        news_items = self.rss_reader.fetch_news()
        self.assertEqual(len(news_items), 0)

    def test_parse_date_formats(self):
        test_dates = [
            # RFC 822 format
            ("Thu, 23 May 2025 10:00:00 +0000", True),
            # ISO 8601 format
            ("2025-05-23T10:00:00Z", True),
            # Invalid format
            ("invalid date", False)
        ]

        for date_str, should_succeed in test_dates:
            parsed_date = self.rss_reader._parse_date(date_str)
            self.assertIsInstance(parsed_date, datetime)
            self.assertTrue(parsed_date.tzinfo)  # Verify timezone awareness
            
            if should_succeed:
                # For valid dates, verify it's not defaulting to current time
                self.assertNotEqual(parsed_date.date(), datetime.now(pytz.UTC).date())

    def test_empty_feed_urls(self):
        empty_reader = RssReader([])
        news_items = empty_reader.fetch_news()
        self.assertEqual(len(news_items), 0)

    @patch('src.agents.rss_reader.requests.get')
    def test_malformed_rss(self, mock_get):
        # Configure mock with malformed XML
        mock_response = MagicMock()
        mock_response.content = "Invalid XML"
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Test error handling for malformed RSS
        news_items = self.rss_reader.fetch_news()
        self.assertEqual(len(news_items), 0)

    @patch('src.agents.rss_reader.requests.get')
    def test_missing_fields(self, mock_get):
        # RSS content with missing fields
        minimal_rss = '''<?xml version="1.0" encoding="UTF-8"?>
        <rss version="2.0">
            <channel>
                <item>
                    <title>Test Article</title>
                </item>
            </channel>
        </rss>'''

        # Configure mock response
        mock_response = MagicMock()
        mock_response.content = minimal_rss.encode('utf-8')
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Test handling of missing fields
        news_items = self.rss_reader.fetch_news()
        self.assertEqual(len(news_items), 2)  # One per feed
        self.assertEqual(news_items[0].title, "Test Article")
        self.assertEqual(news_items[0].description, "")
        self.assertEqual(news_items[0].link, "")