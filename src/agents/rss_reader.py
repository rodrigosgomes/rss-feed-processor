import requests
from bs4 import BeautifulSoup
from datetime import datetime
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

    def fetch_news(self) -> List[NewsItem]:
        news_items = []
        for url in self.feed_urls:
            try:
                logger.info(f"Fetching news from: {url}")
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                
                # Parse XML content
                root = ET.fromstring(response.content)
                
                # Get channel info
                channel = root.find('channel')
                feed_title = channel.find('title').text if channel.find('title') is not None else "Unknown Source"
                
                items = channel.findall('item')
                logger.info(f"Found {len(items)} articles in {feed_title}")
                
                # Process each item
                for item in items:
                    try:
                        title = item.find('title').text if item.find('title') is not None else "No Title"
                        link = item.find('link').text if item.find('link') is not None else None
                        description = item.find('description').text if item.find('description') is not None else ""
                        
                        # Parse publication date
                        pub_date = None
                        date_elem = item.find('pubDate')
                        if date_elem is not None and date_elem.text:
                            pub_date = self.parse_date(date_elem.text)
                        
                        if not pub_date:
                            logger.warning(f"No valid publication date for article: {title}")
                            continue
                        
                        news_items.append(NewsItem(
                            title=title,
                            link=link,
                            description=description,
                            published_date=pub_date,
                            source=feed_title
                        ))
                        
                    except Exception as e:
                        logger.error(f"Error processing item: {str(e)}")
                        continue
                        
            except requests.RequestException as e:
                logger.error(f"Error fetching feed {url}: {str(e)}")
                continue
            except ET.ParseError as e:
                logger.error(f"Error parsing feed {url}: {str(e)}")
                continue
            
        return news_items