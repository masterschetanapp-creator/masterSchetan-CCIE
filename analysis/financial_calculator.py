"""
masterSchetan CCIE — Financial Calculator Engine
ALL financial calculations done strictly in Python code (NEVER by AI).
Supports both Commercial Companies and Banking / Financial Institutions.
"""

import math
from typing import Dict, Any, List, Optional


def get_first_valid(dict_obj: Dict[str, Any], keys: List[str]) -> Optional[float]:
    """Search a dict for the first matching key and return its float value."""
    if not dict_obj or not isinstance(dict_obj, dict):
        return None
    for k in keys:
        if k in dict_obj and dict_obj[k] is not None:
            try:
                val = float(dict_obj[k])
                if not (math.isnan(val) or math.isinf(val)):
                    return val
            except (ValueError, TypeError):
                continue
    return None


def calculate_cagr(start_value: float, end_value: float, years: int) -> Optional[float]:
    """Compound Annual Growth Rate."""
    if years <= 0 or start_value is None or end_value is None:
        return None
    if start_value <= 0:
        return None  # Cannot calculate CAGR with negative or zero base
    try:
        return (math.pow(end_value / start_value, 1 / years) - 1) * 100
    except Exception:
        return None


def calculate_profitability(income_stmt: Dict[str, Any], balance_sheet: Dict[str, Any], is_bank: bool = False) -> Dict[str, Any]:
    """ROE, ROCE, Net Margin, Operating Margin, EBITDA Margin."""
    result = {}

    # Net Income
    net_income = get_first_valid(income_stmt, [
        'Net Income', 'Net Income Common Stockholders',
        'Net Income From Continuing Operation Net Minority Interest',
        'Net Income Continuous Operations'
    ])

    # Equity
    total_equity = get_first_valid(balance_sheet, [
        'Stockholders Equity', 'Total Equity Gross Minority Interest',
        'Common Stock Equity', 'Total Equity'
    ])

    # 1. Return on Equity (ROE)
    if net_income is not None and total_equity is not None and total_equity > 0:
        roe = (net_income / total_equity) * 100
        status = 'green' if roe > 15 else ('amber' if roe >= 10 else 'red')
        result['roe'] = {
            'value': roe,
            'formatted_string': f"{roe:.2f}%",
            'status': status,
            'explanation': "Return on Equity (ROE) measures how efficiently a company generates profits from shareholder money."
        }
    else:
        result['roe'] = None

    # Revenue / Topline
    total_revenue = get_first_valid(income_stmt, [
        'Total Revenue', 'Operating Revenue', 'Net Interest Income',
        'Interest Income', 'Total Income'
    ])

    # Operating Profit / EBIT
    ebit = get_first_valid(income_stmt, [
        'Operating Income', 'EBIT', 'Pretax Income', 'Normalized Income'
    ])

    total_assets = get_first_valid(balance_sheet, ['Total Assets'])
    current_liabilities = get_first_valid(balance_sheet, [
        'Current Liabilities', 'Total Current Liabilities'
    ])

    # 2. Return on Capital Employed (ROCE) or Return on Assets (ROA for Banks)
    if is_bank:
        if net_income is not None and total_assets is not None and total_assets > 0:
            roa = (net_income / total_assets) * 100
            status = 'green' if roa > 1.2 else ('amber' if roa >= 0.8 else 'red')
            result['roce'] = {
                'value': roa,
                'formatted_string': f"{roa:.2f}% (ROA)",
                'status': status,
                'explanation': "Return on Assets (ROA) is the primary efficiency metric for banks, showing profit generated per ₹100 of total assets."
            }
        else:
            result['roce'] = None
    else:
        if ebit is not None and total_assets is not None and current_liabilities is not None:
            capital_employed = total_assets - current_liabilities
            if capital_employed > 0:
                roce = (ebit / capital_employed) * 100
                status = 'green' if roce > 15 else ('amber' if roce >= 10 else 'red')
                result['roce'] = {
                    'value': roce,
                    'formatted_string': f"{roce:.2f}%",
                    'status': status,
                    'explanation': "Return on Capital Employed (ROCE) measures total profit earned per ₹100 of operating capital."
                }
            else:
                result['roce'] = None
        else:
            result['roce'] = None

    # 3. Net Margin
    if total_revenue and total_revenue > 0 and net_income is not None:
        net_margin = (net_income / total_revenue) * 100
        result['net_margin'] = {
            'value': net_margin,
            'formatted_string': f"{net_margin:.2f}%",
            'status': 'green' if net_margin > 12 else ('amber' if net_margin > 5 else 'red'),
            'explanation': "Net Profit Margin shows how much profit is retained out of total revenue."
        }

    # 4. Operating Margin
    if total_revenue and total_revenue > 0 and ebit is not None:
        operating_margin = (ebit / total_revenue) * 100
        result['operating_margin'] = {
            'value': operating_margin,
            'formatted_string': f"{operating_margin:.2f}%",
            'status': 'green' if operating_margin > 15 else ('amber' if operating_margin > 8 else 'red'),
            'explanation': "Operating Margin measures profit generated from core business operations."
        }

    # 5. EBITDA Margin
    ebitda = get_first_valid(income_stmt, ['EBITDA', 'Normalized EBITDA'])
    if total_revenue and total_revenue > 0 and ebitda is not None:
        ebitda_margin = (ebitda / total_revenue) * 100
        result['ebitda_margin'] = {
            'value': ebitda_margin,
            'formatted_string': f"{ebitda_margin:.2f}%",
            'status': 'green' if ebitda_margin > 20 else ('amber' if ebitda_margin > 10 else 'red'),
            'explanation': "EBITDA Margin shows core cash operating profitability before interest, taxes, and depreciation."
        }

    return result


def calculate_growth(income_stmts: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Revenue CAGR (1yr, 3yr), Profit CAGR."""
    result = {}

    if not income_stmts or len(income_stmts) == 0:
        return result

    curr = income_stmts[0]

    def get_val(stmt, metric_list):
        return get_first_valid(stmt, metric_list)

    rev_keys = ['Total Revenue', 'Operating Revenue', 'Net Interest Income', 'Interest Income', 'Total Income']
    pat_keys = ['Net Income', 'Net Income Common Stockholders', 'Net Income Continuous Operations']

    curr_rev = get_val(curr, rev_keys)
    curr_pat = get_val(curr, pat_keys)

    # 1-Year Growth
    if len(income_stmts) > 1:
        prev1_rev = get_val(income_stmts[1], rev_keys)
        if curr_rev and prev1_rev and prev1_rev > 0:
            rev_1y = ((curr_rev - prev1_rev) / prev1_rev) * 100
            result['revenue_cagr_1y'] = {
                'value': rev_1y,
                'formatted_string': f"{rev_1y:+.2f}%",
                'status': 'green' if rev_1y > 10 else ('amber' if rev_1y > 0 else 'red'),
                'explanation': "1-Year Revenue Growth."
            }

        prev1_pat = get_val(income_stmts[1], pat_keys)
        if curr_pat and prev1_pat and prev1_pat > 0:
            pat_1y = ((curr_pat - prev1_pat) / prev1_pat) * 100
            result['profit_cagr_1y'] = {
                'value': pat_1y,
                'formatted_string': f"{pat_1y:+.2f}%",
                'status': 'green' if pat_1y > 10 else ('amber' if pat_1y > 0 else 'red'),
                'explanation': "1-Year Net Profit Growth."
            }

    # 3-Year CAGR
    if len(income_stmts) >= 4:
        prev3_rev = get_val(income_stmts[3], rev_keys)
        if curr_rev and prev3_rev and prev3_rev > 0:
            cagr3_rev = calculate_cagr(prev3_rev, curr_rev, 3)
            if cagr3_rev is not None:
                result['revenue_cagr_3y'] = {
                    'value': cagr3_rev,
                    'formatted_string': f"{cagr3_rev:.2f}% CAGR",
                    'status': 'green' if cagr3_rev > 12 else ('amber' if cagr3_rev > 5 else 'red'),
                    'explanation': "3-Year Compound Annual Growth Rate of Revenue."
                }

        prev3_pat = get_val(income_stmts[3], pat_keys)
        if curr_pat and prev3_pat and prev3_pat > 0:
            cagr3_pat = calculate_cagr(prev3_pat, curr_pat, 3)
            if cagr3_pat is not None:
                result['profit_cagr_3y'] = {
                    'value': cagr3_pat,
                    'formatted_string': f"{cagr3_pat:.2f}% CAGR",
                    'status': 'green' if cagr3_pat > 15 else ('amber' if cagr3_pat > 5 else 'red'),
                    'explanation': "3-Year Compound Annual Growth Rate of Profit."
                }

    return result


def calculate_debt_metrics(balance_sheet: Dict[str, Any], income_stmt: Dict[str, Any], is_bank: bool = False) -> Dict[str, Any]:
    """Debt/Equity, Interest Coverage, Debt/EBITDA."""
    result = {}

    if is_bank:
        # Banks operate on leverage (deposits to equity)
        total_assets = get_first_valid(balance_sheet, ['Total Assets'])
        total_equity = get_first_valid(balance_sheet, ['Stockholders Equity', 'Common Stock Equity'])
        if total_assets and total_equity and total_equity > 0:
            leverage = total_assets / total_equity
            result['debt_to_equity'] = {
                'value': leverage,
                'formatted_string': f"{leverage:.1f}x (Assets/Equity)",
                'status': 'green' if leverage < 15 else 'amber',
                'explanation': "Bank Financial Leverage (Total Assets / Equity capital)."
            }
        return result

    total_debt = get_first_valid(balance_sheet, ['Total Debt', 'Long Term Debt And Capital Lease Obligation'])
    total_equity = get_first_valid(balance_sheet, ['Stockholders Equity', 'Common Stock Equity', 'Total Equity'])

    if total_debt is not None and total_equity is not None and total_equity > 0:
        de_ratio = total_debt / total_equity
        status = 'green' if de_ratio < 0.5 else ('amber' if de_ratio <= 1.5 else 'red')
        result['debt_to_equity'] = {
            'value': de_ratio,
            'formatted_string': f"{de_ratio:.2f}x",
            'status': status,
            'explanation': "Debt-to-Equity ratio measures reliance on borrowed money vs shareholder capital."
        }

    ebit = get_first_valid(income_stmt, ['Operating Income', 'EBIT'])
    interest_expense = get_first_valid(income_stmt, ['Interest Expense', 'Interest Expense Non Operating'])

    if ebit is not None and interest_expense is not None and interest_expense > 0:
        icr = ebit / interest_expense
        status = 'green' if icr > 4 else ('amber' if icr >= 2 else 'red')
        result['interest_coverage'] = {
            'value': icr,
            'formatted_string': f"{icr:.2f}x",
            'status': status,
            'explanation': "Interest Coverage Ratio measures how comfortably operating profit covers interest payments."
        }

    return result


def calculate_valuation(price: float, info: Dict[str, Any]) -> Dict[str, Any]:
    """P/E, P/B, Dividend Yield without invented fallbacks."""
    result = {}

    pe = info.get('trailingPE') or info.get('forwardPE')
    if pe is not None and isinstance(pe, (int, float)) and pe > 0:
        result['pe_ratio'] = {
            'value': float(pe),
            'formatted_string': f"{float(pe):.2f}",
            'status': 'green' if pe < 25 else ('amber' if pe < 45 else 'red'),
            'explanation': "Price-to-Earnings (P/E) ratio: How much investors pay for ₹1 of profit."
        }
    else:
        result['pe_ratio'] = None

    pb = info.get('priceToBook')
    if pb is not None and isinstance(pb, (int, float)) and pb > 0:
        result['pb_ratio'] = {
            'value': float(pb),
            'formatted_string': f"{float(pb):.2f}",
            'status': 'green' if pb < 3 else ('amber' if pb < 6 else 'red'),
            'explanation': "Price-to-Book (P/B) ratio: Stock price relative to net asset book value."
        }
    else:
        result['pb_ratio'] = None

    div_yield = info.get('dividendYield')
    if div_yield is not None and isinstance(div_yield, (int, float)) and div_yield >= 0:
        div_pct = div_yield * 100 if div_yield <= 1.0 else div_yield
        result['dividend_yield'] = {
            'value': float(div_pct),
            'formatted_string': f"{float(div_pct):.2f}%",
            'status': 'green' if div_pct > 2 else 'neutral',
            'explanation': "Dividend Yield: Annual dividend payout expressed as % of stock price."
        }
    else:
        result['dividend_yield'] = None

    return result


def calculate_cash_flow_quality(cashflow: Dict[str, Any], income_stmt: Dict[str, Any]) -> Dict[str, Any]:
    """CFO/PAT ratio, FCF."""
    result = {}

    cfo = get_first_valid(cashflow, ['Operating Cash Flow', 'Cash Flow From Continuing Operating Activities'])
    pat = get_first_valid(income_stmt, ['Net Income', 'Net Income Common Stockholders'])

    if cfo is not None and pat is not None and pat > 0:
        cfo_pat = cfo / pat
        status = 'green' if cfo_pat > 0.8 else ('amber' if cfo_pat >= 0.5 else 'red')
        result['cfo_to_pat'] = {
            'value': cfo_pat,
            'formatted_string': f"{cfo_pat:.2f}x",
            'status': status,
            'explanation': "CFO/PAT ratio shows what portion of reported net profit actually arrives as cash in the bank."
        }

    capex = get_first_valid(cashflow, ['Capital Expenditure', 'Capital Expenditure Reported'])
    if cfo is not None and capex is not None:
        fcf = cfo + capex if capex < 0 else cfo - capex
        fcf_cr = fcf / 1e7
        result['fcf'] = {
            'value': fcf,
            'formatted_string': f"₹{fcf_cr:,.2f} Cr",
            'status': 'green' if fcf > 0 else 'red',
            'explanation': "Free Cash Flow is actual cash left over after paying for operations and capex."
        }

    return result


def calculate_all_metrics(financial_data: Dict[str, Any]) -> Dict[str, Any]:
    """Master function. Takes raw financial statements and returns all computed metrics."""
    metrics = {}

    info = financial_data.get('info', {})
    sector = info.get('sector', '')
    is_bank = 'Financial' in sector or 'Bank' in sector

    # Get structured yearly lists
    income_stmts = financial_data.get('annual_income_stmt') or financial_data.get('financials', {}).get('annual_income_stmt', [])
    balance_sheets = financial_data.get('annual_balance_sheet') or financial_data.get('financials', {}).get('annual_balance_sheet', [])
    cashflows = financial_data.get('annual_cashflow') or financial_data.get('financials', {}).get('annual_cashflow', [])

    curr_income = income_stmts[0] if income_stmts else {}
    curr_balance = balance_sheets[0] if balance_sheets else {}
    curr_cashflow = cashflows[0] if cashflows else {}

    metrics['profitability'] = calculate_profitability(curr_income, curr_balance, is_bank=is_bank)
    metrics['growth'] = calculate_growth(income_stmts)
    metrics['debt_metrics'] = calculate_debt_metrics(curr_balance, curr_income, is_bank=is_bank)

    price = info.get('currentPrice') or info.get('regularMarketPrice') or 0.0
    metrics['valuation'] = calculate_valuation(price, info)
    metrics['cash_flow_quality'] = calculate_cash_flow_quality(curr_cashflow, curr_income)

    return metrics
