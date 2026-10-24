"""Knowledge base CLI.

  .venv/bin/python -m slack_bot.kb backfill --name "Create Listing" output/<run> [output/<run> ...]
      Record finished runs (oldest first) as versions of a feature.
  .venv/bin/python -m slack_bot.kb search "luxury price minimum FR-6"
      Keyword + ID search across all active test cases.
  .venv/bin/python -m slack_bot.kb url
      Print the index link and each feature's sheet link.
"""

from __future__ import annotations

import argparse
import logging
import os
import re
import sys
from pathlib import Path

from qa_tools.common import load_json

from ..net import prefer_ipv4
from ..sources import URL_RE, Source
from . import store
from .flow import KBSession, record
from .merge import find_feature, source_keys
from .search import search


def _run_inputs(run: Path) -> tuple[str, list[str], list[Source]]:
    text = (run / "input.md").read_text(encoding="utf-8")
    name = (re.search(r"^# Feature: (.+)$", text, re.MULTILINE) or [None, run.name])[1].strip()
    context = text.split("## Reference material")[0]
    links = list(dict.fromkeys(m.group(0).rstrip(".,;:)]}>") for m in URL_RE.finditer(context)))
    attachments = run / "attachments"
    sources = [Source("link", p.name, p) for p in sorted(attachments.iterdir())
               if p.is_file() and p.name != "kb-context.md"] if attachments.exists() else []
    return name, links, sources


def backfill(runs: list[Path], name: str | None) -> int:
    for run in runs:
        if not (run / "test-suite.json").exists():
            print(f"skip {run}: no test-suite.json")
            continue
        run_name, links, sources = _run_inputs(run)
        kb, _, _ = store.load()
        keys = source_keys(links, sources)
        feature = find_feature(kb, keys, name or run_name)
        session = KBSession(feature.feature_id if feature else None, feature.name if feature else None,
                            feature.version if feature else 0, keys, links)
        rec = record(session, name or run_name, load_json(run / "input-analysis.json"), load_json(run / "test-suite.json"), run, sources)
        print(f"{run.name}: {rec.result.feature.name} {rec.result.summary()}")
    print("Knowledge base:", store.tab_url(store.spreadsheet()))
    return 0


def main(argv: list[str]) -> int:
    prefer_ipv4()
    try:
        import certifi

        os.environ.setdefault("SSL_CERT_FILE", certifi.where())
    except ImportError:
        pass
    logging.basicConfig(level=logging.WARNING)
    parser = argparse.ArgumentParser(prog="slack_bot.kb", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("backfill")
    p.add_argument("runs", nargs="+", type=Path)
    p.add_argument("--name")
    p = sub.add_parser("search")
    p.add_argument("query")
    p.add_argument("--limit", type=int, default=10)
    sub.add_parser("url")
    args = parser.parse_args(argv)

    if args.cmd == "backfill":
        return backfill(args.runs, args.name)
    if args.cmd == "url":
        kb, info, _ = store.load()
        print("Index:", store.tab_url(info))
        for f in kb.features:
            print(f"  {f.name} v{f.version}: tests {f.tests_url or '(tab created on next save)'} · PRD {f.prd_url or '-'}")
        return 0
    kb, _, _ = store.load()
    for score, t in search(kb.tests, args.query, args.limit):
        print(f"{score:5.1f}  {t.feature} · {t.test_id} [{t.priority} {t.test_type}, {t.status}] {t.title}  ← {t.traces}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
