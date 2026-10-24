"""Duplicate and overlap detection.

Exact duplicates (same scenario content after normalisation, same data) are
errors. Near-duplicates with the *same* test data are warnings per pair.
Cases whose steps/expected match but whose test data differs are
data-driven variants (typical for boundary/validation partitions); they
are reported once per group so Claude can confirm each value is a distinct
partition. The final call is Claude's (see skills/duplicate-review.md).
"""

from __future__ import annotations

from difflib import SequenceMatcher

from .common import Report, normalize, test_data_text

NEAR_DUPLICATE_THRESHOLD = 0.85
SCENARIO_TITLE_THRESHOLD = 0.92


def _body(tc: dict) -> str:
    return normalize(" ".join(tc["steps"]) + " => " + tc["expected_result"])


def _groups(pairs: list[tuple[int, int]], n: int) -> list[list[int]]:
    parent = list(range(n))

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for a, b in pairs:
        parent[find(a)] = find(b)
    members: dict[int, list[int]] = {}
    for a, b in pairs:
        for x in (a, b):
            members.setdefault(find(x), [])
            if x not in members[find(x)]:
                members[find(x)].append(x)
    return [sorted(m) for m in members.values()]


def find_duplicates(suite: dict, threshold: float = NEAR_DUPLICATE_THRESHOLD) -> Report:
    report = Report("duplicate detection")
    cases = suite.get("test_cases", [])
    prepared = [
        (tc, _body(tc), normalize(test_data_text(tc.get("test_data"))), normalize(tc["scenario"]))
        for tc in cases
    ]
    variant_pairs: list[tuple[int, int]] = []

    for i in range(len(prepared)):
        a, body_a, data_a, title_a = prepared[i]
        for j in range(i + 1, len(prepared)):
            b, body_b, data_b, title_b = prepared[j]
            pair = f"{a['id']} ~ {b['id']}"

            if body_a == body_b and data_a == data_b:
                report.error("exact-duplicate", "identical steps, data and expected result; keep one", pair)
                continue

            matcher = SequenceMatcher(None, body_a, body_b, autojunk=False)
            if matcher.quick_ratio() >= threshold and matcher.ratio() >= threshold:
                if data_a == data_b:
                    report.warn("near-duplicate", f"{matcher.ratio():.0%} similar steps+expected with the same test data; merge unless they verify different outcomes", pair)
                else:
                    variant_pairs.append((i, j))
                continue

            if (
                title_a
                and set(a["source_refs"]) == set(b["source_refs"])
                and SequenceMatcher(None, title_a, title_b).ratio() >= SCENARIO_TITLE_THRESHOLD
            ):
                report.warn("overlapping-scenario", "near-identical scenario titles for the same source refs", pair)

    for group in _groups(variant_pairs, len(prepared)):
        ids = [prepared[k][0]["id"] for k in group]
        report.warn(
            "data-variants",
            f"{len(ids)} cases share steps/expected and differ only in test data; confirm each value is a distinct partition or boundary",
            ", ".join(ids),
        )

    return report
