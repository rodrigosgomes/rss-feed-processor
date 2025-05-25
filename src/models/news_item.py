from dataclasses import dataclass
from datetime import datetime

@dataclass
class NewsItem:
    title: str
    description: str
    link: str
    published_date: datetime
    source: str
    summary: str = None  # Optional field for article summary