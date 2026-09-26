import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents.base import call_llm


def run(summary: str) -> str:
    prompt = (
        "You are a careful fact-checker. Review the summary below for bias, "
        "factual errors, unsupported claims, or missing context. List concrete "
        "issues as short bullet points. If you find none, say so plainly in "
        "one line.\n\n"
        f"Summary:\n{summary}\n\nReview:"
    )
    return call_llm(prompt, temperature=0.2, num_predict=300)