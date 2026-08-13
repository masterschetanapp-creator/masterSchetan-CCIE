from analysis.decision_engine import DecisionEngine

def test_missing_profit_is_unknown():
    engine = DecisionEngine()
    result = engine.build(
        dossier={},
        company_type="DEFAULT",
        computed_metrics={},
        evidence_summary={},
        red_flags=[],
        dividends=[],
        news=[]
    )
    assert result["profitability"]["status"] == "UNKNOWN"

def test_missing_nnpa_does_not_make_bank_attractive():
    engine = DecisionEngine()
    result = engine.build(
        dossier={},
        company_type="BANK",
        computed_metrics={"profitability": {"roe": {"value": 18.0, "formatted_string": "18.0%"}}},
        evidence_summary={},
        red_flags=[],
        dividends=[],
        news=[]
    )
    assert result["valuation"]["status"] != "ATTRACTIVE"
    assert result["valuation"]["status"] == "DIFFICULT_TO_JUDGE"

if __name__ == "__main__":
    test_missing_profit_is_unknown()
    test_missing_nnpa_does_not_make_bank_attractive()
    print("test_missing_data PASSED")
