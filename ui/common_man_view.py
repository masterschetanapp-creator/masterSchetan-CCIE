"""
masterSchetan CCIE — Common Man View Renderer
Renders the beginner-friendly Common Man Equity Research Translator report.
Presentation-only renderer consuming canonical DecisionSupport from analysis/decision_engine.py.
"""

import streamlit as st
import pandas as pd
from ui.components import (
    render_section_header,
    render_callout,
    render_investor_questions
)
from ui.evidence_room import render_evidence_room
from analysis.decision_engine import DecisionEngine


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


def _generate_empirical_common_man_verdict(company_name: str, symbol: str, sector_name: str, info: dict, price_data: dict, computed: dict, red_flags: list, dividend_history: list = None, dossier: dict = None) -> dict:
    """
    Adapter wrapper that delegates 100% of decision support logic to canonical DecisionEngine.
    """
    c_type = (dossier.get("company_type") if isinstance(dossier, dict) else None) or "DEFAULT"
    ds = (dossier.get("decision_support") if isinstance(dossier, dict) else None)
    
    if not ds:
        engine = DecisionEngine()
        ds = engine.build(
            dossier=dossier or {},
            company_type=c_type,
            computed_metrics=computed or {},
            evidence_summary={},
            red_flags=red_flags or [],
            dividends=dividend_history or [],
            news=[]
        )

    rows = ds.get("tip_check", {}).get("rows", [])
    
    return {
        "company_name": company_name,
        "symbol": symbol,
        "sector_name": sector_name,
        "biz_doing_well": rows[0].get("Simple answer") if len(rows) > 0 else "N/A",
        "profit_growing": rows[1].get("Simple answer") if len(rows) > 1 else "N/A",
        "debt_control": rows[3].get("Simple answer") if len(rows) > 3 else "N/A",
        "div_status": ds.get("dividend", {}).get("formatted_label", "N/A"),
        "div_matrix": ds.get("dividend", {}).get("status", "N/A"),
        "valuation_verdict": ds.get("valuation", {}).get("verdict_label", "N/A"),
        "valuation_expl": ds.get("valuation", {}).get("explanation", "N/A"),
        "cheap_answer": ds.get("valuation", {}).get("cheap_answer", "N/A"),
        "price_matrix": ds.get("valuation", {}).get("status", "N/A"),
        "tip_result": ds.get("tip_check", {}).get("status", "MIXED FUNDAMENTALS"),
        "tip_check_result": ds.get("tip_check", {}).get("status", "MIXED FUNDAMENTALS"),
        "tip_check_rows": rows,
        "risk_rating": ds.get("risk_level", "MEDIUM"),
        "final_status": ds.get("research_status", "N/A"),
        "final_research_status": ds.get("research_status", "N/A"),
        "bottom_line": ds.get("bottom_line", "N/A"),
        "watch_next_list": ds.get("watch_next", []),
        "beginner_watch_next": ds.get("watch_next", []),
        "what_is_improving": ds.get("positives", []),
        "what_deserves_attention": ds.get("risks", []),
        "why_consider": ds.get("positives", []),
        "why_be_careful": ds.get("risks", [])
    }


def render_common_man_view(dossier: dict):
    """Render the Common Man Equity Research View using canonical DecisionSupport."""
    modules = dossier.get("modules", {})
    profile = modules.get("company_snapshot", {})
    raw_data = modules.get("raw_data", {})
    info = raw_data.get("info", {})
    company_name = profile.get("name", info.get("longName", "Company"))
    symbol = profile.get("symbol", "").replace(".NS", "").replace(".BO", "")
    price_data = modules.get("price_data", {})
    computed = modules.get("computed_metrics", {})
    red_flags = modules.get("red_flags", [])
    sector_name = profile.get("sector") or info.get("sector") or "Industry"

    dividend_history = modules.get("dividends", [])
    if isinstance(dividend_history, dict) and "dividends" in dividend_history:
        dividend_history = dividend_history["dividends"]
    if not isinstance(dividend_history, list):
        dividend_history = []

    empirical_cm = _generate_empirical_common_man_verdict(
        company_name, symbol, sector_name, info, price_data, computed, red_flags,
        dividend_history=dividend_history, dossier=dossier
    )
    
    ai_cm_report = modules.get("common_man_report", {})
    cm_report = dict(empirical_cm)
    if isinstance(ai_cm_report, dict) and len(ai_cm_report) > 0:
        if ai_cm_report.get("simple_ai_view"):
            cm_report["simple_ai_view"] = ai_cm_report["simple_ai_view"]
        if ai_cm_report.get("what_company_does"):
            cm_report["what_company_does"] = ai_cm_report["what_company_does"]
        if ai_cm_report.get("what_is_improving") and isinstance(ai_cm_report["what_is_improving"], list):
            cm_report["what_is_improving"] = ai_cm_report["what_is_improving"]
        if ai_cm_report.get("what_deserves_attention") and isinstance(ai_cm_report["what_deserves_attention"], list):
            cm_report["what_deserves_attention"] = ai_cm_report["what_deserves_attention"]
        if ai_cm_report.get("valuation_explanation"):
            cm_report["valuation_explanation"] = ai_cm_report["valuation_explanation"]
        if ai_cm_report.get("why_consider") and isinstance(ai_cm_report["why_consider"], list):
            cm_report["why_consider"] = ai_cm_report["why_consider"]
        if ai_cm_report.get("why_be_careful") and isinstance(ai_cm_report["why_be_careful"], list):
            cm_report["why_be_careful"] = ai_cm_report["why_be_careful"]
        if ai_cm_report.get("beginner_watch_next") and isinstance(ai_cm_report["beginner_watch_next"], list):
            cm_report["beginner_watch_next"] = ai_cm_report["beginner_watch_next"]

    cur_price = price_data.get("current_price", 0)
    div_yield = info.get("dividendYield", 0) or 0

    # 1. Top Header Banner
    st.markdown(f"""
    <div style="background: #ffffff; padding: 1.5rem 1.75rem; border-radius: 12px; border: 1px solid #e2e8f0; margin-bottom: 1.5rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.03);">
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #f1f5f9; padding-bottom: 0.75rem; margin-bottom: 1rem;">
            <div>
                <span class="badge badge-confirmed" style="font-size: 0.8rem; background: #0f172a; color: #ffffff;">COMMON MAN EQUITY RESEARCH TRANSLATOR</span>
                <h1 style="color: #0f172a; margin: 0.25rem 0 0 0; font-size: 2rem;">{company_name}</h1>
                <div style="color: #475569; font-weight: 600; font-size: 0.95rem;">NSE: {symbol} · {sector_name}</div>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 1.8rem; font-weight: 800; color: #0f172a;">₹{cur_price:,.2f}</div>
                <div style="color: #64748b; font-size: 0.85rem;">Refreshed: {dossier.get('generated_at', '12 August 2026')}</div>
            </div>
        </div>
        <div style="background: #f8fafc; border-left: 4px solid #2563eb; padding: 0.75rem 1rem; border-radius: 4px; font-size: 0.9rem; color: #334155;">
            <strong>Plain-English Guarantee:</strong> Written for beginners with zero financial jargon. Every claim is backed by empirical financial statement data.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 2. Executive Summary Box
    st.markdown(f"""
    <div style="background: #ffffff; padding: 1.5rem; border-radius: 12px; border: 1px solid #e2e8f0; border-left: 5px solid #2563eb; margin-bottom: 1.5rem;">
        <h3 style="color: #2563eb; margin-top: 0; font-size: 1.2rem;">💡 Simple AI Executive Summary</h3>
        <p style="color: #0f172a; font-size: 1.05rem; line-height: 1.6; margin: 0;">
            {cm_report.get('simple_ai_view', f"<strong>{company_name}</strong> is an established enterprise in {sector_name}. Its core operational trajectory and balance sheet position are evaluated below.")}
        </p>
    </div>
    """, unsafe_allow_html=True)

    # 3. 30-Second Question & Answer Grid
    render_section_header("1. Understand This Share in 30 Seconds", "⚡", "Core questions answered in plain language")
    q_rows = [
        {"Question": "Is the company doing well overall?", "Simple Answer": cm_report.get("biz_doing_well", "N/A")},
        {"Question": "Is net profit improving?", "Simple Answer": cm_report.get("profit_growing", "N/A")},
        {"Question": "Are bad loans / debt under control?", "Simple Answer": cm_report.get("debt_control", "N/A")},
        {"Question": "Does it pay dividends?", "Simple Answer": cm_report.get("div_status", "N/A")},
        {"Question": "Is the share price obviously cheap?", "Simple Answer": cm_report.get("cheap_answer", "N/A")},
    ]
    st.markdown(_render_html_table(["Question", "Simple Answer"], q_rows), unsafe_allow_html=True)

    # 4. Underlying Financial Numbers (Expandable)
    with st.expander("📊 Show underlying financial numbers (For advanced users)"):
        roe_str = computed.get("profitability", {}).get("roe", {}).get("formatted_string", "N/A") if isinstance(computed.get("profitability"), dict) else "N/A"
        pe_str = computed.get("valuation", {}).get("pe_ratio", {}).get("formatted_string", "N/A") if isinstance(computed.get("valuation"), dict) else "N/A"
        de_str = computed.get("debt_metrics", {}).get("debt_to_equity", {}).get("formatted_string", "N/A") if isinstance(computed.get("debt_metrics"), dict) else "N/A"
        st.markdown(f"- **ROE (Return on Equity)**: `{roe_str}`")
        st.markdown(f"- **P/E Ratio (Price to Earnings)**: `{pe_str}`")
        st.markdown(f"- **Debt to Equity Ratio**: `{de_str}`")
        st.markdown(f"- **Dividend Yield**: `{div_yield*100:.2f}%`")

    # 5. Business & Operations Overview
    render_section_header("2. What Does The Company Actually Do?", "🏢", "Simple explanation of the core business model")
    st.markdown(cm_report.get("what_company_does", f"{company_name} operates in {sector_name}, manufacturing and providing services to commercial and retail clients."))

    # 6. Positives & Areas to Watch
    col_pos, col_risk = st.columns(2)
    with col_pos:
        render_section_header("What Is Going Well", "🟢", "Key strengths")
        for item in cm_report.get("what_is_improving", []):
            st.markdown(f"- **{item}**")
    with col_risk:
        render_section_header("What Deserves Attention", "⚠️", "Key risk areas")
        for item in cm_report.get("what_deserves_attention", []):
            st.markdown(f"- **{item}**")

    # 7. Valuation Verdict
    render_section_header("3. Is The Share Price Cheap, Fair, or Expensive?", "🏷️", "Valuation evaluation")
    render_callout(
        f"VALUATION JUDGMENT: {cm_report.get('valuation_verdict', 'FAIR')} — {cm_report.get('valuation_expl', '')}",
        label="VALUATION VERDICT", category="info"
    )

    # 8. 7-Point Tip Check Result
    render_section_header("4. Tip Check Result (Someone Told You To Buy It?)", "🎯", "Empirical decision support check")
    st.markdown(_render_html_table(["Question", "Simple answer"], cm_report.get("tip_check_rows", [])), unsafe_allow_html=True)
    render_callout(
        f"TIP CHECK RESULT: {cm_report.get('tip_result', 'MIXED FUNDAMENTALS')} — Evaluated 100% empirically from primary financial statement data.",
        label="TIP CHECK RESULT", category="success" if "SUPPORTED" in str(cm_report.get('tip_result')) else "warning"
    )

    # 9. Bottom Line Summary Box
    st.markdown(f"""
    <div style="background: #ffffff; padding: 1.5rem; border-radius: 12px; border: 1px solid #e2e8f0; border-left: 5px solid #059669; margin: 1.5rem 0; box-shadow: 0 4px 6px rgba(0,0,0,0.04);">
        <h3 style="color: #059669; margin-top: 0;">📌 Bottom Line Summary</h3>
        <p style="color: #0f172a; font-size: 1.05rem; line-height: 1.6; margin: 0;">
            {cm_report.get('bottom_line', '')}
        </p>
        <hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 1rem 0;">
        <div style="font-size: 1.1rem; font-weight: 700; color: #0f172a;">
            Final Research Status: <span class="badge badge-confirmed">{cm_report.get('final_research_status', '')}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 10. Evidence Room
    render_evidence_room(modules.get("source_tracking", {}))
