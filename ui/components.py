"""Shared Streamlit presentation components."""

from html import escape

try:
    import streamlit as st
except ImportError:
    st = None


def render_stock_header(profile: dict, price_data: dict, source_summary: dict = None):
    """Render the dossier header without inventing a price or confidence level."""
    company_name = profile.get("name", "Unknown Company")
    symbol = str(profile.get("symbol", "UNKNOWN")).replace(".NS", "").replace(".BO", "")
    sector = profile.get("sector", "UNKNOWN")
    industry = profile.get("industry", "UNKNOWN")
    market_cap = profile.get("market_cap_formatted", "UNKNOWN")
    price = price_data.get("current_price") if isinstance(price_data, dict) else None
    change = price_data.get("change_percent") if isinstance(price_data, dict) else None
    price_display = f"INR {price:,.2f}" if isinstance(price, (int, float)) else "UNKNOWN"
    change_display = f"{change:+.2f}%" if isinstance(change, (int, float)) else "UNKNOWN"
    change_color = "#059669" if isinstance(change, (int, float)) and change >= 0 else "#dc2626"
    evidence_status = (source_summary or {}).get("status", "UNVERIFIED")
    st.markdown(
        f"<div class='pdf-report-header'><div class='pdf-header-top'><span>AI EQUITY RESEARCH REPORT | {escape(symbol)}</span>"
        f"<span>Research and education only. Not investment advice.</span></div>"
        f"<div class='pdf-header-title'>{escape(str(company_name))}</div><div class='pdf-header-subtitle'>Evidence-gated equity research</div>"
        f"<div style='margin: 0.5rem 0 1rem 0; font-size: 1.5rem; font-weight: 700; color: #0f172a;'>Current Price: {price_display} "
        f"<span style='color: {change_color}; font-size: 1.1rem; margin-left: 0.5rem;'>({change_display})</span></div>"
        f"<div class='pdf-header-meta'><span><strong>NSE:</strong> {escape(symbol)}</span><span>|</span>"
        f"<span><strong>Industry:</strong> {escape(str(sector))} ({escape(str(industry))})</span><span>|</span>"
        f"<span><strong>Market Cap:</strong> {escape(str(market_cap))}</span><span>|</span>"
        f"<span><strong>Evidence:</strong> <span class='badge badge-guidance'>{escape(str(evidence_status))}</span></span></div></div>",
        unsafe_allow_html=True,
    )


def render_report_map():
    st.markdown("""
    <div class="report-callout callout-warning" style="margin-bottom: 2rem;">
        <span class="callout-label" style="color: #d97706;">REPORT MAP</span>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 0.5rem; margin-top: 0.5rem; font-size: 0.9rem;">
            <div>1. 30-second summary</div><div>2. Risks and evidence gaps</div><div>3. Valuation context</div>
            <div>4. Financial evidence</div><div>5. Sector-specific checks</div><div>6. Sources and provenance</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_callout(text: str, label: str = "RESEARCH NOTE", category: str = "info"):
    css_class = f"callout-{category}" if category in {"warning", "danger", "success"} else ""
    label_color = "#60a5fa" if category == "info" else "#fbbf24" if category == "warning" else "#f87171" if category == "danger" else "#34d399"
    st.markdown(f"<div class='report-callout {css_class}'><span class='callout-label' style='color: {label_color};'>{escape(str(label))}</span>{escape(str(text))}</div>", unsafe_allow_html=True)


def render_metric_card(label: str, value: str, status: str, explanation: str = None, icon: str = None):
    icon_html = f"<span style='margin-right: 6px;'>{escape(str(icon))}</span>" if icon else ""
    description = f"<div class='metric-desc'>{escape(str(explanation))}</div>" if explanation else ""
    st.markdown(f"<div class='metric-card metric-card-{escape(str(status))}'><div class='metric-title'>{icon_html}{escape(str(label))}</div><div class='metric-value'>{escape(str(value))}</div>{description}</div>", unsafe_allow_html=True)


def render_metric_grid(metrics: list[dict], columns: int = 3):
    columns = max(1, columns)
    rendered_columns = st.columns(columns)
    for index, metric in enumerate(metrics):
        with rendered_columns[index % columns]:
            render_metric_card(metric.get("label", ""), metric.get("value", "UNKNOWN"), metric.get("status", "neutral"), metric.get("explanation", ""), metric.get("icon", ""))


def render_section_header(title: str, icon: str, description: str = None):
    description_html = f"<p style='color: #94a3b8; margin-top: 0; margin-bottom: 1rem; font-size: 0.9rem;'>{escape(str(description))}</p>" if description else ""
    st.markdown(f"<div style='margin-top: 2rem; margin-bottom: 0.75rem;'><h2 style='display: flex; align-items: center; gap: 0.5rem; color: #f8fafc; margin: 0;'><span>{escape(str(icon))}</span>{escape(str(title))}</h2>{description_html}</div>", unsafe_allow_html=True)


def render_fact_badge(status: str) -> str:
    status_lower = str(status).lower()
    css_class = "badge-confirmed" if "confirm" in status_lower else "badge-guidance" if "guidance" in status_lower else "badge-estimate" if "estimate" in status_lower else "badge-danger"
    return f"<span class='badge {css_class}'>{escape(str(status))}</span>"


def render_investor_questions(questions: list[str]):
    st.markdown("<div class='report-callout' style='border-left-color: #60a5fa;'><span class='callout-label' style='color: #60a5fa;'>DECISION QUESTIONS</span></div>", unsafe_allow_html=True)
    for index, question in enumerate(questions, 1):
        st.markdown(f"{index}. {question}")


def render_view_toggle() -> str:
    view = st.radio("Select research perspective:", ["Common Man View", "Simple View", "Analyst View"], horizontal=True, key="view_mode_radio")
    return "CommonMan" if "Common" in view else "Simple" if "Simple" in view else "Analyst"


def render_disclaimer():
    st.markdown("---")
    st.markdown("""
    <div style="font-size: 0.8rem; color: #64748b; text-align: center; padding: 1.5rem 0; line-height: 1.5;">
        <strong>Research disclaimer:</strong> This application provides educational decision support, not investment advice or a recommendation. Market data may be secondary-sourced; verify company and exchange filings before making financial decisions.
    </div>
    """, unsafe_allow_html=True)
