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
    from data.sector_templates import get_sector_template, classify_company_type, classify_sector
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
                verification_status="DERIVED_FROM_SECONDARY",
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
                verification_status="DERIVED_FROM_SECONDARY",
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
                source=n.get('source', 'Google News RSS Aggregator'),
                source_type="Google News RSS Aggregator",
                confidence=70,
                verification_status="SINGLE_SECONDARY",
                claim_type="MEDIA_REPORT",
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

    # ── Step 10: Canonical Company Classification & Sector Template ─────────
    update_progress("Classifying company & loading sector analysis template...", 60)
    sector = info.get("sector", "")
    industry = info.get("industry", "")
    company_type = classify_company_type(sector, industry, company_name, symbol)
    
    dossier["company_type"] = company_type
    dossier["modules"]["company_type"] = company_type
    
    sector_template = get_sector_template(company_type)
    dossier["modules"]["sector_template"] = sector_template

    # ── Step 10.1: Build Canonical Decision Support Object ──────────────────
    update_progress("Building unified decision support engine...", 61)
    try:
        from analysis.decision_engine import DecisionEngine
        engine = DecisionEngine()
        evidence_summary = source_tracker.get_confidence_summary()
        decision_support = engine.build(
            dossier=dossier,
            company_type=company_type,
            computed_metrics=computed_metrics,
            evidence_summary=evidence_summary,
            red_flags=red_flags,
            dividends=stock_data.get("dividends", []),
            news=news
        )
        dossier["decision_support"] = decision_support
        dossier["modules"]["decision_support"] = decision_support
        dossier["modules"]["common_man_report"] = decision_support
    except Exception as e:
        dossier["errors"].append(f"DecisionEngine error: {str(e)}")
        decision_support = {}
        traceback.print_exc()

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
        research_snapshot = _compute_research_snapshot(computed_metrics, red_flags, info, company_type, decision_support)
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
        computed_metrics, red_flags, stock_data, decision_support, evidence_summary
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


def _build_research_summary(metrics: dict, red_flags: list, stock_data: dict, decision_support: dict = None, source_summary: dict = None) -> dict:
    """Build the Investment Research Summary table using canonical DecisionSupport."""
    if isinstance(decision_support, dict) and decision_support.get("business_health"):
        biz_assess = "Strong" if "STRONG" in decision_support["business_health"].get("status", "") else ("Weak" if "WEAK" in decision_support["business_health"].get("status", "") else "Moderate")
        growth_assess = "Strong" if decision_support.get("growth", {}).get("status") == "STRONG" else ("Weak" if decision_support.get("growth", {}).get("status") == "DECLINING" else "Moderate")
        bal_assess = decision_support.get("financial_health", {}).get("status", "STABLE").replace("_", " ").title()
        val_assess = decision_support.get("valuation", {}).get("verdict_label", "Data shown without recommendation")
        conf_label = source_summary.get("status", "MEDIUM") if isinstance(source_summary, dict) else "MEDIUM"

        danger_flags = [f for f in red_flags if isinstance(f, dict) and f.get("severity") == "danger"]
        warning_flags = [f for f in red_flags if isinstance(f, dict) and f.get("severity") == "warning"]
        gov_str = f"{len(danger_flags)} danger flags" if danger_flags else (f"{len(warning_flags)} monitor items" if warning_flags else "Clean")

        return {
            "dimensions": [
                {"dimension": "Business quality", "assessment": biz_assess},
                {"dimension": "Revenue visibility", "assessment": growth_assess},
                {"dimension": "Balance sheet", "assessment": bal_assess},
                {"dimension": "Cash generation", "assessment": "Evaluated in CFO/PAT"},
                {"dimension": "Governance flags", "assessment": gov_str},
                {"dimension": "Valuation", "assessment": val_assess},
                {"dimension": "Key risk", "assessment": _identify_key_risk(red_flags, metrics)},
                {"dimension": "Key catalyst", "assessment": _identify_key_catalyst(metrics.get("growth", {}), stock_data)},
                {"dimension": "Information confidence", "assessment": conf_label},
            ]
        }

    return {
        "dimensions": [
            {"dimension": "Information confidence", "assessment": "UNVERIFIED"}
        ]
    }


def _identify_key_risk(red_flags: list, metrics: dict) -> str:
    """Identify the single most important risk."""
    danger_flags = [f for f in red_flags if isinstance(f, dict) and f.get("severity") == "danger"]
    if danger_flags:
        return danger_flags[0].get("title", "See red flags")
    warning_flags = [f for f in red_flags if isinstance(f, dict) and f.get("severity") == "warning"]
    if warning_flags:
        return warning_flags[0].get("title", "See warnings")
    return "No major risks identified"


def _identify_key_catalyst(growth: dict, stock_data: dict) -> str:
    """Identify a potential catalyst."""
    revenue_growth = growth.get("revenue_cagr_1y", {}).get("value") if isinstance(growth.get("revenue_cagr_1y"), dict) else None
    if revenue_growth and revenue_growth > 15:
        return "Strong revenue growth momentum"
    elif revenue_growth and revenue_growth > 10:
        return "Steady growth trajectory"
    return "Monitor for catalysts"


def _compute_research_snapshot(metrics: dict, red_flags: list, info: dict, company_type: str = "DEFAULT", decision_support: dict = None) -> dict:
    """Compute the Research Snapshot diagnostic matrix from actual data and decision_support."""
    market_cap = info.get("marketCap", 0)
    
    # Business Scale
    cap_cr = market_cap / 1e7 if isinstance(market_cap, (int, float)) else 0
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

    if isinstance(decision_support, dict) and decision_support.get("financial_health"):
        solvency = decision_support["financial_health"].get("status", "STABLE").replace("_", " ").title()
        growth_mom = decision_support.get("growth", {}).get("status", "STABLE").replace("_", " ").title()
    else:
        solvency = "Comfortable"
        growth_mom = "Stable"

    prof = metrics.get("profitability", {}) if isinstance(metrics.get("profitability"), dict) else {}
    roe = prof.get("roe", {}).get("value") if isinstance(prof.get("roe"), dict) else None
    if roe is None:
        cap_eff = "Data Unavailable"
    elif roe > 20:
        cap_eff = "Excellent (ROE > 20%)"
    elif roe > 15:
        cap_eff = "Strong (ROE > 15%)"
    elif roe > 10:
        cap_eff = "Adequate"
    else:
        cap_eff = "Subpar"

    danger_flags = [f for f in red_flags if isinstance(f, dict) and f.get("severity") == "danger"]
    warning_flags = [f for f in red_flags if isinstance(f, dict) and f.get("severity") == "warning"]
    if danger_flags:
        governance = "Critical Issues"
    elif warning_flags:
        governance = "Some Concerns"
    else:
        governance = "Clean"

    return {
        "business_scale": business_scale,
        "revenue_momentum": growth_mom,
        "solvency_position": solvency,
        "capital_efficiency": cap_eff,
        "governance_flags": governance,
    }
