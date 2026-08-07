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
    initial_sidebar_state="collapsed"
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


def main():
    _render_header()
    
    # Stock Search Bar
    stock_info = _render_search()
    
    if stock_info:
        if (st.session_state.dossier is None or 
            st.session_state.get("current_symbol") != stock_info["symbol"]):
            _run_research(stock_info)
        
        if st.session_state.dossier:
            _render_dossier()
    else:
        if st.session_state.dossier:
            _render_dossier()
        else:
            _render_welcome_screen()

    _render_footer()


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
    """Render the stock search interface."""
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.markdown("<p style='text-align: center; color: #0f172a; font-weight: 600; font-size: 1.1rem;'>Enter any Indian stock name (e.g., PNB, Reliance, TCS, HDFC Bank, SBI)</p>", unsafe_allow_html=True)

        query = st.text_input(
            "Search",
            placeholder="Search BSE / NSE stock name or ticker...",
            label_visibility="collapsed",
            key="stock_search"
        )

        if query and len(query) >= 2:
            from core.entity_resolver import resolve_stock, search_stocks
            suggestions = search_stocks(query)

            if suggestions:
                options = [f"{s['name']} ({s['symbol']})" for s in suggestions]
                selected_option = st.selectbox(
                    "Select Company:",
                    options=options,
                    key="stock_select"
                )

                if st.button("🔍 Generate Complete AI Equity Research Report", type="primary", use_container_width=True):
                    idx = options.index(selected_option)
                    st.session_state.selected_stock = suggestions[idx]
                    st.session_state.search_triggered = True
                    st.rerun()

                if hasattr(st.session_state, 'selected_stock') and st.session_state.search_triggered:
                    return st.session_state.selected_stock
            else:
                resolved = resolve_stock(query)
                if resolved:
                    st.markdown(f"""
                    <div style="background: #ffffff; padding: 0.75rem 1rem; border-radius: 8px; border: 1px solid #e2e8f0; margin-bottom: 0.5rem; text-align: center; color: #0f172a;">
                        <strong>{resolved['name']}</strong> · {resolved['symbol']}
                    </div>
                    """, unsafe_allow_html=True)

                    if st.button("🔍 Generate Complete AI Equity Research Report", type="primary", use_container_width=True):
                        st.session_state.selected_stock = resolved
                        st.session_state.search_triggered = True
                        st.rerun()

                    if hasattr(st.session_state, 'selected_stock') and st.session_state.search_triggered:
                        return st.session_state.selected_stock
                else:
                    st.warning(f"Could not resolve '{query}'. Try the full company name or NSE ticker.")

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
            dossier = build_dossier(symbol, name, progress_callback=update_progress)
            st.session_state.dossier = dossier
            st.toast("✅ Master Research Report Generated!", icon="🎉")
        except Exception as e:
            st.error(f"❌ Research failed: {str(e)}")
            import traceback
            traceback.print_exc()

    progress_container.empty()


def _render_welcome_screen():
    """Render welcome screen with quick stock selection buttons."""
    st.markdown("<h3 style='text-align: center; margin-top: 2rem; color: #0f172a;'>Or choose a featured Indian stock:</h3>", unsafe_allow_html=True)

    popular_stocks = [
        {"name": "Punjab National Bank", "symbol": "PNB.NS"},
        {"name": "Suzlon Energy", "symbol": "SUZLON.NS"},
        {"name": "Larsen & Toubro", "symbol": "LT.NS"},
        {"name": "Reliance Industries", "symbol": "RELIANCE.NS"},
        {"name": "Tata Consultancy Services", "symbol": "TCS.NS"},
        {"name": "State Bank of India", "symbol": "SBIN.NS"},
        {"name": "HDFC Bank", "symbol": "HDFCBANK.NS"},
        {"name": "Sun Pharma", "symbol": "SUNPHARMA.NS"},
    ]

    cols = st.columns(4)
    for idx, stock in enumerate(popular_stocks):
        with cols[idx % 4]:
            if st.button(f"📊 {stock['name']}", key=f"popular_{idx}", use_container_width=True):
                st.session_state.selected_stock = stock
                st.session_state.search_triggered = True
                st.rerun()


def _render_dossier():
    """Render the full company dossier."""
    dossier = st.session_state.dossier
    if not dossier:
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
        dossier.get("modules", {}).get("price_data", {})
    )

    # ── View Toggle ───────────────────────────────────────
    view_mode = render_view_toggle()
    st.session_state.view_mode = view_mode

    # ── Render View ───────────────────────────────────────
    if view_mode == "Simple":
        from ui.simple_view import render_simple_view
        render_simple_view(dossier)
    else:
        from ui.analyst_view import render_analyst_view
        render_analyst_view(dossier)

    # ── Ask This Company (Chatbot) ────────────────────────
    st.markdown("---")
    _render_chatbot(dossier)

    # ── Disclaimer ────────────────────────────────────────
    render_disclaimer()


def _render_chatbot(dossier: dict):
    """Render the 'Ask this Company' AI chatbot."""
    company_name = dossier.get("modules", {}).get("company_snapshot", {}).get("name", "this company")

    st.markdown(f"""
    <div style="background: #ffffff; border-radius: 12px; padding: 1.5rem; border: 1px solid #e2e8f0; margin: 2rem 0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
        <h3 style="margin: 0; color: #1d4ed8;">💬 Ask {company_name} AI — Verified Dossier Q&A</h3>
        <p style="color: #64748b; margin: 0.25rem 0 1rem 0; font-size: 0.9rem;">AI answers strictly from the verified dossier and linked evidence database with citations.</p>
    </div>
    """, unsafe_allow_html=True)

    from ai.chatbot import CompanyChatbot
    from ai.gemini_client import GeminiClient

    try:
        gemini = GeminiClient()
        chatbot = CompanyChatbot(gemini, dossier)
        suggestions = chatbot.get_suggested_questions()

        cols = st.columns(min(len(suggestions), 3))
        for i, q in enumerate(suggestions[:3]):
            with cols[i]:
                if st.button(f"💡 {q}", key=f"suggest_{i}", use_container_width=True):
                    st.session_state.chat_history.append({"role": "user", "content": q})
                    response = chatbot.ask(q)
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
                    st.rerun()

    except Exception:
        pass

    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f"""
            <div style="background: #eff6ff; border-left: 3px solid #2563eb; color: #0f172a; padding: 0.75rem 1rem; border-radius: 6px; margin-bottom: 0.5rem;">
                <strong>You:</strong> {msg['content']}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="background: #f0fdf4; border-left: 3px solid #059669; color: #0f172a; padding: 0.75rem 1rem; border-radius: 6px; margin-bottom: 0.5rem;">
                <strong>🤖 AI Analyst:</strong> {msg['content']}
            </div>
            """, unsafe_allow_html=True)

    user_question = st.chat_input(f"Ask anything about {company_name}...")
    if user_question:
        st.session_state.chat_history.append({"role": "user", "content": user_question})
        try:
            gemini = GeminiClient()
            chatbot = CompanyChatbot(gemini, dossier)
            response = chatbot.ask(user_question)
            st.session_state.chat_history.append({"role": "assistant", "content": response})
        except Exception as e:
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": f"Error: {str(e)}"
            })
        st.rerun()


def _render_footer():
    """Render the app footer."""
    st.markdown(f"""
    <div style="text-align: center; color: #64748b; font-size: 0.85rem; margin-top: 3rem; padding-top: 1.5rem; border-top: 1px solid #e2e8f0;">
        <p>{APP_NAME} v{APP_VERSION} · Zero Cost · Fact-Checked Equity Intelligence</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
