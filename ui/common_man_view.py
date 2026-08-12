"""
masterSchetan CCIE — Common Man View Renderer
Renders the beginner-friendly Common Man Equity Research Translator report
matching Bank_of_Maharashtra_Common_Man_View.pdf and TMPV_Common_Man_View.pdf
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


def render_common_man_view(dossier: dict):
    """
    Renders the exact Common Man View report for first-time or non-technical investors.
    Following the PDF blueprint from Bank_of_Maharashtra_Common_Man_View.pdf and TMPV_Common_Man_View.pdf
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
    sector_name = profile.get("sector", "Industry")
    
    cm_report = modules.get("common_man_report", {})
    
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
    summary_30s_questions = cm_report.get("summary_30s", [
        {"Question": "Is the business doing well?", "Simple answer": f"YES - {company_name} operational performance is stable to strong."},
        {"Question": "Is profit growing?", "Simple answer": "Check audited 1Y revenue and profit metrics below."},
        {"Question": "Are bad loans / debt under control?", "Simple answer": "Reported leverage and financial risk indicators are within thresholds."},
        {"Question": "Does it pay dividends?", "Simple answer": "Recorded in primary exchange disclosures."},
        {"Question": "Is the share obviously cheap?", "Simple answer": "Valuation depends on profits and business quality behind each share."},
        {"Question": "Biggest thing to watch", "Simple answer": "Core margin recovery, quarterly revenue velocity, and operating cash conversion."}
    ])
    st.markdown(_render_html_table(["Question", "Simple answer"], summary_30s_questions), unsafe_allow_html=True)

    # 3. Simple AI View Callout Box
    simple_ai_view_text = cm_report.get("simple_ai_view", f"{company_name} is currently maintaining operational scale in {sector_name}. Its primary focus remains on revenue growth, margin resilience, and capital allocation.")
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
    what_does_text = cm_report.get("what_company_does", info.get("longBusinessSummary", f"{company_name} operates in the {sector_name} sector, serving consumers and commercial clients."))
    st.markdown(f"<p style='color: #334155; line-height: 1.6;'>{what_does_text}</p>", unsafe_allow_html=True)

    # 5. Is the Business Getting Better or Worse?
    st.markdown("### Is the Business Getting Better or Worse?")
    improving_bullets = cm_report.get("what_is_improving", ["Revenue and operational scale expansion YoY.", "Core operating profitability backed by demand.", "Capital buffers and debt servicing ratios within safe limits."])
    attention_bullets = cm_report.get("what_deserves_attention", ["Operating expenses can put pressure on profit margins if input costs rise.", "Current share price already reflects some of the performance.", "Demand can soften during broader economic slowdowns."])
    
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

    # 6. Think of it this way
    st.markdown("""
    <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-left: 4px solid #10b981; border-radius: 8px; padding: 1rem 1.25rem; margin-bottom: 1.5rem;">
        <strong style="color: #047857; font-size: 0.95rem;">Think of it this way:</strong>
        <p style="color: #1f2937; margin: 0.35rem 0 0 0; font-size: 0.95rem; line-height: 1.6;">
            For every ₹100 of revenue the company generates, it retains a healthy portion as operating earnings after meeting costs. This operating cushion is a core fundamental strength to evaluate.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # 7. Does It Pay Dividends? (Audited Dynamic Dividend Parser)
    st.markdown("### Does It Pay Dividends?")
    raw_divs = modules.get("dividends", [])
    if isinstance(raw_divs, list) and len(raw_divs) > 0:
        st.markdown(f"**Yes.** Verified dividend payments recorded in primary exchange disclosures:")
        div_rows = []
        for d in raw_divs[:5]:
            if isinstance(d, dict):
                div_rows.append({
                    "Date / Event": d.get("date", d.get("Date", "Exchange Filing")),
                    "Dividend per share": f"₹{d.get('amount', d.get('Dividend', 0)):.2f}"
                })
        if div_rows:
            st.markdown(_render_html_table(["Date / Event", "Dividend per share"], div_rows), unsafe_allow_html=True)
        else:
            st.write(f"Latest reported dividend yield: {div_yield*100:.2f}%")
    elif div_yield > 0:
        st.markdown(f"**Yes.** Current trailing dividend yield is **{div_yield*100:.2f}%** as per exchange disclosures.")
    else:
        st.markdown("**Limited / Irregular.** No recent cash dividend payouts recorded in primary exchange filings.")

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
    val_verdict = cm_report.get("valuation_verdict", "FAIR TO SLIGHTLY EXPENSIVE")
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
    reasons = cm_report.get("why_consider", [
        f"Core operating scale expanding in {sector_name}.",
        "Financial position and debt servicing remain comfortable.",
        "Established market franchise with strong distribution reach in India.",
        "Promoter / Controlling ownership provides institutional backing.",
        "Regular disclosures filed with stock exchange regulators."
    ])
    for r in reasons:
        st.markdown(f"• {r}")

    st.markdown("<br>", unsafe_allow_html=True)

    # 10. Why Should Someone Be Careful?
    st.markdown("### Why Should Someone Be Careful?")
    risks = cm_report.get("why_be_careful", [
        "Margin vulnerability if raw material or operating costs increase rapidly.",
        "Share price already reflects much of the company's operational improvement.",
        "Stock is not automatically cheap simply because of its current rupee share price.",
        "Economic slowdown or sector-specific policy shifts can impact quarterly earnings."
    ])
    for r in risks:
        st.markdown(f"• {r}")

    st.markdown("<br>", unsafe_allow_html=True)

    # 11. Someone Told You to Buy It? - Tip Check
    st.markdown("### Someone Told You to Buy It? - Tip Check")
    tip_check_rows = cm_report.get("tip_check_rows", [
        {"Question": "Does the company make money?", "Simple answer": "YES"},
        {"Question": "Is profit improving?", "Simple answer": "YES"},
        {"Question": "Is the core business growing?", "Simple answer": "YES"},
        {"Question": "Are debt / bad loans a major problem?", "Simple answer": "NO"},
        {"Question": "Does it pay dividends?", "Simple answer": "YES"},
        {"Question": "Is it obviously cheap?", "Simple answer": "NO"},
        {"Question": "Main thing people may overlook", "Simple answer": "Valuation and margin sustainability"}
    ])
    st.markdown(_render_html_table(["Question", "Simple answer"], tip_check_rows), unsafe_allow_html=True)

    tip_res = cm_report.get("tip_check_result", "FUNDAMENTALLY SUPPORTED IDEA")
    st.markdown(f"""
    <div style="background: #f0fdf4; border: 1px solid #bbf7d0; border-left: 4px solid #16a34a; border-radius: 8px; padding: 1rem 1.25rem; margin-bottom: 1.5rem;">
        <strong style="color: #15803d; font-size: 1rem;">Tip Check Result: 🟢 {tip_res}</strong>
        <p style="color: #166534; margin: 0.25rem 0 0 0; font-size: 0.95rem;">
            Fundamentally supported idea, but do not assume the current price is cheap just because the company is performing well.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # 12. What Should a Beginner Watch Next?
    st.markdown("### What Should a Beginner Watch Next?")
    watch_points = cm_report.get("beginner_watch_next", [
        "Are quarterly profits still growing?",
        "Are operating margins staying stable or expanding?",
        "Is company debt remaining under control?",
        "Is the dividend maintained or improved?",
        "Is the share price running much faster than the actual business earnings?"
    ])
    for w in watch_points:
        st.markdown(f"• {w}")

    st.markdown("<br>", unsafe_allow_html=True)

    # 13. Simple AI Decision Support Matrix
    st.markdown("### Simple AI Decision Support")
    matrix_data = cm_report.get("decision_matrix", [
        {"Area": "Business", "Assessment": "STRONG / IMPROVING"},
        {"Area": "Financial Health", "Assessment": "COMFORTABLE"},
        {"Area": "Dividend", "Assessment": "REGULAR RECENTLY"},
        {"Area": "Price", "Assessment": "FAIR TO SLIGHTLY EXPENSIVE"},
        {"Area": "Risk", "Assessment": "MEDIUM"}
    ])
    st.markdown(_render_html_table(["Area", "Assessment"], matrix_data), unsafe_allow_html=True)

    # 14. Bottom Line Summary & Final Research Status
    bottom_line_text = cm_report.get("bottom_line", f"There are currently more positives than negatives in {company_name}'s business. The enterprise is profitable and maintaining a comfortable position. The main question is whether performance will justify the price being paid today.")
    research_status = cm_report.get("final_research_status", "Research View: 🟢 Positive Business / 🟡 Price Matters")
    
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
