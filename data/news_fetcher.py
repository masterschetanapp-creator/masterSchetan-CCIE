"""
Fetches company news from Google News RSS.
"""

import feedparser
from urllib.parse import quote_plus
from typing import List, Dict, Any
from datetime import datetime

try:
    from config import NEWS_CATEGORIES
except ImportError:
    NEWS_CATEGORIES = {
        "highly_material": ["merger", "acquisition", "earnings", "profit", "loss", "dividend", "resignation", "scam", "fraud", "lawsuit"],
        "medium": ["launch", "expansion", "partnership", "contract", "order", "award"],
        "low": []
    }

def categorize_news(title: str) -> str:
    """Categorize as 'highly_material', 'medium', or 'low' using keywords from config.NEWS_CATEGORIES."""
    title_lower = title.lower()
    
    for category, keywords in NEWS_CATEGORIES.items():
        if category in ["highly_material", "medium"]:
            for keyword in keywords:
                if keyword in title_lower:
                    return category
    
    return "low"

def fetch_company_news(company_name: str, symbol: str, max_items: int = 20) -> List[Dict[str, Any]]:
    """Fetch latest news. Returns list of {title, source, date, url, ai_summary, materiality}."""
    query = quote_plus(f'"{company_name}" OR "{symbol}" stock india')
    url = f"https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en"
    
    try:
        feed = feedparser.parse(url)
        news_items = []
        
        for entry in feed.entries[:max_items]:
            title = entry.title
            
            source = entry.source.title if hasattr(entry, 'source') else "Google News"
            
            news_items.append({
                "title": title,
                "source": source,
                "date": entry.published if hasattr(entry, 'published') else datetime.now().isoformat(),
                "url": entry.link,
                "ai_summary": "", 
                "materiality": categorize_news(title)
            })
            
        return news_items
    except Exception as e:
        print(f"Error fetching news for {company_name}: {e}")
        return []
