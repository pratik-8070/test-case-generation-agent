# Login & Logout — reviewed existing suite

Generated: 2026-10-06 · Input types: EXISTING_TEST_CASES · Test cases: 8

## Inputs analysed

| Source | Detected type | Confidence | Evidence |
|---|---|---|---|
| resources/examples/existing-login-tests.csv | EXISTING_TEST_CASES | high | CSV header 'Test ID,Title,Steps,Expected Result,Priority'; Six rows LG-01..LG-06 in test case format |

## QA Summary

| Metric | Value |
|---|---|
| Requirements identified | 4 (4 covered) |
| Acceptance criteria identified | 0 (0 covered) |
| Business rules identified | 0 (0 covered) |
| Total test cases | 8 |
| Positive | 2 |
| Negative (incl. error handling) | 2 |
| Boundary | 0 |
| Edge cases | 0 |
| Validation | 3 |
| Other types | Session: 1 |
| By priority | High: 3, Medium: 5 |
| Assumption-based cases | 8 |
| Coverage gaps | 3 |

The original 6 cases reduce to 4 (1 kept, 3 improved; LG-02 merged and LG-05 removed), plus 4 new cases for unregistered email, single empty fields and post-logout session. All cases are assumption-based because requirements were reverse-engineered from the tests; supplying the login requirement (Q-1) and the password and lockout rules (Q-2) would enable boundary coverage.

## Clarifications & Assumptions

| ID | Question | Severity | Status | Answer |
|---|---|---|---|---|
| Q-1 | Is there a requirement or story for login/logout that these tests should be checked against? | non_blocking | assumed |  |
| Q-2 | What are the exact error messages, password rules and lockout rules? | non_blocking | assumed |  |

| ID | Assumption | Related |
|---|---|---|
| A-1 | The behaviour implied by the existing tests (LG-01..LG-06) is the intended behaviour. | REQ-001, REQ-002, REQ-003, REQ-004 |
| A-2 | Exact message texts and validation/lockout rules are unknown; expected results assert the observable outcome without inventing message text. | REQ-002, REQ-003 |

## Coverage Gaps

| Ref | Gap | Reason |
|---|---|---|
| — | Boundary cases for password length and lockout | Rules unknown (Q-2) |
| — | Email format validation, case sensitivity, session timeout | No requirement available (Q-1); not added to avoid inventing behaviour |
| REQ-001 | Negative login paths are tracked under REQ-002 and REQ-003 | REQ-001 is the happy path only; its rejections are separate inferred requirements |

## Traceability Matrix

| Kind | ID | Text | Test cases |
|---|---|---|---|
| REQ | REQ-001 | A user can log in with a valid email and password | TC-LOGIN-001 |
| REQ | REQ-002 | Login with invalid credentials is rejected with an error | TC-LOGIN-002, TC-LOGIN-004 |
| REQ | REQ-003 | Login with empty fields is rejected with an error | TC-LOGIN-003, TC-LOGIN-005, TC-LOGIN-006 |
| REQ | REQ-004 | A logged-in user can log out and is redirected to the homepage | TC-LOGOUT-001, TC-LOGOUT-002 |

## Test Case Index

| ID | Feature | Scenario | Type | Priority | Traces to |
|---|---|---|---|---|---|
| TC-LOGIN-001 | Login | Log in with a valid email and password | Positive | High | REQ-001 |
| TC-LOGIN-002 | Login | Log in with a valid email and a wrong password | Negative | High | REQ-002 |
| TC-LOGIN-003 | Login | Submit the login form with both fields empty | Validation | Medium | REQ-003 |
| TC-LOGIN-004 | Login | Log in with an email that is not registered | Negative | High | REQ-002 |
| TC-LOGIN-005 | Login | Submit with email filled and password empty | Validation | Medium | REQ-003 |
| TC-LOGIN-006 | Login | Submit with password filled and email empty | Validation | Medium | REQ-003 |
| TC-LOGOUT-001 | Logout | Log out from a logged-in session | Positive | Medium | REQ-004 |
| TC-LOGOUT-002 | Logout | Back button after logout does not restore the logged-in session | Session | Medium | REQ-004 |

## Test Cases

### TC-LOGIN-001 — Log in with a valid email and password

**Feature:** Login · **Type:** Positive · **Priority:** High · **Traces to:** REQ-001

⚠️ Assumption-based (A-1) · Origin: improved (was LG-01, LG-02)

**Preconditions**

- Active account user@example.com exists with password Valid#Pass1
- User is logged out and on the login page

**Test Data**

- `email`: user@example.com
- `password`: Valid#Pass1

**Steps**

1. Enter `email` and `password` from test data
2. Click 'Log in'

**Expected Result:** The user leaves the login page and the header shows the logged-in state (account name and a 'Logout' option)

_Notes: Merged duplicates LG-01 and LG-02; replaced 'logged in successfully' / 'works as expected' with observable outcomes._

---

### TC-LOGIN-002 — Log in with a valid email and a wrong password

**Feature:** Login · **Type:** Negative · **Priority:** High · **Traces to:** REQ-002

⚠️ Assumption-based (A-1, A-2) · Origin: improved (was LG-03)

**Preconditions**

- Active account user@example.com exists with password Valid#Pass1
- User is on the login page

**Test Data**

- `email`: user@example.com
- `password`: Wrong#Pass9

**Steps**

1. Enter `email` and `password` from test data
2. Click 'Log in'

**Expected Result:** An error message is displayed on the login page and the user remains on the login page and is not logged in (no logged-in header state)

---

### TC-LOGIN-003 — Submit the login form with both fields empty

**Feature:** Login · **Type:** Validation · **Priority:** Medium · **Traces to:** REQ-003

⚠️ Assumption-based (A-1, A-2) · Origin: improved (was LG-04)

**Preconditions**

- User is on the login page

**Test Data**

- `email`: 
- `password`: 

**Steps**

1. Leave Email and Password empty
2. Click 'Log in'

**Expected Result:** An error or required-field indication is shown for the empty fields and the user remains on the login page and is not logged in (no logged-in header state)

---

### TC-LOGIN-004 — Log in with an email that is not registered

**Feature:** Login · **Type:** Negative · **Priority:** High · **Traces to:** REQ-002

⚠️ Assumption-based (A-1, A-2) · Origin: new

**Preconditions**

- No account exists for nobody@example.com
- User is on the login page

**Test Data**

- `email`: nobody@example.com
- `password`: Valid#Pass1

**Steps**

1. Enter `email` and `password` from test data
2. Click 'Log in'

**Expected Result:** An error message is displayed and the user remains on the login page and is not logged in (no logged-in header state)

---

### TC-LOGIN-005 — Submit with email filled and password empty

**Feature:** Login · **Type:** Validation · **Priority:** Medium · **Traces to:** REQ-003

⚠️ Assumption-based (A-1, A-2) · Origin: new

**Preconditions**

- User is on the login page

**Test Data**

- `email`: user@example.com
- `password`: 

**Steps**

1. Enter only the email
2. Click 'Log in'

**Expected Result:** An error or required-field indication is shown for the password field and the user remains on the login page and is not logged in (no logged-in header state)

---

### TC-LOGIN-006 — Submit with password filled and email empty

**Feature:** Login · **Type:** Validation · **Priority:** Medium · **Traces to:** REQ-003

⚠️ Assumption-based (A-1, A-2) · Origin: new

**Preconditions**

- User is on the login page

**Test Data**

- `email`: 
- `password`: Valid#Pass1

**Steps**

1. Enter only the password
2. Click 'Log in'

**Expected Result:** An error or required-field indication is shown for the email field and the user remains on the login page and is not logged in (no logged-in header state)

---

### TC-LOGOUT-001 — Log out from a logged-in session

**Feature:** Logout · **Type:** Positive · **Priority:** Medium · **Traces to:** REQ-004

⚠️ Assumption-based (A-1) · Origin: existing (was LG-06)

**Preconditions**

- Active account user@example.com exists with password Valid#Pass1

**Test Data**

- `email`: user@example.com
- `password`: Valid#Pass1

**Steps**

1. Log in with the test data credentials
2. Click Logout

**Expected Result:** User is logged out and redirected to the homepage

---

### TC-LOGOUT-002 — Back button after logout does not restore the logged-in session

**Feature:** Logout · **Type:** Session · **Priority:** Medium · **Traces to:** REQ-004

⚠️ Assumption-based (A-1) · Origin: new

**Preconditions**

- Active account user@example.com exists with password Valid#Pass1
- User is logged in and viewing their account page

**Test Data**

_None_

**Steps**

1. Click Logout
2. Press the browser Back button
3. Reload the page

**Expected Result:** The account page is not shown in a logged-in state after reload; the header shows the logged-out state

_Notes: Common logout risk not covered by the original suite._

## Review Findings (existing test cases)

| ID | Type | Test cases | Finding | Action |
|---|---|---|---|---|
| RF-1 | duplicate | LG-01, LG-02, TC-LOGIN-001 | LG-01 and LG-02 both test a valid login with the same steps. | Merged into TC-LOGIN-001. |
| RF-2 | vague_expected_result | LG-01, LG-02, LG-03, LG-04 | Expected results 'logged in successfully', 'Login works as expected', 'Error shown' and 'Error' cannot be verified. | Rewritten with observable outcomes in TC-LOGIN-001..003. |
| RF-3 | weak_steps | LG-05 | LG-05 'Test login' has the step 'Test the functionality' and expected result 'Works correctly'; it tests nothing identifiable. | Removed; its intent is covered by TC-LOGIN-001. |
| RF-4 | missing_negative | TC-LOGIN-004 | No case for an unregistered email. | Added TC-LOGIN-004. |
| RF-5 | missing_validation | TC-LOGIN-005, TC-LOGIN-006 | Empty-field validation only tested with both fields empty. | Added TC-LOGIN-005 and TC-LOGIN-006. |
| RF-6 | missing_boundary |  | No boundary cases (password length, lockout attempts); the limits are not known from the tests. | Not added; recorded as a coverage gap pending Q-2. |
| RF-7 | missing_coverage | TC-LOGOUT-002 | Logout is only tested for the redirect, not session invalidation. | Added TC-LOGOUT-002. |
