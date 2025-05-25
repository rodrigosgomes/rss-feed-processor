import google.generativeai as genai
from datetime import datetime
import pytz
from itertools import groupby
from operator import attrgetter
from templates.prompts import ARTICLE_SUMMARY_PROMPT
from config.settings import GEMINI_API_KEY
from utils.logger import logger
from utils.gemini_client import GeminiClient

class Summarizer:
    def __init__(self):
        logger.info("Initializing Gemini AI summarizer")
        self.client = GeminiClient(GEMINI_API_KEY)
        self.client.initialize_model()

    def summarize(self, news_items):
        logger.info("Starting news summarization process")
        
        # Get current date in UTC
        current_date = datetime.now(pytz.UTC).date()
        logger.info(f"Filtering news for current date: {current_date}")
        
        # Filter news items for current day only
        current_news = [
            item for item in news_items 
            if item.published_date.date() == current_date
        ]
        
        if not current_news:
            logger.warning("No news items found for the current day")
            return {}
            
        logger.info(f"Found {len(current_news)} news items for today")
        
        # Generate summaries for each article
        summarized_news = []
        for item in current_news:
            try:
                summary = self._generate_article_summary(item)
                # Create a new news item with the summary
                summarized_item = item.__class__(
                    title=item.title,
                    description=item.description,
                    link=item.link,
                    published_date=item.published_date,
                    source=item.source,
                    summary=summary
                )
                summarized_news.append(summarized_item)
            except Exception as e:
                logger.error(f"Error summarizing article {item.title}: {str(e)}")
                # Include the article without a summary
                item.summary = "Error generating summary for this article."
                summarized_news.append(item)
        
        grouped_news = {
            current_date: {
                'items': summarized_news
            }
        }
        
        logger.info("Completed summarization for today's news")
        return grouped_news

    def _generate_article_summary(self, news_item):
        try:
            logger.info(f"Generating summary for article: {news_item.title}")
            prompt = ARTICLE_SUMMARY_PROMPT.format(
                title=news_item.title,
                description=news_item.description,
                source=news_item.source
            )
            response = self.client.generate_content(prompt)
            logger.info("Article summary generated successfully")
            return response.text
        except Exception as e:
            logger.error(f"Error generating article summary: {str(e)}")
            return "Error generating summary. Please check the logs."