#!/usr/bin/env python3
"""Quick test of RSS reader functionality."""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from agents.rss_reader import RssReader
from config.settings import RSS_FEED_URLS
from utils.logger import logger
import logging

# Set INFO level only for clean output
logger.setLevel(logging.INFO)
for handler in logger.handlers:
    handler.setLevel(logging.INFO)

def quick_test():
    """Quick test of RSS functionality."""
    
    # Test with just 3 feeds
    test_feeds = [
        "https://www.bing.com/news/search?q=Product+management&format=rss",
        "https://www.mindtheproduct.com/feed/", 
        "https://www.producttalk.org/feed/"
    ]
    
    print("🔄 Quick RSS Reader Test")
    print(f"Testing {len(test_feeds)} feeds...")
    
    rss_reader = RssReader(test_feeds)
    news_items = rss_reader.fetch_news(days=3)
    
    print(f"\n✅ Test Results:")
    print(f"   Found {len(news_items)} news items")
    
    if news_items:
        print(f"   Date range: {min(item.published_date for item in news_items).date()} to {max(item.published_date for item in news_items).date()}")
        print(f"   Sample titles:")
        for i, item in enumerate(news_items[:3]):
            print(f"     {i+1}. {item.title[:60]}...")
    
    return len(news_items)

if __name__ == "__main__":
    try:
        count = quick_test()
        print(f"\n🎉 SUCCESS: RSS reader working with {count} items found!")
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
