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

    # Check 7: CWIP Stuffing (Capital Work-in-Progress > 35% Net Block & Negative FCF)
    if balance_sheets and len(balance_sheets) >= 1:
        bs = balance_sheets[0]
        cwip = bs.get('Capital Work In Progress') or bs.get('CWIP', 0)
        net_block = bs.get('Net PPE') or bs.get('Gross PPE', 0)
        fcf_val = computed_metrics.get('cash_flow_quality', {}).get('fcf', {}).get('value')
        
        if cwip and net_block and net_block > 0 and (cwip / net_block) > 0.35 and fcf_val and fcf_val < 0:
            flags.append({
                'id': 7,
                'severity': 'warning',
                'title': 'High CWIP Capitalization Risk',
                'finding': f"Capital Work-In-Progress represents {(cwip/net_block)*100:.1f}% of Net PPE alongside negative FCF.",
                'explanation': "A large portion of capital is locked in unfinished projects while free cash flow remains negative.",
                'what_it_means': "Management may be capitalizing operating expenses into CWIP or projects are experiencing execution delays."
            })

    # Check 8: Promoter Pledge Risk
    info = financial_data.get('info', {})
    pledge_pct = info.get('pledgedShares', 0) or 0
    if isinstance(pledge_pct, (int, float)) and pledge_pct > 10.0:
        severity = 'danger' if pledge_pct > 25.0 else 'warning'
        flags.append({
            'id': 8,
            'severity': severity,
            'title': 'High Promoter Share Pledging',
            'finding': f"Promoter pledged shares stand at {pledge_pct:.1f}%.",
            'explanation': "Promoters have pledged their equity stake as collateral for loans.",
            'what_it_means': "Creates margin call risks. Sudden stock drops can trigger panic selling by lenders."
        })

    # Check 9: Promoter Stake Decline
    insider_pct = info.get('heldPercentInsiders')
    if isinstance(insider_pct, (int, float)) and insider_pct < 0.15 and not any(k in info.get('sector', '') for k in ['Bank', 'Financial']):
        flags.append({
            'id': 9,
            'severity': 'warning',
            'title': 'Low Promoter Holding',
            'finding': f"Promoter/Insider holding is {insider_pct*100:.1f}%.",
            'explanation': "Promoters hold a relatively small equity stake in the enterprise.",
            'what_it_means': "Promoters have less skin in the game, though the company may be professionally managed."
        })

    # Check 10: Revenue-Profit Divergence (Revenue up > 15% but Profit down)
    rev_1y = computed_metrics.get('growth', {}).get('revenue_cagr_1y', {}).get('value')
    pat_1y = computed_metrics.get('growth', {}).get('profit_cagr_1y', {}).get('value')
    if pat_1y is None:
        pat_1y = computed_metrics.get('growth', {}).get('pat_cagr_1y', {}).get('value')
    if rev_1y is not None and pat_1y is not None and rev_1y > 15.0 and pat_1y < 0:
        flags.append({
            'id': 10,
            'severity': 'warning',
            'title': 'Revenue-Profit Growth Divergence',
            'finding': f"Revenue grew {rev_1y:.1f}% YoY but Net Profit declined by {abs(pat_1y):.1f}%.",
            'explanation': "Topline sales expanded, but profits shrank due to margin compression.",
            'what_it_means': "Input cost inflation, price discounting, or rising operating costs are eroding profitability."
        })

    # Check 11: Inventory Accumulation (Sector-Aware)
    if len(income_stmts) >= 2 and len(balance_sheets) >= 2:
        curr_inc, prev_inc = income_stmts[0], income_stmts[1]
        curr_bs, prev_bs = balance_sheets[0], balance_sheets[1]
        curr_rev = curr_inc.get('Total Revenue') or curr_inc.get('Operating Revenue', 0)
        prev_rev = prev_inc.get('Total Revenue') or prev_inc.get('Operating Revenue', 0)
        curr_inv = curr_bs.get('Inventory') or curr_bs.get('Inventories', 0)
        prev_inv = prev_bs.get('Inventory') or prev_bs.get('Inventories', 0)

        if curr_rev and prev_rev and prev_rev > 0 and curr_inv and prev_inv and prev_inv > 0:
            rev_g = (curr_rev - prev_rev) / prev_rev
            inv_g = (curr_inv - prev_inv) / prev_inv
            if inv_g > (1.5 * rev_g) and inv_g > 0.10:
                sec_text = str(info.get('sector', '')).lower() + " " + str(info.get('industry', '')).lower() + " " + str(info.get('symbol', '')).upper()
                if any(k in sec_text for k in ["oil", "gas", "energy", "petroleum", "ongc", "reliance", "ioc", "bpcl", "hpcl"]):
                    flags.append({
                        'id': 11,
                        'severity': 'info',
                        'title': 'Oil & Gas Feedstock / Petroleum Inventory Watch',
                        'finding': f"Inventory value changed by {inv_g*100:.1f}% YoY vs revenue growth of {rev_g*100:.1f}%.",
                        'explanation': "Inventory movements reflect operational crude oil feedstock, petroleum products, and international commodity price dynamics across energy/refining operations.",
                        'what_it_means': "Reflects crude stocking and crude price valuation rather than consumer overproduction. Monitor refining throughput and GRMs."
                    })
                else:
                    flags.append({
                        'id': 11,
                        'severity': 'warning',
                        'title': 'Inventory Accumulation Bloat',
                        'finding': f"Inventory grew {inv_g*100:.1f}% YoY vs revenue growth of {rev_g*100:.1f}%.",
                        'explanation': "Unsold finished goods or raw materials are piling up faster than sales.",
                        'what_it_means': "Signals potential demand slowdown, overproduction, or inventory write-down risk."
                    })

    # Check 12: Contingent Liability Exposure
    cont_liab = info.get('contingentLiabilities', 0)
    net_worth = info.get('bookValue', 0) * info.get('sharesOutstanding', 1)
    if cont_liab and net_worth and net_worth > 0 and (cont_liab / net_worth) > 0.20:
        flags.append({
            'id': 12,
            'severity': 'danger',
            'title': 'High Contingent Liability Exposure',
            'finding': f"Contingent liabilities represent {(cont_liab/net_worth)*100:.1f}% of net worth.",
            'explanation': "The company faces significant off-balance-sheet legal or tax disputes.",
            'what_it_means': "Adverse judicial or tax rulings could directly impact equity net worth."
        })

    # Check 13: Cash Conversion Deterioration
    wc = computed_metrics.get('working_capital', {})
    ccc = wc.get('cash_conversion_cycle', {}).get('value') if isinstance(wc, dict) else None
    if ccc is not None and ccc > 120:
        flags.append({
            'id': 13,
            'severity': 'warning',
            'title': 'Extended Cash Conversion Cycle',
            'finding': f"Cash Conversion Cycle is {ccc:.0f} days.",
            'explanation': "It takes over 120 days to convert working capital investments back into cash.",
            'what_it_means': "Working capital is tied up, increasing reliance on short-term bank borrowings."
        })

    # Check 14: High Dividend Payout Despite Debt
    div_yield = computed_metrics.get('valuation', {}).get('dividend_yield', {}).get('value')
    de_val = computed_metrics.get('debt_metrics', {}).get('debt_to_equity', {}).get('value')
    if div_yield is not None and de_val is not None and div_yield > 4.0 and de_val > 1.5:
        flags.append({
            'id': 14,
            'severity': 'warning',
            'title': 'High Dividend Payout Amid Heavy Leverage',
            'finding': f"Dividend yield is {div_yield:.1f}% while Debt-to-Equity is {de_val:.2f}x.",
            'explanation': "The company distributes large dividends despite carrying elevated debt.",
            'what_it_means': "Cash is being paid out to shareholders instead of de-leveraging the balance sheet."
        })

    # Check 15: Low Asset Turnover Efficiency
    assets = balance_sheets[0].get('Total Assets', 0) if balance_sheets else 0
    rev = income_stmts[0].get('Total Revenue', 0) if income_stmts else 0
    if assets and rev and assets > 0:
        asset_turnover = rev / assets
        if asset_turnover < 0.35 and not any(k in info.get('sector', '') for k in ['Bank', 'Financial', 'Utilities']):
            flags.append({
                'id': 15,
                'severity': 'info',
                'title': 'Low Asset Turnover Efficiency',
                'finding': f"Asset turnover ratio is {asset_turnover:.2f}x.",
                'explanation': "The company generates low revenue relative to total assets.",
                'what_it_means': "Heavy capital block or un-utilized plant capacity drag down overall capital return."
            })

    return flags
