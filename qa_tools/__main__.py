"""CLI: python3 -m qa_tools <command> ...

Commands
  new-run <slug>                     create output/<YYYY-MM-DD>-<slug>/ and print its path
  check-analysis <analysis.json>     validate an input analysis (schema, ids, open blocking questions)
  validate <suite.json>              schema + quality rules (+ traceability if analysis found)
  dedupe <suite.json>                exact / near-duplicate detection
  coverage <suite.json> [--write]    coverage numbers and traceability; --write stores them in the suite
  check <suite.json>                 validate + dedupe + coverage gate (exit 1 on any error)
  export <suite.json>                render test-suite.md and test-suite.csv next to the suite
  finalize <suite.json>              check; if clean, write coverage into the suite and export

--analysis defaults to input-analysis.json in the same folder as the suite.
Exit codes: 0 = no errors, 1 = errors found, 2 = usage / file problem.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .common import OUTPUT_DIR, Report, create_run_dir, find_analysis, load_json, save_json
from .coverage import compute_coverage, coverage_report, render_text, write_coverage
from .dedupe import NEAR_DUPLICATE_THRESHOLD, find_duplicates
from .export import export
from .validate import validate_analysis, validate_suite


def _load_pair(args) -> tuple[dict, dict | None]:
    suite = load_json(args.suite)
    analysis_path = find_analysis(args.suite, getattr(args, "analysis", None))
    analysis = load_json(analysis_path) if analysis_path else None
    return suite, analysis


def _emit(reports: list[Report], as_json: bool) -> int:
    if as_json:
        print(json.dumps([r.to_dict() for r in reports], indent=2))
    else:
        print("\n\n".join(r.render() for r in reports))
        total_err = sum(len(r.errors) for r in reports)
        total_warn = sum(len(r.warnings) for r in reports)
        print(f"\nRESULT: {'PASS' if total_err == 0 else 'FAIL'} ({total_err} error(s), {total_warn} warning(s))")
    return 0 if all(r.ok for r in reports) else 1


def check_reports(suite: dict, analysis: dict | None, threshold: float) -> list[Report]:
    reports = []
    if analysis is not None:
        reports.append(validate_analysis(analysis))
    reports.append(validate_suite(suite, analysis))
    if reports[-1].codes() & {"schema-type", "schema-required"}:
        return reports  # later stages would crash on a malformed suite
    reports.append(find_duplicates(suite, threshold))
    reports.append(coverage_report(suite, analysis))
    return reports


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="qa_tools", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("new-run")
    p.add_argument("slug")
    p.add_argument("--output-dir", default=str(OUTPUT_DIR))

    p = sub.add_parser("check-analysis")
    p.add_argument("analysis")
    p.add_argument("--json", action="store_true")

    for name in ("validate", "dedupe", "coverage", "check", "export", "finalize"):
        p = sub.add_parser(name)
        p.add_argument("suite")
        p.add_argument("--analysis")
        p.add_argument("--json", action="store_true")
        if name in ("dedupe", "check", "finalize"):
            p.add_argument("--threshold", type=float, default=NEAR_DUPLICATE_THRESHOLD)
        if name == "coverage":
            p.add_argument("--write", action="store_true")

    args = parser.parse_args(argv)

    try:
        if args.cmd == "new-run":
            print(create_run_dir(args.slug, args.output_dir))
            return 0

        if args.cmd == "check-analysis":
            return _emit([validate_analysis(load_json(args.analysis))], args.json)

        suite, analysis = _load_pair(args)

        if args.cmd == "validate":
            return _emit([validate_suite(suite, analysis)], args.json)
        if args.cmd == "dedupe":
            return _emit([find_duplicates(suite, args.threshold)], args.json)
        if args.cmd == "coverage":
            cov = compute_coverage(suite, analysis)
            if args.write:
                save_json(write_coverage(suite, analysis), args.suite)
            print(json.dumps(cov, indent=2) if args.json else render_text(cov))
            return _emit([coverage_report(suite, analysis)], False) if not args.json else 0
        if args.cmd == "check":
            return _emit(check_reports(suite, analysis, args.threshold), args.json)
        if args.cmd == "export":
            for path in export(suite, analysis, Path(args.suite).resolve().parent):
                print(path)
            return 0
        if args.cmd == "finalize":
            reports = check_reports(suite, analysis, args.threshold)
            code = _emit(reports, args.json)
            if code != 0:
                print("\nNot exported: fix the errors above and run finalize again.", file=sys.stderr)
                return code
            save_json(write_coverage(suite, analysis), args.suite)
            print("\n" + render_text(suite["coverage_summary"]["computed"]))
            print("\nWrote:")
            print(Path(args.suite).resolve())
            for path in export(suite, analysis, Path(args.suite).resolve().parent):
                print(path)
            return 0
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as exc:
        print(f"error: invalid JSON: {exc}", file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    sys.exit(main())
