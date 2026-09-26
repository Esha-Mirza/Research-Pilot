"""
Real search agent.

The previous version of this file returned a hardcoded template string
with the topic name dropped in -- it never actually looked anything up,
which is why every report came back generic and wrong regardless of
topic. This version pulls real grounding data from two free, no-API-key
sources:

  1. Wikipedia's REST summary API -- great for "what/who is X" grounding
     on people, places, companies, concepts.
  2. DuckDuckGo web search (via the `ddgs` package) -- current, broader
     web results for anything Wikipedia doesn't cover well.

Both are best-effort: if one fails (no network, rate limit, topic not
found) the other still runs, and the function always returns *something*
useful to downstream agents instead of raising.
"""

import requests

try:
    from ddgs import DDGS  # package name: ddgs (formerly duckduckgo_search)
except ImportError:  # pragma: no cover
    DDGS = None


def _wikipedia_summary(topic: str):
    """Fetch a short factual summary from Wikipedia, if a matching page exists."""
    try:
        resp = requests.get(
            "https://en.wikipedia.org/api/rest_v1/page/summary/"
            + requests.utils.quote(topic.replace(" ", "_")),
            timeout=10,
            headers={"User-Agent": "Research-Pilot/1.0"},
        )
        if resp.status_code != 200:
            return None
        data = resp.json()
        if data.get("type") == "disambiguation":
            return None
        extract = data.get("extract", "").strip()
        title = data.get("title", topic)
        return f"[Wikipedia: {title}]\n{extract}" if extract else None
    except requests.exceptions.RequestException:
        return None


def _web_search(topic: str, max_results: int = 6):
    """Fetch live web results via DuckDuckGo. Returns [] on any failure."""
    if DDGS is None:
        return []
    try:
        with DDGS() as ddgs:
            return list(ddgs.text(topic, max_results=max_results))
    except Exception:
        return []


def run(topic: str) -> str:
    sections = [f"SEARCH RESULTS FOR: {topic}\n"]
    found_anything = False

    wiki = _wikipedia_summary(topic)
    if wiki:
        sections.append(wiki)
        found_anything = True

    results = _web_search(topic)
    if results:
        found_anything = True
        lines = []
        for i, r in enumerate(results, 1):
            title = r.get("title", "").strip()
            body = r.get("body", "").strip()
            href = r.get("href", "").strip()
            lines.append(f"{i}. {title}\n   {body}\n   Source: {href}")
        sections.append("[Web search results]\n" + "\n".join(lines))

    if not found_anything:
        sections.append(
            "No live search results could be retrieved (no network access, "
            "or the `ddgs` package is not installed / DuckDuckGo rate-limited "
            "this request). Downstream agents should say clearly that they "
            "have no grounded information on this topic rather than "
            "inventing facts."
        )

    return "\n\n".join(sections)
