# Skill: Test Case Writing

Each case follows `schemas/test-suite.schema.json`. A QA engineer who has never
seen the requirement must be able to run it and decide pass or fail without
asking anyone.

## Fields

| Field | Rule |
|---|---|
| `id` | `TC-<FEATURE_CODE>-<NNN>`, numbered from 001 in each feature with no gaps. Use the feature `code` from the analysis: `TC-LOGIN-001`, `TC-ORDERS-API-014`. |
| `source_refs` | The most specific items covered: ACs or BRs before requirements. Use several refs only when the case truly verifies each of them. |
| `feature` | The feature `name` from the analysis. |
| `scenario` | One line in the form "<action/condition> → <outcome>", without the arrow if it reads fine without. Example: "Log in with an unregistered email". This is the test title. |
| `description` | 1–2 sentences: what the case verifies and why it matters, for example "Confirms unregistered emails get the generic error, so the login form doesn't reveal which accounts exist." |
| `test_type` | One primary type from the enum. Choose the reason the case exists: a boundary case that also rejects input is `Boundary`. |
| `priority` | Use the rubric below. |
| `preconditions` | The concrete state before step 1: the account exists and is active, the cart holds 2 items, the user is logged in as Admin. |
| `test_data` | An object of named, exact values: `{"email": "user@example.com", "password": "Valid#Pass1"}`. Use `null` only when no data is involved. |
| `steps` | Imperative, one action per step, with no expectations inside steps. Reference data by name: "Enter `password` from test data". |
| `expected_result` | Specific and verifiable: the message text when stated, the URL or page, the status code and body field, the state change, and what must **not** happen. |
| `postconditions` | Only when the state left behind matters, such as "The account is locked" or "The order is in PENDING". |
| `assumption` / `assumption_refs` | `true` with `A-n` refs when the case depends on an inferred item or an assumption. |
| `origin` / `original_id` | Only for EXISTING_TEST_CASES runs. |
| `notes` | Optional reviewer notes, for example "Needs a seeded locked account". |

## Priority rubric

| Priority | Use when |
|---|---|
| **Critical** | Core happy path of a must-have requirement; security or auth enforcement; money, data loss or legal impact |
| **High** | Main negative paths and business rules of core features; key validations; boundaries of stated limits |
| **Medium** | Secondary flows, less likely invalid inputs, UI states, most edge cases |
| **Low** | Cosmetic issues, rare edge cases, compatibility checks without stated requirements |

Spread the priorities honestly. A suite that is all Critical or all High is
not prioritised.

## Wording

The validator rejects these expected results:
- "works as expected"
- "works correctly"
- "is handled properly"
- "no issues"

It warns on these:
- "appropriate"
- "proper"
- "relevant"
- "etc."

| ❌ Avoid | ✅ Write |
|---|---|
| Verify login works | User lands on `/dashboard` and the header shows "Hi, Asha" |
| Appropriate error shown | Error "Invalid email or password" is shown above the form, and the password field is cleared |
| API returns error | Response is `422` with `errors[0].field = "quantity"`, and no order is created |

When the input does not give the exact message, describe the observable class
and mark the gap. Do not invent message text:
"A validation error is shown for the quantity field, and the item is not added
(message text not specified; see A-2)".

## Final self-review

Do this after `qa_tools check` passes. The script cannot judge these:

- [ ] Every case tests something the input actually says, or is flagged as an assumption.
- [ ] Each AC has a positive case, and a negative or boundary case where one applies.
- [ ] Every stated number has boundary cases with exact values.
- [ ] No two cases prove the same thing.
- [ ] The steps would work for someone new to the product.
- [ ] Priorities follow the rubric.
