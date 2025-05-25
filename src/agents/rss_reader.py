import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pytz
from models.news_item import NewsItem
import xml.etree.ElementTree as ET
from typing import List, Optional
from utils.logger import logger
import email.utils
import time

class RssReader:
    def __init__(self, feed_urls: List[str]):
        self.feed_urls = feed_urls
        logger.info(f"Initialized RSS Reader with {len(feed_urls)} feeds")

    def parse_date(self, date_str: str) -> Optional[datetime]:
        try:
            # Try RFC822 format (standard for RSS)
            time_tuple = email.utils.parsedate_tz(date_str)
            if time_tuple:
                timestamp = email.utils.mktime_tz(time_tuple)
                return datetime.fromtimestamp(timestamp, pytz.UTC)
            
            # Try other common formats
            formats = [
                '%Y-%m-%dT%H:%M:%SZ',  # ISO format
                '%Y-%m-%d %H:%M:%S',   # Standard format
                '%a, %d %b %Y %H:%M:%S %z',  # RFC822 variant
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
            
            logger.warning(f"Could not parse date: {date_str}")
            return None
        except Exception as e:
            logger.error(f"Error parsing date {date_str}: {str(e)}")
            return None    
    def fetch_news(self, days: int = 1) -> List[NewsItem]:
        # Calculate the cutoff date in UTC
        cutoff_date = datetime.now(pytz.UTC) - timedelta(days=days)
        logger.info(f"RSS Reader: Fetching news from last {days} days")
        logger.info(f"RSS Reader: Date range {cutoff_date.date()} to {datetime.now(pytz.UTC).date()}")
        
        total_items = 0
        news_items = []
        for url in self.feed_urls:
            try:
                logger.info(f"RSS Reader: Processing feed: {url}")
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                
                feed_items = self._parse_feed(response.content, url)
                valid_items = [item for item in feed_items 
                             if item.published_date and item.published_date >= cutoff_date]
                
                news_items.extend(valid_items)
                total_items += len(valid_items)
                logger.info(f"RSS Reader: Found {len(valid_items)} items in date range from {url}")
                
            except requests.RequestException as e:
                logger.error(f"RSS Reader: Error fetching feed {url}: {str(e)}")
                continue
        
        logger.info(f"RSS Reader: Total items found in date range: {total_items}")
        return sorted(news_items, key=lambda x: x.published_date, reverse=True)