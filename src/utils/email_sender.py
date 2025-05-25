# src/utils/email_sender.py

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Environment, FileSystemLoader
import os
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
            total_articles = sum(len(date_data['items']) for date_data in news_by_date.values())
            logger.info(f"Processing {total_articles} articles across {len(news_by_date)} days")
            
            template = self.template_env.get_template('email_template.html')
            html_content = template.render(news_by_date=news_by_date)

            msg = MIMEMultipart('alternative')
            
            # Get all dates safely
            dates = sorted(list(news_by_date.keys()))
            if not dates:
                raise EmailSendError("No dates found in news data")
            
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