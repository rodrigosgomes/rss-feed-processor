try:
    from datetime import datetime, timedelta
    from itertools import groupby
    from operator import attrgetter
    import google.generativeai as genai
    import pytz
    from templates.prompts import ARTICLE_SUMMARY_PROMPT
    from config.settings import GEMINI_API_KEY
    from utils.logger import logger
    from utils.gemini_client import GeminiClient
except ImportError as e:
    import sys
    print(f"Error importing required modules: {e}", file=sys.stderr)
    print("Please ensure all dependencies are installed: pip install -r requirements.txt", file=sys.stderr)
    raise

class Summarizer:
    def __init__(self):
        logger.info("Initializing Gemini AI summarizer")
        self.client = GeminiClient(GEMINI_API_KEY)
        self.client.initialize_model()

    def summarize(self, news_items, days=1):
        logger.info("Starting news summarization process")
        
        # Get date range in UTC
        end_date = datetime.now(pytz.UTC).date()
        start_date = end_date - timedelta(days=days-1)  # -1 because we want to include today
        logger.info(f"Filtering news from {start_date} to {end_date}")
        
        # Filter news items for the specified date range
        filtered_news = [
            item for item in news_items 
            if start_date <= item.published_date.date() <= end_date
        ]
        
        if not filtered_news:
            logger.warning(f"No news items found between {start_date} and {end_date}")
            return {}
            
        logger.info(f"Found {len(filtered_news)} news items in the date range")
        
        # Group news by date and generate summaries
        summarized_news = {}
        for item in filtered_news:
            try:
                item_date = item.published_date.date()
                if item_date not in summarized_news:
                    summarized_news[item_date] = {'items': []}
                    
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
                summarized_news[item_date]['items'].append(summarized_item)
            except Exception as e:
                logger.error(f"Error summarizing article {item.title}: {str(e)}")
                # Include the article without a summary
                item.summary = "Error generating summary for this article."
                item_date = item.published_date.date()
                if item_date not in summarized_news:
                    summarized_news[item_date] = {'items': []}
                summarized_news[item_date]['items'].append(item)
        
        logger.info(f"Completed summarization for news between {start_date} and {end_date}")
        return summarized_news

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