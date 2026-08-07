def explain_metric(metric_name: str, value: float, context: dict = None, gemini_client=None) -> dict:
    """Convert a single metric into simple explanation.
    Returns: {simple_text, why_it_matters, status, see_calculation}
    Uses templates for common metrics, AI for complex ones."""
    if context is None:
        context = {}
        
    metric_lower = metric_name.lower()
    simple_text = ""
    why_it_matters = ""
    
    if "roe" in metric_lower or "return on equity" in metric_lower:
        simple_text = f"The company earns ₹{value} for every ₹100 of shareholder money."
        why_it_matters = "Shows how efficiently the company is using investors' money to generate profits."
    elif "d/e" in metric_lower or "debt to equity" in metric_lower:
        simple_text = f"For every ₹100 of its own money, the company has borrowed ₹{value}."
        why_it_matters = "High debt can be risky, especially if earnings are unstable."
    elif "p/e" in metric_lower or "price to earnings" in metric_lower:
        ind_pe = context.get("industry_pe", "N/A")
        simple_text = f"Investors are paying ₹{value} for every ₹1 of profit. Industry average is ₹{ind_pe}."
        why_it_matters = "Helps gauge if the stock is overvalued or undervalued compared to peers."
    elif "roce" in metric_lower:
        simple_text = f"The company earns ₹{value} for every ₹100 of capital used in the business."
        why_it_matters = "Indicates overall efficiency of capital allocation."
    else:
        if gemini_client:
            from .prompts.system_prompts import SIMPLE_VIEW_PROMPT
            prompt = f"Metric: {metric_name}, Value: {value}, Context: {context}\nReturn a JSON with keys: simple_text, why_it_matters."
            ai_res = gemini_client.generate_json(prompt, system_instruction=SIMPLE_VIEW_PROMPT)
            simple_text = ai_res.get("simple_text", f"{metric_name} is {value}.")
            why_it_matters = ai_res.get("why_it_matters", "")
        else:
            simple_text = f"The value for {metric_name} is {value}."
            why_it_matters = "Information not available."

    return {
        "simple_text": simple_text,
        "why_it_matters": why_it_matters,
        "status": "Calculated",
        "see_calculation": "Available in detailed metrics view"
    }

def explain_all_metrics(computed_metrics: dict, context: dict = None, gemini_client=None) -> dict:
    """Batch convert all metrics to simple explanations."""
    explanations = {}
    for metric_name, value in computed_metrics.items():
        explanations[metric_name] = explain_metric(metric_name, value, context, gemini_client)
    return explanations
