import streamlit as st
from ui.components import render_section_header, render_fact_badge

def render_evidence_room(source_tracker_data: dict):
    """Render the Evidence Room section.
    Shows categorized source documents with confidence scores."""
    
    render_section_header("Evidence Room", "🔎", "Transparent sourcing for every claim made.")
    
    st.markdown("""
    <div style="background-color: rgba(17, 25, 40, 0.5); padding: 1rem; border-radius: 8px; border: 1px solid rgba(255,255,255,0.05); margin-bottom: 2rem;">
        <small class="text-muted">
            The Evidence Room tracks the provenance of every data point and qualitative claim. 
            Confidence scores reflect the reliability of the source (e.g., Audited Financials = 100%, News = 80%, AI Inference = Variable).
        </small>
    </div>
    """, unsafe_allow_html=True)
    
    if not source_tracker_data:
        st.info("No evidence data available for this dossier.")
        return
        
    categories = [
        "Financial Statements",
        "News & Announcements",
        "Company Disclosures",
        "Data Aggregator (yfinance)",
        "AI-Generated Analysis"
    ]
    
    for category in categories:
        items = source_tracker_data.get(category, [])
        if not items:
            continue
            
        with st.expander(f"📁 {category} ({len(items)} items)", expanded=False):
            for item in items:
                claim = item.get("claim", "N/A")
                source = item.get("source", "Unknown Source")
                date = item.get("date", "Unknown Date")
                confidence = item.get("confidence", 0)
                
                # Determine status badge text based on confidence
                status = "Confirmed" if confidence >= 90 else "Guidance" if confidence >= 70 else "Estimate"
                badge_html = render_fact_badge(status)
                
                st.markdown(f"""
                <div style="margin-bottom: 1rem; padding-bottom: 1rem; border-bottom: 1px solid rgba(255,255,255,0.05);">
                    <div style="margin-bottom: 0.5rem; color: #f8fafc; font-weight: 500;">
                        "{claim}"
                    </div>
                    <div style="font-size: 0.8rem; color: #94a3b8; display: flex; align-items: center; gap: 0.5rem;">
                        <span>📚 {source}</span>
                        <span>📅 {date}</span>
                        <span>🎯 {confidence}%</span>
                        {badge_html}
                    </div>
                </div>
                """, unsafe_allow_html=True)
