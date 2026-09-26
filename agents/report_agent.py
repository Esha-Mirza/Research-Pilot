import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents.base import call_llm


def run(summary: str, feedback: str) -> str:
    prompt = (
        "Write a short, well-organized research report using only the summary "
        "and reviewer feedback below — don't invent facts that aren't in them. "
        "Structure it as: one title line, then 2-3 short paragraphs.\n\n"
        f"Summary:\n{summary}\n\nReviewer feedback:\n{feedback}\n\nReport:"
    )
    return call_llm(prompt, temperature=0.3, num_predict=500)