"""
Regression Test: Source Hierarchy & Yfinance Classification
Ensures yfinance data is strictly classified as SECONDARY_MARKET_DATA and NEVER PRIMARY_VERIFIED.
"""

from analysis.source_tracker import SourceTracker


def test_source_hierarchy():
    st = SourceTracker()
    
    # 1. Add claim from yfinance with PRIMARY_VERIFIED attempt
    claim = st.add_claim(
        claim="Market Cap ₹2,50,000 Cr",
        value=250000,
        source="yfinance API",
        source_type="Yahoo Finance Feed",
        verification_status="PRIMARY_VERIFIED"
    )

    assert claim["source_type"] == "SECONDARY_MARKET_DATA", f"Expected SECONDARY_MARKET_DATA, got {claim['source_type']}"
    assert claim["verification_status"] != "PRIMARY_VERIFIED", "yfinance cannot be claimed as PRIMARY_VERIFIED!"

    # 2. Add claim from BSE Filing
    bse_claim = st.add_claim(
        claim="Standalone PAT ₹10,000 Cr",
        value=10000,
        source="BSE Quarterly Result Filing",
        source_type="Regulatory Exchange Filing",
        verification_status="PRIMARY_VERIFIED"
    )

    assert bse_claim["verification_status"] == "PRIMARY_VERIFIED"

    summary = st.get_confidence_summary()
    assert summary["secondary_coverage_pct"] > 0

    print("TEST NO PRIMARY CLAIM FOR YFINANCE PASSED!")


if __name__ == "__main__":
    test_source_hierarchy()
