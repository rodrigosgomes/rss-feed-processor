import os
import sys
import pytest
from datetime import datetime
import pytz
from pathlib import Path

# Add src directory to Python path for test discovery
test_dir = Path(__file__).parent
project_root = test_dir.parent
src_path = project_root / 'src'
sys.path.insert(0, str(src_path))

@pytest.fixture(autouse=True)
def setup_test_env():
    """Automatically set up test environment for all tests"""
    # Store original sys.path
    original_path = sys.path.copy()
    
    # Add src directory to path
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
    yield
    
    # Restore original sys.path
    sys.path = original_path

from models.news_item import NewsItem
from utils.gemini_client import GeminiClient
from utils.email_sender import EmailSender

@pytest.fixture
def mock_news_items():
    """Fixture providing sample news items for testing"""
    current_date = datetime.now(pytz.UTC)
    old_date = datetime(2023, 1, 1, tzinfo=pytz.UTC)
    
    return [
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

@pytest.fixture
def mock_rss_content():
    """Fixture providing sample RSS content for testing"""
    return '''<?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0">
        <channel>
            <title>Test Feed</title>
            <link>http://example.com</link>
            <description>Test Description</description>
            <item>
                <title>Test Article</title>
                <link>http://example.com/article1</link>
                <description>Test article description</description>
                <pubDate>Thu, 23 May 2025 10:00:00 +0000</pubDate>
            </item>
        </channel>
    </rss>'''

@pytest.fixture
def mock_email_settings():
    """Fixture providing test email settings"""
    return {
        "smtp_server": "smtp.test.com",
        "smtp_port": 587,
        "sender_email": "test@example.com",
        "sender_password": "test_password",
        "recipient_email": "recipient@example.com"
    }

@pytest.fixture
def mock_gemini_client(mocker):
    """Fixture providing a mocked GeminiClient"""
    mock_client = mocker.Mock(spec=GeminiClient)
    mock_client.generate_content.return_value = mocker.Mock(text="Test summary")
    return mock_client

@pytest.fixture
def mock_email_sender(mock_email_settings):
    """Fixture providing an EmailSender instance with test settings"""
    return EmailSender(mock_email_settings)
