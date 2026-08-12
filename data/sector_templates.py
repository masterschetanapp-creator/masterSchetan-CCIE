"""
Sector-specific metric definitions for specialized analysis.
"""

SECTOR_METRICS: dict[str, dict] = {
    "banks": {
        "name": "Banking",
        "metrics": ["NIM", "CASA Ratio", "GNPA", "NNPA", "Slippages", "Credit Cost", "CET1", "ROA"],
        "key_questions": [
            "Is asset quality improving?",
            "Is the bank gaining CASA deposits?",
            "Are Net Interest Margins (NIMs) expanding or contracting?",
            "Is credit growth robust?"
        ],
        "analysis_template": "Focus heavily on asset quality (GNPA/NNPA) and margin profile (NIM)."
    },
    "nbfc": {
        "name": "Non-Banking Financial Company (NBFC)",
        "metrics": ["AUM Growth", "NIM", "GNPA", "NNPA", "Cost of Borrowing", "CRAR", "ROA", "ROE"],
        "key_questions": [
            "How is the AUM growth trajectory?",
            "Are borrowing costs well managed?",
            "Is the asset quality holding up?"
        ],
        "analysis_template": "Examine liability management and growth in Assets Under Management (AUM)."
    },
    "insurance": {
        "name": "Insurance",
        "metrics": ["VNB Margin", "APE Growth", "Combined Ratio", "Solvency Ratio", "Persistency Ratio", "AUM"],
        "key_questions": [
            "Is the Value of New Business (VNB) margin expanding?",
            "How are persistency ratios across cohorts?",
            "Are combined ratios (for general insurers) within profitable limits?"
        ],
        "analysis_template": "Evaluate embedded value growth and persistency of premiums."
    },
    "it": {
        "name": "Information Technology",
        "metrics": ["Revenue Growth (CC)", "EBIT Margin", "Attrition Rate", "TCV of Deals", "Client Concentration"],
        "key_questions": [
            "What is the Total Contract Value (TCV) trend?",
            "Are operating margins stable or expanding?",
            "Is attrition cooling off?"
        ],
        "analysis_template": "Assess deal wins, margin resilience, and geographical revenue mix."
    },
    "pharma": {
        "name": "Pharmaceuticals",
        "metrics": ["US Revenue Mix", "R&D % of Sales", "EBITDA Margin", "ANDA Filings/Approvals", "Domestic Growth"],
        "key_questions": [
            "Are there any pending US FDA issues (OAI/WL)?",
            "What is the pipeline of complex generics?",
            "How is the domestic branded business performing?"
        ],
        "analysis_template": "Focus on regulatory compliance, R&D productivity, and US pricing pressure."
    },
    "capital_goods": {
        "name": "Capital Goods / Engineering",
        "metrics": ["Order Book", "Order Inflow Growth", "Execution Rate", "EBITDA Margin", "Working Capital Days"],
        "key_questions": [
            "What is the book-to-bill ratio?",
            "Are margins impacted by raw material inflation?",
            "Is working capital cycle improving?"
        ],
        "analysis_template": "Track order inflows, execution capabilities, and working capital intensity."
    },
    "real_estate": {
        "name": "Real Estate",
        "metrics": ["Pre-sales", "Collections", "Net Debt", "Unsold Inventory", "Operating Cash Flow"],
        "key_questions": [
            "Are pre-sales growing steadily?",
            "Is debt reduction on track?",
            "What is the launch pipeline?"
        ],
        "analysis_template": "Monitor cash flow generation, pre-sales traction, and leverage."
    },
    "fmcg": {
        "name": "Fast-Moving Consumer Goods",
        "metrics": ["Volume Growth", "Gross Margin", "EBITDA Margin", "A&P Spend %", "Rural vs Urban Growth"],
        "key_questions": [
            "Is growth driven by volume or price hikes?",
            "Are input cost benefits being passed on or retained?",
            "How is rural demand trending?"
        ],
        "analysis_template": "Evaluate volume growth trajectory and pricing power."
    },
    "auto": {
        "name": "Automobiles",
        "metrics": ["Wholesales vs Retails", "Market Share", "EBITDA Margin", "EV Penetration", "Average Realization"],
        "key_questions": [
            "How is the EV transition progressing?",
            "Are raw material costs stabilizing?",
            "Is market share increasing in key segments?"
        ],
        "analysis_template": "Analyze volume trends, margin expansion, and electrification strategy."
    },
    "utilities": {
        "name": "Utilities & Power",
        "metrics": ["Regulated Equity", "Plant Availability Factor", "Receivables Days", "Capacity Addition", "Renewable Mix"],
        "key_questions": [
            "What is the pace of renewable capacity addition?",
            "Are receivables from discoms under control?",
            "Is the regulated return on equity stable?"
        ],
        "analysis_template": "Assess transition to renewables and stability of regulated cash flows."
    },
    "metals": {
        "name": "Metals & Mining",
        "metrics": ["LME Prices", "Spreads/Margins per ton", "Net Debt / EBITDA", "Capacity Utilization", "Cost of Production"],
        "key_questions": [
            "How are global metal prices impacting realizations?",
            "Is the company deleveraging?",
            "Are expansion projects on track without cost overruns?"
        ],
        "analysis_template": "Monitor global macro factors, leverage, and cost curve positioning."
    }
}

def classify_sector(sector: str = "", industry: str = "", company_name: str = "", symbol: str = "") -> dict:
    """
    Normalizes sector + industry + company_name + symbol into a canonical company_type,
    mapping to the correct SECTOR_METRICS template.
    Guarantees no silent fallthrough to {} for banks, autos, IT, pharma, power, capital goods, metals, real estate, FMCG.
    """
    s_lower = str(sector or "").lower()
    i_lower = str(industry or "").lower()
    c_lower = str(company_name or "").lower()
    sym_upper = str(symbol or "").upper()
    
    text = f"{s_lower} {i_lower} {c_lower} {sym_upper}"

    # 1. Banking & Finance
    if any(k in text for k in ["bank", "pnb", "sbi", "hdfcbank", "icicibank", "axisbank", "kotakbank", "canbk", "unionbank", "bankbaroda", "indusindbk"]):
        if "nbfc" in text or "housing" in i_lower or "lending" in i_lower:
            return SECTOR_METRICS["nbfc"]
        return SECTOR_METRICS["banks"]
    elif any(k in text for k in ["nbfc", "asset management", "brokerage", "financial services", "chola", "shriram", "muthoot", "bajfinance", "jiofin", "lic"]):
        if "insurance" in i_lower or "life" in i_lower or "general insurance" in i_lower:
            return SECTOR_METRICS["insurance"]
        return SECTOR_METRICS["nbfc"]
    elif "insurance" in text:
        return SECTOR_METRICS["insurance"]

    # 2. Automotive & Transportation
    if any(k in text for k in ["auto", "car", "vehicle", "truck", "motor", "maruti", "tatamotors", "tmpv", "tmcv", "mahindra", "m&m", "bajaj-auto", "eicher", "heromotoco", "tvsmotor", "ashokley"]):
        return SECTOR_METRICS["auto"]

    # 3. IT & Tech
    if any(k in text for k in ["it services", "software", "technology", "tcs", "infosys", "wipro", "hcltech", "techm", "ltim", "persistent", "coforge", "mphasis"]):
        return SECTOR_METRICS["it"]

    # 4. Pharma & Healthcare
    if any(k in text for k in ["pharma", "drug", "biotech", "healthcare", "hospital", "sunpharma", "cipla", "drreddy", "divislab", "lupin", "mankind"]):
        return SECTOR_METRICS["pharma"]

    # 5. Utilities, Power & Renewable Energy
    if any(k in text for k in ["power", "utility", "electric", "renewable", "hydro", "solar", "wind", "sjvn", "tatapower", "ntpc", "nhpc", "powergrid", "suzlon", "ireda"]):
        return SECTOR_METRICS["utilities"]

    # 6. Capital Goods, Defense & EPC
    if any(k in text for k in ["capital goods", "machinery", "engineering", "defense", "shipbuilder", "railway", "bhel", "hal", "bel", "mazdock", "cochinship", "lt", "larsen", "rvnl", "irfc"]):
        return SECTOR_METRICS["capital_goods"]

    # 7. Metals & Mining
    if any(k in text for k in ["metal", "steel", "aluminium", "mining", "copper", "iron", "tatasteel", "jswsteel", "hindalco", "vedanta", "nmdc", "sail"]):
        return SECTOR_METRICS["metals"]

    # 8. Real Estate & Construction
    if any(k in text for k in ["real estate", "realty", "property", "construction", "dlf", "godrejprop", "oberoirealty", "macrotech", "nbcc"]):
        return SECTOR_METRICS["real_estate"]

    # 9. FMCG & Consumer Goods
    if any(k in text for k in ["fmcg", "consumer goods", "packaged food", "personal care", "hul", "itc", "nestle", "britannia", "dabur", "marico", "colpal"]):
        return SECTOR_METRICS["fmcg"]

    # Keyword fallbacks
    for key, template in SECTOR_METRICS.items():
        if key in text:
            return template

    return SECTOR_METRICS["capital_goods"]


def get_sector_template(sector_key: str, industry: str = "", company_name: str = "", symbol: str = "") -> dict:
    """Return the sector template using the full sector classifier."""
    return classify_sector(sector_key, industry, company_name, symbol)
