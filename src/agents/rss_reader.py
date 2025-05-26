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
import random
from urllib.parse import urlparse

class RssReader:
    def __init__(self, feed_urls: List[str]):
        self.feed_urls = feed_urls
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; ProductReader/1.0; +https://github.com/yourusername/product_reader)',
            'Accept': 'application/rss+xml, application/xml, application/atom+xml, text/xml, */*'
        }
        self.max_retries = 3
        self.base_delay = 1  # Base delay in seconds
        logger.info(f"Initialized RSS Reader with {len(feed_urls)} feeds")

    def _get_with_retry(self, url: str) -> requests.Response:
        """Make HTTP request with retry mechanism and exponential backoff."""
        retries = 0
        last_error = None

        while retries < self.max_retries:
            try:
                # Add a small random delay to prevent rate limiting
                time.sleep(random.uniform(0, 0.5))
                
                # Get the domain to use as referer
                parsed_url = urlparse(url)
                domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
                
                # Add referer header for the specific request
                headers = {**self.headers, 'Referer': domain}
                
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                return response
            
            except requests.RequestException as e:
                last_error = e
                retries += 1
                if retries < self.max_retries:
                    delay = self.base_delay * (2 ** (retries - 1)) + random.uniform(0, 0.5)
                    logger.warning(f"Attempt {retries} failed for {url}. Retrying in {delay:.1f} seconds. Error: {str(e)}")
                    time.sleep(delay)
                continue
        
        raise last_error

    def parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string from RSS feed in various formats."""
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
                '%Y-%m-%d',  # Just date
            ]
            
            for fmt in formats:
                try:
                    dt = datetime.strptime(date_str, fmt)
                    return dt.replace(tzinfo=pytz.UTC) if dt.tzinfo is None else dt
                except ValueError:
                    continue
            
            logger.warning(f"Could not parse date: {date_str}")
            return None
        except Exception as e:
            logger.error(f"Error parsing date {date_str}: {str(e)}")
            return None
            
    def fetch_news(self, days: int = 1) -> List[NewsItem]:
        """Fetch news from RSS feeds and filter by date range."""
        from utils.date_helpers import get_date_range
        start_date, end_date = get_date_range(days)
        logger.info(f"RSS Reader: Fetching news from last {days} days")
        logger.info(f"RSS Reader: Date range {start_date.date()} to {end_date.date()}")
        
        news_items = []
        successful_feeds = 0
        skipped_feeds = 0
        total_items = 0
        
        for url in self.feed_urls:
            try:
                logger.info(f"RSS Reader: Processing feed: {url}")
                response = self._get_with_retry(url)
                
                feed_items = self._parse_feed(response.content, url)
                logger.info(f"RSS Reader: Parsed {len(feed_items)} items from {url}")
                
                if not feed_items:
                    logger.warning(f"RSS Reader: No items found in feed {url}")
                    skipped_feeds += 1
                    continue
                
                items_with_dates = [item for item in feed_items if item.published_date is not None]
                if len(items_with_dates) < len(feed_items):
                    logger.warning(f"RSS Reader: {len(feed_items) - len(items_with_dates)} items had invalid dates in {url}")
                
                valid_items = [item for item in items_with_dates 
                             if start_date <= item.published_date <= end_date]
                
                logger.info(f"RSS Reader: Found {len(valid_items)} items in date range from {url}")
                if len(valid_items) == 0:
                    logger.warning(f"RSS Reader: All items from {url} were outside date range {start_date.date()} to {end_date.date()}")
                    skipped_feeds += 1
                else:
                    successful_feeds += 1
                
                news_items.extend(valid_items)
                total_items += len(valid_items)
                
            except requests.RequestException as e:
                logger.error(f"RSS Reader: Error fetching feed {url}: {str(e)}")
                skipped_feeds += 1
                continue
            except Exception as e:
                logger.error(f"RSS Reader: Unexpected error processing feed {url}: {str(e)}")
                skipped_feeds += 1
                continue
        
        logger.info(f"RSS Reader: Summary:")
        logger.info(f"- Total feeds processed: {len(self.feed_urls)}")
        logger.info(f"- Successful feeds: {successful_feeds}")
        logger.info(f"- Skipped/failed feeds: {skipped_feeds}")
        logger.info(f"- Total valid items found: {total_items}")
        
        if total_items == 0:
            logger.warning("RSS Reader: No valid news items found in any feed!")
        
        return sorted(news_items, key=lambda x: x.published_date, reverse=True)
    
    def _parse_feed(self, content: bytes, feed_url: str) -> List[NewsItem]:
        """Parse RSS feed content and return a list of NewsItem objects."""
        try:
            # Try parsing as XML first
            root = ET.fromstring(content)
            
            # Detect feed type (RSS or Atom)
            is_atom = root.tag.endswith('feed')
            
            if is_atom:
                items = root.findall('{http://www.w3.org/2005/Atom}entry') or root.findall('entry')
                return self._parse_atom_items(items, feed_url)
            else:
                items = root.findall('.//item')
                return self._parse_rss_items(items, feed_url)
            
        except ET.ParseError as e:
            # Try parsing with BeautifulSoup as fallback
            logger.warning(f"RSS Reader: XML parsing failed for {feed_url}, trying BeautifulSoup")
            try:
                soup = BeautifulSoup(content, 'xml')
                items = soup.find_all('item') or soup.find_all('entry')
                return self._parse_items_from_soup(items, feed_url)
            except Exception as soup_error:
                logger.error(f"RSS Reader: BeautifulSoup parsing also failed for {feed_url}: {str(soup_error)}")
                return []
        except Exception as e:
            logger.error(f"RSS Reader: Unexpected error parsing feed from {feed_url}: {str(e)}")
            return []

    def _parse_rss_items(self, items, feed_url: str) -> List[NewsItem]:
        """Parse RSS format items."""
        news_items = []
        for item in items:
            try:
                title_elem = item.find('title')
                desc_elem = item.find('description')
                link_elem = item.find('link')
                date_elem = (item.find('pubDate') or item.find('published') or 
                           item.find('date') or item.find('dc:date'))
                
                if not title_elem is None and not link_elem is None:
                    title = title_elem.text.strip()
                    link = link_elem.text.strip() if link_elem.text else link_elem.get('href', '')
                    
                    # Get description from multiple possible elements
                    desc_text = None
                    if desc_elem is not None and desc_elem.text:
                        desc_text = desc_elem.text
                    elif item.find('content:encoded') is not None:
                        desc_text = item.find('content:encoded').text
                    else:
                        desc_text = title
                    
                    # Parse date
                    published_date = None
                    if date_elem is not None and date_elem.text:
                        published_date = self.parse_date(date_elem.text.strip())
                    
                    if published_date:
                        news_item = NewsItem(
                            title=title,
                            description=BeautifulSoup(desc_text, 'html.parser').get_text(),
                            link=link,
                            published_date=published_date,
                            source=feed_url
                        )
                        news_items.append(news_item)
                    
            except Exception as e:
                logger.error(f"RSS Reader: Error parsing RSS item from {feed_url}: {str(e)}")
                continue
        
        return news_items

    def _parse_atom_items(self, items, feed_url: str) -> List[NewsItem]:
        """Parse Atom format items."""
        news_items = []
        for item in items:
            try:
                ns = {'atom': 'http://www.w3.org/2005/Atom'}
                
                # Extract elements with namespace awareness
                title = item.find('atom:title', ns) or item.find('title')
                content = item.find('atom:content', ns) or item.find('content')
                summary = item.find('atom:summary', ns) or item.find('summary')
                link = item.find('atom:link', ns) or item.find('link')
                published = (item.find('atom:published', ns) or item.find('published') or
                           item.find('atom:updated', ns) or item.find('updated'))
                
                if title is not None and link is not None:
                    # Get link from href attribute
                    link_href = link.get('href', '')
                    
                    # Get description from content or summary
                    desc_text = None
                    if content is not None and content.text:
                        desc_text = content.text
                    elif summary is not None and summary.text:
                        desc_text = summary.text
                    else:
                        desc_text = title.text
                    
                    # Parse date
                    published_date = None
                    if published is not None and published.text:
                        published_date = self.parse_date(published.text.strip())
                    
                    if published_date:
                        news_item = NewsItem(
                            title=title.text.strip(),
                            description=BeautifulSoup(desc_text, 'html.parser').get_text(),
                            link=link_href,
                            published_date=published_date,
                            source=feed_url
                        )
                        news_items.append(news_item)
                    
            except Exception as e:
                logger.error(f"RSS Reader: Error parsing Atom item from {feed_url}: {str(e)}")
                continue
        
        return news_items

    def _parse_items_from_soup(self, items, feed_url: str) -> List[NewsItem]:
        """Parse items using BeautifulSoup as fallback."""
        news_items = []
        for item in items:
            try:
                title = item.find('title')
                desc = item.find('description') or item.find('content') or item.find('summary')
                link = item.find('link')
                date = (item.find('pubDate') or item.find('published') or 
                       item.find('updated') or item.find('date'))
                
                if title and link:
                    # Get link text or href attribute
                    link_text = link.text.strip() if link.text else link.get('href', '')
                    
                    # Get description
                    desc_text = desc.text if desc else title.text
                    
                    # Parse date
                    published_date = None
                    if date and date.text:
                        published_date = self.parse_date(date.text.strip())
                    
                    if published_date:
                        news_item = NewsItem(
                            title=title.text.strip(),
                            description=BeautifulSoup(desc_text, 'html.parser').get_text(),
                            link=link_text,
                            published_date=published_date,
                            source=feed_url
                        )
                        news_items.append(news_item)
                    
            except Exception as e:
                logger.error(f"RSS Reader: Error parsing item using BeautifulSoup from {feed_url}: {str(e)}")
                continue
        
        return news_items
