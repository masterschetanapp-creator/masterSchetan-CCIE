"""
Resolves stock names to NSE/BSE tickers.
"""

import logging
from typing import Dict, Optional, List
import yfinance as yf
import difflib

# A common mapping of top Indian stocks for instant resolution
COMMON_STOCKS = {
    "RELIANCE": {"symbol": "RELIANCE.NS", "name": "Reliance Industries Limited", "exchange": "NSE"},
    "TCS": {"symbol": "TCS.NS", "name": "Tata Consultancy Services Limited", "exchange": "NSE"},
    "HDFCBANK": {"symbol": "HDFCBANK.NS", "name": "HDFC Bank Limited", "exchange": "NSE"},
    "HDFC BANK": {"symbol": "HDFCBANK.NS", "name": "HDFC Bank Limited", "exchange": "NSE"},
    "ICICIBANK": {"symbol": "ICICIBANK.NS", "name": "ICICI Bank Limited", "exchange": "NSE"},
    "ICICI BANK": {"symbol": "ICICIBANK.NS", "name": "ICICI Bank Limited", "exchange": "NSE"},
    "INFY": {"symbol": "INFY.NS", "name": "Infosys Limited", "exchange": "NSE"},
    "INFOSYS": {"symbol": "INFY.NS", "name": "Infosys Limited", "exchange": "NSE"},
    "SBI": {"symbol": "SBIN.NS", "name": "State Bank of India", "exchange": "NSE"},
    "SBIN": {"symbol": "SBIN.NS", "name": "State Bank of India", "exchange": "NSE"},
    "STATE BANK": {"symbol": "SBIN.NS", "name": "State Bank of India", "exchange": "NSE"},
    "BHARTIARTL": {"symbol": "BHARTIARTL.NS", "name": "Bharti Airtel Limited", "exchange": "NSE"},
    "AIRTEL": {"symbol": "BHARTIARTL.NS", "name": "Bharti Airtel Limited", "exchange": "NSE"},
    "ITC": {"symbol": "ITC.NS", "name": "ITC Limited", "exchange": "NSE"},
    "L&T": {"symbol": "LT.NS", "name": "Larsen & Toubro Limited", "exchange": "NSE"},
    "LT": {"symbol": "LT.NS", "name": "Larsen & Toubro Limited", "exchange": "NSE"},
    "LARSEN": {"symbol": "LT.NS", "name": "Larsen & Toubro Limited", "exchange": "NSE"},
    "BAJFINANCE": {"symbol": "BAJFINANCE.NS", "name": "Bajaj Finance Limited", "exchange": "NSE"},
    "HINDUNILVR": {"symbol": "HINDUNILVR.NS", "name": "Hindustan Unilever Limited", "exchange": "NSE"},
    "HUL": {"symbol": "HINDUNILVR.NS", "name": "Hindustan Unilever Limited", "exchange": "NSE"},
    "TATASTEEL": {"symbol": "TATASTEEL.NS", "name": "Tata Steel Limited", "exchange": "NSE"},
    "TATA STEEL": {"symbol": "TATASTEEL.NS", "name": "Tata Steel Limited", "exchange": "NSE"},
    "ASIANPAINT": {"symbol": "ASIANPAINT.NS", "name": "Asian Paints Limited", "exchange": "NSE"},
    "ASIAN PAINTS": {"symbol": "ASIANPAINT.NS", "name": "Asian Paints Limited", "exchange": "NSE"},
    "KOTAKBANK": {"symbol": "KOTAKBANK.NS", "name": "Kotak Mahindra Bank", "exchange": "NSE"},
    "KOTAK": {"symbol": "KOTAKBANK.NS", "name": "Kotak Mahindra Bank", "exchange": "NSE"},
    "MARUTI": {"symbol": "MARUTI.NS", "name": "Maruti Suzuki India Limited", "exchange": "NSE"},
    "MARUTI SUZUKI": {"symbol": "MARUTI.NS", "name": "Maruti Suzuki India Limited", "exchange": "NSE"},
    "AXISBANK": {"symbol": "AXISBANK.NS", "name": "Axis Bank Limited", "exchange": "NSE"},
    "AXIS BANK": {"symbol": "AXISBANK.NS", "name": "Axis Bank Limited", "exchange": "NSE"},
    "SUNPHARMA": {"symbol": "SUNPHARMA.NS", "name": "Sun Pharmaceutical Industries", "exchange": "NSE"},
    "TITAN": {"symbol": "TITAN.NS", "name": "Titan Company Limited", "exchange": "NSE"},
    "ULTRACEMCO": {"symbol": "ULTRACEMCO.NS", "name": "UltraTech Cement Limited", "exchange": "NSE"},
    "BAJAJFINSV": {"symbol": "BAJAJFINSV.NS", "name": "Bajaj Finserv Limited", "exchange": "NSE"},
    "NESTLEIND": {"symbol": "NESTLEIND.NS", "name": "Nestle India Limited", "exchange": "NSE"},
    "WIPRO": {"symbol": "WIPRO.NS", "name": "Wipro Limited", "exchange": "NSE"},
    "M&M": {"symbol": "M&M.NS", "name": "Mahindra & Mahindra Limited", "exchange": "NSE"},
    "HCLTECH": {"symbol": "HCLTECH.NS", "name": "HCL Technologies Limited", "exchange": "NSE"},
    "ADANIENT": {"symbol": "ADANIENT.NS", "name": "Adani Enterprises Limited", "exchange": "NSE"},
    "ADANIPORTS": {"symbol": "ADANIPORTS.NS", "name": "Adani Ports and Special Economic Zone", "exchange": "NSE"},
    "NTPC": {"symbol": "NTPC.NS", "name": "NTPC Limited", "exchange": "NSE"},
    "POWERGRID": {"symbol": "POWERGRID.NS", "name": "Power Grid Corporation of India", "exchange": "NSE"},
    "TATAMOTORS": {"symbol": "TATAMOTORS.NS", "name": "Tata Motors Limited", "exchange": "NSE"},
    "COALINDIA": {"symbol": "COALINDIA.NS", "name": "Coal India Limited", "exchange": "NSE"},
    "ONGC": {"symbol": "ONGC.NS", "name": "Oil and Natural Gas Corporation", "exchange": "NSE"},
    "HDFCLIFE": {"symbol": "HDFCLIFE.NS", "name": "HDFC Life Insurance Company", "exchange": "NSE"},
    "SBILIFE": {"symbol": "SBILIFE.NS", "name": "SBI Life Insurance Company", "exchange": "NSE"},
    "GRASIM": {"symbol": "GRASIM.NS", "name": "Grasim Industries Limited", "exchange": "NSE"},
    "TECHM": {"symbol": "TECHM.NS", "name": "Tech Mahindra Limited", "exchange": "NSE"},
    "PINE LABS": {"symbol": "PINELABS.NS", "name": "Pine Labs Limited", "exchange": "NSE"},
    "PINELABS": {"symbol": "PINELABS.NS", "name": "Pine Labs Limited", "exchange": "NSE"},
    "EICHERMOT": {"symbol": "EICHERMOT.NS", "name": "Eicher Motors Limited", "exchange": "NSE"},
    "INDUSINDBK": {"symbol": "INDUSINDBK.NS", "name": "IndusInd Bank Limited", "exchange": "NSE"},
    "DRREDDY": {"symbol": "DRREDDY.NS", "name": "Dr. Reddy's Laboratories", "exchange": "NSE"},
    "CIPLA": {"symbol": "CIPLA.NS", "name": "Cipla Limited", "exchange": "NSE"},
    "BAJAJ-AUTO": {"symbol": "BAJAJ-AUTO.NS", "name": "Bajaj Auto Limited", "exchange": "NSE"},
    "APOLLOHOSP": {"symbol": "APOLLOHOSP.NS", "name": "Apollo Hospitals Enterprise", "exchange": "NSE"},
    "DIVISLAB": {"symbol": "DIVISLAB.NS", "name": "Divi's Laboratories Limited", "exchange": "NSE"},
    "HINDALCO": {"symbol": "HINDALCO.NS", "name": "Hindalco Industries Limited", "exchange": "NSE"},
    "BRITANNIA": {"symbol": "BRITANNIA.NS", "name": "Britannia Industries Limited", "exchange": "NSE"},
    "BPCL": {"symbol": "BPCL.NS", "name": "Bharat Petroleum Corporation", "exchange": "NSE"},
    "TATACONSUM": {"symbol": "TATACONSUM.NS", "name": "Tata Consumer Products", "exchange": "NSE"},
    "UPL": {"symbol": "UPL.NS", "name": "UPL Limited", "exchange": "NSE"},
    "HEROMOTOCO": {"symbol": "HEROMOTOCO.NS", "name": "Hero MotoCorp Limited", "exchange": "NSE"},
    "LTIM": {"symbol": "LTIM.NS", "name": "LTIMindtree Limited", "exchange": "NSE"}
}

def search_stocks(query: str) -> List[Dict]:
    """
    Fuzzy match query against COMMON_STOCKS names and return top matches.
    """
    if not query:
        return []
    query_upper = query.upper().strip()
    
    # Check for exact matches
    if query_upper in COMMON_STOCKS:
        return [COMMON_STOCKS[query_upper]]
        
    # Fuzzy match keys
    matches = difflib.get_close_matches(query_upper, COMMON_STOCKS.keys(), n=5, cutoff=0.5)
    
    results = []
    seen = set()
    for match in matches:
        stock = COMMON_STOCKS[match]
        if stock['symbol'] not in seen:
            results.append(stock)
            seen.add(stock['symbol'])
            
    # Fuzzy match values (names)
    names = [s['name'] for s in COMMON_STOCKS.values()]
    name_matches = difflib.get_close_matches(query, names, n=5, cutoff=0.5)
    for name_match in name_matches:
        for key, stock in COMMON_STOCKS.items():
            if stock['name'] == name_match and stock['symbol'] not in seen:
                results.append(stock)
                seen.add(stock['symbol'])
                break
                
    # If no results, just return a default structure for the query
    if not results:
        results.append({
            "symbol": f"{query_upper}.NS",
            "name": query_upper,
            "exchange": "NSE"
        })
        
    return results[:5]


def resolve_stock(query: str) -> Optional[Dict]:
    """
    Resolve a stock name/symbol to full ticker info.
    Returns dict with: symbol, name, exchange.
    First checks COMMON_STOCKS, then tries yfinance search.
    """
    if not query:
        return None

    query_upper = query.upper().strip()
    
    # Check in common stocks first
    if query_upper in COMMON_STOCKS:
        return COMMON_STOCKS[query_upper]

    try:
        # Check if it has an extension, if not append .NS
        symbol = query_upper if "." in query_upper else f"{query_upper}.NS"
        ticker = yf.Ticker(symbol)
        info = ticker.info
        if 'shortName' in info or 'longName' in info:
            return {
                "symbol": symbol,
                "name": info.get("longName") or info.get("shortName") or query_upper,
                "exchange": info.get("exchange", "NSE")
            }
    except Exception as e:
        logging.warning(f"Failed to resolve stock via yfinance: {e}")

    # Standard fallback
    return {
        "symbol": f"{query_upper}.NS",
        "name": query_upper,
        "exchange": "NSE"
    }
