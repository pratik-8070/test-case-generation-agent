"""Quality rules for input analyses and test suites (beyond plain schema shape).

Errors block the run; warnings are for Claude to review and either fix or
consciously accept. Rule codes are stable so tests and docs can refer to them.
"""

from __future__ import annotations

import re
from collections import Counter, defaultdict

from .common import Report, traceable_items
from .schema import validate_against

# Expected results containing these are not verifiable -> error.
VAGUE_EXPECTED = [
    r"\bas expected\b",
    r"\bworks? (correctly|properly|fine|as intended)\b",
    r"\b(functions?|behaves?|performs?) (correctly|properly|as intended)\b",
    r"\bshould work\b",
    r"\bis handled (correctly|properly|appropriately)\b",
    r"\bno issues?\b",
    r"\beverything is (ok|fine|correct)\b",
    r"\bcorrect behaviou?r\b",
]
# Softer signals -> warning: often vague, sometimes fine in context.
SOFT_VAGUE_EXPECTED = [
    r"\bappropriate\b",
    r"\bproper\b",
    r"\brelevant\b",
    r"\betc\.?\b",
    r"\band so on\b",
    r"\bsuccessfully\.?$",
]
VAGUE_STEP = [r"^(test|check|verify) (the )?(functionality|feature|it|everything)\.?$", r"^\s*(do|perform) (the )?(action|test)\.?$"]

_ID_PREFIX = re.compile(r"^(TC-.+)-\d{3}$")


def validate_analysis(analysis: dict) -> Report:
    report = Report("input analysis")
    report.extend(validate_against(analysis, "input-analysis.schema.json"))
    if not report.ok:
        return report  # structural problems first; rules below assume the shape

    ids = [i["id"] for key in ("requirements", "acceptance_criteria", "business_rules") for i in analysis[key]]
    for dup, n in Counter(ids).items():
        if n > 1:
            report.error("duplicate-trace-id", f"id used {n} times across requirements/ACs/BRs", dup)

    req_ids = {r["id"] for r in analysis["requirements"]}
    feature_codes = {f["code"] for f in analysis["features"]}
    for r in analysis["requirements"]:
        if r["feature"] not in feature_codes:
            report.error("unknown-feature", f"feature '{r['feature']}' is not declared in features[]", r["id"])
    for key in ("acceptance_criteria", "business_rules"):
        for item in analysis[key]:
            if item["requirement_id"] not in req_ids:
                report.error("dangling-parent", f"requirement_id '{item['requirement_id']}' does not exist", item["id"])

    if not analysis["requirements"]:
        report.error("no-requirements", "no testable requirements were extracted")

    for inp in analysis["inputs"]:
        if inp["input_type"] == "UNKNOWN" or inp["confidence"] == "low":
            open_q = [q for q in analysis["clarifications"] if q["status"] == "open"]
            if not open_q:
                report.warn("low-confidence-input", f"classified {inp['input_type']} ({inp['confidence']}) but no clarification was raised", inp["source"])

    for q in analysis["clarifications"]:
        if q["severity"] == "blocking" and q["status"] == "open":
            report.error("blocking-clarification-open", f"blocking question unanswered: {q['question']}", q["id"])
        if q["status"] == "assumed" and not any(a.get("from_clarification") == q["id"] for a in analysis["assumptions"]):
            report.warn("assumed-without-assumption", "clarification marked 'assumed' but no assumptions[] entry references it", q["id"])
        if q["status"] == "answered" and not q.get("answer"):
            report.error("answer-missing", "clarification marked 'answered' but has no answer text", q["id"])

    return report


def _prefix(tc_id: str) -> str:
    m = _ID_PREFIX.match(tc_id)
    return m.group(1) if m else tc_id


def validate_suite(suite: dict, analysis: dict | None = None) -> Report:
    report = Report("test suite")
    report.extend(validate_against(suite, "test-suite.schema.json"))
    if not report.ok:
        return report

    cases = suite["test_cases"]
    for dup, n in Counter(tc["id"] for tc in cases).items():
        if n > 1:
            report.error("duplicate-id", f"test case id used {n} times", dup)

    prefixes_by_feature: dict[str, set[str]] = defaultdict(set)
    for tc in cases:
        tid = tc["id"]
        prefixes_by_feature[tc["feature"]].add(_prefix(tid))

        expected = tc["expected_result"]
        for pat in VAGUE_EXPECTED:
            if re.search(pat, expected, re.IGNORECASE):
                report.error("vague-expected-result", f"expected result is not verifiable ({pat!s} matched): {expected!r}", tid)
                break
        else:
            for pat in SOFT_VAGUE_EXPECTED:
                if re.search(pat, expected, re.IGNORECASE):
                    report.warn("soft-vague-expected-result", f"expected result may be vague ('{pat}'); state the exact outcome", tid)
                    break

        for n, step in enumerate(tc["steps"], 1):
            if any(re.search(p, step.strip(), re.IGNORECASE) for p in VAGUE_STEP):
                report.error("vague-step", f"step {n} is not actionable: {step!r}", tid)
            elif len(step.split()) < 2:
                report.warn("short-step", f"step {n} is very short: {step!r}", tid)

        steps_norm = [s.strip().lower() for s in tc["steps"]]
        if any(a == b for a, b in zip(steps_norm, steps_norm[1:])):
            report.warn("repeated-step", "the same step appears twice in a row; merge or say 'repeat N times'", tid)

        if tc["test_type"] in ("Boundary", "Validation") and not tc["test_data"]:
            report.warn("missing-test-data", f"{tc['test_type']} case without test_data; state the exact values used", tid)

        if tc["assumption"] and not tc.get("assumption_refs"):
            report.warn("assumption-unreferenced", "assumption=true but no assumption_refs; link the A-n it depends on", tid)
        if not tc["assumption"] and tc.get("assumption_refs"):
            report.error("assumption-flag-mismatch", "has assumption_refs but assumption=false", tid)

    for feature, prefixes in prefixes_by_feature.items():
        if len(prefixes) > 1:
            report.warn("inconsistent-id-prefix", f"feature '{feature}' uses several id prefixes: {sorted(prefixes)}")

    if len(cases) >= 6 and len({tc["priority"] for tc in cases}) == 1:
        report.warn("flat-priorities", f"all {len(cases)} cases have priority {cases[0]['priority']}; apply the priority rubric")

    if analysis is None:
        report.warn("no-analysis", "no input-analysis.json given; traceability refs were not verified")
        return report

    items = traceable_items(analysis)
    assumption_ids = {a["id"] for a in analysis.get("assumptions", [])}
    for tc in cases:
        tid = tc["id"]
        for ref in tc["source_refs"]:
            if ref not in items:
                report.error("dangling-trace-ref", f"source_ref '{ref}' not found in the input analysis", tid)
            elif items[ref]["origin"] == "inferred" and not tc["assumption"]:
                report.warn("unsupported-assumption", f"traces to inferred item '{ref}' but is not flagged assumption=true", tid)
        for ref in tc.get("assumption_refs", []):
            if ref not in assumption_ids:
                report.error("dangling-assumption-ref", f"assumption_ref '{ref}' not found in assumptions[]", tid)

    for q in analysis.get("clarifications", []):
        if q["severity"] == "blocking" and q["status"] == "open":
            report.error("blocking-clarification-open", "test cases were generated while a blocking question is unanswered", q["id"])

    return report
