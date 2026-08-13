"""
masterSchetan CCIE — Master Application Entry Point
Streamlit app with Corporate Light Theme, 26 PDF Report Sections, Dynamic Sector Intelligence, & PDF Export.
"""

import streamlit as st
import os
import sys

# Configure page
st.set_page_config(
    page_title="masterSchetan CCIE — Indian Equity Research Engine",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

from config import APP_NAME, APP_TAGLINE, APP_VERSION
from ui.styles import inject_custom_css

# Inject Light Corporate CSS
inject_custom_css()

# Session State Initialization
if "selected_stock" not in st.session_state:
    st.session_state.selected_stock = None
if "dossier" not in st.session_state:
    st.session_state.dossier = None
if "view_mode" not in st.session_state:
    st.session_state.view_mode = "Simple"
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "search_triggered" not in st.session_state:
    st.session_state.search_triggered = False
if "force_research" not in st.session_state:
    st.session_state.force_research = False


def main():
    _render_sidebar()
    _render_header()
    
    # Stock Search Bar
    stock_info = _render_search()
    
    if stock_info:
        if (st.session_state.dossier is None or
            st.session_state.get("current_symbol") != stock_info["symbol"] or
            st.session_state.pop("force_research", False)):
            _run_research(stock_info)
        
        if st.session_state.dossier:
            _render_dossier()
    else:
        if st.session_state.dossier:
            _render_dossier()
        else:
            _render_welcome_screen()

    _render_footer()


def _render_sidebar():
    """Render sidebar for AI API Keys & Provider Quotas."""
    with st.sidebar:
        st.markdown("### 🤖 Multi-Model AI Engines")
        st.caption("Powered by Zero-Cost AI Integration")
        
        from ai.gemini_client import GeminiClient
        try:
            client = GeminiClient()
            status = client.get_provider_status()
            
            st.markdown("**Provider Status:**")
            name_map = {
                'gemini': 'Google Gemini 2.5',
                'groq': 'GroqCloud (Llama 3.3)',
                'openrouter': 'OpenRouter (Nemotron)',
                'deepseek': 'DeepSeek R1 / V3'
            }
            for provider, data in status.items():
                icon = "🟢" if data['configured'] else "⚪"
                state_text = "Active" if data['configured'] else "Not Configured"
                st.markdown(f"{icon} **{name_map[provider]}**: {state_text}")
        except Exception:
            pass
            
        st.markdown("---")
        with st.expander("🔑 Add / Change Free API Keys", expanded=False):
            st.markdown("Keys are stored in session memory only.")
            gemini_k = st.text_input("Google Gemini API Key", value=os.getenv("GEMINI_API_KEY", ""), type="password", key="input_gemini_k")
            groq_k = st.text_input("Groq API Key", value=os.getenv("GROQ_API_KEY", ""), type="password", key="input_groq_k")
            openrouter_k = st.text_input("OpenRouter API Key", value=os.getenv("OPENROUTER_API_KEY", ""), type="password", key="input_openrouter_k")
            deepseek_k = st.text_input("DeepSeek API Key", value=os.getenv("DEEPSEEK_API_KEY", ""), type="password", key="input_deepseek_k")
            
            if st.button("Save & Update AI Engines", use_container_width=True):
                if gemini_k:
                    os.environ["GEMINI_API_KEY"] = gemini_k
                    st.session_state["GEMINI_API_KEY"] = gemini_k
                if groq_k:
                    os.environ["GROQ_API_KEY"] = groq_k
                    st.session_state["GROQ_API_KEY"] = groq_k
                if openrouter_k:
                    os.environ["OPENROUTER_API_KEY"] = openrouter_k
                    st.session_state["OPENROUTER_API_KEY"] = openrouter_k
                if deepseek_k:
                    os.environ["DEEPSEEK_API_KEY"] = deepseek_k
                    st.session_state["DEEPSEEK_API_KEY"] = deepseek_k
                st.success("API keys updated successfully!")
                st.rerun()

        st.markdown("---")
        with st.expander("Primary Filing Evidence", expanded=False):
            st.file_uploader(
                "Filing text or HTML",
                type=["txt", "html", "htm"],
                key="primary_evidence_document",
            )
            st.selectbox(
                "Document category",
                options=["QUARTERLY_RESULTS", "ANNUAL_REPORT", "INVESTOR_PRESENTATION", "EARNINGS_TRANSCRIPT"],
                key="primary_evidence_source_type",
            )
            st.text_input("Public document link", key="primary_evidence_source_url")
            st.text_input("Exchange or company filing ID", key="primary_evidence_document_id")
            st.text_input("BSE scrip code (optional)", key="primary_evidence_bse_scrip_code")
            st.text_input("Document title", key="primary_evidence_document_title")
            st.text_input("Reporting period end (YYYY-MM-DD)", key="primary_evidence_period_end")
            st.selectbox(
                "Statement scope",
                options=["UNKNOWN", "STANDALONE", "CONSOLIDATED"],
                key="primary_evidence_statement_scope",
            )
            st.text_input("Published date (YYYY-MM-DD)", key="primary_evidence_published_date")
            st.text_input("Page number (optional)", key="primary_evidence_page")
            if st.session_state.get("primary_evidence_document"):
                st.caption("The document is used only when its link and filing ID are provided.")


def _uploaded_primary_evidence():
    """Convert the optional sidebar upload into a validated primary-evidence pack."""
    uploaded_file = st.session_state.get("primary_evidence_document")
    bse_scrip_code = str(st.session_state.get("primary_evidence_bse_scrip_code", "")).strip()
    if uploaded_file is None:
        return {"bse_scrip_code": bse_scrip_code} if bse_scrip_code else None

    try:
        content = uploaded_file.getvalue().decode("utf-8", errors="replace")
    except Exception:
        return None

    from data.primary_evidence_collector import build_uploaded_evidence_pack

    page_text = str(st.session_state.get("primary_evidence_page", "")).strip()
    page = int(page_text) if page_text.isdigit() and int(page_text) > 0 else None
    filename = str(getattr(uploaded_file, "name", "")).lower()
    pack = build_uploaded_evidence_pack(
        content,
        source_type=st.session_state.get("primary_evidence_source_type", ""),
        source_url=st.session_state.get("primary_evidence_source_url", ""),
        document_id=st.session_state.get("primary_evidence_document_id", ""),
        document_title=st.session_state.get("primary_evidence_document_title", ""),
        period_end=st.session_state.get("primary_evidence_period_end", ""),
        reporting_period="latest_period",
        statement_scope=st.session_state.get("primary_evidence_statement_scope", "UNKNOWN"),
        published_date=st.session_state.get("primary_evidence_published_date", ""),
        page=page,
        content_format="html" if filename.endswith((".html", ".htm")) else "text",
    )
    if bse_scrip_code:
        pack["bse_scrip_code"] = bse_scrip_code
    return pack if pack.get("documents") or bse_scrip_code else None


def _render_header():
    """Render the app header with branding in clean corporate light theme."""
    st.markdown(f"""
    <div style="background: #ffffff; border-radius: 12px; padding: 1.5rem 2rem; margin-bottom: 1.5rem; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
            <div>
                <h1 style="margin: 0; padding: 0; font-size: 2.2rem; color: #0f172a;">🔍 {APP_NAME}</h1>
                <p style="margin: 0.25rem 0 0 0; color: #475569; font-size: 1rem;">{APP_TAGLINE}</p>
            </div>
            <div style="text-align: right;">
                <span class="badge badge-confirmed">v{APP_VERSION}</span>
                <span class="badge badge-guidance">Multi-Model AI (Gemini + Groq)</span>
                <span class="badge badge-estimate">Zero Cost</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def _render_search():
    """Render the stock search interface with automatic Enter key trigger."""
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.markdown("<p style='text-align: center; color: #0f172a; font-weight: 600; font-size: 1.1rem;'>Enter any Indian stock name (e.g., IDBI, PNB, Reliance, TCS, HDFC Bank, SBI)</p>", unsafe_allow_html=True)

        query = st.text_input(
            "Search",
            placeholder="Type any BSE / NSE stock name or ticker (e.g. IDBI, SJVN, Tata)...",
            label_visibility="collapsed",
            key="stock_search"
        )

        if query and len(query.strip()) >= 2:
            from core.entity_resolver import resolve_stock, search_stocks
            suggestions = search_stocks(query.strip())
            resolved = resolve_stock(query.strip())

            stock_to_run = None

            if resolved and resolved.get("is_ambiguous"):
                st.markdown("<div style='color: #d97706; font-weight: 700; font-size: 1.05rem; margin-top: 0.5rem;'>Which Tata Motors business do you mean?</div>", unsafe_allow_html=True)
                opts = resolved["options"]
                opt_labels = [f"{o['name']} ({o['symbol']})" for o in opts]
                sel = st.selectbox("Select Business Entity:", options=opt_labels, key="demerger_select")
                idx = opt_labels.index(sel)
                stock_to_run = opts[idx]
            elif suggestions:
                options = [f"{s['name']} ({s['symbol']})" for s in suggestions]
                selected_option = st.selectbox(
                    "Select Company:",
                    options=options,
                    key="stock_select"
                )
                idx = options.index(selected_option)
                stock_to_run = suggestions[idx]
            elif resolved:
                stock_to_run = resolved
                st.markdown(f"""
                <div style="background: #ffffff; padding: 0.75rem 1rem; border-radius: 8px; border: 1px solid #2563eb; margin-bottom: 0.5rem; text-align: center; color: #0f172a;">
                    <strong>{resolved['name']}</strong> · {resolved['symbol']} ({resolved['exchange']})
                </div>
                """, unsafe_allow_html=True)

            if stock_to_run:
                btn_clicked = st.button("Generate Equity Research Dossier", type="primary", use_container_width=True, key="btn_run_research")
                query_changed = st.session_state.get("last_auto_query") != query.strip()

                if btn_clicked or query_changed:
                    st.session_state.last_auto_query = query.strip()
                    st.session_state.selected_stock = stock_to_run
                    st.session_state.search_triggered = True
                    st.session_state.force_research = btn_clicked
                    st.rerun()

                if hasattr(st.session_state, 'selected_stock') and st.session_state.search_triggered:
                    return st.session_state.selected_stock
            else:
                st.warning(f"Company '{query}' could not be reliably identified on BSE or NSE. Please check spelling or ticker symbol.")

    return None


def _run_research(stock_info: dict):
    """Run the complete research pipeline with progress display."""
    symbol = stock_info["symbol"]
    name = stock_info["name"]

    st.session_state.current_symbol = symbol
    st.session_state.chat_history = []

    progress_container = st.container()
    with progress_container:
        st.markdown(f"""
        <div style="background: #ffffff; padding: 2rem; border-radius: 12px; border: 1px solid #2563eb; text-align: center; margin: 2rem 0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
            <h2 style="color: #1d4ed8; margin-top: 0;">🔬 Generating Research Report for {name}</h2>
            <p style="color: #475569;">Compiling 26 research sections, auditing financial statements, and running multi-model AI synthesis...</p>
        </div>
        """, unsafe_allow_html=True)

        progress_bar = st.progress(0)
        status_text = st.empty()

        def update_progress(step: str, pct: int):
            progress_bar.progress(min(pct, 100))
            status_text.markdown(f"<div style='text-align: center; color: #475569; font-weight: 500;'>⏳ {step}</div>", unsafe_allow_html=True)

        from core.research_orchestrator import build_dossier

        try:
            dossier = build_dossier(
                symbol,
                name,
                progress_callback=update_progress,
                primary_evidence=_uploaded_primary_evidence(),
            )
            st.session_state.dossier = dossier
            if dossier.get("render_blocked"):
                st.warning("Research data was collected, but report rendering is blocked by reliability validation.")
            st.toast("✅ Master Research Report Generated!", icon="🎉")
        except Exception as e:
            st.error(f"❌ Research failed: {str(e)}")
            import traceback
            traceback.print_exc()

    progress_container.empty()


def _render_welcome_screen():
    """Render clean welcome screen banner."""
    st.markdown("""
    <div style="background: #ffffff; border: 1px solid #e2e8f0; border-left: 4px solid #2563eb; border-radius: 12px; padding: 2rem; margin: 2rem 0; text-align: center; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.03);">
        <h3 style="color: #0f172a; margin-top: 0; font-size: 1.4rem;">📊 Instant Multi-Model Equity Intelligence Engine</h3>
        <p style="color: #475569; font-size: 1rem; max-width: 700px; margin: 0.5rem auto 0 auto; line-height: 1.6;">
            Search any BSE or NSE listed stock to generate an evidence-gated research dossier. Source type, available evidence, and missing disclosures are shown explicitly.
        </p>
    </div>
    """, unsafe_allow_html=True)


def _render_dossier():
    """Render the full company dossier."""
    dossier = st.session_state.dossier
    if not dossier:
        return

    if dossier.get("render_blocked"):
        st.error("Report rendering is blocked because the consistency validator found missing or conflicting evidence.")
        for issue in dossier.get("consistency_check", {}).get("mismatches", []):
            st.write(f"- {issue}")
        return

    from ui.components import render_stock_header, render_view_toggle, render_disclaimer

    col1, col2 = st.columns([3, 1])
    with col2:
        st.components.v1.html("""
            <button onclick="window.parent.print()" style="
                background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
                color: #ffffff;
                border: none;
                padding: 0.65rem 1.2rem;
                border-radius: 8px;
                font-weight: 700;
                font-size: 0.95rem;
                cursor: pointer;
                width: 100%;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
                transition: all 0.2s ease;
            " onmouseover="this.style.opacity='0.9'" onmouseout="this.style.opacity='1.0'">
                🖨️ Save Report / Print PDF
            </button>
        """, height=45)

    # ── Stock Header ──────────────────────────────────────
    render_stock_header(
        dossier.get("modules", {}).get("company_snapshot", {}),
        dossier.get("modules", {}).get("price_data", {}),
        dossier.get("modules", {}).get("source_tracking", {}).get("summary", {})
    )

    # ── 3 Research Perspective Tabs ────────────────────────
    tab1, tab2, tab3 = st.tabs([
        "🟢 Common Man View (PDF Report)",
        "📊 Simple View (26 Research Sections)",
        "📈 Analyst View (Detailed Ratios & Financials)"
    ])

    with tab1:
        from ui.common_man_view import render_common_man_view
        render_common_man_view(dossier)

    with tab2:
        from ui.simple_view import render_simple_view
        render_simple_view(dossier)

    with tab3:
        from ui.analyst_view import render_analyst_view
        render_analyst_view(dossier)

    # ── Disclaimer ────────────────────────────────────────
    render_disclaimer()


def _render_footer():
    """Render the app footer."""
    st.markdown(f"""
    <div style="text-align: center; color: #64748b; font-size: 0.85rem; margin-top: 3rem; padding-top: 1.5rem; border-top: 1px solid #e2e8f0;">
        <p>{APP_NAME} v{APP_VERSION} · Zero Cost · Evidence-Gated Equity Intelligence</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
