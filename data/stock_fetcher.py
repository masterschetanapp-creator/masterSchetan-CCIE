"""
Fetches ALL stock data from yfinance. This is the PRIMARY data source.
Converts DataFrames to clean, JSON-serializable structures.
"""

import yfinance as yf
import pandas as pd
import numpy as np
from typing import Dict, Any, List

def convert_types(obj: Any) -> Any:
    """Recursively convert pandas/numpy types to native python types for JSON."""
    if isinstance(obj, (np.integer, int)):
        return int(obj)
    elif isinstance(obj, (np.floating, float)):
        if np.isnan(obj) or np.isinf(obj):
            return None
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return [convert_types(x) for x in obj]
    elif isinstance(obj, pd.Timestamp):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {str(k.isoformat() if hasattr(k, 'isoformat') else k): convert_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_types(x) for x in obj]
    return obj


def df_to_yearly_dicts(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Convert pandas DataFrame where columns are dates and rows are metric names into a list of yearly dicts."""
    if df is None or not isinstance(df, pd.DataFrame) or df.empty:
        return []
    records = []
    for col in df.columns:
        date_str = str(col.date()) if hasattr(col, 'date') else str(col)
        year_data = {'date': date_str}
        for metric, val in df[col].items():
            if pd.notna(val):
                if isinstance(val, (np.integer, int)):
                    year_data[str(metric)] = int(val)
                elif isinstance(val, (np.floating, float)):
                    if not (np.isnan(val) or np.isinf(val)):
                        year_data[str(metric)] = float(val)
                else:
                    year_data[str(metric)] = str(val)
        records.append(year_data)
    return records


def df_to_display_table(df: pd.DataFrame) -> Dict[str, Any]:
    """Convert financial DataFrame into a displayable table dictionary (metrics as rows, formatted dates as columns)."""
    if df is None or not isinstance(df, pd.DataFrame) or df.empty:
        return {"columns": [], "data": []}
    
    # Format column headers as YYYY-MM-DD
    cols = [str(c.date()) if hasattr(c, 'date') else str(c) for c in df.columns]
    rows = []
    
    for metric, row in df.iterrows():
        row_dict = {"Metric": str(metric)}
        for col_raw, col_formatted in zip(df.columns, cols):
            val = row[col_raw]
            if pd.isna(val):
                row_dict[col_formatted] = "-"
            elif isinstance(val, (int, float, np.number)):
                # Convert to Cr (Crores) if large
                val_float = float(val)
                if abs(val_float) >= 1e7:
                    row_dict[col_formatted] = f"₹{val_float / 1e7:,.2f} Cr"
                elif abs(val_float) >= 1e5:
                    row_dict[col_formatted] = f"₹{val_float / 1e5:,.2f} L"
                else:
                    row_dict[col_formatted] = f"{val_float:,.2f}"
            else:
                row_dict[col_formatted] = str(val)
        rows.append(row_dict)
        
    return {"columns": ["Metric"] + cols, "data": rows}


def fetch_stock_profile(symbol: str) -> Dict[str, Any]:
    """Company profile: name, sector, industry, description, website, employees, officers, market_cap, listing_date etc."""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info or {}
        
        return convert_types({
            "name": info.get("longName") or info.get("shortName") or symbol,
            "sector": info.get("sector", "N/A"),
            "industry": info.get("industry", "N/A"),
            "description": info.get("longBusinessSummary", "Company description not available."),
            "website": info.get("website", ""),
            "employees": info.get("fullTimeEmployees", None),
            "market_cap": info.get("marketCap", None),
            "current_price": info.get("currentPrice", None),
            "fifty_two_week_high": info.get("fiftyTwoWeekHigh", None),
            "fifty_two_week_low": info.get("fiftyTwoWeekLow", None),
            "trailing_pe": info.get("trailingPE", None),
            "forward_pe": info.get("forwardPE", None),
            "price_to_book": info.get("priceToBook", None),
            "debt_to_equity": info.get("debtToEquity", None),
            "return_on_equity": info.get("returnOnEquity", None),
            "dividend_yield": info.get("dividendYield", None),
            "officers": info.get("companyOfficers", [])
        })
    except Exception as e:
        print(f"Error fetching profile for {symbol}: {e}")
        return {}


def fetch_price_data(symbol: str) -> Dict[str, Any]:
    """Current price, change%, 52W high/low, volume, VWAP."""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="1mo")
        if hist.empty:
            info = ticker.info or {}
            return {
                "current_price": info.get("currentPrice") or info.get("regularMarketPrice") or 0.0,
                "change_percent": 0.0,
                "volume": info.get("volume") or 0,
                "vwap": 0.0,
                "history": []
            }
            
        current = float(hist['Close'].iloc[-1])
        prev = float(hist['Close'].iloc[-2]) if len(hist) > 1 else current
        change_pct = ((current - prev) / prev) * 100 if prev else 0.0
        
        vwap = (hist['Close'] * hist['Volume']).sum() / hist['Volume'].sum() if hist['Volume'].sum() > 0 else current
        
        # Prepare lightweight history
        hist_records = []
        for idx, row in hist.iterrows():
            hist_records.append({
                "Date": str(idx.date()) if hasattr(idx, 'date') else str(idx),
                "Close": float(row["Close"]),
                "Volume": int(row["Volume"])
            })
            
        return convert_types({
            "current_price": current,
            "change_percent": change_pct,
            "volume": int(hist['Volume'].iloc[-1]),
            "vwap": vwap,
            "history": hist_records
        })
    except Exception as e:
        print(f"Error fetching price data for {symbol}: {e}")
        return {}


def fetch_financial_statements(symbol: str) -> Dict[str, Any]:
    """Income statement, balance sheet, cash flow in both structured list and table format."""
    try:
        ticker = yf.Ticker(symbol)
        
        inc = ticker.income_stmt if hasattr(ticker, 'income_stmt') else None
        bs = ticker.balance_sheet if hasattr(ticker, 'balance_sheet') else None
        cf = ticker.cashflow if hasattr(ticker, 'cashflow') else None
        
        q_inc = ticker.quarterly_income_stmt if hasattr(ticker, 'quarterly_income_stmt') else None
        q_bs = ticker.quarterly_balance_sheet if hasattr(ticker, 'quarterly_balance_sheet') else None
        q_cf = ticker.quarterly_cashflow if hasattr(ticker, 'quarterly_cashflow') else None
        
        return convert_types({
            # Year-by-year structured lists for financial calculator
            "annual_income_stmt": df_to_yearly_dicts(inc),
            "annual_balance_sheet": df_to_yearly_dicts(bs),
            "annual_cashflow": df_to_yearly_dicts(cf),
            
            "quarterly_income_stmt": df_to_yearly_dicts(q_inc),
            "quarterly_balance_sheet": df_to_yearly_dicts(q_bs),
            "quarterly_cashflow": df_to_yearly_dicts(q_cf),
            
            # Display tables for UI tabs
            "display_income_statement": df_to_display_table(inc),
            "display_balance_sheet": df_to_display_table(bs),
            "display_cash_flow": df_to_display_table(cf),
            "display_quarterly_income": df_to_display_table(q_inc),
        })
    except Exception as e:
        print(f"Error fetching financials for {symbol}: {e}")
        return {
            "annual_income_stmt": [],
            "annual_balance_sheet": [],
            "annual_cashflow": [],
            "display_income_statement": {"columns": [], "data": []},
            "display_balance_sheet": {"columns": [], "data": []},
            "display_cash_flow": {"columns": [], "data": []},
        }


def fetch_dividends_and_actions(symbol: str) -> Dict[str, Any]:
    """Dividend history, stock splits."""
    try:
        ticker = yf.Ticker(symbol)
        dividends = ticker.dividends if hasattr(ticker, 'dividends') else pd.Series()
        splits = ticker.splits if hasattr(ticker, 'splits') else pd.Series()
        
        div_list = []
        if not dividends.empty:
            # Sort newest first
            dividends_sorted = dividends.sort_index(ascending=False).head(15)
            for dt, val in dividends_sorted.items():
                div_list.append({
                    "Date": str(dt.date()) if hasattr(dt, 'date') else str(dt),
                    "Dividend (₹)": float(val)
                })
                
        split_list = []
        if not splits.empty:
            splits_sorted = splits.sort_index(ascending=False).head(10)
            for dt, val in splits_sorted.items():
                split_list.append({
                    "Date": str(dt.date()) if hasattr(dt, 'date') else str(dt),
                    "Split Ratio": float(val)
                })
                
        return {
            "dividends": div_list,
            "splits": split_list
        }
    except Exception as e:
        print(f"Error fetching actions for {symbol}: {e}")
        return {"dividends": [], "splits": []}


def fetch_holders(symbol: str) -> Dict[str, Any]:
    """Major holders, institutional holders, mutual fund holders from yfinance."""
    try:
        ticker = yf.Ticker(symbol)
        
        maj = ticker.major_holders
        inst = ticker.institutional_holders
        mf = ticker.mutualfund_holders
        
        maj_dict = {}
        if isinstance(maj, pd.DataFrame) and not maj.empty:
            # Handle different yfinance versions
            for _, row in maj.iterrows():
                if len(row) >= 2:
                    maj_dict[str(row.iloc[1])] = str(row.iloc[0])
                    
        return convert_types({
            "major_holders": maj_dict,
            "institutional_holders": inst.to_dict(orient="records") if isinstance(inst, pd.DataFrame) and not inst.empty else [],
            "mutual_fund_holders": mf.to_dict(orient="records") if isinstance(mf, pd.DataFrame) and not mf.empty else []
        })
    except Exception as e:
        print(f"Error fetching holders for {symbol}: {e}")
        return {"major_holders": {}, "institutional_holders": [], "mutual_fund_holders": []}


def fetch_all_data(symbol: str) -> Dict[str, Any]:
    """Master function that calls all above and returns complete data bundle."""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info or {}
    except Exception as e:
        print(f"Error fetching info for {symbol}: {e}")
        info = {}

    actions_data = fetch_dividends_and_actions(symbol)
    financials = fetch_financial_statements(symbol)

    return {
        "info": info,
        "profile": fetch_stock_profile(symbol),
        "price_data": fetch_price_data(symbol),
        "financials": financials,
        "annual_income_stmt": financials.get("annual_income_stmt", []),
        "annual_balance_sheet": financials.get("annual_balance_sheet", []),
        "annual_cashflow": financials.get("annual_cashflow", []),
        "dividends": actions_data.get("dividends", []),
        "actions": actions_data.get("splits", []),
        "holders": fetch_holders(symbol)
    }
