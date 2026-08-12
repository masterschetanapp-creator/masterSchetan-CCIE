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
            verification_status="SECONDARY_ONLY",
            claim_type="FACT",
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
                source="Financial Calculator Engine (Python Code)",
                source_type="Calculated from Yahoo Finance financial-statement data",
                confidence=95,
                verification_status="PRIMARY_VERIFIED",
                claim_type="CALCULATION",
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
        for rf in red_flags:
            source_tracker.add_claim(
                claim=f"Forensic Audit Check: {rf.get('title')}",
                value=rf.get('finding'),
                source="Forensic Audit Engine (Code)",
                source_type="Automated Quantitative Check",
                confidence=95,
                verification_status="PRIMARY_VERIFIED",
                claim_type="CALCULATION",
                module="financial_calculations"
            )
    except Exception as e:
        dossier["errors"].append(f"Red-flag engine error: {str(e)}")
        red_flags = []
        traceback.print_exc()

    # ── Step 7: Fetch news & concall transcripts ──────────────
    update_progress("Gathering news & concall transcripts...", 50)
    try:
        from data.news_fetcher import fetch_concall_transcripts
        news = fetch_company_news(company_name, symbol)
        concalls = fetch_concall_transcripts(company_name, symbol)
        dossier["modules"]["news"] = news
        dossier["modules"]["concall_transcripts"] = concalls
        set_cached(symbol, "news", {"news": news})
        for n in news[:5]:
            source_tracker.add_claim(
                claim=f"News: {n.get('title', '')[:80]}",
                value=n.get('source', 'Media'),
                source=n.get('source', 'Google News RSS'),
                source_type="Verified News & Corporate Announcements",
                confidence=80,
                verification_status="MULTI_SOURCE_VERIFIED",
                claim_type="EXTERNAL_ESTIMATE",
                module="news"
            )
    except Exception as e:
        dossier["errors"].append(f"News fetch error: {str(e)}")
        news = []
        dossier["modules"]["concall_transcripts"] = []
        traceback.print_exc()

    # ── Step 8: Dividends & Corporate Actions ─────────────────
    update_progress("Processing dividends & corporate actions...", 55)
    dossier["modules"]["dividends"] = stock_data.get("dividends", {})
    dossier["modules"]["corporate_actions"] = stock_data.get("actions", {})

    # ── Step 9: Shareholding ──────────────────────────────────
    update_progress("Analyzing shareholding pattern...", 58)
    dossier["modules"]["holders"] = stock_data.get("holders", {})
    source_tracker.add_claim(
        claim=f"Shareholding Pattern & Insider Ownership",
        value=f"Insiders {info.get('heldPercentInsiders', 0)*100:.1f}%",
        source="Yahoo Finance API (yfinance)",
        source_type="Secondary Market Data Aggregator",
        confidence=85,
        verification_status="SECONDARY_ONLY",
        claim_type="FACT",
        module="shareholding"
    )

    # ── Step 10: Sector-specific template ─────────────────────
    update_progress("Loading sector analysis template...", 60)
    sector = info.get("sector", "")
    industry = info.get("industry", "")
    sector_template = get_sector_template(sector, industry, company_name, symbol)
    dossier["modules"]["sector_template"] = sector_template

    # ── Step 10.5: Generate Central Thesis (CTSO) ─────────────
    update_progress("Synthesizing central investment thesis...", 62)
    try:
        from ai.thesis_synthesizer import generate_ctso
        ctso = generate_ctso(stock_data, computed_metrics, red_flags, sector_template, news)
        dossier["modules"]["ctso"] = ctso
        if ctso:
            source_tracker.add_claim(
                claim=f"Central Investment Thesis ({ctso.get('archetype', 'Synthesis')})",
                value=ctso.get("golden_thread", "")[:100],
                source="Multi-Model AI Thesis Engine (Gemini 2.5)",
                source_type="AI Institutional Synthesis",
                confidence=85,
                verification_status="SECONDARY_ONLY",
                claim_type="AI_INTERPRETATION",
                module="ai_analysis"
            )
    except Exception as e:
        dossier["errors"].append(f"CTSO generation error: {str(e)}")
        ctso = {}
        dossier["modules"]["ctso"] = ctso
        traceback.print_exc()

    # ── Step 10.6: Compute dynamic Research Snapshot ──────────
    update_progress("Computing research diagnostic snapshot...", 63)
    try:
        research_snapshot = _compute_research_snapshot(computed_metrics, red_flags, info)
        dossier["modules"]["research_snapshot"] = research_snapshot
    except Exception as e:
        dossier["errors"].append(f"Research snapshot error: {str(e)}")
        dossier["modules"]["research_snapshot"] = {}

    # ── Step 11: AI-powered analysis (Gemini) ─────────────────
    update_progress("AI is analyzing the company (this takes a moment)...", 65)
    try:
        gemini = GeminiClient()
        agents = ResearchAgents(gemini)

        # Inject CTSO context into stock data for all agent calls
        if ctso:
            stock_data_with_ctso = dict(stock_data)
            stock_data_with_ctso["_ctso"] = ctso
        else:
            stock_data_with_ctso = stock_data

        # Generate executive summary
        update_progress("Writing executive summary...", 70)
        exec_summary = agents.generate_executive_summary(stock_data_with_ctso, computed_metrics, red_flags)
        dossier["modules"]["executive_summary"] = exec_summary

        # Generate company profile narrative
        update_progress("Building company profile...", 75)
        company_profile = agents.generate_company_profile(stock_data_with_ctso)
        dossier["modules"]["company_profile_narrative"] = company_profile

        # Generate strengths & weaknesses
        update_progress("Identifying strengths & weaknesses...", 78)
        swot = agents.generate_strengths_weaknesses(stock_data_with_ctso, computed_metrics, red_flags)
        dossier["modules"]["strengths_weaknesses"] = swot

        # Generate risk assessment
        update_progress("Assessing risks...", 80)
        risks = agents.generate_risk_assessment(stock_data_with_ctso, computed_metrics)
        dossier["modules"]["risk_assessment"] = risks

        # Generate future outlook
        update_progress("Analyzing future outlook...", 83)
        outlook = agents.generate_future_outlook(stock_data_with_ctso, news)
        dossier["modules"]["future_outlook"] = outlook

        # Generate simple explanations for all metrics
        update_progress("Converting to simple language...", 86)
        simple_explanations = explain_all_metrics(computed_metrics, gemini)
        dossier["modules"]["simple_explanations"] = simple_explanations

        # Generate Common Man Report
        update_progress("Generating Common Man Equity Research report...", 89)
        common_man_report = agents.generate_common_man_report(stock_data_with_ctso, computed_metrics, red_flags, sector_template, news)
        dossier["modules"]["common_man_report"] = common_man_report

        # Generate investor questions (not BUY/SELL)
        update_progress("Preparing investor decision questions...", 89)
        questions = agents.generate_investor_questions(stock_data_with_ctso, computed_metrics, red_flags)
        dossier["modules"]["investor_questions"] = questions

        # Generate what to monitor
        update_progress("Identifying what to watch...", 91)
        monitor = agents.generate_what_to_monitor(stock_data_with_ctso, computed_metrics)
        dossier["modules"]["what_to_monitor"] = monitor

        # Track AI sources
        source_tracker.add_claim(
            claim="AI analysis generated",
            value="complete",
            source="Multi-Model AI (Gemini 2.5 Flash + Groq + OpenRouter)",
            source_type="AI-generated analysis with Central Thesis coherence",
            confidence=80,
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


def _compute_research_snapshot(metrics: dict, red_flags: list, info: dict) -> dict:
    """Compute the Research Snapshot diagnostic matrix from actual data."""
    market_cap = info.get("marketCap", 0)
    
    # Business Scale
    cap_cr = market_cap / 1e7
    if cap_cr >= 100000:
        business_scale = "Mega Cap"
    elif cap_cr >= 20000:
        business_scale = "Large Cap"
    elif cap_cr >= 5000:
        business_scale = "Mid Cap"
    elif cap_cr >= 1000:
        business_scale = "Small Cap"
    else:
        business_scale = "Micro Cap"
    
    # Revenue Momentum
    growth = metrics.get("growth", {})
    rev_1y = growth.get("revenue_cagr_1y", {}).get("value") if isinstance(growth.get("revenue_cagr_1y"), dict) else None
    if rev_1y is None:
        revenue_momentum = "Data Unavailable"
    elif rev_1y > 20:
        revenue_momentum = "Accelerating"
    elif rev_1y > 10:
        revenue_momentum = "Growing"
    elif rev_1y > 0:
        revenue_momentum = "Stable"
    elif rev_1y > -5:
        revenue_momentum = "Stagnating"
    else:
        revenue_momentum = "Declining"
    
    # Solvency Position
    debt = metrics.get("debt_metrics", {})
    de = debt.get("debt_to_equity", {}).get("value") if isinstance(debt.get("debt_to_equity"), dict) else None
    icr = debt.get("interest_coverage", {}).get("value") if isinstance(debt.get("interest_coverage"), dict) else None
    if de is None:
        solvency = "Data Unavailable"
    elif de < 0.3 and (icr is None or icr > 5):
        solvency = "Fortress"
    elif de < 0.8:
        solvency = "Comfortable"
    elif de < 1.5:
        solvency = "Adequate"
    elif de < 2.5:
        solvency = "Stretched"
    else:
        solvency = "Distressed"
    
    # Capital Adequacy (based on ROE/ROCE)
    prof = metrics.get("profitability", {})
    roe = prof.get("roe", {}).get("value") if isinstance(prof.get("roe"), dict) else None
    if roe is None:
        capital_adequacy = "Data Unavailable"
    elif roe > 20:
        capital_adequacy = "Excellent"
    elif roe > 15:
        capital_adequacy = "Strong"
    elif roe > 10:
        capital_adequacy = "Adequate"
    elif roe > 5:
        capital_adequacy = "Tight"
    else:
        capital_adequacy = "Inadequate"
    
    # Earnings Quality
    cf = metrics.get("cash_flow_quality", {})
    cfo_pat = cf.get("cfo_to_pat", {}).get("value") if isinstance(cf.get("cfo_to_pat"), dict) else None
    if cfo_pat is None:
        earnings_quality = "Data Unavailable"
    elif cfo_pat > 1.0:
        earnings_quality = "Excellent"
    elif cfo_pat > 0.75:
        earnings_quality = "Good"
    elif cfo_pat > 0.5:
        earnings_quality = "Average"
    elif cfo_pat > 0.25:
        earnings_quality = "Below Average"
    else:
        earnings_quality = "Poor"
    
    # Governance Flags
    danger_flags = [f for f in red_flags if f.get("severity") == "danger"]
    warning_flags = [f for f in red_flags if f.get("severity") == "warning"]
    if danger_flags:
        governance = "Critical Issues"
    elif warning_flags:
        governance = "Some Concerns"
    else:
        governance = "Clean"
    
    return {
        "business_scale": business_scale,
        "revenue_momentum": revenue_momentum,
        "solvency_position": solvency,
        "capital_adequacy": capital_adequacy,
        "earnings_quality": earnings_quality,
        "governance_flags": governance,
    }
