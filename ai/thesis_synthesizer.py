"""
masterSchetan CCIE — Central Thesis Synthesizer
Generates the Central Thesis State Object (CTSO) — the "golden thread" 
that unifies all 26 sections into a coherent investment narrative.
"""

import json
import logging
from typing import Optional
from ai.gemini_client import GeminiClient
from ai.llm_provider import safe_dumps

logger = logging.getLogger(__name__)


# ── Company Archetypes ────────────────────────────────
ARCHETYPES = {
    "GROWTH_COMPOUNDER": "Consistent revenue & earnings growth above sector average with expanding margins",
    "TURNAROUND_PLAY": "Company recovering from a period of financial distress or operational underperformance",
    "DEEP_VALUE": "Trading significantly below intrinsic value with strong asset backing",
    "CAPACITY_EXPANSION": "Aggressively expanding production/service capacity with front-loaded capex",
    "GOVERNMENT_UTILITY": "Government-backed entity with regulated returns and policy-driven growth",
    "DELEVERAGING_STORY": "Actively reducing debt burden, leading to ROCE expansion and re-rating",
    "CYCLICAL_RECOVERY": "Benefiting from a sectoral upcycle after a prolonged downturn",
    "DIVIDEND_ARISTOCRAT": "Consistent high dividend payout with stable cash generation",
    "MARKET_LEADER": "Dominant market share with strong competitive moat and pricing power",
    "ASSET_LIGHT_PLATFORM": "Scalable platform business with high ROE and low capital intensity",
    "DISTRESSED_ENTITY": "Facing significant financial, operational, or governance challenges",
}


def _build_ctso_input(info: dict, computed_metrics: dict, red_flags: list, sector_template: dict, news: list) -> str:
    """Builds a concise text summary of the company's financial position for the LLM."""
    
    # Extract Profitability
    roe = computed_metrics.get("ROE", "N/A")
    roce = computed_metrics.get("ROCE", "N/A")
    op_margin = computed_metrics.get("Operating Margin", "N/A")
    
    # Extract Growth
    rev_cagr_1y = computed_metrics.get("Revenue CAGR 1Y", "N/A")
    rev_cagr_3y = computed_metrics.get("Revenue CAGR 3Y", "N/A")
    pat_cagr = computed_metrics.get("PAT CAGR", "N/A")
    
    # Extract Debt
    de_ratio = computed_metrics.get("D/E", "N/A")
    int_cov = computed_metrics.get("Interest Coverage", "N/A")
    
    # Extract Cash Flow
    cfo_pat = computed_metrics.get("CFO/PAT", "N/A")
    fcf = computed_metrics.get("FCF", "N/A")
    
    # Extract Valuation
    pe = computed_metrics.get("P/E", "N/A")
    pb = computed_metrics.get("P/B", "N/A")
    div_yield = computed_metrics.get("Dividend Yield", "N/A")
    
    # Format Red Flags
    red_flag_text = ""
    if red_flags:
        red_flag_text = "\n".join([f"- [{rf.get('severity', 'Warning')}] {rf.get('description', '')}" for rf in red_flags])
    else:
        red_flag_text = "None detected."
        
    # Sector Context
    key_questions = ""
    if sector_template and "key_questions" in sector_template:
        key_questions = "\n".join([f"- {q}" for q in sector_template["key_questions"]])
        
    # News
    news_text = ""
    if news:
        # Assuming news is sorted or we take first 5
        top_news = news[:5]
        news_text = "\n".join([f"- {n.get('title', n.get('headline', ''))}" for n in top_news])
        
    summary = f"""
Profitability:
- ROE: {roe}
- ROCE: {roce}
- Operating Margin: {op_margin}

Growth:
- Revenue CAGR 1Y: {rev_cagr_1y}
- Revenue CAGR 3Y: {rev_cagr_3y}
- PAT CAGR: {pat_cagr}

Debt & Solvency:
- D/E Ratio: {de_ratio}
- Interest Coverage: {int_cov}

Cash Flow:
- CFO/PAT: {cfo_pat}
- FCF: {fcf}

Valuation:
- P/E: {pe}
- P/B: {pb}
- Dividend Yield: {div_yield}

Red Flags:
{red_flag_text}

Sector Context (Key Questions):
{key_questions if key_questions else "N/A"}

Recent Material News:
{news_text if news_text else "None"}
"""
    return summary


def _generate_rule_based_ctso(info: dict, computed_metrics: dict, red_flags: list, sector_template: dict) -> dict:
    """Fallback when LLM is unavailable. Uses deterministic rules."""
    market_cap = info.get("marketCap", 0)
    
    # Helper to parse metric values
    def get_num(key):
        val = computed_metrics.get(key, 0)
        try:
            # Handle string percentages if needed
            if isinstance(val, str) and "%" in val:
                return float(val.replace("%", "").strip())
            return float(val) if val is not None else 0.0
        except (ValueError, TypeError):
            return 0.0

    roe = get_num("ROE")
    de = get_num("D/E")
    rev_growth = get_num("Revenue CAGR 1Y")
    div_yield = get_num("Dividend Yield")
    op_margin_trend = computed_metrics.get("Operating Margin Trend", "flat")
    de_trend = computed_metrics.get("D/E Trend", "flat")
    
    # Check promoter holding
    promoter_holding = info.get("heldPercentInsiders", 0) * 100
    is_govt = "government" in str(info.get("longName", "")).lower() or "state" in str(info.get("longName", "")).lower()
    
    # Count danger flags
    danger_flags = sum(1 for rf in red_flags if str(rf.get("severity", "")).lower() == "danger")
    
    archetype = "CYCLICAL_RECOVERY" # Default
    
    if danger_flags >= 2:
        archetype = "DISTRESSED_ENTITY"
    elif market_cap > 1000000000000 and roe > 15:
        archetype = "MARKET_LEADER"
    elif de > 2 and de_trend == "decreasing":
        archetype = "DELEVERAGING_STORY"
    elif rev_growth > 20 and op_margin_trend == "expanding":
        archetype = "GROWTH_COMPOUNDER"
    elif is_govt and promoter_holding > 50:
        archetype = "GOVERNMENT_UTILITY"
    elif div_yield > 3:
        archetype = "DIVIDEND_ARISTOCRAT"
    elif sector_template:
        sector_name = sector_template.get("name", "").lower()
        if "it" in sector_name or "platform" in sector_name:
            archetype = "ASSET_LIGHT_PLATFORM"
        elif "bank" in sector_name or "nbfc" in sector_name:
            archetype = "GROWTH_COMPOUNDER"
            
    return {
        "archetype": archetype,
        "golden_thread": f"Rule-based thesis mapping to {archetype} driven by basic financial filters.",
        "key_positive_drivers": ["Metric-driven strengths observed in basic financials"],
        "key_risk_factors": [rf.get("description", "Potential risks") for rf in red_flags] if red_flags else ["Standard market risks"],
        "conviction_level": "Medium"
    }


def _fallback_thesis_prompt() -> str:
    return """You are a top-tier institutional equity research analyst.
Your job is to synthesize the 'Central Thesis State Object' (CTSO) based on financial metrics, sector context, and red flags.
Analyze the provided data, identify the most appropriate Company Archetype from the available list, and write a unifying 'golden thread' narrative.
Return ONLY a valid JSON object with the following schema:
{
  "archetype": "string (must match one of the provided available archetypes)",
  "golden_thread": "string (2-3 sentences summarizing the core investment narrative)",
  "key_positive_drivers": ["string", "string"],
  "key_risk_factors": ["string", "string"],
  "conviction_level": "string (High, Medium, or Low)"
}"""


def generate_ctso(stock_data: dict, computed_metrics: dict, red_flags: list, 
                  sector_template: dict, news: list = None) -> dict:
    """
    Generate the Central Thesis State Object (CTSO).
    
    This is the single most important AI call in the entire application.
    It determines the "golden thread" narrative that ties all 26 sections together.
    
    Args:
        stock_data: Raw stock data from yfinance
        computed_metrics: Calculated financial metrics
        red_flags: List of forensic red flags
        sector_template: Sector-specific analysis template
        news: Recent news articles (optional)
    
    Returns:
        CTSO dict with archetype, golden_thread, drivers, risks, conviction
    """
    info = stock_data.get("info", {})
    company_name = info.get("longName", info.get("shortName", "Unknown"))
    sector = info.get("sector", "N/A")
    industry = info.get("industry", "N/A")
    market_cap = info.get("marketCap", 0)
    
    # Build a focused data summary for the LLM (don't send everything — too noisy)
    data_summary = _build_ctso_input(info, computed_metrics, red_flags, sector_template, news)
    
    # Import the prompt
    try:
        from ai.prompts.system_prompts import THESIS_SYNTHESIZER_PROMPT
    except ImportError:
        THESIS_SYNTHESIZER_PROMPT = _fallback_thesis_prompt()
    
    prompt = f"""Company: {company_name}
Sector: {sector} | Industry: {industry}
Market Cap: ₹{market_cap / 1e7:,.0f} Cr

Available Archetypes: {json.dumps(list(ARCHETYPES.keys()))}

FINANCIAL DATA SUMMARY:
{data_summary}

Generate the Central Thesis State Object (CTSO) as JSON."""
    
    try:
        client = GeminiClient()
        result = client.generate(
            prompt=prompt,
            system_instruction=THESIS_SYNTHESIZER_PROMPT,
            json_mode=True,
            temperature=0.3
        )
        
        if result:
            ctso = json.loads(result)
            # Validate required fields
            required = ['archetype', 'golden_thread', 'conviction_level']
            if all(k in ctso for k in required):
                ctso['company_name'] = company_name
                ctso['sector'] = sector
                logger.info(f"CTSO generated for {company_name}: {ctso.get('archetype')}")
                return ctso
    except Exception as e:
        logger.warning(f"CTSO LLM generation failed: {e}")
    
    # Fallback: Rule-based CTSO generation
    return _generate_rule_based_ctso(info, computed_metrics, red_flags, sector_template)


def interpret_section_with_ctso(section_number: int, section_name: str, 
                                  section_data: dict, ctso: dict,
                                  sector_template: dict = None) -> str:
    """
    Generate AI interpretation for a specific report section using CTSO context.
    This ensures every section connects back to the central thesis.
    """
    try:
        from ai.prompts.system_prompts import SECTION_INTERPRETER_PROMPT
    except ImportError:
        SECTION_INTERPRETER_PROMPT = "You are a financial analyst. Interpret the provided section data in the context of the Central Thesis. Connect the data back to the 'golden thread' narrative. Keep it concise."
        
    prompt = f"""Central Thesis (Golden Thread): {ctso.get('golden_thread', 'N/A')}
Company Archetype: {ctso.get('archetype', 'N/A')}
Section {section_number}: {section_name}

Section Data:
{safe_dumps(section_data)}

Sector Context:
{safe_dumps(sector_template) if sector_template else 'N/A'}

Analyze this section's data and explain how it supports or contradicts the central thesis.
"""
    try:
        client = GeminiClient()
        result = client.generate(
            prompt=prompt,
            system_instruction=SECTION_INTERPRETER_PROMPT,
            temperature=0.4
        )
        if result:
            return result
    except Exception as e:
        logger.warning(f"Section interpretation failed for {section_name}: {e}")
        
    # Fallback rule-based interpretation
    return f"Based on the provided data for {section_name}, the section aligns with the overall archetype of {ctso.get('archetype', 'Unknown')}."
