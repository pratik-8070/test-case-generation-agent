# Login (US-101)

Generated: 2026-10-06 · Input types: USER_STORY · Test cases: 17

## Inputs analysed

| Source | Detected type | Confidence | Evidence |
|---|---|---|---|
| resources/examples/login.md | USER_STORY | high | 'As a registered customer, I want to log in ... so that ...' story format; Story id 'US-101' with an attached 'Acceptance Criteria' list AC1-AC6 |

## QA Summary

| Metric | Value |
|---|---|
| Requirements identified | 1 (1 covered) |
| Acceptance criteria identified | 6 (6 covered) |
| Business rules identified | 3 (3 covered) |
| Total test cases | 17 |
| Positive | 2 |
| Negative (incl. error handling) | 2 |
| Boundary | 6 |
| Edge cases | 0 |
| Validation | 3 |
| Other types | Business Rule: 2, UI: 2 |
| By priority | Critical: 2, High: 8, Medium: 7 |
| Assumption-based cases | 4 |
| Coverage gaps | 3 |

All 6 acceptance criteria and both stated business rules are covered, with boundaries on the 5-attempt lock and its 15-minute duration. Cases TC-LOGIN-011/012/016/017 rely on assumptions A-1 and A-2. The main remaining risks are the unspecified lock-counting rules (Q-3) and password-length handling at login (Q-2).

## Clarifications & Assumptions

| ID | Question | Severity | Status | Answer |
|---|---|---|---|---|
| Q-1 | While the account is locked, is a login with the correct password rejected with the lock message? | non_blocking | assumed |  |
| Q-2 | Does the login form enforce the 8-64 password length itself, or does an out-of-range password simply fail as invalid credentials? | non_blocking | assumed |  |
| Q-3 | Are failed attempts with an unregistered email or an invalid email format counted towards the lock? | non_blocking | out_of_scope |  |

| ID | Assumption | Related |
|---|---|---|
| A-1 | During the 15-minute lock, the correct password is rejected with 'Your account is locked. Try again in 15 minutes.' | AC5, BR-003 |
| A-2 | The login form does not validate password length; BR-001 is only used to confirm that 8- and 64-character passwords work at login. Out-of-range lengths are not tested. | BR-001 |

## Coverage Gaps

| Ref | Gap | Reason |
|---|---|---|
| — | Behaviour for passwords shorter than 8 or longer than 64 characters at login is not specified | Assumption A-2; awaiting answer to Q-2 |
| — | Whether failures with an unregistered or badly formatted email count towards the lock | Not stated (Q-3) |
| — | Password case sensitivity, session duration and 'remember me' are not specified | Not in US-101; not tested to avoid inventing requirements |

## Traceability Matrix

| Kind | ID | Text | Test cases |
|---|---|---|---|
| REQ | US-101 | A registered customer can log in with email and password to access their account | TC-LOGIN-001, TC-LOGIN-002, TC-LOGIN-003, TC-LOGIN-004, TC-LOGIN-005, TC-LOGIN-006, TC-LOGIN-007, TC-LOGIN-008, TC-LOGIN-009, TC-LOGIN-010, TC-LOGIN-011, TC-LOGIN-012, TC-LOGIN-013, TC-LOGIN-014, TC-LOGIN-015, TC-LOGIN-016, TC-LOGIN-017 |
| AC | AC1 | Correct email and password for an active account redirects to the 'My Account' page | TC-LOGIN-001 |
| AC | AC2 | Incorrect email or password shows 'Invalid email or password' and the customer remains on the login page | TC-LOGIN-002, TC-LOGIN-003 |
| AC | AC3 | 'Log in' button is disabled until both email and password are non-empty | TC-LOGIN-004, TC-LOGIN-005, TC-LOGIN-006 |
| AC | AC4 | Invalid email format shows inline 'Enter a valid email address' under the field | TC-LOGIN-007, TC-LOGIN-008 |
| AC | AC5 | After 5 consecutive failed attempts the account is locked for 15 minutes and 'Your account is locked. Try again in 15 minutes.' is shown | TC-LOGIN-009, TC-LOGIN-010, TC-LOGIN-012, TC-LOGIN-013 |
| AC | AC6 | Email matching is case-insensitive | TC-LOGIN-015 |
| BR | BR-001 | Password is 8-64 characters (existing registration rule) | TC-LOGIN-016, TC-LOGIN-017 |
| BR | BR-002 | A successful login resets the failed-attempt counter | TC-LOGIN-014 |
| BR | BR-003 | While locked, a login with the correct password is also rejected with the lock message | TC-LOGIN-011 |

## Test Case Index

| ID | Feature | Scenario | Type | Priority | Traces to |
|---|---|---|---|---|---|
| TC-LOGIN-001 | Login | Log in with correct email and password for an active account | Positive | Critical | AC1 |
| TC-LOGIN-002 | Login | Log in with a registered email and a wrong password | Negative | High | AC2 |
| TC-LOGIN-003 | Login | Log in with an email that is not registered | Negative | High | AC2 |
| TC-LOGIN-004 | Login | 'Log in' button is disabled when both fields are empty | UI | High | AC3 |
| TC-LOGIN-005 | Login | 'Log in' stays disabled when only one field is filled | Validation | Medium | AC3 |
| TC-LOGIN-006 | Login | 'Log in' enables once both fields are filled and disables again when one is cleared | UI | Medium | AC3 |
| TC-LOGIN-007 | Login | Email without '@' shows the inline format message | Validation | High | AC4 |
| TC-LOGIN-008 | Login | Email with a missing domain part shows the inline format message | Validation | Medium | AC4 |
| TC-LOGIN-009 | Login | Four consecutive failures do not lock the account | Boundary | High | AC5 |
| TC-LOGIN-010 | Login | Fifth consecutive failure locks the account | Boundary | Critical | AC5 |
| TC-LOGIN-011 | Login | Correct password is rejected while the account is locked | Business Rule | High | BR-003 |
| TC-LOGIN-012 | Login | Account is still locked just before 15 minutes have passed | Boundary | Medium | AC5 |
| TC-LOGIN-013 | Login | Account unlocks after 15 minutes | Boundary | High | AC5 |
| TC-LOGIN-014 | Login | Successful login resets the failed-attempt counter | Business Rule | High | BR-002 |
| TC-LOGIN-015 | Login | Log in with the email in different letter case | Positive | Medium | AC6 |
| TC-LOGIN-016 | Login | Log in with a password of the minimum length (8 characters) | Boundary | Medium | BR-001 |
| TC-LOGIN-017 | Login | Log in with a password of the maximum length (64 characters) | Boundary | Medium | BR-001 |

## Test Cases

### TC-LOGIN-001 — Log in with correct email and password for an active account

**Feature:** Login · **Type:** Positive · **Priority:** Critical · **Traces to:** AC1

**Preconditions**

- Active account exists for asha@example.com with password Valid#Pass1
- User is logged out and on the login page

**Test Data**

- `email`: asha@example.com
- `password`: Valid#Pass1

**Steps**

1. Enter `email` from test data in the Email field
2. Enter `password` from test data in the Password field
3. Click 'Log in'

**Expected Result:** User is redirected to the 'My Account' page and is logged in (reloading the page keeps them on 'My Account')

---

### TC-LOGIN-002 — Log in with a registered email and a wrong password

**Feature:** Login · **Type:** Negative · **Priority:** High · **Traces to:** AC2

**Preconditions**

- Active account exists for asha@example.com with password Valid#Pass1
- User is on the login page

**Test Data**

- `email`: asha@example.com
- `password`: Wrong#Pass9

**Steps**

1. Enter `email` from test data
2. Enter `password` from test data
3. Click 'Log in'

**Expected Result:** Message 'Invalid email or password' is shown, the user remains on the login page and is not logged in

---

### TC-LOGIN-003 — Log in with an email that is not registered

**Feature:** Login · **Type:** Negative · **Priority:** High · **Traces to:** AC2

**Preconditions**

- No account exists for nobody@example.com
- User is on the login page

**Test Data**

- `email`: nobody@example.com
- `password`: Valid#Pass1

**Steps**

1. Enter `email` from test data
2. Enter `password` from test data
3. Click 'Log in'

**Expected Result:** The same message 'Invalid email or password' is shown (no hint that the email is unknown) and the user remains on the login page

---

### TC-LOGIN-004 — 'Log in' button is disabled when both fields are empty

**Feature:** Login · **Type:** UI · **Priority:** High · **Traces to:** AC3

**Preconditions**

- User opens the login page fresh (no autofill)

**Test Data**

- `email`: 
- `password`: 

**Steps**

1. Leave Email and Password empty
2. Try to click 'Log in'

**Expected Result:** 'Log in' button is shown disabled and clicking it triggers no request and no navigation

---

### TC-LOGIN-005 — 'Log in' stays disabled when only one field is filled

**Feature:** Login · **Type:** Validation · **Priority:** Medium · **Traces to:** AC3

**Preconditions**

- User is on the login page with both fields empty

**Test Data**

- `case_a`: email: asha@example.com; password: 
- `case_b`: email: ; password: Valid#Pass1

**Steps**

1. Enter only the email from case_a
2. Observe the 'Log in' button
3. Clear the email and enter only the password from case_b
4. Observe the 'Log in' button

**Expected Result:** In both case_a and case_b the 'Log in' button remains disabled

---

### TC-LOGIN-006 — 'Log in' enables once both fields are filled and disables again when one is cleared

**Feature:** Login · **Type:** UI · **Priority:** Medium · **Traces to:** AC3

**Preconditions**

- User is on the login page with both fields empty

**Test Data**

- `email`: asha@example.com
- `password`: Valid#Pass1

**Steps**

1. Enter `email` and `password` from test data
2. Observe the 'Log in' button
3. Clear the Password field
4. Observe the 'Log in' button

**Expected Result:** The button becomes enabled after both fields are filled and becomes disabled again as soon as the password is cleared

---

### TC-LOGIN-007 — Email without '@' shows the inline format message

**Feature:** Login · **Type:** Validation · **Priority:** High · **Traces to:** AC4

**Preconditions**

- User is on the login page

**Test Data**

- `email`: asha.example.com
- `password`: Valid#Pass1

**Steps**

1. Enter `email` from test data
2. Enter `password` from test data
3. Click 'Log in' (or move focus out of the Email field)

**Expected Result:** Inline message 'Enter a valid email address' is shown under the Email field and the user is not logged in

---

### TC-LOGIN-008 — Email with a missing domain part shows the inline format message

**Feature:** Login · **Type:** Validation · **Priority:** Medium · **Traces to:** AC4

**Preconditions**

- User is on the login page

**Test Data**

- `email`: asha@
- `password`: Valid#Pass1

**Steps**

1. Enter `email` from test data
2. Enter `password` from test data
3. Click 'Log in' (or move focus out of the Email field)

**Expected Result:** Inline message 'Enter a valid email address' is shown under the Email field and the user is not logged in

---

### TC-LOGIN-009 — Four consecutive failures do not lock the account

**Feature:** Login · **Type:** Boundary · **Priority:** High · **Traces to:** AC5

**Preconditions**

- Active account asha@example.com with 0 failed attempts

**Test Data**

- `email`: asha@example.com
- `wrong_password`: Wrong#Pass9
- `correct_password`: Valid#Pass1
- `failed_attempts`: 4

**Steps**

1. Log in with `wrong_password` 4 times in a row
2. Log in with `correct_password`

**Expected Result:** Each of the 4 failures shows 'Invalid email or password' (no lock message); the 5th attempt with the correct password redirects to 'My Account'

---

### TC-LOGIN-010 — Fifth consecutive failure locks the account

**Feature:** Login · **Type:** Boundary · **Priority:** Critical · **Traces to:** AC5

**Preconditions**

- Active account asha@example.com with 0 failed attempts

**Test Data**

- `email`: asha@example.com
- `wrong_password`: Wrong#Pass9
- `failed_attempts`: 5

**Steps**

1. Log in with `wrong_password` 5 times in a row

**Expected Result:** After the 5th attempt the message 'Your account is locked. Try again in 15 minutes.' is shown and the user is not logged in

**Postconditions**

- Account asha@example.com is locked for 15 minutes

---

### TC-LOGIN-011 — Correct password is rejected while the account is locked

**Feature:** Login · **Type:** Business Rule · **Priority:** High · **Traces to:** BR-003

⚠️ Assumption-based (A-1)

**Preconditions**

- Account asha@example.com was locked by 5 failed attempts less than 1 minute ago

**Test Data**

- `email`: asha@example.com
- `password`: Valid#Pass1

**Steps**

1. Enter `email` and the correct `password`
2. Click 'Log in'

**Expected Result:** Message 'Your account is locked. Try again in 15 minutes.' is shown and the user is not redirected to 'My Account'

---

### TC-LOGIN-012 — Account is still locked just before 15 minutes have passed

**Feature:** Login · **Type:** Boundary · **Priority:** Medium · **Traces to:** AC5

⚠️ Assumption-based (A-1)

**Preconditions**

- Account asha@example.com was locked exactly 14 minutes 50 seconds ago (use a controllable clock or adjust the lock timestamp in the test environment)

**Test Data**

- `email`: asha@example.com
- `password`: Valid#Pass1
- `elapsed_since_lock`: 14m50s

**Steps**

1. Enter `email` and the correct `password`
2. Click 'Log in'

**Expected Result:** Message 'Your account is locked. Try again in 15 minutes.' is shown and the user is not logged in

---

### TC-LOGIN-013 — Account unlocks after 15 minutes

**Feature:** Login · **Type:** Boundary · **Priority:** High · **Traces to:** AC5

**Preconditions**

- Account asha@example.com was locked 15 minutes 10 seconds ago

**Test Data**

- `email`: asha@example.com
- `password`: Valid#Pass1
- `elapsed_since_lock`: 15m10s

**Steps**

1. Enter `email` and the correct `password`
2. Click 'Log in'

**Expected Result:** User is redirected to the 'My Account' page

---

### TC-LOGIN-014 — Successful login resets the failed-attempt counter

**Feature:** Login · **Type:** Business Rule · **Priority:** High · **Traces to:** BR-002

**Preconditions**

- Active account asha@example.com with 0 failed attempts

**Test Data**

- `email`: asha@example.com
- `wrong_password`: Wrong#Pass9
- `correct_password`: Valid#Pass1

**Steps**

1. Log in with `wrong_password` 4 times
2. Log in with `correct_password`
3. Log out
4. Log in with `wrong_password` 4 more times

**Expected Result:** The last 4 failures each show 'Invalid email or password' and no lock message appears, proving the counter restarted from 0 after the successful login

---

### TC-LOGIN-015 — Log in with the email in different letter case

**Feature:** Login · **Type:** Positive · **Priority:** Medium · **Traces to:** AC6

**Preconditions**

- Active account registered as asha@example.com with password Valid#Pass1

**Test Data**

- `email`: ASHA@Example.COM
- `password`: Valid#Pass1

**Steps**

1. Enter `email` from test data
2. Enter `password` from test data
3. Click 'Log in'

**Expected Result:** User is redirected to the 'My Account' page of the asha@example.com account

---

### TC-LOGIN-016 — Log in with a password of the minimum length (8 characters)

**Feature:** Login · **Type:** Boundary · **Priority:** Medium · **Traces to:** BR-001

⚠️ Assumption-based (A-2)

**Preconditions**

- Active account min8@example.com with an 8-character password

**Test Data**

- `email`: min8@example.com
- `password`: Abcd#123

**Steps**

1. Enter `email` from test data
2. Enter the 8-character `password`
3. Click 'Log in'

**Expected Result:** User is redirected to the 'My Account' page

---

### TC-LOGIN-017 — Log in with a password of the maximum length (64 characters)

**Feature:** Login · **Type:** Boundary · **Priority:** Medium · **Traces to:** BR-001

⚠️ Assumption-based (A-2)

**Preconditions**

- Active account max64@example.com with a 64-character password

**Test Data**

- `email`: max64@example.com
- `password`: 64 characters: 'Aa1#' repeated 16 times

**Steps**

1. Enter `email` from test data
2. Paste the 64-character `password`
3. Click 'Log in'

**Expected Result:** User is redirected to the 'My Account' page (the password is not truncated)
