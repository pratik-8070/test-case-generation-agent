# Skill: Requirement Extraction

Turn the input into testable, traceable units. Understand the functionality
first. Do not copy sentences across one by one.

## What to extract

- **features[]**: `code` (UPPERCASE, short, used in test case IDs: LOGIN, CART, ORDERS-API) and `name`.
- **requirements[]**: one entry per testable behaviour. Split compound statements: "users can add and remove items" becomes two requirements.
- **acceptance_criteria[]**: the conditions of satisfaction under a requirement.
- **business_rules[]**: constraints and policies such as limits, calculations, eligibility, state rules and lockouts. If a rule is stated inside an AC, extract it as a BR as well, but only when it carries an independent constraint, such as "max 10 per item".
- **context** (and each requirement's `details` where it is specific to that requirement): user roles, preconditions, dependencies, inputs, expected behaviour, validations, error conditions, boundary conditions, data requirements, UI behaviour, API behaviour, auth, external dependencies. Fill only what the input supports.

## IDs

- **Keep source IDs exactly as written** (US-12, FR-3.1, AC2). Traceability depends on them.
- When the source has no IDs, assign them:
  - Requirements: `REQ-001`, `REQ-002`, and so on.
  - Acceptance criteria: `AC-<req number>.<n>`, for example `AC-001.1`.
  - Business rules: `BR-001`, and so on.
  - Use `-<n>` suffixes if an assigned ID would collide with a source ID.
- IDs are unique across requirements, ACs and BRs.

## source_ref

Point to where the item came from, specific enough that a reviewer can find it:
- `"PRD §3.2 Cart"`
- `"Story line 4"`
- `"POST /orders → 422 response"`
- `"login.png: below password field"`
- `"existing-tests.csv row 7"`

## origin, and how assumptions are kept honest

| origin | Meaning |
|---|---|
| `stated` | Explicitly written in the input |
| `observed` | Visible in a UI image or design |
| `inferred` | You deduced it. It is reasonable but not stated. **Tests that use it must be flagged as assumptions.** |
| `clarified` | Came from the user's answer to a clarification |

- Never invent requirements, business rules, validations, APIs or error messages.
  - If a common behaviour is *likely* but not stated (for example "email format is validated"), do not add it as `stated`. Either add it as an `inferred` item or raise a clarification.
  - Prefer the clarification when the expected result would otherwise be a guess.
- Never upgrade `inferred` to `stated`.

## Checklist before moving on

- Every requirement belongs to a declared feature.
- Every AC and BR has a `requirement_id` that exists.
- Compound requirements are split.
- Exact limits, messages, roles and states are copied verbatim, including numbers, units and quotes.
- You can list for yourself what the input does **not** say. That list feeds `skills/clarification.md`.
