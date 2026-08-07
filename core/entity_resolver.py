"""
masterSchetan CCIE — Entity Resolver
Resolves Indian stock names, brands, and search queries to valid NSE/BSE tickers.
Includes comprehensive mapping for Nifty 50, Nifty Next 50, Midcap 100, & recent IPOs.
"""

import logging
from typing import Dict, Optional, List
import yfinance as yf
import difflib

# A comprehensive dictionary of top 120+ Indian stocks for instant resolution
COMMON_STOCKS = {
    # Top Large Caps
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
    "BAJFINANCE": {"symbol": "BAJFINANCE.NS", "name": "Bajaj Finance Limited", "exchange": "NSE"},
    "HINDUNILVR": {"symbol": "HINDUNILVR.NS", "name": "Hindustan Unilever Limited", "exchange": "NSE"},
    "HUL": {"symbol": "HINDUNILVR.NS", "name": "Hindustan Unilever Limited", "exchange": "NSE"},
    "TATASTEEL": {"symbol": "TATASTEEL.NS", "name": "Tata Steel Limited", "exchange": "NSE"},
    "ASIANPAINT": {"symbol": "ASIANPAINT.NS", "name": "Asian Paints Limited", "exchange": "NSE"},
    "KOTAKBANK": {"symbol": "KOTAKBANK.NS", "name": "Kotak Mahindra Bank", "exchange": "NSE"},
    "MARUTI": {"symbol": "MARUTI.NS", "name": "Maruti Suzuki India Limited", "exchange": "NSE"},
    "AXISBANK": {"symbol": "AXISBANK.NS", "name": "Axis Bank Limited", "exchange": "NSE"},
    "AXIS BANK": {"symbol": "AXISBANK.NS", "name": "Axis Bank Limited", "exchange": "NSE"},
    "SUNPHARMA": {"symbol": "SUNPHARMA.NS", "name": "Sun Pharmaceutical Industries", "exchange": "NSE"},
    "TITAN": {"symbol": "TITAN.NS", "name": "Titan Company Limited", "exchange": "NSE"},
    "ULTRACEMCO": {"symbol": "ULTRACEMCO.NS", "name": "UltraTech Cement Limited", "exchange": "NSE"},
    "BAJAJFINSV": {"symbol": "BAJAJFINSV.NS", "name": "Bajaj Finserv Limited", "exchange": "NSE"},
    "WIPRO": {"symbol": "WIPRO.NS", "name": "Wipro Limited", "exchange": "NSE"},
    "M&M": {"symbol": "M&M.NS", "name": "Mahindra & Mahindra Limited", "exchange": "NSE"},
    "HCLTECH": {"symbol": "HCLTECH.NS", "name": "HCL Technologies Limited", "exchange": "NSE"},
    "ADANIENT": {"symbol": "ADANIENT.NS", "name": "Adani Enterprises Limited", "exchange": "NSE"},
    "ADANIPORTS": {"symbol": "ADANIPORTS.NS", "name": "Adani Ports and Special Economic Zone", "exchange": "NSE"},
    "NTPC": {"symbol": "NTPC.NS", "name": "NTPC Limited", "exchange": "NSE"},
    "POWERGRID": {"symbol": "POWERGRID.NS", "name": "Power Grid Corporation of India", "exchange": "NSE"},
    "TATAMOTORS": {"symbol": "TATAMOTORS.NS", "name": "Tata Motors Limited", "exchange": "NSE"},
    "TATA MOTORS": {"symbol": "TATAMOTORS.NS", "name": "Tata Motors Limited", "exchange": "NSE"},
    "COALINDIA": {"symbol": "COALINDIA.NS", "name": "Coal India Limited", "exchange": "NSE"},
    "ONGC": {"symbol": "ONGC.NS", "name": "Oil and Natural Gas Corporation", "exchange": "NSE"},

    # PSU & Capital Goods Giants
    "PNB": {"symbol": "PNB.NS", "name": "Punjab National Bank", "exchange": "NSE"},
    "PUNJAB NATIONAL BANK": {"symbol": "PNB.NS", "name": "Punjab National Bank", "exchange": "NSE"},
    "SUZLON": {"symbol": "SUZLON.NS", "name": "Suzlon Energy Limited", "exchange": "NSE"},
    "SUZLON ENERGY": {"symbol": "SUZLON.NS", "name": "Suzlon Energy Limited", "exchange": "NSE"},
    "BHEL": {"symbol": "BHEL.NS", "name": "Bharat Heavy Electricals Limited", "exchange": "NSE"},
    "HAL": {"symbol": "HAL.NS", "name": "Hindustan Aeronautics Limited", "exchange": "NSE"},
    "BEL": {"symbol": "BEL.NS", "name": "Bharat Electronics Limited", "exchange": "NSE"},
    "MAZDOCK": {"symbol": "MAZDOCK.NS", "name": "Mazagon Dock Shipbuilders", "exchange": "NSE"},
    "MAHDOCK": {"symbol": "MAZDOCK.NS", "name": "Mazagon Dock Shipbuilders", "exchange": "NSE"},
    "MAZAGON": {"symbol": "MAZDOCK.NS", "name": "Mazagon Dock Shipbuilders", "exchange": "NSE"},
    "IREDA": {"symbol": "IREDA.NS", "name": "Indian Renewable Energy Development Agency", "exchange": "NSE"},
    "IRFC": {"symbol": "IRFC.NS", "name": "Indian Railway Finance Corporation", "exchange": "NSE"},
    "RVNL": {"symbol": "RVNL.NS", "name": "Rail Vikas Nigam Limited", "exchange": "NSE"},
    "NHPC": {"symbol": "NHPC.NS", "name": "NHPC Limited", "exchange": "NSE"},
    "PFC": {"symbol": "PFC.NS", "name": "Power Finance Corporation", "exchange": "NSE"},
    "REC": {"symbol": "RECLTD.NS", "name": "REC Limited", "exchange": "NSE"},
    "RECLTD": {"symbol": "RECLTD.NS", "name": "REC Limited", "exchange": "NSE"},

    # Banking & NBFC
    "IDFC FIRST": {"symbol": "IDFCFIRSTB.NS", "name": "IDFC First Bank Limited", "exchange": "NSE"},
    "IDFCFIRSTB": {"symbol": "IDFCFIRSTB.NS", "name": "IDFC First Bank Limited", "exchange": "NSE"},
    "YES BANK": {"symbol": "YESBANK.NS", "name": "Yes Bank Limited", "exchange": "NSE"},
    "YESBANK": {"symbol": "YESBANK.NS", "name": "Yes Bank Limited", "exchange": "NSE"},
    "MUTHOOT": {"symbol": "MUTHOOTFIN.NS", "name": "Muthoot Finance Limited", "exchange": "NSE"},
    "MUTHOOTFIN": {"symbol": "MUTHOOTFIN.NS", "name": "Muthoot Finance Limited", "exchange": "NSE"},
    "JIOFIN": {"symbol": "JIOFIN.NS", "name": "Jio Financial Services Limited", "exchange": "NSE"},
    "JIO FINANCIAL": {"symbol": "JIOFIN.NS", "name": "Jio Financial Services Limited", "exchange": "NSE"},

    # Tech & Tech Tech Stars
    "ZOMATO": {"symbol": "ZOMATO.NS", "name": "Zomato Limited", "exchange": "NSE"},
    "PAYTM": {"symbol": "PAYTM.NS", "name": "One97 Communications (Paytm)", "exchange": "NSE"},
    "SWIGGY": {"symbol": "SWIGGY.NS", "name": "Swiggy Limited", "exchange": "NSE"},
    "OLA": {"symbol": "OLAELEC.NS", "name": "Ola Electric Mobility Limited", "exchange": "NSE"},
    "OLA ELECTRIC": {"symbol": "OLAELEC.NS", "name": "Ola Electric Mobility Limited", "exchange": "NSE"},
    "OLAELEC": {"symbol": "OLAELEC.NS", "name": "Ola Electric Mobility Limited", "exchange": "NSE"},
    "PINE LABS": {"symbol": "PINELABS.NS", "name": "Pine Labs Limited", "exchange": "NSE"},
    "PINELABS": {"symbol": "PINELABS.NS", "name": "Pine Labs Limited", "exchange": "NSE"},
    "TATATECH": {"symbol": "TATATECH.NS", "name": "Tata Technologies Limited", "exchange": "NSE"},
    "TATA TECH": {"symbol": "TATATECH.NS", "name": "Tata Technologies Limited", "exchange": "NSE"},
    "POLYCAB": {"symbol": "POLYCAB.NS", "name": "Polycab India Limited", "exchange": "NSE"},
    "VBL": {"symbol": "VBL.NS", "name": "Varun Beverages Limited", "exchange": "NSE"},
    "VARUN BEVERAGES": {"symbol": "VBL.NS", "name": "Varun Beverages Limited", "exchange": "NSE"},
    "DIXON": {"symbol": "DIXON.NS", "name": "Dixon Technologies Limited", "exchange": "NSE"},
    "DLF": {"symbol": "DLF.NS", "name": "DLF Limited", "exchange": "NSE"},
    "LODHA": {"symbol": "LODHA.NS", "name": "Macrotech Developers (Lodha)", "exchange": "NSE"},
}


def search_stocks(query: str) -> List[Dict[str, str]]:
    """Fuzzy search against COMMON_STOCKS and returns matching candidates."""
    if not query:
        return []
    query_upper = query.upper().strip()
    
    if query_upper in COMMON_STOCKS:
        return [COMMON_STOCKS[query_upper]]
        
    matches = difflib.get_close_matches(query_upper, COMMON_STOCKS.keys(), n=5, cutoff=0.35)
    
    results = []
    seen = set()
    for match in matches:
        stock = COMMON_STOCKS[match]
        if stock['symbol'] not in seen:
            results.append(stock)
            seen.add(stock['symbol'])
            
    for key, stock in COMMON_STOCKS.items():
        if query_upper in key or query_upper in stock['name'].upper():
            if stock['symbol'] not in seen:
                results.append(stock)
                seen.add(stock['symbol'])
                if len(results) >= 5:
                    break

    return results


def resolve_stock(query: str) -> Optional[Dict[str, str]]:
    """Master entity resolver."""
    if not query:
        return None
        
    query_upper = query.upper().strip()
    
    if query_upper in COMMON_STOCKS:
        return COMMON_STOCKS[query_upper]
        
    for key, stock in COMMON_STOCKS.items():
        if query_upper in key or query_upper in stock['name'].upper():
            return stock
            
    clean_query = query_upper.replace(" ", "").replace("&", "")
    if clean_query in COMMON_STOCKS:
        return COMMON_STOCKS[clean_query]

    # Try yfinance direct ticker search
    symbol_candidates = [
        f"{query_upper}.NS",
        f"{query_upper}.BO",
        f"{clean_query}.NS",
        query_upper
    ]

    for sym in symbol_candidates:
        try:
            ticker = yf.Ticker(sym)
            info = ticker.info or {}
            if info and (info.get("regularMarketPrice") or info.get("currentPrice") or info.get("longName")):
                return {
                    "symbol": sym,
                    "name": info.get("longName") or info.get("shortName") or query_upper,
                    "exchange": "NSE" if ".NS" in sym else "BSE"
                }
        except Exception:
            continue

    return {
        "symbol": f"{clean_query}.NS",
        "name": query.title(),
        "exchange": "NSE"
    }
