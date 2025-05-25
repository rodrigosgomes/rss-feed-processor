from datetime import datetime
from collections import defaultdict

def format_date(date_str):
    """Convert a date string to a formatted date."""
    date_obj = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S%z')
    return date_obj.strftime('%B %d, %Y')

def group_news_by_date(news_items):
    """Group news items by their publication date."""
    grouped_news = defaultdict(list)
    for item in news_items:
        pub_date = format_date(item['pub_date'])
        grouped_news[pub_date].append(item)
    return dict(grouped_news)