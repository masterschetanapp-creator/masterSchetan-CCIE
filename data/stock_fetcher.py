"""Secondary-market data adapter for CCIE.

This module deliberately does not infer exchange disclosures. Yahoo Finance data
is useful for a market snapshot, but it is not a primary filing and it cannot
reliably identify a statement as standalone or consolidated. Every returned
statement is tagged accordingly so downstream decisions can keep that boundary.
"""

from typing import Any, Dict, List
import re

import numpy as np
import pandas as pd
import yfinance as yf


UNKNOWN = "UNKNOWN"
SECONDARY_EVIDENCE = {
    "source_type": "SECONDARY_MARKET_DATA",
    "verification_status": "SECONDARY_ONLY",
}


def convert_types(obj: Any) -> Any:
    """Recursively convert pandas and NumPy values to JSON-safe Python values."""
    if isinstance(obj, (np.integer, int)):
        return int(obj)
    if isinstance(obj, (np.floating, float)):
        return None if np.isnan(obj) or np.isinf(obj) else float(obj)
    if isinstance(obj, np.ndarray):
        return [convert_types(item) for item in obj]
    if isinstance(obj, pd.Timestamp):
        return obj.isoformat()
    if isinstance(obj, dict):
        return {str(key.isoformat() if hasattr(key, "isoformat") else key): convert_types(value) for key, value in obj.items()}
    if isinstance(obj, list):
        return [convert_types(item) for item in obj]
    return obj


def _statement_date(column: Any) -> str:
    return str(column.date()) if hasattr(column, "date") else str(column)


def _sorted_statement_columns(df: pd.DataFrame) -> List[Any]:
    """Return financial-statement columns newest first, regardless of provider order."""
    return sorted(list(df.columns), key=lambda column: pd.to_datetime(column, errors="coerce"), reverse=True)


def df_to_yearly_dicts(
    df: pd.DataFrame,
    statement_frequency: str = "annual",
    statement_scope: str = UNKNOWN,
) -> List[Dict[str, Any]]:
    """Convert a statement table to newest-first records with period and scope tags."""
    if df is None or not isinstance(df, pd.DataFrame) or df.empty:
        return []

    frequency = str(statement_frequency or "annual").lower()
    records: List[Dict[str, Any]] = []
    for index, column in enumerate(_sorted_statement_columns(df)):
        period_end = _statement_date(column)
        record: Dict[str, Any] = {
            "date": period_end,
            "period_end": period_end,
            "reporting_period": f"latest_{frequency}" if index == 0 else f"historical_{frequency}",
            "statement_scope": statement_scope or UNKNOWN,
            **SECONDARY_EVIDENCE,
        }
        for metric, value in df[column].items():
            if pd.isna(value):
                continue
            if isinstance(value, (np.integer, int)):
                record[str(metric)] = int(value)
            elif isinstance(value, (np.floating, float)):
                if not (np.isnan(value) or np.isinf(value)):
                    record[str(metric)] = float(value)
            else:
                record[str(metric)] = str(value)
        records.append(record)
    return records


def df_to_display_table(df: pd.DataFrame) -> Dict[str, Any]:
    """Convert a financial DataFrame to a display table without invented values."""
    if df is None or not isinstance(df, pd.DataFrame) or df.empty:
        return {"columns": [], "data": []}

    columns = [_statement_date(column) for column in _sorted_statement_columns(df)]
    rows = []
    for metric, row in df.iterrows():
        display_row = {"Metric": str(metric)}
        for column, label in zip(_sorted_statement_columns(df), columns):
            value = row[column]
            if pd.isna(value):
                display_row[label] = UNKNOWN
            elif isinstance(value, (int, float, np.number)):
                value_float = float(value)
                display_row[label] = f"{value_float / 1e7:,.2f} Cr" if abs(value_float) >= 1e7 else f"{value_float:,.2f}"
            else:
                display_row[label] = str(value)
        rows.append(display_row)
    return {"columns": ["Metric"] + columns, "data": rows}


def fetch_expanded_resources(ticker: yf.Ticker, info: dict, symbol: str) -> Dict[str, Any]:
    """Expose supplied consensus targets without a CCIE recommendation or synthetic ratings."""
    return {
        **SECONDARY_EVIDENCE,
        "analyst_target_high": info.get("targetHighPrice") if isinstance(info.get("targetHighPrice"), (int, float)) else None,
        "analyst_target_mean": info.get("targetMeanPrice") if isinstance(info.get("targetMeanPrice"), (int, float)) else None,
        "analyst_target_low": info.get("targetLowPrice") if isinstance(info.get("targetLowPrice"), (int, float)) else None,
        "analyst_opinion_count": info.get("numberOfAnalystOpinions") if isinstance(info.get("numberOfAnalystOpinions"), int) else None,
        "credit_rating": UNKNOWN,
        "regulatory_status": UNKNOWN,
    }


def fetch_delivery_and_bulk_deals(ticker: yf.Ticker, info: dict, symbol: str) -> Dict[str, Any]:
    """Exchange-only delivery and bulk-deal information requires an exchange feed."""
    return {
        "delivery_pct": None,
        "delivery_status": UNKNOWN,
        "bulk_deals": [],
        "source_type": UNKNOWN,
        "verification_status": "UNVERIFIED",
    }


def fetch_segment_breakdown_and_trajectory(ticker: yf.Ticker, info: dict, symbol: str) -> Dict[str, Any]:
    """Segment figures are only available after parsing an annual-report disclosure."""
    return {
        "segment_breakdown": [],
        "source_type": UNKNOWN,
        "verification_status": "UNVERIFIED",
    }


def fetch_automated_meta(ticker: yf.Ticker, info: dict, symbol: str) -> Dict[str, Any]:
    """Extract only metadata that can be read directly from the secondary payload."""
    founding_year = None
    description = str(info.get("longBusinessSummary") or "")
    match = re.findall(r"(?:incorporated|founded|established|started|formed)\s+in\s+(\d{4})", description, re.IGNORECASE)
    if match:
        founding_year = match[0]

    listing_date = None
    try:
        history = ticker.history(period="max")
        if not history.empty:
            listing_date = str(history.index[0].date())
    except Exception:
        pass

    upcoming_earnings = None
    try:
        calendar = getattr(ticker, "calendar", {})
        if isinstance(calendar, dict) and calendar.get("Earnings Date"):
            upcoming_earnings = str(calendar["Earnings Date"][0])
    except Exception:
        pass

    return {
        "founding_year": founding_year,
        "listing_date": listing_date,
        "upcoming_earnings": upcoming_earnings,
        "shareholding": UNKNOWN,
        **SECONDARY_EVIDENCE,
    }


def fetch_stock_profile(symbol: str) -> Dict[str, Any]:
    """Fetch a secondary company profile."""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info or {}
        return convert_types({
            "name": info.get("longName") or info.get("shortName") or symbol,
            "sector": info.get("sector") or UNKNOWN,
            "industry": info.get("industry") or UNKNOWN,
            "description": info.get("longBusinessSummary") or UNKNOWN,
            "website": info.get("website") or None,
            "employees": info.get("fullTimeEmployees"),
            "market_cap": info.get("marketCap"),
            "current_price": info.get("currentPrice") or info.get("regularMarketPrice"),
            "fifty_two_week_high": info.get("fiftyTwoWeekHigh"),
            "fifty_two_week_low": info.get("fiftyTwoWeekLow"),
            "trailing_pe": info.get("trailingPE"),
            "forward_pe": info.get("forwardPE"),
            "price_to_book": info.get("priceToBook"),
            "debt_to_equity": info.get("debtToEquity"),
            "return_on_equity": info.get("returnOnEquity"),
            "dividend_yield": info.get("dividendYield"),
            "officers": info.get("companyOfficers", []),
            "auto_meta": fetch_automated_meta(ticker, info, symbol),
            **SECONDARY_EVIDENCE,
        })
    except Exception:
        return {"name": symbol, "source_type": UNKNOWN, "verification_status": "UNVERIFIED"}


def fetch_price_data(symbol: str) -> Dict[str, Any]:
    """Fetch a secondary market-price snapshot; unavailable values remain UNKNOWN."""
    try:
        ticker = yf.Ticker(symbol)
        history = ticker.history(period="1mo")
        if history.empty:
            info = ticker.info or {}
            current = info.get("currentPrice") or info.get("regularMarketPrice")
            previous = info.get("regularMarketPreviousClose") or info.get("previousClose")
            change = ((current - previous) / previous) * 100 if isinstance(current, (int, float)) and isinstance(previous, (int, float)) and previous else None
            return convert_types({
                "current_price": current,
                "change_percent": change,
                "volume": info.get("volume") or info.get("regularMarketVolume"),
                "vwap": None,
                "history": [],
                **SECONDARY_EVIDENCE,
            })

        current = float(history["Close"].iloc[-1])
        previous = float(history["Close"].iloc[-2]) if len(history) > 1 else None
        change = ((current - previous) / previous) * 100 if previous else None
        volume_sum = history["Volume"].sum()
        vwap = (history["Close"] * history["Volume"]).sum() / volume_sum if volume_sum > 0 else None
        history_rows = [
            {"Date": _statement_date(index), "Close": float(row["Close"]), "Volume": int(row["Volume"])}
            for index, row in history.iterrows()
        ]
        return convert_types({
            "current_price": current,
            "change_percent": change,
            "volume": int(history["Volume"].iloc[-1]),
            "vwap": vwap,
            "history": history_rows,
            **SECONDARY_EVIDENCE,
        })
    except Exception:
        return {
            "current_price": None,
            "change_percent": None,
            "volume": None,
            "vwap": None,
            "history": [],
            "source_type": UNKNOWN,
            "verification_status": "UNVERIFIED",
        }


def fetch_financial_statements(symbol: str) -> Dict[str, Any]:
    """Fetch annual and quarterly statements separately; never merge their scope."""
    try:
        ticker = yf.Ticker(symbol)
        annual_income = ticker.financials
        annual_balance = ticker.balance_sheet
        annual_cashflow = ticker.cashflow
        quarterly_income = ticker.quarterly_financials
        quarterly_balance = ticker.quarterly_balance_sheet
        quarterly_cashflow = ticker.quarterly_cashflow
        return convert_types({
            "annual_income_stmt": df_to_yearly_dicts(annual_income, "annual"),
            "annual_balance_sheet": df_to_yearly_dicts(annual_balance, "annual"),
            "annual_cashflow": df_to_yearly_dicts(annual_cashflow, "annual"),
            "quarterly_income_stmt": df_to_yearly_dicts(quarterly_income, "quarterly"),
            "quarterly_balance_sheet": df_to_yearly_dicts(quarterly_balance, "quarterly"),
            "quarterly_cashflow": df_to_yearly_dicts(quarterly_cashflow, "quarterly"),
            "display_income_statement": df_to_display_table(annual_income),
            "display_balance_sheet": df_to_display_table(annual_balance),
            "display_cash_flow": df_to_display_table(annual_cashflow),
            "display_quarterly_income": df_to_display_table(quarterly_income),
            **SECONDARY_EVIDENCE,
        })
    except Exception:
        return {
            "annual_income_stmt": [], "annual_balance_sheet": [], "annual_cashflow": [],
            "quarterly_income_stmt": [], "quarterly_balance_sheet": [], "quarterly_cashflow": [],
            "display_income_statement": {"columns": [], "data": []},
            "display_balance_sheet": {"columns": [], "data": []},
            "display_cash_flow": {"columns": [], "data": []},
            "display_quarterly_income": {"columns": [], "data": []},
            "source_type": UNKNOWN,
            "verification_status": "UNVERIFIED",
        }


def fetch_dividends_and_actions(symbol: str) -> Dict[str, Any]:
    """Fetch raw dividend and split history, retaining numerical dividend amounts."""
    try:
        ticker = yf.Ticker(symbol)
        dividends = ticker.dividends if hasattr(ticker, "dividends") else pd.Series()
        splits = ticker.splits if hasattr(ticker, "splits") else pd.Series()
        dividend_rows = [
            {"Date": _statement_date(date), "amount": float(value), "Dividend": float(value), **SECONDARY_EVIDENCE}
            for date, value in dividends.sort_index(ascending=False).items()
        ] if not dividends.empty else []
        split_rows = [
            {"Date": _statement_date(date), "Split Ratio": float(value), **SECONDARY_EVIDENCE}
            for date, value in splits.sort_index(ascending=False).items()
        ] if not splits.empty else []
        return {"dividends": dividend_rows, "splits": split_rows, **SECONDARY_EVIDENCE}
    except Exception:
        return {"dividends": [], "splits": [], "source_type": UNKNOWN, "verification_status": "UNVERIFIED"}


def fetch_holders(symbol: str) -> Dict[str, Any]:
    """Return provider holder tables without mapping them to exchange taxonomy."""
    try:
        ticker = yf.Ticker(symbol)
        major = ticker.major_holders
        institutional = ticker.institutional_holders
        mutual_funds = ticker.mutualfund_holders
        major_rows = major.to_dict(orient="records") if isinstance(major, pd.DataFrame) and not major.empty else []
        institutional_rows = institutional.to_dict(orient="records") if isinstance(institutional, pd.DataFrame) and not institutional.empty else []
        mutual_fund_rows = mutual_funds.to_dict(orient="records") if isinstance(mutual_funds, pd.DataFrame) and not mutual_funds.empty else []
        return convert_types({
            "major_holders": major_rows,
            "institutional_holders": institutional_rows,
            "mutual_fund_holders": mutual_fund_rows,
            "shareholding_taxonomy": UNKNOWN,
            **SECONDARY_EVIDENCE,
        })
    except Exception:
        return {"major_holders": [], "institutional_holders": [], "mutual_fund_holders": [], "source_type": UNKNOWN, "verification_status": "UNVERIFIED"}


def fetch_all_data(symbol: str) -> Dict[str, Any]:
    """Build a raw secondary-data packet with no derived exchange claims."""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info or {}
    except Exception:
        ticker = yf.Ticker(symbol)
        info = {}

    actions = fetch_dividends_and_actions(symbol)
    financials = fetch_financial_statements(symbol)
    return {
        "info": info,
        "profile": fetch_stock_profile(symbol),
        "price_data": fetch_price_data(symbol),
        "financials": financials,
        "annual_income_stmt": financials.get("annual_income_stmt", []),
        "annual_balance_sheet": financials.get("annual_balance_sheet", []),
        "annual_cashflow": financials.get("annual_cashflow", []),
        "quarterly_income_stmt": financials.get("quarterly_income_stmt", []),
        "quarterly_balance_sheet": financials.get("quarterly_balance_sheet", []),
        "quarterly_cashflow": financials.get("quarterly_cashflow", []),
        "dividends": actions.get("dividends", []),
        "actions": actions.get("splits", []),
        "holders": fetch_holders(symbol),
        "phase1_nse": fetch_delivery_and_bulk_deals(ticker, info, symbol),
        "phase2_segments": fetch_segment_breakdown_and_trajectory(ticker, info, symbol).get("segment_breakdown", []),
        "expanded_resources": fetch_expanded_resources(ticker, info, symbol),
        **SECONDARY_EVIDENCE,
    }
