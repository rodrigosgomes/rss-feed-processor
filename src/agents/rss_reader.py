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
        
        # Primary headers (work for 25/27 feeds based on diagnostics)
        self.primary_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/rss+xml, application/xml, text/xml, application/atom+xml, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }
        
        # Fallback headers (work for 2/27 remaining feeds)
        self.fallback_headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; ProductReader/1.0)',
            'Accept': '*/*',
            'Accept-Language': 'en',
        }
        
        # Known blocked feeds to skip or handle differently
        self.blocked_feeds = {
            "https://theproductmanager.com/feed/",
            "https://www.bringthedonuts.com/blog/"
        }
        
        # Known empty feeds to handle differently
        self.empty_feeds = {
            "https://www.productplan.com/blog/feed/",
            "https://melissaperri.com/blog",
            "https://www.carlsnewsletter.com/?format=rss",
            "https://www.productmanagementtoday.com/product-management/"
        }
        
        self.max_retries = 3
        self.base_delay = 1  # Base delay in seconds
        logger.info(f"Initialized RSS Reader with {len(feed_urls)} feeds")

    def _get_with_retry(self, url: str) -> requests.Response:
        """Make HTTP request with retry mechanism and exponential backoff."""
        headers_list = [self.primary_headers, self.fallback_headers]
        
        for attempt in range(self.max_retries):
            for header_idx, headers in enumerate(headers_list):
                try:
                    # Add random delay to prevent being blocked
                    delay = self.base_delay * (2 ** attempt) + random.uniform(0, 1)
                    if attempt > 0 or header_idx > 0:
                        logger.debug(f"Waiting {delay:.2f}s before retry attempt {attempt+1}, headers {header_idx+1}")
                        time.sleep(delay)
                    
                    logger.debug(f"Fetching {url} with headers set {header_idx+1}")
                    response = requests.get(url, headers=headers, timeout=30)
                    response.raise_for_status()
                    
                    logger.debug(f"Successfully fetched {url} with headers set {header_idx+1}")
                    return response
                    
                except requests.exceptions.RequestException as e:
                    logger.debug(f"Request failed for {url} with headers {header_idx+1}: {str(e)}")
                    continue
            
            logger.warning(f"Attempt {attempt+1} failed for {url}, retrying...")
        
        raise requests.exceptions.RequestException(f"Failed to fetch {url} after {self.max_retries} attempts with all header variants")

    def parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string from RSS feed in various formats."""
        if not date_str:
            return None
            
        try:
            # Clean the date string
            date_str = date_str.strip()
            
            # Try different date formats commonly used in RSS feeds
            formats = [
                '%a, %d %b %Y %H:%M:%S %z', # RFC822 format
                '%a, %d %b %Y %H:%M:%S %Z', # RFC822 with timezone name
                '%a, %d %b %Y %H:%M:%S',    # RFC822 without timezone
                '%Y-%m-%d %H:%M:%S',        # Basic format
                '%d %b %Y %H:%M:%S %z',     # Short RFC822
                '%d %b %Y %H:%M:%S',        # Short date time
                '%Y-%m-%d',                 # Just date
            ]
            
            for fmt in formats:
                try:
                    dt = datetime.strptime(date_str, fmt)
                    # Se a data não tem timezone, assume UTC
                    if dt.tzinfo is None:
                        dt = dt.replace(tzinfo=pytz.UTC)
                    return dt
                except ValueError:
                    continue
            
            # Try parsing with email.utils.parsedate_tz (handles RFC 2822 dates)
            try:
                parsed = email.utils.parsedate_tz(date_str)
                if parsed:
                    timestamp = email.utils.mktime_tz(parsed)
                    return datetime.fromtimestamp(timestamp, tz=pytz.UTC)
            except (ValueError, TypeError):
                pass
            
            logger.warning(f"Could not parse date: {date_str}")
            return None
            
        except Exception as e:
            logger.error(f"Error parsing date '{date_str}': {str(e)}")
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
        items_without_dates = 0
        
        for url in self.feed_urls:
            try:
                logger.info(f"RSS Reader: Processing feed: {url}")
                
                # Check if this is a known blocked feed
                if url in self.blocked_feeds:
                    logger.warning(f"RSS Reader: Skipping known blocked feed: {url}")
                    skipped_feeds += 1
                    continue
                
                # Check if this is a known empty feed
                if url in self.empty_feeds:
                    logger.warning(f"RSS Reader: Skipping known empty feed: {url}")
                    skipped_feeds += 1
                    continue
                
                response = self._get_with_retry(url)
                
                feed_items = self._parse_feed(response.content, url)
                logger.info(f"RSS Reader: Parsed {len(feed_items)} raw items from {url}")
                
                if not feed_items:
                    logger.warning(f"RSS Reader: No items found in feed {url}")
                    skipped_feeds += 1
                    continue
                
                # Verificar quais itens têm datas válidas
                items_with_dates = []
                for item in feed_items:
                    if item.published_date is None:
                        items_without_dates += 1
                        logger.debug(f"Item sem data: {item.title} from {url}")
                        continue
                    items_with_dates.append(item)
                
                if len(items_with_dates) < len(feed_items):
                    logger.warning(f"RSS Reader: {len(feed_items) - len(items_with_dates)} items had invalid dates in {url}")
                
                # Filtrar por data
                valid_items = []
                for item in items_with_dates:
                    try:
                        if start_date <= item.published_date <= end_date:
                            valid_items.append(item)
                        else:
                            logger.debug(f"Item fora do range de datas: {item.title} - {item.published_date} from {url}")
                    except Exception as e:
                        logger.error(f"Error comparing dates for {item.title}: {str(e)}")
                        continue
                
                logger.info(f"RSS Reader: Found {len(valid_items)} items in date range from {url}")
                if len(valid_items) == 0:
                    logger.warning(f"RSS Reader: All items from {url} were outside date range {start_date.date()} to {end_date.date()}")
                    if items_with_dates:
                        logger.debug(f"Date range for {url}: {min(item.published_date for item in items_with_dates)} to {max(item.published_date for item in items_with_dates)}")
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
        logger.info(f"- Items without dates: {items_without_dates}")
        
        if total_items == 0:
            logger.warning("RSS Reader: No valid news items found in any feed!")
        
        return sorted(news_items, key=lambda x: x.published_date, reverse=True)

    def _parse_feed(self, content: bytes, feed_url: str) -> List[NewsItem]:
        """Parse RSS feed content and return a list of NewsItem objects."""
        try:
            logger.debug(f"Feed content from {feed_url}: {content[:500].decode('utf-8', errors='ignore')}...")
            
            try:
                # Try parsing as XML first
                root = ET.fromstring(content)
                
                # Detect feed type (RSS or Atom) and try multiple paths
                is_atom = root.tag.endswith('feed')
                logger.debug(f"Feed type for {feed_url}: {'Atom' if is_atom else 'RSS'}")
                
                if is_atom:
                    # Try multiple possible paths for Atom entries
                    items = []
                    for path in ['{http://www.w3.org/2005/Atom}entry', 'entry', './/entry']:
                        found_items = root.findall(path)
                        if found_items:
                            logger.debug(f"Found {len(found_items)} Atom entries with path {path}")
                            items = found_items
                            break
                            
                    if not items:
                        # Try finding items in namespaced elements
                        ns = {'atom': 'http://www.w3.org/2005/Atom'}
                        items = root.findall('.//atom:entry', ns)
                        if items:
                            logger.debug(f"Found {len(items)} Atom entries using namespace")
                    
                    return self._parse_atom_items(items, feed_url)
                else:
                    # Try multiple possible paths for RSS items
                    items = []
                    for path in ['.//item', 'channel/item', './channel/item', 'item']:
                        found_items = root.findall(path)
                        if found_items:
                            logger.debug(f"Found {len(found_items)} RSS items with path {path}")
                            items = found_items
                            break
                            
                    if not items:
                        # Try with explicit RSS namespace
                        ns = {'rss': 'http://purl.org/rss/1.0/'}
                        items = root.findall('.//rss:item', ns)
                        if items:
                            logger.debug(f"Found {len(items)} RSS items using namespace")
                    
                    return self._parse_rss_items(items, feed_url)
                    
            except ET.ParseError as xml_error:
                logger.warning(f"RSS Reader: XML parsing failed for {feed_url}: {str(xml_error)}")
                logger.debug("Trying BeautifulSoup as fallback")
                
                # Try parsing with BeautifulSoup as fallback
                soup = BeautifulSoup(content, 'lxml-xml')  # Using lxml parser for better XML handling
                
                # Try to find items with BeautifulSoup
                items = (soup.find_all('item') or 
                        soup.find_all('entry') or 
                        soup.select('channel > item') or 
                        soup.select('feed > entry'))
                
                if items:
                    logger.debug(f"Found {len(items)} items with BeautifulSoup in {feed_url}")
                else:
                    logger.debug(f"No items found with BeautifulSoup in {feed_url}")
                    # Log the actual structure we found
                    channel = soup.find('channel')
                    if channel:
                        logger.debug(f"Channel content: {str(channel)[:500]}...")
                return self._parse_items_from_soup(items, feed_url)
                
        except Exception as e:
            logger.error(f"RSS Reader: Unexpected error parsing feed from {feed_url}: {str(e)}")
            logger.debug(f"Full error for {feed_url}:", exc_info=True)
            return []

    def _parse_rss_items(self, items, feed_url: str) -> List[NewsItem]:
        """Parse RSS format items."""
        news_items = []
        logger.debug(f"RSS Parser: Processing {len(items)} items from {feed_url}")
        
        for i, item in enumerate(items):
            try:
                title_elem = item.find('title')
                desc_elem = item.find('description')
                link_elem = item.find('link')                # Look for date elements with various approaches
                date_elem = None
                # Try standard RSS date fields
                for date_tag in ['pubDate', 'published', 'date', 'dc:date', 'pubdate']:
                    date_elem = item.find(date_tag)
                    if date_elem is not None:
                        logger.debug(f"RSS Item {i+1}: Found date element '{date_tag}'")
                        break
                
                # If still no date found, try looking at all child elements for date-like content
                if date_elem is None:
                    for child in item:
                        if 'date' in child.tag.lower() or 'pub' in child.tag.lower():
                            date_elem = child
                            logger.debug(f"RSS Item {i+1}: Found date-like element '{child.tag}'")
                            break
                
                logger.debug(f"RSS Item {i+1}: title={title_elem is not None}, link={link_elem is not None}, date={date_elem is not None}")
                
                if title_elem is not None and link_elem is not None:
                    title = title_elem.text.strip() if title_elem.text else "No title"
                    link = link_elem.text.strip() if link_elem.text else link_elem.get('href', '')
                    
                    # Get description from multiple possible elements
                    desc_text = None
                    if desc_elem is not None and desc_elem.text:
                        desc_text = desc_elem.text
                    elif item.find('content:encoded') is not None:
                        desc_text = item.find('content:encoded').text
                    else:
                        desc_text = title
                    
                    # Parse date with debugging
                    published_date = None
                    if date_elem is not None and date_elem.text:
                        date_str = date_elem.text.strip()
                        logger.debug(f"RSS Item {i+1}: Raw date string: '{date_str}'")
                        published_date = self.parse_date(date_str)
                        logger.debug(f"RSS Item {i+1}: Parsed date: {published_date}")
                    else:
                        logger.debug(f"RSS Item {i+1}: No date element found")
                    
                    # Create NewsItem even if no date (we'll filter later)
                    news_item = NewsItem(
                        title=title,
                        description=BeautifulSoup(desc_text, 'html.parser').get_text() if desc_text else title,
                        link=link,
                        published_date=published_date,
                        source=feed_url
                    )
                    news_items.append(news_item)
                    logger.debug(f"RSS Item {i+1}: Created NewsItem with title: '{title[:50]}...'")
                else:
                    logger.debug(f"RSS Item {i+1}: Skipped - missing title or link")
                    
            except Exception as e:
                logger.error(f"RSS Reader: Error parsing RSS item {i+1} from {feed_url}: {str(e)}")
                continue
        
        logger.debug(f"RSS Parser: Created {len(news_items)} NewsItems from {feed_url}")
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
