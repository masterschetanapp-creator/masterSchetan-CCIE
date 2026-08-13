"""
masterSchetan CCIE — Canonical Decision Support Engine
Single source of truth for all quantitative & qualitative investment judgments.
Renderers consume output from this engine; they NEVER determine conclusions independently.
"""

from typing import Dict, Any, List, Optional

REQUIRED_METRICS: Dict[str, List[str]] = {
    "BANK": ["net_profit", "loan_growth", "deposit_growth", "gnpa", "nnpa", "roa", "capital_adequacy", "pb_ratio"],
    "NBFC": ["net_profit", "aum_growth", "gnpa", "nnpa", "roa", "cost_of_borrowing", "pb_ratio"],
    "INSURANCE": ["net_profit", "vnb_margin", "ape_growth", "solvency_ratio", "persistency_ratio", "pb_ratio"],
    "WIND_EQUIPMENT": ["revenue", "profit", "order_book", "deliveries", "commissioning", "receivables", "inventory", "net_debt_or_cash"],
    "AUTO": ["revenue", "profit", "volumes", "margins", "debt_to_equity", "cash_flow"],
    "IT": ["revenue", "profit", "operating_margin", "roe", "pe_ratio"],
    "PHARMA": ["revenue", "profit", "operating_margin", "roe", "pe_ratio"],
    "METALS": ["revenue", "profit", "operating_margin", "debt_to_equity", "pe_ratio"],
    "DEFAULT": ["revenue", "profit", "operating_margin", "debt_to_equity", "roe", "cfo_to_pat", "pe_ratio"]
}


def is_missing(value: Any) -> bool:
    """Helper to check if a metric value is missing. Returns True if None or empty string or 'N/A'."""
    if value is None:
        return True
    if isinstance(value, str) and value.strip().upper() in ["", "N/A", "NONE", "NULL", "UNAVAILABLE", "NOT VERIFIED"]:
        return True
    return False


def get_metric_val(metrics: dict, group: str, key: str) -> Optional[Any]:
    """Safely extracts numerical float or string value from nested computed_metrics dict."""
    if not isinstance(metrics, dict):
        return None
    grp = metrics.get(group, {})
    if isinstance(grp, dict):
        item = grp.get(key)
        if isinstance(item, dict):
            val = item.get("value")
            return val if val is not None else None
        elif item is not None:
            return item
    # Flat lookup fallback
    item = metrics.get(key)
    if isinstance(item, dict):
        return item.get("value")
    return item if item is not None else None


def get_metric_fmt(metrics: dict, group: str, key: str, fallback: str = "N/A") -> str:
    """Safely extracts formatted string from nested computed_metrics dict."""
    if not isinstance(metrics, dict):
        return fallback
    grp = metrics.get(group, {})
    if isinstance(grp, dict):
        item = grp.get(key)
        if isinstance(item, dict):
            fmt = item.get("formatted_string")
            if fmt and not is_missing(fmt):
                return fmt
            val = item.get("value")
            if val is not None:
                return str(val)
    return fallback


class DecisionEngine:
    """
    Determines all investment conclusions deterministically.
    Produces a single structured DecisionSupport object consumed by all UI renderers and reports.
    """

    def build(self, dossier: dict, company_type: str, computed_metrics: dict, 
              evidence_summary: dict, red_flags: list, dividends: list, news: list) -> Dict[str, Any]:
        
        info = dossier.get("raw_data", {}).get("info", {}) or dossier.get("info", {})
        price_data = dossier.get("raw_data", {}).get("price_data", {}) or dossier.get("price_data", {})
        company_name = dossier.get("company_name", info.get("longName", "Company"))
        symbol = dossier.get("symbol", "STOCK")
        
        c_type = str(company_type or "DEFAULT").upper().strip()
        is_bank = (c_type == "BANK")
        is_nbfc = (c_type == "NBFC")
        is_wind = (c_type == "WIND_EQUIPMENT")
        is_metals = (c_type == "METALS")
        is_ep = (c_type in ["OIL_GAS_E&P", "OIL_GAS_INTEGRATED"])
        is_tech = (c_type in ["IT", "RETAIL"])

        # ── 1. Extract Metrics ──────────────────────────────────────
        m_prof = computed_metrics.get("profitability", {}) if isinstance(computed_metrics.get("profitability"), dict) else {}
        m_grow = computed_metrics.get("growth", {}) if isinstance(computed_metrics.get("growth"), dict) else {}
        m_val = computed_metrics.get("valuation", {}) if isinstance(computed_metrics.get("valuation"), dict) else {}
        m_debt = computed_metrics.get("debt_metrics", {}) if isinstance(computed_metrics.get("debt_metrics"), dict) else {}
        m_cash = computed_metrics.get("cash_flow_quality", {}) if isinstance(computed_metrics.get("cash_flow_quality"), dict) else {}

        roe_val = get_metric_val(computed_metrics, "profitability", "roe")
        op_margin_val = get_metric_val(computed_metrics, "profitability", "operating_margin")
        rev_growth_val = get_metric_val(computed_metrics, "growth", "revenue_cagr_1y")
        pat_growth_val = get_metric_val(computed_metrics, "growth", "profit_cagr_1y")
        pe_val = get_metric_val(computed_metrics, "valuation", "pe_ratio")
        pb_val = get_metric_val(computed_metrics, "valuation", "pb_ratio")
        de_val = get_metric_val(computed_metrics, "debt_metrics", "debt_to_equity")
        cfo_pat_val = get_metric_val(computed_metrics, "cash_flow_quality", "cfo_to_pat")

        roe_fmt = get_metric_fmt(computed_metrics, "profitability", "roe")
        op_fmt = get_metric_fmt(computed_metrics, "profitability", "operating_margin")
        rev_fmt = get_metric_fmt(computed_metrics, "growth", "revenue_cagr_1y")
        pat_fmt = get_metric_fmt(computed_metrics, "growth", "profit_cagr_1y")
        pe_fmt = get_metric_fmt(computed_metrics, "valuation", "pe_ratio")
        pb_fmt = get_metric_fmt(computed_metrics, "valuation", "pb_ratio")
        de_fmt = get_metric_fmt(computed_metrics, "debt_metrics", "debt_to_equity")

        net_income = info.get("netIncomeToCommon") or info.get("trailingEps")
        gnpa_val = get_metric_val(computed_metrics, "banks", "gnpa") or get_metric_val(computed_metrics, "top", "gnpa")
        nnpa_val = get_metric_val(computed_metrics, "banks", "nnpa") or get_metric_val(computed_metrics, "top", "nnpa")
        gnpa_fmt = get_metric_fmt(computed_metrics, "banks", "gnpa")
        nnpa_fmt = get_metric_fmt(computed_metrics, "banks", "nnpa")

        danger_flags = [rf for rf in red_flags if isinstance(rf, dict) and str(rf.get("severity", "")).lower() == "danger"]
        warning_flags = [rf for rf in red_flags if isinstance(rf, dict) and str(rf.get("severity", "")).lower() == "warning"]

        # ── 2. Evidence Coverage Gate ──────────────────────────────
        req_keys = REQUIRED_METRICS.get(c_type, REQUIRED_METRICS["DEFAULT"])
        avail_keys = []
        missing_keys = []

        for rk in req_keys:
            if rk == "revenue" and not is_missing(rev_growth_val): avail_keys.append(rk)
            elif rk == "profit" and (net_income is not None or not is_missing(pat_growth_val)): avail_keys.append(rk)
            elif rk in ["operating_margin", "margins"] and not is_missing(op_margin_val): avail_keys.append(rk)
            elif rk == "roe" and not is_missing(roe_val): avail_keys.append(rk)
            elif rk == "debt_to_equity" and not is_missing(de_val): avail_keys.append(rk)
            elif rk == "pe_ratio" and not is_missing(pe_val): avail_keys.append(rk)
            elif rk == "pb_ratio" and not is_missing(pb_val): avail_keys.append(rk)
            elif rk == "cfo_to_pat" and not is_missing(cfo_pat_val): avail_keys.append(rk)
            elif rk == "gnpa" and not is_missing(gnpa_val): avail_keys.append(rk)
            elif rk == "nnpa" and not is_missing(nnpa_val): avail_keys.append(rk)
            elif rk == "roa" and not is_missing(roe_val): avail_keys.append(rk)
            else: missing_keys.append(rk)

        coverage_pct = round((len(avail_keys) / len(req_keys)) * 100, 1) if req_keys else 0.0
        if coverage_pct >= 80.0:
            coverage_confidence = "HIGH"
        elif coverage_pct >= 60.0:
            coverage_confidence = "MEDIUM"
        elif coverage_pct >= 40.0:
            coverage_confidence = "LOW"
        else:
            coverage_confidence = "INSUFFICIENT"

        # ── 3. Tri-State Profitability & Business Health ────────────
        if is_missing(net_income) and is_missing(roe_val):
            prof_status = "UNKNOWN"
            prof_expl = "Profitability data could not be verified from available disclosures."
            biz_status = "UNKNOWN"
            biz_doing_well = "UNCLEAR - Profitability disclosures unavailable."
        elif net_income is not None and isinstance(net_income, (int, float)) and net_income < 0:
            prof_status = "LOSS_MAKING"
            prof_expl = f"{company_name} is currently reporting a net loss."
            biz_status = "WEAK / LOSS-MAKING"
            biz_doing_well = f"NO - {company_name} is currently loss-making."
        elif roe_val is not None and roe_val > 15:
            prof_status = "PROFITABLE_STRONG"
            prof_expl = f"Strong capital efficiency ({roe_fmt} ROE)."
            biz_status = "STRONG / IMPROVING"
            biz_doing_well = f"YES - Operating performance and ROE ({roe_fmt}) are strong."
        elif roe_val is not None and roe_val > 8:
            prof_status = "PROFITABLE_STABLE"
            prof_expl = f"Steady operating returns ({roe_fmt} ROE)."
            biz_status = "STABLE"
            biz_doing_well = f"STABLE - Operating performance is steady with {roe_fmt} ROE."
        else:
            prof_status = "PROFITABLE_MODEST"
            prof_expl = f"Operating returns are modest ({roe_fmt} ROE)."
            biz_status = "MIXED"
            biz_doing_well = f"MIXED - Operating returns are modest ({roe_fmt} ROE)."

        # ── 4. Tri-State Financial & Solvency Health ────────────────
        if is_bank:
            if is_missing(gnpa_val) and is_missing(nnpa_val):
                fin_status = "UNKNOWN"
                fin_expl = "Asset-quality disclosures (GNPA/NNPA) could not be verified from available market data."
                debt_control_str = "UNCLEAR - Asset-quality data (GNPA/NNPA) could not be verified."
            elif nnpa_val is not None and nnpa_val > 3.0:
                fin_status = "WEAK_BAD_LOANS"
                fin_expl = f"Net Bad Loans (NNPA) elevated at {nnpa_fmt}."
                debt_control_str = f"NO / CONCERN - Net Bad Loans (NNPA) elevated at {nnpa_fmt}."
            elif gnpa_val is not None and gnpa_val > 5.0:
                fin_status = "MONITOR_ASSET_QUALITY"
                fin_expl = f"Gross Bad Loans (GNPA) at {gnpa_fmt} (NNPA: {nnpa_fmt})."
                debt_control_str = f"MONITOR - Gross Bad Loans (GNPA) at {gnpa_fmt}."
            elif danger_flags:
                fin_status = "NEEDS_MONITORING"
                fin_expl = f"{len(danger_flags)} high-severity forensic flags detected."
                debt_control_str = f"MONITOR - {len(danger_flags)} danger flags detected."
            else:
                fin_status = "COMFORTABLE"
                fin_expl = f"Bad loans under control (GNPA: {gnpa_fmt}, NNPA: {nnpa_fmt}). Capital position adequate."
                debt_control_str = f"YES - Bad loans under control (GNPA: {gnpa_fmt}, NNPA: {nnpa_fmt})."

        elif is_wind:
            fin_status = "MONITOR_EXECUTION"
            fin_expl = "Order execution, delivery trajectory, O&M cash flows, and working capital intensity require monitoring."
            debt_control_str = "MONITOR - Evaluate order book execution velocity and receivables."

        else:
            if is_missing(de_val):
                fin_status = "UNKNOWN"
                fin_expl = "Borrowing and debt metrics could not be verified."
                debt_control_str = "UNCLEAR - Debt disclosures unavailable."
            elif de_val > 2.0:
                fin_status = "HIGH_LEVERAGE"
                fin_expl = f"Debt-to-Equity is elevated ({de_fmt})."
                debt_control_str = f"NO / HIGH RISK - Debt-to-Equity elevated ({de_fmt})."
            elif danger_flags:
                fin_status = "NEEDS_MONITORING"
                fin_expl = f"{len(danger_flags)} danger flags detected."
                debt_control_str = f"MONITOR - {len(danger_flags)} danger flags detected."
            elif de_val < 0.5 and not red_flags:
                fin_status = "COMFORTABLE"
                fin_expl = f"Borrowing is low ({de_fmt}) and financial position is healthy."
                debt_control_str = f"YES - Borrowing low ({de_fmt}), comfortable balance sheet."
            else:
                fin_status = "STABLE"
                fin_expl = f"Debt to Equity is {de_fmt}."
                debt_control_str = f"STABLE - Debt to Equity is {de_fmt}."

        # ── 5. Tri-State Growth Status ──────────────────────────────
        if is_missing(rev_growth_val) and is_missing(pat_growth_val):
            growth_status = "UNKNOWN"
            growth_expl = "Growth metrics could not be verified from available disclosures."
            profit_growing_str = "Check P&L filings for YoY profit growth."
        elif pat_growth_val is not None and pat_growth_val > 15:
            growth_status = "STRONG"
            growth_expl = f"Net profit expanded {pat_fmt} YoY."
            profit_growing_str = f"YES - 1Y Net Profit expanded {pat_fmt} YoY."
        elif pat_growth_val is not None and pat_growth_val > 0:
            growth_status = "MODERATE"
            growth_expl = f"Net profit grew {pat_fmt} YoY."
            profit_growing_str = f"MODERATE - 1Y Net Profit grew {pat_fmt} YoY."
        elif pat_growth_val is not None and pat_growth_val < 0:
            growth_status = "DECLINING"
            growth_expl = f"Net profit contracted {pat_fmt} YoY."
            profit_growing_str = f"NO - 1Y Net Profit contracted {pat_fmt} YoY."
        elif rev_growth_val is not None and rev_growth_val > 0:
            growth_status = "REVENUE_GROWING"
            growth_expl = f"Revenue expanded {rev_fmt} YoY."
            profit_growing_str = f"1Y Revenue grew {rev_fmt} YoY."
        else:
            growth_status = "STAGNANT"
            growth_expl = "Growth trajectory requires close quarterly monitoring."
            profit_growing_str = "Growth trajectory requires quarterly monitoring."

        # ── 6. Tri-State Valuation Engine (Coverage Gated) ─────────
        if coverage_confidence == "INSUFFICIENT" or (is_bank and (is_missing(gnpa_val) or is_missing(nnpa_val))):
            val_status = "DIFFICULT_TO_JUDGE"
            val_verdict = "⚪ DIFFICULT TO JUDGE RELIABLY"
            val_expl = "Key required financial disclosures (asset quality/coverage) are unavailable."
            cheap_answer = "UNCLEAR - Insufficient verified data to evaluate valuation reliably."
        elif prof_status == "LOSS_MAKING":
            val_status = "LOSS_MAKING"
            val_verdict = "🔴 VERY EXPENSIVE / LOSS-MAKING"
            val_expl = "Company is reporting net losses; standard valuation multiples are not usable."
            cheap_answer = "NO - Enterprise is currently loss-making."
        elif is_bank:
            if is_missing(pb_val):
                val_status = "UNKNOWN"
                val_verdict = "⚪ DIFFICULT TO JUDGE RELIABLY"
                val_expl = "Price-to-Book multiple is unavailable."
                cheap_answer = "UNCLEAR - Price-to-Book multiple unavailable."
            elif pb_val > 3.0:
                val_status = "VERY_EXPENSIVE"
                val_verdict = "🔴 VERY EXPENSIVE"
                val_expl = f"Bank trades at a high price-to-book multiple of {pb_fmt} net worth."
                cheap_answer = f"NO - Traded at a premium Price-to-Book multiple of {pb_fmt}."
            elif pb_val > 1.8:
                val_status = "EXPENSIVE"
                val_verdict = "🟠 EXPENSIVE"
                val_expl = f"Bank trades at {pb_fmt} Price-to-Book multiple."
                cheap_answer = f"NO - Price-to-Book multiple is {pb_fmt}."
            elif pb_val < 1.0 and (roe_val is not None and roe_val > 12):
                val_status = "ATTRACTIVE"
                val_verdict = "🟢 ATTRACTIVE"
                val_expl = f"Bank trades below book value ({pb_fmt} P/B) while generating {roe_fmt} ROE."
                cheap_answer = f"YES - Attractively valued below book value ({pb_fmt} P/B)."
            else:
                val_status = "FAIR"
                val_verdict = "🟡 FAIR"
                val_expl = f"Bank trades at a reasonable P/B multiple of {pb_fmt}."
                cheap_answer = f"FAIR - Priced at {pb_fmt} P/B."
        elif is_metals:
            if is_missing(pe_val):
                val_status = "UNKNOWN"
                val_verdict = "⚪ UNKNOWN"
                val_expl = "Valuation multiple unavailable."
                cheap_answer = "UNCLEAR - Valuation metrics unavailable."
            elif pe_val < 10:
                val_status = "CYCLICAL_PEAK_WARNING"
                val_verdict = "🟡 LOW P/E (CYCLICAL PEAK WARNING)"
                val_expl = f"Metals company trades at low P/E ({pe_fmt}). Low P/E in cyclical commodities can occur near peak earnings."
                cheap_answer = f"CAUTION - Low P/E of {pe_fmt} may reflect peak cyclical earnings."
            else:
                val_status = "FAIR"
                val_verdict = "🟡 FAIR"
                val_expl = f"Trades at {pe_fmt} P/E multiple."
                cheap_answer = f"FAIR - Traded at {pe_fmt} P/E."
        else:
            if is_missing(pe_val):
                val_status = "UNKNOWN"
                val_verdict = "⚪ UNKNOWN"
                val_expl = "P/E ratio unavailable."
                cheap_answer = "UNCLEAR - Valuation metrics unavailable."
            elif pe_val > 50:
                val_status = "VERY_EXPENSIVE"
                val_verdict = "🔴 VERY EXPENSIVE"
                val_expl = f"Investors are paying a high growth multiple of {pe_fmt} trailing earnings."
                cheap_answer = f"NO - Traded at a high premium multiple of {pe_fmt} P/E."
            elif pe_val > 28:
                val_status = "EXPENSIVE"
                val_verdict = "🟠 EXPENSIVE"
                val_expl = f"Valued at a premium multiple of {pe_fmt} P/E."
                cheap_answer = f"NO - Traded at a premium multiple of {pe_fmt} P/E."
            elif pe_val < 15 and roe_val is not None and roe_val > 12:
                val_status = "ATTRACTIVE"
                val_verdict = "🟢 ATTRACTIVE"
                val_expl = f"Attractively priced at {pe_fmt} P/E relative to operating return ({roe_fmt} ROE)."
                cheap_answer = f"YES - Attractively priced at {pe_fmt} P/E."
            else:
                val_status = "FAIR"
                val_verdict = "🟡 FAIR"
                val_expl = f"Trades at a reasonable P/E multiple of {pe_fmt}."
                cheap_answer = f"FAIR - Reasonably priced at {pe_fmt} P/E."

        # ── 7. Tri-State Dividend Evaluation ─────────────────────────
        div_yield = info.get("dividendYield", 0) or 0
        raw_divs = dividends if isinstance(dividends, list) else []
        if isinstance(raw_divs, dict) and "dividends" in raw_divs:
            raw_divs = raw_divs["dividends"]
        if not isinstance(raw_divs, list):
            raw_divs = []

        years_paid = set()
        for d in raw_divs:
            if isinstance(d, dict):
                dt_str = str(d.get("Date", d.get("date", "")))
                if len(dt_str) >= 4 and dt_str[:4].isdigit():
                    yr = int(dt_str[:4])
                    if yr >= 2021:
                        years_paid.add(yr)

        num_years = len(years_paid)
        if not raw_divs and div_yield == 0:
            div_status = "NO_VERIFIED_DIVIDEND"
            div_expl = "No verified recent dividend payments recorded."
            div_str = "NO VERIFIED RECENT DIVIDEND"
        elif num_years >= 4:
            div_status = "REGULAR_RECENTLY"
            div_expl = f"Regular dividend track record ({num_years}/5 recent years paid)."
            div_str = f"REGULAR RECENTLY ({num_years}/5 years paid)"
        elif num_years >= 1 or div_yield > 0:
            div_status = "IRREGULAR"
            div_expl = f"Irregular dividend payments ({num_years}/5 recent years paid)."
            div_str = f"IRREGULAR ({num_years}/5 years paid)"
        else:
            div_status = "NO_VERIFIED_DIVIDEND"
            div_expl = "No verified recent dividend payments recorded."
            div_str = "NO VERIFIED RECENT DIVIDEND"

        # ── 8. Risk Level & Tip Check ────────────────────────────────
        if danger_flags or prof_status == "LOSS_MAKING" or fin_status in ["HIGH_LEVERAGE", "WEAK_BAD_LOANS"]:
            risk_level = "HIGH"
        elif len(red_flags) > 1 or fin_status in ["MONITOR_ASSET_QUALITY", "NEEDS_MONITORING"]:
            risk_level = "MEDIUM-HIGH"
        else:
            risk_level = "MEDIUM"

        if prof_status == "LOSS_MAKING" or fin_status in ["WEAK_BAD_LOANS", "HIGH_LEVERAGE"]:
            tip_result = "MAJOR FUNDAMENTAL CONCERNS"
        elif danger_flags or fin_status == "NEEDS_MONITORING" or val_status in ["VERY_EXPENSIVE", "EXPENSIVE"]:
            tip_result = "HIGH EXPECTATIONS / IMPORTANT RISKS"
        elif prof_status in ["PROFITABLE_STRONG", "PROFITABLE_STABLE"] and fin_status in ["COMFORTABLE", "STABLE"]:
            tip_result = "FUNDAMENTALLY SUPPORTED IDEA"
        else:
            tip_result = "MIXED FUNDAMENTALS"

        # ── 9. Research Status & Bottom Line ─────────────────────────
        if coverage_confidence == "INSUFFICIENT":
            res_status = "Research View: ⚪ Insufficient Verified Data / Verification Required"
            bottom_line = f"Primary financial disclosures for {company_name} are insufficient to formulate a high-confidence research judgment. Verify filings directly."
        elif "STRONG" in biz_status and val_status == "ATTRACTIVE":
            res_status = "Research View: 🟢 Strong Business / 🟢 Attractive Price"
            bottom_line = f"{company_name} displays strong fundamental efficiency and is currently priced attractively relative to operating returns."
        elif "STRONG" in biz_status and val_status in ["EXPENSIVE", "VERY_EXPENSIVE", "FAIR"]:
            res_status = "Research View: 🟢 Strong Business / 🟡 Price Matters"
            bottom_line = f"There are currently more positives than negatives in {company_name}'s core business. However, a good company is not automatically a bargain at every price."
        elif "WEAK" in biz_status or "LOSS" in biz_status:
            res_status = "Research View: 🔴 Major Fundamental Concerns / 🔴 Avoid Unproven Turnarounds"
            bottom_line = f"{company_name} is currently facing material operational or profitability headwinds. Unproven turnarounds carry elevated risk."
        else:
            res_status = "Research View: 🟡 Mixed Fundamentals / 🟡 Perform Detailed Verification"
            bottom_line = f"{company_name} demonstrates mixed fundamental indicators. Evaluate debt trajectory and margin recovery velocity closely."

        # ── 10. 7-Point Tip Check Rows ──────────────────────────────
        tip_check_rows = [
            {"Question": "Does the company make money?", "Simple answer": biz_doing_well},
            {"Question": "Is profit improving?", "Simple answer": profit_growing_str},
            {"Question": "Is the core business growing?", "Simple answer": f"1Y Revenue growth is {rev_fmt}." if not is_missing(rev_growth_val) else "Check quarterly revenue trajectory."},
            {"Question": "Are bad loans / debt a major current problem?", "Simple answer": debt_control_str},
            {"Question": "Does it pay dividends?", "Simple answer": div_str},
            {"Question": "Is it obviously cheap?", "Simple answer": cheap_answer},
            {"Question": "Main thing people may overlook", "Simple answer": "Valuation multiples and operating cash flow conversion."}
        ]

        # ── 11. Watch Next List ─────────────────────────────────────
        if is_bank:
            watch_next = [
                "Net Interest Margin (NIM spread) trajectory",
                "Gross & Net NPA bad-loan slippages in quarterly filings",
                "Growth in low-cost CASA savings deposits",
                "Capital Adequacy Ratio (CRAR / CET1 buffer)"
            ]
        elif is_wind:
            watch_next = [
                "Quarterly order book execution and MW delivery trajectory",
                "Growth and profitability of recurring O&M service business",
                "Working capital cycle, inventory, and receivables collection",
                "Net debt reduction and cash flow conversion"
            ]
        else:
            watch_next = [
                "Quarterly revenue and customer demand velocity",
                "Operating profit margin trajectory left after expenses",
                "Actual cash flow from operations (CFO) vs reported net profit",
                "Debt service coverage and interest cost burden"
            ]

        # ── 12. Positives & Risks Lists ──────────────────────────────
        positives = []
        if prof_status in ["PROFITABLE_STRONG", "PROFITABLE_STABLE"]:
            positives.append(f"Operating profitability is established ({roe_fmt} ROE).")
        if growth_status in ["STRONG", "MODERATE"]:
            positives.append(f"1Y Net profit trajectory expanded {pat_fmt} YoY.")
        if fin_status == "COMFORTABLE":
            positives.append("Balance sheet financial health is comfortable.")
        if not positives:
            positives.append("Core operational scale and market presence.")

        risks = []
        if prof_status == "LOSS_MAKING":
            risks.append("Company is currently reporting a net loss.")
        if fin_status in ["HIGH_LEVERAGE", "WEAK_BAD_LOANS"]:
            risks.append(f"Financial leverage or bad-loan indicators require monitoring ({fin_expl}).")
        if danger_flags:
            risks.append(f"{len(danger_flags)} high-severity forensic red flags detected.")
        if val_status in ["VERY_EXPENSIVE", "EXPENSIVE"]:
            risks.append(f"Share price trades at a premium valuation multiple ({pe_fmt} P/E / {pb_fmt} P/B).")
        if not risks:
            risks.append("Margin sensitivity to economic cycles and input cost inflation.")

        return {
            "company_type": c_type,
            "business_health": {
                "status": biz_status,
                "confidence": coverage_confidence,
                "explanation": f"Evaluated from operating return ({roe_fmt} ROE) and revenue trajectory ({rev_fmt})."
            },
            "profitability": {
                "status": prof_status,
                "confidence": coverage_confidence,
                "explanation": prof_expl
            },
            "financial_health": {
                "status": fin_status,
                "confidence": coverage_confidence,
                "explanation": fin_expl,
                "debt_control_text": debt_control_str
            },
            "growth": {
                "status": growth_status,
                "confidence": coverage_confidence,
                "explanation": growth_expl
            },
            "valuation": {
                "status": val_status,
                "verdict_label": val_verdict,
                "confidence": coverage_confidence,
                "explanation": val_expl,
                "cheap_answer": cheap_answer
            },
            "dividend": {
                "status": div_status,
                "confidence": coverage_confidence,
                "explanation": div_expl,
                "formatted_label": div_str
            },
            "risk_level": risk_level,
            "positives": positives,
            "risks": risks,
            "watch_next": watch_next,
            "tip_check": {
                "status": tip_result,
                "rows": tip_check_rows
            },
            "bottom_line": bottom_line,
            "research_status": res_status,
            "coverage": {
                "required_metrics": req_keys,
                "available_metrics": avail_keys,
                "missing_metrics": missing_keys,
                "coverage_pct": coverage_pct,
                "confidence": coverage_confidence
            }
        }
