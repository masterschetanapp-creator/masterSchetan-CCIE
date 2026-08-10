"""
masterSchetan CCIE — Gemini & Multi-Model Client Wrapper
"""

from ai.llm_provider import MultiModelLLMClient, safe_dumps

class GeminiClient:
    def __init__(self):
        self.provider = MultiModelLLMClient()
    
    def generate(self, prompt: str, system_instruction: str = None, 
                 json_mode: bool = False, temperature: float = 0.3,
                 task_type: str = 'analysis') -> str:
        return self.provider.generate(prompt, system_instruction, json_mode, temperature, task_type)
    
    def generate_json(self, prompt: str, system_instruction: str = None,
                      temperature: float = 0.3, task_type: str = 'analysis') -> dict:
        return self.provider.generate_json(prompt, system_instruction, temperature, task_type)
    
    def generate_stream(self, prompt: str, system_instruction: str = None):
        text = self.generate(prompt, system_instruction)
        yield text
    
    def get_provider_status(self) -> dict:
        """Returns status of all configured LLM providers."""
        return self.provider.get_provider_status()

