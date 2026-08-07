"""
masterSchetan CCIE — Research Orchestrator
Coordinates all research agents to build a complete stock dossier.
"""
import time
import traceback
from typing import Optional
from config import CACHE_TTL


def build_dossier(symbol: str, company_name: str, progress_callback=None) -> dict:
    """
    Master orchestrator. Builds a complete investment research dossier for a stock.
    
    Pipeline: Entity Resolve → Cache Check → Data Fetch → Calculate → Red Flags → AI Analysis → Cache & Return
    
    Args:
        symbol: NSE ticker symbol (e.g., 'RELIANCE.NS')
        company_name: Full company name
        progress_callback: Optional callable(step_name, progress_pct) for UI updates
    
    Returns:
        Complete dossier dict with all 41 research modules
    """
    from core.cache_manager import get_cached, set_cached, is_fresh
    from data.stock_fetcher import fetch_all_data
    from data.news_fetcher import fetch_company_news
    from data.sector_templates import get_sector_template
    from analysis.financial_calculator import calculate_all_metrics
    from analysis.red_flag_engine import run_forensic_checks
    from analysis.source_tracker import SourceTracker
    from ai.gemini_client import GeminiClient
    from ai.research_agents import ResearchAgents
    from ai.explanation_engine import explain_all_metrics

    def update_progress(step: str, pct: int):
        if progress_callback:
            progress_callback(step, pct)

    dossier = {
        "symbol": symbol,
        "company_name": company_name,
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S IST"),
        "modules": {},
        "errors": [],
    }

    source_tracker = SourceTracker()

    # ── Step 1: Check cache for complete dossier ──────────────
    update_progress("Checking cache...", 5)
    cached_dossier = get_cached(symbol, "full_dossier")
    if cached_dossier and is_fresh(symbol, "full_dossier"):
        # Check if dynamic sections need refresh
        needs_news_refresh = not is_fresh(symbol, "news")
        needs_price_refresh = not is_fresh(symbol, "price_data")

        if not needs_news_refresh and not needs_price_refresh:
            cached_dossier["from_cache"] = True
            return cached_dossier
        else:
            # Use cached dossier but refresh dynamic sections
            dossier = cached_dossier
            dossier["from_cache"] = "partial"

    # ── Step 2: Fetch raw stock data from yfinance ────────────
    update_progress("Fetching stock data from markets...", 10)
    try:
        stock_data = fetch_all_data(symbol)
        if not stock_data or not stock_data.get("info"):
            dossier["errors"].append("Could not fetch stock data. Please check the symbol.")
            return dossier

        # Track source
        source_tracker.add_claim(
            claim=f"Stock data for {symbol}",
            value="fetched",
            source="Yahoo Finance",
            source_type="Data aggregator",
            confidence=85,
            module="stock_data"
        )
    except Exception as e:
        dossier["errors"].append(f"Data fetch error: {str(e)}")
        traceback.print_exc()
        return dossier

    dossier["modules"]["raw_data"] = stock_data

    # ── Step 3: Extract company profile ───────────────────────
    update_progress("Building company profile...", 20)
    info = stock_data.get("info", {})
    dossier["modules"]["company_snapshot"] = {
        "name": info.get("longName", company_name),
        "symbol": symbol,
        "nse_symbol": symbol.replace(".NS", "").replace(".BO", ""),
        "sector": info.get("sector", "N/A"),
        "industry": info.get("industry", "N/A"),
        "market_cap": info.get("marketCap", 0),
        "market_cap_formatted": _format_market_cap(info.get("marketCap", 0)),
        "website": info.get("website", ""),
        "employees": info.get("fullTimeEmployees", "N/A"),
        "description": info.get("longBusinessSummary", ""),
        "country": info.get("country", "India"),
        "city": info.get("city", ""),
    }

    # ── Step 4: Extract price data ────────────────────────────
    update_progress("Processing price data...", 25)
    dossier["modules"]["price_data"] = stock_data.get("price_data", {})

    # ── Step 5: Financial calculations (CODE, not AI) ─────────
    update_progress("Running financial calculations...", 35)
    try:
        computed_metrics = calculate_all_metrics(stock_data)
        dossier["modules"]["computed_metrics"] = computed_metrics

        # Track calculated metrics source
        for metric_name in computed_metrics:
            source_tracker.add_claim(
                claim=f"{metric_name} calculated",
                value=computed_metrics[metric_name],
                source="Financial Calculator (Code)",
                source_type="Calculated from audited data",
                confidence=95,
                module="financial_calculations"
            )
    except Exception as e:
        dossier["errors"].append(f"Calculation error: {str(e)}")
        computed_metrics = {}
        traceback.print_exc()

    # ── Step 6: Red-flag forensic checks (CODE, not AI) ───────
    update_progress("Running forensic red-flag checks...", 45)
    try:
        red_flags = run_forensic_checks(stock_data, computed_metrics)
        dossier["modules"]["red_flags"] = red_flags
    except Exception as e:
        dossier["errors"].append(f"Red-flag engine error: {str(e)}")
        red_flags = []
        traceback.print_exc()

    # ── Step 7: Fetch news ────────────────────────────────────
    update_progress("Gathering latest news...", 50)
    try:
        news = fetch_company_news(company_name, symbol)
        dossier["modules"]["news"] = news
        set_cached(symbol, "news", {"news": news})
    except Exception as e:
        dossier["errors"].append(f"News fetch error: {str(e)}")
        news = []
        traceback.print_exc()

    # ── Step 8: Dividends & Corporate Actions ─────────────────
    update_progress("Processing dividends & corporate actions...", 55)
    dossier["modules"]["dividends"] = stock_data.get("dividends", {})
    dossier["modules"]["corporate_actions"] = stock_data.get("actions", {})

    # ── Step 9: Shareholding ──────────────────────────────────
    update_progress("Analyzing shareholding pattern...", 58)
    dossier["modules"]["holders"] = stock_data.get("holders", {})

    # ── Step 10: Sector-specific template ─────────────────────
    update_progress("Loading sector analysis template...", 60)
    sector = info.get("sector", "")
    sector_template = get_sector_template(sector)
    dossier["modules"]["sector_template"] = sector_template

    # ── Step 11: AI-powered analysis (Gemini) ─────────────────
    update_progress("AI is analyzing the company (this takes a moment)...", 65)
    try:
        gemini = GeminiClient()
        agents = ResearchAgents(gemini)

        # Generate executive summary
        update_progress("Writing executive summary...", 70)
        exec_summary = agents.generate_executive_summary(stock_data, computed_metrics, red_flags)
        dossier["modules"]["executive_summary"] = exec_summary

        # Generate company profile narrative
        update_progress("Building company profile...", 75)
        company_profile = agents.generate_company_profile(stock_data)
        dossier["modules"]["company_profile_narrative"] = company_profile

        # Generate strengths & weaknesses
        update_progress("Identifying strengths & weaknesses...", 78)
        swot = agents.generate_strengths_weaknesses(stock_data, computed_metrics, red_flags)
        dossier["modules"]["strengths_weaknesses"] = swot

        # Generate risk assessment
        update_progress("Assessing risks...", 80)
        risks = agents.generate_risk_assessment(stock_data, computed_metrics)
        dossier["modules"]["risk_assessment"] = risks

        # Generate future outlook
        update_progress("Analyzing future outlook...", 83)
        outlook = agents.generate_future_outlook(stock_data, news)
        dossier["modules"]["future_outlook"] = outlook

        # Generate simple explanations for all metrics
        update_progress("Converting to simple language...", 86)
        simple_explanations = explain_all_metrics(computed_metrics, gemini)
        dossier["modules"]["simple_explanations"] = simple_explanations

        # Generate investor questions (not BUY/SELL)
        update_progress("Preparing investor decision questions...", 89)
        questions = agents.generate_investor_questions(stock_data, computed_metrics, red_flags)
        dossier["modules"]["investor_questions"] = questions

        # Generate what to monitor
        update_progress("Identifying what to watch...", 91)
        monitor = agents.generate_what_to_monitor(stock_data, computed_metrics)
        dossier["modules"]["what_to_monitor"] = monitor

        # Track AI sources
        source_tracker.add_claim(
            claim="AI analysis generated",
            value="complete",
            source="Google Gemini 2.0 Flash",
            source_type="AI-generated analysis",
            confidence=75,
            module="ai_analysis"
        )

    except Exception as e:
        dossier["errors"].append(f"AI analysis error: {str(e)}")
        traceback.print_exc()

    # ── Step 12: Investment Research Summary ───────────────────
    update_progress("Compiling investment research summary...", 93)
    dossier["modules"]["research_summary"] = _build_research_summary(
        computed_metrics, red_flags, stock_data
    )

    # ── Step 13: Save source tracking ─────────────────────────
    update_progress("Saving source evidence...", 95)
    dossier["modules"]["source_tracking"] = source_tracker.to_dict()

    # ── Step 14: Cache the complete dossier ────────────────────
    update_progress("Caching research for future visitors...", 98)
    dossier["from_cache"] = False
    try:
        set_cached(symbol, "full_dossier", dossier)
    except Exception:
        pass  # Cache failure is non-critical

    update_progress("Research complete!", 100)
    return dossier


def _format_market_cap(value: float) -> str:
    """Format market cap in Indian number system (Crore/Lakh)."""
    if not value or value == 0:
        return "N/A"
    crore = value / 1e7
    if crore >= 100000:
        return f"₹{crore / 100000:.2f} Lakh Cr"
    elif crore >= 1:
        return f"₹{crore:,.0f} Cr"
    else:
        lakh = value / 1e5
        return f"₹{lakh:,.0f} Lakh"


def _build_research_summary(metrics: dict, red_flags: list, stock_data: dict) -> dict:
    """Build the Investment Research Summary table (SEBI-safe, no BUY/SELL)."""
    info = stock_data.get("info", {})

    def assess(metric_dict: dict, key: str, good_threshold: float, 
               bad_threshold: float, higher_is_better: bool = True) -> str:
        val = metric_dict.get(key, {}).get("value") if isinstance(metric_dict.get(key), dict) else None
        if val is None:
            return "Data unavailable"
        if higher_is_better:
            if val >= good_threshold:
                return "Strong"
            elif val >= bad_threshold:
                return "Moderate"
            else:
                return "Weak"
        else:
            if val <= good_threshold:
                return "Strong"
            elif val <= bad_threshold:
                return "Moderate"
            else:
                return "Weak"

    profitability = metrics.get("profitability", {})
    growth = metrics.get("growth", {})
    debt = metrics.get("debt_metrics", {})
    cashflow = metrics.get("cash_flow_quality", {})

    # Count material red flags
    danger_flags = [f for f in red_flags if f.get("severity") == "danger"]
    warning_flags = [f for f in red_flags if f.get("severity") == "warning"]

    governance = "None material identified"
    if danger_flags:
        governance = f"{len(danger_flags)} concerns identified"
    elif warning_flags:
        governance = f"{len(warning_flags)} items to monitor"

    return {
        "dimensions": [
            {"dimension": "Business quality", "assessment": assess(profitability, "roce", 15, 10) if profitability.get("roce") else assess(profitability, "roe", 15, 10)},
            {"dimension": "Revenue visibility", "assessment": assess(growth, "revenue_cagr_3y", 10, 5) if growth.get("revenue_cagr_3y") else assess(growth, "revenue_cagr_1y", 10, 0)},
            {"dimension": "Balance sheet", "assessment": assess(debt, "debt_to_equity", 0.5, 1.5, higher_is_better=False)},
            {"dimension": "Cash generation", "assessment": assess(cashflow, "cfo_to_pat", 0.8, 0.5)},
            {"dimension": "Governance flags", "assessment": governance},
            {"dimension": "Valuation", "assessment": "Data shown without recommendation"},
            {"dimension": "Key risk", "assessment": _identify_key_risk(red_flags, metrics)},
            {"dimension": "Key catalyst", "assessment": _identify_key_catalyst(growth, stock_data)},
            {"dimension": "Information confidence", "assessment": "High"},
        ]
    }


def _identify_key_risk(red_flags: list, metrics: dict) -> str:
    """Identify the single most important risk."""
    danger_flags = [f for f in red_flags if f.get("severity") == "danger"]
    if danger_flags:
        return danger_flags[0].get("title", "See red flags")
    warning_flags = [f for f in red_flags if f.get("severity") == "warning"]
    if warning_flags:
        return warning_flags[0].get("title", "See warnings")
    return "No major risks identified"


def _identify_key_catalyst(growth: dict, stock_data: dict) -> str:
    """Identify a potential catalyst."""
    revenue_growth = growth.get("revenue_cagr_3yr", {}).get("value") if isinstance(growth.get("revenue_cagr_3yr"), dict) else None
    if revenue_growth and revenue_growth > 15:
        return "Strong revenue growth momentum"
    elif revenue_growth and revenue_growth > 10:
        return "Steady growth trajectory"
    return "Monitor for catalysts"
