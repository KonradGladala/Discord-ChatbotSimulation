import os
import openai
import asyncio
from dotenv import load_dotenv

load_dotenv()

VENICE_API_KEY = os.getenv("VENICE_API_KEY")
BASE_URL = "https://api.venice.ai/api/v1"
MODEL_ID = "venice-uncensored"

class AIMessageService:
    def __init__(self):
        if not VENICE_API_KEY:
            raise ValueError("VENICE_API_KEY not set")

        self.client = openai.OpenAI(
            api_key=VENICE_API_KEY,
            base_url=BASE_URL,
            timeout=30.0,
        )

    async def generate_message(self, prompt: str) -> str:
        def _call_api():
            print("Venice request started")
            response = self.client.chat.completions.create(
                model=MODEL_ID,
                messages=[{"role": "user", "content": prompt}],
            )
            print("Venice response received")
            return response.choices[0].message.content

        return await asyncio.to_thread(_call_api)
