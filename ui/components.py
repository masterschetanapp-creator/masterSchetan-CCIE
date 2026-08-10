"""
masterSchetan CCIE — UI Components
Matches exact components from PNB_Complete_AI_Equity_Research_Report.pdf
"""

import streamlit as st

def render_stock_header(profile: dict, price_data: dict):
    """Render PDF Report Header Banner (Page 1 style)."""
    company_name = profile.get("name", "Unknown Company")
    symbol = profile.get("symbol", "").replace(".NS", "").replace(".BO", "")
    sector = profile.get("sector", "Public Sector Bank")
    industry = profile.get("industry", "Financial Services")
    market_cap = profile.get("market_cap_formatted", "N/A")
    price = price_data.get("current_price", 0.0)
    change = price_data.get("change_percent", 0.0)
    
    color_style = "color: #059669;" if change >= 0 else "color: #dc2626;"
    sign = "+" if change >= 0 else ""

    html = f"""
    <div class="pdf-report-header">
        <div class="pdf-header-top">
            <span>AI EQUITY RESEARCH REPORT · {symbol}</span>
            <span>Research/education only — Not investment advice</span>
        </div>
        <div class="pdf-header-title">{company_name}</div>
        <div class="pdf-header-subtitle">Complete AI Equity Research Report</div>
        <div style="margin: 0.5rem 0 1rem 0; font-size: 1.5rem; font-weight: 700; color: #0f172a;">
            Current Price: ₹{price:,.2f} <span style="{color_style} font-size: 1.1rem; margin-left: 0.5rem;">({sign}{change:.2f}%)</span>
        </div>
        <div class="pdf-header-meta">
            <span><strong>NSE:</strong> {symbol}</span>
            <span>·</span>
            <span><strong>Industry:</strong> {sector} ({industry})</span>
            <span>·</span>
            <span><strong>Market Cap:</strong> {market_cap}</span>
            <span>·</span>
            <span><strong>Confidence:</strong> <span class="badge badge-confirmed">High</span></span>
            <span>·</span>
            <span><strong>Mode:</strong> Simple + Analyst</span>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_report_map():
    """Render 10-point Report Map (Table of Contents from Page 2)."""
    html = """
    <div class="report-callout callout-warning" style="margin-bottom: 2rem;">
        <span class="callout-label" style="color: #fbbf24;">📍 Report Map & Navigation</span>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 0.5rem; margin-top: 0.5rem; font-size: 0.9rem;">
            <div>1. Identity & 30-Second Summary</div>
            <div>2. Research Snapshot & Business Model</div>
            <div>3. History & Ownership</div>
            <div>4. Earnings Quality & Asset Quality</div>
            <div>5. Future Growth & Management Plans</div>
            <div>6. Monitoring Points & Governance</div>
            <div>7. Dividend & Distribution Reach</div>
            <div>8. Developments & Upcoming Events</div>
            <div>9. Catalysts, Risks & Conclusion</div>
            <div>10. Evidence Room & Source Register</div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_callout(text: str, label: str = "APP PHILOSOPHY", category: str = "info"):
    """Render callout box (Page 2/3/4 callout style)."""
    cat_class = f"callout-{category}" if category in ["warning", "danger", "success"] else ""
    label_color = "#60a5fa" if category == "info" else "#fbbf24" if category == "warning" else "#f87171" if category == "danger" else "#34d399"

    html = f"""
    <div class="report-callout {cat_class}">
        <span class="callout-label" style="color: {label_color};">{label}</span>
        {text}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_metric_card(label: str, value: str, status: str, explanation: str = None, icon: str = None):
    """Single metric card with traffic-light border."""
    status_class = f"metric-card-{status}"
    icon_html = f"<span style='margin-right: 6px;'>{icon}</span>" if icon else ""
    desc_html = f'<div class="metric-desc">{explanation}</div>' if explanation else ''

    html = f"""
    <div class="metric-card {status_class}">
        <div class="metric-title">{icon_html}{label}</div>
        <div class="metric-value">{value}</div>
        {desc_html}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_metric_grid(metrics: list[dict], columns: int = 3):
    """Grid of metric cards using st.columns."""
    cols = st.columns(columns)
    for i, metric in enumerate(metrics):
        with cols[i % columns]:
            render_metric_card(
                label=metric.get("label", ""),
                value=metric.get("value", ""),
                status=metric.get("status", "neutral"),
                explanation=metric.get("explanation", ""),
                icon=metric.get("icon", "")
            )


def render_section_header(title: str, icon: str, description: str = None):
    """Section header matching PDF report headings."""
    desc_html = f'<p style="color: #94a3b8; margin-top: -0.25rem; margin-bottom: 1rem; font-size: 0.9rem;">{description}</p>' if description else ''
    html = f"""
    <div style="margin-top: 2rem; margin-bottom: 0.75rem;">
        <h2 style="display: flex; align-items: center; gap: 0.5rem; color: #f8fafc; margin: 0;">
            <span>{icon}</span> {title}
        </h2>
        {desc_html}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_fact_badge(status: str) -> str:
    """Returns HTML badge for fact status: Confirmed, Guidance, Estimate, Danger."""
    status_lower = str(status).lower()
    badge_class = "badge-confirmed" if "confirm" in status_lower else "badge-guidance" if "guidance" in status_lower or "plan" in status_lower else "badge-estimate" if "estimate" in status_lower else "badge-danger"
    return f'<span class="badge {badge_class}">{status}</span>'


def render_investor_questions(questions: list[str]):
    """'Questions an Investor Should Answer' section."""
    st.markdown("""
    <div class="report-callout" style="border-left-color: #60a5fa;">
        <span class="callout-label" style="color: #60a5fa;">❓ 5 Decision Questions for Investors</span>
    """, unsafe_allow_html=True)
    for i, q in enumerate(questions, 1):
        st.markdown(f"**{i}.** {q}")
    st.markdown('</div>', unsafe_allow_html=True)


def render_view_toggle() -> str:
    """Simple View / Analyst View toggle with crisp white background."""
    st.markdown("""
    <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 0.75rem 1.25rem; margin: 1.25rem 0; box-shadow: 0 2px 4px rgba(0,0,0,0.03);">
    """, unsafe_allow_html=True)
    view = st.radio(
        "Select Research Perspective:",
        ["Simple View (Common Man)", "Analyst View (Detailed Ratios & Financials)"],
        horizontal=True,
        key="view_mode_radio"
    )
    st.markdown("</div>", unsafe_allow_html=True)
    return "Simple" if "Simple" in view else "Analyst"


def render_disclaimer():
    """Research Disclaimer matching Page 13 of PDF."""
    st.markdown("---")
    st.markdown("""
    <div style="font-size: 0.8rem; color: #64748b; text-align: center; padding: 1.5rem 0; line-height: 1.5;">
        <strong>Research Disclaimer:</strong> This application is a product of AI-generated equity research simulation. 
        It is provided for research and educational purposes only and is not investment advice, a research recommendation, 
        or a personalized Buy/Sell/Hold call. Financial figures and event dates can change; users should verify primary 
        exchange disclosures before making financial decisions.
    </div>
    """, unsafe_allow_html=True)
