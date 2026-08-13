from analysis.decision_engine import DecisionEngine

def test_decision_engine_output_schema():
    engine = DecisionEngine()
    result = engine.build(
        dossier={"company_name": "Test Co", "symbol": "TEST"},
        company_type="IT",
        computed_metrics={
            "profitability": {"roe": {"value": 20.0, "formatted_string": "20.0%"}},
            "growth": {"revenue_cagr_1y": {"value": 15.0, "formatted_string": "15.0%"}},
            "valuation": {"pe_ratio": {"value": 20.0, "formatted_string": "20.0x"}},
            "debt_metrics": {"debt_to_equity": {"value": 0.1, "formatted_string": "0.1x"}}
        },
        evidence_summary={"status": "HIGH"},
        red_flags=[],
        dividends=[],
        news=[]
    )
    assert result["company_type"] == "IT"
    assert result["business_health"]["status"] == "STRONG / IMPROVING"
    assert "tip_check" in result
    assert "bottom_line" in result
    assert "coverage" in result

if __name__ == "__main__":
    test_decision_engine_output_schema()
    print("test_decision_engine PASSED")
