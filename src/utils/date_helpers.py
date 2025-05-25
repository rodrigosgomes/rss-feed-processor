from datetime import datetime
from collections import defaultdict

def format_date(date):
    """Convert a datetime object to a formatted date string."""
    if isinstance(date, str):
        try:
            date = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S%z')
        except ValueError:
            # If the first format fails, try RFC822 format
            date = datetime.strptime(date, '%a, %d %b %Y %H:%M:%S %z')
    return date.strftime('%B %d, %Y')

def get_date_range(days: int = 1):
    """Get the start and end dates for a given number of days."""
    from datetime import datetime, timedelta
    import pytz
    
    end_date = datetime.now(pytz.UTC)
    start_date = end_date - timedelta(days=days-1)  # -1 to include today
    return start_date, end_date

def group_news_by_date(news_items):
    """Group news items by their publication date."""
    grouped_news = defaultdict(list)
    for item in news_items:
        if hasattr(item, 'published_date'):
            pub_date = format_date(item.published_date)
            grouped_news[pub_date].append(item)
    return dict(grouped_news)