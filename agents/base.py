import os
import requests

# NOTE: the default used to be "llama3.2:3b " (trailing space), which Ollama
# can't match to an installed model. .strip() also protects against stray
# whitespace in the OLLAMA_MODEL environment variable.
MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2:3b").strip()
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434/api/generate")
# Prompts now carry real source excerpts, so a local model needs more time
# than before on first load / CPU-only machines.
REQUEST_TIMEOUT = int(os.environ.get("OLLAMA_TIMEOUT", "300"))
# Ollama's default context window is small and it silently truncates longer
# prompts from the start (dropping the instructions!). Set it explicitly.
NUM_CTX = int(os.environ.get("OLLAMA_NUM_CTX", "6144"))


def is_error(text: str) -> bool:
    """True if `text` is one of call_llm's "Error: ..." messages."""
    return isinstance(text, str) and text.startswith("Error:")


def call_llm(prompt: str, temperature: float = 0.3, num_predict: int = 400) -> str:
    """Call the local Ollama model and return its text response.

    Any failure is returned as a readable "Error: ..." string (instead of
    raising) so one agent failing doesn't take down the whole pipeline —
    but the message now says *why* it failed instead of a bare KeyError.
    """
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        # Ollama's /api/generate has no top-level "max_tokens" field — that
        # was silently ignored before. Generation length/creativity is
        # controlled via "options" instead.
        "options": {
            "temperature": temperature,
            "num_predict": num_predict,
            "num_ctx": NUM_CTX,
        },
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=REQUEST_TIMEOUT)
    except requests.exceptions.ConnectionError:
        return (
            f"Error: Could not reach Ollama at {OLLAMA_URL}. "
            "Make sure it's running (`ollama serve`) and that the model has "
            f"been pulled (`ollama pull {MODEL}`)."
        )
    except requests.exceptions.Timeout:
        return (
            f"Error: Ollama did not respond within {REQUEST_TIMEOUT}s. "
            f"'{MODEL}' may still be loading into memory on first use — "
            "try again, or raise the OLLAMA_TIMEOUT environment variable."
        )
    except requests.exceptions.RequestException as e:
        return f"Error: Request to Ollama failed ({e})."

    if response.status_code != 200:
        # Ollama returns JSON like {"error": "model 'tinyllama' not found, try pulling it first"}
        try:
            detail = response.json().get("error", response.text)
        except ValueError:
            detail = response.text
        return f"Error: Ollama returned HTTP {response.status_code} — {detail}"

    try:
        data = response.json()
    except ValueError:
        return "Error: Ollama returned a response that wasn't valid JSON."

    if "error" in data:
        return f"Error: {data['error']}"

    if "response" not in data:
        return f"Error: Unexpected response shape from Ollama: {data}"

    return data["response"].strip()