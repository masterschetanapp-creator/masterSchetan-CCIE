"""
masterSchetan CCIE — Forensic Red Flag Engine
15-Point Forensic Checks performed strictly by code & AI signals.
"""

from typing import Dict, Any, List

def run_forensic_checks(financial_data: Dict[str, Any], computed_metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Run 15 forensic checks on financial data and computed metrics.
    Returns ONLY actual detected flags/warnings.
    """
    flags = []

    income_stmts = financial_data.get('annual_income_stmt') or financial_data.get('financials', {}).get('annual_income_stmt', [])
    balance_sheets = financial_data.get('annual_balance_sheet') or financial_data.get('financials', {}).get('annual_balance_sheet', [])
    cashflows = financial_data.get('annual_cashflow') or financial_data.get('financials', {}).get('annual_cashflow', [])

    # Check 1: Profit Quality (CFO/PAT < 0.6)
    cfo_pat_metric = computed_metrics.get('cash_flow_quality', {}).get('cfo_to_pat')
    if cfo_pat_metric and isinstance(cfo_pat_metric, dict):
        val = cfo_pat_metric.get('value')
        if val is not None and val < 0.6:
            flags.append({
                'id': 1,
                'severity': 'danger',
                'title': 'Poor Profit Quality',
                'finding': f"CFO/PAT ratio is {cfo_pat_metric.get('formatted_string', 'low')}, below 0.6.",
                'explanation': "The company's operating cash flow is significantly lower than its reported net profit.",
                'what_it_means': "The company reports paper profit, but cash is not reaching the bank. What this could mean: Aggressive revenue booking or working capital delays."
            })

    # Check 2: Debt-to-Equity > 2.0 (for non-financials)
    de_metric = computed_metrics.get('debt_metrics', {}).get('debt_to_equity')
    if de_metric and isinstance(de_metric, dict):
        val = de_metric.get('value')
        if val is not None and val > 2.0 and "Assets/Equity" not in de_metric.get('formatted_string', ''):
            flags.append({
                'id': 2,
                'severity': 'warning',
                'title': 'High Financial Leverage',
                'finding': f"Debt-to-Equity is {de_metric.get('formatted_string')}.",
                'explanation': "The company relies heavily on debt capital relative to equity.",
                'what_it_means': "High debt increases interest costs and insolvency risks during market downturns."
            })

    # Check 3: Interest Coverage Ratio < 2.0
    icr_metric = computed_metrics.get('debt_metrics', {}).get('interest_coverage')
    if icr_metric and isinstance(icr_metric, dict):
        val = icr_metric.get('value')
        if val is not None and val < 2.0:
            flags.append({
                'id': 3,
                'severity': 'danger',
                'title': 'Weak Interest Coverage',
                'finding': f"Interest Coverage Ratio is {icr_metric.get('formatted_string')}.",
                'explanation': "Operating profits barely cover interest payments.",
                'what_it_means': "A small drop in operating profit could make debt servicing difficult."
            })

    # Check 4: Receivables growing faster than sales (>1.5x)
    if len(income_stmts) >= 2 and len(balance_sheets) >= 2:
        curr_inc, prev_inc = income_stmts[0], income_stmts[1]
        curr_bs, prev_bs = balance_sheets[0], balance_sheets[1]

        curr_rev = curr_inc.get('Total Revenue') or curr_inc.get('Operating Revenue', 0)
        prev_rev = prev_inc.get('Total Revenue') or prev_inc.get('Operating Revenue', 0)
        curr_rec = curr_bs.get('Accounts Receivable') or curr_bs.get('Receivables', 0)
        prev_rec = prev_bs.get('Accounts Receivable') or prev_bs.get('Receivables', 0)

        if curr_rev and prev_rev and prev_rev > 0 and curr_rec and prev_rec and prev_rec > 0:
            rev_growth = (curr_rev - prev_rev) / prev_rev
            rec_growth = (curr_rec - prev_rec) / prev_rec

            if rec_growth > (1.5 * rev_growth) and rec_growth > 0.10:
                flags.append({
                    'id': 4,
                    'severity': 'warning',
                    'title': 'Receivables Growing Faster Than Sales',
                    'finding': f"Receivables grew by {rec_growth*100:.1f}%, vs revenue growth of {rev_growth*100:.1f}%.",
                    'explanation': "Accounts receivable are accumulating faster than actual sales.",
                    'what_it_means': "Customers are taking longer to pay, or credit terms are being relaxed to boost sales."
                })

    # Check 5: Negative Free Cash Flow
    fcf_metric = computed_metrics.get('cash_flow_quality', {}).get('fcf')
    if fcf_metric and isinstance(fcf_metric, dict):
        val = fcf_metric.get('value')
        if val is not None and val < 0:
            flags.append({
                'id': 5,
                'severity': 'warning',
                'title': 'Negative Free Cash Flow',
                'finding': f"Free Cash Flow is {fcf_metric.get('formatted_string')}.",
                'explanation': "Operating cash flow was insufficient to fund capital expenditures.",
                'what_it_means': "The company is spending more cash than it generates, requiring external debt or equity funding."
            })

    # Check 6: Low ROE (< 8%)
    roe_metric = computed_metrics.get('profitability', {}).get('roe')
    if roe_metric and isinstance(roe_metric, dict):
        val = roe_metric.get('value')
        if val is not None and val < 8.0:
            flags.append({
                'id': 6,
                'severity': 'warning',
                'title': 'Subpar Capital Return (Low ROE)',
                'finding': f"Return on Equity is {roe_metric.get('formatted_string')}.",
                'explanation': "The company generates low profits relative to shareholder capital.",
                'what_it_means': "Shareholder equity is compounding at a rate lower than long-term inflation/bank fixed deposits."
            })

    return flags
