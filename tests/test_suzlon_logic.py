from data.sector_templates import classify_company_type, get_sector_template
from analysis.decision_engine import DecisionEngine

def test_suzlon_classification_and_metrics():
    c_type = classify_company_type("", "", "Suzlon Energy Limited", "SUZLON.NS")
    assert c_type == "WIND_EQUIPMENT"
    
    template = get_sector_template("WIND_EQUIPMENT")
    assert "Order Book (MW)" in template["metrics"]
    
    engine = DecisionEngine()
    result = engine.build(
        dossier={"company_name": "Suzlon Energy", "symbol": "SUZLON.NS"},
        company_type="WIND_EQUIPMENT",
        computed_metrics={},
        evidence_summary={},
        red_flags=[],
        dividends=[],
        news=[]
    )
    assert result["company_type"] == "WIND_EQUIPMENT"
    assert any("order" in item.lower() for item in result["watch_next"])

if __name__ == "__main__":
    test_suzlon_classification_and_metrics()
    print("test_suzlon_logic PASSED")
