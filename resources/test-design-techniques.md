# Test Design Techniques: Quick Reference

## Equivalence Partitioning (EP)

Split each input into classes that the system should treat the same way. Test
one representative per class.

Example: quantity 1–10 gives these classes:
- valid: 1–10
- below the range: ≤0
- above the range: ≥11
- non-numeric
- empty

## Boundary Value Analysis (BVA)

Defects cluster at the edges.

- For the range [min, max], test **min-1, min, max, max+1**.
- Add min+1 and max-1 when the rule is likely to have an off-by-one error, such as `<` written instead of `≤`.
- Apply BVA to lengths, counts, amounts, dates and times, attempt counters, list sizes and pagination limits.
- When a limit is stated as "up to N", confirm whether N itself is included. If unclear, raise a clarification.

## Decision Table

Use one when the outcome depends on a **combination** of conditions.

| Condition / Rule | R1 | R2 | R3 | R4 |
|---|---|---|---|---|
| Logged in | Y | Y | N | N |
| Item in stock | Y | N | Y | N |
| **Outcome** | Added | "Out of stock" | Redirect to login | Redirect to login |

Collapse columns with the same outcome when the condition truly does not
matter; R3 and R4 collapse here. Each remaining column is one test case.

## State Transition

Use for lifecycles such as order status, account lock, cart or session.

1. List the states and the events that move between them.
2. Test every valid transition.
3. Test at least one invalid transition, such as cancelling a delivered order.
4. Test transitions that are guarded by a rule, such as locking after N failures.

## Error Guessing / Risk-Based

Draw on experience. Common hot spots:
- empty input, or whitespace only;
- leading and trailing spaces;
- case sensitivity;
- Unicode and emoji;
- double submit;
- the back button after submitting;
- refreshing mid-flow;
- a session expiring mid-flow;
- concurrent updates;
- very large inputs;
- special characters in free text (`' " < > ; --`).

Include a case only when the input makes it relevant.

## Pairwise

Use it when there are many independent parameters, such as browser × OS ×
locale. Cover every **pair** of values rather than every combination. Apply it
only if the input specifies that configuration matrix.
