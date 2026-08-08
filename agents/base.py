import requests

MODEL = "tinyllama"
OLLAMA_URL = "http://localhost:11434/api/generate"

def call_llm(prompt: str) -> str:
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False,
                "max_tokens": 300
            },
            timeout=30
        )
        return response.json()["response"].strip()
    except Exception as e:
        return f"Error: {str(e)}"