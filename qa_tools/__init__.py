"""Deterministic QA tooling for the Test Case Generation Agent.

Claude does the reasoning (classification, extraction, scenario design);
this package does the checks that must be repeatable: schema validation,
quality rules, duplicate detection, coverage computation and export.

Standard library only, by design: the agent runs inside Claude Code and
should work on a bare Python 3.10+ install with no pip step.
"""

from .common import Issue, Report, load_json, find_analysis, ROOT, SCHEMAS_DIR

__all__ = ["Issue", "Report", "load_json", "find_analysis", "ROOT", "SCHEMAS_DIR"]
