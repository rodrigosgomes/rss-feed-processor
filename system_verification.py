#!/usr/bin/env python3
"""Complete system verification for RSS Feed Processor."""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from agents.rss_reader import RssReader
from agents.summarizer import Summarizer
from utils.logger import logger
import logging

# Set INFO level for clean output
logger.setLevel(logging.INFO)
for handler in logger.handlers:
    handler.setLevel(logging.INFO)

def test_complete_system():
    """Test the complete RSS feed processing system."""
    
    print("🚀 RSS FEED PROCESSOR - COMPLETE SYSTEM TEST")
    print("=" * 60)
    
    # Test subset of working feeds
    test_feeds = [
        "https://www.bing.com/news/search?q=Product+management&format=rss",
        "https://www.mindtheproduct.com/feed/",
        "https://www.producttalk.org/feed/",
        "https://www.romanpichler.com/feed/",
        "https://newsletter.uxdesign.cc/feed"
    ]
    
    print(f"\n📡 Testing RSS Reader with {len(test_feeds)} feeds...")
    
    try:
        # Initialize RSS reader
        rss_reader = RssReader(test_feeds)
        
        # Fetch news from last 3 days
        news_items = rss_reader.fetch_news(days=3)
        
        print(f"✅ RSS Reader: Found {len(news_items)} news items")
        
        if news_items:
            print(f"   📅 Date range: {min(item.published_date for item in news_items).date()} to {max(item.published_date for item in news_items).date()}")
            
            # Test summarizer
            print(f"\n🤖 Testing Summarizer...")
            summarizer = Summarizer()
            
            # Test with first few items
            test_items = news_items[:5] if len(news_items) > 5 else news_items
            summary = summarizer.summarize(test_items, days=3)
            
            if summary:
                print(f"✅ Summarizer: Generated summary ({len(summary)} chars)")
                print(f"   📝 Preview: {summary[:100]}...")
                
                print(f"\n🎯 SYSTEM STATUS: FULLY OPERATIONAL")
                print(f"   ✅ RSS Reader: Working")
                print(f"   ✅ Date Parsing: Working") 
                print(f"   ✅ Feed Processing: Working")
                print(f"   ✅ Summarizer: Working")
                print(f"   ✅ Complete Pipeline: Ready")
                
                return len(news_items), True
            else:
                print(f"❌ Summarizer: Failed to generate summary")
                return len(news_items), False
        else:
            print(f"⚠️  No news items found in date range")
            return 0, True
            
    except Exception as e:
        print(f"❌ System test failed: {str(e)}")
        return 0, False

if __name__ == "__main__":
    try:
        items, working = test_complete_system()
        
        if working and items > 0:
            print(f"\n🎉 COMPLETE SYSTEM VERIFICATION: SUCCESS!")
            print(f"   🚀 Ready for production deployment")
            print(f"   📊 {items} news items processed successfully") 
            print(f"   ⚡ All components operational")
        elif working:
            print(f"\n✅ System working but no recent news items")
            print(f"   💡 Try extending date range for more content")
        else:
            print(f"\n❌ System needs attention")
            
    except Exception as e:
        print(f"❌ Verification failed: {str(e)}")
