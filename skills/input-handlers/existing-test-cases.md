# Input Handler: Existing Test Cases

The goal is to **review and improve** the existing suite, not just append to it.

## 1. Reverse-engineer the requirements

1. Group the existing cases by feature.
2. For each group, infer what is being tested and record it as a requirement or AC with `origin: "inferred"` and `source_ref: "<file> row N / <TC id>"`.
   - When the requirement or source document is also supplied, use those items instead (`stated`), and map each existing case to them.
3. If you only have the tests, the "requirements" are your reading of them. Record that as an assumption, and keep the new cases conservative.

## 2. Review every existing case

Record each problem as a `review_findings[]` entry (`RF-1`, …):

| type | What to look for |
|---|---|
| `duplicate` / `overlap` | Two cases proving the same thing |
| `weak_steps` | Steps missing, compound, or not executable ("Test login") |
| `vague_expected_result` | "Works as expected", "success", "error shown" with nothing specific |
| `missing_negative` | A feature tested only on its happy path |
| `missing_boundary` | A limit is mentioned but its edges are not tested |
| `missing_validation` | Input fields with no validation cases |
| `missing_coverage` | A requirement or AC with no case at all |
| `outdated` | Contradicts the supplied requirements |

Each finding gives a concrete `action`, such as "Merged into TC-LOGIN-003" or
"Added TC-LOGIN-007, TC-LOGIN-008".

## 3. Produce the unified suite

| origin | When |
|---|---|
| `existing` | Kept unchanged. Its ID is renumbered into the TC-<FEAT>-NNN scheme, with `original_id` keeping the old ID. |
| `improved` | Rewritten steps or expected result, or merged duplicates. `original_id` lists the old IDs, comma-separated if merged. |
| `new` | Fills a gap found in review. |

- Drop exact duplicates, but record them in `review_findings`.
- Never silently delete an existing case. Every removal or merge appears in `review_findings`.

## 4. Report

In the final chat message, give:
- the counts of existing, improved and new cases, and of removed duplicates;
- the top 3 coverage risks found in the original suite.
