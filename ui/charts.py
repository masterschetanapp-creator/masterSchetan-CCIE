import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

# Global layout settings for premium dark theme
DARK_LAYOUT = dict(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#e2e8f0'),
    margin=dict(l=40, r=40, t=40, b=40),
    xaxis=dict(showgrid=False, zeroline=False, linecolor='rgba(255,255,255,0.1)'),
    yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', zeroline=False, linecolor='rgba(255,255,255,0.1)'),
)

def _empty_figure(message="Data not available") -> go.Figure:
    """Helper to return an empty figure with a message gracefully."""
    fig = go.Figure()
    fig.add_annotation(text=message, xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False, font=dict(size=16, color="#94a3b8"))
    fig.update_layout(**DARK_LAYOUT)
    return fig

def create_price_chart(price_history: dict) -> go.Figure:
    """Interactive price chart with volume."""
    try:
        df = pd.DataFrame(price_history)
        if df.empty: return _empty_figure()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df['date'], y=df['close'], mode='lines', name='Price', line=dict(color='#60a5fa', width=2)))
        fig.update_layout(title="Price History", yaxis_title="Price (₹)", **DARK_LAYOUT)
        return fig
    except Exception:
        return _empty_figure()

def create_revenue_profit_chart(financials: dict) -> go.Figure:
    """Revenue & Profit trend bar chart."""
    try:
        df = pd.DataFrame(financials)
        if df.empty: return _empty_figure()
        
        fig = go.Figure()
        fig.add_trace(go.Bar(x=df['year'], y=df['revenue'], name='Revenue', marker_color='#60a5fa'))
        fig.add_trace(go.Bar(x=df['year'], y=df['profit'], name='Net Profit', marker_color='#34d399'))
        
        fig.update_layout(title="Revenue vs Profit (₹ Cr)", barmode='group', **DARK_LAYOUT)
        return fig
    except Exception:
        return _empty_figure()

def create_margin_chart(metrics: dict) -> go.Figure:
    """Operating, Net, EBITDA margin line chart."""
    try:
        df = pd.DataFrame(metrics)
        if df.empty: return _empty_figure()
        
        fig = go.Figure()
        if 'operating_margin' in df.columns:
            fig.add_trace(go.Scatter(x=df['year'], y=df['operating_margin'], mode='lines+markers', name='Operating Margin', line=dict(color='#fbbf24')))
        if 'net_margin' in df.columns:
            fig.add_trace(go.Scatter(x=df['year'], y=df['net_margin'], mode='lines+markers', name='Net Margin', line=dict(color='#34d399')))
            
        fig.update_layout(title="Margins Over Time (%)", yaxis_title="%", **DARK_LAYOUT)
        return fig
    except Exception:
        return _empty_figure()

def create_shareholding_chart(holding_data: dict) -> go.Figure:
    """Stacked bar chart for shareholding pattern."""
    try:
        df = pd.DataFrame(holding_data)
        if df.empty: return _empty_figure()
        
        fig = px.bar(df, x="quarter", y=["promoter", "fii", "dii", "public"], 
                     title="Shareholding Pattern",
                     color_discrete_map={"promoter": "#60a5fa", "fii": "#34d399", "dii": "#fbbf24", "public": "#f87171"})
        fig.update_layout(**DARK_LAYOUT, barmode="stack", yaxis_title="Holding (%)")
        return fig
    except Exception:
        return _empty_figure()

def create_dividend_chart(dividends: dict) -> go.Figure:
    """Dividend history bar chart."""
    try:
        df = pd.DataFrame(dividends)
        if df.empty: return _empty_figure()
        
        fig = px.bar(df, x='year', y='dividend_per_share', title="Dividend History (₹ per share)", color_discrete_sequence=['#34d399'])
        fig.update_layout(**DARK_LAYOUT)
        return fig
    except Exception:
        return _empty_figure()

def create_debt_equity_chart(financials: dict) -> go.Figure:
    """Debt vs Equity over time."""
    try:
        df = pd.DataFrame(financials)
        if df.empty: return _empty_figure()
        
        fig = go.Figure()
        if 'debt' in df.columns:
            fig.add_trace(go.Bar(x=df['year'], y=df['debt'], name='Total Debt', marker_color='#f87171'))
        if 'equity' in df.columns:
            fig.add_trace(go.Bar(x=df['year'], y=df['equity'], name='Total Equity', marker_color='#60a5fa'))
            
        fig.update_layout(title="Debt vs Equity (₹ Cr)", barmode='group', **DARK_LAYOUT)
        return fig
    except Exception:
        return _empty_figure()

def create_cashflow_chart(cashflow: dict) -> go.Figure:
    """Operating, Investing, Financing cash flow."""
    try:
        df = pd.DataFrame(cashflow)
        if df.empty: return _empty_figure()
        
        fig = go.Figure()
        fig.add_trace(go.Bar(x=df['year'], y=df['operating'], name='Operating CF', marker_color='#34d399'))
        fig.add_trace(go.Bar(x=df['year'], y=df['investing'], name='Investing CF', marker_color='#f87171'))
        fig.add_trace(go.Bar(x=df['year'], y=df['financing'], name='Financing CF', marker_color='#fbbf24'))
        
        fig.update_layout(title="Cash Flows (₹ Cr)", barmode='group', **DARK_LAYOUT)
        return fig
    except Exception:
        return _empty_figure()

def create_peer_comparison_chart(peers: dict) -> go.Figure:
    """Horizontal bar chart comparing peer metrics."""
    try:
        df = pd.DataFrame(peers)
        if df.empty: return _empty_figure()
        
        fig = px.bar(df, x="pe_ratio", y="company", orientation='h', title="P/E Ratio Comparison vs Peers",
                     color="is_target", color_discrete_map={True: "#60a5fa", False: "#94a3b8"})
        
        fig.update_layout(**DARK_LAYOUT, showlegend=False, yaxis_title="")
        return fig
    except Exception:
        return _empty_figure()
