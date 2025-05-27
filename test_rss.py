#!/usr/bin/env python3
"""Test RSS reader with optimized feed configuration."""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from agents.rss_reader import RssReader
from config.settings import RSS_FEED_URLS
from utils.logger import logger

def test_rss_reader():
    """Test the RSS reader with a small subset of feeds."""
    
    # Use first 3 feeds for testing
    test_feeds = RSS_FEED_URLS[:3]
    logger.info(f"Testing RSS reader with {len(test_feeds)} feeds")
    
    # Initialize RSS reader
    rss_reader = RssReader(test_feeds)
    
    # Fetch news from last 2 days to increase chances of finding items
    news_items = rss_reader.fetch_news(days=2)
    
    logger.info(f"Test Results:")
    logger.info(f"- Total news items found: {len(news_items)}")
    
    if news_items:
        logger.info(f"- Sample items:")
        for i, item in enumerate(news_items[:3]):  # Show first 3 items
            logger.info(f"  {i+1}. {item.title[:60]}...")
            logger.info(f"     Date: {item.published_date}")
            logger.info(f"     Source: {item.source}")
    else:
        logger.warning("No news items found!")
    
    return len(news_items)

if __name__ == "__main__":
    try:
        count = test_rss_reader()
        print(f"\nTEST COMPLETED: Found {count} news items")
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        print(f"ERROR: {str(e)}")
