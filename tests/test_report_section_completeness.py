"""
Regression Test: Report Completeness Validator
Ensures section completeness is verified before claiming complete 26-section research report.
"""

from analysis.report_completeness_validator import ReportCompletenessValidator


def test_completeness_validator():
    validator = ReportCompletenessValidator()
    
    # 1. Full dossier test
    full_dossier = {
        "decision_support": {"tip_check": {}},
        "modules": {
            "company_snapshot": {"name": "ONGC"},
            "strengths_weaknesses": {},
            "computed_metrics": {"valuation": {}, "profitability": {}, "growth": {}, "debt_metrics": {}, "cash_flow_quality": {}},
            "company_profile_narrative": {},
            "holders": {},
            "red_flags": [],
            "dividends": [],
            "source_tracking": {}
        }
    }

    res = validator.validate_completeness(full_dossier)
    assert res["completed_count"] >= 15
    assert "badge_text" in res

    # 2. Empty dossier test
    empty_dossier = {"modules": {}}
    res_empty = validator.validate_completeness(empty_dossier)
    assert "unavailable" in res_empty["badge_text"] or res_empty["completed_count"] < 26

    print("TEST REPORT SECTION COMPLETENESS PASSED!")


if __name__ == "__main__":
    test_completeness_validator()
