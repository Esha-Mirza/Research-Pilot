import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents.base import call_llm


def run(content: str) -> str:
    prompt = (
        "You are a precise research summarizer. Read the findings below and "
        "write exactly 3 concise bullet points capturing the most important, "
        "concrete facts. Use ONLY information present in the findings — do "
        "not add outside knowledge, statistics, or claims that aren't "
        "stated there. If the findings say no data could be retrieved, your "
        "summary must say plainly that no grounded information is "
        "available, instead of inventing content. Do not add commentary, "
        "headings, or repeat these instructions.\n\n"
        f"Findings:\n{content}\n\nSummary:"
    )
    return call_llm(prompt, temperature=0.2, num_predict=300)