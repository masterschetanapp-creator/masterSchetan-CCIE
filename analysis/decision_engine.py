"""Canonical, evidence-gated decision support for all CCIE report views."""

from typing import Any, Dict, List, Optional

from analysis.metric_schema import UNKNOWN, first_known, is_unknown


REQUIRED_METRICS: Dict[str, List[str]] = {
    "BANK": ["net_profit", "revenue", "gnpa", "nnpa", "roa", "capital_adequacy", "pb_ratio"],
    "NBFC": ["net_profit", "aum_growth", "gnpa", "nnpa", "roa", "cost_of_borrowing", "pb_ratio"],
    "INSURANCE": ["net_profit", "vnb_margin", "ape_growth", "solvency_ratio", "persistency_ratio", "pb_ratio"],
    "WIND_EQUIPMENT": ["revenue", "net_profit", "order_book", "deliveries", "receivables", "net_debt_or_cash"],
    "OIL_GAS_E&P": ["revenue", "net_profit", "production_volume", "net_realisation", "reserve_replacement_ratio", "debt_to_equity", "cash_flow"],
    "OIL_GAS_INTEGRATED": ["revenue", "net_profit", "refining_margin", "upstream_production", "debt_to_equity", "cash_flow"],
    "REFINING_MARKETING": ["revenue", "net_profit", "refining_margin", "throughput", "marketing_volume", "debt_to_equity"],
    "GAS_TRANSMISSION": ["revenue", "net_profit", "transmission_volume", "tariff_realisation", "debt_to_equity", "cash_flow"],
    "AUTO": ["revenue", "net_profit", "volumes", "operating_margin", "debt_to_equity", "cash_flow"],
    "IT": ["revenue", "net_profit", "operating_margin", "roe", "pe_ratio"],
    "PHARMA": ["revenue", "net_profit", "operating_margin", "roe", "pe_ratio"],
    "DEFENCE": ["revenue", "net_profit", "order_book", "operating_margin", "cash_flow"],
    "METALS": ["revenue", "net_profit", "operating_margin", "debt_to_equity", "pe_ratio"],
    "UNKNOWN": ["revenue", "net_profit", "operating_margin", "debt_to_equity", "roe", "cash_flow", "pe_ratio"],
}


METRIC_PATHS = {
    "revenue": [("financial_summary", "revenue"), ("growth", "revenue_cagr_1y")],
    "net_profit": [("financial_summary", "net_profit"), ("growth", "profit_cagr_1y")],
    "operating_margin": [("profitability", "operating_margin")],
    "roe": [("profitability", "roe")],
    "roa": [("profitability", "roce")],
    "debt_to_equity": [("debt_metrics", "debt_to_equity")],
    "cash_flow": [("cash_flow_quality", "cfo_to_pat"), ("cash_flow_quality", "fcf")],
    "pe_ratio": [("valuation", "pe_ratio")],
    "pb_ratio": [("valuation", "pb_ratio")],
    "gnpa": [("banks", "gnpa"), ("top", "gnpa")],
    "nnpa": [("banks", "nnpa"), ("top", "nnpa")],
    "production_volume": [("sector_operating", "total_boe_production"), ("sector_operating", "crude_oil_production_mmt"), ("sector_operating", "natural_gas_production_bcm")],
    "upstream_production": [("sector_operating", "total_boe_production"), ("sector_operating", "crude_oil_production_mmt")],
    "net_realisation": [("sector_operating", "crude_realisation_usd_per_bbl"), ("sector_operating", "gas_realisation_usd_per_mmbtu")],
    "reserve_replacement_ratio": [("sector_operating", "reserve_replacement_ratio")],
    "refining_margin": [("sector_operating", "gross_refining_margin_usd_per_bbl")],
    "throughput": [("sector_operating", "refinery_throughput_mmt")],
    "marketing_volume": [("sector_operating", "marketing_sales_volume_mmt")],
    "transmission_volume": [("sector_operating", "gas_transmission_volume_mmscmd")],
    "tariff_realisation": [("sector_operating", "tariff_realisation")],
    "order_book": [("sector_operating", "order_book")],
    "deliveries": [("sector_operating", "deliveries")],
    "receivables": [("sector_operating", "receivables")],
    "net_debt_or_cash": [("sector_operating", "net_debt_or_cash")],
    "aum_growth": [("sector_operating", "aum_growth")],
    "cost_of_borrowing": [("sector_operating", "cost_of_borrowing")],
    "vnb_margin": [("sector_operating", "vnb_margin")],
    "ape_growth": [("sector_operating", "ape_growth")],
    "solvency_ratio": [("sector_operating", "solvency_ratio")],
    "persistency_ratio": [("sector_operating", "persistency_ratio")],
    "volumes": [("sector_operating", "volumes")],
    "capital_adequacy": [("sector_operating", "capital_adequacy")],
}


def is_missing(value: Any) -> bool:
    """Compatibility alias for the canonical missing-data policy."""
    return is_unknown(value)


def get_metric(metrics: dict, group: str, key: str) -> Dict[str, Any]:
    if not isinstance(metrics, dict):
        return {}
    candidate = metrics.get(group, {})
    item = candidate.get(key) if isinstance(candidate, dict) else None
    if isinstance(item, dict):
        return item
    item = metrics.get(key)
    return item if isinstance(item, dict) else {}


def get_metric_val(metrics: dict, group: str, key: str) -> Optional[Any]:
    value = get_metric(metrics, group, key).get("value")
    return None if is_unknown(value) else value


def get_metric_fmt(metrics: dict, group: str, key: str, fallback: str = UNKNOWN) -> str:
    item = get_metric(metrics, group, key)
    formatted = item.get("formatted_string")
    if not is_unknown(formatted):
        return str(formatted)
    value = item.get("value")
    return fallback if is_unknown(value) else str(value)


def _metric_available(metrics: dict, key: str) -> bool:
    for group, metric_name in METRIC_PATHS.get(key, []):
        if not is_missing(get_metric_val(metrics, group, metric_name)):
            return True
    return False


def _metric_snapshot(metrics: dict) -> Dict[str, Dict[str, Any]]:
    """Expose canonical metric objects to every renderer and validator."""
    snapshot = {}
    for key, paths in METRIC_PATHS.items():
        for group, metric_name in paths:
            item = get_metric(metrics, group, metric_name)
            if item:
                snapshot[key] = item
                break
    return snapshot


class DecisionEngine:
    """Build a single deterministic object that renderers may display but not alter."""

    def build(
        self,
        dossier: dict,
        company_type: str,
        computed_metrics: dict,
        evidence_summary: dict,
        red_flags: list,
        dividends: list,
        news: list,
    ) -> Dict[str, Any]:
        modules = dossier.get("modules", {}) if isinstance(dossier, dict) else {}
        raw_data = dossier.get("raw_data") or modules.get("raw_data") or {}
        info = raw_data.get("info", {}) if isinstance(raw_data, dict) else {}
        company_name = dossier.get("company_name") or modules.get("company_snapshot", {}).get("name") or info.get("longName") or "Company"

        c_type = str(company_type or UNKNOWN).upper().strip()
        if c_type == "DEFAULT":
            c_type = UNKNOWN
        required = REQUIRED_METRICS.get(c_type, REQUIRED_METRICS[UNKNOWN])
        available = [name for name in required if _metric_available(computed_metrics, name)]
        missing = [name for name in required if name not in available]
        coverage_pct = round((len(available) / len(required)) * 100, 1) if required else 0.0
        coverage_confidence = "HIGH" if coverage_pct >= 80 else "MEDIUM" if coverage_pct >= 60 else "LOW" if coverage_pct >= 40 else "INSUFFICIENT"

        roe = get_metric_val(computed_metrics, "profitability", "roe")
        roe_fmt = get_metric_fmt(computed_metrics, "profitability", "roe")
        revenue_growth = get_metric_val(computed_metrics, "growth", "revenue_cagr_1y")
        revenue_growth_fmt = get_metric_fmt(computed_metrics, "growth", "revenue_cagr_1y")
        profit_growth = get_metric_val(computed_metrics, "growth", "profit_cagr_1y")
        profit_growth_fmt = get_metric_fmt(computed_metrics, "growth", "profit_cagr_1y")
        pe = get_metric_val(computed_metrics, "valuation", "pe_ratio")
        pe_fmt = get_metric_fmt(computed_metrics, "valuation", "pe_ratio")
        pb = get_metric_val(computed_metrics, "valuation", "pb_ratio")
        pb_fmt = get_metric_fmt(computed_metrics, "valuation", "pb_ratio")
        debt_to_equity = get_metric_val(computed_metrics, "debt_metrics", "debt_to_equity")
        debt_to_equity_fmt = get_metric_fmt(computed_metrics, "debt_metrics", "debt_to_equity")
        net_profit = first_known(get_metric_val(computed_metrics, "financial_summary", "net_profit"), info.get("netIncomeToCommon"))
        gnpa = first_known(get_metric_val(computed_metrics, "banks", "gnpa"), get_metric_val(computed_metrics, "top", "gnpa"))
        nnpa = first_known(get_metric_val(computed_metrics, "banks", "nnpa"), get_metric_val(computed_metrics, "top", "nnpa"))
        gnpa_fmt = get_metric_fmt(computed_metrics, "banks", "gnpa") if not is_missing(get_metric_val(computed_metrics, "banks", "gnpa")) else get_metric_fmt(computed_metrics, "top", "gnpa")
        nnpa_fmt = get_metric_fmt(computed_metrics, "banks", "nnpa") if not is_missing(get_metric_val(computed_metrics, "banks", "nnpa")) else get_metric_fmt(computed_metrics, "top", "nnpa")
        danger_flags = [flag for flag in red_flags if isinstance(flag, dict) and str(flag.get("severity", "")).lower() == "danger"]
        warning_flags = [flag for flag in red_flags if isinstance(flag, dict) and str(flag.get("severity", "")).lower() == "warning"]

        if is_missing(net_profit) and is_missing(roe):
            profitability = ("UNKNOWN", "Profitability data is unavailable from the current evidence.", "UNCLEAR - profitability figures are unavailable.")
        elif isinstance(net_profit, (int, float)) and net_profit < 0:
            profitability = ("LOSS_MAKING", "The latest available period reports a net loss.", "NO - the latest available period reports a loss.")
        elif isinstance(roe, (int, float)) and roe > 15:
            profitability = ("PROFITABLE_STRONG", "The business is generating strong profit from shareholder capital.", "YES - profit generation appears strong in the available figures.")
        elif isinstance(roe, (int, float)) and roe > 8:
            profitability = ("PROFITABLE_STABLE", "The business is generating a steady profit from shareholder capital.", "STABLE - available profitability is steady.")
        else:
            profitability = ("PROFITABLE_MODEST", "The available profit data indicates modest returns.", "MIXED - returns in the available figures are modest.")
        prof_status, prof_explanation, business_answer = profitability
        business_status = "STRONG / IMPROVING" if prof_status == "PROFITABLE_STRONG" else "STABLE" if prof_status == "PROFITABLE_STABLE" else "WEAK / LOSS-MAKING" if prof_status == "LOSS_MAKING" else "MIXED" if prof_status == "PROFITABLE_MODEST" else UNKNOWN

        if c_type == "BANK":
            if is_missing(gnpa) and is_missing(nnpa):
                fin_status, fin_explanation, debt_answer = "UNKNOWN", "Bad-loan data is unavailable from the current evidence.", "UNCLEAR - bad-loan data is unavailable."
            elif isinstance(nnpa, (int, float)) and nnpa > 3:
                fin_status, fin_explanation, debt_answer = "WEAK_BAD_LOANS", f"Net bad loans are elevated at {nnpa_fmt}.", f"CONCERN - net bad loans are elevated at {nnpa_fmt}."
            elif isinstance(gnpa, (int, float)) and gnpa > 5:
                fin_status, fin_explanation, debt_answer = "MONITOR_ASSET_QUALITY", f"Gross bad loans are {gnpa_fmt}; asset quality needs monitoring.", f"MONITOR - gross bad loans are {gnpa_fmt}."
            else:
                fin_status, fin_explanation, debt_answer = "COMFORTABLE", "The available bad-loan metrics do not show an immediate concern.", "YES - available bad loans are within the model thresholds."
        elif c_type == "WIND_EQUIPMENT":
            fin_status, fin_explanation, debt_answer = "MONITOR_EXECUTION", "Order execution, collections, and working-capital conversion remain key checks.", "MONITOR - verify order execution and customer collections."
        elif is_missing(debt_to_equity):
            fin_status, fin_explanation, debt_answer = "UNKNOWN", "Debt data is unavailable from the current evidence.", "UNCLEAR - borrowing data is unavailable."
        elif isinstance(debt_to_equity, (int, float)) and debt_to_equity > 2:
            fin_status, fin_explanation, debt_answer = "HIGH_LEVERAGE", f"Borrowing is high relative to shareholder capital ({debt_to_equity_fmt}).", f"CONCERN - borrowing is high ({debt_to_equity_fmt})."
        elif danger_flags:
            fin_status, fin_explanation, debt_answer = "NEEDS_MONITORING", f"{len(danger_flags)} high-severity quantitative flags need review.", f"MONITOR - {len(danger_flags)} high-severity flags need review."
        else:
            fin_status, fin_explanation, debt_answer = "STABLE", f"Borrowing is {debt_to_equity_fmt} relative to shareholder capital.", "STABLE - review the trend in borrowing alongside cash generation."

        if is_missing(revenue_growth) and is_missing(profit_growth):
            growth_status, growth_explanation, growth_answer = "UNKNOWN", "The latest comparable growth figures are unavailable.", "UNCLEAR - comparable growth figures are unavailable."
        elif isinstance(profit_growth, (int, float)) and profit_growth > 15:
            growth_status, growth_explanation, growth_answer = "STRONG", f"Profit grew {profit_growth_fmt} against the comparable period.", f"YES - profit grew {profit_growth_fmt} against the comparable period."
        elif isinstance(profit_growth, (int, float)) and profit_growth > 0:
            growth_status, growth_explanation, growth_answer = "MODERATE", f"Profit grew {profit_growth_fmt} against the comparable period.", f"MODERATE - profit grew {profit_growth_fmt}."
        elif isinstance(profit_growth, (int, float)) and profit_growth < 0:
            growth_status, growth_explanation, growth_answer = "DECLINING", f"Profit fell {profit_growth_fmt} against the comparable period.", f"NO - profit fell {profit_growth_fmt}."
        elif isinstance(revenue_growth, (int, float)) and revenue_growth > 0:
            growth_status, growth_explanation, growth_answer = "REVENUE_GROWING", f"Revenue grew {revenue_growth_fmt} against the comparable period.", f"Revenue grew {revenue_growth_fmt}."
        else:
            growth_status, growth_explanation, growth_answer = "STAGNANT", "The available growth figures show no clear improvement.", "MIXED - no clear growth improvement is visible."

        if coverage_confidence == "INSUFFICIENT":
            valuation_status, valuation_label, valuation_explanation, cheap_answer = "DIFFICULT_TO_JUDGE", "DIFFICULT TO JUDGE RELIABLY", "Sector-critical inputs are unavailable, so valuation cannot be judged reliably.", "UNCLEAR - sector-critical inputs are unavailable."
        elif c_type in {"OIL_GAS_E&P", "OIL_GAS_INTEGRATED"}:
            valuation_status, valuation_label, valuation_explanation, cheap_answer = "CYCLE_SENSITIVE", "CYCLE-SENSITIVE / MULTI-FACTOR REVIEW REQUIRED", "A low earnings multiple alone cannot establish value for an oil and gas producer. Production, realised prices, reserves, project execution, and cash flow must also be verified.", "UNCLEAR - commodity-cycle and operating inputs require verification."
        elif c_type == "BANK":
            if is_missing(pb):
                valuation_status, valuation_label, valuation_explanation, cheap_answer = "UNKNOWN", "UNKNOWN", "Price-to-book data is unavailable.", "UNCLEAR - valuation data is unavailable."
            elif pb > 3:
                valuation_status, valuation_label, valuation_explanation, cheap_answer = "VERY_EXPENSIVE", "VERY EXPENSIVE", f"The bank trades at {pb_fmt} times book value.", f"NO - the available price-to-book multiple is {pb_fmt}."
            elif pb < 1 and isinstance(roe, (int, float)) and roe > 12:
                valuation_status, valuation_label, valuation_explanation, cheap_answer = "ATTRACTIVE", "ATTRACTIVE", f"The bank trades below book value ({pb_fmt}) while the available return measure is strong.", "POTENTIALLY ATTRACTIVE - verify asset quality and capital before drawing a conclusion."
            else:
                valuation_status, valuation_label, valuation_explanation, cheap_answer = "FAIR", "FAIR", f"The available price-to-book multiple is {pb_fmt}.", "FAIR - verify asset quality and profitability trends."
        elif is_missing(pe):
            valuation_status, valuation_label, valuation_explanation, cheap_answer = "UNKNOWN", "UNKNOWN", "Earnings-multiple data is unavailable.", "UNCLEAR - valuation data is unavailable."
        elif pe > 50:
            valuation_status, valuation_label, valuation_explanation, cheap_answer = "VERY_EXPENSIVE", "VERY EXPENSIVE", f"The available earnings multiple is {pe_fmt}.", f"NO - the available earnings multiple is {pe_fmt}."
        elif pe > 28:
            valuation_status, valuation_label, valuation_explanation, cheap_answer = "EXPENSIVE", "EXPENSIVE", f"The available earnings multiple is {pe_fmt}.", f"NO - the available earnings multiple is {pe_fmt}."
        elif pe < 15 and isinstance(roe, (int, float)) and roe > 12:
            valuation_status, valuation_label, valuation_explanation, cheap_answer = "ATTRACTIVE", "ATTRACTIVE", f"The available earnings multiple is {pe_fmt} alongside strong returns.", "POTENTIALLY ATTRACTIVE - verify the quality and durability of earnings."
        else:
            valuation_status, valuation_label, valuation_explanation, cheap_answer = "FAIR", "FAIR", f"The available earnings multiple is {pe_fmt}.", "FAIR - evaluate the multiple against future earnings quality."

        dividend_data = computed_metrics.get("fy_dividends", {}) if isinstance(computed_metrics, dict) else {}
        paid_years = dividend_data.get("num_years_paid") if isinstance(dividend_data, dict) else None
        dividend_label = dividend_data.get("years_paid_str", UNKNOWN) if isinstance(dividend_data, dict) else UNKNOWN
        if isinstance(paid_years, int) and paid_years >= 4:
            dividend_status, dividend_explanation = "REGULAR_RECENTLY", f"Recorded dividends were paid in {dividend_label}."
        elif isinstance(paid_years, int) and paid_years > 0:
            dividend_status, dividend_explanation = "IRREGULAR", f"Recorded dividends were paid in {dividend_label}."
        else:
            dividend_status, dividend_explanation, dividend_label = "UNKNOWN", "Recent dividend history is unavailable.", "UNKNOWN"

        risk_level = "HIGH" if coverage_confidence == "INSUFFICIENT" or danger_flags or prof_status == "LOSS_MAKING" or fin_status in {"HIGH_LEVERAGE", "WEAK_BAD_LOANS"} else "MEDIUM-HIGH" if warning_flags or fin_status.startswith("MONITOR") else "MEDIUM"
        tip_status = "INSUFFICIENT DATA" if coverage_confidence == "INSUFFICIENT" else "MAJOR FUNDAMENTAL CONCERNS" if prof_status == "LOSS_MAKING" or fin_status in {"HIGH_LEVERAGE", "WEAK_BAD_LOANS"} else "HIGH EXPECTATIONS / IMPORTANT RISKS" if danger_flags or valuation_status in {"VERY_EXPENSIVE", "EXPENSIVE"} else "FUNDAMENTALLY SUPPORTED IDEA" if prof_status in {"PROFITABLE_STRONG", "PROFITABLE_STABLE"} and fin_status in {"COMFORTABLE", "STABLE"} else "MIXED FUNDAMENTALS"

        if coverage_confidence == "INSUFFICIENT":
            research_status = "Research View: Insufficient Data / Verification Required"
            bottom_line = f"The current evidence for {company_name} does not support a reliable research judgment. Verify primary filings and sector operating data."
        elif prof_status == "LOSS_MAKING":
            research_status = "Research View: Material Fundamental Concerns"
            bottom_line = f"{company_name} is loss-making in the latest available data. Review the cause, financing needs, and recovery evidence."
        elif business_status == "STRONG / IMPROVING":
            research_status = "Research View: Strong Operations / Price and Evidence Matter"
            bottom_line = f"{company_name} shows strong available operating evidence, but valuation and remaining information gaps still need independent verification."
        else:
            research_status = "Research View: Mixed Fundamentals / Verify Further"
            bottom_line = f"{company_name} has mixed available indicators. Review the missing metrics and next reporting period before forming a view."

        if c_type == "OIL_GAS_E&P":
            watch_next = ["Crude and gas production volume", "Realised price after taxes and levies", "Reserve replacement and new discoveries", "Major development-project execution and capital spending"]
        elif c_type == "WIND_EQUIPMENT":
            watch_next = ["Order-book execution and deliveries", "Customer collections and receivables", "Working-capital movement", "Operating cash generation after capital spending"]
        elif c_type == "BANK":
            watch_next = ["Bad-loan additions and recoveries", "Deposit growth and funding cost", "Capital buffer", "Profitability trend"]
        else:
            watch_next = ["Revenue trend in the next reported period", "Operating profitability", "Cash generated relative to reported profit", "Borrowing and interest burden"]

        positives = []
        if prof_status in {"PROFITABLE_STRONG", "PROFITABLE_STABLE"}:
            positives.append("Available figures show an established profit base.")
        if growth_status in {"STRONG", "MODERATE", "REVENUE_GROWING"}:
            positives.append("Available comparable-period data shows growth.")
        if fin_status in {"COMFORTABLE", "STABLE"}:
            positives.append("Available balance-sheet indicators are not above the model thresholds.")
        if not positives:
            positives.append("No evidence-backed positive can be stated from the current data.")

        risks = []
        if coverage_confidence in {"INSUFFICIENT", "LOW"}:
            risks.append("Important sector and filing inputs are missing or only secondary-sourced.")
        if danger_flags:
            risks.append(f"{len(danger_flags)} high-severity quantitative flags require review.")
        if fin_status in {"HIGH_LEVERAGE", "WEAK_BAD_LOANS", "MONITOR_EXECUTION", "MONITOR_ASSET_QUALITY"}:
            risks.append(fin_explanation)
        if valuation_status in {"VERY_EXPENSIVE", "EXPENSIVE", "CYCLE_SENSITIVE"}:
            risks.append(valuation_explanation)
        if not risks:
            risks.append("Future reported performance can differ from the available secondary data.")

        tip_rows = [
            {"Question": "Does the company make money?", "Simple answer": business_answer},
            {"Question": "Is profit improving?", "Simple answer": growth_answer},
            {"Question": "Is the core business growing?", "Simple answer": f"Revenue changed {revenue_growth_fmt} against the comparable period." if not is_missing(revenue_growth) else "UNCLEAR - comparable revenue data is unavailable."},
            {"Question": "Are bad loans or debt a major current problem?", "Simple answer": debt_answer},
            {"Question": "Does it pay dividends?", "Simple answer": dividend_label},
            {"Question": "Is the share price obviously cheap?", "Simple answer": cheap_answer},
            {"Question": "Main thing to verify next", "Simple answer": watch_next[0]},
        ]

        return {
            "company_type": c_type,
            "business_health": {"status": business_status, "confidence": coverage_confidence, "explanation": prof_explanation},
            "profitability": {"status": prof_status, "confidence": coverage_confidence, "explanation": prof_explanation},
            "financial_health": {"status": fin_status, "confidence": coverage_confidence, "explanation": fin_explanation, "debt_control_text": debt_answer},
            "growth": {"status": growth_status, "confidence": coverage_confidence, "explanation": growth_explanation},
            "valuation": {"status": valuation_status, "verdict_label": valuation_label, "confidence": coverage_confidence, "explanation": valuation_explanation, "cheap_answer": cheap_answer},
            "dividend": {"status": dividend_status, "confidence": coverage_confidence, "explanation": dividend_explanation, "formatted_label": dividend_label},
            "risk_level": risk_level,
            "positives": positives,
            "risks": risks,
            "watch_next": watch_next,
            "tip_check": {"status": tip_status, "rows": tip_rows},
            "bottom_line": bottom_line,
            "research_status": research_status,
            "coverage": {"required_metrics": required, "available_metrics": available, "missing_metrics": missing, "coverage_pct": coverage_pct, "confidence": coverage_confidence},
            "metric_snapshot": _metric_snapshot(computed_metrics),
            "period_context": computed_metrics.get("period_context", {}) if isinstance(computed_metrics, dict) else {},
            "evidence_summary": evidence_summary if isinstance(evidence_summary, dict) else {},
        }
