from datetime import datetime, timedelta
import pytz
from typing import Union
from zoneinfo import ZoneInfo
from collections import defaultdict

def format_date(date: Union[datetime, str]) -> str:
    """Convert a datetime object or date string to a formatted date string."""
    if isinstance(date, str):
        date = parse_date_string(date)
    
    # Ensure the date has timezone info
    if date.tzinfo is None:
        date = date.replace(tzinfo=pytz.UTC)
    
    # Convert to local time for display
    local_tz = ZoneInfo('America/Sao_Paulo')  # Adjust for your timezone
    local_date = date.astimezone(local_tz)
    return local_date.strftime('%B %d, %Y')

def parse_date_string(date_str: str) -> datetime:
    """Parse a date string in various formats to datetime object."""
    formats = [
        '%Y-%m-%dT%H:%M:%S%z',      # ISO format with timezone
        '%Y-%m-%dT%H:%M:%SZ',       # ISO format UTC
        '%Y-%m-%dT%H:%M:%S.%f%z',   # ISO format with microseconds and timezone
        '%Y-%m-%dT%H:%M:%S.%fZ',    # ISO format with microseconds UTC
        '%a, %d %b %Y %H:%M:%S %z', # RFC822 format
        '%a, %d %b %Y %H:%M:%S %Z', # RFC822 with timezone name
        '%Y-%m-%d %H:%M:%S',        # Basic format
        '%Y-%m-%d',                 # Just date
    ]
    
    for fmt in formats:
        try:
            parsed_date = datetime.strptime(date_str, fmt)
            # If the parsed date has no timezone, assume UTC
            if parsed_date.tzinfo is None:
                parsed_date = parsed_date.replace(tzinfo=pytz.UTC)
            return parsed_date
        except ValueError:
            continue
    
    raise ValueError(f"Could not parse date string: {date_str}")

def get_date_range(days: int = 1):
    """Get the start and end dates for a given number of days."""
    local_tz = ZoneInfo('America/Sao_Paulo')  # Ajuste para seu fuso horário
    end_date = datetime.now(local_tz)
    
    # Set the end date to 23:59:59 of today
    end_date = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    # Calculate start date and set it to 00:00:00
    start_date = (end_date - timedelta(days=days-1)).replace(hour=0, minute=0, second=0, microsecond=0)
    
    return start_date, end_date

def group_news_by_date(news_items):
    """Group news items by their publication date."""
    grouped_news = defaultdict(list)
    for item in news_items:
        if hasattr(item, 'published_date') and item.published_date:
            try:
                pub_date = format_date(item.published_date)
                grouped_news[pub_date].append(item)
            except Exception as e:
                print(f"Error formatting date for item {item.title}: {str(e)}")
                continue
    return dict(grouped_news)