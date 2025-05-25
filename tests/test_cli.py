import pytest
from datetime import datetime, timedelta
import sys
from unittest.mock import patch, MagicMock
from src.main import parse_args, get_feed_urls, process_news

def test_parse_args_default():
    with patch('sys.argv', ['main.py']):
        args = parse_args()
        assert args.days == 1
        assert args.feeds is None
        assert args.dry_run is False

def test_parse_args_with_values():
    test_args = ['main.py', '--days', '3', '--feeds', 'feed1,feed2', '--dry-run']
    with patch('sys.argv', test_args):
        args = parse_args()
        assert args.days == 3
        assert args.feeds == 'feed1,feed2'
        assert args.dry_run is True

def test_get_feed_urls():
    class Args:
        def __init__(self, feeds=None):
            self.feeds = feeds
    
    default_feeds = ['http://default1.com', 'http://default2.com']
    with patch('src.main.RSS_FEED_URLS', default_feeds):
        # Test with no feeds specified
        args = Args()
        assert get_feed_urls(args) == default_feeds
        
        # Test with specific feeds
        args = Args('http://test1.com,http://test2.com')
        assert get_feed_urls(args) == ['http://test1.com', 'http://test2.com']

@pytest.mark.asyncio
async def test_process_news_dry_run():
    # Mock dependencies
    mock_news_items = [
        MagicMock(
            title='Test Article',
            published_date=datetime.now() - timedelta(hours=1)
        )
    ]
    
    mock_summary = "Test Summary"
    
    with patch('src.main.RssReader') as mock_reader, \
         patch('src.main.Summarizer') as mock_summarizer, \
         patch('src.main.EmailSender') as mock_sender:
        
        # Setup mocks
        mock_reader.return_value.fetch_news.return_value = mock_news_items
        mock_summarizer.return_value.summarize.return_value = mock_summary
        
        # Test dry run mode
        process_news(days=1, feed_urls=['http://test.com'], dry_run=True)
        
        # Verify email was not sent
        mock_sender.return_value.send_email.assert_not_called()

@pytest.mark.asyncio
async def test_process_news_with_email():
    # Mock dependencies
    mock_news_items = [
        MagicMock(
            title='Test Article',
            published_date=datetime.now() - timedelta(hours=1)
        )
    ]
    
    mock_summary = "Test Summary"
    
    with patch('src.main.RssReader') as mock_reader, \
         patch('src.main.Summarizer') as mock_summarizer, \
         patch('src.main.EmailSender') as mock_sender:
        
        # Setup mocks
        mock_reader.return_value.fetch_news.return_value = mock_news_items
        mock_summarizer.return_value.summarize.return_value = mock_summary
        
        # Test normal mode
        process_news(days=1, feed_urls=['http://test.com'], dry_run=False)
        
        # Verify email was sent
        mock_sender.return_value.send_email.assert_called_once_with(mock_summary)
