import re
import sys
import os
from datetime import date
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents.base import call_llm, is_error
from agents import grounding

NO_DATA_REPORT = (
    "No report could be produced: the search step returned no usable sources "
    "for this topic, and a report written without sources would be invented. "
    "Check your internet connection or try rewording the topic."
)


def _review_caveats(feedback: str) -> list:
    """Pull 'Caution' notes and non-empty AI-review bullets out of the feedback."""
    caveats = []
    for line in feedback.splitlines():
        s = line.strip()
        if s.startswith("- Caution:"):
            caveats.append(s[2:].replace("Caution: ", "").rstrip(".").capitalize() + ".")
    if "AI REVIEW" in feedback:
        for line in feedback.split("AI REVIEW", 1)[1].splitlines():
            s = line.strip()
            if re.match(r"^[-*•]\s+", s) and "none found" not in s.lower() and len(s) > 12:
                caveats.append(re.sub(r"^[-*•]\s+", "", s))
    return caveats[:6]


def run(summary: str, feedback: str, sources: list, topic: str = "") -> str:
    if is_error(summary):
        return summary
    if not sources:
        return NO_DATA_REPORT

    findings = grounding.parse_bullets(summary)
    if not findings:
        return NO_DATA_REPORT
    info = grounding.assess(sources, findings)
    valid_ids = {s["id"] for s in sources}
    findings_text = "\n".join(f"- {f}" for f in findings)

    prompt = (
        f"Write a short research report on: {topic or 'the topic'}\n\n"
        "VERIFIED FINDINGS (the only facts you may use):\n"
        f"{findings_text}\n\n"
        "RULES:\n"
        "- Use ONLY facts stated in the verified findings. Do not add any "
        "statistic, date, name or claim that is not there.\n"
        "- Do not round or change numbers.\n"
        "- Keep the [S#] source tags on the sentences that use them.\n"
        "- If the findings are thin, say so plainly instead of padding.\n"
        "- Plain text only, no markdown symbols.\n\n"
        "Write exactly two parts, using these labels:\n"
        "EXECUTIVE SUMMARY: (3 to 4 sentences)\n"
        "ANALYSIS: (1 short paragraph on how the findings fit together, "
        "where sources agree or differ, and what remains unclear)\n"
    )
    raw = call_llm(prompt, temperature=0.2, num_predict=600)
    if is_error(raw):
        return raw

    m = re.search(r"EXECUTIVE SUMMARY:?(.*?)(?:ANALYSIS:?(.*))?$", raw, re.S | re.I)
    exec_raw, analysis_raw = (m.group(1), m.group(2) or "") if m else (raw, "")

    allowed = grounding.all_numbers(findings_text)
    allowed.add(str(date.today().year))
    clean = lambda t: grounding.drop_unsupported_sentences(
        t.strip(), allowed, findings_text + " " + topic, valid_ids)
    executive = clean(exec_raw)
    analysis = clean(analysis_raw)
    if not executive:  # model drifted: build the overview from verified findings
        executive = " ".join(grounding.strip_tags(f).rstrip(".") + "." for f in findings[:3])

    caveats = _review_caveats(feedback)
    cited = sorted({t for f in findings for t in grounding.extract_tags(f)} & valid_ids)
    ref_sources = [s for s in sources if s["id"] in cited] or sources

    parts = [
        f"RESEARCH REPORT: {topic}" if topic else "RESEARCH REPORT",
        f"Generated {date.today().isoformat()} from {len(sources)} live web source(s). "
        f"Confidence: {info['level']}.",
        "EXECUTIVE SUMMARY\n" + executive,
        "KEY FINDINGS\n" + "\n".join(f"- {f}" for f in findings),
    ]
    if analysis:
        parts.append("ANALYSIS\n" + analysis)
    if caveats:
        parts.append("LIMITATIONS AND CAVEATS\n" + "\n".join(f"- {c}" for c in caveats))
    parts.append("SOURCES\n" + "\n".join(
        f"[S{s['id']}] {s['title']} - {s['url']}" for s in ref_sources))
    return "\n\n".join(parts)
