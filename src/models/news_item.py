from dataclasses import dataclass
from datetime import datetime
import pytz

@dataclass
class NewsItem:
    title: str
    description: str
    link: str
    published_date: datetime
    source: str
    summary: str = None  # Optional field for article summary

    def __post_init__(self):
        # Ensure published_date has timezone information
        if self.published_date and self.published_date.tzinfo is None:
            self.published_date = self.published_date.replace(tzinfo=pytz.UTC)