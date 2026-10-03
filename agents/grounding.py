"""
Deterministic grounding helpers shared by the agents.

A small local LLM (llama3.2:3b, TinyLlama, ...) is good at wording but
unreliable at *facts*: it rounds numbers, merges sources and invents
details. Instead of trusting it, every claim it produces is checked here,
in plain Python, against the exact source text the model was shown:

  * every claim must be supported by the source it cites (word overlap),
  * every figure in a claim (numbers, %, years) must appear in that source,
  * claims that fail are removed and reported instead of shipped.

Sources are dicts produced by search_agent.collect():
    {"id": 1, "title": ..., "url": ..., "domain": ..., "kind": "web"|"news",
     "date": "...", "evidence": "<title + excerpt shown to the LLM>"}
"""

import re
from urllib.parse import urlparse

# ----------------------------------------------------------------------------
# Text utilities
# ----------------------------------------------------------------------------

_STOP = set(
    """a an the and or of to in on for with by from at as is are was were be been
    being this that these those it its into about over under between than then so
    such not no nor can could should would may might will shall do does did has
    have had how what when where which who whom why vs versus also more most
    other their there they them his her our your you we i he she""".split()
)

# Words that describe the *kind* of query rather than its subject.
_GENERIC_TOPIC_WORDS = {"trends", "trend", "overview", "latest", "new", "current",
                        "recent", "future", "applications", "application"}

_BRACKET_TAG = re.compile(r"\[\s*S\d+(?:\s*[,;]\s*S?\d+)*\s*\]", re.I)
_BULLET_START = re.compile(r"^\s*(?:[-*•–—]|\d{1,2}[.)])\s+")
_NUMBER = re.compile(r"(?<![\w.])\d[\d,]*(?:\.\d+)?")


def _stem(word: str) -> str:
    return word[:5] if len(word) > 5 else word


def stems(text: str, drop_generic: bool = False) -> set:
    """Set of crude word stems for overlap comparisons (stopwords removed)."""
    out = set()
    for w in re.findall(r"[a-z0-9]+", text.lower()):
        if len(w) < 2 or w in _STOP:
            continue
        if drop_generic and w in _GENERIC_TOPIC_WORDS:
            continue
        out.add(_stem(w))
    return out


def topic_relevance(topic: str, text: str) -> float:
    """Fraction (0-1) of the topic's key words that appear in `text`."""
    t = stems(topic, drop_generic=True) or stems(topic)
    if not t:
        return 1.0
    return len(t & stems(text)) / len(t)


def domain_of(url: str) -> str:
    host = urlparse(url).netloc.lower().split("@")[-1].split(":")[0]
    return host[4:] if host.startswith("www.") else host


def is_error(text: str) -> bool:
    return isinstance(text, str) and text.startswith("Error:")


# ----------------------------------------------------------------------------
# Source tags like [S1]
# ----------------------------------------------------------------------------

def extract_tags(text: str) -> list:
    ids = []
    for m in _BRACKET_TAG.finditer(text):
        for n in re.findall(r"\d+", m.group()):
            if int(n) not in ids:
                ids.append(int(n))
    return ids


def strip_tags(text: str) -> str:
    return re.sub(r"\s+", " ", _BRACKET_TAG.sub("", text)).strip()


def format_tags(ids) -> str:
    return "".join(f"[S{i}]" for i in sorted(set(ids)))


# ----------------------------------------------------------------------------
# Numbers
# ----------------------------------------------------------------------------

def _norm_num(s: str) -> str:
    s = s.replace(",", "")
    if "." in s:
        return s.rstrip("0").rstrip(".")
    return s.lstrip("0") or "0"


def all_numbers(text: str) -> set:
    """Every number in `text`, normalised (used for source text)."""
    return {_norm_num(m.group()) for m in _NUMBER.finditer(strip_tags(text))}


def claim_numbers(text: str) -> set:
    """
    Numbers in a claim that must be verifiable. Bare single digits ("2 types")
    are ignored unless they are percentages/currency, because models freely
    swap "two"/"2" and list numbering would cause false alarms.
    """
    text = strip_tags(text)
    out = set()
    for m in _NUMBER.finditer(text):
        val = _norm_num(m.group())
        is_small_int = "." not in val and len(val) == 1
        if is_small_int:
            after = text[m.end():m.end() + 1]
            before = text[m.start() - 1:m.start()] if m.start() else ""
            if after != "%" and before not in "$€£":
                continue
        out.add(val)
    return out


# ----------------------------------------------------------------------------
# Parsing LLM output
# ----------------------------------------------------------------------------

def parse_bullets(text: str) -> list:
    """Extract bullet/numbered lines (joining wrapped continuation lines)."""
    items, current = [], None
    for line in text.splitlines():
        if not line.strip():
            continue
        if _BULLET_START.match(line):
            if current:
                items.append(current)
            current = _BULLET_START.sub("", line).strip()
        elif current is not None:
            current += " " + line.strip()
    if current:
        items.append(current)
    if items:
        return items
    # Model ignored the bullet format: fall back to long-enough lines.
    return [l.strip() for l in text.splitlines() if len(l.strip().split()) >= 6]


def split_sentences(text: str) -> list:
    text = re.sub(r"([.!?])\s*(\[\s*S\d+(?:\s*[,;]\s*S?\d+)*\s*\])", r" \2\1", text)
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9\"'(])", text.strip())
    return [p.strip() for p in parts if p.strip()]


# ----------------------------------------------------------------------------
# Verification
# ----------------------------------------------------------------------------

def _jaccard(a: set, b: set) -> float:
    return len(a & b) / len(a | b) if (a or b) else 0.0


def verify_claims(claims, sources, max_keep: int = 7, min_overlap: float = 0.45):
    """
    Check each claim against the sources. Returns (kept, removed):
      kept    -> ["claim text [S1][S3]", ...] (tags corrected/added)
      removed -> [(claim text, reason), ...]
    """
    by_id = {s["id"]: s for s in sources}
    ev_stems = {i: stems(s["evidence"]) for i, s in by_id.items()}
    ev_nums = {i: all_numbers(s["evidence"]) for i, s in by_id.items()}

    kept, kept_stems, removed = [], [], []
    for raw in claims:
        tags = [t for t in extract_tags(raw) if t in by_id]
        body = strip_tags(raw).strip(" -•*\t")
        if len(body.split()) < 5:
            removed.append((body or raw.strip(), "too short to verify"))
            continue

        cst = stems(body)
        if not cst:
            removed.append((body, "no checkable content"))
            continue

        def overlap(i):
            return len(cst & ev_stems[i]) / len(cst)

        best = max(by_id, key=overlap)
        support = [t for t in tags if overlap(t) >= min_overlap]
        if not support and overlap(best) >= min_overlap:
            support = [best]  # missing/wrong tag: re-attribute to the true source
        if not support:
            removed.append((body, "not supported by the retrieved sources"))
            continue

        allowed = set().union(*(ev_nums[i] for i in support))
        missing = sorted(n for n in claim_numbers(body) if n not in allowed)
        if missing:
            removed.append((body, f"figure(s) {', '.join(missing)} not found in the cited source"))
            continue

        if any(_jaccard(cst, k) > 0.8 for k in kept_stems):
            continue  # near-duplicate of a bullet we already kept

        kept.append(f"{body} {format_tags(support)}")
        kept_stems.append(cst)
        if len(kept) >= max_keep:
            break
    return kept, removed


def extractive_findings(topic: str, sources, limit: int = 5, exclude=()):
    """
    Verbatim, most-relevant sentences from the sources (round-robin so one
    source can't dominate). 100% grounded by construction; used to top up or
    replace LLM bullets that failed verification.
    """
    exclude_stems = [stems(e) for e in exclude]
    per_source = []
    for s in sources:
        excerpt = s["evidence"].split("\n", 1)[-1]  # drop the title line
        cands = []
        for sent in split_sentences(excerpt):
            n_words = len(sent.split())
            if not 8 <= n_words <= 45:
                continue
            rel = topic_relevance(topic, sent)
            if rel <= 0:
                continue
            st = stems(sent)
            if any(_jaccard(st, e) > 0.7 for e in exclude_stems):
                continue
            cands.append((rel + (0.1 if _NUMBER.search(sent) else 0), sent))
        cands.sort(key=lambda c: -c[0])
        per_source.append((s["id"], [c[1] for c in cands]))

    out, round_ = [], 0
    while len(out) < limit and any(len(c) > round_ for _, c in per_source):
        for sid, cands in per_source:
            if len(cands) > round_ and len(out) < limit:
                out.append(f"{cands[round_].rstrip()} [S{sid}]")
        round_ += 1
    return out


def drop_unsupported_sentences(text: str, allowed_numbers: set, ref_text: str,
                               valid_ids, min_overlap: float = 0.35) -> str:
    """
    Remove sentences from LLM-written prose that contain a figure not present
    in the verified findings, or that share too little vocabulary with them
    (i.e. new, unsourced claims). Invalid [S#] tags are discarded.
    """
    ref = stems(ref_text)
    out = []
    for sent in split_sentences(text):
        clean = strip_tags(sent)
        if len(clean.split()) < 4:
            continue
        if any(n not in allowed_numbers for n in claim_numbers(clean)):
            continue
        cst = stems(clean)
        if cst and len(cst & ref) / len(cst) < min_overlap:
            continue
        tags = [t for t in extract_tags(sent) if t in valid_ids]
        out.append((clean + (" " + format_tags(tags) if tags else "")).strip())
    return " ".join(out)


# ----------------------------------------------------------------------------
# Evidence formatting + confidence
# ----------------------------------------------------------------------------

def evidence_block(sources, max_chars_each: int = 1200) -> str:
    blocks = []
    for s in sources:
        ev = s["evidence"]
        if len(ev) > max_chars_each:
            ev = ev[:max_chars_each].rsplit(" ", 1)[0] + " ..."
        blocks.append(f"[S{s['id']}] ({s['domain']}) {ev}")
    return "\n\n".join(blocks)


_TRUSTED_SUFFIXES = (".gov", ".edu", ".int", ".mil", ".ac.uk", ".gov.uk", ".edu.pk", ".gov.pk")
_TRUSTED_SITES = {
    "nature.com", "science.org", "who.int", "nih.gov", "nasa.gov", "reuters.com",
    "apnews.com", "bbc.com", "bbc.co.uk", "ieee.org", "acm.org", "arxiv.org",
    "sciencedirect.com", "springer.com", "oecd.org", "worldbank.org", "imf.org",
    "un.org", "europa.eu", "hbr.org", "economist.com", "ft.com", "nytimes.com",
    "theguardian.com", "bloomberg.com", "statista.com", "mckinsey.com",
    "britannica.com", "mayoclinic.org", "cdc.gov", "iea.org", "irena.org",
}


def is_trusted(domain: str) -> bool:
    return domain.endswith(_TRUSTED_SUFFIXES) or any(
        domain == d or domain.endswith("." + d) for d in _TRUSTED_SITES
    )


def assess(sources, claims) -> dict:
    """Transparent, rule-based confidence level for the final output."""
    domains = {s["domain"] for s in sources}
    cited = set()
    for c in claims:
        cited.update(extract_tags(c))
    trusted = sum(1 for s in sources if is_trusted(s["domain"]))

    notes = []
    if not sources or not claims:
        level = "None"
        notes.append("no verified claims could be produced")
    else:
        level = "Low"
        if len(sources) >= 2 and len(claims) >= 2:
            level = "Medium"
        if (len(sources) >= 3 and len(domains) >= 3 and len(claims) >= 4
                and len(cited) >= 2 and trusted >= 1):
            level = "High"
        if len(sources) < 3:
            notes.append(f"only {len(sources)} source(s) retrieved")
        if len(domains) < 2:
            notes.append("all sources come from a single website")
        if len(cited) < 2:
            notes.append("findings rest on a single source")
        if trusted == 0:
            notes.append("no institutional/major-publisher source among them")
    return {"level": level, "notes": notes, "domains": len(domains),
            "trusted": trusted, "cited": len(cited)}
