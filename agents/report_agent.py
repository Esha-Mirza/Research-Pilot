import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents.base import call_llm

def run(summary: str, feedback: str) -> str:
    prompt = f"""
Create a research report based on:
Summary: {summary}
Feedback: {feedback}
"""
    return call_llm(prompt)