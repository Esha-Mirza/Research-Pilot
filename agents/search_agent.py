"""
Search agent.

Pulls live results from DuckDuckGo (via the `ddgs` package, no API key) and
turns them into numbered, citable sources:

  1. Runs a few differently-worded queries (+ a news query for recency).
  2. Drops Wikipedia/mirrors and social/video sites, de-duplicates by URL and
     limits each website to 2 results.
  3. Ranks by topic relevance and source credibility.
  4. Downloads the top pages and extracts the paragraphs most relevant to the
     topic (search snippets alone are too thin to ground a summary).
  5. Re-checks relevance on the extracted text and keeps the best sources.

Everything is best-effort: a failed query/page never raises, and the agent
always returns something downstream agents can handle honestly.
"""

import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from html.parser import HTMLParser

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests

from agents import grounding

try:
    from ddgs import DDGS  # package name: ddgs (formerly duckduckgo_search)
except ImportError:  # pragma: no cover
    DDGS = None

MAX_SOURCES = int(os.environ.get("RESEARCH_MAX_SOURCES", "6"))
EXCERPT_CHARS = int(os.environ.get("RESEARCH_EXCERPT_CHARS", "1100"))
_MAX_PER_DOMAIN = 2
_MAX_PAGE_BYTES = 400_000

# Wikipedia (and its mirrors) are intentionally excluded, plus sites that are
# social/video feeds or user-generated Q&A and rarely hold citable facts.
_BLOCKED_DOMAINS = (
    "wikipedia.org", "wikiwand.com", "wikimedia.org", "wikidata.org",
    "dbpedia.org", "wikitia.com",
    "facebook.com", "instagram.com", "tiktok.com", "pinterest.com",
    "youtube.com", "youtu.be", "x.com", "twitter.com", "quora.com",
)
_LOW_QUALITY = ("medium.com", "blogspot.com", "wordpress.com")

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36 Research-Pilot/1.1"
    ),
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "en-US,en;q=0.8",
}

_BOILERPLATE = re.compile(
    r"cookie|subscribe|newsletter|all rights reserved|privacy policy|"
    r"terms of (use|service)|sign up|log ?in|javascript|advertisement|"
    r"click here|share this|follow us|accept all|read more|skip to",
    re.I,
)


# ----------------------------------------------------------------------------
# Searching
# ----------------------------------------------------------------------------

def _domain_matches(domain: str, blocked) -> bool:
    return any(domain == d or domain.endswith("." + d) for d in blocked)


def _ddg(call, *args, **kwargs):
    """Run a DDGS call; retry once (rate limits are common), [] on failure."""
    if DDGS is None:
        return []
    for attempt in range(2):
        try:
            with DDGS() as ddgs:
                return list(getattr(ddgs, call)(*args, **kwargs)) or []
        except Exception:
            if attempt == 0:
                time.sleep(1.0)
    return []


def _queries(topic: str) -> list:
    return [topic, f"{topic} overview key facts"]


def _gather(topic: str) -> list:
    hits = []
    for q in _queries(topic):
        for r in _ddg("text", q, max_results=8):
            hits.append({
                "title": (r.get("title") or "").strip(),
                "url": (r.get("href") or "").strip(),
                "snippet": (r.get("body") or "").strip(),
                "kind": "web", "date": "",
            })
    for r in _ddg("news", topic, max_results=4):
        hits.append({
            "title": (r.get("title") or "").strip(),
            "url": (r.get("url") or "").strip(),
            "snippet": (r.get("body") or "").strip(),
            "kind": "news", "date": (r.get("date") or "")[:10],
        })
    return hits


def _url_key(url: str) -> str:
    return re.sub(r"^https?://(www\.)?", "", url.lower()).split("#")[0].split("?")[0].rstrip("/")


def _rank(topic: str, hits: list) -> list:
    seen, per_domain, ranked = set(), {}, []
    for idx, h in enumerate(hits):
        url = h["url"]
        if not url.startswith(("http://", "https://")):
            continue
        dom = grounding.domain_of(url)
        key = _url_key(url)
        if _domain_matches(dom, _BLOCKED_DOMAINS) or key in seen:
            continue
        seen.add(key)
        h["domain"] = dom
        rel = grounding.topic_relevance(topic, h["title"] + " " + h["snippet"])
        score = 2.0 * rel + 0.3 / (1 + idx)
        if grounding.is_trusted(dom):
            score += 0.35
        if _domain_matches(dom, _LOW_QUALITY):
            score -= 0.2
        h["score"] = score
        ranked.append(h)
    ranked.sort(key=lambda h: -h["score"])

    out = []
    for h in ranked:  # cap results per website *after* ranking
        if per_domain.get(h["domain"], 0) >= _MAX_PER_DOMAIN:
            continue
        per_domain[h["domain"]] = per_domain.get(h["domain"], 0) + 1
        out.append(h)
    return out


# ----------------------------------------------------------------------------
# Page text extraction
# ----------------------------------------------------------------------------

class _TextBlocks(HTMLParser):
    """Collects visible text blocks, skipping navigation/scripts/footers."""

    _SKIP = {"script", "style", "noscript", "nav", "footer", "header", "aside",
             "form", "svg", "iframe", "button", "template", "select"}
    _BREAK = {"p", "li", "div", "br", "tr", "section", "article", "blockquote",
              "h1", "h2", "h3", "h4", "h5", "h6", "td", "dd", "dt"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.blocks, self._buf, self._skip = [], [], 0

    def _flush(self):
        text = re.sub(r"\s+", " ", "".join(self._buf)).strip()
        self._buf = []
        if text:
            self.blocks.append(text)

    def handle_starttag(self, tag, attrs):
        if tag in self._SKIP:
            self._flush()
            self._skip += 1
        elif tag in self._BREAK:
            self._flush()

    def handle_endtag(self, tag):
        if tag in self._SKIP:
            self._flush()
            self._skip = max(0, self._skip - 1)
        elif tag in self._BREAK:
            self._flush()

    def handle_data(self, data):
        if not self._skip:
            self._buf.append(data)


def _fetch_paragraphs(url: str) -> list:
    """Download a page and return its substantive paragraphs ([] on failure)."""
    try:
        resp = requests.get(url, headers=_HEADERS, timeout=(4, 8), stream=True)
        ctype = resp.headers.get("Content-Type", "").lower()
        if resp.status_code != 200 or "html" not in ctype:
            resp.close()
            return []
        raw = b""
        for chunk in resp.iter_content(16384):
            raw += chunk
            if len(raw) > _MAX_PAGE_BYTES:
                break
        resp.close()
        enc = requests.utils.get_encoding_from_headers(resp.headers)
        html = raw.decode(enc if enc and enc.lower() != "iso-8859-1" else "utf-8",
                          errors="replace")
        parser = _TextBlocks()
        parser.feed(html)
        parser.close()
    except Exception:
        return []

    paras, seen = [], set()
    for b in parser.blocks:
        if len(b.split()) < 12 or len(b) > 1500 or _BOILERPLATE.search(b):
            continue
        if b in seen:
            continue
        seen.add(b)
        paras.append(b)
    return paras


def _clip(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    cut = text[:limit]
    end = max(cut.rfind(". "), cut.rfind("! "), cut.rfind("? "))
    if end >= limit * 0.6:
        return cut[:end + 1]
    return cut.rsplit(" ", 1)[0] + " ..."


def _select_excerpt(topic: str, paragraphs: list, max_chars: int) -> str:
    """Keep the paragraphs most relevant to the topic, in original order."""
    scored = [(grounding.topic_relevance(topic, p), -i, i, p)
              for i, p in enumerate(paragraphs)]
    scored.sort(reverse=True)
    chosen, total = [], 0
    for rel, _, i, p in scored:
        if rel <= 0:
            break
        room = max_chars - total
        if room < 150:
            break
        p = _clip(p, min(len(p), room))
        chosen.append((i, p))
        total += len(p) + 1
    chosen.sort()
    return " ".join(p for _, p in chosen)


# ----------------------------------------------------------------------------
# Public API
# ----------------------------------------------------------------------------

def collect(topic: str, max_sources: int = None) -> list:
    """Return up to `max_sources` citable source dicts (possibly empty)."""
    topic = " ".join(topic.split())[:200]
    max_sources = max_sources or MAX_SOURCES

    candidates = _rank(topic, _gather(topic))[: max_sources + 3]
    if not candidates:
        return []

    with ThreadPoolExecutor(max_workers=6) as pool:
        pages = list(pool.map(lambda c: _fetch_paragraphs(c["url"]), candidates))

    n_kw = len(grounding.stems(topic, drop_generic=True) or grounding.stems(topic))
    threshold = 1.0 if n_kw <= 1 else 0.5

    scored = []
    for cand, paras in zip(candidates, pages):
        body = _select_excerpt(topic, paras, EXCERPT_CHARS) if paras else ""
        if not body:
            body = _clip(cand["snippet"], EXCERPT_CHARS)
        if not body:
            continue
        title = cand["title"] or cand["domain"]
        rel = grounding.topic_relevance(topic, title + " " + body)
        scored.append((rel, cand, title, body, bool(paras)))

    kept = [x for x in scored if x[0] >= threshold]
    if not kept:  # nothing clearly on-topic: keep only partial matches, never zero-overlap
        kept = [x for x in scored if x[0] > 0][:3]

    # Preserve the ranking order established above, but prefer on-topic text.
    order = {id(c): i for i, c in enumerate(candidates)}
    kept.sort(key=lambda x: (-round(x[0], 1), order[id(x[1])]))

    sources = []
    for rel, cand, title, body, fetched in kept[:max_sources]:
        sources.append({
            "id": len(sources) + 1,
            "title": title,
            "url": cand["url"],
            "domain": cand["domain"],
            "kind": cand["kind"],
            "date": cand["date"],
            "fetched_page": fetched,
            "evidence": f"{title}\n{body}",
        })
    return sources


def format_results(topic: str, sources: list) -> str:
    """Human-readable (and LLM-readable) rendering of the sources."""
    head = (f"SEARCH RESULTS FOR: {topic}\n"
            f"Retrieved: {date.today().isoformat()} | Sources: {len(sources)}")
    if not sources:
        return head + (
            "\n\nNo live search results could be retrieved (no network access, "
            "no relevant pages found, the `ddgs` package is not installed, or "
            "DuckDuckGo rate-limited this request). Downstream agents should "
            "say clearly that they have no grounded information on this topic "
            "rather than inventing facts."
        )

    blocks = []
    for s in sources:
        label = "News" if s["kind"] == "news" else "Web"
        when = f" | {s['date']}" if s["date"] else ""
        excerpt = s["evidence"].split("\n", 1)[1]
        blocks.append(
            f"[S{s['id']}] {s['title']}\n"
            f"Source: {s['url']}  ({s['domain']} | {label}{when})\n"
            f"Excerpt: {excerpt}"
        )
    return head + "\n\n" + "\n\n".join(blocks)


def run(topic: str) -> str:
    return format_results(topic, collect(topic))
