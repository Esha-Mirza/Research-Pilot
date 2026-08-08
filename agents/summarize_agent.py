import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents.base import call_llm

def run(content: str) -> str:
    prompt = f"Summarize these findings in 3 bullet points:\n{content}"
    return call_llm(prompt)