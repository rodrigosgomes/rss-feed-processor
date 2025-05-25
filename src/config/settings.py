from dotenv import load_dotenv
import os
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class ConfigurationError(Exception):
    """Raised when there is an error in the configuration"""
    pass

def validate_email_settings(settings: Dict[str, Any]) -> bool:
    """Validate email settings"""
    required_fields = ['smtp_server', 'smtp_port', 'sender_email', 
                      'sender_password', 'recipient_email']
    
    for field in required_fields:
        if not settings.get(field):
            raise ConfigurationError(f"Missing required email setting: {field}")
    
    # Validate port number
    try:
        port = int(settings['smtp_port'])
        if port <= 0 or port > 65535:
            raise ConfigurationError("SMTP port must be between 1 and 65535")
    except ValueError:
        raise ConfigurationError("SMTP port must be a valid number")
    
    # Validate email addresses
    for email_field in ['sender_email', 'recipient_email']:
        email = settings[email_field]
        if not '@' in email or not '.' in email:
            raise ConfigurationError(f"Invalid email address in {email_field}: {email}")
    
    return True

def validate_rss_feeds(urls: List[str]) -> bool:
    """Validate RSS feed URLs"""
    if not urls or not urls[0]:
        raise ConfigurationError("No RSS feed URLs configured")
    
    for url in urls:
        if not url.startswith(('http://', 'https://')):
            raise ConfigurationError(f"Invalid RSS feed URL: {url}")
    
    return True

def validate_api_key(api_key: str) -> bool:
    """Validate API key"""
    if not api_key:
        raise ConfigurationError("Missing Gemini API key")
    return True

# Load environment variables
load_dotenv()

# Get and validate RSS feed URLs
RSS_FEED_URLS = os.getenv('RSS_FEED_URLS', '').split(',')
validate_rss_feeds(RSS_FEED_URLS)

# Get and validate email settings
EMAIL_SETTINGS = {
    "smtp_server": os.getenv("SMTP_SERVER", "smtp.gmail.com"),
    "smtp_port": int(os.getenv("SMTP_PORT", "587")),
    "sender_email": os.getenv("SENDER_EMAIL"),
    "sender_password": os.getenv("SENDER_PASSWORD"),
    "recipient_email": os.getenv("RECIPIENT_EMAIL")
}
validate_email_settings(EMAIL_SETTINGS)

# Get and validate API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
validate_api_key(GEMINI_API_KEY)

# Cache settings
CACHE_TTL = int(os.getenv("CACHE_TTL", "3600"))  # Default 1 hour
MAX_CACHE_SIZE = int(os.getenv("MAX_CACHE_SIZE", "1000"))  # Default 1000 items