# Skill: Scenario Design

Think like an experienced QA engineer. Understand the behaviour, find the risks,
then design the **smallest set of scenarios that covers them**. Quality and
coverage matter more than quantity. Technique details are in
`resources/test-design-techniques.md`.

## Per requirement, ask in this order

1. **Happy path.** What does success look like for each role and each main variant? → `Positive`
2. **Inputs.** For each input, find the equivalence classes: valid, invalid, empty, wrong type or format. Test one representative per class. → `Validation` / `Negative`
3. **Limits.** For every stated number (length, count, amount, time, attempts), test min-1, min, max and max+1. Test min+1 and max-1 only when the rule is off-by-one-prone. → `Boundary`
4. **Rules.** When conditions combine, build a decision table and test each meaningful column. → `Business Rule`
5. **State.** Look for lifecycle or status changes: cart, order, account lock, session. Test the valid transitions and at least one invalid one. → `Business Rule` / `Negative` / `Session`
6. **Failures.** Look for downstream errors, timeouts, missing data, and concurrent or duplicate submits, but only where the input names the dependency. → `Error Handling` / `Integration`
7. **Who.** If roles exist, check allowed and denied, logged-out access, and access to another user's data. → `Authentication` / `Authorization`
8. **Edge cases.** Look for realistic oddities: leading or trailing spaces, Unicode, case sensitivity, back button or refresh, double click, an empty list, a very large list. → `Edge Case`
9. **UI.** If the feature is UI: states (loading, empty, error, disabled), navigation, and responsiveness when it is relevant. → `UI` / `Compatibility`
10. **Security.** Only when the input makes it relevant (auth, payments, PII, file upload, public APIs). Cover injection in free-text fields, rate limiting if specified, and sensitive data in responses or URLs. → `Security`

## Rules

- **Relevance filter.** Every scenario must trace to a requirement, AC, BR, or a flagged assumption. If you cannot name what it protects, drop it.
- **One behaviour per case.** Combine inputs only when testing the combination. One case may still verify several observable outcomes of the same action.
- **Boundaries need exact values** in `test_data`. "Long password" is not a boundary; "129 characters" is.
- **Negative cases specify the observable rejection.** State the message (when stated), the state that is unchanged, and the status code.
- **Do not duplicate across categories.** If a validation case already proves a rejection, do not add a generic "Negative" twin.
- **Deliberate skips.** If a category does not apply or cannot be tested from this input, note the reason for `coverage_summary.gaps`. For example: "Performance: no targets specified".

## Sizing guide

These are heuristics, not quotas:
- A single story with 3–5 ACs usually yields 8–20 cases.
- An API endpoint usually yields 10–25 cases.
- A PRD yields cases for each feature at the same density.
- Far fewer cases usually means categories were missed. Far more usually means duplicates or padding.
