"""Check an agent run folder against an expectation file.

Usage:
  python3 tests/agent_evals/check_run.py <run_dir> <expectation.json>
  python3 tests/agent_evals/check_run.py --all          # newest run per expectation, matched by slug

The unit tests cover qa_tools. This script covers the *agent*: did it
classify correctly, extract the source IDs, pick relevant scenarios, avoid
out-of-scope ones, and produce clean, exported output?
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from qa_tools.__main__ import check_reports  # noqa: E402
from qa_tools.common import OUTPUT_DIR, load_json  # noqa: E402

EXPECTATIONS = Path(__file__).resolve().parent / "expectations"


def _suite_text(suite: dict) -> str:
    return json.dumps(suite["test_cases"], ensure_ascii=False).lower()


def check_run(run_dir: Path, exp: dict) -> list[tuple[bool, str]]:
    results: list[tuple[bool, str]] = []

    def check(ok: bool, msg: str) -> None:
        results.append((bool(ok), msg))

    analysis_path = run_dir / "input-analysis.json"
    suite_path = run_dir / "test-suite.json"
    check(analysis_path.exists(), "input-analysis.json exists")
    if not analysis_path.exists():
        return results
    analysis = load_json(analysis_path)

    types = [i["input_type"] for i in analysis["inputs"]]
    check(any(t in exp["input_types"] for t in types), f"input classified as one of {exp['input_types']} (got {types})")

    if exp.get("expect_blocked"):
        blocking = [q for q in analysis["clarifications"] if q["severity"] == "blocking"]
        check(len(blocking) >= 1, f"raised blocking clarification(s) ({len(blocking)})")
        still_open = any(q["status"] == "open" for q in blocking)
        check(not (suite_path.exists() and still_open), "did not generate test cases while blocking questions were open")
        return results

    check(suite_path.exists(), "test-suite.json exists")
    if not suite_path.exists():
        return results
    suite = load_json(suite_path)

    reports = check_reports(suite, analysis, 0.85)
    errors = [str(i) for r in reports for i in r.errors]
    check(not errors, "qa_tools check passes" + ("" if not errors else ": " + "; ".join(errors[:5])))
    check((run_dir / "test-suite.md").exists() and (run_dir / "test-suite.csv").exists(), "markdown and csv exported")
    check("computed" in suite.get("coverage_summary", {}), "coverage_summary.computed written by finalize")

    if "min_features" in exp:
        check(len(analysis["features"]) >= exp["min_features"], f">= {exp['min_features']} features (got {len(analysis['features'])})")
    if "min_requirements" in exp:
        check(len(analysis["requirements"]) >= exp["min_requirements"], f">= {exp['min_requirements']} requirements (got {len(analysis['requirements'])})")

    n = len(suite["test_cases"])
    lo, hi = exp.get("test_case_range", [1, 10_000])
    check(lo <= n <= hi, f"test case count {n} within [{lo}, {hi}]")

    extracted = {i["id"] for k in ("requirements", "acceptance_criteria", "business_rules") for i in analysis[k]}
    traced = {ref for tc in suite["test_cases"] for ref in tc["source_refs"]}
    for sid in exp.get("required_source_ids", []):
        check(sid in extracted, f"source id {sid} extracted verbatim")
        # Covered directly or via a child item whose requirement_id is sid.
        children = {i["id"] for k in ("acceptance_criteria", "business_rules") for i in analysis[k] if i["requirement_id"] == sid}
        check(sid in traced or bool(children & traced), f"source id {sid} traced by a test case")

    present_types = {tc["test_type"] for tc in suite["test_cases"]}
    for t in exp.get("required_test_types", []):
        check(t in present_types, f"has {t} test case(s)")

    text = _suite_text(suite)
    for kw in exp.get("must_mention", []):
        check(kw.lower() in text, f"test cases mention {kw!r}")
    for kw in exp.get("must_not_mention", []):
        check(kw.lower() not in text, f"test cases do not mention out-of-scope {kw!r}")

    gaps_text = json.dumps(suite.get("coverage_summary", {}).get("gaps", [])).lower()
    for kw in exp.get("expect_gap_keywords", []):
        check(kw.lower() in gaps_text, f"coverage gaps mention {kw!r}")

    finding_types = {f["type"] for f in suite.get("review_findings", [])}
    for t in exp.get("expect_review_finding_types", []):
        check(t in finding_types, f"review finding of type {t!r}")
    origins = {tc.get("origin") for tc in suite["test_cases"]}
    for o in exp.get("expect_origins", []):
        check(o in origins, f"has test cases with origin {o!r}")

    return results


def _latest_run_for(slug: str) -> Path | None:
    """Newest output/<date>-<slug>[-N] folder; exact slug match so 'login' doesn't pick 'existing-login-tests'."""
    pattern = re.compile(rf"^\d{{4}}-\d{{2}}-\d{{2}}-{re.escape(slug)}(-\d+)?$")
    runs = [p for p in OUTPUT_DIR.iterdir() if p.is_dir() and pattern.match(p.name)]
    return max(runs, key=lambda p: p.stat().st_mtime) if runs else None


def _print(name: str, run_dir: Path | None, results: list[tuple[bool, str]]) -> bool:
    print(f"\n== {name}: {run_dir if run_dir else 'NO RUN FOUND'} ==")
    for ok, msg in results:
        print(f"  {'PASS' if ok else 'FAIL'}  {msg}")
    passed = run_dir is not None and all(ok for ok, _ in results)
    print(f"  -> {'PASS' if passed else 'FAIL'} ({sum(ok for ok, _ in results)}/{len(results)})")
    return passed


def main(argv: list[str]) -> int:
    if argv == ["--all"]:
        all_ok = True
        for exp_path in sorted(EXPECTATIONS.glob("*.json")):
            run_dir = _latest_run_for(exp_path.stem)
            results = check_run(run_dir, load_json(exp_path)) if run_dir else []
            all_ok &= _print(exp_path.stem, run_dir, results)
        return 0 if all_ok else 1
    if len(argv) != 2:
        print(__doc__)
        return 2
    run_dir, exp_path = Path(argv[0]), Path(argv[1])
    return 0 if _print(exp_path.stem, run_dir, check_run(run_dir, load_json(exp_path))) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
