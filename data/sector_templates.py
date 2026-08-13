from dataclasses import dataclass

@dataclass
class CompanyClassification:
    company_type: str
    sector: str
    industry: str
    confidence: str


SECTOR_METRICS: dict[str, dict] = {
    "unknown": {
        "name": "Unclassified / Evidence Required",
        "metrics": [],
        "key_questions": ["Which regulated sector classification is supported by an exchange filing?"],
        "analysis_template": "Do not apply a sector model until the company classification is verified."
    },
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
    "wind_equipment": {
        "name": "Wind Energy & Renewable Equipment",
        "metrics": ["Order Book (MW)", "Order Intake", "Deliveries (MW)", "Commissioning", "Manufacturing Capacity", "Turbine Platform Mix", "EPC Exposure", "Receivables", "Inventory", "Cash Conversion", "O&M Business"],
        "key_questions": [
            "What is the total order book in MW and megawatt value?",
            "What are the delivery and commissioning velocity trends?",
            "How profitable is the long-term Operations & Maintenance (O&M) service business?",
            "Are working capital, inventory, and receivables well managed?"
        ],
        "analysis_template": "Focus on order execution, delivery trajectory, O&M recurring income, working capital, and net leverage."
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
    },
    "oil_gas_ep": {
        "name": "Oil & Gas Exploration & Production (E&P)",
        "metrics": [
            "Crude Oil Production (MMT)", "Natural Gas Production (BCM)", "Total BOE Production",
            "Crude Realization ($/bbl)", "Gas Realization ($/mmbtu)", "Reserve Replacement Ratio (RRR)",
            "Proven Reserves (2P/1P)", "Lifting Cost ($/bbl)", "Exploration Capex",
            "Development Capex", "Major Discoveries", "Production Guidance", "ONGC Videsh / Overseas E&P",
            "Crude Price Sensitivity", "USD/INR Sensitivity", "Royalty & Cess Impact"
        ],
        "key_questions": [
            "Is domestic crude and natural gas production growing or stabilizing?",
            "What are the net crude ($/bbl) and gas ($/mmbtu) realizations after windfall tax/cess?",
            "Is the Reserve Replacement Ratio (RRR) above 1.0x to sustain long-term reserves?",
            "Are major offshore development projects (e.g. KG-DWN-98/2, Mumbai High) on schedule?",
            "How are overseas E&P subsidiaries (e.g. ONGC Videsh) and refining subsidiaries contributing to consolidated cash flows?"
        ],
        "analysis_template": "Analyze upstream crude/gas production volumes, net realizations, offshore project commissioning, reserve replacement, and government regulatory/cess impact."
    },
    "refining_marketing": {
        "name": "Oil Refining & Petroleum Marketing",
        "metrics": ["Gross Refining Margin (GRM $/bbl)", "Refinery Throughput (MMT)", "Marketing Sales Volume", "Pipeline Throughput", "Petrochemical Margins", "Inventory Realization"],
        "key_questions": [
            "How are Gross Refining Margins (GRMs) trending relative to regional benchmarks?",
            "Are petroleum marketing margins sufficient to cover distribution overheads?",
            "What is the refinery capacity utilization?"
        ],
        "analysis_template": "Evaluate refining margins (GRM $/bbl), crude processing throughput, marketing retail margins, and inventory gains/losses."
    },
    "gas_transmission": {
        "name": "Natural Gas Transmission & Distribution",
        "metrics": ["Gas Transmission Volume (MMSCMD)", "Tariff Realization", "City Gas Distribution (CGD) Volume", "PNG/CNG Mix", "APM Gas Allocation"],
        "key_questions": [
            "What is the daily gas transmission throughput (MMSCMD)?",
            "Are regulatory tariffs per MMBTU stable?",
            "How is CNG and PNG volume growth trending in city gas networks?"
        ],
        "analysis_template": "Focus on pipeline throughput, PNGRB tariff revisions, and city gas volume traction."
    }
}


def classify_company_type(sector: str = "", industry: str = "", company_name: str = "", symbol: str = "") -> str:
    """
    Normalizes sector + industry + company_name + symbol into a single canonical company_type string code.
    Must return one of: "BANK", "NBFC", "INSURANCE", "IT", "PHARMA", "AUTO", "WIND_EQUIPMENT", 
    "OIL_GAS_E&P", "OIL_GAS_INTEGRATED", "REFINING_MARKETING", "GAS_TRANSMISSION", "OILFIELD_SERVICES",
    "CAPITAL_GOODS", "DEFENCE", "RETAIL", "FMCG", "REAL_ESTATE", "METALS", "UTILITIES", "TELECOM", "UNKNOWN".
    """
    s_lower = str(sector or "").lower()
    i_lower = str(industry or "").lower()
    c_lower = str(company_name or "").lower()
    sym_upper = str(symbol or "").upper()
    
    text = f"{s_lower} {i_lower} {c_lower} {sym_upper}"

    # 1. Wind Turbine & Equipment Manufacturing (MUST PRECEDE generic utilities/power)
    if "SUZLON" in sym_upper or "suzlon" in text or "wind turbine" in text or "wind equipment" in text or "wind generator" in text:
        return "WIND_EQUIPMENT"

    # 2. Oil & Gas Sub-Sectors (MUST PRECEDE generic utilities and metals!)
    if any(k in sym_upper for k in ["ONGC", "OIL"]) or \
       any(k in c_lower for k in ["oil and natural gas", "ongc", "oil india"]) or \
       ("exploration" in text and "oil" in text):
        return "OIL_GAS_E&P"

    if "RELIANCE" in sym_upper or "reliance industries" in c_lower:
        return "OIL_GAS_INTEGRATED"

    if any(k in sym_upper for k in ["IOC", "BPCL", "HPCL", "MRPL", "CHENNPETRO"]) or \
       any(k in c_lower for k in ["indian oil", "bharat petroleum", "hindustan petroleum", "mangalor refinery"]):
        return "REFINING_MARKETING"

    if any(k in sym_upper for k in ["GAIL", "GUJGASLTD", "IGL", "MGL", "ATGL"]) or \
       any(k in c_lower for k in ["gail", "indraprastha gas", "mahanagar gas", "gujarat gas", "adani total gas"]) or \
       ("gas transmission" in text or "gas distribution" in text):
        return "GAS_TRANSMISSION"

    # 3. Banking (PSU & Private Banks — PNB, MAHABANK, SBI, HDFC Bank, ICICI, Axis, etc.)
    if any(k in sym_upper for k in ["PNB", "MAHABANK", "SBIN", "HDFCBANK", "ICICIBANK", "AXISBANK", "KOTAKBANK", "CANBK", "UNIONBANK", "BANKBARODA", "INDUSINDBK"]) or \
       any(k in c_lower for k in ["punjab national bank", "bank of maharashtra", "state bank of india", "hdfc bank", "icici bank", "axis bank", "kotak mahindra bank"]) or \
       ("bank" in text and not any(k in text for k in ["nbfc", "housing", "microfinance", "small finance"])):
        return "BANK"

    # 4. NBFC & Financial Services (Bajaj Finance, Chola, Shriram, Jio Financial, etc.)
    if any(k in sym_upper for k in ["BAJFINANCE", "BAJAJFINSV", "CHOLAFIN", "SHRIRAMFIN", "MUTHOOTFIN", "JIOFIN", "M&MFIN", "POONAWALLA"]) or \
       any(k in c_lower for k in ["bajaj finance", "chola", "shriram finance", "muthoot", "jio financial"]) or \
       any(k in text for k in ["nbfc", "non-banking", "housing finance", "asset management", "microfinance", "lending"]):
        return "NBFC"

    # 5. Insurance (HDFC Life, SBI Life, ICICI Pru, LIC, GIC, etc.)
    if any(k in sym_upper for k in ["HDFCLIFE", "SBILIFE", "ICICIPRULI", "LICI", "GICRE", "NIACL"]) or \
       any(k in c_lower for k in ["hdfc life", "sbi life", "life insurance", "general insurance", "lic of india"]) or \
       "insurance" in text:
        return "INSURANCE"

    # 6. Automotive & Vehicles (Tata Motors PV/CV, Maruti, M&M, Bajaj Auto, Eicher, Hero)
    if any(k in sym_upper for k in ["TMPV", "TMCV", "TATAMOTORS", "MARUTI", "M&M", "BAJAJ-AUTO", "EICHERMOT", "HEROMOTOCO", "TVSMOTOR", "ASHOKLEY"]) or \
       any(k in c_lower for k in ["tata motors", "maruti", "mahindra", "bajaj auto", "eicher", "hero motocorp", "ashok leyland"]) or \
       any(k in text for k in ["auto", "vehicle", "automobile", "truck", "motorcycle", "passenger vehicle", "commercial vehicle"]):
        return "AUTO"

    # 7. IT & Technology (Infosys, TCS, Wipro, HCL Tech, Tech Mahindra, LTIM)
    if any(k in sym_upper for k in ["INFY", "TCS", "WIPRO", "HCLTECH", "TECHM", "LTIM", "PERSISTENT", "COFORGE", "MPHASIS"]) or \
       any(k in c_lower for k in ["infosys", "tata consultancy", "wipro", "hcl tech", "tech mahindra"]) or \
       any(k in text for k in ["it services", "software", "technology", "digital services"]):
        return "IT"

    # 8. Pharma & Healthcare (Sun Pharma, Cipla, Dr Reddy's, Divi's, Lupin)
    if any(k in sym_upper for k in ["SUNPHARMA", "CIPLA", "DRREDDY", "DIVISLAB", "LUPIN", "MANKIND", "APOLLOHOSP", "MAXHEALTH"]) or \
       any(k in c_lower for k in ["sun pharma", "cipla", "dr reddy", "divi's", "lupin"]) or \
       any(k in text for k in ["pharma", "pharmaceutical", "drug", "biotech", "healthcare", "hospital"]):
        return "PHARMA"

    # 9. Defense Equipment & Shipbuilding
    if any(k in sym_upper for k in ["HAL", "BEL", "MAZDOCK", "COCHINSHIP", "GRSE", "BDL"]) or \
       any(k in c_lower for k in ["hindustan aeronautics", "bharat electronics", "mazagon", "cochin shipyard"]) or \
       "defense" in text or "defence" in text:
        return "DEFENCE"

    # 10. Capital Goods, Engineering & EPC (L&T, BHEL, Siemens, ABB)
    if any(k in sym_upper for k in ["LT", "BHEL", "SIEMENS", "ABB", "THERMAX", "CGPOWER", "RVNL"]) or \
       any(k in c_lower for k in ["larsen & toubro", "l&t", "bhel", "siemens"]) or \
       any(k in text for k in ["capital goods", "machinery", "engineering", "epc", "heavy equipment"]):
        return "CAPITAL_GOODS"

    # 11. Metals & Mining (Tata Steel, JSW Steel, Hindalco, Vedanta, NMDC, SAIL)
    if any(k in sym_upper for k in ["TATASTEEL", "JSWSTEEL", "HINDALCO", "VEDL", "NMDC", "SAIL", "COALINDIA", "JINDALSTEL"]) or \
       any(k in c_lower for k in ["tata steel", "jsw steel", "hindalco", "vedanta", "nmdc", "sail"]) or \
       any(k in text for k in ["metal", "steel", "aluminium", "copper", "iron ore", "mining"]):
        return "METALS"

    # 12. Real Estate & Realty (DLF, Godrej Prop, Oberoi, Macrotech)
    if any(k in sym_upper for k in ["DLF", "GODREJPROP", "OBEROIRLTY", "LODHA", "MACROTECH", "NBCC", "PRESTIGE"]) or \
       any(k in text for k in ["real estate", "realty", "property", "residential construction"]):
        return "REAL_ESTATE"

    # 13. FMCG & Consumer Goods (HUL, ITC, Nestle, Britannia, Dabur, Marico)
    if any(k in sym_upper for k in ["HINDUNILVR", "ITC", "NESTLEIND", "BRITANNIA", "DABUR", "MARICO", "COLPAL", "TATACONSUM"]) or \
       any(k in c_lower for k in ["hindustan unilever", "itc limited", "nestle", "britannia"]) or \
       any(k in text for k in ["fmcg", "consumer goods", "packaged food", "personal care"]):
        return "FMCG"

    # 14. Retail & E-Commerce (Avenue Supermarts, Trent, Nykaa, Zomato)
    if any(k in sym_upper for k in ["DMART", "TRENT", "NYKAA", "ZOMATO", "SWIGGY"]) or \
       any(k in text for k in ["retail", "supermarket", "e-commerce", "hypermarket"]):
        return "RETAIL"

    # 15. Utilities & Power Generation (NTPC, NHPC, Power Grid, SJVN, Tata Power)
    if any(k in sym_upper for k in ["NTPC", "NHPC", "POWERGRID", "SJVN", "TATAPOWER", "TORNTPOWER", "CESC"]) or \
       any(k in text for k in ["utility", "electric utility", "power generation", "power transmission"]):
        return "UTILITIES"

    # 16. Telecom
    if any(k in sym_upper for k in ["BHARTIARTL", "IDEA", "INDUSTOWERS"]) or "telecom" in text:
        return "TELECOM"

    return "UNKNOWN"


def get_sector_template(company_type: str) -> dict:
    """
    Return the sector template dictionary for a canonical company_type string code.
    Accepts ONLY a canonical string (e.g. 'BANK', 'NBFC', 'WIND_EQUIPMENT', 'OIL_GAS_E&P', etc.).
    """
    c_type = str(company_type or "").upper().strip()
    mapping = {
        "BANK": SECTOR_METRICS["banks"],
        "NBFC": SECTOR_METRICS["nbfc"],
        "INSURANCE": SECTOR_METRICS["insurance"],
        "AUTO": SECTOR_METRICS["auto"],
        "IT": SECTOR_METRICS["it"],
        "PHARMA": SECTOR_METRICS["pharma"],
        "WIND_EQUIPMENT": SECTOR_METRICS["wind_equipment"],
        "OIL_GAS_E&P": SECTOR_METRICS["oil_gas_ep"],
        "OIL_GAS_INTEGRATED": SECTOR_METRICS["oil_gas_ep"],
        "REFINING_MARKETING": SECTOR_METRICS["refining_marketing"],
        "GAS_TRANSMISSION": SECTOR_METRICS["gas_transmission"],
        "CAPITAL_GOODS": SECTOR_METRICS["capital_goods"],
        "DEFENCE": SECTOR_METRICS["capital_goods"],
        "METALS": SECTOR_METRICS["metals"],
        "REAL_ESTATE": SECTOR_METRICS["real_estate"],
        "FMCG": SECTOR_METRICS["fmcg"],
        "UTILITIES": SECTOR_METRICS["utilities"],
        "RETAIL": SECTOR_METRICS["fmcg"],
        "TELECOM": SECTOR_METRICS["it"]
    }
    return mapping.get(c_type, SECTOR_METRICS["unknown"])


def classify_sector(sector: str = "", industry: str = "", company_name: str = "", symbol: str = "") -> dict:
    """Convenience wrapper returning the template dictionary from classification."""
    company_type = classify_company_type(sector, industry, company_name, symbol)
    return get_sector_template(company_type)


def get_company_classification(sector: str = "", industry: str = "", company_name: str = "", symbol: str = "") -> CompanyClassification:
    """Returns a structured CompanyClassification object."""
    c_type = classify_company_type(sector, industry, company_name, symbol)
    conf = "HIGH" if c_type != "UNKNOWN" else "UNKNOWN"
    return CompanyClassification(
        company_type=c_type,
        sector=sector or "Unknown Sector",
        industry=industry or "Unknown Industry",
        confidence=conf
    )
