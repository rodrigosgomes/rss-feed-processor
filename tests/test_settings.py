import pytest
import os
from src.config.settings import (
    validate_email_settings,
    validate_rss_feeds,
    validate_api_key,
    ConfigurationError
)

class TestSettings:
    def test_validate_email_settings_success(self):
        settings = {
            "smtp_server": "smtp.test.com",
            "smtp_port": "587",
            "sender_email": "test@example.com",
            "sender_password": "password123",
            "recipient_email": "recipient@example.com"
        }
        assert validate_email_settings(settings) is True

    def test_validate_email_settings_missing_field(self):
        settings = {
            "smtp_server": "smtp.test.com",
            "smtp_port": "587",
            "sender_email": "test@example.com",
            # missing sender_password
            "recipient_email": "recipient@example.com"
        }
        with pytest.raises(ConfigurationError, match="Missing required email setting"):
            validate_email_settings(settings)

    def test_validate_email_settings_invalid_port(self):
        settings = {
            "smtp_server": "smtp.test.com",
            "smtp_port": "invalid",
            "sender_email": "test@example.com",
            "sender_password": "password123",
            "recipient_email": "recipient@example.com"
        }
        with pytest.raises(ConfigurationError, match="must be a valid number"):
            validate_email_settings(settings)

    def test_validate_email_settings_invalid_email(self):
        settings = {
            "smtp_server": "smtp.test.com",
            "smtp_port": "587",
            "sender_email": "invalid-email",
            "sender_password": "password123",
            "recipient_email": "recipient@example.com"
        }
        with pytest.raises(ConfigurationError, match="Invalid email address"):
            validate_email_settings(settings)

    def test_validate_rss_feeds_success(self):
        urls = ["https://example.com/feed", "http://another.com/rss"]
        assert validate_rss_feeds(urls) is True

    def test_validate_rss_feeds_empty(self):
        with pytest.raises(ConfigurationError, match="No RSS feed URLs configured"):
            validate_rss_feeds([])

    def test_validate_rss_feeds_invalid_url(self):
        urls = ["https://example.com/feed", "invalid-url"]
        with pytest.raises(ConfigurationError, match="Invalid RSS feed URL"):
            validate_rss_feeds(urls)

    def test_validate_api_key_success(self):
        assert validate_api_key("test-api-key") is True

    def test_validate_api_key_missing(self):
        with pytest.raises(ConfigurationError, match="Missing Gemini API key"):
            validate_api_key("")
