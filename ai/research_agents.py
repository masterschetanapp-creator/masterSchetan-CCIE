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
        prompt = f"Stock Data: {safe_dumps(stock_data)}\nMetrics: {safe_dumps(computed_metrics)}\nRed Flags: {safe_dumps(red_flags)}"
        return self.client.generate(prompt=prompt, system_instruction=EXECUTIVE_SUMMARY_PROMPT)
    
    def generate_company_profile(self, stock_data: dict) -> dict:
        """Generate detailed company profile with history, business model, revenue segments."""
        prompt = f"Stock Data: {safe_dumps(stock_data)}\nReturn the profile as a JSON object with keys: history, business_model, key_products, revenue_segments."
        return self.client.generate_json(prompt=prompt, system_instruction=COMPANY_PROFILE_PROMPT)
    
    def generate_strengths_weaknesses(self, stock_data: dict, metrics: dict, flags: list) -> dict:
        """Generate SWOT-style analysis with data backing."""
        sys_prompt = "You are a financial analyst. Based on the data, identify Strengths and Weaknesses. Return a JSON with keys 'strengths' (list of strings) and 'weaknesses' (list of strings). Use simple language."
        prompt = f"Data: {safe_dumps(stock_data)}\nMetrics: {safe_dumps(metrics)}\nFlags: {safe_dumps(flags)}"
        return self.client.generate_json(prompt=prompt, system_instruction=sys_prompt)
    
    def generate_risk_assessment(self, stock_data: dict, metrics: dict) -> dict:
        """Company-specific risk analysis."""
        prompt = f"Data: {safe_dumps(stock_data)}\nMetrics: {safe_dumps(metrics)}\nReturn JSON with keys: operational, financial, market, regulatory (each a list of strings)."
        return self.client.generate_json(prompt=prompt, system_instruction=RISK_ASSESSMENT_PROMPT)
    
    def generate_future_outlook(self, stock_data: dict, news: list) -> dict:
        """Forward-looking analysis with proper fact/future labels."""
        prompt = f"Data: {safe_dumps(stock_data)}\nNews: {safe_dumps(news)}\nReturn JSON with keys: short_term, long_term, key_catalysts."
        return self.client.generate_json(prompt=prompt, system_instruction=FUTURE_OUTLOOK_PROMPT)
    
    def generate_simple_explanations(self, metrics: dict) -> dict:
        """Convert all metrics to Simple View explanations."""
        prompt = f"Metrics: {safe_dumps(metrics)}\nReturn a JSON where keys are metric names and values are simple explanations."
        return self.client.generate_json(prompt=prompt, system_instruction=SIMPLE_VIEW_PROMPT)
    
    def generate_investor_questions(self, stock_data: dict, metrics: dict, flags: list) -> list[str]:
        """Generate 'Questions an investor should answer' instead of BUY/SELL."""
        sys_prompt = "Generate 5 critical questions an investor should ask before investing in this company. Return JSON with a key 'questions' containing a list of strings."
        prompt = f"Data: {safe_dumps(stock_data)}\nMetrics: {safe_dumps(metrics)}\nFlags: {safe_dumps(flags)}"
        result = self.client.generate_json(prompt=prompt, system_instruction=sys_prompt)
        return result.get("questions", [])
    
    def generate_what_to_monitor(self, stock_data: dict, metrics: dict) -> list[str]:
        """Key metrics/events to watch for next quarter."""
        sys_prompt = "What are the key metrics and events to monitor for this company in the next quarter? Return JSON with a key 'monitor' containing a list of strings."
        prompt = f"Data: {safe_dumps(stock_data)}\nMetrics: {safe_dumps(metrics)}"
        result = self.client.generate_json(prompt=prompt, system_instruction=sys_prompt)
        return result.get("monitor", [])

