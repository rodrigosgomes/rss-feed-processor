# src/utils/email_sender.py

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Environment, FileSystemLoader
import os
from datetime import datetime
from utils.logger import logger

class EmailSendError(Exception):
    """Custom exception for email sending errors"""
    pass

class EmailSender:
    def __init__(self, email_settings):
        self.settings = email_settings
        self.template_env = Environment(
            loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), '../templates'))
        )
        logger.info("Email sender initialized")

    def send_email(self, news_by_date):
        try:
            if not news_by_date:
                raise EmailSendError("No news items to send")

            logger.info("=== Preparing Email ===")
            
            # Separate news items and LinkedIn content
            filtered_news = {}
            linkedin_content = None
            
            for key, value in news_by_date.items():
                if isinstance(key, datetime) or isinstance(key, str) and key != 'linkedin_content':
                    if isinstance(value, dict) and 'items' in value:
                        filtered_news[key] = value
                elif key == 'linkedin_content':
                    linkedin_content = value

            if not filtered_news:
                raise EmailSendError("No valid news items found in data")

            total_articles = sum(len(date_data['items']) for date_data in filtered_news.values())
            logger.info(f"Processing {total_articles} articles across {len(filtered_news)} days")
            
            template = self.template_env.get_template('email_template.html')
            template_data = {
                'news_by_date': filtered_news,
                'linkedin_content': linkedin_content,
                'stats': self._generate_stats(filtered_news)
            }
            
            html_content = template.render(**template_data)
            msg = MIMEMultipart('alternative')

            # Get all dates safely
            dates = sorted(list(filtered_news.keys()))
            
            # Create appropriate subject line based on date range
            if len(dates) == 1:
                subject = f"Daily News Summary - {dates[0].strftime('%Y-%m-%d')}"
            else:
                subject = f"News Summary {dates[0].strftime('%Y-%m-%d')} to {dates[-1].strftime('%Y-%m-%d')}"
            
            msg['Subject'] = subject
            msg['From'] = self.settings['sender_email']
            msg['To'] = self.settings['recipient_email']
            msg.attach(MIMEText(html_content, 'html'))

            logger.info("Connecting to SMTP server")
            try:
                with smtplib.SMTP(self.settings['smtp_server'], self.settings['smtp_port']) as server:
                    server.starttls()
                    logger.info("Attempting SMTP login")
                    server.login(self.settings['sender_email'], self.settings['sender_password'])
                    logger.info("Sending email")
                    server.send_message(msg)
                    logger.info("Email sent successfully!")
            except Exception as smtp_error:
                raise EmailSendError(f"Email sending failed: {str(smtp_error)}")

        except Exception as e:
            logger.error(f"Email sending failed: {str(e)}")
            raise EmailSendError(str(e))

    def _generate_stats(self, news_data):
        """Generate statistics for the news data"""
        total_articles = sum(len(date_data['items']) for date_data in news_data.values())
        sources = set()
        for date_data in news_data.values():
            for item in date_data['items']:
                if hasattr(item, 'source'):
                    sources.add(item.source)
                
        return {
            'total_articles': total_articles,
            'total_days': len(news_data),
            'total_sources': len(sources),
            'sources': list(sources)
        }