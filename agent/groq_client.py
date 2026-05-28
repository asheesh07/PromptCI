import os
from google import genai

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))


def groq_chat(messages: list, max_tokens: int = 1024, retries: int = 3) -> str:
    import time
    
    # convert messages to single prompt for Gemini
    prompt = ""
    for msg in messages:
        if msg["role"] == "system":
            prompt += f"{msg['content']}\n\n"
        elif msg["role"] == "user":
            prompt += f"{msg['content']}"

    for attempt in range(retries):
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            if attempt == retries - 1:
                raise
            wait = 2 ** attempt + 1
            print(f"Rate limit hit, waiting {wait}s... (attempt {attempt + 1}/{retries})")
            time.sleep(wait)