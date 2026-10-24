"""Identify the feature a run belongs to and fold a new run into the knowledge base as the next version.

Rules (agreed with the user):
- Same feature = any shared source key (Confluence page, Figma file, document URL); otherwise same name.
- Reuse + update: unchanged tests keep their row; AI-draft tests the agent rewrote are updated; new tests are
  added; tests whose requirements were all removed become Obsolete. Active tests the agent dropped while
  their requirements still exist are kept (coverage is never lost silently).
- Reviewed tests (edited by a person) are never overwritten: if the agent proposes a change or a traced
  requirement changed, the row becomes "Needs review" with a note and the proposal in "Suggested update".
- A test a person marked Obsolete stays Obsolete.
"""

from __future__ import annotations

import re
import urllib.parse
from dataclasses import dataclass, field
from datetime import date

from ..google_sheets import doc_priority, doc_test_type, test_description
from ..sources import Source, parse_figma
from qa_tools.common import test_data_text

from .model import (ACTIVE, NEEDS_REVIEW, OBSOLETE, PRIORITY_TO_SUITE, REVIEWED, SHEET_TO_SUITE_TYPE, ChangeEntry,
                    Feature, KBRequirement, KBTest, KnowledgeBase)

_CONFLUENCE_FILE = re.compile(r"^confluence-(\d+)-")
_GDOC = re.compile(r"docs\.google\.com/document/d/([A-Za-z0-9_-]+)")


# ---------------------------------------------------------------- feature identity

def normalize_name(name: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", (name or "").lower()))


def link_key(url: str) -> str:
    figma = parse_figma(url)
    if figma:
        return f"figma:{figma[0]}"
    if m := _GDOC.search(url):
        return f"gdoc:{m.group(1)}"
    p = urllib.parse.urlparse(url)
    if m := re.search(r"/pages/(\d+)", p.path):
        return f"confluence:{m.group(1)}"
    return f"url:{(p.hostname or '').lower()}{p.path.rstrip('/')}"


def source_keys(links: list[str], sources: list[Source]) -> list[str]:
    """Stable keys for everything the run read: linked URLs plus resolved Confluence page ids."""
    keys = [link_key(u) for u in links]
    for src in sources:
        if src.ok and (m := _CONFLUENCE_FILE.match(src.path.name)):
            keys.append(f"confluence:{m.group(1)}")
    return list(dict.fromkeys(keys))


def find_feature(kb: KnowledgeBase, keys: list[str], name: str) -> Feature | None:
    """Most shared source keys wins; with no shared keys, an exact (normalized) name match."""
    wanted = set(keys)
    best, overlap = None, 0
    for f in kb.features:
        shared = len(wanted & set(f.source_keys))
        if shared > overlap:
            best, overlap = f, shared
    if best:
        return best
    norm = normalize_name(name)
    return next((f for f in kb.features if norm and normalize_name(f.name) == norm), None)


# ---------------------------------------------------------------- converting a run

def tests_from_suite(suite: dict, feature: Feature) -> list[KBTest]:
    rows = []
    for tc in suite["test_cases"]:
        rows.append(KBTest(
            feature_id=feature.feature_id, feature=feature.name, test_id=tc["id"], title=tc["scenario"],
            description=test_description(tc), test_type=doc_test_type(tc), priority=doc_priority(tc),
            preconditions="\n".join(f"• {p}" for p in tc["preconditions"]) or "None",
            test_data=test_data_text(tc.get("test_data")) or "None",
            steps="\n".join(f"{n}. {s}" for n, s in enumerate(tc["steps"], 1)),
            expected=tc["expected_result"], traces=", ".join(tc.get("source_refs", []))))
    return rows


def requirements_from_analysis(analysis: dict) -> dict[str, tuple[str, str, str]]:
    """id -> (kind, text, source_ref) for requirements, acceptance criteria and business rules."""
    out = {}
    for key, kind in (("requirements", "Requirement"), ("acceptance_criteria", "Acceptance criterion"),
                      ("business_rules", "Business rule")):
        for item in analysis.get(key, []):
            out[item["id"]] = (kind, item["text"], item.get("source_ref", ""))
    return out


def _same_text(a: str, b: str) -> bool:
    return " ".join(a.lower().split()) == " ".join(b.lower().split())


def _proposal(t: KBTest) -> str:
    return f"Title: {t.title}\nSteps:\n{t.steps}\nExpected: {t.expected}\nPriority: {t.priority} · Type: {t.test_type}"


# ---------------------------------------------------------------- applying a run

@dataclass
class VersionResult:
    feature: Feature
    version: int
    is_new_feature: bool
    unchanged: list[str] = field(default_factory=list)
    updated: list[str] = field(default_factory=list)
    added: list[str] = field(default_factory=list)
    obsolete: list[str] = field(default_factory=list)
    needs_review: list[str] = field(default_factory=list)
    kept: list[str] = field(default_factory=list)  # active tests the agent dropped but whose requirements still exist
    requirement_changes: dict[str, list[str]] = field(default_factory=dict)  # new/changed/removed -> ids

    def summary(self) -> str:
        if self.is_new_feature:
            return f"v{self.version} (new feature): {len(self.added)} test cases added"
        parts = [f"{len(self.unchanged) + len(self.kept)} unchanged", f"{len(self.updated)} updated", f"{len(self.added)} added",
                 f"{len(self.obsolete)} obsolete"]
        if self.needs_review:
            parts.append(f"{len(self.needs_review)} need review")
        req = ", ".join(f"{len(v)} {k}" for k, v in self.requirement_changes.items() if v)
        return f"v{self.version}: " + " · ".join(parts) + (f" (requirements: {req})" if req else "")

    def changes(self) -> dict[str, str]:
        """Test ID -> what happened in this version (the fresh sheet's Change column)."""
        out = {tid: "Unchanged" for tid in self.unchanged + self.kept}
        out.update({tid: "Updated" for tid in self.updated})
        out.update({tid: "New" for tid in self.added})
        out.update({tid: "Needs review" for tid in self.needs_review})
        return out

    def active_tests(self, kb: KnowledgeBase) -> list[KBTest]:
        return [t for t in kb.tests_for(self.feature.feature_id) if t.status != OBSOLETE]


def apply_run(kb: KnowledgeBase, *, name: str, keys: list[str], links: list[str], analysis: dict, suite: dict,
              run_name: str, sources_desc: str = "", feature: Feature | None = None, today: str | None = None) -> VersionResult:
    today = today or date.today().isoformat()
    is_new = feature is None
    if is_new:
        feature = Feature(kb.next_feature_id(), name)
        kb.features.append(feature)
    feature.version += 1
    v = f"v{feature.version}"
    feature.source_keys = list(dict.fromkeys(feature.source_keys + keys))
    feature.source_links = list(dict.fromkeys(feature.source_links + links))
    feature.updated = today
    result = VersionResult(feature, feature.version, is_new)

    # Requirements: compare by ID.
    prev_reqs = {r.req_id: r for r in kb.requirements_for(feature.feature_id) if r.change != "removed"}
    new_reqs = requirements_from_analysis(analysis)
    changes = {"new": [], "changed": [], "removed": []}
    rows = []
    for rid, (kind, text, src) in new_reqs.items():
        prev = prev_reqs.get(rid)
        if prev is None:
            change = "new"
        elif not _same_text(prev.text, text):
            change = "changed"
        else:
            change = "unchanged"
        if change != "unchanged":
            changes[change].append(rid)
        changed_in = v if change != "unchanged" else (prev.changed_in or v)
        rows.append(KBRequirement(feature.feature_id, feature.name, rid, kind, text, src, change, changed_in))
    for rid, prev in prev_reqs.items():
        if rid not in new_reqs:
            changes["removed"].append(rid)
            rows.append(KBRequirement(feature.feature_id, feature.name, rid, prev.kind, prev.text, prev.source, "removed", v))
    if is_new:
        changes = {"new": [], "changed": [], "removed": []}  # a first version has nothing to compare against
    result.requirement_changes = changes
    kb.requirements = [r for r in kb.requirements if r.feature_id != feature.feature_id] + rows
    changed_or_removed = set(changes["changed"]) | set(changes["removed"])

    # Tests: compare by Test ID.
    prev_tests = {t.test_id: t for t in kb.tests_for(feature.feature_id)}
    merged: list[KBTest] = []
    seen = set()
    for new in tests_from_suite(suite, feature):
        seen.add(new.test_id)
        prev = prev_tests.get(new.test_id)
        if prev is None:
            new.added_in = new.changed_in = v
            result.added.append(new.test_id)
            merged.append(new)
        elif prev.status == OBSOLETE and prev.origin == REVIEWED:
            merged.append(prev)  # a person retired it; respect that
        elif prev.origin == REVIEWED:
            hit = sorted(set(prev.refs()) & changed_or_removed)
            proposes_change = new.content() != prev.content()
            if proposes_change or hit:
                notes = [f"{', '.join(hit)} changed in {v}." if hit else ""]
                notes.append("The AI proposes an update (see Suggested update)." if proposes_change
                             else "Check this test still matches.")
                prev.status = NEEDS_REVIEW
                prev.review_note = " ".join(n for n in notes if n)
                prev.suggested_update = _proposal(new) if proposes_change else ""
                result.needs_review.append(prev.test_id)
            else:
                result.unchanged.append(prev.test_id)
            merged.append(prev)
        elif new.content() == prev.content():
            prev.status = ACTIVE if prev.status != NEEDS_REVIEW else prev.status
            result.unchanged.append(prev.test_id)
            merged.append(prev)
        else:
            new.added_in, new.changed_in = prev.added_in or v, v
            result.updated.append(new.test_id)
            merged.append(new)

    for tid, prev in prev_tests.items():
        if tid in seen:
            continue
        refs = set(prev.refs())
        if prev.status == OBSOLETE:
            merged.append(prev)
        elif refs and refs <= set(changes["removed"]):
            if prev.origin == REVIEWED:
                prev.status = NEEDS_REVIEW
                prev.review_note = f"{', '.join(sorted(refs))} removed from the source in {v}; retire this test if it no longer applies."
                result.needs_review.append(tid)
            else:
                prev.status, prev.changed_in = OBSOLETE, v
                prev.review_note = f"Requirement removed in {v} ({', '.join(sorted(refs))})."
                result.obsolete.append(tid)
            merged.append(prev)
        else:
            result.kept.append(tid)  # requirement still exists; keep the test rather than lose coverage
            merged.append(prev)

    for t in merged:
        t.feature, t.feature_id = feature.name, feature.feature_id
    kb.tests = [t for t in kb.tests if t.feature_id != feature.feature_id] + merged
    feature.active_tests = sum(1 for t in merged if t.status != OBSOLETE)

    def fmt(ids):
        return ", ".join(ids[:12]) + (f" (+{len(ids) - 12})" if len(ids) > 12 else "")

    kb.changelog.append(ChangeEntry(
        feature.feature_id, feature.name, v, today, run_name, sources_desc,
        unchanged=len(result.unchanged) + len(result.kept), updated=len(result.updated), added=len(result.added),
        obsolete=len(result.obsolete), needs_review=len(result.needs_review),
        requirement_changes="; ".join(f"{k}: {fmt(ids)}" for k, ids in changes.items() if ids)))
    return result


def suite_from_kb(kb: KnowledgeBase, feature: Feature, base_suite: dict) -> dict:
    """The merged, current test list of a feature in test-suite form (for the run's snapshot sheet)."""
    by_id = {tc["id"]: tc for tc in base_suite["test_cases"]}
    cases = []
    for t in kb.tests_for(feature.feature_id):
        if t.status == OBSOLETE:
            continue
        tc = by_id.get(t.test_id)
        if tc is None or t.origin == REVIEWED:
            tc = {"id": t.test_id, "scenario": t.title, "description": t.description,
                  "test_type": SHEET_TO_SUITE_TYPE.get(t.test_type, "Positive"),
                  "priority": PRIORITY_TO_SUITE.get(t.priority, "Medium"),
                  "preconditions": [p.lstrip("• ").strip() for p in t.preconditions.splitlines() if p.strip() and p != "None"],
                  "test_data": None if t.test_data == "None" else t.test_data,
                  "steps": [re.sub(r"^\d+\.\s*", "", s) for s in t.steps.splitlines() if s.strip()],
                  "expected_result": t.expected, "source_refs": t.refs() or ["—"], "feature": t.feature}
        cases.append(tc)
    return {**base_suite, "test_cases": cases}
