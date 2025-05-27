#!/usr/bin/env python3
"""Test RSS reader with optimized feed configuration."""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from agents.rss_reader import RssReader
from config.settings import RSS_FEED_URLS
from utils.logger import logger

def test_optimized_feeds():
    """Test the RSS reader with optimized feeds."""
    
    # Use first 5 feeds for testing
    test_feeds = RSS_FEED_URLS[:5]
    logger.info(f"Testing RSS reader with {len(test_feeds)} optimized feeds")
    logger.info("Feeds being tested:")
    for i, feed in enumerate(test_feeds, 1):
        logger.info(f"  {i}. {feed}")
    
    # Initialize RSS reader
    rss_reader = RssReader(test_feeds)
    
    # Fetch news from last 3 days
    news_items = rss_reader.fetch_news(days=3)
    
    logger.info(f"\n=== TEST RESULTS ===")
    logger.info(f"Total news items found: {len(news_items)}")
    
    if news_items:
        logger.info(f"\nSample items (first 5):")
        for i, item in enumerate(news_items[:5]):
            logger.info(f"  {i+1}. {item.title[:80]}...")
            logger.info(f"     Date: {item.published_date}")
            logger.info(f"     Source: {item.source.split('/')[-1] if '/' in item.source else item.source}")
            logger.info("")
    else:
        logger.warning("No news items found!")
    
    return news_items

if __name__ == "__main__":
    try:
        items = test_optimized_feeds()
        print(f"\n🎉 TEST COMPLETED SUCCESSFULLY!")
        print(f"Found {len(items)} news items from optimized RSS feeds")
        
        if items:
            # Group by source for summary
            by_source = {}
            for item in items:
                source = item.source.split('/')[-1] if '/' in item.source else item.source
                by_source[source] = by_source.get(source, 0) + 1
            
            print("\nItems by source:")
            for source, count in by_source.items():
                print(f"  {source}: {count} items")
                
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        print(f"❌ ERROR: {str(e)}")
