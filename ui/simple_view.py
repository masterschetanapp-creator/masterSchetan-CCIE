"""Presentation-only Simple View for the canonical CCIE decision support object."""

from html import escape
from typing import Any, Dict, List, Tuple

try:
    import streamlit as st
except ImportError:
    st = None

from analysis.metric_schema import UNKNOWN, is_unknown
from ui.components import render_callout, render_report_map, render_section_header
from ui.evidence_room import render_evidence_room


def _render_html_table(headers: List[str], rows: List[Dict[str, Any]]) -> str:
    if not rows:
        return "<p style='color: #64748b;'>UNKNOWN</p>"
    header_cells = "".join(f"<th style='padding: 0.85rem 1rem; background: #0f172a; color: #ffffff;'>{escape(str(header))}</th>" for header in headers)
    body_rows = []
    for row in rows:
        cells = "".join(f"<td style='padding: 0.85rem 1rem; color: #0f172a;'>{escape(str(row.get(header, UNKNOWN)))}</td>" for header in headers)
        body_rows.append(f"<tr style='border-bottom: 1px solid #e2e8f0;'>{cells}</tr>")
    return f"<div style='margin: 1rem 0; overflow-x: auto;'><table style='width: 100%; border-collapse: collapse; background: #ffffff; border: 1px solid #e2e8f0;'><thead><tr>{header_cells}</tr></thead><tbody>{''.join(body_rows)}</tbody></table></div>"


def _generate_dynamic_shareholding(
    info: dict,
    symbol: str,
    company_name: str,
    sector_name: str,
    promoter_holding: str = UNKNOWN,
    institutional_holding: str = UNKNOWN,
    ctso: dict = None,
) -> Tuple[List[Dict[str, str]], str]:
    """Use exchange taxonomy only; never convert Yahoo holder fields into promoter data."""
    rows = [
        {"Holder Category": "Promoter", "Holding %": UNKNOWN, "AI Observation": "Exchange shareholding filing required"},
        {"Holder Category": "Government (Non-Promoter)", "Holding %": UNKNOWN, "AI Observation": "Exchange shareholding filing required"},
        {"Holder Category": "FII", "Holding %": UNKNOWN, "AI Observation": "Exchange shareholding filing required"},
        {"Holder Category": "DII", "Holding %": UNKNOWN, "AI Observation": "Exchange shareholding filing required"},
        {"Holder Category": "Public", "Holding %": UNKNOWN, "AI Observation": "Exchange shareholding filing required"},
        {"Holder Category": "Promoter Pledge", "Holding %": UNKNOWN, "AI Observation": "Exchange pledge filing required"},
    ]
    return rows, "Shareholding taxonomy is UNKNOWN until a BSE/NSE quarterly filing is collected."


def _metric_value(decision: dict, name: str) -> str:
    item = decision.get("metric_snapshot", {}).get(name, {}) if isinstance(decision, dict) else {}
    return item.get("formatted_string", UNKNOWN) if isinstance(item, dict) else UNKNOWN


def render_simple_view(dossier: dict):
    """Render only the values and conclusions prepared by the orchestrator."""
    if dossier.get("render_blocked"):
        st.error("This report is blocked because its evidence or cross-view validation failed.")
        return

    modules = dossier.get("modules", {})
    decision = dossier.get("decision_support") or modules.get("decision_support")
    if not isinstance(decision, dict):
        st.error("Canonical decision support is unavailable. The report cannot be rendered reliably.")
        return

    profile = modules.get("company_snapshot", {})
    raw_data = modules.get("raw_data", {})
    info = raw_data.get("info", {}) if isinstance(raw_data, dict) else {}
    company_name = profile.get("name") or dossier.get("company_name") or "Company"
    symbol = str(profile.get("symbol") or dossier.get("symbol") or UNKNOWN).replace(".NS", "").replace(".BO", "")
    company_type = decision.get("company_type", UNKNOWN)
    sector_name = modules.get("sector_template", {}).get("name", UNKNOWN)
    badge = dossier.get("completeness", {}).get("badge_text", "0/26 research sections available. Evidence has not been checked.")

    render_report_map()
    st.markdown(
        f"<div style='background: #ffffff; padding: 1.5rem; border-radius: 12px; border: 1px solid #e2e8f0; margin-bottom: 1.5rem;'>"
        f"<div style='color: #2563eb; font-weight: 700; font-size: 0.85rem;'>SIMPLE INVESTOR VIEW</div>"
        f"<h1 style='color: #0f172a; margin: 0.25rem 0 0.5rem 0; font-size: 2.2rem;'>{escape(str(company_name))}</h1>"
        f"<div style='color: #475569; font-size: 1rem; font-weight: 600;'>NSE: {escape(symbol)} | Company type: {escape(str(company_type))}</div>"
        f"<div style='color: #475569; font-weight: 600; font-size: 0.95rem; margin-top: 0.35rem;'>{escape(str(badge))}</div>"
        f"<div style='color: #64748b; font-size: 0.9rem; margin-top: 0.25rem;'>Generated: {escape(str(dossier.get('generated_at', UNKNOWN)))}</div>"
        f"</div>",
        unsafe_allow_html=True,
    )

    render_section_header(f"1. Understand {company_name} in 30 Seconds", "", f"Decision support for {sector_name}")
    st.markdown(_render_html_table(["Question", "Simple answer"], decision.get("tip_check", {}).get("rows", [])), unsafe_allow_html=True)
    render_callout(decision.get("business_health", {}).get("explanation", UNKNOWN), label="CURRENT EVIDENCE", category="info")

    render_section_header("2. Strengths and Risks", "", "Evidence-backed observations")
    positives, risks = st.columns(2)
    with positives:
        st.markdown("**Evidence-backed positives**")
        for item in decision.get("positives", [UNKNOWN]):
            st.markdown(f"- {item}")
    with risks:
        st.markdown("**Risks and data gaps**")
        for item in decision.get("risks", [UNKNOWN]):
            st.markdown(f"- {item}")

    render_section_header("3. Valuation and Price Assessment", "", "No recommendation")
    valuation = decision.get("valuation", {})
    render_callout(f"{valuation.get('verdict_label', UNKNOWN)}: {valuation.get('explanation', UNKNOWN)}", label="VALUATION", category="info")

    render_section_header("4. Business Segmental Breakdown", "", "Primary filing evidence only")
    segments = raw_data.get("phase2_segments", []) if isinstance(raw_data, dict) else []
    if segments:
        st.markdown(_render_html_table(list(segments[0].keys()), segments), unsafe_allow_html=True)
    else:
        st.info("UNKNOWN: no primary segment disclosure has been collected.")

    render_section_header("5. Shareholding Pattern", "", "Exchange taxonomy")
    shareholding_rows, shareholding_note = _generate_dynamic_shareholding(info, symbol, company_name, sector_name)
    st.markdown(_render_html_table(["Holder Category", "Holding %", "AI Observation"], shareholding_rows), unsafe_allow_html=True)
    st.caption(shareholding_note)

    render_section_header("6-9. Financial Evidence", "", "Latest selected period and scope")
    period_context = decision.get("period_context", {})
    metric_rows = [
        {"Metric": "Latest reporting period", "Value": period_context.get("selected_reporting_period", UNKNOWN)},
        {"Metric": "Statement scope", "Value": period_context.get("statement_scope", UNKNOWN)},
        {"Metric": "Period end", "Value": period_context.get("period_end", UNKNOWN)},
        {"Metric": "Profitability return", "Value": _metric_value(decision, "roe")},
        {"Metric": "Debt to equity", "Value": _metric_value(decision, "debt_to_equity")},
        {"Metric": "Operating cash relative to profit", "Value": _metric_value(decision, "cash_flow")},
    ]
    st.markdown(_render_html_table(["Metric", "Value"], metric_rows), unsafe_allow_html=True)

    render_section_header("14. Tip Check", "", "Decision support, not investment advice")
    st.markdown(_render_html_table(["Question", "Simple answer"], decision.get("tip_check", {}).get("rows", [])), unsafe_allow_html=True)
    render_callout(decision.get("tip_check", {}).get("status", UNKNOWN), label="TIP CHECK", category="warning")

    render_section_header("15. What to Monitor", "", "Sector-specific evidence to collect next")
    for index, item in enumerate(decision.get("watch_next", []), 1):
        st.markdown(f"{index}. {item}")

    render_section_header("20. Dividend History", "", "Aggregated by financial year")
    dividend = decision.get("dividend", {})
    st.markdown(f"**Recorded frequency:** {dividend.get('formatted_label', UNKNOWN)}")
    st.caption(dividend.get("explanation", UNKNOWN))

    render_section_header("21. Sector-specific Operating Evidence", "", "Values extracted from supplied primary documents")
    sector_operating = modules.get("computed_metrics", {}).get("sector_operating", {})
    operating_rows = []
    if isinstance(sector_operating, dict):
        for metric_name, item in sector_operating.items():
            if not isinstance(item, dict):
                continue
            evidence = item.get("evidence", {}) if isinstance(item.get("evidence"), dict) else {}
            operating_rows.append({
                "Metric": str(metric_name).replace("_", " ").title(),
                "Value": item.get("formatted_string", UNKNOWN),
                "Period": evidence.get("period_end", UNKNOWN),
                "Scope": evidence.get("statement_scope", UNKNOWN),
                "Source": evidence.get("source_type", UNKNOWN),
            })
    if operating_rows:
        st.markdown(_render_html_table(["Metric", "Value", "Period", "Scope", "Source"], operating_rows), unsafe_allow_html=True)
    else:
        st.info("UNKNOWN: no sector operating metrics have been extracted from a primary document.")
    primary_evidence = modules.get("primary_evidence", {}) if isinstance(modules, dict) else {}
    collection = primary_evidence.get("collection", {}) if isinstance(primary_evidence, dict) else {}
    collection_mode = collection.get("mode", UNKNOWN) if isinstance(collection, dict) else UNKNOWN
    discovered_count = collection.get("discovered_count", UNKNOWN) if isinstance(collection, dict) else UNKNOWN
    downloaded_count = collection.get("downloaded_count", UNKNOWN) if isinstance(collection, dict) else UNKNOWN
    readable_text_count = collection.get("readable_text_count", UNKNOWN) if isinstance(collection, dict) else UNKNOWN
    st.caption(
        f"Filing collection: {collection_mode}. Documents discovered: {discovered_count}. Documents downloaded: {downloaded_count}. "
        f"Documents with readable text: {readable_text_count}."
    )

    render_section_header("24. Source Evidence", "", "No primary-source claim is made for secondary data")
    render_evidence_room(modules.get("source_tracking", {}))

    render_section_header("26. Research Status", "", "Evidence-gated summary")
    render_callout(decision.get("bottom_line", UNKNOWN), label=decision.get("research_status", UNKNOWN), category="warning")
