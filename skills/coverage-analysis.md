# Skill: Coverage Analysis

`python3 -m qa_tools coverage <suite>` computes the numbers:
- items identified and covered;
- counts by type and priority;
- the uncovered requirements, ACs and BRs;
- requirements with no negative-style coverage;
- the full traceability matrix.

Your job is to add the judgement those numbers cannot provide.

## Steps

1. **Close or document every hole.**
   - For each `uncovered` ID, either add a case or add a `coverage_summary.gaps` entry with `ref`, `description` and `reason`. Valid reasons include "not testable from the given input", "out of scope per PRD §1.3" and "awaiting answer to Q-2".
   - The finalize gate fails on undocumented holes.
2. **Check category coverage per requirement.**
   - Every **acceptance criterion** needs at least one case.
   - Every **business rule** needs a case at each side of the rule.
   - **Positive and negative flows** are both present.
   - **Boundaries** are tested for every stated limit.
   - **Important validations** each have a case.
   - **Error handling** is covered where dependencies or failures are named.
   - **Roles and permissions** cover allowed and denied, where roles exist.
3. **Note gaps the script cannot see.** Add them as `gaps` entries without a `ref`:
   - behaviour the input leaves unspecified;
   - non-functional requirements with no targets;
   - integrations you cannot test from this input.
4. **Write `coverage_summary.notes`.** Use 2–4 sentences: overall coverage, the biggest risks left, and what would improve coverage, such as answers to open questions or missing specs.

The finalize step stores the computed numbers in `coverage_summary.computed`.
The report's QA Summary is built from them, covering requirements and ACs
identified, total cases, positive, negative, boundary, edge, validation, and gaps.
