"""Shared types and helpers used by every qa_tools module."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCHEMAS_DIR = ROOT / "schemas"
TEMPLATES_DIR = ROOT / "resources" / "templates"
OUTPUT_DIR = ROOT / "output"

ANALYSIS_FILENAME = "input-analysis.json"
SUITE_FILENAME = "test-suite.json"


@dataclass
class Issue:
    level: str  # "error" | "warning"
    code: str  # short machine-readable rule id, e.g. "vague-expected-result"
    message: str
    ref: str = ""  # test case / requirement id the issue is about

    def __str__(self) -> str:
        where = f"[{self.ref}] " if self.ref else ""
        return f"{self.level.upper():7} {self.code:28} {where}{self.message}"


@dataclass
class Report:
    title: str
    issues: list[Issue] = field(default_factory=list)

    def error(self, code: str, message: str, ref: str = "") -> None:
        self.issues.append(Issue("error", code, message, ref))

    def warn(self, code: str, message: str, ref: str = "") -> None:
        self.issues.append(Issue("warning", code, message, ref))

    def extend(self, other: "Report") -> None:
        self.issues.extend(other.issues)

    @property
    def errors(self) -> list[Issue]:
        return [i for i in self.issues if i.level == "error"]

    @property
    def warnings(self) -> list[Issue]:
        return [i for i in self.issues if i.level == "warning"]

    @property
    def ok(self) -> bool:
        return not self.errors

    def codes(self) -> set[str]:
        return {i.code for i in self.issues}

    def render(self) -> str:
        lines = [f"== {self.title} =="]
        lines += [str(i) for i in self.errors + self.warnings]
        lines.append(f"-- {len(self.errors)} error(s), {len(self.warnings)} warning(s)")
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "ok": self.ok,
            "issues": [i.__dict__ for i in self.issues],
        }


def load_json(path: str | Path) -> dict:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def save_json(data: dict, path: str | Path) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
        fh.write("\n")


def create_run_dir(slug: str, output_dir: str | Path = OUTPUT_DIR) -> Path:
    """Create output/<YYYY-MM-DD>-<slug>[-N]/ and return it (never reuses an existing folder)."""
    import re
    from datetime import date

    clean = re.sub(r"[^a-z0-9]+", "-", slug.lower()).strip("-")[:40].strip("-") or "run"
    base = Path(output_dir) / f"{date.today().isoformat()}-{clean}"
    path, n = base, 2
    while path.exists():
        path, n = Path(f"{base}-{n}"), n + 1
    path.mkdir(parents=True)
    return path


def find_analysis(suite_path: str | Path, explicit: str | Path | None = None) -> Path | None:
    """Return the analysis file to use: the explicit one, else the sibling input-analysis.json."""
    if explicit:
        return Path(explicit)
    sibling = Path(suite_path).resolve().parent / ANALYSIS_FILENAME
    return sibling if sibling.exists() else None


def traceable_items(analysis: dict) -> dict[str, dict]:
    """Every id a test case may reference (requirements, ACs, business rules) -> item, tagged with its kind."""
    items: dict[str, dict] = {}
    for kind, key in (("requirement", "requirements"), ("acceptance_criterion", "acceptance_criteria"), ("business_rule", "business_rules")):
        for item in analysis.get(key, []):
            items[item["id"]] = {**item, "_kind": kind}
    return items


def normalize(text: str) -> str:
    """Lowercase, collapse whitespace and strip punctuation for text comparison."""
    out = []
    for ch in text.lower():
        out.append(ch if ch.isalnum() or ch.isspace() else " ")
    return " ".join("".join(out).split())


def test_data_text(value) -> str:
    """Flatten test_data (object, list, string or null) into one line."""
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        return "; ".join(f"{k}: {test_data_text(v)}" for k, v in value.items())
    if isinstance(value, list):
        return "; ".join(test_data_text(v) for v in value)
    return json.dumps(value)
