# Workflow: Test Case Generation

The pipeline the agent follows for every run. Each stage names the skill
file that holds its detailed rules. Read a skill file when you reach its stage.
Read all of them on the first run in a session.

```
Input → 1 Intake → 2 Classify → 3 Extract → 4 Clarify (gate) → 5 Scenarios
      → 6 Write cases → 7 Validate & de-dupe (loop) → 8 Coverage → 9 Finalize & report
```

Artifacts for each run go in one folder:

```
output/<YYYY-MM-DD>-<slug>/
  input-analysis.json   ← stages 2-4   (schemas/input-analysis.schema.json)
  test-suite.json       ← stages 5-8   (schemas/test-suite.schema.json)
  test-suite.md         ← stage 9 (generated, do not hand-edit)
  test-suite.csv        ← stage 9 (generated, do not hand-edit)
```

---

## 1. Intake

- Collect every input. It may be pasted text, one or more file paths, a folder, or a mix.
- Read each file in full:
  - `.md`, `.txt`, `.json`, `.yaml`, `.csv`, `.feature`: Read.
  - PDF: Read with `pages`. For more than 20 pages, read it in chunks.
  - Images such as screenshots and mockups: Read, which shows them to you.
  - `.docx`: `textutil -convert txt -stdout <file>` on macOS. Elsewhere, ask the user for a PDF or text copy.
- Create the run folder: `python3 -m qa_tools new-run <short-slug>`. Use a slug such as `login` or `checkout-prd`.
- If no input was given, ask for it and stop.

## 2. Classify → `skills/input-classification.md`

Give each input exactly one primary `input_type` and a `confidence`. List 1–3
concrete `evidence` strings, quoting the signals you saw. Add `secondary_types`
when an input mixes types, for example a PRD that embeds user stories.

**Gate:** if the type is `UNKNOWN` or `confidence: low`, add a blocking
clarification that asks what the input is. Do not guess.

## 3. Extract → `skills/requirement-extraction.md` + the input handler

Choose the handler by type:

| Input type | Handler |
|---|---|
| PRD, BRD, TECHNICAL_SPEC | `skills/input-handlers/prd.md` |
| API_SPEC | `skills/input-handlers/api-spec.md` |
| UI_DESIGN | `skills/input-handlers/ui-design.md` |
| EXISTING_TEST_CASES | `skills/input-handlers/existing-test-cases.md` |
| more than one input | `skills/input-handlers/multi-input.md` (in addition to the per-type handler) |
| REQUIREMENT, USER_STORY, ACCEPTANCE_CRITERIA, FEATURE_DESCRIPTION, PLAIN_TEXT | the general rules in `requirement-extraction.md` |

From the input, produce `features[]`, `requirements[]`, `acceptance_criteria[]`,
`business_rules[]` and `context`. Every item gets an `id`, a `source_ref` and an
`origin` (`stated`, `observed`, `inferred` or `clarified`).

## 4. Clarify (gate) → `skills/clarification.md`

1. List what is missing, ambiguous or contradictory. Mark each item `blocking` or `non_blocking`.
2. Write `input-analysis.json`, with the open questions included.
3. Run `python3 -m qa_tools check-analysis <run>/input-analysis.json`.
4. **If any blocking question is open, STOP.**
   - Ask the user with AskUserQuestion, at most 4 questions per call. If that tool is unavailable, ask a numbered list in chat.
   - Do not generate test cases yet.
   - When the user answers, set `status: answered` and fill in `answer`. Add or revise the affected items with `origin: clarified`. Rerun the check.
5. Record each non-blocking gap as `status: assumed` with a matching `assumptions[]` entry, then continue.
6. If the user says "proceed with assumptions", convert the open blocking questions to `assumed` with explicit assumptions. Every case that depends on one is flagged.

Continue only when `check-analysis` passes.

## 5. Design scenarios → `skills/scenario-design.md`

For each requirement:
1. Apply the techniques: equivalence partitioning, boundary values, decision tables, state transitions, and error guessing.
2. Choose the categories that apply (positive, negative, boundary, edge, validation, business rule, error handling, auth, session, UI, API, integration).
3. Write down a category you deliberately skip, with the reason, and put it in `coverage_summary.gaps` later. Never pad the count.

## 6. Write test cases → `skills/test-case-writing.md`

- Write `test-suite.json`.
- Each case follows the schema and the ID, priority and wording rules in the skill.
- `source_refs` points at the most specific item: an AC or BR rather than its parent requirement.
- A case that relies on an `inferred` item or an assumption gets `assumption: true` and `assumption_refs`.
- For EXISTING_TEST_CASES inputs, also fill in `review_findings[]` and set `origin` on every case.

## 7. Validate and de-duplicate (loop) → `skills/duplicate-review.md`

1. Run `python3 -m qa_tools check <run>/test-suite.json`.
2. Fix every **error**.
3. Look at every **warning**. Fix it, or accept it on purpose. You may keep near-duplicate boundary cases that cover distinct values.
4. Repeat until the result is `PASS`. Then do one manual review against the "Final self-review" checklist in `skills/test-case-writing.md`, because the script cannot judge whether a case is meaningful.

## 8. Coverage → `skills/coverage-analysis.md`

- Run `python3 -m qa_tools coverage <run>/test-suite.json`.
- Every uncovered AC or BR must be either covered or listed in `coverage_summary.gaps` with a `ref` and a `reason`.
- Also add gaps the script cannot see: unspecified behaviour, NFRs that are not in scope, and integrations that cannot be tested from the given input.
- Write the 2–4 sentence summary in `coverage_summary.notes`.

## 9. Finalize and report

1. Run `python3 -m qa_tools finalize <run>/test-suite.json`. It re-runs every check, stores the computed coverage, and writes the `.md` and `.csv`. It refuses to export while errors remain.
2. In chat, reply with:
   - the detected input type(s);
   - a summary table: requirements, ACs and BRs identified/covered, total cases, and the counts for positive, negative, boundary, edge and validation;
   - the assumptions made and the open gaps;
   - links to the 4 files in the run folder.
3. Do not paste the full suite into chat unless the user asks for it.
