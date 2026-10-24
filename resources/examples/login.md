# US-101: Login with email and password

As a registered customer, I want to log in with my email and password so that I can access my account and order history.

## Acceptance Criteria

- AC1: Given a registered, active account, when the customer enters the correct email and password and clicks "Log in", then they are redirected to the "My Account" page.
- AC2: Given an incorrect email or password, when the customer clicks "Log in", then the message "Invalid email or password" is shown and the customer remains on the login page.
- AC3: The "Log in" button is disabled until both the email and password fields are non-empty.
- AC4: The email field must contain a valid email format; otherwise the inline message "Enter a valid email address" is shown under the field.
- AC5: After 5 consecutive failed login attempts the account is locked for 15 minutes and the message "Your account is locked. Try again in 15 minutes." is shown.
- AC6: Email matching is case-insensitive.

## Notes

- Password must be 8–64 characters (existing registration rule).
- A successful login resets the failed-attempt counter.
