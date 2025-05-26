from dotenv import load_dotenv
import os
from typing import List, Dict, Any
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class ConfigurationError(Exception):
    """Raised when there is an error in the configuration"""
    pass

def validate_email_settings(settings: Dict[str, Any]) -> bool:
    """Validate email settings"""
    required_fields = ["smtp_server", "smtp_port", "sender_email", "sender_password"]
    for field in required_fields:
        if not settings.get(field):
            raise ConfigurationError(f"Missing required email setting: {field}")
    
    try:
        port = int(settings["smtp_port"])
        if port < 1 or port > 65535:
            raise ConfigurationError(f"Invalid SMTP port: {port}")
    except ValueError:
        raise ConfigurationError(f"SMTP port must be a number")
    
    return True

def validate_rss_feeds(urls: List[str]) -> bool:
    """Validate RSS feed URLs"""
    if not urls:
        raise ConfigurationError("No RSS feed URLs provided")
    
    for url in urls:
        if not url.startswith(('http://', 'https://')):
            raise ConfigurationError(f"Invalid RSS feed URL: {url}")
    
    return True

def validate_api_key(api_key: str) -> bool:
    """Validate API key"""
    if not api_key:
        raise ConfigurationError("Missing API key")
    return True

def read_file_lines(filepath: str) -> List[str]:
    """Read lines from a file and return non-empty lines"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        logger.warning(f"Configuration file not found: {filepath}")
        return []

# Load environment variables
load_dotenv()

# Get config file paths
config_dir = Path(__file__).parent
feeds_file = config_dir / 'feeds.txt'
recipients_file = config_dir / 'recipients.txt'

# Get and validate RSS feed URLs
RSS_FEED_URLS = read_file_lines(str(feeds_file))
if not RSS_FEED_URLS:  # Fallback to environment variable if file is empty or doesn't exist
    RSS_FEED_URLS = [url.strip() for url in os.getenv('RSS_FEED_URLS', '').split(',') if url.strip()]
validate_rss_feeds(RSS_FEED_URLS)

# Get recipients from file
recipients = read_file_lines(str(recipients_file))
recipient_email = recipients[0] if recipients else os.getenv("RECIPIENT_EMAIL")

if not recipient_email:
    raise ConfigurationError("No recipient email found in recipients.txt or environment variables")

# Get and validate email settings
EMAIL_SETTINGS = {
    "smtp_server": os.getenv("SMTP_SERVER", "smtp.gmail.com"),
    "smtp_port": int(os.getenv("SMTP_PORT", "587")),
    "sender_email": os.getenv("SENDER_EMAIL"),
    "sender_password": os.getenv("SENDER_PASSWORD"),
    "recipient_email": recipient_email
}
validate_email_settings(EMAIL_SETTINGS)

# Get and validate API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
validate_api_key(GEMINI_API_KEY)