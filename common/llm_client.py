from openai import OpenAI
from common.config import Config
import google.generativeai as genai

class OpenAIClient:
    def __init__(self):
        Config.validate_openai()
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.model = Config.OPENAI_MODEL

    def generate(self, system_prompt, user_content):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ]
        )
        return response.choices[0].message.content.strip()


class GeminiClient:
    def __init__(self):
        Config.validate_gemini()
        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(Config.GEMINI_MODEL)

    def generate(self, system_prompt, user_content):
        response = self.model.generate_content(
            [system_prompt, user_content]
        )
        return response.text.strip()
