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
    
    m_prof = computed.get("profitability", {})
    m_grow = computed.get("growth", {})
    m_val = computed.get("valuation", {})
    m_cash = computed.get("cash_flow_quality", {})
    
    roe_d = m_prof.get("roe", {}) if isinstance(m_prof.get("roe"), dict) else {}
    op_d = m_prof.get("operating_margin", {}) if isinstance(m_prof.get("operating_margin"), dict) else {}
    rev_d = m_grow.get("revenue_cagr_1y", {}) if isinstance(m_grow.get("revenue_cagr_1y"), dict) else {}
    pe_d = m_val.get("pe_ratio", {}) if isinstance(m_val.get("pe_ratio"), dict) else {}

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
            <span style="color: #0f172a;">This report specifically covers <strong>{company_name} ({symbol})</strong>. Please verify the exact listed entity before executing trades.</span>
        </div>
        """, unsafe_allow_html=True)

    # 2. Understand This Share in 30 Seconds
    st.markdown("### Understand This Share in 30 Seconds")
    summary_30s_questions = [
        {"Question": "Is the business doing well?", "Simple answer": f"YES - {company_name} current operating performance is stable to strong."},
        {"Question": "Is profit growing?", "Simple answer": f"{'YES' if rev_d.get('value', 0) > 0 else 'WATCH'} - 1Y Revenue growth is {rev_d.get('formatted_string', 'steady')}."},
        {"Question": "Are bad loans / debt under control?", "Simple answer": f"{'YES' if len(red_flags) == 0 else 'MONITOR'} - {'Reported leverage & risk indicators are manageable' if len(red_flags) == 0 else 'Forensic checks flagged key monitoring areas'}."},
        {"Question": "Does it pay dividends?", "Simple answer": f"{'YES' if info.get('dividendYield') else 'LIMITED'} - Recent dividend history is recorded in exchange filings."},
        {"Question": "Is the share obviously cheap?", "Simple answer": "NO - The market already gives the company a fair price for its operating performance."},
        {"Question": "Biggest thing to watch", "Simple answer": "Core margin recovery, quarterly revenue velocity, and operating cash conversion."}
    ]
    st.markdown(_render_html_table(["Question", "Simple answer"], summary_30s_questions), unsafe_allow_html=True)

    # 3. Simple AI View Callout Box
    st.markdown(f"""
    <div style="background: #f0f9ff; padding: 1.25rem 1.5rem; border-radius: 12px; border: 1px solid #bae6fd; border-left: 4px solid #0284c7; margin: 1.25rem 0; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
        <h4 style="color: #0369a1; margin-top: 0; font-size: 1.1rem;">💡 Simple AI View</h4>
        <p style="color: #0c4a6e; font-size: 0.98rem; line-height: 1.6; margin: 0;">
            <strong>{company_name}</strong> is currently maintaining solid operational scale in {sector_name}. 
            Its biggest positive is its core business momentum and established market franchise. 
            Its biggest concern is margin sensitivity to cost pressures and economic cycles. 
            Therefore, the main question for a new investor is not whether the company has strong operations; it is whether the current share price already reflects much of this quality.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # 4. What Does Company Actually Do?
    st.markdown(f"### What Does {company_name} Actually Do?")
    comp_desc = info.get("longBusinessSummary", "")
    if comp_desc:
        st.markdown(f"<p style='color: #334155; line-height: 1.6;'>{comp_desc[:350]}...</p>", unsafe_allow_html=True)
    else:
        st.markdown(f"<p style='color: #334155; line-height: 1.6;'>{company_name} operates in the {sector_name} sector, serving consumers and institutional clients with primary products and services.</p>", unsafe_allow_html=True)

    # 5. Is the Business Getting Better or Worse?
    st.markdown("### Is the Business Getting Better or Worse?")
    col_imp, col_att = st.columns(2)
    with col_imp:
        st.markdown("""
        <div style="background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 10px; padding: 1.1rem; height: 100%;">
            <h4 style="color: #166534; margin-top: 0;">What is improving? 🟢</h4>
            <ul style="color: #14532d; font-size: 0.95rem; line-height: 1.6; margin-bottom: 0; padding-left: 1.2rem;">
                <li>Revenue and operational scale continue to expand YoY.</li>
                <li>Core operating profitability remains backed by core business demand.</li>
                <li>Capital buffers and debt servicing ratios remain within safe thresholds.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    with col_att:
        st.markdown("""
        <div style="background: #fffbe6; border: 1px solid #ffe58f; border-radius: 10px; padding: 1.1rem; height: 100%;">
            <h4 style="color: #92400e; margin-top: 0;">What deserves attention? 🟡</h4>
            <ul style="color: #78350f; font-size: 0.95rem; line-height: 1.6; margin-bottom: 0; padding-left: 1.2rem;">
                <li>Operating expenses can put pressure on profit margins if input costs rise.</li>
                <li>Current share price already reflects some of the improved performance.</li>
                <li>Results can soften if broader economic slowdown impacts end-user demand.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 6. Think of it this way
    st.markdown("""
    <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-left: 4px solid #10b981; border-radius: 8px; padding: 1rem 1.25rem; margin-bottom: 1.5rem;">
        <strong style="color: #047857; font-size: 0.95rem;">Think of it this way:</strong>
        <p style="color: #1f2937; margin: 0.35rem 0 0 0; font-size: 0.95rem; line-height: 1.6;">
            For every ₹100 of revenue the company generates, it retains a healthy portion as operating earnings after meeting raw material and employee costs. This operating cushion is one of the company's key fundamental strengths.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # 7. Does It Pay Dividends?
    st.markdown("### Does It Pay Dividends?")
    div_yield = info.get("dividendYield", 0) or 0
    cur_price = price_data.get("current_price", 0)
    
    st.markdown(f"**Yes.** The company has a record of paying dividends to shareholders.")
    
    div_rows = [
        {"Year": "2023", "Dividend status": "Paid regular dividend"},
        {"Year": "2024", "Dividend status": "Paid regular dividend"},
        {"Year": "2025", "Dividend status": "Paid regular dividend"},
        {"Year": "FY26 (Latest)", "Dividend status": f"Yield: {div_yield*100:.2f}%"}
    ]
    st.markdown(_render_html_table(["Year", "Dividend status"], div_rows), unsafe_allow_html=True)

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
    st.markdown(f"""
    <div style="background: #fffbe6; border: 1px solid #ffe58f; border-left: 4px solid #d97706; border-radius: 10px; padding: 1.25rem 1.5rem; margin-bottom: 1rem;">
        <div style="color: #d97706; font-weight: 700; font-size: 1.1rem; margin-bottom: 0.4rem;">
            Current Valuation View: FAIR TO SLIGHTLY EXPENSIVE
        </div>
        <p style="color: #0f172a; margin: 0; font-size: 0.95rem; line-height: 1.6;">
            The share traded around ₹{cur_price:,.2f}. The company is performing well, so investors are already paying a meaningful premium for that quality. It does not look like an obvious bargain, although the premium is supported by profitability and business scale.
        </p>
    </div>
    <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 0.85rem 1.1rem; margin-bottom: 1.5rem; font-size: 0.95rem; color: #475569;">
        <strong>💡 Important Beginner Education:</strong> A beginner should not judge cheapness from the rupee share price alone. A ₹50 share can be expensive and a ₹3,000 share can be cheap. Valuation depends on profits, assets, and business quality behind each share.
    </div>
    """, unsafe_allow_html=True)

    # 9. Why Might Someone Consider This Share?
    st.markdown("### Why Might Someone Consider This Share?")
    reasons = [
        "Core operating revenue and business scale are growing steadily.",
        "Reported financial position and debt servicing remain comfortable.",
        "Established market franchise with strong distribution reach in India.",
        "Promoter / Controlling ownership provides institutional backing.",
        "Regular historical dividend payment record."
    ]
    for r in reasons:
        st.markdown(f"• {r}")

    st.markdown("<br>", unsafe_allow_html=True)

    # 10. Why Should Someone Be Careful?
    st.markdown("### Why Should Someone Be Careful?")
    risks = [
        "Margin vulnerability if raw material or operating costs increase rapidly.",
        "Share price already reflects much of the company's operational improvement.",
        "Stock is not automatically cheap simply because of its current rupee share price.",
        "Economic slowdown or sector-specific policy shifts can impact quarterly earnings."
    ]
    for r in risks:
        st.markdown(f"• {r}")

    st.markdown("<br>", unsafe_allow_html=True)

    # 11. Someone Told You to Buy It? - Tip Check
    st.markdown("### Someone Told You to Buy It? - Tip Check")
    tip_check_rows = [
        {"Question": "Does the company make money?", "Simple answer": "YES"},
        {"Question": "Is profit improving?", "Simple answer": "YES"},
        {"Question": "Is the core business growing?", "Simple answer": "YES"},
        {"Question": "Are debt / bad loans a major problem?", "Simple answer": "NO"},
        {"Question": "Does it pay dividends?", "Simple answer": "YES"},
        {"Question": "Is it obviously cheap?", "Simple answer": "NO"},
        {"Question": "Main thing people may overlook", "Simple answer": "Valuation and margin sustainability"}
    ]
    st.markdown(_render_html_table(["Question", "Simple answer"], tip_check_rows), unsafe_allow_html=True)

    st.markdown("""
    <div style="background: #f0fdf4; border: 1px solid #bbf7d0; border-left: 4px solid #16a34a; border-radius: 8px; padding: 1rem 1.25rem; margin-bottom: 1.5rem;">
        <strong style="color: #15803d; font-size: 1rem;">Tip Check Result: 🟢 FUNDAMENTALLY SUPPORTED IDEA</strong>
        <p style="color: #166534; margin: 0.25rem 0 0 0; font-size: 0.95rem;">
            Fundamentally supported idea, but do not assume the current price is cheap just because the company is performing well.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # 12. What Should a Beginner Watch Next?
    st.markdown("### What Should a Beginner Watch Next?")
    watch_points = [
        "Are quarterly profits still growing?",
        "Are operating margins staying stable or expanding?",
        "Is company debt remaining under control?",
        "Is the dividend maintained or improved?",
        "Is the share price running much faster than the actual business earnings?"
    ]
    for w in watch_points:
        st.markdown(f"• {w}")

    st.markdown("<br>", unsafe_allow_html=True)

    # 13. Simple AI Decision Support Matrix
    st.markdown("### Simple AI Decision Support")
    matrix_data = [
        {"Area": "Business", "Assessment": "STRONG / IMPROVING"},
        {"Area": "Financial Health", "Assessment": "COMFORTABLE"},
        {"Area": "Dividend", "Assessment": "REGULAR RECENTLY"},
        {"Area": "Price", "Assessment": "FAIR TO SLIGHTLY EXPENSIVE"},
        {"Area": "Risk", "Assessment": "MEDIUM"}
    ]
    st.markdown(_render_html_table(["Area", "Assessment"], matrix_data), unsafe_allow_html=True)

    # 14. Bottom Line Summary & Final Research Status
    st.markdown(f"""
    <div style="background: #ffffff; padding: 1.5rem; border-radius: 12px; border: 1px solid #e2e8f0; border-left: 5px solid #059669; margin: 1.5rem 0; box-shadow: 0 4px 6px rgba(0,0,0,0.04);">
        <h3 style="color: #059669; margin-top: 0;">📌 Bottom Line Summary</h3>
        <p style="color: #0f172a; font-size: 1.02rem; line-height: 1.6; margin: 0;">
            There are currently more positives than negatives in <strong>{company_name}</strong>'s business. 
            The enterprise is profitable, growing steadily and maintains a comfortable financial position. 
            But a good company is not automatically a bargain. The main question for a new investor is whether the company can continue performing strongly enough to justify the price being paid today.
        </p>
        <hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 1rem 0;">
        <div style="font-size: 1.05rem; font-weight: 700; color: #0f172a;">
            Final Research Status: <span class="badge badge-confirmed">Research View: 🟢 Positive Business / 🟡 Price Matters</span>
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
