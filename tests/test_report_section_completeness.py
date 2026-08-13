"""
Regression Test: Report Completeness Validator
Ensures section completeness is verified before claiming complete 26-section research report.
"""

from analysis.report_completeness_validator import ReportCompletenessValidator


def test_completeness_validator():
    validator = ReportCompletenessValidator()
    
    # A sparse dossier must not receive an invented +13 section credit.
    sparse_dossier = {
        "decision_support": {"tip_check": {"rows": []}, "research_status": "UNKNOWN"},
        "modules": {
            "company_snapshot": {"name": "ONGC"},
            "computed_metrics": {"valuation": {}, "profitability": {}, "growth": {}, "debt_metrics": {}, "cash_flow_quality": {}},
            "red_flags": [],
            "dividends": [],
            "source_tracking": {"claims": []}
        }
    }

    res = validator.validate_completeness(sparse_dossier)
    assert res["completed_count"] < 15
    assert res["completed_count"] + res["missing_count"] == 26
    assert "badge_text" in res

    # 2. Empty dossier test
    empty_dossier = {"modules": {}}
    res_empty = validator.validate_completeness(empty_dossier)
    assert "unavailable" in res_empty["badge_text"] or res_empty["completed_count"] < 26

    print("TEST REPORT SECTION COMPLETENESS PASSED!")


if __name__ == "__main__":
    test_completeness_validator()
