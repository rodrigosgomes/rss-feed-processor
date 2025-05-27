#!/usr/bin/env python3
"""Test RSS reader with single feed and debug info."""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from agents.rss_reader import RssReader
from utils.logger import logger
import logging

# Set debug logging
logger.setLevel(logging.DEBUG)
for handler in logger.handlers:
    handler.setLevel(logging.DEBUG)

def test_single_feed():
    """Test with a single feed to debug date parsing."""
    
    # Test with just Bing News RSS
    test_feeds = ["https://www.bing.com/news/search?q=Product+management&format=rss"]
    
    logger.info(f"Testing single feed: {test_feeds[0]}")
    
    # Initialize RSS reader
    rss_reader = RssReader(test_feeds)
    
    # Fetch news from last 7 days to see more items
    news_items = rss_reader.fetch_news(days=7)
    
    logger.info(f"Final result: {len(news_items)} items found")
    
    return news_items

if __name__ == "__main__":
    try:
        items = test_single_feed()
        print(f"\nTEST COMPLETED: Found {len(items)} news items")
        if items:
            for i, item in enumerate(items[:2]):
                print(f"{i+1}. {item.title}")
                print(f"   Date: {item.published_date}")
                print(f"   Source: {item.source}")
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        print(f"ERROR: {str(e)}")
