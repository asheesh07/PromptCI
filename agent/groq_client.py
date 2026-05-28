import os
import time
from groq import Groq

_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))


def groq_chat(messages: list, max_tokens: int = 1024, retries: int = 3) -> str:
    for attempt in range(retries):
        try:
            response = _client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            if attempt == retries - 1:
                raise
            wait = 2 ** attempt + 1
            print(f"Groq rate limit hit, waiting {wait}s... (attempt {attempt + 1}/{retries})")
            time.sleep(wait)