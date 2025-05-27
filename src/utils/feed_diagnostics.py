import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from datetime import datetime
import pytz
from typing import Dict, List, Tuple, Optional
from utils.logger import logger
import time
import random
from urllib.parse import urlparse

class FeedDiagnostics:
    """Diagnose RSS feed issues and test different parsing strategies"""
    
    def __init__(self):
        self.headers_variants = [
            # Standard RSS reader headers
            {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'application/rss+xml, application/xml, text/xml, application/atom+xml, */*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Cache-Control': 'no-cache',
            },
            # More generic browser headers
            {
                'User-Agent': 'Mozilla/5.0 (compatible; ProductReader/1.0)',
                'Accept': '*/*',
                'Accept-Language': 'en',
            },
            # RSS reader specific
            {
                'User-Agent': 'RSS Reader Bot',
                'Accept': 'application/rss+xml, application/xml',
            },
            # Feedburner compatible
            {
                'User-Agent': 'FeedBurner/1.0 (http://www.FeedBurner.com)',
                'Accept': 'application/rss+xml',
            }
        ]
    
    def diagnose_feed(self, url: str) -> Dict:
        """Comprehensive diagnosis of a single RSS feed"""
        result = {
            'url': url,
            'accessible': False,
            'content_type': None,
            'status_code': None,
            'error': None,
            'items_found': 0,
            'feed_type': None,
            'sample_items': [],
            'date_formats': [],
            'working_headers': None,
            'parsing_strategy': None
        }
        
        logger.info(f"🔍 Diagnosing feed: {url}")
        
        # Try different header combinations
        for i, headers in enumerate(self.headers_variants):
            try:
                logger.debug(f"Trying header variant {i+1}")
                response = self._make_request(url, headers)
                
                if response.status_code == 200:
                    result['accessible'] = True
                    result['status_code'] = response.status_code
                    result['content_type'] = response.headers.get('content-type', 'unknown')
                    result['working_headers'] = i + 1
                    
                    # Try to parse the content
                    parse_result = self._try_parse_strategies(response.content, url)
                    result.update(parse_result)
                    
                    if result['items_found'] > 0:
                        logger.info(f"✅ Feed working with header variant {i+1}: {result['items_found']} items found")
                        break
                    else:
                        logger.warning(f"⚠️ Feed accessible but no items found with header variant {i+1}")
                else:
                    logger.warning(f"❌ HTTP {response.status_code} with header variant {i+1}")
                    
            except Exception as e:
                logger.debug(f"Header variant {i+1} failed: {str(e)}")
                result['error'] = str(e)
                continue
        
        if not result['accessible']:
            logger.error(f"❌ Feed not accessible: {url}")
        
        return result
    
    def _make_request(self, url: str, headers: Dict) -> requests.Response:
        """Make HTTP request with specific headers"""
        parsed_url = urlparse(url)
        headers['Host'] = parsed_url.netloc
        headers['Referer'] = f"{parsed_url.scheme}://{parsed_url.netloc}"
        
        # Add small delay to avoid rate limiting
        time.sleep(random.uniform(0.1, 0.3))
        
        response = requests.get(url, headers=headers, timeout=10)
        return response
    
    def _try_parse_strategies(self, content: bytes, url: str) -> Dict:
        """Try different parsing strategies"""
        strategies = [
            ('ElementTree_Standard', self._parse_with_et_standard),
            ('ElementTree_Namespaced', self._parse_with_et_namespaced),
            ('BeautifulSoup_XML', self._parse_with_bs_xml),
            ('BeautifulSoup_HTML', self._parse_with_bs_html),
        ]
        
        best_result = {
            'items_found': 0,
            'feed_type': None,
            'sample_items': [],
            'date_formats': [],
            'parsing_strategy': None
        }
        
        for strategy_name, strategy_func in strategies:
            try:
                logger.debug(f"Trying parsing strategy: {strategy_name}")
                result = strategy_func(content, url)
                
                if result['items_found'] > best_result['items_found']:
                    best_result = result
                    best_result['parsing_strategy'] = strategy_name
                    logger.debug(f"Strategy {strategy_name} found {result['items_found']} items")
                
            except Exception as e:
                logger.debug(f"Strategy {strategy_name} failed: {str(e)}")
                continue
        
        return best_result
    
    def _parse_with_et_standard(self, content: bytes, url: str) -> Dict:
        """Parse using standard ElementTree"""
        root = ET.fromstring(content)
        
        # Detect feed type
        is_atom = root.tag.endswith('feed')
        feed_type = 'Atom' if is_atom else 'RSS'
        
        if is_atom:
            items = root.findall('.//entry') or root.findall('{http://www.w3.org/2005/Atom}entry')
        else:
            items = root.findall('.//item')
        
        sample_items, date_formats = self._extract_sample_data(items, feed_type)
        
        return {
            'items_found': len(items),
            'feed_type': feed_type,
            'sample_items': sample_items,
            'date_formats': date_formats
        }
    
    def _parse_with_et_namespaced(self, content: bytes, url: str) -> Dict:
        """Parse using ElementTree with namespace awareness"""
        root = ET.fromstring(content)
        
        # Try with explicit namespaces
        namespaces = {
            'atom': 'http://www.w3.org/2005/Atom',
            'rss': 'http://purl.org/rss/1.0/',
            'dc': 'http://purl.org/dc/elements/1.1/',
            'content': 'http://purl.org/rss/1.0/modules/content/'
        }
        
        items = []
        feed_type = None
        
        # Try Atom with namespace
        atom_items = root.findall('.//atom:entry', namespaces)
        if atom_items:
            items = atom_items
            feed_type = 'Atom'
        else:
            # Try RSS with various paths
            for path in ['.//item', './/rss:item', 'channel/item']:
                try:
                    rss_items = root.findall(path, namespaces)
                    if rss_items:
                        items = rss_items
                        feed_type = 'RSS'
                        break
                except:
                    continue
        
        sample_items, date_formats = self._extract_sample_data(items, feed_type or 'Unknown')
        
        return {
            'items_found': len(items),
            'feed_type': feed_type,
            'sample_items': sample_items,
            'date_formats': date_formats
        }
    
    def _parse_with_bs_xml(self, content: bytes, url: str) -> Dict:
        """Parse using BeautifulSoup with XML parser"""
        soup = BeautifulSoup(content, 'lxml-xml')
        
        items = soup.find_all('item') or soup.find_all('entry')
        feed_type = 'Atom' if soup.find_all('entry') else 'RSS'
        
        sample_items, date_formats = self._extract_sample_data_bs(items, feed_type)
        
        return {
            'items_found': len(items),
            'feed_type': feed_type,
            'sample_items': sample_items,
            'date_formats': date_formats
        }
    
    def _parse_with_bs_html(self, content: bytes, url: str) -> Dict:
        """Parse using BeautifulSoup with HTML parser (fallback)"""
        soup = BeautifulSoup(content, 'html.parser')
        
        items = soup.find_all('item') or soup.find_all('entry')
        feed_type = 'Atom' if soup.find_all('entry') else 'RSS'
        
        sample_items, date_formats = self._extract_sample_data_bs(items, feed_type)
        
        return {
            'items_found': len(items),
            'feed_type': feed_type,
            'sample_items': sample_items,
            'date_formats': date_formats
        }
    
    def _extract_sample_data(self, items, feed_type: str) -> Tuple[List[Dict], List[str]]:
        """Extract sample data from ElementTree items"""
        sample_items = []
        date_formats = set()
        
        for i, item in enumerate(items[:3]):  # Only sample first 3 items
            sample_item = {}
            
            if feed_type == 'Atom':
                title_elem = item.find('title') or item.find('{http://www.w3.org/2005/Atom}title')
                link_elem = item.find('link') or item.find('{http://www.w3.org/2005/Atom}link')
                date_elem = (item.find('published') or item.find('{http://www.w3.org/2005/Atom}published') or
                           item.find('updated') or item.find('{http://www.w3.org/2005/Atom}updated'))
            else:
                title_elem = item.find('title')
                link_elem = item.find('link')
                date_elem = item.find('pubDate') or item.find('published') or item.find('date')
            
            if title_elem is not None and title_elem.text:
                sample_item['title'] = title_elem.text.strip()
            
            if link_elem is not None:
                sample_item['link'] = link_elem.text.strip() if link_elem.text else link_elem.get('href', '')
            
            if date_elem is not None and date_elem.text:
                date_str = date_elem.text.strip()
                sample_item['date'] = date_str
                date_formats.add(self._identify_date_format(date_str))
            
            if sample_item:
                sample_items.append(sample_item)
        
        return sample_items, list(date_formats)
    
    def _extract_sample_data_bs(self, items, feed_type: str) -> Tuple[List[Dict], List[str]]:
        """Extract sample data from BeautifulSoup items"""
        sample_items = []
        date_formats = set()
        
        for i, item in enumerate(items[:3]):  # Only sample first 3 items
            sample_item = {}
            
            title_elem = item.find('title')
            link_elem = item.find('link')
            
            if feed_type == 'Atom':
                date_elem = item.find('published') or item.find('updated')
            else:
                date_elem = item.find('pubDate') or item.find('published') or item.find('date')
            
            if title_elem and title_elem.text:
                sample_item['title'] = title_elem.text.strip()
            
            if link_elem:
                sample_item['link'] = link_elem.text.strip() if link_elem.text else link_elem.get('href', '')
            
            if date_elem and date_elem.text:
                date_str = date_elem.text.strip()
                sample_item['date'] = date_str
                date_formats.add(self._identify_date_format(date_str))
            
            if sample_item:
                sample_items.append(sample_item)
        
        return sample_items, list(date_formats)
    
    def _identify_date_format(self, date_str: str) -> str:
        """Identify the format of a date string"""
        formats = {
            r'\w{3}, \d{1,2} \w{3} \d{4} \d{2}:\d{2}:\d{2}': 'RFC822',
            r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z': 'ISO8601_UTC',
            r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}': 'ISO8601_TZ',
            r'\d{4}-\d{2}-\d{2}': 'Date_Only',
        }
        
        import re
        for pattern, format_name in formats.items():
            if re.match(pattern, date_str):
                return format_name
        
        return 'Unknown'
    
    def diagnose_all_feeds(self, feed_urls: List[str]) -> Dict:
        """Diagnose all feeds and provide summary"""
        results = []
        
        logger.info(f"🔍 Starting diagnosis of {len(feed_urls)} feeds...")
        
        for i, url in enumerate(feed_urls, 1):
            logger.info(f"📊 Progress: {i}/{len(feed_urls)}")
            result = self.diagnose_feed(url)
            results.append(result)
            
            # Add delay between requests
            time.sleep(random.uniform(0.5, 1.0))
        
        # Generate summary
        summary = self._generate_summary(results)
        return {
            'individual_results': results,
            'summary': summary
        }
    
    def _generate_summary(self, results: List[Dict]) -> Dict:
        """Generate summary statistics"""
        total_feeds = len(results)
        accessible_feeds = sum(1 for r in results if r['accessible'])
        feeds_with_items = sum(1 for r in results if r['items_found'] > 0)
        
        # Group by status
        working_feeds = [r for r in results if r['items_found'] > 0]
        blocked_feeds = [r for r in results if not r['accessible']]
        empty_feeds = [r for r in results if r['accessible'] and r['items_found'] == 0]
        
        # Analyze working feeds
        feed_types = {}
        parsing_strategies = {}
        header_variants = {}
        
        for feed in working_feeds:
            # Count feed types
            feed_type = feed.get('feed_type', 'Unknown')
            feed_types[feed_type] = feed_types.get(feed_type, 0) + 1
            
            # Count parsing strategies
            strategy = feed.get('parsing_strategy', 'Unknown')
            parsing_strategies[strategy] = parsing_strategies.get(strategy, 0) + 1
            
            # Count header variants
            headers = feed.get('working_headers', 'Unknown')
            header_variants[headers] = header_variants.get(headers, 0) + 1
        
        return {
            'total_feeds': total_feeds,
            'accessible_feeds': accessible_feeds,
            'working_feeds': len(working_feeds),
            'blocked_feeds': len(blocked_feeds),
            'empty_feeds': len(empty_feeds),
            'success_rate': f"{(len(working_feeds)/total_feeds)*100:.1f}%",
            'feed_types': feed_types,
            'parsing_strategies': parsing_strategies,
            'header_variants': header_variants,
            'blocked_feed_urls': [f['url'] for f in blocked_feeds],
            'empty_feed_urls': [f['url'] for f in empty_feeds],
            'working_feed_urls': [f['url'] for f in working_feeds]
        }