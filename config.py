"""
masterSchetan CCIE — Complete Company Intelligence Engine
Configuration & Constants
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ── Paths ──────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent
CACHE_DIR = PROJECT_ROOT / "cache"
CACHE_DIR.mkdir(exist_ok=True)

try:
    import streamlit as st
    GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY", ""))
    GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY", ""))
    OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY", os.getenv("OPENROUTER_API_KEY", ""))
    DEEPSEEK_API_KEY = st.secrets.get("DEEPSEEK_API_KEY", os.getenv("DEEPSEEK_API_KEY", ""))
except Exception:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")

# ── App Settings ───────────────────────────────────────
APP_NAME = "masterSchetan CCIE"
APP_TAGLINE = "Complete Company Intelligence Engine for Indian Equities"
APP_VERSION = "1.0.0"

# ── Cache Freshness (seconds) ──────────────────────────
CACHE_TTL = {
    "company_history": 30 * 86400,      # 30 days
    "business_description": 90 * 86400,  # 90 days (quarterly)
    "management": 7 * 86400,             # 7 days
    "annual_financials": 90 * 86400,     # Quarterly
    "quarterly_results": 1 * 86400,      # Daily check
    "shareholding": 90 * 86400,          # Quarterly
    "order_book": 1 * 86400,             # Daily
    "dividends": 7 * 86400,             # Weekly
    "analyst_meetings": 1 * 86400,       # Daily
    "news": 4 * 3600,                    # 4 hours
    "credit_ratings": 7 * 86400,         # Weekly
    "governance": 7 * 86400,             # Weekly
    "price_data": 900,                   # 15 minutes
    "default": 1 * 86400,               # 1 day fallback
}

# ── Source Hierarchy ───────────────────────────────────
SOURCE_HIERARCHY = {
    1: "SEBI filing",
    2: "Exchange/company regulatory filing",
    3: "Company annual report",
    4: "Audited financial statements",
    5: "Company investor presentation",
    6: "Company earnings-call material",
    7: "Credit-rating agency",
    8: "Company website",
    9: "Reputed financial/news publication",
    10: "Data aggregator (yfinance)",
}

# ── Sector Definitions ─────────────────────────────────
SECTOR_MAP = {
    "Financial Services": "banks",
    "Banks": "banks",
    "NBFC": "nbfc",
    "Insurance": "insurance",
    "Information Technology": "it",
    "Technology": "it",
    "Pharmaceuticals": "pharma",
    "Healthcare": "pharma",
    "Capital Goods": "capital_goods",
    "Construction": "capital_goods",
    "Real Estate": "real_estate",
    "Consumer Goods": "fmcg",
    "FMCG": "fmcg",
    "Automobile": "auto",
    "Auto Components": "auto",
    "Utilities": "utilities",
    "Power": "utilities",
    "Metals & Mining": "metals",
    "Oil & Gas": "oil_gas",
    "Energy": "oil_gas",
    "Telecom": "telecom",
    "Media": "media",
    "Chemicals": "chemicals",
    "Textiles": "textiles",
    "Cement": "cement",
}

# ── Red Flag Thresholds ────────────────────────────────
RED_FLAG_THRESHOLDS = {
    "cfo_pat_ratio_min": 0.6,           # CFO/PAT below this is warning
    "receivable_growth_vs_sales": 1.5,   # Receivables growing 1.5x faster than sales
    "inventory_growth_vs_sales": 1.5,    # Inventory growing 1.5x faster than sales
    "debt_growth_vs_earnings": 1.5,      # Debt growing 1.5x faster than earnings
    "promoter_decline_pct": 2.0,         # Promoter holding declined > 2% in a year
    "pledge_warning_pct": 10.0,          # Pledge > 10% is a warning
    "pledge_danger_pct": 25.0,           # Pledge > 25% is danger
    "interest_coverage_min": 2.0,        # Interest coverage below 2x is risky
    "debt_equity_max": 2.0,             # D/E above 2 is high
    "contingent_liability_pct": 20.0,    # > 20% of net worth
}

# ── News Materiality Categories ────────────────────────
NEWS_CATEGORIES = {
    "highly_material": [
        "resignation", "fraud", "acquisition", "merger", "plant closure",
        "bankruptcy", "default", "debt", "investigation", "sebi",
        "order win", "large contract", "fundraise", "ipo", "buyback",
        "promoter", "stake sale", "delisting",
    ],
    "medium": [
        "product launch", "expansion", "partnership", "management",
        "interview", "industry", "market share", "technology",
        "joint venture", "subsidiary", "capacity",
    ],
    "low": [
        "commentary", "market", "sector", "general", "opinion",
        "forecast", "estimate",
    ],
}

# ── Fact Status Labels ─────────────────────────────────
FACT_STATUS = {
    "confirmed": {"icon": "🏷️", "label": "Confirmed Fact"},
    "guidance": {"icon": "🔵", "label": "Management Guidance"},
    "planned": {"icon": "🏗️", "label": "Planned"},
    "expectation": {"icon": "⚠️", "label": "Analyst/Media Expectation"},
    "ai_scenario": {"icon": "🔮", "label": "AI Scenario"},
}
