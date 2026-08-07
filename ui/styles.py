"""
masterSchetan CCIE — Premium Report Styling & CSS
Corporate Light Theme (High Readability, Crisp Light Background, Professional PDF Styling).
"""

import streamlit as st

CUSTOM_CSS = """
/* Streamlit Base Overrides (Light Corporate Theme) */
[data-testid="stAppViewContainer"] {
    background-color: #f8fafc;
    color: #0f172a;
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
    color: #0f172a !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em;
}

h1 { font-size: 2.2rem !important; color: #0f172a !important; }
h2 { font-size: 1.6rem !important; border-bottom: 2px solid #2563eb; padding-bottom: 0.4rem; margin-top: 1.8rem !important; color: #0f172a !important; }
h3 { font-size: 1.3rem !important; color: #1d4ed8 !important; }
h4 { font-size: 1.1rem !important; color: #1e293b !important; }

p, li, span, td {
    color: #1e293b;
}

/* Report Header Banner (Deep Navy Accent Header) */
.pdf-report-header {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    border: 1px solid #cbd5e1;
    border-radius: 12px;
    padding: 1.75rem 2rem;
    margin-bottom: 2rem;
    box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.15);
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
    color: #cbd5e1;
    margin-bottom: 1rem;
}

.pdf-header-meta {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
    font-size: 0.85rem;
    color: #e2e8f0;
    border-top: 1px solid rgba(255,255,255,0.15);
    padding-top: 0.75rem;
}

/* Callout Boxes (Light Corporate Style) */
.report-callout {
    background: #ffffff;
    border-left: 4px solid #2563eb;
    border-top: 1px solid #e2e8f0;
    border-right: 1px solid #e2e8f0;
    border-bottom: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 1.25rem 1.5rem;
    margin: 1.25rem 0;
    font-size: 1rem;
    line-height: 1.65;
    color: #0f172a;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

.callout-warning { border-left-color: #d97706; background: #fffbebfb; }
.callout-danger { border-left-color: #dc2626; background: #fef2f2; }
.callout-success { border-left-color: #059669; background: #ecfdf5; }

.callout-label {
    font-size: 0.75rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 0.5rem;
    display: block;
}

/* Tables (Light High-Contrast Formatting) */
table {
    width: 100%;
    border-collapse: collapse;
    margin: 1rem 0;
    border-radius: 8px;
    overflow: hidden;
    background: #ffffff;
    border: 1px solid #cbd5e1;
}

th {
    background-color: #0f172a;
    color: #ffffff;
    font-weight: 700;
    text-align: left;
    padding: 0.85rem 1rem;
    border-bottom: 2px solid #2563eb;
    font-size: 0.9rem;
}

td {
    padding: 0.85rem 1rem;
    border-bottom: 1px solid #e2e8f0;
    color: #0f172a;
    font-size: 0.95rem;
}

tr:nth-child(even) td {
    background-color: #f8fafc;
}

tr:hover td {
    background-color: #eff6ff;
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

.badge-confirmed { background-color: #d1fae5; color: #047857; border: 1px solid #a7f3d0; }
.badge-guidance { background-color: #dbeafe; color: #1d4ed8; border: 1px solid #bfdbfe; }
.badge-estimate { background-color: #fef3c7; color: #b45309; border: 1px solid #fde68a; }
.badge-danger { background-color: #fee2e2; color: #b91c1c; border: 1px solid #fca5a5; }

/* Metric Grid Cards */
.metric-card {
    background: #ffffff;
    border-radius: 10px;
    padding: 1.2rem;
    border: 1px solid #e2e8f0;
    border-left: 4px solid #2563eb;
    margin-bottom: 1rem;
    box-shadow: 0 2px 4px rgba(0,0,0,0.03);
}

.metric-card-green { border-left-color: #059669; }
.metric-card-amber { border-left-color: #d97706; }
.metric-card-red { border-left-color: #dc2626; }

.metric-title { font-size: 0.8rem; color: #64748b; text-transform: uppercase; font-weight: 700; }
.metric-value { font-size: 1.6rem; font-weight: 800; color: #0f172a; margin: 0.3rem 0; }
.metric-desc { font-size: 0.85rem; color: #475569; line-height: 1.4; }

/* Clean PDF & Print Rules */
@media print {
    body, [data-testid="stAppViewContainer"] {
        background-color: #ffffff !important;
        color: #0f172a !important;
    }
    
    .stTextInput, [data-testid="stRadio"], iframe, .stChatInput, [data-testid="stForm"] {
        display: none !important;
    }
    
    .pdf-report-header {
        background: #0f172a !important;
        color: #ffffff !important;
        -webkit-print-color-adjust: exact !important;
        print-color-adjust: exact !important;
    }

    .report-callout {
        background: #f8fafc !important;
        color: #0f172a !important;
        border-left: 4px solid #2563eb !important;
        -webkit-print-color-adjust: exact !important;
        print-color-adjust: exact !important;
    }
    
    table {
        background: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
    }

    th {
        background-color: #0f172a !important;
        color: #ffffff !important;
        -webkit-print-color-adjust: exact !important;
        print-color-adjust: exact !important;
    }

    td {
        color: #0f172a !important;
        border-bottom: 1px solid #e2e8f0 !important;
    }
    
    h1, h2, h3, h4 {
        color: #0f172a !important;
    }
}
"""

def inject_custom_css():
    """Inject custom light report styling into Streamlit app."""
    st.markdown(f'<style>{CUSTOM_CSS}</style>', unsafe_allow_html=True)
