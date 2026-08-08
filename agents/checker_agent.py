import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents.base import call_llm

def run(summary: str) -> str:
    prompt = f"Review this summary for bias, errors, or missing info:\n{summary}"
    return call_llm(prompt)