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
            return None      def fetch_news(self, days: int = 1) -> List[NewsItem]:
        # Get date range using helper
        from utils.date_helpers import get_date_range
        start_date, end_date = get_date_range(days)
        logger.info(f"RSS Reader: Fetching news from last {days} days")
        logger.info(f"RSS Reader: Date range {start_date.date()} to {end_date.date()}")
        
        total_items = 0
        news_items = []
        for url in self.feed_urls:
            try:
                logger.info(f"RSS Reader: Processing feed: {url}")
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                
                feed_items = self._parse_feed(response.content, url)
                valid_items = [item for item in feed_items 
                             if item.published_date and start_date <= item.published_date <= end_date]
                
                news_items.extend(valid_items)
                total_items += len(valid_items)
                logger.info(f"RSS Reader: Found {len(valid_items)} items in date range from {url}")
                
            except requests.RequestException as e:
                logger.error(f"RSS Reader: Error fetching feed {url}: {str(e)}")
                continue
        
        logger.info(f"RSS Reader: Total items found in date range: {total_items}")
        return sorted(news_items, key=lambda x: x.published_date, reverse=True)
    
    def _parse_feed(self, content: bytes, feed_url: str) -> List[NewsItem]:
        """Parse RSS feed content and return a list of NewsItem objects."""
        try:
            root = ET.fromstring(content)
            items = root.findall('.//item')
            logger.info(f"RSS Reader: Found {len(items)} raw items in feed")
            
            news_items = []
            for item in items:
                try:
                    title = item.find('title')
                    description = item.find('description')
                    link = item.find('link')
                    pub_date = item.find('pubDate')
                    
                    if not all([title is not None, description is not None, 
                              link is not None, pub_date is not None]):
                        continue
                    
                    published_date = self.parse_date(pub_date.text)
                    if not published_date:
                        continue
                    
                    news_item = NewsItem(
                        title=title.text,
                        description=BeautifulSoup(description.text, 'html.parser').get_text(),
                        link=link.text,
                        published_date=published_date,
                        source=feed_url
                    )
                    news_items.append(news_item)
                    
                except Exception as e:
                    logger.error(f"RSS Reader: Error parsing item: {str(e)}")
                    continue
                    
            return news_items
            
        except ET.ParseError as e:
            logger.error(f"RSS Reader: Error parsing feed XML: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"RSS Reader: Unexpected error parsing feed: {str(e)}")
            return []