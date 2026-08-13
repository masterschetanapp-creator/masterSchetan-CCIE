from analysis.decision_engine import DecisionEngine

def test_bank_logic():
    engine = DecisionEngine()
    result = engine.build(
        dossier={"company_name": "Punjab National Bank", "symbol": "PNB.NS"},
        company_type="BANK",
        computed_metrics={
            "profitability": {"roe": {"value": 14.0, "formatted_string": "14.0%"}},
            "valuation": {"pb_ratio": {"value": 1.2, "formatted_string": "1.2x"}},
            "top": {
                "gnpa": {"value": 4.5, "formatted_string": "4.5%"},
                "nnpa": {"value": 0.8, "formatted_string": "0.8%"}
            }
        },
        evidence_summary={"status": "HIGH"},
        red_flags=[],
        dividends=[],
        news=[]
    )
    assert result["company_type"] == "BANK"
    assert "bad loans" in result["financial_health"]["debt_control_text"].lower() or "gnpa" in result["financial_health"]["debt_control_text"].lower()

if __name__ == "__main__":
    test_bank_logic()
    print("test_bank_logic PASSED")
