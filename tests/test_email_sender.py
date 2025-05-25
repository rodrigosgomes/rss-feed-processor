import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
import pytz
from src.utils.email_sender import EmailSender
from src.models.news_item import NewsItem

class TestEmailSender(unittest.TestCase):
    def setUp(self):
        self.email_settings = {
            "smtp_server": "smtp.test.com",
            "smtp_port": 587,
            "sender_email": "test@example.com",
            "sender_password": "test_password",
            "recipient_email": "recipient@example.com"
        }
        self.email_sender = EmailSender(self.email_settings)
        
        # Sample news data
        current_date = datetime.now(pytz.UTC).date()
        self.test_news = {
            current_date: {
                'summary': 'Test summary',
                'items': [
                    NewsItem(
                        title="Test News",
                        description="Test description",
                        link="http://example.com",
                        published_date=datetime.now(pytz.UTC),
                        source="Test Source"
                    )
                ]
            }
        }

    @patch('src.utils.email_sender.smtplib.SMTP')
    def test_send_email_success(self, mock_smtp):
        # Configure mock
        mock_smtp_instance = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_smtp_instance
        
        # Test email sending
        self.email_sender.send_email(self.test_news)
        
        # Verify SMTP calls
        mock_smtp.assert_called_once_with(
            self.email_settings['smtp_server'],
            self.email_settings['smtp_port']
        )
        mock_smtp_instance.starttls.assert_called_once()
        mock_smtp_instance.login.assert_called_once_with(
            self.email_settings['sender_email'],
            self.email_settings['sender_password']
        )
        mock_smtp_instance.send_message.assert_called_once()

    @patch('src.utils.email_sender.smtplib.SMTP')
    def test_send_email_smtp_error(self, mock_smtp):
        # Configure mock to raise an exception
        mock_smtp.return_value.__enter__.side_effect = Exception("SMTP Error")
        
        # Test error handling
        with self.assertRaises(Exception) as context:
            self.email_sender.send_email(self.test_news)
        
        self.assertIn("Email sending failed", str(context.exception))

    def test_email_content_formatting(self):
        """Test that the email content is properly formatted"""
        # Get the rendered template
        template = self.email_sender.template_env.get_template('email_template.html')
        html_content = template.render(news_by_date=self.test_news)
        
        # Check for required elements
        self.assertIn("Daily News Summary", html_content)
        self.assertIn(self.test_news[list(self.test_news.keys())[0]]['summary'], 
                     html_content)
        self.assertIn(self.test_news[list(self.test_news.keys())[0]]['items'][0].title, 
                     html_content)

    def test_empty_news_handling(self):
        """Test handling of empty news data"""
        with self.assertRaises(Exception) as context:
            self.email_sender.send_email({})
        self.assertIn("No news items to send", str(context.exception))

if __name__ == '__main__':
    unittest.main()
