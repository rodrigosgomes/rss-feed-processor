#!/usr/bin/env python3
"""Quick test to verify the date filtering fix"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from datetime import datetime, timedelta
import pytz
from agents.rss_reader import RssReader
from agents.summarizer import Summarizer
from config.settings import RSS_FEED_URLS

def test_date_filtering():
    print("=== Testing Date Filtering Fix ===")
    
    # Get a small subset of feeds for quick testing
    test_feeds = RSS_FEED_URLS[:3]  # Just test first 3 feeds
    print(f"Testing with {len(test_feeds)} feeds")
    
    # Fetch news items
    rss_reader = RssReader(test_feeds)
    news_items = rss_reader.fetch_news(days=1)
    print(f"Fetched {len(news_items)} news items")
    
    if not news_items:
        print("No news items found - this might be the issue")
        return False
    
    # Filter items like main.py does
    date_cutoff = datetime.now(pytz.UTC) - timedelta(days=1)
    filtered_items = [item for item in news_items 
                     if item.published_date is not None and item.published_date >= date_cutoff]
    print(f"Items after main.py filtering: {len(filtered_items)}")
    
    if not filtered_items:
        print("No items pass main.py filtering")
        return False
    
    # Test summarizer
    summarizer = Summarizer()
    summary = summarizer.summarize(filtered_items, days=1)
    print(f"Summarizer returned: {type(summary)}")
    print(f"Summary keys: {list(summary.keys()) if summary else 'Empty'}")
    
    if summary:
        print("SUCCESS: Summarizer found valid news items!")
        return True
    else:
        print("FAILURE: Summarizer still returns empty results")
        return False

if __name__ == "__main__":
    success = test_date_filtering()
    print(f"\nTest result: {'PASSED' if success else 'FAILED'}")
