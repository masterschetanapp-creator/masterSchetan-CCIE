from data.sector_templates import classify_company_type

def test_company_classification():
    assert classify_company_type("", "", "Punjab National Bank", "PNB.NS") == "BANK"
    assert classify_company_type("", "", "Bank of Maharashtra", "MAHABANK.NS") == "BANK"
    assert classify_company_type("", "", "State Bank of India", "SBIN.NS") == "BANK"
    assert classify_company_type("", "", "Bajaj Finance Limited", "BAJFINANCE.NS") == "NBFC"
    assert classify_company_type("", "", "HDFC Life Insurance", "HDFCLIFE.NS") == "INSURANCE"
    assert classify_company_type("", "", "Suzlon Energy Limited", "SUZLON.NS") == "WIND_EQUIPMENT"
    assert classify_company_type("", "", "Tata Motors Passenger Vehicles", "TMPV.NS") == "AUTO"
    assert classify_company_type("", "", "Tata Motors Commercial Vehicles", "TMCV.NS") == "AUTO"
    assert classify_company_type("", "", "Infosys Limited", "INFY.NS") == "IT"
    assert classify_company_type("", "", "Sun Pharma", "SUNPHARMA.NS") == "PHARMA"

if __name__ == "__main__":
    test_company_classification()
    print("test_company_classification PASSED")
