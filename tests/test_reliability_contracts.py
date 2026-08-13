"""High-risk reliability regressions independent of live market data."""

from analysis.decision_engine import DecisionEngine
from analysis.financial_calculator import aggregate_dividends_by_financial_year, calculate_all_metrics
from analysis.metric_schema import latest_statement, metric
from analysis.report_consistency_validator import ReportConsistencyValidator
from core.entity_resolver import resolve_stock
from data.sector_templates import classify_company_type


def test_latest_period_selection_and_scope_isolation():
    records = [
        {"period_end": "2026-06-30", "statement_scope": "CONSOLIDATED"},
        {"period_end": "2026-03-31", "statement_scope": "STANDALONE"},
        {"period_end": "2025-12-31", "statement_scope": "CONSOLIDATED"},
    ]
    assert latest_statement(records, "CONSOLIDATED")["period_end"] == "2026-06-30"
    assert latest_statement(records, "STANDALONE")["period_end"] == "2026-03-31"


def test_dividend_events_aggregate_to_financial_year_end_label():
    result = aggregate_dividends_by_financial_year([
        {"Date": "2025-11-15", "amount": 6.0},
        {"Date": "2026-02-10", "amount": 4.0},
    ])
    assert result["fy_dividends"]["FY2026"] == 10.0
    assert result["num_years_paid"] <= 5


def test_oil_gas_ep_never_gets_low_pe_only_attractive_label():
    engine = DecisionEngine()
    metrics = {
        "financial_summary": {"revenue": metric(100, "100 Cr"), "net_profit": metric(10, "10 Cr")},
        "debt_metrics": {"debt_to_equity": metric(0.2, "0.20x")},
        "cash_flow_quality": {"cfo_to_pat": metric(1.0, "1.00x")},
        "valuation": {"pe_ratio": metric(6.0, "6.00")},
    }
    result = engine.build({}, "OIL_GAS_E&P", metrics, {}, [], [], [])
    assert result["valuation"]["status"] != "ATTRACTIVE"
    assert result["valuation"]["status"] == "CYCLE_SENSITIVE"


def test_representative_company_classifications():
    expected = {
        "ONGC": "OIL_GAS_E&P", "OIL": "OIL_GAS_E&P", "RELIANCE": "OIL_GAS_INTEGRATED",
        "IOC": "REFINING_MARKETING", "BPCL": "REFINING_MARKETING", "GAIL": "GAS_TRANSMISSION",
        "PNB": "BANK", "MAHABANK": "BANK", "BAJFINANCE": "NBFC", "HDFCLIFE": "INSURANCE",
        "SUZLON": "WIND_EQUIPMENT", "TMPV": "AUTO", "INFY": "IT", "SUNPHARMA": "PHARMA", "HAL": "DEFENCE",
    }
    for symbol, company_type in expected.items():
        assert classify_company_type(symbol=symbol) == company_type


def test_representative_company_resolution():
    expected_symbols = {
        "ONGC": "ONGC.NS", "OIL": "OIL.NS", "RELIANCE": "RELIANCE.NS", "IOC": "IOC.NS", "BPCL": "BPCL.NS",
        "GAIL": "GAIL.NS", "PNB": "PNB.NS", "MAHABANK": "MAHABANK.NS", "BAJFINANCE": "BAJFINANCE.NS",
        "HDFCLIFE": "HDFCLIFE.NS", "SUZLON": "SUZLON.NS", "TMPV": "TMPV.NS", "INFY": "INFY.NS",
        "SUNPHARMA": "SUNPHARMA.NS", "HAL": "HAL.NS",
    }
    for query, symbol in expected_symbols.items():
        resolved = resolve_stock(query)
        assert resolved is not None
        assert resolved["symbol"] == symbol


def test_consistency_validator_blocks_duplicate_common_man_payload():
    decision = {
        "company_type": "IT",
        "metric_snapshot": {"pe_ratio": metric(20, "20.0")},
        "research_status": "Research View: Mixed Fundamentals / Verify Further",
    }
    dossier = {
        "company_type": "IT",
        "decision_support": decision,
        "modules": {"computed_metrics": {}, "common_man_report": {"conflicting": True}, "source_tracking": {"summary": {"primary_coverage_pct": 0}}},
    }
    result = ReportConsistencyValidator().validate_dossier_consistency(dossier)
    assert result["status"] == "BLOCKED"
    assert not result["render_allowed"]


def test_canonical_calculator_and_decision_pass_consistency_gate():
    record = {
        "period_end": "2026-06-30", "reporting_period": "latest_quarter", "statement_scope": "UNKNOWN",
        "Total Revenue": 1000000000, "Net Income": 150000000, "Operating Income": 200000000,
    }
    financial_data = {
        "info": {"symbol": "INFY", "trailingPE": 22.0, "priceToBook": 7.0},
        "quarterly_income_stmt": [record],
        "quarterly_balance_sheet": [{"period_end": "2026-06-30", "statement_scope": "UNKNOWN", "Stockholders Equity": 1000000000, "Total Debt": 100000000, "Total Assets": 2000000000, "Current Liabilities": 400000000}],
        "quarterly_cashflow": [{"period_end": "2026-06-30", "statement_scope": "UNKNOWN", "Operating Cash Flow": 175000000, "Capital Expenditure": -25000000}],
        "dividends": [],
    }
    metrics = calculate_all_metrics(financial_data, company_type="IT")
    decision = DecisionEngine().build({"modules": {"raw_data": financial_data}}, "IT", metrics, {}, [], [], [])
    dossier = {
        "company_type": "IT",
        "decision_support": decision,
        "modules": {"raw_data": financial_data, "computed_metrics": metrics, "decision_support": decision, "source_tracking": {"summary": {"primary_coverage_pct": 0}}},
    }
    result = ReportConsistencyValidator().validate_dossier_consistency(dossier)
    assert result["status"] == "CONSISTENT"
    assert result["render_allowed"]
