import os
import requests

class DeepSeekService:
    def __init__(self):
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = "deepseek/deepseek-chat-v3-0324:free"

    def chat(self, messages):
        """
        Envía mensajes al modelo Deepseek y retorna la respuesta.
        :param messages: Lista de dicts [{"role": "user", "content": "Texto"}]
        """
        if not self.api_key:
            raise ValueError("Falta la variable DEEPSEEK_API_KEY en el entorno")
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.model,
            "messages": messages
        }
        response = requests.post(self.api_url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()