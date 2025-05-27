import argparse
from datetime import datetime, timedelta
from typing import List, Optional
import pytz
from agents.rss_reader import RssReader
from agents.summarizer import Summarizer
from utils.email_sender import EmailSender
from config.settings import RSS_FEED_URLS, EMAIL_SETTINGS, GEMINI_API_KEY
from utils.gemini_client import GeminiClient
import smtplib
from utils.logger import logger
import logging
import sys

def parse_args():
    parser = argparse.ArgumentParser(description='RSS Feed Processor')
    parser.add_argument('--days', type=int, default=1,
                      help='Number of days of news to process (default: 1)')
    parser.add_argument('--feeds', type=str,
                      help='Comma-separated list of specific feeds to process')
    parser.add_argument('--dry-run', action='store_true',
                      help='Run without sending emails')
    parser.add_argument('--debug', action='store_true',
                      help='Enable debug logging')
    return parser.parse_args()

def setup_logging(debug: bool = False):
    level = logging.DEBUG if debug else logging.INFO
    logger.setLevel(level)
    # Ensure all handlers also respect the debug level
    for handler in logger.handlers:
        handler.setLevel(level)

def get_feed_urls(args) -> List[str]:
    if args.feeds:
        return [feed.strip() for feed in args.feeds.split(',')]
    return RSS_FEED_URLS

def test_connections():
    """Test Gemini API and SMTP connections before running the main process"""
    try:
        logger.info("=== Testing Connections ===")
        logger.info("1. Testing Gemini API connection...")
        client = GeminiClient(GEMINI_API_KEY)
        
        # Initialize the model (this will retry if needed)
        logger.info("Initializing Gemini model...")
        if not client.initialize_model():
            raise Exception("Failed to initialize Gemini model")
        logger.info("Gemini API connection successful")
            
    except Exception as e:
        logger.error(f"Gemini API connection failed: {str(e)}")
        return False

    try:
        logger.info("2. Testing SMTP connection...")
        # Test SMTP connection
        with smtplib.SMTP(EMAIL_SETTINGS['smtp_server'], EMAIL_SETTINGS['smtp_port']) as server:
            logger.info("SMTP server connected, starting TLS...")
            server.starttls()
            logger.info("TLS started, attempting login...")
            server.login(EMAIL_SETTINGS['sender_email'], EMAIL_SETTINGS['sender_password'])
            logger.info("SMTP connection successful")
    except Exception as e:
        logger.error(f"SMTP connection failed: {str(e)}")
        return False

    logger.info("All connection tests successful!")
    return True

def process_news(days: int = 1, feed_urls: Optional[List[str]] = None, dry_run: bool = False):
    try:
        logger.info("Starting News Digest process")
        logger.info(f"Processing news for the last {days} days")
        
        # Use provided feed URLs or default ones
        feeds_to_process = feed_urls or RSS_FEED_URLS
        logger.info(f"Using {len(feeds_to_process)} RSS feeds")
        
        # Initialize the RSS reader with the selected feeds
        rss_reader = RssReader(feeds_to_process)
        
        # Set the date range for filtering with timezone awareness
        date_cutoff = datetime.now(pytz.UTC) - timedelta(days=days)
        logger.info(f"Date range: {date_cutoff.date()} to {datetime.now(pytz.UTC).date()}")
        
        # Fetch and parse the RSS feeds with the specified date range
        news_items = rss_reader.fetch_news(days=days)
        logger.info(f"Fetched {len(news_items) if news_items else 0} items from RSS feeds")
        
        # Filter news items by date, ensuring we have a valid published_date
        news_items = [item for item in news_items 
                     if item.published_date is not None and item.published_date >= date_cutoff]
        
        if not news_items:
            logger.warning("No news items found within the specified date range.")
            return
        
        logger.info(f"Found {len(news_items)} items in date range")
        
        # Initialize the summarizer
        summarizer = Summarizer()
        
        # Generate the summary grouped by day
        summary = summarizer.summarize(news_items, days=days)
        
        if not summary:
            logger.warning("No summaries generated. Check the Gemini API connection.")
            return
        
        if dry_run:
            logger.info("Dry run mode - Email would have contained:")
            logger.info(summary)
            return
        
        # Initialize the email sender
        email_sender = EmailSender(EMAIL_SETTINGS)
        
        # Send the summarized news via email
        email_sender.send_email(summary)
        
        logger.info("News Digest process completed successfully!")
        
    except Exception as e:
        logger.error(f"Process failed: {str(e)}")
        raise

def main():
    args = parse_args()
    setup_logging(args.debug)
    logger.info("=== Starting News Digest Application ===")
    logger.info(f"Command line arguments: days={args.days}, dry_run={args.dry_run}")
    
    if test_connections():
        process_news(
            days=args.days,
            feed_urls=get_feed_urls(args) if args.feeds else None,
            dry_run=args.dry_run
        )
    else:
        logger.error("Connection tests failed. Please check your settings.")
    
    logger.info("=== Application Finished ===")

if __name__ == "__main__":
    main()
