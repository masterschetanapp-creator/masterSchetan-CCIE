"""
Regression Test: HTML Formatting & Unescaped Markup Check
Ensures no unindented or unrendered HTML markup (<div style=...) is displayed as raw text blocks in UI views.
"""

from ui.simple_view import _generate_dynamic_shareholding


def test_html_formatting():
    # Verify shareholding generator output format
    rows, interp = _generate_dynamic_shareholding(
        info={"heldPercentInsiders": 0.68, "heldPercentInstitutions": 0.20},
        symbol="ONGC",
        company_name="Oil and Natural Gas Corporation",
        sector_name="Oil & Gas E&P",
        promoter_holding="68.9%",
        institutional_holding="20.0%"
    )

    assert len(rows) >= 4
    assert any(r["Holder Category"] == "Government (Non-Promoter)" for r in rows)
    assert "<div" not in interp, "Raw unescaped HTML <div must not exist inside string interpolation!"

    print("TEST HTML NOT RENDERED AS TEXT PASSED!")


if __name__ == "__main__":
    test_html_formatting()
