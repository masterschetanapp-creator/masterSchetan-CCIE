"""
Regression Test: Oil & Gas E&P Classification & Sector Template Routing
Ensures ONGC and Oil India resolve to OIL_GAS_E&P and NEVER to METALS_MINING, UTILITIES, or GOVERNMENT_UTILITY.
"""

from data.sector_templates import classify_company_type, get_sector_template


def test_ongc_ep_classification():
    # 1. ONGC Parent / Upstream
    ongc_type = classify_company_type(
        sector="Energy",
        industry="Oil & Gas Exploration & Production",
        company_name="Oil and Natural Gas Corporation Limited",
        symbol="ONGC"
    )
    assert ongc_type == "OIL_GAS_E&P", f"Expected OIL_GAS_E&P, got {ongc_type}"
    assert ongc_type not in ["METALS", "UTILITIES", "GOVERNMENT_UTILITY"], f"ONGC must not resolve to {ongc_type}"

    # 2. Oil India Limited
    oil_type = classify_company_type(
        sector="Energy",
        industry="Oil & Gas E&P",
        company_name="Oil India Limited",
        symbol="OIL"
    )
    assert oil_type == "OIL_GAS_E&P", f"Expected OIL_GAS_E&P, got {oil_type}"

    # 3. Reliance Industries
    ril_type = classify_company_type(
        sector="Energy",
        industry="Integrated Oil & Gas",
        company_name="Reliance Industries Limited",
        symbol="RELIANCE"
    )
    assert ril_type == "OIL_GAS_INTEGRATED", f"Expected OIL_GAS_INTEGRATED, got {ril_type}"

    # 4. Indian Oil Corporation
    ioc_type = classify_company_type(
        sector="Energy",
        industry="Refining & Marketing",
        company_name="Indian Oil Corporation Limited",
        symbol="IOC"
    )
    assert ioc_type == "REFINING_MARKETING", f"Expected REFINING_MARKETING, got {ioc_type}"

    # 5. GAIL India
    gail_type = classify_company_type(
        sector="Energy",
        industry="Gas Transmission",
        company_name="GAIL (India) Limited",
        symbol="GAIL"
    )
    assert gail_type == "GAS_TRANSMISSION", f"Expected GAS_TRANSMISSION, got {gail_type}"

    # 6. Template metric check
    tmpl = get_sector_template("OIL_GAS_E&P")
    metrics = tmpl.get("metrics", [])
    assert "Crude Oil Production (MMT)" in metrics
    assert "LME Prices" not in metrics, "Metals metrics must not be present in E&P template!"

    print("TEST SECTOR OIL GAS EP PASSED!")


if __name__ == "__main__":
    test_ongc_ep_classification()
