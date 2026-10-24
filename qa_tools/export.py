"""Render test-suite.json into test-suite.md (human report) and test-suite.csv (import format)."""

from __future__ import annotations

import csv
from pathlib import Path

from .common import TEMPLATES_DIR, test_data_text
from .coverage import compute_coverage

CSV_COLUMNS = [
    "Test Case ID", "Source Refs", "Feature", "Scenario", "Test Type", "Priority",
    "Preconditions", "Test Data", "Test Steps", "Expected Result", "Postconditions",
    "Assumption", "Assumption Refs", "Origin", "Notes",
]


def _cell(text: str) -> str:
    """Make text safe inside a Markdown table cell."""
    return str(text).replace("|", "\\|").replace("\n", "<br>")


def _numbered(items: list[str]) -> str:
    return "\n".join(f"{n}. {s}" for n, s in enumerate(items, 1))


def _test_data_md(value) -> str:
    if not value:
        return "_None_"
    if isinstance(value, dict):
        return "\n".join(f"- `{k}`: {test_data_text(v)}" for k, v in value.items())
    if isinstance(value, list):
        return "\n".join(f"- {test_data_text(v)}" for v in value)
    return str(value)


def _table(headers: list[str], rows: list[list]) -> str:
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    out += ["| " + " | ".join(_cell(c) for c in row) + " |" for row in rows]
    return "\n".join(out)


def _render_case(tc: dict) -> str:
    flags = []
    if tc.get("assumption"):
        flags.append(f"⚠️ Assumption-based ({', '.join(tc.get('assumption_refs', [])) or 'unreferenced'})")
    if tc.get("origin"):
        flags.append(f"Origin: {tc['origin']}" + (f" (was {tc['original_id']})" if tc.get("original_id") else ""))
    parts = [
        f"### {tc['id']} — {tc['scenario']}",
        "",
        f"**Feature:** {tc['feature']} · **Type:** {tc['test_type']} · **Priority:** {tc['priority']} · "
        f"**Traces to:** {', '.join(tc['source_refs'])}",
    ]
    if flags:
        parts += ["", " · ".join(flags)]
    parts += [
        "",
        "**Preconditions**",
        "",
        "\n".join(f"- {p}" for p in tc["preconditions"]) or "_None_",
        "",
        "**Test Data**",
        "",
        _test_data_md(tc.get("test_data")),
        "",
        "**Steps**",
        "",
        _numbered(tc["steps"]),
        "",
        f"**Expected Result:** {tc['expected_result']}",
    ]
    if tc.get("postconditions"):
        parts += ["", "**Postconditions**", "", "\n".join(f"- {p}" for p in tc["postconditions"])]
    if tc.get("notes"):
        parts += ["", f"_Notes: {tc['notes']}_"]
    return "\n".join(parts)


def render_markdown(suite: dict, analysis: dict | None = None, template_path: Path | None = None) -> str:
    template = (template_path or TEMPLATES_DIR / "test-suite-report.md").read_text(encoding="utf-8")
    cases = suite["test_cases"]
    cov = compute_coverage(suite, analysis)
    gaps = suite.get("coverage_summary", {}).get("gaps", [])

    if analysis:
        inputs = _table(["Source", "Detected type", "Confidence", "Evidence"],
                        [[i["source"], i["input_type"], i["confidence"], "; ".join(i["evidence"])] for i in analysis["inputs"]])
    else:
        inputs = "_No input analysis attached._"

    summary_rows = []
    for key, label in (("requirements_identified", "Requirements identified"),
                       ("acceptance_criteria_identified", "Acceptance criteria identified"),
                       ("business_rules_identified", "Business rules identified")):
        if key in cov:
            covered = cov[key.replace("identified", "covered")]
            summary_rows.append([label, f"{cov[key]} ({covered} covered)"])
    summary_rows += [
        ["Total test cases", cov["total_test_cases"]],
        ["Positive", cov["positive"]],
        ["Negative (incl. error handling)", cov["negative"]],
        ["Boundary", cov["boundary"]],
        ["Edge cases", cov["edge"]],
        ["Validation", cov["validation"]],
        ["Other types", ", ".join(f"{t}: {n}" for t, n in cov["by_type"].items()
                                  if t not in {"Positive", "Negative", "Error Handling", "Boundary", "Edge Case", "Validation"}) or "—"],
        ["By priority", ", ".join(f"{p}: {n}" for p, n in cov["by_priority"].items())],
        ["Assumption-based cases", cov["assumption_based"]],
        ["Coverage gaps", len(gaps)],
    ]
    summary = _table(["Metric", "Value"], summary_rows)
    if suite.get("coverage_summary", {}).get("notes"):
        summary += "\n\n" + suite["coverage_summary"]["notes"]

    clar_parts = []
    if analysis and analysis.get("clarifications"):
        clar_parts.append(_table(["ID", "Question", "Severity", "Status", "Answer"],
                                 [[q["id"], q["question"], q["severity"], q["status"], q.get("answer", "")] for q in analysis["clarifications"]]))
    if analysis and analysis.get("assumptions"):
        clar_parts.append(_table(["ID", "Assumption", "Related"],
                                 [[a["id"], a["text"], ", ".join(a.get("related_refs", []))] for a in analysis["assumptions"]]))
    clarifications = "\n\n".join(clar_parts) or "_None._"

    gaps_md = _table(["Ref", "Gap", "Reason"], [[g.get("ref", "—"), g["description"], g.get("reason", "")] for g in gaps]) if gaps else "_No coverage gaps identified._"

    if "traceability" in cov:
        trace_rows = []
        for kind, label in (("requirements", "REQ"), ("acceptance_criteria", "AC"), ("business_rules", "BR")):
            for row in cov["traceability"][kind]:
                trace_rows.append([label, row["id"], row["text"], ", ".join(row["test_cases"]) or "❌ none"])
        traceability = _table(["Kind", "ID", "Text", "Test cases"], trace_rows)
    else:
        traceability = "_No input analysis attached; refs: " + ", ".join(cov.get("referenced_ids", [])) + "_"

    index = _table(["ID", "Feature", "Scenario", "Type", "Priority", "Traces to"],
                   [[tc["id"], tc["feature"], tc["scenario"], tc["test_type"], tc["priority"], ", ".join(tc["source_refs"])] for tc in cases])

    findings = suite.get("review_findings") or []
    findings_md = ""
    if findings:
        findings_md = "\n## Review Findings (existing test cases)\n\n" + _table(
            ["ID", "Type", "Test cases", "Finding", "Action"],
            [[f["id"], f["type"], ", ".join(f["test_case_refs"]), f["description"], f["action"]] for f in findings])

    values = {
        "suite_name": suite["metadata"]["suite_name"],
        "created": suite["metadata"]["created"],
        "input_types": ", ".join(suite["metadata"].get("input_types", [])) or "—",
        "total": str(len(cases)),
        "inputs": inputs,
        "summary": summary,
        "clarifications": clarifications,
        "gaps": gaps_md,
        "traceability": traceability,
        "index": index,
        "test_cases": "\n\n---\n\n".join(_render_case(tc) for tc in cases),
        "review_findings": findings_md,
    }
    out = template
    for key, val in values.items():
        out = out.replace("{{" + key + "}}", val)
    return out.rstrip() + "\n"


def write_csv(suite: dict, path: Path) -> None:
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        for tc in suite["test_cases"]:
            writer.writerow({
                "Test Case ID": tc["id"],
                "Source Refs": ", ".join(tc["source_refs"]),
                "Feature": tc["feature"],
                "Scenario": tc["scenario"],
                "Test Type": tc["test_type"],
                "Priority": tc["priority"],
                "Preconditions": "\n".join(tc["preconditions"]),
                "Test Data": test_data_text(tc.get("test_data")),
                "Test Steps": _numbered(tc["steps"]),
                "Expected Result": tc["expected_result"],
                "Postconditions": "\n".join(tc.get("postconditions", [])),
                "Assumption": "Yes" if tc.get("assumption") else "No",
                "Assumption Refs": ", ".join(tc.get("assumption_refs", [])),
                "Origin": tc.get("origin", ""),
                "Notes": tc.get("notes", ""),
            })


def export(suite: dict, analysis: dict | None, out_dir: Path) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    md_path = out_dir / "test-suite.md"
    csv_path = out_dir / "test-suite.csv"
    md_path.write_text(render_markdown(suite, analysis), encoding="utf-8")
    write_csv(suite, csv_path)
    return [md_path, csv_path]
