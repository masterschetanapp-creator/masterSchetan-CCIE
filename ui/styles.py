"""
masterSchetan CCIE — Premium Report Styling & CSS
Matches the exact theme and visual design of PNB_Complete_AI_Equity_Research_Report.pdf
"""

import streamlit as st

CUSTOM_CSS = """
/* Streamlit Base Overrides */
[data-testid="stAppViewContainer"] {
    background-color: #0b0f19;
    color: #f1f5f9;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}

[data-testid="stHeader"] {
    background-color: transparent;
}

/* Hide Streamlit default chrome */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Headings */
h1, h2, h3, h4, h5, h6 {
    color: #f8fafc !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em;
}

h1 { font-size: 2.2rem !important; }
h2 { font-size: 1.6rem !important; border-bottom: 2px solid #3b82f6; padding-bottom: 0.4rem; margin-top: 1.8rem !important; }
h3 { font-size: 1.3rem !important; color: #60a5fa !important; }
h4 { font-size: 1.1rem !important; }

/* Report Header Banner */
.pdf-report-header {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    padding: 1.75rem 2rem;
    margin-bottom: 2rem;
    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
}

.pdf-header-top {
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #60a5fa;
    margin-bottom: 0.5rem;
    display: flex;
    justify-content: space-between;
}

.pdf-header-title {
    font-size: 2.4rem;
    font-weight: 800;
    color: #ffffff;
    margin: 0.25rem 0;
}

.pdf-header-subtitle {
    font-size: 1.1rem;
    color: #94a3b8;
    margin-bottom: 1rem;
}

.pdf-header-meta {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
    font-size: 0.85rem;
    color: #cbd5e1;
    border-top: 1px solid rgba(255,255,255,0.1);
    padding-top: 0.75rem;
}

/* Callout Boxes (PDF Report Style) */
.report-callout {
    background: rgba(30, 41, 59, 0.75);
    border-left: 4px solid #3b82f6;
    border-radius: 8px;
    padding: 1.25rem 1.5rem;
    margin: 1.25rem 0;
    font-size: 1rem;
    line-height: 1.65;
    color: #f1f5f9;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.callout-warning { border-left-color: #f59e0b; background: rgba(245, 158, 11, 0.08); }
.callout-danger { border-left-color: #ef4444; background: rgba(239, 68, 68, 0.08); }
.callout-success { border-left-color: #10b981; background: rgba(16, 185, 129, 0.08); }

.callout-label {
    font-size: 0.75rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 0.5rem;
    display: block;
}

/* Tables (Exact Report Formatting) */
table {
    width: 100%;
    border-collapse: collapse;
    margin: 1rem 0;
    border-radius: 8px;
    overflow: hidden;
    background: rgba(15, 23, 42, 0.6);
}

th {
    background-color: #1e293b;
    color: #f8fafc;
    font-weight: 700;
    text-align: left;
    padding: 0.85rem 1rem;
    border-bottom: 2px solid #3b82f6;
    font-size: 0.9rem;
}

td {
    padding: 0.85rem 1rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    color: #e2e8f0;
    font-size: 0.95rem;
}

tr:nth-child(even) td {
    background-color: rgba(255, 255, 255, 0.02);
}

tr:hover td {
    background-color: rgba(59, 130, 246, 0.08);
}

/* Badges */
.badge {
    display: inline-flex;
    align-items: center;
    padding: 0.2rem 0.6rem;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.badge-confirmed { background-color: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); }
.badge-guidance { background-color: rgba(59, 130, 246, 0.15); color: #60a5fa; border: 1px solid rgba(59, 130, 246, 0.3); }
.badge-estimate { background-color: rgba(245, 158, 11, 0.15); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.3); }
.badge-danger { background-color: rgba(239, 68, 68, 0.15); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.3); }

/* Metric Grid Cards */
.metric-card {
    background: rgba(15, 23, 42, 0.75);
    border-radius: 10px;
    padding: 1.2rem;
    border-top: 1px solid rgba(255, 255, 255, 0.08);
    border-right: 1px solid rgba(255, 255, 255, 0.08);
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    border-left: 4px solid #3b82f6;
    margin-bottom: 1rem;
}

.metric-card-green { border-left-color: #10b981; }
.metric-card-amber { border-left-color: #f59e0b; }
.metric-card-red { border-left-color: #ef4444; }

.metric-title { font-size: 0.8rem; color: #94a3b8; text-transform: uppercase; font-weight: 700; }
.metric-value { font-size: 1.6rem; font-weight: 800; color: #ffffff; margin: 0.3rem 0; }
.metric-desc { font-size: 0.85rem; color: #cbd5e1; line-height: 1.4; }

/* Print & PDF Export rules */
@media print {
    [data-testid="stAppViewContainer"] { background-color: #ffffff !important; color: #000000 !important; }
    .pdf-report-header { background: #0f172a !important; color: #ffffff !important; }
    th { background-color: #1e293b !important; color: #ffffff !important; }
    td { color: #000000 !important; }
}
"""

def inject_custom_css():
    """Inject custom report styling into Streamlit app."""
    st.markdown(f'<style>{CUSTOM_CSS}</style>', unsafe_allow_html=True)
