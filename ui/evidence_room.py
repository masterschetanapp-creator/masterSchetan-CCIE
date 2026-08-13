"""Transparent source and provenance display."""

from html import escape

try:
    import streamlit as st
except ImportError:
    st = None

from ui.components import render_section_header


def render_evidence_room(source_tracker_data: dict):
    """Show source claims exactly as tracked, without inflating verification coverage."""
    render_section_header("Evidence Room and Source Audit Trail", "", "Provenance for quantitative figures and narrative interpretation")
    if not isinstance(source_tracker_data, dict):
        st.info("UNKNOWN: no source tracking is available.")
        return

    claims = source_tracker_data.get("claims", [])
    summary = source_tracker_data.get("summary", {})
    if not isinstance(claims, list) or not claims:
        st.info("UNKNOWN: no source claims were recorded.")
        return

    primary = summary.get("primary_coverage_pct", 0)
    secondary = summary.get("secondary_coverage_pct", 0)
    unverified = summary.get("unverified_pct", 0)
    average = summary.get("average_confidence", 0)
    st.markdown(
        f"<div style='background: #ffffff; padding: 1.25rem 1.5rem; border-radius: 12px; border: 1px solid #e2e8f0; border-left: 4px solid #2563eb; margin-bottom: 1rem;'>"
        f"<strong>Source status:</strong> {escape(str(summary.get('status', 'UNVERIFIED')))}<br>"
        f"<span style='color: #475569;'>Primary filing coverage: {primary}% | Secondary coverage: {secondary}% | Unverified: {unverified}% | Claim confidence average: {average}%</span></div>",
        unsafe_allow_html=True,
    )
    st.caption("A high calculation-confidence score does not turn secondary market data into primary filing evidence.")

    grouped = {"Primary evidence": [], "Secondary market data": [], "Derived calculations": [], "AI or unverified material": []}
    for claim in claims:
        status = str(claim.get("verification_status", "UNVERIFIED"))
        claim_type = str(claim.get("claim_type", "FACT"))
        if status in {"PRIMARY_VERIFIED", "DERIVED_FROM_PRIMARY", "PRIMARY_DOCUMENT_EXTRACTED"}:
            grouped["Primary evidence"].append(claim)
        elif status in {"SECONDARY_ONLY", "DERIVED_FROM_SECONDARY", "SINGLE_SECONDARY"}:
            target = "Derived calculations" if claim_type == "CALCULATION" else "Secondary market data"
            grouped[target].append(claim)
        else:
            grouped["AI or unverified material"].append(claim)

    for title, entries in grouped.items():
        if not entries:
            continue
        with st.expander(f"{title} ({len(entries)} items)", expanded=title == "Secondary market data"):
            for claim in entries:
                claim_text = escape(str(claim.get("claim_text", "UNKNOWN")))
                source = escape(str(claim.get("source", "UNKNOWN")))
                details = escape(str(claim.get("source_type", "UNKNOWN")))
                verification = escape(str(claim.get("verification_status", "UNVERIFIED")).replace("_", " "))
                checked = escape(str(claim.get("last_checked", "UNKNOWN"))[:10])
                source_url = escape(str(claim.get("source_url") or "UNKNOWN"))
                document_id = escape(str(claim.get("source_document_id") or "UNKNOWN"))
                page = escape(str(claim.get("page") if claim.get("page") is not None else "UNKNOWN"))
                snippet = escape(str(claim.get("evidence_snippet") or "UNKNOWN"))
                st.markdown(
                    f"<div style='background: #ffffff; padding: 0.9rem 1.1rem; border-radius: 8px; border: 1px solid #e2e8f0; margin-bottom: 0.75rem;'>"
                    f"<strong style='color: #0f172a;'>{claim_text}</strong><div style='font-size: 0.82rem; color: #475569; margin-top: 0.35rem;'>"
                    f"Source: {source} | Details: {details} | Status: {verification} | Checked: {checked}<br>"
                    f"Document: {document_id} | Page: {page}<br>"
                    f"URL: {source_url}<br>Evidence: {snippet}</div></div>",
                    unsafe_allow_html=True,
                )
