"""Coverage computation and traceability matrix.

A test case covers every id in its source_refs. Covering an AC or business
rule also counts as covering its parent requirement.
"""

from __future__ import annotations

from collections import Counter

from .common import Report, traceable_items

# Summary buckets the report must always show, mapped from test_type.
SUMMARY_BUCKETS = {
    "positive": {"Positive"},
    "negative": {"Negative", "Error Handling"},
    "boundary": {"Boundary"},
    "edge": {"Edge Case"},
    "validation": {"Validation"},
}
NEGATIVE_LIKE = {"Negative", "Error Handling", "Validation", "Boundary", "Edge Case", "Business Rule", "Session", "Authorization", "Authentication", "Security"}


def compute_coverage(suite: dict, analysis: dict | None = None) -> dict:
    cases = suite.get("test_cases", [])
    by_type = Counter(tc["test_type"] for tc in cases)
    by_priority = Counter(tc["priority"] for tc in cases)

    covering: dict[str, list[str]] = {}
    for tc in cases:
        for ref in tc["source_refs"]:
            covering.setdefault(ref, []).append(tc["id"])

    result: dict = {
        "total_test_cases": len(cases),
        **{bucket: sum(by_type[t] for t in types) for bucket, types in SUMMARY_BUCKETS.items()},
        "by_type": dict(sorted(by_type.items())),
        "by_priority": {p: by_priority[p] for p in ("Critical", "High", "Medium", "Low") if by_priority[p]},
        "assumption_based": sum(1 for tc in cases if tc.get("assumption")),
    }

    if analysis is None:
        result["referenced_ids"] = sorted(covering)
        return result

    items = traceable_items(analysis)
    types_by_tc = {tc["id"]: tc["test_type"] for tc in cases}

    # Roll child coverage up to the parent requirement.
    req_cover: dict[str, set[str]] = {r["id"]: set(covering.get(r["id"], [])) for r in analysis["requirements"]}
    for ref, tcs in covering.items():
        parent = items.get(ref, {}).get("requirement_id")
        if parent in req_cover:
            req_cover[parent].update(tcs)

    def matrix(key: str, cover_map) -> list[dict]:
        rows = []
        for item in analysis.get(key, []):
            tcs = sorted(cover_map(item["id"]))
            rows.append({
                "id": item["id"],
                "text": item["text"],
                "test_cases": tcs,
                "test_types": sorted({types_by_tc[t] for t in tcs}),
            })
        return rows

    req_rows = matrix("requirements", lambda i: req_cover.get(i, set()))
    ac_rows = matrix("acceptance_criteria", lambda i: set(covering.get(i, [])))
    br_rows = matrix("business_rules", lambda i: set(covering.get(i, [])))

    result.update({
        "requirements_identified": len(analysis["requirements"]),
        "acceptance_criteria_identified": len(analysis["acceptance_criteria"]),
        "business_rules_identified": len(analysis["business_rules"]),
        "requirements_covered": sum(1 for r in req_rows if r["test_cases"]),
        "acceptance_criteria_covered": sum(1 for r in ac_rows if r["test_cases"]),
        "business_rules_covered": sum(1 for r in br_rows if r["test_cases"]),
        "uncovered": {
            "requirements": [r["id"] for r in req_rows if not r["test_cases"]],
            "acceptance_criteria": [r["id"] for r in ac_rows if not r["test_cases"]],
            "business_rules": [r["id"] for r in br_rows if not r["test_cases"]],
        },
        "requirements_without_negative": [
            r["id"] for r in req_rows if r["test_cases"] and not (set(r["test_types"]) & NEGATIVE_LIKE)
        ],
        "traceability": {"requirements": req_rows, "acceptance_criteria": ac_rows, "business_rules": br_rows},
    })
    return result


def coverage_report(suite: dict, analysis: dict | None) -> Report:
    """Turn coverage holes into issues. A hole listed in coverage_summary.gaps[].ref is an accepted gap (warning)."""
    report = Report("coverage")
    if analysis is None:
        report.warn("no-analysis", "coverage against requirements not checked (no input analysis)")
        return report

    cov = compute_coverage(suite, analysis)
    accepted = {g.get("ref") for g in suite.get("coverage_summary", {}).get("gaps", []) if g.get("ref")}

    labels = {"requirements": "requirement", "acceptance_criteria": "acceptance criterion", "business_rules": "business rule"}
    for key, label in labels.items():
        for ref in cov["uncovered"][key]:
            if ref in accepted:
                report.warn("accepted-gap", f"{label} has no test case (documented in coverage_summary.gaps)", ref)
            else:
                report.error("uncovered", f"{label} has no test case; cover it or document it in coverage_summary.gaps with a reason", ref)

    for ref in cov["requirements_without_negative"]:
        if ref not in accepted:
            report.warn("no-negative-coverage", "requirement only has positive-style cases; add negative/validation/boundary cases or document why not", ref)

    if cov["total_test_cases"] and cov["positive"] == 0:
        report.warn("no-positive-cases", "suite has no Positive (happy-path) case")
    return report


def write_coverage(suite: dict, analysis: dict | None) -> dict:
    """Store the computed coverage in suite['coverage_summary']['computed'], keeping Claude's gaps/notes."""
    summary = suite.setdefault("coverage_summary", {})
    summary["computed"] = compute_coverage(suite, analysis)
    summary.setdefault("gaps", [])
    return suite


def render_text(cov: dict) -> str:
    lines = ["== coverage =="]
    for key in ("requirements_identified", "acceptance_criteria_identified", "business_rules_identified",
                "requirements_covered", "acceptance_criteria_covered", "business_rules_covered",
                "total_test_cases", "positive", "negative", "boundary", "edge", "validation", "assumption_based"):
        if key in cov:
            lines.append(f"{key.replace('_', ' '):34} {cov[key]}")
    lines.append(f"{'by type':34} {cov['by_type']}")
    lines.append(f"{'by priority':34} {cov['by_priority']}")
    if "uncovered" in cov:
        for key, ids in cov["uncovered"].items():
            if ids:
                lines.append(f"UNCOVERED {key:24} {', '.join(ids)}")
        if cov["requirements_without_negative"]:
            lines.append(f"{'no negative coverage':34} {', '.join(cov['requirements_without_negative'])}")
    return "\n".join(lines)
