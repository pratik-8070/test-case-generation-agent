# Skill: Clarification

Ask before generating whenever important information is missing or ambiguous.
Do not ask about trivia.

## Blocking or non-blocking

A gap is **blocking** when you **cannot write a specific, verifiable expected
result** for core behaviour without the answer. Typical blocking gaps:

- The input type is unknown, or classification confidence is low.
- The core rule has no value: "limited attempts" without a number, or "strong password" without a policy.
- The outcome of the main flow is undefined: what happens after success or failure.
- Roles or permissions are mentioned but not defined: "only authorized users".
- Requirements contradict each other: §2 says 5 items maximum and §4 says 10.
- The scope is unclear: two possible readings would produce substantially different suites.

A gap is **non-blocking** when tests can still be written meaningfully and the
gap affects only edge details. For example:
- The exact error-message wording is not given.
- Session timeout or performance targets are not stated.
- Browser or device coverage is not stated.

Record each non-blocking gap as an assumption:
1. Set the clarification's `status: "assumed"`.
2. Add an `assumptions[]` entry with `from_clarification` pointing back to the question.
3. Flag every dependent case `assumption: true`.

When you cannot write a specific expected result, word the case to verify the
**observable class** of the outcome without inventing exact text. For example:
"An error message is shown, the user is not logged in, and the attempt is not
counted as success". Note the gap.

## How to ask

- Ask at most **4 questions** per round, highest impact first. Use AskUserQuestion when it is available.
- Each question should:
  - be specific and answerable;
  - state why it matters (`why`);
  - offer concrete options where possible, such as "3 attempts / 5 attempts / Other";
  - reference the related IDs.
- Do not ask what the input already answers. Do not ask about future features.
- After answers arrive:
  - Set `status: "answered"` and fill in `answer`.
  - Add or update the items it affects with `origin: "clarified"`.
  - Rerun `check-analysis`.
- If the user declines to answer or says "proceed", convert the open questions to `assumed` with explicit assumptions and continue.
- Name the open questions in the final report.

## Example

Input: "Users can reset their password via email."

Blocking questions:
1. How long is the reset link valid, and can it be used more than once?
2. What password policy applies to the new password?

Non-blocking gap, assumed: the response for an unregistered email. The
assumption is that it is generic, so it does not reveal whether the account
exists.
