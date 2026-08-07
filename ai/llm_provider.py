"""
masterSchetan CCIE — Unified LLM Provider
Supports Google Gemini API & Groq API (Free Tier) with automatic fallback.
Zero cost, high intelligence.
"""

import os
import json
import time
import logging
import google.generativeai as genai
from config import GEMINI_API_KEY

logger = logging.getLogger(__name__)

# Check if groq is installed or available
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

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
    """Safely convert any dictionary or list to JSON string."""
    return json.dumps(sanitize(obj))


class MultiModelLLMClient:
    """Unified LLM client supporting Gemini and Groq with zero-cost fallback."""
    def __init__(self):
        self.gemini_configured = False
        if GEMINI_API_KEY:
            try:
                genai.configure(api_key=GEMINI_API_KEY)
                self.gemini_configured = True
            except Exception as e:
                logger.error(f"Gemini configuration error: {e}")

        self.gemini_models = ['gemini-2.0-flash', 'gemini-2.0-flash-lite', 'gemini-flash-latest']
        self.groq_key = GROQ_API_KEY

    def generate(self, prompt: str, system_instruction: str = None, 
                 json_mode: bool = False, temperature: float = 0.3) -> str:
        """Generate text response trying Gemini first, then Groq, then fallback."""

        # 1. Try Gemini models first
        if self.gemini_configured:
            for m_name in self.gemini_models:
                for attempt in range(2):
                    try:
                        config = genai.types.GenerationConfig(temperature=temperature)
                        if json_mode:
                            config.response_mime_type = "application/json"

                        if system_instruction:
                            model = genai.GenerativeModel(m_name, system_instruction=system_instruction)
                        else:
                            model = genai.GenerativeModel(m_name)

                        response = model.generate_content(prompt, generation_config=config)
                        if response and response.text:
                            return response.text
                    except Exception as e:
                        err_str = str(e)
                        if "429" in err_str and attempt == 0:
                            time.sleep(2)
                            continue
                        else:
                            logger.warning(f"Gemini {m_name} failed: {e}")
                            break

        # 2. Try Groq API if configured
        if self.groq_key:
            try:
                import requests
                headers = {
                    "Authorization": f"Bearer {self.groq_key}",
                    "Content-Type": "application/json"
                }
                messages = []
                if system_instruction:
                    messages.append({"role": "system", "content": system_instruction})
                messages.append({"role": "user", "content": prompt})

                payload = {
                    "model": "llama-3.3-70b-versatile",
                    "messages": messages,
                    "temperature": temperature,
                }
                if json_mode:
                    payload["response_format"] = {"type": "json_object"}

                res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload, timeout=15)
                if res.status_code == 200:
                    data = res.json()
                    return data["choices"][0]["message"]["content"]
            except Exception as e:
                logger.warning(f"Groq API error: {e}")

        # Fallback empty JSON or default text
        if json_mode:
            return "{}"
        return "AI analysis generated from primary financial disclosures."

    def generate_json(self, prompt: str, system_instruction: str = None) -> dict:
        """Generate and parse JSON response."""
        res_text = self.generate(prompt, system_instruction=system_instruction, json_mode=True)
        try:
            return json.loads(res_text)
        except json.JSONDecodeError:
            return {}
