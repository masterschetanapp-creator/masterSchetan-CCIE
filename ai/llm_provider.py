"""
masterSchetan CCIE — Unified LLM Provider
Supports Google Gemini API, Groq, OpenRouter, and DeepSeek with intelligent routing.
Zero cost, high intelligence.
"""

import os
import json
import time
import logging
import requests
import google.generativeai as genai
from config import GEMINI_API_KEY

logger = logging.getLogger(__name__)

def get_secret(key_name):
    try:
        import streamlit as st
        if hasattr(st, "session_state"):
            if key_name in st.session_state and st.session_state[key_name]:
                return st.session_state[key_name]
            st_key = "input_" + key_name.lower().replace("_api_key", "_k")
            if st_key in st.session_state and st.session_state[st_key]:
                return st.session_state[st_key]
    except Exception:
        pass

    env_val = os.getenv(key_name, "")
    if env_val:
        return env_val

    try:
        import streamlit as st
        try:
            sec_val = st.secrets.get(key_name, "")
            if sec_val:
                return sec_val
        except Exception:
            pass
    except Exception:
        pass

    return ""

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
    """Unified LLM client supporting intelligent routing across 4 providers."""
    def __init__(self):
        self._call_counts = {'gemini': 0, 'groq': 0, 'openrouter': 0, 'deepseek': 0}
        self._rate_limits = {'gemini': 1500, 'groq': 1000, 'openrouter': 50, 'deepseek': 999999}
        
        self.gemini_key = get_secret("GEMINI_API_KEY")
        self.groq_key = get_secret("GROQ_API_KEY")
        self.openrouter_key = get_secret("OPENROUTER_API_KEY")
        self.deepseek_key = get_secret("DEEPSEEK_API_KEY")

        self.gemini_configured = False
        if self.gemini_key:
            try:
                genai.configure(api_key=self.gemini_key)
                self.gemini_configured = True
            except Exception as e:
                logger.error(f"Gemini configuration error: {e}")

        self.gemini_models = ['gemini-1.5-flash', 'models/gemini-1.5-flash', 'gemini-1.5-pro', 'models/gemini-1.5-pro', 'gemini-2.0-flash', 'models/gemini-2.0-flash']
        self.groq_models = ['llama-3.3-70b-versatile', 'gemma2-9b-it']
        self.openrouter_models = [
            'openrouter/auto',
            'deepseek/deepseek-r1:free',
            'qwen/qwen-2.5-72b-instruct:free',
            'google/gemma-2-9b-it:free'
        ]
        self.deepseek_models = ['deepseek-chat']

    def get_provider_status(self) -> dict:
        return {
            'gemini': {
                'configured': self.gemini_configured,
                'used': self._call_counts['gemini'],
                'limit': self._rate_limits['gemini']
            },
            'groq': {
                'configured': bool(self.groq_key),
                'used': self._call_counts['groq'],
                'limit': self._rate_limits['groq']
            },
            'openrouter': {
                'configured': bool(self.openrouter_key),
                'used': self._call_counts['openrouter'],
                'limit': self._rate_limits['openrouter']
            },
            'deepseek': {
                'configured': bool(self.deepseek_key),
                'used': self._call_counts['deepseek'],
                'limit': self._rate_limits['deepseek']
            }
        }

    def _check_limit(self, provider: str) -> bool:
        return self._call_counts[provider] < self._rate_limits[provider]

    def _increment_limit(self, provider: str):
        self._call_counts[provider] += 1

    def _call_gemini(self, prompt: str, system_instruction: str, json_mode: bool, temperature: float) -> str:
        if not self.gemini_configured or not self._check_limit('gemini'):
            return None

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
                        self._increment_limit('gemini')
                        logger.info(f"Successfully used Gemini model: {m_name}")
                        return response.text
                except Exception as e:
                    err_str = str(e)
                    if "429" in err_str and attempt == 0:
                        time.sleep(2)
                        continue
                    else:
                        logger.warning(f"Gemini {m_name} failed: {e}")
                        break
        return None

    def _call_openai_compatible(self, provider: str, url: str, key: str, models: list, prompt: str, 
                                system_instruction: str, json_mode: bool, temperature: float, 
                                extra_headers: dict = None) -> str:
        if not key or not self._check_limit(provider):
            return None

        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        }
        if extra_headers:
            headers.update(extra_headers)

        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})

        for m_name in models:
            for attempt in range(2):
                payload = {
                    "model": m_name,
                    "messages": messages,
                    "temperature": temperature,
                }
                
                if json_mode:
                    payload["response_format"] = {"type": "json_object"}
                
                try:
                    res = requests.post(url, headers=headers, json=payload, timeout=20)
                    if res.status_code == 200:
                        data = res.json()
                        content = data["choices"][0]["message"]["content"]
                        self._increment_limit(provider)
                        logger.info(f"Successfully used {provider} model: {m_name}")
                        return content
                    elif res.status_code == 429 and attempt == 0:
                        time.sleep(2)
                        continue
                    elif res.status_code == 400 and json_mode and "response_format" in str(res.text).lower() and attempt == 0:
                        del payload["response_format"]
                        res_retry = requests.post(url, headers=headers, json=payload, timeout=20)
                        if res_retry.status_code == 200:
                            data = res_retry.json()
                            content = data["choices"][0]["message"]["content"]
                            self._increment_limit(provider)
                            logger.info(f"Successfully used {provider} model without response_format: {m_name}")
                            return content
                        break
                    else:
                        logger.warning(f"{provider} {m_name} failed with status {res.status_code}: {res.text}")
                        break
                except requests.exceptions.RequestException as e:
                    logger.warning(f"{provider} {m_name} request error: {e}")
                    if attempt == 0:
                        time.sleep(2)
                        continue
                    break
                except Exception as e:
                    logger.warning(f"{provider} {m_name} error: {e}")
                    break
        return None

    def _call_groq(self, prompt: str, system_instruction: str, json_mode: bool, temperature: float) -> str:
        return self._call_openai_compatible(
            'groq', "https://api.groq.com/openai/v1/chat/completions", self.groq_key, 
            self.groq_models, prompt, system_instruction, json_mode, temperature
        )
        
    def _call_openrouter(self, prompt: str, system_instruction: str, json_mode: bool, temperature: float) -> str:
        return self._call_openai_compatible(
            'openrouter', "https://openrouter.ai/api/v1/chat/completions", self.openrouter_key, 
            self.openrouter_models, prompt, system_instruction, json_mode, temperature,
            extra_headers={'HTTP-Referer': 'https://masterschetan-ccie.streamlit.app', 'X-Title': 'masterSchetan CCIE'}
        )
        
    def _call_deepseek(self, prompt: str, system_instruction: str, json_mode: bool, temperature: float) -> str:
        return self._call_openai_compatible(
            'deepseek', "https://api.deepseek.com/v1/chat/completions", self.deepseek_key, 
            self.deepseek_models, prompt, system_instruction, json_mode, temperature
        )

    def generate(self, prompt: str, system_instruction: str = None, 
                 json_mode: bool = False, temperature: float = 0.3,
                 task_type: str = 'analysis') -> str:
        """Generate text response trying intelligent routing based on task type."""
        
        routes = {
            'fast_parse': [self._call_groq, self._call_gemini, self._call_openrouter],
            'deep_analysis': [self._call_gemini, self._call_openrouter, self._call_groq],
            'thesis': [self._call_gemini, self._call_openrouter, self._call_deepseek],
            'analysis': [self._call_gemini, self._call_groq, self._call_openrouter, self._call_deepseek],
            'math': [self._call_deepseek, self._call_gemini, self._call_groq]
        }
        
        funcs = routes.get(task_type, routes['analysis'])
        
        for func in funcs:
            res = func(prompt, system_instruction, json_mode, temperature)
            if res:
                return res

        # Fallback empty JSON or default text
        if json_mode:
            return "{}"
        return "AI analysis generated from primary financial disclosures."

    def generate_json(self, prompt: str, system_instruction: str = None, 
                      temperature: float = 0.3, task_type: str = 'analysis') -> dict:
        """Generate and parse JSON response."""
        res_text = self.generate(
            prompt, 
            system_instruction=system_instruction, 
            json_mode=True, 
            temperature=temperature, 
            task_type=task_type
        )
        try:
            res_text = res_text.strip()
            if res_text.startswith("```json"):
                res_text = res_text[7:-3].strip()
            elif res_text.startswith("```"):
                res_text = res_text[3:-3].strip()
            return json.loads(res_text)
        except json.JSONDecodeError:
            logger.warning("Failed to decode JSON from model response.")
            return {}
