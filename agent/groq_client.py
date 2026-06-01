import os
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))



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
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            if attempt == retries - 1:
                raise
            wait = 2 ** attempt + 1
            print(f"Rate limit hit, waiting {wait}s... (attempt {attempt + 1}/{retries})")
            time.sleep(wait)