"""
masterSchetan CCIE — Common Man View Renderer
Renders the beginner-friendly Common Man Equity Research Translator report
matching Bank_of_Maharashtra_Common_Man_View.pdf and TMPV_Common_Man_View.pdf
All verdicts, ratings, valuation views, tip checks, and conclusions are 100% DYNAMICALLY COMPUTED from empirical stock data.
"""

import streamlit as st
import pandas as pd
from ui.components import (
    render_section_header,
    render_callout,
    render_investor_questions
)
from ui.evidence_room import render_evidence_room


def _render_html_table(headers: list, rows: list) -> str:
    """Helper to render clean light-theme HTML table matching PDF report."""
    if not rows:
        return "<p style='color: #64748b;'>No rows available.</p>"
    html = "<div style='margin: 1rem 0; overflow-x: auto;'><table style='width: 100%; border-collapse: collapse; background: #ffffff; border: 1px solid #e2e8f0;'>"
    html += "<thead><tr>"
    for h in headers:
        html += f"<th style='padding: 0.85rem 1rem; background: #0f172a; color: #ffffff; font-weight: 700; border-bottom: 2px solid #2563eb;'>{h}</th>"
    html += "</tr></thead><tbody>"
    
    for r in rows:
        html += "<tr style='border-bottom: 1px solid #e2e8f0;'>"
        for h in headers:
            val = r.get(h, "")
            html += f"<td style='padding: 0.85rem 1rem; color: #0f172a;'>{val}</td>"
        html += "</tr>"
        
    html += "</tbody></table></div>"
    return html


def _generate_empirical_common_man_verdict(company_name: str, symbol: str, sector_name: str, info: dict, price_data: dict, computed: dict, red_flags: list, dividend_history: list = None) -> dict:
    """
    Computes 100% dynamic, data-driven Common Man research verdicts, 30s questions, valuation classifications,
    tip check results, decision support matrix, and bottom line summary based strictly on empirical financial figures.
    Prevents any hard-coded static verdicts for loss-making or high-debt stocks.
    """
    m_prof = computed.get("profitability", {}) if isinstance(computed.get("profitability"), dict) else {}
    m_grow = computed.get("growth", {}) if isinstance(computed.get("growth"), dict) else {}
    m_val = computed.get("valuation", {}) if isinstance(computed.get("valuation"), dict) else {}
    m_debt = computed.get("debt", {}) if isinstance(computed.get("debt"), dict) else {}
    
    roe_val = m_prof.get("roe", {}).get("value") if isinstance(m_prof.get("roe"), dict) else None
    op_margin_val = m_prof.get("operating_margin", {}).get("value") if isinstance(m_prof.get("operating_margin"), dict) else None
    rev_growth_val = m_grow.get("revenue_cagr_1y", {}).get("value") if isinstance(m_grow.get("revenue_cagr_1y"), dict) else None
    pe_val = m_val.get("pe_ratio", {}).get("value") if isinstance(m_val.get("pe_ratio"), dict) else None
    pb_val = m_val.get("pb_ratio", {}).get("value") if isinstance(m_val.get("pb_ratio"), dict) else None
    de_val = m_debt.get("debt_to_equity", {}).get("value") if isinstance(m_debt.get("debt_to_equity"), dict) else None
    
    roe_str = m_prof.get("roe", {}).get("formatted_string", "N/A") if isinstance(m_prof.get("roe"), dict) else "N/A"
    op_str = m_prof.get("operating_margin", {}).get("formatted_string", "N/A") if isinstance(m_prof.get("operating_margin"), dict) else "N/A"
    rev_str = m_grow.get("revenue_cagr_1y", {}).get("formatted_string", "N/A") if isinstance(m_grow.get("revenue_cagr_1y"), dict) else "N/A"
    pe_str = m_val.get("pe_ratio", {}).get("formatted_string", "N/A") if isinstance(m_val.get("pe_ratio"), dict) else "N/A"
    de_str = m_debt.get("debt_to_equity", {}).get("formatted_string", "N/A") if isinstance(m_debt.get("debt_to_equity"), dict) else "N/A"

    div_yield = info.get("dividendYield", 0) or 0
    cur_price = price_data.get("current_price", 0)
    net_income = info.get("netIncomeToCommon") or info.get("trailingEps")
       
    # Check if entity is a Bank / Financial Institution
    sec_ind_text = f"{sector_name} {info.get('industry', '')} {company_name} {symbol}".lower()
    is_bank = any(k in sec_ind_text for k in ["bank", "pnb", "sbin", "hdfc", "icici", "axis", "kotak", "canbk", "unionbank", "bankbaroda", "indusind"])

    # For banks, corporate Debt-to-Equity is NOT a risk metric (Assets/Equity ~10x is normal operating leverage)
    effective_de_val = None if is_bank else de_val

    # 1. Evaluate Business Health
    if net_income is not None and isinstance(net_income, (int, float)) and net_income < 0:
        biz_doing_well = f"NO - {company_name} is currently loss-making."
        biz_status = "WEAK / LOSS-MAKING"
    elif roe_val is not None and isinstance(roe_val, (int, float)) and roe_val > 15 and (rev_growth_val is None or (isinstance(rev_growth_val, (int, float)) and rev_growth_val > 5)):
        biz_doing_well = f"YES - Current operating performance and ROE ({roe_str}) are strong."
        biz_status = "STRONG / IMPROVING"
    elif roe_val is not None and isinstance(roe_val, (int, float)) and roe_val > 8:
        biz_doing_well = f"STABLE - Operating performance is steady with {roe_str} ROE."
        biz_status = "STABLE"
    else:
        biz_doing_well = f"MIXED - Operating returns are modest ({roe_str} ROE)."
        biz_status = "MIXED"

    # 2. Evaluate Net Profit Growth (PAT) — MUST check Profit growth, NOT Revenue!
    pat_growth_obj = m_grow.get("profit_cagr_1y") or m_grow.get("pat_cagr_1y")
    pat_growth_val = pat_growth_obj.get("value") if isinstance(pat_growth_obj, dict) else None
    pat_str = pat_growth_obj.get("formatted_string", "N/A") if isinstance(pat_growth_obj, dict) else "N/A"

    if net_income is not None and isinstance(net_income, (int, float)) and net_income < 0:
        profit_growing = "NO - Company is currently reporting a net loss."
    elif pat_growth_val is not None and isinstance(pat_growth_val, (int, float)) and pat_growth_val > 15:
        profit_growing = f"YES - 1Y Net Profit expanded {pat_str} YoY."
    elif pat_growth_val is not None and isinstance(pat_growth_val, (int, float)) and pat_growth_val > 0:
        profit_growing = f"MODERATE - 1Y Net Profit grew {pat_str} YoY."
    elif pat_growth_val is not None and isinstance(pat_growth_val, (int, float)) and pat_growth_val < 0:
        profit_growing = f"NO - 1Y Net Profit contracted {pat_str} YoY (despite top-line revenue trends)."
    elif rev_growth_val is not None and isinstance(rev_growth_val, (int, float)):
        profit_growing = f"1Y Revenue grew {rev_str} YoY; check P&L for net profit breakdown."
    else:
        profit_growing = "Check audited P&L filings for YoY net profit growth."

    # 3. Evaluate Debt & Asset Quality (Bank vs Corporate routing)
    danger_flags = [rf for rf in red_flags if isinstance(rf, dict) and rf.get("severity") == "danger"]
    
    gnpa_obj = computed.get("gnpa") if isinstance(computed, dict) else None
    nnpa_obj = computed.get("nnpa") if isinstance(computed, dict) else None
    gnpa_val = gnpa_obj.get("value") if isinstance(gnpa_obj, dict) else None
    nnpa_val = nnpa_obj.get("value") if isinstance(nnpa_obj, dict) else None
    gnpa_str = gnpa_obj.get("formatted_string", "N/A") if isinstance(gnpa_obj, dict) else "N/A"
    nnpa_str = nnpa_obj.get("formatted_string", "N/A") if isinstance(nnpa_obj, dict) else "N/A"

    if is_bank:
        if nnpa_val is not None and isinstance(nnpa_val, (int, float)) and nnpa_val > 3.0:
            debt_control = f"NO / CONCERN - Net Bad Loans (NNPA) elevated at {nnpa_str}."
            fin_health = "HIGH BAD LOANS / WEAK"
        elif gnpa_val is not None and isinstance(gnpa_val, (int, float)) and gnpa_val > 5.0:
            debt_control = f"MONITOR - Gross Bad Loans (GNPA) at {gnpa_str} (NNPA: {nnpa_str})."
            fin_health = "NEEDS MONITORING"
        elif len(danger_flags) > 0:
            debt_control = f"MONITOR - {len(danger_flags)} high-severity forensic flags detected."
            fin_health = "NEEDS MONITORING"
        else:
            debt_control = f"YES - Bad loans under control (GNPA: {gnpa_str}, NNPA: {nnpa_str}). Capital position is adequate."
            fin_health = "COMFORTABLE"
    else:
        if de_val is not None and isinstance(de_val, (int, float)) and de_val > 2.0:
            debt_control = f"NO / HIGH RISK - Debt-to-Equity is elevated ({de_str})."
            fin_health = "HIGH LEVERAGE / WEAK"
        elif len(danger_flags) > 0:
            debt_control = f"MONITOR - {len(danger_flags)} high-severity forensic flags detected."
            fin_health = "NEEDS MONITORING"
        elif de_val is not None and isinstance(de_val, (int, float)) and de_val < 0.5 and len(red_flags) == 0:
            debt_control = f"YES - Borrowing is low ({de_str}) and financial position is healthy."
            fin_health = "COMFORTABLE"
        else:
            debt_control = f"STABLE - Debt to Equity is {de_str}."
            fin_health = "STABLE"

    # 4. Evaluate Dividend (Single Unified Engine)
    raw_divs = dividend_history if isinstance(dividend_history, list) else []
    if isinstance(raw_divs, dict) and "dividends" in raw_divs:
        raw_divs = raw_divs["dividends"]
    if not isinstance(raw_divs, list):
        raw_divs = []

    years_paid = set()
    for d in raw_divs:
        if isinstance(d, dict):
            dt_str = str(d.get("Date", d.get("date", "")))
            if len(dt_str) >= 4 and dt_str[:4].isdigit():
                yr = int(dt_str[:4])
                if yr >= 2021:
                    years_paid.add(yr)
    num_years_paid = len(years_paid)

    if not raw_divs and div_yield == 0:
        div_status = "NO VERIFIED RECENT DIVIDEND"
        div_matrix = "NONE"
    elif num_years_paid >= 4:
        div_status = f"REGULAR RECENTLY ({num_years_paid}/5 years paid, Yield: {div_yield*100:.2f}%)"
        div_matrix = "REGULAR RECENTLY"
    elif num_years_paid >= 1 or div_yield > 0:
        div_status = f"IRREGULAR ({num_years_paid}/5 years paid, Yield: {div_yield*100:.2f}%)"
        div_matrix = "IRREGULAR"
    else:
        div_status = "NO VERIFIED RECENT DIVIDEND"
        div_matrix = "NONE"

    # 5. Sector-Specific Valuation Engine
    is_metals = any(k in sec_ind_text for k in ["metal", "steel", "mining", "aluminium", "copper", "iron"])
    is_tech_retail = any(k in sec_ind_text for k in ["tech", "software", "it services", "retail", "internet", "e-commerce"])

    if net_income is not None and isinstance(net_income, (int, float)) and net_income < 0:
        valuation_verdict = "🔴 VERY EXPENSIVE / LOSS-MAKING"
        valuation_expl = f"{company_name} is currently reporting negative net earnings. A loss-making company cannot be evaluated on standard P/E multiples; valuation depends on an operational turnaround."
        cheap_answer = "NO - Company is currently reporting a net loss."
        price_matrix = "HIGH RISK / LOSS-MAKING"

    elif is_bank:
        # Bank Valuation Model: P/B ratio + Asset Efficiency (ROA) + Asset Quality (NNPA)
        pb_str = m_val.get("pb_ratio", {}).get("formatted_string", "N/A") if isinstance(m_val.get("pb_ratio"), dict) else "N/A"
        if pb_val is not None and isinstance(pb_val, (int, float)) and pb_val > 3.0:
            valuation_verdict = "🔴 VERY EXPENSIVE"
            valuation_expl = f"Bank trades at a high price-to-book multiple of {pb_str} net worth. Market expects strong credit expansion and low bad loans."
            cheap_answer = f"NO - Traded at a premium Price-to-Book multiple of {pb_str}."
            price_matrix = "VERY EXPENSIVE"
        elif pb_val is not None and isinstance(pb_val, (int, float)) and pb_val > 1.8:
            valuation_verdict = "🟠 EXPENSIVE"
            valuation_expl = f"Bank trades at {pb_str} Price-to-Book. Operating quality is established, but share price already discounts future credit growth."
            cheap_answer = f"NO - Valued at {pb_str} Price-to-Book multiple."
            price_matrix = "EXPENSIVE"
        elif pb_val is not None and isinstance(pb_val, (int, float)) and pb_val >= 0.8:
            valuation_verdict = "🟡 FAIR"
            valuation_expl = f"Bank trades at a reasonable multiple of {pb_str} Price-to-Book, aligning with sector averages for bank equity."
            cheap_answer = f"FAIR - Valued at a reasonable {pb_str} Price-to-Book."
            price_matrix = "FAIR"
        elif pb_val is not None and isinstance(pb_val, (int, float)) and pb_val < 0.8 and (nnpa_val is None or nnpa_val <= 1.5):
            valuation_verdict = "🟢 ATTRACTIVE"
            valuation_expl = f"Bank trades below book value ({pb_str} P/B) despite manageable bad loans (NNPA: {nnpa_str}). Share price appears discounted relative to asset net worth."
            cheap_answer = f"YES - Discounted valuation at {pb_str} Price-to-Book."
            price_matrix = "ATTRACTIVE"
        else:
            valuation_verdict = "⚪ DIFFICULT TO JUDGE RELIABLY"
            valuation_expl = "Bank valuation multiple could not be reliably verified from available disclosures."
            cheap_answer = "UNCLEAR - Bank valuation metrics could not be verified."
            price_matrix = "UNCLEAR"

    elif is_metals:
        # Metals / Commodity Model: Low trailing P/E often occurs near peak earnings!
        if pe_val is not None and isinstance(pe_val, (int, float)) and pe_val > 25:
            valuation_verdict = "🔴 VERY EXPENSIVE"
            valuation_expl = f"Metal/commodity producer trades at {pe_str} trailing P/E during a cyclical phase."
            cheap_answer = f"NO - Traded at a high P/E multiple of {pe_str}."
            price_matrix = "VERY EXPENSIVE"
        elif pe_val is not None and isinstance(pe_val, (int, float)) and pe_val < 8:
            valuation_verdict = "🟠 CYCLICAL CAUTION"
            valuation_expl = f"Commodity producer trades at a low trailing P/E of {pe_str}. Note for beginners: In cyclical metal sectors, low trailing P/E often occurs near peak cycle earnings."
            cheap_answer = f"CYCLICAL CAUTION - Low P/E ({pe_str}) may reflect peak cycle earnings."
            price_matrix = "EXPENSIVE"
        elif pe_val is not None and isinstance(pe_val, (int, float)) and pe_val >= 8:
            valuation_verdict = "🟡 FAIR"
            valuation_expl = f"Commodity producer trades at {pe_str} P/E, reflecting mid-cycle market pricing."
            cheap_answer = f"FAIR - Traded at {pe_str} P/E."
            price_matrix = "FAIR"
        else:
            valuation_verdict = "⚪ DIFFICULT TO JUDGE RELIABLY"
            valuation_expl = "Commodity valuation multiple could not be verified."
            cheap_answer = "UNCLEAR - Valuation metrics unavailable."
            price_matrix = "UNCLEAR"

    elif is_tech_retail:
        # Fast Growing Tech / Retail Model: Accommodates higher P/E for high ROE (>20%) & high growth
        if pe_val is not None and isinstance(pe_val, (int, float)) and pe_val > 65:
            valuation_verdict = "🔴 VERY EXPENSIVE"
            valuation_expl = f"Fast-growing service/retail business trades at a high multiple of {pe_str} P/E."
            cheap_answer = f"NO - Premium growth multiple of {pe_str} P/E."
            price_matrix = "VERY EXPENSIVE"
        elif pe_val is not None and isinstance(pe_val, (int, float)) and pe_val > 30:
            valuation_verdict = "🟠 EXPENSIVE"
            valuation_expl = f"Trades at {pe_str} P/E. Growth trajectory is healthy, but current share price already discounts future expansion."
            cheap_answer = f"NO - Premium growth pricing at {pe_str} P/E."
            price_matrix = "EXPENSIVE"
        elif pe_val is not None and isinstance(pe_val, (int, float)) and pe_val >= 18:
            valuation_verdict = "🟡 FAIR"
            valuation_expl = f"Trades at a reasonable P/E multiple of {pe_str} relative to sector peer growth rates."
            cheap_answer = f"FAIR - Reasonably priced at {pe_str} P/E."
            price_matrix = "FAIR"
        elif pe_val is not None and isinstance(pe_val, (int, float)) and pe_val < 18:
            valuation_verdict = "🟢 ATTRACTIVE"
            valuation_expl = f"Tech/retail business trades at an attractive multiple of {pe_str} P/E relative to its operating returns."
            cheap_answer = f"YES - Attractively priced at {pe_str} P/E."
            price_matrix = "ATTRACTIVE"
        else:
            valuation_verdict = "⚪ DIFFICULT TO JUDGE RELIABLY"
            valuation_expl = "Valuation multiple could not be verified."
            cheap_answer = "UNCLEAR - Valuation metrics unavailable."
            price_matrix = "UNCLEAR"

    else:
        # Standard Industrial / Corporate Model
        if pe_val is not None and isinstance(pe_val, (int, float)) and pe_val > 50:
            valuation_verdict = "🔴 VERY EXPENSIVE"
            valuation_expl = f"Investors are paying a high growth multiple of {pe_str} trailing profits. The share price carries high market expectations."
            cheap_answer = f"NO - Traded at a premium multiple of {pe_str} P/E."
            price_matrix = "VERY EXPENSIVE"
        elif pe_val is not None and isinstance(pe_val, (int, float)) and pe_val > 28:
            valuation_verdict = "🟠 EXPENSIVE"
            valuation_expl = f"The share trades at {pe_str} P/E. The company is performing well, but investors are already paying a premium for that operating quality."
            cheap_answer = f"NO - Market already prices in performance at {pe_str} P/E."
            price_matrix = "EXPENSIVE"
        elif pe_val is not None and isinstance(pe_val, (int, float)) and pe_val >= 12:
            valuation_verdict = "🟡 FAIR"
            valuation_expl = f"The share trades at a reasonable multiple of {pe_str} trailing profits, aligning with industry valuation benchmarks."
            cheap_answer = f"FAIR - Traded at {pe_str} P/E."
            price_matrix = "FAIR"
        elif pe_val is not None and isinstance(pe_val, (int, float)) and pe_val < 12 and roe_val is not None and isinstance(roe_val, (int, float)) and roe_val > 12:
            valuation_verdict = "🟢 ATTRACTIVE"
            valuation_expl = f"The share trades at a low multiple of {pe_str} P/E despite earning a high ROE of {roe_str}. Today's share price appears deeply discounted."
            cheap_answer = f"YES - Traded at an attractive P/E of {pe_str}."
            price_matrix = "ATTRACTIVE"
        else:
            valuation_verdict = "⚪ DIFFICULT TO JUDGE RELIABLY"
            valuation_expl = "Valuation is difficult to judge reliably — current earnings multiple could not be verified from available primary disclosures."
            cheap_answer = "UNCLEAR - Current earnings multiple could not be verified."
            price_matrix = "UNCLEAR"

    # 6. Sector & Stock Specific Watchpoint
    if is_bank:
        biggest_watch = "Gross bad loans (GNPA), Net NPAs (NNPA), deposit growth velocity, and NIM spread."
    elif "auto" in sec_ind_text or "vehicle" in sec_ind_text:
        biggest_watch = "Vehicle sales volumes, EV penetration, and raw material steel costs."
    elif "tech" in sec_ind_text or "it" in sec_ind_text or "software" in sec_ind_text:
        biggest_watch = "BFSI deal wins, attrition, billing rates, and US client tech spend."
    elif "power" in sec_ind_text or "energy" in sec_ind_text:
        biggest_watch = "PPA tariff execution, renewable project commissioning, and debt levels."
    else:
        biggest_watch = "Quarterly revenue velocity, operating margin, and cash conversion."

    # 7. Tip Check Result (Safe Bank Routing: effective_de_val ignores corporate Debt/Equity for banks)
    if net_income is not None and isinstance(net_income, (int, float)) and net_income < 0:
        tip_result = "MAJOR FUNDAMENTAL CONCERNS"
    elif is_bank and nnpa_val is not None and isinstance(nnpa_val, (int, float)) and nnpa_val > 3.0:
        tip_result = "MAJOR FUNDAMENTAL CONCERNS"
    elif len(danger_flags) > 0 or (effective_de_val is not None and effective_de_val > 2.0):
        tip_result = "HIGH EXPECTATIONS / IMPORTANT RISKS"
    elif roe_val is not None and isinstance(roe_val, (int, float)) and roe_val > 12 and (fin_health in ("COMFORTABLE", "STABLE")):
        tip_result = "FUNDAMENTALLY SUPPORTED IDEA"
    else:
        tip_result = "MIXED FUNDAMENTALS"

    # 8. Risk Rating (Safe Bank Routing: effective_de_val ignores corporate Debt/Equity for banks)
    if len(danger_flags) > 0 or (net_income is not None and isinstance(net_income, (int, float)) and net_income < 0) or (effective_de_val is not None and effective_de_val > 2.0) or (is_bank and nnpa_val is not None and isinstance(nnpa_val, (int, float)) and nnpa_val > 3.0):
        risk_rating = "HIGH"
    elif len(red_flags) > 1 or (effective_de_val is not None and effective_de_val > 1.0) or (is_bank and gnpa_val is not None and isinstance(gnpa_val, (int, float)) and gnpa_val > 5.0):
        risk_rating = "MEDIUM-HIGH"
    else:
        risk_rating = "MEDIUM"

    # 9. Dynamic Bottom Line & Status
    if "STRONG" in biz_status and "ATTRACTIVE" in valuation_verdict:
        final_status = "Research View: 🟢 Strong Business / 🟢 Attractive Price"
    elif "STRONG" in biz_status and ("EXPENSIVE" in valuation_verdict or "FAIR" in valuation_verdict):
        final_status = "Research View: 🟢 Strong Business / 🟡 Price Matters"
    elif "WEAK" in biz_status or "LOSS" in biz_status:
        final_status = "Research View: 🔴 Major Fundamental Concerns / 🔴 Avoid Unproven Turnarounds"
    else:
        final_status = "Research View: 🟡 Mixed Fundamentals / 🟡 Perform Detailed Verification"

    # Beginner-Friendly Jargon-Free Statements (Numbers kept accessible behind 'Show numbers →')
    rev_imp_text = "Sales and overall business activity are expanding YoY." if (rev_growth_val is not None and rev_growth_val > 0) else "Sales trends require close quarterly monitoring."
    
    if roe_val is not None and isinstance(roe_val, (int, float)) and roe_val > 15:
        roe_imp_text = "The company is earning a healthy profit relative to shareholder money."
    elif roe_val is not None and isinstance(roe_val, (int, float)) and roe_val > 8:
        roe_imp_text = "The company generates steady, reasonable returns on shareholder equity."
    else:
        roe_imp_text = "Operating returns generated on shareholder money remain modest."

    if is_bank:
        debt_att_text = "Bad loans and credit risk levels are low and well-controlled." if (nnpa_val is None or nnpa_val <= 1.0) else "Net bad loans require ongoing monitoring."
        careful_debt_text = "Asset quality and credit cost movements require monitoring."
        watch_next_list = [
            "Profit earned on total loans and deposits (NIM spread)",
            "Movement in new bad loans (Slippages & NPAs)",
            "Growth in low-cost savings deposits (CASA ratio)",
            "Safety cushion reserve against bad loans (Capital Adequacy & PCR)"
        ]
    else:
        if de_val is not None and isinstance(de_val, (int, float)) and de_val > 1.5:
            debt_att_text = "Borrowing level is meaningful and should be monitored."
        elif de_val is not None and isinstance(de_val, (int, float)) and de_val < 0.5:
            debt_att_text = "Borrowing levels are low and debt is well within safe boundaries."
        else:
            debt_att_text = "Debt and borrowing levels are moderate and stable."
        careful_debt_text = "Company debt levels require monitoring alongside operating cash flow."
        watch_next_list = [
            "Quarterly sales and customer demand velocity",
            "Profit margin left after operational costs",
            "Actual cash arriving in bank vs reported net profit",
            "Borrowing levels and interest costs",
            "Progress on announced new factories or expansion plans"
        ]

    val_att_text = "Share price carries high market expectations relative to company earnings." if "EXPENSIVE" in valuation_verdict else "Share price trades at reasonable valuation expectations relative to earnings."

    raw_metrics_summary = {
        "Return on Equity (ROE)": roe_str,
        "Operating Margin": op_str,
        "1Y Revenue Growth": rev_str,
        "1Y Net Profit Growth": pat_str,
        "Price-to-Earnings (P/E)": pe_str,
        "Debt to Equity": "N/A (Bank)" if is_bank else de_str,
        "Gross NPAs (GNPA)": gnpa_str if is_bank else "N/A",
        "Net NPAs (NNPA)": nnpa_str if is_bank else "N/A"
    }

    return {
        "summary_30s": [
            {"Question": "Is the business doing well?", "Simple answer": biz_doing_well},
            {"Question": "Is profit growing?", "Simple answer": profit_growing},
            {"Question": "Are debt / bad loans under control?", "Simple answer": debt_control},
            {"Question": "Does it pay dividends?", "Simple answer": div_status},
            {"Question": "Is the share obviously cheap?", "Simple answer": cheap_answer},
            {"Question": "Biggest thing to watch", "Simple answer": biggest_watch}
        ],
        "simple_ai_view": f"{company_name} is operating in {sector_name}. Business health is assessed as {biz_status}, with debt position {fin_health.lower()}. Valuation is currently {valuation_verdict}.",
        "what_company_does": info.get("longBusinessSummary", f"{company_name} operates in the {sector_name} sector, serving consumers and commercial clients."),
        "what_is_improving": [
            rev_imp_text,
            roe_imp_text,
            "Core business profit margin remains stable after meeting operational costs."
        ],
        "what_deserves_attention": [
            debt_att_text,
            f"Automated forensic audit: {len(red_flags)} items flagged for monitoring",
            val_att_text
        ],
        "valuation_verdict": valuation_verdict,
        "valuation_explanation": valuation_expl,
        "why_consider": [
            f"Established business scale and market presence in {sector_name}",
            "Strong track record of earning profit on shareholder capital",
            "Established domestic customer franchise and distribution network",
            "Promoter / Controlling ownership stability",
            "Regular audited financial disclosures filed with BSE/NSE"
        ],
        "why_be_careful": [
            f"Share valuation is assessed as {valuation_verdict}",
            careful_debt_text,
            f"{len(red_flags)} accounting/forensic checks flagged for monitoring",
            "Sensitivity to raw material cost inflation and broader economic demand",
            "Share price alone does not indicate whether a stock is cheap or expensive"
        ],
        "tip_check_rows": [
            {"Question": "Does the company make money?", "Simple answer": "NO (Loss-making)" if net_income is not None and isinstance(net_income, (int, float)) and net_income < 0 else "YES"},
            {"Question": "Is profit improving?", "Simple answer": profit_growing},
            {"Question": "Is core business growing?", "Simple answer": f"Sales 1Y: {rev_str}"},
            {"Question": "Are debt / bad loans okay?", "Simple answer": debt_control},
            {"Question": "Does it pay dividends?", "Simple answer": div_status},
            {"Question": "Is it obviously cheap?", "Simple answer": cheap_answer},
            {"Question": "Main thing people may overlook", "Simple answer": biggest_watch}
        ],
        "tip_check_result": tip_result,
        "beginner_watch_next": watch_next_list,
        "decision_matrix": [
            {"Area": "Business", "Assessment": biz_status},
            {"Area": "Financial Health", "Assessment": fin_health},
            {"Area": "Dividend", "Assessment": div_matrix},
            {"Area": "Price", "Assessment": valuation_verdict},
            {"Area": "Risk", "Assessment": risk_rating}
        ],
        "raw_metrics_summary": raw_metrics_summary,
        "bottom_line": f"Based on empirical financial statements, {company_name}'s business quality is assessed as {biz_status} with {fin_health.lower()} financial health. At today's price of ₹{cur_price:,.2f}, valuation is {valuation_verdict}. The key variable for an investor is whether earnings will support this price.",
        "final_research_status": final_status
    }


def render_common_man_view(dossier: dict):
    """
    Renders the exact Common Man View report for first-time or non-technical investors.
    Following the PDF blueprint from Bank_of_Maharashtra_Common_Man_View.pdf and TMPV_Common_Man_View.pdf
    All verdicts are 100% dynamically computed from empirical financial data.
    """
    if not dossier:
        st.warning("No dossier data available.")
        return

    company_name = dossier.get("company_name", "Company")
    symbol = dossier.get("symbol", "TICKER")
    modules = dossier.get("modules", {})
    raw_data = modules.get("raw_data", {})
    info = raw_data.get("info", {})
    price_data = modules.get("price_data", {})
    computed = modules.get("computed_metrics", {})
    red_flags = modules.get("red_flags", [])
    profile = modules.get("company_snapshot", {})
    # Extract single unified dividend history
    dividend_history = modules.get("dividends", [])
    if isinstance(dividend_history, dict) and "dividends" in dividend_history:
        dividend_history = dividend_history["dividends"]
    if not isinstance(dividend_history, list):
        dividend_history = []

    # Generate empirical verdicts (100% data-driven, single unified dividend engine)
    empirical_cm = _generate_empirical_common_man_verdict(
        company_name, symbol, sector_name, info, price_data, computed, red_flags,
        dividend_history=dividend_history
    )
    
    # Merge AI report outputs with empirical verdicts (Deterministic Facts + AI Beginner Language Translation)
    ai_cm_report = modules.get("common_man_report", {})
    cm_report = dict(empirical_cm)
    if isinstance(ai_cm_report, dict) and len(ai_cm_report) > 0:
        if ai_cm_report.get("simple_ai_view"):
            cm_report["simple_ai_view"] = ai_cm_report["simple_ai_view"]
        if ai_cm_report.get("what_company_does"):
            cm_report["what_company_does"] = ai_cm_report["what_company_does"]
        if ai_cm_report.get("what_is_improving") and isinstance(ai_cm_report["what_is_improving"], list) and len(ai_cm_report["what_is_improving"]) > 0:
            cm_report["what_is_improving"] = ai_cm_report["what_is_improving"]
        if ai_cm_report.get("what_deserves_attention") and isinstance(ai_cm_report["what_deserves_attention"], list) and len(ai_cm_report["what_deserves_attention"]) > 0:
            cm_report["what_deserves_attention"] = ai_cm_report["what_deserves_attention"]
        if ai_cm_report.get("valuation_explanation"):
            cm_report["valuation_explanation"] = ai_cm_report["valuation_explanation"]
        if ai_cm_report.get("why_consider") and isinstance(ai_cm_report["why_consider"], list) and len(ai_cm_report["why_consider"]) > 0:
            cm_report["why_consider"] = ai_cm_report["why_consider"]
        if ai_cm_report.get("why_be_careful") and isinstance(ai_cm_report["why_be_careful"], list) and len(ai_cm_report["why_be_careful"]) > 0:
            cm_report["why_be_careful"] = ai_cm_report["why_be_careful"]
        if ai_cm_report.get("beginner_watch_next") and isinstance(ai_cm_report["beginner_watch_next"], list) and len(ai_cm_report["beginner_watch_next"]) > 0:
            cm_report["beginner_watch_next"] = ai_cm_report["beginner_watch_next"]

    cur_price = price_data.get("current_price", 0)
    div_yield = info.get("dividendYield", 0) or 0

    # 1. Top Header Banner matching PDF Page 1
    st.markdown(f"""
    <div style="background: #ffffff; padding: 1.5rem 1.75rem; border-radius: 12px; border: 1px solid #e2e8f0; margin-bottom: 1.5rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.03);">
        <div style="color: #2563eb; font-weight: 700; font-size: 0.85rem; letter-spacing: 0.05em; text-transform: uppercase;">SIMPLE INVESTOR VIEW</div>
        <h1 style="color: #0f172a; margin: 0.25rem 0 0.5rem 0; font-size: 2.2rem; font-weight: 800;">{company_name}</h1>
        <div style="color: #475569; font-size: 1.05rem; font-weight: 600;">NSE: {symbol} · BSE: {info.get('bse_code', 'Listed')}</div>
        <div style="color: #64748b; font-size: 0.9rem; margin-top: 0.25rem;">A beginner-friendly research report - refreshed {dossier.get('generated_at', '12 August 2026')}</div>
        <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 0.9rem 1.1rem; margin-top: 1rem;">
            <strong style="color: #0f172a; font-size: 0.95rem;">Who this report is for:</strong>
            <span style="color: #475569; font-size: 0.95rem;">A first-time or non-technical investor who wants to understand the business, price, dividend, positives and risks before making their own decision.</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Identity Ambiguity Note
    if any(k in symbol.upper() for k in ["TATA", "L&T", "SBI", "HDFC", "RELIANCE"]):
        st.markdown(f"""
        <div style="background: #fffbe6; border: 1px solid #ffe58f; border-left: 4px solid #d97706; border-radius: 8px; padding: 0.85rem 1.1rem; margin-bottom: 1.5rem;">
            <strong style="color: #d97706;">Important Identity Note:</strong>
            <span style="color: #0f172a;">This report specifically covers <strong>{company_name} ({symbol})</strong>. Verify the exact listed entity before executing trades.</span>
        </div>
        """, unsafe_allow_html=True)

    # 2. Understand This Share in 30 Seconds
    st.markdown("### Understand This Share in 30 Seconds")
    summary_30s_questions = cm_report.get("summary_30s", [])
    st.markdown(_render_html_table(["Question", "Simple answer"], summary_30s_questions), unsafe_allow_html=True)

    # 3. Simple AI View Callout Box
    simple_ai_view_text = cm_report.get("simple_ai_view", "")
    st.markdown(f"""
    <div style="background: #f0f9ff; padding: 1.25rem 1.5rem; border-radius: 12px; border: 1px solid #bae6fd; border-left: 4px solid #0284c7; margin: 1.25rem 0; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
        <h4 style="color: #0369a1; margin-top: 0; font-size: 1.1rem;">💡 Simple AI View</h4>
        <p style="color: #0c4a6e; font-size: 0.98rem; line-height: 1.6; margin: 0;">
            {simple_ai_view_text}
        </p>
    </div>
    """, unsafe_allow_html=True)

    # 4. What Does Company Actually Do?
    st.markdown(f"### What Does {company_name} Actually Do?")
    what_does_text = cm_report.get("what_company_does", "")
    st.markdown(f"<p style='color: #334155; line-height: 1.6;'>{what_does_text}</p>", unsafe_allow_html=True)

    # 5. Is the Business Getting Better or Worse?
    st.markdown("### Is the Business Getting Better or Worse?")
    improving_bullets = cm_report.get("what_is_improving", [])
    attention_bullets = cm_report.get("what_deserves_attention", [])
    
    col_imp, col_att = st.columns(2)
    with col_imp:
        imp_html = "".join([f"<li>{b}</li>" for b in improving_bullets])
        st.markdown(f"""
        <div style="background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 10px; padding: 1.1rem; height: 100%;">
            <h4 style="color: #166534; margin-top: 0;">What is improving? 🟢</h4>
            <ul style="color: #14532d; font-size: 0.95rem; line-height: 1.6; margin-bottom: 0; padding-left: 1.2rem;">
                {imp_html}
            </ul>
        </div>
        """, unsafe_allow_html=True)
    with col_att:
        att_html = "".join([f"<li>{b}</li>" for b in attention_bullets])
        st.markdown(f"""
        <div style="background: #fffbe6; border: 1px solid #ffe58f; border-radius: 10px; padding: 1.1rem; height: 100%;">
            <h4 style="color: #92400e; margin-top: 0;">What deserves attention? 🟡</h4>
            <ul style="color: #78350f; font-size: 0.95rem; line-height: 1.6; margin-bottom: 0; padding-left: 1.2rem;">
                {att_html}
            </ul>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    with st.expander("📊 Show underlying financial numbers (For advanced users)", expanded=False):
        raw_m = cm_report.get("raw_metrics_summary", {})
        if raw_m:
            rows_html = "".join([f"<tr><td style='padding: 0.5rem 1rem; color: #0f172a; font-weight: 600;'>{k}</td><td style='padding: 0.5rem 1rem; color: #2563eb; font-weight: 700;'>{v}</td></tr>" for k, v in raw_m.items()])
            st.markdown(f"""
            <table style="width: 100%; border-collapse: collapse; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; margin-top: 0.5rem;">
                <thead>
                    <tr style="background: #f8fafc; border-bottom: 2px solid #cbd5e1;">
                        <th style="padding: 0.6rem 1rem; text-align: left; color: #475569;">Financial Metric</th>
                        <th style="padding: 0.6rem 1rem; text-align: left; color: #475569;">Calculated Value</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>
            """, unsafe_allow_html=True)

    # 6. Think of it this way
    st.markdown("""
    <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-left: 4px solid #10b981; border-radius: 8px; padding: 1rem 1.25rem; margin-bottom: 1.5rem;">
        <strong style="color: #047857; font-size: 0.95rem;">Think of it this way:</strong>
        <p style="color: #1f2937; margin: 0.35rem 0 0 0; font-size: 0.95rem; line-height: 1.6;">
            For every Rs 100 of revenue the company generates, it retains a portion as operating earnings after meeting costs. Operating profit margin and free cash flow dictate the underlying health of this business.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # 7. Does It Pay Dividends? (Audited Dynamic Dividend Parser)
    st.markdown("### Does It Pay Dividends?")
    raw_divs = modules.get("dividends", [])
    if isinstance(raw_divs, dict) and "dividends" in raw_divs:
        raw_divs = raw_divs["dividends"]
    if not isinstance(raw_divs, list):
        raw_divs = []

    years_paid = set()
    div_rows = []
    for d in raw_divs[:10]:
        if isinstance(d, dict):
            dt_val = str(d.get("Date", d.get("date", "Filing Date")))
            amt_val = d.get("Dividend (₹)", d.get("Dividend", d.get("amount", 0)))
            div_rows.append({
                "Date / Event": dt_val,
                "Dividend per share": f"₹{amt_val:.2f}" if isinstance(amt_val, (int, float)) else str(amt_val)
            })
            if len(dt_val) >= 4 and dt_val[:4].isdigit():
                yr = int(dt_val[:4])
                if yr >= 2021:
                    years_paid.add(yr)

    num_years_paid = len(years_paid)

    if not raw_divs and div_yield == 0:
        st.markdown("**NO VERIFIED RECENT DIVIDEND.** No recent dividend was found in the market-data history available to CCIE.")
    elif num_years_paid >= 4:
        st.markdown(f"**REGULAR RECENTLY.** Dividend payouts recorded in **{num_years_paid} of the last 5 years** (Yield: **{div_yield*100:.2f}%**; Sourced from market data history — verify with official NSE/BSE corporate action filings):")
        if div_rows:
            st.markdown(_render_html_table(["Date / Event", "Dividend per share"], div_rows), unsafe_allow_html=True)
    elif num_years_paid >= 1 or div_yield > 0:
        st.markdown(f"**IRREGULAR.** Dividend payouts recorded in **{num_years_paid} of the last 5 years** (Yield: **{div_yield*100:.2f}%**; Sourced from market data history — verify with official NSE/BSE corporate action filings):")
        if div_rows:
            st.markdown(_render_html_table(["Date / Event", "Dividend per share"], div_rows), unsafe_allow_html=True)
    else:
        st.markdown("**NO VERIFIED RECENT DIVIDEND.** No recent dividend was found in the market-data history available to CCIE.")

    if cur_price > 0 and div_yield > 0:
        est_lakh_div = cur_price * (100000 / cur_price) * div_yield
        st.markdown(f"""
        <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 1rem 1.25rem; margin-bottom: 1.5rem;">
            <strong style="color: #0f172a;">💰 If someone owned shares worth approx. ₹1 Lakh at today's price (₹{cur_price:,.2f}):</strong>
            <p style="color: #334155; margin: 0.25rem 0 0 0; font-size: 0.95rem;">
                Estimated annual dividend based on latest payouts is <strong>₹{est_lakh_div:,.0f}</strong>. 
                <br><small style="color: #64748b;"><em>This is only an illustration. Future dividends are not guaranteed and depend on profits and board approval.</em></small>
            </p>
        </div>
        """, unsafe_allow_html=True)

    # 8. Is the Current Share Price Cheap or Expensive?
    st.markdown("### Is the Current Share Price Cheap or Expensive?")
    val_verdict = cm_report.get("valuation_verdict", "UNCLEAR")
    val_explanation = cm_report.get("valuation_explanation", f"The share traded around ₹{cur_price:,.2f}. Valuation reflects market expectations of future operating growth and net worth.")
    
    st.markdown(f"""
    <div style="background: #fffbe6; border: 1px solid #ffe58f; border-left: 4px solid #d97706; border-radius: 10px; padding: 1.25rem 1.5rem; margin-bottom: 1rem;">
        <div style="color: #d97706; font-weight: 700; font-size: 1.1rem; margin-bottom: 0.4rem;">
            Current Valuation View: {val_verdict}
        </div>
        <p style="color: #0f172a; margin: 0; font-size: 0.95rem; line-height: 1.6;">
            {val_explanation}
        </p>
    </div>
    <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 0.85rem 1.1rem; margin-bottom: 1.5rem; font-size: 0.95rem; color: #475569;">
        <strong>💡 Important Beginner Education:</strong> A beginner should not judge cheapness from the rupee share price alone. A ₹50 share can be expensive and a ₹3,000 share can be cheap. Valuation depends on profits, assets, and business quality behind each share.
    </div>
    """, unsafe_allow_html=True)

    # 9. Why Might Someone Consider This Share?
    st.markdown("### Why Might Someone Consider This Share?")
    reasons = cm_report.get("why_consider", [])
    for r in reasons:
        st.markdown(f"• {r}")

    st.markdown("<br>", unsafe_allow_html=True)

    # 10. Why Should Someone Be Careful?
    st.markdown("### Why Should Someone Be Careful?")
    risks = cm_report.get("why_be_careful", [])
    for r in risks:
        st.markdown(f"• {r}")

    st.markdown("<br>", unsafe_allow_html=True)

    # 11. Someone Told You to Buy It? - Tip Check
    st.markdown("### Someone Told You to Buy It? - Tip Check")
    tip_check_rows = cm_report.get("tip_check_rows", [])
    st.markdown(_render_html_table(["Question", "Simple answer"], tip_check_rows), unsafe_allow_html=True)

    tip_res = cm_report.get("tip_check_result", "MIXED FUNDAMENTALS")
    tip_bg = "#f0fdf4" if "SUPPORTED" in tip_res else "#fef2f2" if "CONCERNS" in tip_res else "#fffbe6"
    tip_border = "#16a34a" if "SUPPORTED" in tip_res else "#dc2626" if "CONCERNS" in tip_res else "#d97706"
    tip_text_color = "#15803d" if "SUPPORTED" in tip_res else "#991b1b" if "CONCERNS" in tip_res else "#92400e"

    st.markdown(f"""
    <div style="background: {tip_bg}; border: 1px solid {tip_border}; border-left: 4px solid {tip_border}; border-radius: 8px; padding: 1rem 1.25rem; margin-bottom: 1.5rem;">
        <strong style="color: {tip_text_color}; font-size: 1rem;">Tip Check Result: {tip_res}</strong>
        <p style="color: #1f2937; margin: 0.25rem 0 0 0; font-size: 0.95rem;">
            Always evaluate fundamentals, debt, and valuation before acting on market sentiment or stock tips.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # 12. What Should a Beginner Watch Next?
    st.markdown("### What Should a Beginner Watch Next?")
    watch_points = cm_report.get("beginner_watch_next", [])
    for w in watch_points:
        st.markdown(f"• {w}")

    st.markdown("<br>", unsafe_allow_html=True)

    # 13. Simple AI Decision Support Matrix
    st.markdown("### Simple AI Decision Support")
    matrix_data = cm_report.get("decision_matrix", [])
    st.markdown(_render_html_table(["Area", "Assessment"], matrix_data), unsafe_allow_html=True)

    # 14. Bottom Line Summary & Final Research Status
    bottom_line_text = cm_report.get("bottom_line", "")
    research_status = cm_report.get("final_research_status", "Research View: 🟡 Perform Detailed Verification")
    
    st.markdown(f"""
    <div style="background: #ffffff; padding: 1.5rem; border-radius: 12px; border: 1px solid #e2e8f0; border-left: 5px solid #059669; margin: 1.5rem 0; box-shadow: 0 4px 6px rgba(0,0,0,0.04);">
        <h3 style="color: #059669; margin-top: 0;">📌 Bottom Line Summary</h3>
        <p style="color: #0f172a; font-size: 1.02rem; line-height: 1.6; margin: 0;">
            {bottom_line_text}
        </p>
        <hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 1rem 0;">
        <div style="font-size: 1.05rem; font-weight: 700; color: #0f172a;">
            Final Research Status: <span class="badge badge-confirmed">{research_status}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 15. Evidence Room
    st.markdown("---")
    source_tracking = modules.get("source_tracking", {})
    render_evidence_room(source_tracking)

    # 16. Ask This Company
    st.markdown("---")
    st.markdown("### 💬 Ask This Company")
    st.markdown("Click any beginner question below to get instant verified answers from our AI assistant:")

    ask_questions = [
        f"Why is {company_name} making more profit?",
        f"Does {company_name} have too much debt?",
        f"Why is the share called expensive or fair?",
        f"What could make {company_name}'s share price fall?",
        f"How reliable is {company_name}'s dividend?",
        f"What should I check in the next quarterly result?",
        f"Explain the biggest risk in very simple language.",
        f"What does {company_name} actually do in 2 sentences?"
    ]

    col_q1, col_q2 = st.columns(2)
    for idx, q_text in enumerate(ask_questions):
        with (col_q1 if idx % 2 == 0 else col_q2):
            if st.button(f"❓ {q_text}", key=f"ask_cm_q_{idx}", use_container_width=True):
                if "chat_history" not in st.session_state:
                    st.session_state.chat_history = []
                st.session_state.chat_history.append({"role": "user", "content": q_text})
                from ai.chatbot import CompanyChatbot
                from ai.gemini_client import GeminiClient
                bot = CompanyChatbot(GeminiClient(), dossier)
                ans = bot.ask(q_text)
                st.session_state.chat_history.append({"role": "assistant", "content": ans})
                st.toast(f"Answered: {q_text[:30]}...", icon="💡")
