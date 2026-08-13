"""Plain-English, presentation-only view of canonical decision support."""

from html import escape
from typing import Any, Dict, List

import streamlit as st

from analysis.metric_schema import UNKNOWN
from ui.components import render_callout, render_section_header
from ui.evidence_room import render_evidence_room


def _render_html_table(headers: List[str], rows: List[Dict[str, Any]]) -> str:
    if not rows:
        return "<p style='color: #64748b;'>UNKNOWN</p>"
    head = "".join(f"<th style='padding: 0.85rem 1rem; background: #0f172a; color: #ffffff;'>{escape(str(header))}</th>" for header in headers)
    body = "".join(
        "<tr style='border-bottom: 1px solid #e2e8f0;'>" + "".join(
            f"<td style='padding: 0.85rem 1rem; color: #0f172a;'>{escape(str(row.get(header, UNKNOWN)))}</td>" for header in headers
        ) + "</tr>"
        for row in rows
    )
    return f"<div style='margin: 1rem 0; overflow-x: auto;'><table style='width: 100%; border-collapse: collapse; background: #ffffff; border: 1px solid #e2e8f0;'><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>"


def _metric(decision: dict, name: str) -> str:
    item = decision.get("metric_snapshot", {}).get(name, {}) if isinstance(decision, dict) else {}
    return item.get("formatted_string", UNKNOWN) if isinstance(item, dict) else UNKNOWN


def render_common_man_view(dossier: dict):
    """Render plain language from the orchestrator's decision object without re-deciding."""
    if dossier.get("render_blocked"):
        st.error("This report is blocked because its evidence or cross-view validation failed.")
        return

    modules = dossier.get("modules", {})
    decision = dossier.get("decision_support") or modules.get("decision_support")
    if not isinstance(decision, dict):
        st.error("Plain-English report is unavailable because canonical decision support is missing.")
        return

    profile = modules.get("company_snapshot", {})
    price_data = modules.get("price_data", {})
    company_name = profile.get("name") or dossier.get("company_name") or "Company"
    symbol = str(profile.get("symbol") or dossier.get("symbol") or UNKNOWN).replace(".NS", "").replace(".BO", "")
    price = price_data.get("current_price") if isinstance(price_data, dict) else None
    price_display = f"INR {price:,.2f}" if isinstance(price, (int, float)) else UNKNOWN

    st.markdown(
        f"<div style='background: #ffffff; padding: 1.5rem 1.75rem; border-radius: 12px; border: 1px solid #e2e8f0; margin-bottom: 1.5rem;'>"
        f"<div style='color: #0f172a; font-weight: 700; font-size: 0.8rem;'>PLAIN-ENGLISH RESEARCH VIEW</div>"
        f"<h1 style='color: #0f172a; margin: 0.25rem 0 0; font-size: 2rem;'>{escape(str(company_name))}</h1>"
        f"<div style='color: #475569; font-weight: 600; font-size: 0.95rem;'>NSE: {escape(symbol)} | Current price: {escape(price_display)}</div>"
        f"<div style='background: #f8fafc; border-left: 4px solid #2563eb; padding: 0.75rem 1rem; margin-top: 1rem; color: #334155;'>"
        f"This view translates the same evidence shown in the source audit. Primary filing facts are counted only when a document is recorded.</div></div>",
        unsafe_allow_html=True,
    )

    render_section_header("1. Understand This Share in 30 Seconds", "", "Plain-language answers")
    st.markdown(_render_html_table(["Question", "Simple answer"], decision.get("tip_check", {}).get("rows", [])), unsafe_allow_html=True)

    render_section_header("2. What the Available Evidence Says", "", "No recommendation")
    render_callout(decision.get("bottom_line", UNKNOWN), label=decision.get("research_status", UNKNOWN), category="info")

    good, attention = st.columns(2)
    with good:
        st.markdown("**What is going well in the available data**")
        for item in decision.get("positives", [UNKNOWN]):
            st.markdown(f"- {item}")
    with attention:
        st.markdown("**What deserves attention**")
        for item in decision.get("risks", [UNKNOWN]):
            st.markdown(f"- {item}")

    render_section_header("3. Is the Price Easy to Judge?", "", "Valuation is not a recommendation")
    valuation = decision.get("valuation", {})
    render_callout(f"{valuation.get('verdict_label', UNKNOWN)}: {valuation.get('explanation', UNKNOWN)}", label="PRICE CHECK", category="warning")

    render_section_header("4. Numbers Behind the Plain English", "", "For readers who want the technical details")
    with st.expander("Show underlying figures"):
        st.markdown(_render_html_table(["Measure", "Value"], [
            {"Measure": "Return on shareholder money", "Value": _metric(decision, "roe")},
            {"Measure": "Debt compared with shareholder money", "Value": _metric(decision, "debt_to_equity")},
            {"Measure": "Price compared with recent earnings", "Value": _metric(decision, "pe_ratio")},
            {"Measure": "Recorded dividend frequency", "Value": decision.get("dividend", {}).get("formatted_label", UNKNOWN)},
        ]), unsafe_allow_html=True)

    render_section_header("5. What to Check Next", "", "Evidence to collect in the next result or filing")
    for index, item in enumerate(decision.get("watch_next", []), 1):
        st.markdown(f"{index}. {item}")

    render_section_header("6. Source Evidence", "", "Provenance and confidence")
    render_evidence_room(modules.get("source_tracking", {}))
