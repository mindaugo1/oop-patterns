import json
import os
from typing import Optional

from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()


class OpenAIClient:
    """Adapter for OpenAI Responses API returning parsed JSON objects."""

    def __init__(self, model: Optional[str] = None) -> None:
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

    async def get_response(self, *, user_prompt: str) -> dict:
        resp = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.0,
        )
        return json.loads(resp.choices[0].message.content or "{}")
