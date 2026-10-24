"""Knowledge base data model: four tabs of the "Test Case Knowledge Base" Google Sheet.

The sheet is the single source of truth - people edit test cases there. Each test row carries a hidden
`Sync` fingerprint of the values the bot last wrote; on load, a row whose fingerprint no longer matches
was edited by a person and becomes Origin "Reviewed" (the bot never overwrites reviewed tests).
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field, fields

ACTIVE, NEEDS_REVIEW, OBSOLETE = "Active", "Needs review", "Obsolete"
STATUSES = [ACTIVE, NEEDS_REVIEW, OBSOLETE]
AI_DRAFT, REVIEWED = "AI draft", "Reviewed"

PRIORITY_TO_SUITE = {"P0": "Critical", "P1": "High", "P2": "Medium", "P3": "Low"}
# Sheet test type -> schema test_type whose sheet mapping gives the same value back (API comes from HTTP steps).
SHEET_TO_SUITE_TYPE = {"Positive": "Positive", "Negative": "Negative", "Boundary": "Boundary", "Validation": "Validation",
                       "Edge Case": "Edge Case", "UI": "UI", "UI/UX": "Compatibility", "Security": "Security",
                       "API": "Positive", "Integration": "Integration"}


@dataclass
class Feature:
    feature_id: str
    name: str
    source_keys: list[str] = field(default_factory=list)  # e.g. confluence:720897, figma:opbq..., url:example.com/prd
    source_links: list[str] = field(default_factory=list)
    version: int = 0
    updated: str = ""
    active_tests: int = 0
    latest_snapshot: str = ""
    tests_tab: str = ""   # sheetId of the "<feature> – Tests" tab in the knowledge base
    prd_tab: str = ""     # sheetId of the "<feature> – PRD" tab
    tests_url: str = ""
    prd_url: str = ""
    sheet_id: str = ""    # older layout: a separate spreadsheet per feature (migrated into tabs, then trashed)

    COLUMNS = ["Feature ID", "Feature", "Current version", "Last updated", "Active tests", "Test cases", "PRD",
               "Source links", "Latest run sheet", "Source keys", "Tab IDs", "Sheet ID"]

    def to_row(self) -> list[str]:
        return [self.feature_id, self.name, f"v{self.version}" if self.version else "", self.updated, str(self.active_tests),
                self.tests_url, self.prd_url, "\n".join(self.source_links), self.latest_snapshot,
                " ".join(self.source_keys), f"tests:{self.tests_tab} prd:{self.prd_tab}", self.sheet_id]

    @classmethod
    def from_row(cls, r: dict) -> "Feature":
        version = re.sub(r"\D", "", r.get("Current version", "")) or "0"
        tabs = dict(part.split(":", 1) for part in r.get("Tab IDs", "").split() if ":" in part)
        return cls(r.get("Feature ID", ""), r.get("Feature", ""), r.get("Source keys", "").split(),
                   [l for l in r.get("Source links", "").splitlines() if l.strip()], int(version),
                   r.get("Last updated", ""), int(r.get("Active tests") or 0), r.get("Latest run sheet", ""),
                   tabs.get("tests", ""), tabs.get("prd", ""), r.get("Test cases", ""), r.get("PRD", ""),
                   r.get("Sheet ID", ""))


@dataclass
class KBTest:
    feature_id: str
    feature: str
    test_id: str
    title: str = ""
    description: str = ""
    test_type: str = ""
    priority: str = ""
    preconditions: str = ""
    test_data: str = ""
    steps: str = ""
    expected: str = ""
    traces: str = ""
    status: str = ACTIVE
    origin: str = AI_DRAFT
    added_in: str = ""
    changed_in: str = ""
    review_note: str = ""
    suggested_update: str = ""
    sync: str = ""

    COLUMNS = ["Feature ID", "Feature", "Test ID", "Test title", "Test description", "Test type", "Priority",
               "Preconditions", "Test data", "Test steps", "Expected result", "Traces to", "Status", "Origin",
               "Added in", "Last changed in", "Review note", "Suggested update", "Sync"]
    # Fields a person can meaningfully edit; their fingerprint detects human edits.
    CONTENT = ("title", "description", "test_type", "priority", "preconditions", "test_data", "steps", "expected", "traces")
    EDITABLE = CONTENT + ("status",)

    def to_row(self) -> list[str]:
        return [getattr(self, f.name) for f in fields(self)]

    @classmethod
    def from_row(cls, r: dict) -> "KBTest":
        return cls(*(r.get(col, "") for col in cls.COLUMNS))

    def content(self) -> tuple:
        return tuple(_norm(getattr(self, f)) for f in self.CONTENT)

    def fingerprint(self) -> str:
        joined = "\x1f".join(_norm(getattr(self, f)) for f in self.EDITABLE)
        return hashlib.sha1(joined.encode()).hexdigest()[:12]

    def refs(self) -> list[str]:
        return [r.strip() for r in re.split(r"[,\s]+", self.traces) if r.strip()]


@dataclass
class KBRequirement:
    feature_id: str
    feature: str
    req_id: str
    kind: str
    text: str
    source: str = ""
    change: str = ""  # new | changed | unchanged | removed
    changed_in: str = ""

    COLUMNS = ["Feature ID", "Feature", "Requirement ID", "Kind", "Text", "Source", "Change", "Changed in"]

    def to_row(self) -> list[str]:
        return [getattr(self, f.name) for f in fields(self)]

    @classmethod
    def from_row(cls, r: dict) -> "KBRequirement":
        return cls(*(r.get(col, "") for col in cls.COLUMNS))


@dataclass
class ChangeEntry:
    feature_id: str
    feature: str
    version: str
    date: str
    run: str
    sources: str
    unchanged: int = 0
    updated: int = 0
    added: int = 0
    obsolete: int = 0
    needs_review: int = 0
    requirement_changes: str = ""
    snapshot: str = ""

    COLUMNS = ["Feature ID", "Feature", "Version", "Date", "Run", "Sources", "Unchanged", "Updated", "Added",
               "Obsolete", "Needs review", "Requirement changes", "Run sheet"]

    def to_row(self) -> list[str]:
        return [str(getattr(self, f.name)) for f in fields(self)]

    @classmethod
    def from_row(cls, r: dict) -> "ChangeEntry":
        vals = [r.get(col, "") for col in cls.COLUMNS]
        for i in range(6, 11):
            vals[i] = int(vals[i] or 0)
        return cls(*vals)


@dataclass
class KnowledgeBase:
    features: list[Feature] = field(default_factory=list)
    tests: list[KBTest] = field(default_factory=list)
    requirements: list[KBRequirement] = field(default_factory=list)
    changelog: list[ChangeEntry] = field(default_factory=list)

    def feature(self, feature_id: str) -> Feature | None:
        return next((f for f in self.features if f.feature_id == feature_id), None)

    def tests_for(self, feature_id: str) -> list[KBTest]:
        return [t for t in self.tests if t.feature_id == feature_id]

    def requirements_for(self, feature_id: str) -> list[KBRequirement]:
        return [r for r in self.requirements if r.feature_id == feature_id]

    def next_feature_id(self) -> str:
        nums = [int(m.group(1)) for f in self.features if (m := re.fullmatch(r"F-(\d+)", f.feature_id))]
        return f"F-{max(nums, default=0) + 1:03d}"

    def mark_human_edits(self) -> list[str]:
        """Rows whose Sync fingerprint no longer matches were edited by a person -> Reviewed. Returns their IDs."""
        edited = []
        for t in self.tests:
            if t.sync != t.fingerprint():
                if t.origin != REVIEWED:
                    edited.append(t.test_id)
                t.origin = REVIEWED
        return edited

    def stamp(self) -> None:
        """Refresh fingerprints just before writing, so the next load can detect human edits."""
        for t in self.tests:
            t.sync = t.fingerprint()


def _norm(value) -> str:
    return " ".join(str(value or "").split())
