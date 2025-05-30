import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from datetime import datetime, date
import pytz
from models.news_item import NewsItem

# Create a mock summarizer output to debug
def debug_summarizer_structure():
    # This is what the summarizer returns
    mock_date = date(2024, 1, 15)
    mock_news_item = NewsItem(
        title="Test Article",
        description="Test description",
        link="http://example.com",
        published_date=datetime.now(pytz.UTC),
        source="Test Source",
        summary="Test summary"
    )
    
    # This is the structure returned by summarizer.summarize()
    summarizer_output = {
        mock_date: {  # This is a date object, not datetime
            'items': [mock_news_item]
        },
        'linkedin_content': 'Test LinkedIn content'
    }
    
    print("Summarizer output structure:")
    print(f"Keys: {list(summarizer_output.keys())}")
    print(f"Key types: {[type(k) for k in summarizer_output.keys()]}")
    
    # Test the email sender filtering logic
    filtered_news = {}
    linkedin_content = None
    
    for key, value in summarizer_output.items():
        print(f"\nProcessing key: {key} (type: {type(key)})")
        print(f"Value type: {type(value)}")
        
        # This is the current filtering logic from email_sender.py
        if (isinstance(key, datetime) or 
            isinstance(key, str) or 
            hasattr(key, 'year')) and key != 'linkedin_content':
            print(f"Key {key} passes the filter check")
            if isinstance(value, dict) and 'items' in value:
                print(f"Value has 'items' - adding to filtered_news")
                filtered_news[key] = value
            else:
                print(f"Value doesn't have 'items' structure")
        elif key == 'linkedin_content':
            print(f"Found LinkedIn content")
            linkedin_content = value
        else:
            print(f"Key {key} failed filter check")
    
    print(f"\nFiltered news keys: {list(filtered_news.keys())}")
    print(f"LinkedIn content: {linkedin_content is not None}")
    
    # Check if we would get the error
    if not filtered_news:
        print("ERROR: No valid news items found in data - this is the error we're seeing!")
    else:
        print("SUCCESS: Valid news items found")

if __name__ == "__main__":
    debug_summarizer_structure()
