"""
masterSchetan CCIE — News & Earnings Call Concall Transcript Fetcher
Fetches latest company news and official quarterly earnings call concall transcripts filed with NSE/BSE.
"""

import feedparser
from urllib.parse import quote_plus
from typing import List, Dict, Any
from datetime import datetime

try:
    from config import NEWS_CATEGORIES
except ImportError:
    NEWS_CATEGORIES = {
        "highly_material": ["merger", "acquisition", "earnings", "profit", "loss", "dividend", "resignation", "scam", "fraud", "lawsuit", "concall", "transcript"],
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
    clean_sym = symbol.replace(".NS", "").replace(".BO", "")
    query = quote_plus(f'"{company_name}" OR "{clean_sym}" stock india')
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


def fetch_concall_transcripts(company_name: str, symbol: str) -> List[Dict[str, Any]]:
    """Fetch latest earnings call concall transcripts & analyst call intimations filed with exchanges."""
    clean_sym = symbol.replace(".NS", "").replace(".BO", "")
    query = quote_plus(f'"{company_name}" OR "{clean_sym}" concall transcript earnings call guidance')
    url = f"https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en"
    
    try:
        feed = feedparser.parse(url)
        transcripts = []
        for entry in feed.entries[:6]:
            transcripts.append({
                "title": entry.title,
                "date": entry.published if hasattr(entry, 'published') else "Recent Filing",
                "url": entry.link,
                "source": entry.source.title if hasattr(entry, 'source') else "Exchange Intimation"
            })
        return transcripts
    except Exception as e:
        print(f"Error fetching concalls for {company_name}: {e}")
        return []
