import sys
sys.path.append('src')

from datetime import datetime, date
from utils.email_sender import EmailSender
from config.settings import EMAIL_SETTINGS
import pytz

def test_email_sender_logic():
    print("=== Testing Email Sender Logic ===")
    
    # Create test data structure similar to what Summarizer returns
    test_date = date(2025, 5, 29)
    test_summary = {
        test_date: {
            'items': [
                {
                    'title': 'Test Article 1',
                    'description': 'Test description 1',
                    'link': 'http://example.com/1',
                    'summary': 'Test summary 1'
                },
                {
                    'title': 'Test Article 2', 
                    'description': 'Test description 2',
                    'link': 'http://example.com/2',
                    'summary': 'Test summary 2'
                }
            ]
        },
        'linkedin_content': 'Test LinkedIn content'
    }
    
    print(f"Test summary structure:")
    print(f"Keys: {list(test_summary.keys())}")
    print(f"Key types: {[type(k) for k in test_summary.keys()]}")
    
    # Test the EmailSender logic
    filtered_news = {}
    linkedin_content = None
    
    for key, value in test_summary.items():
        print(f"\nProcessing key: {key} (type: {type(key)})")
        
        is_datetime = isinstance(key, datetime)
        is_str = isinstance(key, str)
        has_year = hasattr(key, 'year')
        is_not_linkedin = key != 'linkedin_content'
        
        print(f"  - isinstance(key, datetime): {is_datetime}")
        print(f"  - isinstance(key, str): {is_str}")
        print(f"  - hasattr(key, 'year'): {has_year}")
        print(f"  - key != 'linkedin_content': {is_not_linkedin}")
        
        date_condition = (is_datetime or is_str or has_year) and is_not_linkedin
        print(f"  - Date condition: {date_condition}")
        
        if date_condition:
            if isinstance(value, dict) and 'items' in value:
                print(f"  - Valid value structure: YES")
                filtered_news[key] = value
            else:
                print(f"  - Valid value structure: NO")
        elif key == 'linkedin_content':
            print(f"  - Setting LinkedIn content")
            linkedin_content = value
    
    print(f"\nFiltered news keys: {list(filtered_news.keys())}")
    print(f"LinkedIn content: {linkedin_content is not None}")
    
    if not filtered_news:
        print("ERROR: No valid news items found in data")
    else:
        print("SUCCESS: Valid news items found!")
        total_articles = sum(len(date_data['items']) for date_data in filtered_news.values())
        print(f"Total articles: {total_articles}")

if __name__ == "__main__":
    test_email_sender_logic()
