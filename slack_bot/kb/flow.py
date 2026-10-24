"""Knowledge base around one run: brief the agent before generation, record the new version afterwards."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path

from .. import google_sheets as G
from ..sources import Source
from . import store
from .context import build_context, write_context
from .merge import VersionResult, apply_run, find_feature, source_keys, suite_from_kb
from .model import Feature

log = logging.getLogger("slack_bot.kb")
QUERY_CHARS = 6000  # how much source text feeds the similar-test search


@dataclass
class KBSession:
    feature_id: str | None
    feature_name: str | None
    version: int
    keys: list[str]
    links: list[str]
    edited: list[str] = field(default_factory=list)


@dataclass
class KBRecord:
    result: VersionResult
    kb_url: str          # the feature's "<name> – Tests" tab in the knowledge base
    snapshot_url: str = ""
    index_url: str = ""  # the "Test Case Knowledge Base" index


def enabled() -> bool:
    return G.is_configured()


def _query(feature_context: str, sources: list[Source]) -> str:
    text = [feature_context]
    for s in sources:
        if s.ok and s.kind != "kb" and s.path.suffix.lower() in (".md", ".txt"):
            text.append(s.path.read_text(encoding="utf-8", errors="replace")[:QUERY_CHARS])
    return "\n".join(text)[:QUERY_CHARS * 3]


def prepare(name: str, feature_context: str, links: list[str], sources: list[Source], run_dir: Path) -> tuple[KBSession, list[Source]]:
    """Find the feature and add the knowledge-base briefing to the run's sources (as kind 'kb')."""
    kb, _, edited = store.load()
    keys = source_keys(links, sources)
    feature = find_feature(kb, keys, name)
    session = KBSession(feature.feature_id if feature else None, feature.name if feature else None,
                        feature.version if feature else 0, keys, links, edited)
    text = build_context(kb, feature, _query(feature_context, sources))
    if text:
        path = write_context(run_dir, text)
        label = f"Knowledge base: {feature.name} v{feature.version}" if feature else "Knowledge base: similar test cases"
        sources = [*sources, Source("kb", label, path, note="knowledge base")]
    log.info("kb: run %s -> %s", run_dir.name, f"{feature.name} v{feature.version}" if feature else "new feature")
    return session, sources


def record(session: KBSession, name: str, analysis: dict, suite: dict, run_dir: Path, sources: list[Source]) -> KBRecord:
    """Fold the run in as the next version, save a snapshot sheet of the current tests, write the knowledge base."""
    with store.WRITE_LOCK:
        kb, info, _ = store.load()  # fresh copy: includes edits people made while the run was going
        feature: Feature | None = kb.feature(session.feature_id) if session.feature_id else find_feature(kb, session.keys, name)
        described = "; ".join(s.label for s in sources if s.ok and s.kind != "kb")
        result = apply_run(kb, name=feature.name if feature else name, keys=session.keys, links=session.links,
                           analysis=analysis, suite=suite, run_name=run_dir.name, sources_desc=described[:1000], feature=feature)
        snapshot = ""
        try:
            snapshot_suite = suite_from_kb(kb, result.feature, suite)
            snapshot = G.create_test_case_sheet(snapshot_suite, analysis, f"{result.feature.name} v{result.version}", run_dir,
                                                changes=result.changes())
        except G.GoogleSheetsError as exc:
            log.warning("kb: snapshot sheet failed for %s: %s", run_dir.name, exc)
        result.feature.latest_snapshot = snapshot
        kb.changelog[-1].snapshot = snapshot
        store.save(kb, info, [result.feature.feature_id])
    log.info("kb: recorded %s %s", result.feature.name, result.summary())
    index_url = store.tab_url(info)
    return KBRecord(result, result.feature.tests_url or index_url, snapshot, index_url)
