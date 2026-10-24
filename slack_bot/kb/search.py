"""Keyword + ID search over knowledge-base test cases (BM25, standard library only)."""

from __future__ import annotations

import math
import re
from collections import Counter

from .model import OBSOLETE, KBTest

_ID = re.compile(r"\b(?:FR|NFR|BR|AC|US|UC|REQ|TC)-[A-Z0-9]+(?:[-.][A-Z0-9]+)*\b", re.IGNORECASE)
_WORD = re.compile(r"[a-z0-9₹]+")
_STOP = set("a an the and or of to in on for with is are be by as at it its this that from into your you not no "
            "when then if can should must will user page step steps click enter open test case shown display displayed".split())


def tokens(text: str) -> list[str]:
    return [w for w in _WORD.findall((text or "").lower()) if w not in _STOP and len(w) > 1]


def _doc_text(t: KBTest) -> str:
    return " ".join([t.title, t.title, t.description, t.steps, t.expected, t.traces, t.feature])


def search(tests: list[KBTest], query: str, limit: int = 10, exclude_feature: str | None = None,
           include_obsolete: bool = False) -> list[tuple[float, KBTest]]:
    """Rank tests for a query. IDs in the query (FR-6, TC-LUXURY-001) are matched exactly and boosted."""
    pool = [t for t in tests if (include_obsolete or t.status != OBSOLETE) and t.feature_id != exclude_feature]
    if not pool:
        return []
    q_ids = {m.group(0).upper() for m in _ID.finditer(query or "")}
    q_terms = set(tokens(_ID.sub(" ", query or "")))
    docs = [Counter(tokens(_doc_text(t))) for t in pool]
    avg = sum(sum(d.values()) for d in docs) / len(docs) or 1
    df = Counter(term for d in docs for term in d)
    n = len(docs)
    k1, b = 1.4, 0.75

    scored = []
    for t, d in zip(pool, docs):
        length = sum(d.values()) or 1
        score = 0.0
        for term in q_terms:
            tf = d.get(term)
            if tf:
                idf = math.log(1 + (n - df[term] + 0.5) / (df[term] + 0.5))
                score += idf * tf * (k1 + 1) / (tf + k1 * (1 - b + b * length / avg))
        ids = {t.test_id.upper(), *(r.upper() for r in t.refs())}
        score += 10.0 * len(q_ids & ids)
        if score > 0:
            scored.append((score, t))
    scored.sort(key=lambda x: (-x[0], x[1].feature_id, x[1].test_id))
    return scored[:limit]
