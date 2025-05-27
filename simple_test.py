#!/usr/bin/env python3
"""Simple RSS verification test."""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from agents.rss_reader import RssReader
from utils.logger import logger
import logging

# Set WARNING level for minimal output
logger.setLevel(logging.WARNING)
for handler in logger.handlers:
    handler.setLevel(logging.WARNING)

def simple_test():
    """Simple test of RSS functionality."""
    
    print("🔄 Simple RSS Test")
    
    # Test with just 1 reliable feed
    test_feeds = ["https://www.bing.com/news/search?q=Product+management&format=rss"]
    
    try:
        rss_reader = RssReader(test_feeds)
        news_items = rss_reader.fetch_news(days=7)  # 7 days to ensure we get items
        
        print(f"✅ Found {len(news_items)} news items")
        
        if news_items:
            print(f"📄 Sample: {news_items[0].title[:50]}...")
            print(f"📅 Date: {news_items[0].published_date}")
            print(f"🔗 Link: {news_items[0].link[:50]}...")
            
        return len(news_items)
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return 0

if __name__ == "__main__":
    count = simple_test()
    if count > 0:
        print(f"\n🎉 RSS SYSTEM WORKING: {count} items found!")
    else:
        print(f"\n❌ RSS system needs attention")
