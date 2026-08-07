import json
from .prompts.system_prompts import CHATBOT_PROMPT

class CompanyChatbot:
    def __init__(self, gemini_client, dossier: dict):
        self.client = gemini_client
        self.dossier = dossier  # The verified company dossier
    
    def ask(self, question: str) -> str:
        """Answer user question using ONLY the verified dossier.
        Must cite sources. Must refuse to answer if data not in dossier."""
        prompt = f"Dossier Data:\n{json.dumps(self.dossier)}\n\nUser Question: {question}"
        return self.client.generate(prompt=prompt, system_instruction=CHATBOT_PROMPT)
    
    def get_suggested_questions(self) -> list[str]:
        """Return 5 suggested questions based on the company's data."""
        sys_prompt = "Based on the provided dossier, generate 5 insightful questions a common person should ask about this company. Return JSON with a key 'questions' containing a list of strings."
        prompt = f"Dossier: {json.dumps(self.dossier)}"
        result = self.client.generate_json(prompt=prompt, system_instruction=sys_prompt)
        return result.get("questions", [
            "What is the company's main source of revenue?",
            "How much debt does the company have?",
            "What are the biggest risks for this company?",
            "Who are the main competitors?",
            "What did management say about future growth?"
        ])
