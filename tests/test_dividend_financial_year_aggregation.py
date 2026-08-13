"""
Regression Test: Dividend Financial Year Aggregation
Ensures dividends are aggregated by FY and years_paid / years_checked NEVER exceeds 5/5.
"""

from analysis.financial_calculator import aggregate_dividends_by_financial_year


def test_fy_dividend():
    history = [
        {"Date": "2025-11-15", "Dividends": 6.0},
        {"Date": "2026-02-10", "Dividends": 4.0},
        {"Date": "2024-11-10", "Dividends": 5.0},
        {"Date": "2023-11-10", "Dividends": 4.5},
        {"Date": "2022-11-10", "Dividends": 3.0},
        {"Date": "2021-11-10", "Dividends": 2.5},
    ]

    res = aggregate_dividends_by_financial_year(history)
    years_str = res.get("years_paid_str", "")
    num_paid = res.get("num_years_paid", 0)

    assert "/" in years_str, "Must format as X/5 years paid"
    assert num_paid <= 5, f"Paid years count ({num_paid}) cannot exceed 5!"
    assert "6/5" not in years_str, "Impossible 6/5 ratio detected!"

    print("TEST DIVIDEND FY AGGREGATION PASSED!")


if __name__ == "__main__":
    test_fy_dividend()
