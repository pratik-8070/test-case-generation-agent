"""Slack messages: progress, result summary and failure."""

from __future__ import annotations

from qa_tools.coverage import compute_coverage

from .modal import FORMATS, TestCaseRequest

SECTION_LIMIT = 2900  # Slack section text max is 3000 chars
MAX_LIST_ITEMS = 5


def _section(text: str) -> dict:
    if len(text) > SECTION_LIMIT:
        text = text[: SECTION_LIMIT - 1] + "…"
    return {"type": "section", "text": {"type": "mrkdwn", "text": text}}


def _bullets(items: list[str], more_hint: str) -> str:
    shown = [f"• {i}" for i in items[:MAX_LIST_ITEMS]]
    if len(items) > MAX_LIST_ITEMS:
        shown.append(f"_…and {len(items) - MAX_LIST_ITEMS} more {more_hint}_")
    return "\n".join(shown)


def progress_text(req: TestCaseRequest) -> str:
    extras = []
    if req.reference_links:
        extras.append(f"{len(req.reference_links)} link{'s' * (len(req.reference_links) != 1)}")
    if req.file_ids:
        extras.append(f"{len(req.file_ids)} file{'s' * (len(req.file_ids) != 1)}")
    with_refs = f" with {' and '.join(extras)}" if extras else ""
    return (f":hourglass_flowing_sand: <@{req.user_id}> requested test cases for *{req.feature_name}*{with_refs} "
            f"({FORMATS[req.output_format][0]}). Generating — this usually takes a few minutes…")


def sources_text(sources: list) -> str:
    """'Reference material' section: what was read and what couldn't be (with the reason)."""
    sources = [s for s in sources or [] if s.kind != "kb"]
    if not sources:
        return ""
    used = [s.label for s in sources if s.ok]
    failed = [f"{s.label} — {s.note}" for s in sources if not s.ok]
    lines = [f"*Reference material:* {len(used)} read" + (f", {len(failed)} couldn't be read" if failed else "")]
    if failed:
        lines.append(_bullets(failed, "unreadable sources"))
    return "\n".join(lines)


def kb_text(record) -> str:
    """Link to this run's newly generated test cases sheet, plus a one-line note of what changed.

    The knowledge base itself is never linked from Slack (the team works from each run's sheet).
    """
    r = record.result
    lines = []
    if record.snapshot_url:
        lines.append(f":bar_chart: *<{record.snapshot_url}|Open the test cases (Google Sheet)>*")
    lines.append(f":books: Saved to the knowledge base as *{r.feature.name} {r.summary()}*")
    if r.needs_review:
        lines.append(f"Needs review (edited by a person, source changed): {', '.join(r.needs_review[:8])}")
    return "\n".join(lines)


def result_blocks(req: TestCaseRequest, suite: dict, analysis: dict | None, sources: list | None = None,
                  sheet_url: str | None = None, sheet_note: str = "", kb_record=None) -> list[dict]:
    cov = compute_coverage(suite, analysis)
    input_types = ", ".join(i["input_type"] for i in (analysis or {}).get("inputs", [])) or "—"

    blocks: list[dict] = [
        {"type": "header", "text": {"type": "plain_text", "text": f"Test cases: {req.feature_name}"[:150]}},
        _section(f":white_check_mark: <@{req.user_id}> *{cov['total_test_cases']} test cases* generated · input read as *{input_types}*"),
        *([_section(kb_text(kb_record))] if kb_record else []),
        *([_section(f":bar_chart: *<{sheet_url}|Open the test cases in Google Sheets>*" + (f"\n_{sheet_note}_" if sheet_note else ""))]
          if sheet_url and not kb_record else []),
        {"type": "section", "fields": [
            {"type": "mrkdwn", "text": f"*Positive*\n{cov['positive']}"},
            {"type": "mrkdwn", "text": f"*Negative*\n{cov['negative']}"},
            {"type": "mrkdwn", "text": f"*Boundary*\n{cov['boundary']}"},
            {"type": "mrkdwn", "text": f"*Edge cases*\n{cov['edge']}"},
            {"type": "mrkdwn", "text": f"*Validation*\n{cov['validation']}"},
            {"type": "mrkdwn", "text": f"*Assumption-based*\n{cov['assumption_based']}"},
        ]},
    ]
    if "acceptance_criteria_identified" in cov:
        blocks.append(_section(
            f"*Coverage:* {cov['requirements_covered']}/{cov['requirements_identified']} requirements · "
            f"{cov['acceptance_criteria_covered']}/{cov['acceptance_criteria_identified']} acceptance criteria · "
            f"{cov['business_rules_covered']}/{cov['business_rules_identified']} business rules"))

    if sources:
        blocks.append(_section(sources_text(sources)))

    questions = [q["question"] for q in (analysis or {}).get("clarifications", []) if q.get("status") != "answered"]
    if questions:
        blocks.append(_section("*Open questions* — add the answers to *Feature context* and run `/test-case` again for stronger coverage:\n"
                               + _bullets(questions, "in the report")))
    gaps = [g["description"] for g in suite.get("coverage_summary", {}).get("gaps", [])]
    if gaps:
        blocks.append(_section("*Coverage gaps*\n" + _bullets(gaps, "in the report")))
    if not sheet_url and (not kb_record or req.output_format != "gsheet"):
        attached = FORMATS["md" if req.output_format == "gsheet" else req.output_format][0]
        blocks.append({"type": "context", "elements": [
            {"type": "mrkdwn", "text": f"{sheet_note + ' · ' if sheet_note else ''}Full {attached} attached in the thread :thread:"}]})
    return blocks


def failure_text(req: TestCaseRequest, error: str, check_errors: list[str]) -> str:
    lines = [f":x: <@{req.user_id}> test case generation for *{req.feature_name}* failed: {error}"]
    if check_errors:
        lines.append("Validation errors:\n" + _bullets(check_errors, "errors"))
    lines.append("Try again with more detail, or check the bot logs.")
    return "\n".join(lines)[:SECTION_LIMIT]
