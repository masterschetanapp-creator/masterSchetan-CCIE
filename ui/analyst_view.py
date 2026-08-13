"""
masterSchetan CCIE — Analyst View Renderer
Designed for experienced investors and financial analysts.
Provides complete financial statement tables, ratio grids, and sector metrics.
"""

import streamlit as st
import pandas as pd
from ui.components import render_section_header, render_metric_grid
from ui.charts import create_revenue_profit_chart, create_debt_equity_chart, create_cashflow_chart


def render_analyst_view(dossier: dict):
    """Render the complete Analyst View with full financial tables and ratios."""
    modules = dossier.get("modules", {})
    computed = modules.get("computed_metrics", {})
    raw_data = modules.get("raw_data", {})
    financials = raw_data.get("financials", {})

    # ── 1. Key Ratios & Metrics Dashboard ─────────────────────
    render_section_header("Key Ratios & Metrics Dashboard", "🧮", "Complete quantitative ratios")

    for cat_name, cat_label in [
        ("profitability", "Profitability & Returns"),
        ("growth", "Growth & Velocity"),
        ("debt_metrics", "Debt & Solvency"),
        ("valuation", "Valuation Multiples"),
        ("cash_flow_quality", "Cash Flow & Capital Conversion")
    ]:
        cat_dict = computed.get(cat_name, {})
        if isinstance(cat_dict, dict) and cat_dict:
            st.markdown(f"#### {cat_label}")
            cards = []
            for k, item in cat_dict.items():
                if isinstance(item, dict) and item.get("formatted_string"):
                    cards.append({
                        "label": k.replace("_", " ").title(),
                        "value": item.get("formatted_string"),
                        "status": item.get("status", "neutral"),
                        "explanation": item.get("explanation", "")
                    })
            if cards:
                render_metric_grid(cards, columns=min(len(cards), 4))
                st.markdown("<br>", unsafe_allow_html=True)

    # ── 2. Financial Statements (Tables) ──────────────────────
    render_section_header("Financial Statements", "📑", "Financial statement data — secondary aggregation; verify against company filings")
    tab1, tab2, tab3 = st.tabs(["Profit & Loss Statement", "Balance Sheet", "Cash Flow Statement"])

    with tab1:
        pl_table = financials.get("display_income_statement", {})
        if pl_table.get("data"):
            df = pd.DataFrame(pl_table["data"])
            st.dataframe(df, use_container_width=True, height=400)
        else:
            st.info("Profit & Loss statement data not available for this ticker.")

    with tab2:
        bs_table = financials.get("display_balance_sheet", {})
        if bs_table.get("data"):
            df = pd.DataFrame(bs_table["data"])
            st.dataframe(df, use_container_width=True, height=400)
        else:
            st.info("Balance Sheet statement data not available for this ticker.")

    with tab3:
        cf_table = financials.get("display_cash_flow", {})
        if cf_table.get("data"):
            df = pd.DataFrame(cf_table["data"])
            st.dataframe(df, use_container_width=True, height=400)
        else:
            st.info("Cash Flow statement data not available for this ticker.")

    # ── 3. Sector Specific Focus ──────────────────────────────
    sector_template = modules.get("sector_template", {})
    if sector_template and isinstance(sector_template, dict):
        render_section_header(f"Sector Focus: {sector_template.get('name', 'Industry')}", "🏭", "Specialized metrics")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Key Industry Metrics Tracked:**")
            for m in sector_template.get("metrics", []):
                st.markdown(f"- 🔹 `{m}`")
        with col2:
            st.markdown("**Key Analyst Questions for this Sector:**")
            for q in sector_template.get("key_questions", []):
                st.markdown(f"- ❓ {q}")

        operating_metrics = computed.get("sector_operating", {}) if isinstance(computed, dict) else {}
        operating_rows = []
        if isinstance(operating_metrics, dict):
            for metric_name, item in operating_metrics.items():
                if not isinstance(item, dict):
                    continue
                evidence = item.get("evidence", {}) if isinstance(item.get("evidence"), dict) else {}
                operating_rows.append({
                    "Metric": str(metric_name).replace("_", " ").title(),
                    "Value": item.get("formatted_string", "UNKNOWN"),
                    "Period End": evidence.get("period_end", "UNKNOWN"),
                    "Scope": evidence.get("statement_scope", "UNKNOWN"),
                    "Source": evidence.get("source_type", "UNKNOWN"),
                    "Page": evidence.get("page", "UNKNOWN"),
                })
        if operating_rows:
            st.markdown("#### Extracted Sector Operating Evidence")
            st.dataframe(pd.DataFrame(operating_rows), use_container_width=True, hide_index=True)
        else:
            st.info("No primary-document sector operating metrics have been collected.")

    # ── 4. Detailed Red Flags & Forensic Audit ────────────────
    red_flags = modules.get("red_flags", [])
    render_section_header("Forensic Red Flags Audit", "🚩", "Automated quantitative checks")
    if not red_flags:
        st.info("No quantitative red flags were generated from the available data. This is not a clean bill of health; missing evidence remains UNKNOWN.")
    elif red_flags:
        for rf in red_flags:
            sev = rf.get("severity", "warning")
            color = "#f87171" if sev == "danger" else "#fbbf24"
            st.markdown(f"""
            <div style="border-left: 4px solid {color}; background: rgba(17, 25, 40, 0.75); padding: 1rem; border-radius: 8px; margin-bottom: 0.75rem;">
                <strong style="color: #f8fafc;">⚠️ {rf.get('title')}</strong>
                <p style="color: {color}; margin: 0.25rem 0;">{rf.get('finding')}</p>
                <p style="color: #94a3b8; font-size: 0.85rem; margin: 0;">{rf.get('explanation')}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.success("✅ All quantitative forensic red-flag checks passed with zero alerts.")
