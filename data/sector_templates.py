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

def get_sector_template(sector_key: str) -> dict:
    """Return the sector template for the given sector key."""
    if not sector_key:
        return {}
        
    sector_key = sector_key.lower().replace(" ", "_")
    for key, template in SECTOR_METRICS.items():
        if key in sector_key or sector_key in key:
            return template
            
    return {}
