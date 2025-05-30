import sys
sys.path.append('src')

from agents.rss_reader import RssReader
from agents.summarizer import Summarizer
from config.settings import RSS_FEED_URLS
import pprint
from datetime import datetime, timedelta, date
import pytz

def debug_email_structure():
    print("=== Debugging Email Structure ===")
      # Get some news items
    rss_reader = RssReader(RSS_FEED_URLS[:1])  # Only use first feed for speed
    news_items = rss_reader.fetch_news(days=1)  # Only 1 day
    
    print(f"Found {len(news_items)} news items")
    
    if not news_items:
        print("No news items found, exiting")
        return
    
    # Summarize them
    summarizer = Summarizer()
    summary = summarizer.summarize(news_items, days=3)
    
    print("\n=== Summary Structure ===")
    print(f"Summary type: {type(summary)}")
    print(f"Summary keys: {list(summary.keys())}")
    
    for key, value in summary.items():
        print(f"\nKey: {key}")
        print(f"Key type: {type(key)}")
        print(f"Value type: {type(value)}")
        if isinstance(value, dict):
            print(f"Value keys: {list(value.keys())}")
            if 'items' in value:
                print(f"Items count: {len(value['items'])}")
        
        # Test the email sender logic
        is_date_like = (isinstance(key, datetime) or 
                       isinstance(key, str) or 
                       hasattr(key, 'year'))
        is_not_linkedin = key != 'linkedin_content'
        is_valid_value = isinstance(value, dict) and 'items' in value
        
        print(f"Is date-like: {is_date_like}")
        print(f"Is not linkedin: {is_not_linkedin}")
        print(f"Is valid value: {is_valid_value}")
        print(f"Would be included: {is_date_like and is_not_linkedin and is_valid_value}")

if __name__ == "__main__":
    debug_email_structure()
