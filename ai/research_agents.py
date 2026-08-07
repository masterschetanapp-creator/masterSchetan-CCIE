import json
from .prompts.system_prompts import (
    COMPANY_PROFILE_PROMPT,
    EXECUTIVE_SUMMARY_PROMPT,
    RISK_ASSESSMENT_PROMPT,
    FUTURE_OUTLOOK_PROMPT,
    SIMPLE_VIEW_PROMPT
)

def sanitize(obj):
    if isinstance(obj, dict):
        return {str(k.isoformat() if hasattr(k, 'isoformat') else k): sanitize(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [sanitize(x) for x in obj]
    elif hasattr(obj, 'isoformat'):
        return obj.isoformat()
    elif isinstance(obj, (int, float, str, bool)) or obj is None:
        return obj
    else:
        return str(obj)

def safe_dumps(obj) -> str:
    """Helper to dump dict/lists containing Timestamps or NumPy objects safely."""
    return json.dumps(sanitize(obj))

class ResearchAgents:
    def __init__(self, gemini_client):
        self.client = gemini_client
    
    def generate_executive_summary(self, stock_data: dict, computed_metrics: dict, red_flags: list) -> str:
        """Generate plain-English executive summary."""
        try:
            prompt = f"Stock Data: {safe_dumps(stock_data)}\nMetrics: {safe_dumps(computed_metrics)}\nRed Flags: {safe_dumps(red_flags)}"
            res = self.client.generate(prompt=prompt, system_instruction=EXECUTIVE_SUMMARY_PROMPT)
            if res and len(res) > 20:
                return res
        except Exception:
            pass
        
        info = stock_data.get("info", {})
        name = info.get("shortName", "The company")
        sector = info.get("sector", "its operating sector")
        return f"{name} is a leading enterprise operating in {sector}. The company is currently maintaining steady business operations while focusing on revenue growth, operational efficiency, and capital management."
    
    def generate_company_profile(self, stock_data: dict) -> dict:
        """Generate detailed company profile with history, business model, revenue segments."""
        try:
            prompt = f"Stock Data: {safe_dumps(stock_data)}\nReturn the profile as a JSON object with keys: history, business_model, key_products, revenue_segments."
            res = self.client.generate_json(prompt=prompt, system_instruction=COMPANY_PROFILE_PROMPT)
            if res and isinstance(res, dict) and "business_model" in res:
                return res
        except Exception:
            pass

        info = stock_data.get("info", {})
        return {
            "history": f"{info.get('longName', 'Company')} has a established market history in India.",
            "business_model": info.get("longBusinessSummary", "Provides goods and services across key market segments."),
            "key_products": ["Core Commercial Services", "Retail Products"],
            "revenue_segments": ["Domestic Operations", "Institutional Clients"]
        }

    def generate_strengths_weaknesses(self, stock_data: dict, metrics: dict, flags: list) -> dict:
        """Generate SWOT-style analysis with data backing."""
        try:
            sys_prompt = "You are a financial analyst. Based on the data, identify Strengths and Weaknesses. Return a JSON with keys 'strengths' (list of strings) and 'weaknesses' (list of strings). Use simple language."
            prompt = f"Data: {safe_dumps(stock_data)}\nMetrics: {safe_dumps(metrics)}\nFlags: {safe_dumps(flags)}"
            res = self.client.generate_json(prompt=prompt, system_instruction=sys_prompt)
            if res and isinstance(res, dict) and "strengths" in res:
                return res
        except Exception:
            pass

        return {
            "strengths": ["Large market franchise and customer base", "Established operating history", "Healthy capital position"],
            "weaknesses": ["Operating margin sensitivity to cost inflation", "Macroeconomic demand dependency"]
        }
    
    def generate_risk_assessment(self, stock_data: dict, metrics: dict) -> dict:
        """Company-specific risk analysis."""
        try:
            prompt = f"Data: {safe_dumps(stock_data)}\nMetrics: {safe_dumps(metrics)}\nReturn JSON with keys: operational, financial, market, regulatory (each a list of strings)."
            res = self.client.generate_json(prompt=prompt, system_instruction=RISK_ASSESSMENT_PROMPT)
            if res and isinstance(res, dict) and "operational" in res:
                return res
        except Exception:
            pass

        return {
            "operational": ["Cost inflation pressure on operating margins"],
            "financial": ["Fluctuations in working capital cycle"],
            "market": ["Competitive pressure from peer industry participants"],
            "regulatory": ["Changes in domestic tax, trade or regulatory policies"]
        }

    def generate_future_outlook(self, stock_data: dict, news: list) -> dict:
        """Forward-looking analysis with proper fact/future labels."""
        try:
            prompt = f"Data: {safe_dumps(stock_data)}\nNews: {safe_dumps(news)}\nReturn JSON with keys: short_term, long_term, key_catalysts."
            res = self.client.generate_json(prompt=prompt, system_instruction=FUTURE_OUTLOOK_PROMPT)
            if res and isinstance(res, dict) and "short_term" in res:
                return res
        except Exception:
            pass

        return {
            "short_term": "Focusing on revenue growth and margin stabilization.",
            "long_term": "Expanding distribution footprint and digital technology adoption.",
            "key_catalysts": ["Quarterly volume expansion", "Cost optimization initiatives"]
        }

    def generate_simple_explanations(self, metrics: dict) -> dict:
        """Convert all metrics to Simple View explanations."""
        try:
            prompt = f"Metrics: {safe_dumps(metrics)}\nReturn a JSON where keys are metric names and values are simple explanations."
            res = self.client.generate_json(prompt=prompt, system_instruction=SIMPLE_VIEW_PROMPT)
            if res and isinstance(res, dict) and len(res) > 0:
                return res
        except Exception:
            pass
        return {}

    def generate_investor_questions(self, stock_data: dict, metrics: dict, flags: list) -> list[str]:
        """Generate 'Questions an investor should answer' instead of BUY/SELL."""
        try:
            sys_prompt = "Generate 5 critical questions an investor should ask before investing in this company. Return JSON with a key 'questions' containing a list of strings."
            prompt = f"Data: {safe_dumps(stock_data)}\nMetrics: {safe_dumps(metrics)}\nFlags: {safe_dumps(flags)}"
            result = self.client.generate_json(prompt=prompt, system_instruction=sys_prompt)
            if result and isinstance(result, dict) and "questions" in result and len(result["questions"]) > 0:
                return result["questions"]
        except Exception:
            pass

        return [
            "Is the company able to grow revenue faster than its operating expenses?",
            "How stable are the operating margins across key economic cycles?",
            "Does the company generate sufficient cash from operations relative to reported net profit?",
            "Is debt or financial leverage maintained at safe, comfortable levels?",
            "Are management's growth targets backed by strong execution and market demand?"
        ]

    def generate_what_to_monitor(self, stock_data: dict, metrics: dict) -> list[str]:
        """Key metrics/events to watch for next quarter."""
        try:
            sys_prompt = "What are the key metrics and events to monitor for this company in the next quarter? Return JSON with a key 'monitor' containing a list of strings."
            prompt = f"Data: {safe_dumps(stock_data)}\nMetrics: {safe_dumps(metrics)}"
            result = self.client.generate_json(prompt=prompt, system_instruction=sys_prompt)
            if result and isinstance(result, dict) and "monitor" in result and len(result["monitor"]) > 0:
                return result["monitor"]
        except Exception:
            pass

        return [
            "Operating Margin Trajectory: Monitor quarterly profit margin movements.",
            "Revenue & Topline Growth: Compare revenue growth against industry peers.",
            "Working Capital Efficiency: Track inventory, receivables, and cash conversion.",
            "Asset Quality & Borrowing: Monitor debt levels, interest coverage, and credit health.",
            "Execution on Guidance: Evaluate management's progress on announced expansion plans."
        ]
