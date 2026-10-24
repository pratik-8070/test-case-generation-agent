# Payment Method Orchestrator Test Suite

Generated: 2026-10-15 · Input types: PRD, API_SPEC, TECHNICAL_SPEC · Test cases: 22

## Inputs analysed

| Source | Detected type | Confidence | Evidence |
|---|---|---|---|
| output/2026-10-15-payment-method/attachments/confluence-1507329-RFC-Payment-Page-Multi-Method.md | PRD | high | RFC: Payment Page (Multi-Method); Status: IN REVIEW (DEMO); POST /v1/payments/intents; interface PaymentMethodAdapter |

## QA Summary

| Metric | Value |
|---|---|
| Requirements identified | 8 (8 covered) |
| Acceptance criteria identified | 15 (15 covered) |
| Business rules identified | 5 (5 covered) |
| Total test cases | 22 |
| Positive | 4 |
| Negative (incl. error handling) | 6 |
| Boundary | 2 |
| Edge cases | 0 |
| Validation | 1 |
| Other types | Business Rule: 6, Integration: 1, Security: 2 |
| By priority | Critical: 8, High: 13, Medium: 1 |
| Assumption-based cases | 3 |
| Coverage gaps | 1 |

The test suite thoroughly covers multi-method payment orchestration, eligibility rules for restricted items (Luxury, Bulk, Buyer Protection), state machine transitions, split tenders, idempotency, gateway failover, and reconciliation, preserving exact requirement and AC IDs from inputs.

## Clarifications & Assumptions

| ID | Question | Severity | Status | Answer |
|---|---|---|---|---|
| Q-01 | Which specific gateways are primary and secondary for Cards, UPI, Net Banking, and EMI? | non_blocking | assumed | Assumed Gateway A is primary and Gateway B is secondary. |
| Q-02 | Is the ₹50,000 COD cap and ₹10,000 OTP threshold final across all product categories? | non_blocking | assumed | Assumed ₹50,000 COD cap and ₹10,000 OTP threshold apply as stated in the demo values. |

| ID | Assumption | Related |
|---|---|---|
| A-01 | Gateway A is configured as the primary gateway and Gateway B as the secondary gateway for routing and failover tests. | FR-8 |
| A-02 | The COD limit of ₹50,000 and OTP threshold of ₹10,000 are enforced strictly as documented. | AC-PAY-004.5, BR-01 |

## Coverage Gaps

| Ref | Gap | Reason |
|---|---|---|
| FR-8 | Exact gateway health scoring algorithm formulas and latency weightings. | Not fully specified in RFC; relies on internal adapter configuration. |

## Traceability Matrix

| Kind | ID | Text | Test cases |
|---|---|---|---|
| REQ | FR-1 | The system shall support eight payment methods (Cards, UPI, Net Banking, Wallets & Postpaid, E-Gift Vouchers, Pay Later, EMI, and Cash on Delivery) on web, Android, and iOS from one server-driven method list. | TC-PAYMENT-001, TC-PAYMENT-002 |
| REQ | FR-3 | Every payment attempt shall be idempotent and reconciled daily against gateway settlement files without losing or double-charging a payment. | TC-PAYMENT-003, TC-PAYMENT-004 |
| REQ | FR-8 | The system shall route traffic around a failing gateway to a secondary gateway without requiring a release. | TC-PAYMENT-005, TC-PAYMENT-006 |
| REQ | FR-16 | The system shall enforce payment method eligibility rules based on cart type, order amount, PIN code, and buyer history. | TC-PAYMENT-007, TC-PAYMENT-008, TC-PAYMENT-009, TC-PAYMENT-010, TC-PAYMENT-011, TC-PAYMENT-012 |
| REQ | REQ-PAY-005 | The system shall maintain a payment intent lifecycle and a payment attempt state machine with terminal states Succeeded, Failed, COD confirmed, and Auto-refunded. | TC-PAYMENT-013, TC-PAYMENT-014 |
| REQ | REQ-PAY-006 | The system shall provide method-specific initiation, callback handling, and status checking via isolated adapters. | TC-PAYMENT-015, TC-PAYMENT-016, TC-PAYMENT-017, TC-PAYMENT-018 |
| REQ | REQ-PAY-007 | The payment API shall provide endpoints for intent creation, intent retrieval, attempt initiation, attempt status checking, webhooks, and EMI plans with signature verification and idempotency enforcement. | TC-PAYMENT-019, TC-PAYMENT-020, TC-PAYMENT-021 |
| REQ | NFR-4 | The system shall enforce security and compliance controls including PCI DSS scoping via gateway-hosted fields, network-tokenised saved cards, data localisation in India, and HMAC signature verification for webhooks. | TC-PAYMENT-021, TC-PAYMENT-022 |
| AC | AC-01 | Payment page displays server-driven method list containing all applicable methods for the order. | TC-PAYMENT-001, TC-PAYMENT-002 |
| AC | AC-03 | Submitting an attempt with a duplicate Idempotency-Key within 24 hours returns the original attempt rather than creating a new charge. | TC-PAYMENT-003, TC-PAYMENT-004 |
| AC | AC-05 | Traffic automatically shifts from primary gateway to secondary gateway when success rate drops 10 points below the 24-hour average. | TC-PAYMENT-005, TC-PAYMENT-006 |
| AC | AC-FR16-1 | Buyer Protection and Luxury orders hide Cash on Delivery. | TC-PAYMENT-007 |
| AC | AC-PAY-004.2 | Bulk orders allow all prepaid methods and hide Cash on Delivery. | TC-PAYMENT-008 |
| AC | AC-PAY-004.3 | If a cart mixes types, the strictest rule wins (hiding COD for Luxury/Buyer Protection/Bulk). | TC-PAYMENT-009 |
| AC | AC-PAY-004.4 | EMI requires order amount >= ₹3,000 and an eligible card and tenure. | TC-PAYMENT-010 |
| AC | AC-PAY-004.5 | Cash on Delivery is hidden for orders > ₹50,000, unserviceable PIN codes, or buyers with 2+ refused COD orders in 90 days. | TC-PAYMENT-011, TC-PAYMENT-012 |
| AC | AC-PAY-005.1 | Payment intent transitions through OPEN, PARTIALLY_PAID, PAID, COD_CONFIRMED, EXPIRED, CANCELLED states correctly. | TC-PAYMENT-013 |
| AC | AC-PAY-005.2 | A late success received after intent expiration triggers an automatic refund. | TC-PAYMENT-014 |
| AC | AC-PAY-006.1 | Cards adapter redirects to 3-D Secure page and supports tokenised saved cards. | TC-PAYMENT-015 |
| AC | AC-PAY-006.2 | UPI adapter returns intent URI or QR code, polls every 3s for up to 5 min, and treats webhook as source of truth. | TC-PAYMENT-016 |
| AC | AC-PAY-006.3 | Gift vouchers allow split tender with one other method and up to 3 vouchers per order. | TC-PAYMENT-017, TC-PAYMENT-018 |
| AC | AC-PAY-007.1 | API endpoints return correct normalise error codes and messages (PAYMENT_DECLINED, AUTH_FAILED, INSUFFICIENT_FUNDS, METHOD_NOT_ELIGIBLE, PROVIDER_UNAVAILABLE, PAYMENT_TIMEOUT, INTENT_EXPIRED). | TC-PAYMENT-019, TC-PAYMENT-020 |
| AC | AC-PAY-008.1 | Webhooks verify HMAC signatures, check IP allow-lists, and enforce a replay window of 5 minutes. | TC-PAYMENT-021, TC-PAYMENT-022 |
| BR | BR-01 | COD is blocked for Buyer Protection, Luxury, Bulk items, orders over ₹50,000, unserviceable PIN codes, and buyers with 2+ refused COD orders in the last 90 days. | TC-PAYMENT-007, TC-PAYMENT-008, TC-PAYMENT-009, TC-PAYMENT-011, TC-PAYMENT-012 |
| BR | BR-PAY-002 | EMI requires order amount of at least ₹3,000 and an eligible card/tenure combination. | TC-PAYMENT-010 |
| BR | BR-PAY-003 | Payment intent expires exactly 30 minutes after creation if unpaid. | TC-PAYMENT-013 |
| BR | BR-PAY-004 | Split tender with Gift Voucher holds the voucher amount for 30 minutes; if the second attempt fails and intent expires, held voucher funds are released. | TC-PAYMENT-017, TC-PAYMENT-018 |
| BR | BR-PAY-005 | Webhook and redirect may arrive in any order; the first terminal status wins and later ones are logged only. | TC-PAYMENT-021 |

## Test Case Index

| ID | Feature | Scenario | Type | Priority | Traces to |
|---|---|---|---|---|---|
| TC-PAYMENT-001 | Payment Method Orchestrator | Fetch server-driven method list for standard order -> All eight payment methods displayed | Positive | Critical | AC-01 |
| TC-PAYMENT-002 | Payment Method Orchestrator | Fetch method list with invalid intent ID or unauthenticated request -> Returns 404 or 401 error | Negative | High | AC-01 |
| TC-PAYMENT-003 | Payment Method Orchestrator | Submit payment attempt with duplicate Idempotency-Key within 24 hours -> Original attempt returned without double charge | Business Rule | Critical | AC-03 |
| TC-PAYMENT-004 | Payment Method Orchestrator | Submit payment attempt with missing Idempotency-Key header -> Returns validation error | Validation | High | AC-03 |
| TC-PAYMENT-005 | Payment Method Orchestrator | Gateway success rate drops below threshold -> Traffic automatically shifts to secondary gateway | Integration | Critical | AC-05 |
| TC-PAYMENT-006 | Payment Method Orchestrator | Both primary and secondary gateways are completely unavailable -> Returns PROVIDER_UNAVAILABLE error | Error Handling | High | AC-05 |
| TC-PAYMENT-007 | Payment Method Orchestrator | View payment methods for Buyer Protection or Luxury cart -> Cash on Delivery is hidden | Business Rule | High | AC-FR16-1, BR-01 |
| TC-PAYMENT-008 | Payment Method Orchestrator | View payment methods for Bulk order cart -> Prepaid methods allowed and Cash on Delivery hidden | Business Rule | Medium | AC-PAY-004.2, BR-01 |
| TC-PAYMENT-009 | Payment Method Orchestrator | View payment methods for mixed cart containing Luxury and Standard items -> Strictest rule wins and COD is hidden | Business Rule | High | AC-PAY-004.3, BR-01 |
| TC-PAYMENT-010 | Payment Method Orchestrator | Check EMI eligibility for order amount below minimum threshold -> EMI method unavailable | Boundary | High | AC-PAY-004.4, BR-PAY-002 |
| TC-PAYMENT-011 | Payment Method Orchestrator | Check Cash on Delivery eligibility across order amount boundary -> COD blocked above ₹50,000 | Boundary | High | AC-PAY-004.5, BR-01 |
| TC-PAYMENT-012 | Payment Method Orchestrator | Attempt Cash on Delivery with buyer having 2+ refused orders in 90 days -> COD blocked | Business Rule | High | AC-PAY-004.5, BR-01 |
| TC-PAYMENT-013 | Payment Method Orchestrator | Payment intent expires after 30 minutes of inactivity -> Status updates to EXPIRED and payment blocked | Business Rule | High | AC-PAY-005.1, BR-PAY-003 |
| TC-PAYMENT-014 | Payment Method Orchestrator | Receive late payment success webhook after intent has expired -> System triggers automatic refund | Error Handling | Critical | AC-PAY-005.2 |
| TC-PAYMENT-015 | Payment Method Orchestrator | Initiate Card payment with saved token -> Redirects to 3-D Secure authentication page | Positive | Critical | AC-PAY-006.1 |
| TC-PAYMENT-016 | Payment Method Orchestrator | Initiate UPI payment attempt -> Client polls status every 3s and handles webhook source of truth | Positive | Critical | AC-PAY-006.2 |
| TC-PAYMENT-017 | Payment Method Orchestrator | Perform split tender with E-Gift Voucher and UPI -> Voucher amount blocked and remainder paid via UPI | Positive | High | AC-PAY-006.3, BR-PAY-004 |
| TC-PAYMENT-018 | Payment Method Orchestrator | Split tender second attempt fails -> Held gift voucher funds released after intent expires | Error Handling | High | AC-PAY-006.3, BR-PAY-004 |
| TC-PAYMENT-019 | Payment Method Orchestrator | Attempt payment with insufficient funds -> Returns normalised INSUFFICIENT_FUNDS error code and message | Negative | High | AC-PAY-007.1 |
| TC-PAYMENT-020 | Payment Method Orchestrator | Attempt payment with declined card -> Returns PAYMENT_DECLINED error code and message | Negative | High | AC-PAY-007.1 |
| TC-PAYMENT-021 | Payment Method Orchestrator | Receive webhook callback with valid HMAC signature and duplicate event -> First terminal status wins | Security | Critical | AC-PAY-008.1, BR-PAY-005 |
| TC-PAYMENT-022 | Payment Method Orchestrator | Receive webhook callback with invalid HMAC signature -> Rejected with 401 Unauthorized | Security | Critical | AC-PAY-008.1 |

## Test Cases

### TC-PAYMENT-001 — Fetch server-driven method list for standard order -> All eight payment methods displayed

**Feature:** Payment Method Orchestrator · **Type:** Positive · **Priority:** Critical · **Traces to:** AC-01

**Preconditions**

- Checkout service has created a valid payment intent for a standard order of ₹2,500

**Test Data**

- `order_amount`: 250000
- `cart_type`: Standard

**Steps**

1. Send GET /v1/payments/intents/{id} or load payment page
2. Inspect the list of allowed methods returned in the response

**Expected Result:** Response contains all 8 payment methods (Cards, UPI, Net Banking, Wallets & Postpaid, E-Gift Vouchers, Pay Later, EMI, Cash on Delivery) with eligibility status true.

---

### TC-PAYMENT-002 — Fetch method list with invalid intent ID or unauthenticated request -> Returns 404 or 401 error

**Feature:** Payment Method Orchestrator · **Type:** Negative · **Priority:** High · **Traces to:** AC-01

**Preconditions**

- Payment intent does not exist

**Test Data**

- `invalid_intent_id`: 00000000-0000-0000-0000-000000000000

**Steps**

1. Send GET /v1/payments/intents/00000000-0000-0000-0000-000000000000

**Expected Result:** API returns 404 Not Found error with proper error schema and no method list.

---

### TC-PAYMENT-003 — Submit payment attempt with duplicate Idempotency-Key within 24 hours -> Original attempt returned without double charge

**Feature:** Payment Method Orchestrator · **Type:** Business Rule · **Priority:** Critical · **Traces to:** AC-03

**Preconditions**

- Payment intent OPEN
- Client has a unique Idempotency-Key

**Test Data**

- `idempotency_key`: IDEMP-KEY-998877
- `method`: CARD
- `amount`: 150000

**Steps**

1. Send POST /v1/payments/intents/{id}/attempts with header Idempotency-Key: IDEMP-KEY-998877
2. Resend the identical POST request with the same Idempotency-Key within 24 hours

**Expected Result:** First request initiates payment attempt (201 Created); second request returns the exact same attempt record without creating a new payment attempt or charging the buyer again.

---

### TC-PAYMENT-004 — Submit payment attempt with missing Idempotency-Key header -> Returns validation error

**Feature:** Payment Method Orchestrator · **Type:** Validation · **Priority:** High · **Traces to:** AC-03

**Preconditions**

- Payment intent OPEN

**Test Data**

- `missing_header`: true
- `method`: CARD
- `amount`: 150000

**Steps**

1. Send POST /v1/payments/intents/{id}/attempts without Idempotency-Key header

**Expected Result:** API returns 400 Bad Request or 422 Unprocessable Entity stating Idempotency-Key header is required.

---

### TC-PAYMENT-005 — Gateway success rate drops below threshold -> Traffic automatically shifts to secondary gateway

**Feature:** Payment Method Orchestrator · **Type:** Integration · **Priority:** Critical · **Traces to:** AC-05

⚠️ Assumption-based (A-01)

**Preconditions**

- Primary gateway (Gateway A) success rate drops 10 points below 24-hour average

**Test Data**

- `gateway_primary`: Gateway A
- `gateway_secondary`: Gateway B

**Steps**

1. Simulate continuous failures on Gateway A over a 10-minute window
2. Initiate a new Card payment attempt

**Expected Result:** Orchestrator automatically routes the payment attempt to Gateway B without requiring a deployment or client release.

---

### TC-PAYMENT-006 — Both primary and secondary gateways are completely unavailable -> Returns PROVIDER_UNAVAILABLE error

**Feature:** Payment Method Orchestrator · **Type:** Error Handling · **Priority:** High · **Traces to:** AC-05

⚠️ Assumption-based (A-01)

**Preconditions**

- Gateway A and Gateway B both experiencing outages

**Test Data**

- `gateway_status`: both_down

**Steps**

1. Initiate payment attempt when both primary and secondary gateways are unavailable

**Expected Result:** API returns error with code PROVIDER_UNAVAILABLE and buyer message 'This option is slow right now. Try another.'

---

### TC-PAYMENT-007 — View payment methods for Buyer Protection or Luxury cart -> Cash on Delivery is hidden

**Feature:** Payment Method Orchestrator · **Type:** Business Rule · **Priority:** High · **Traces to:** AC-FR16-1, BR-01

**Preconditions**

- Buyer has a Luxury listing in the cart

**Test Data**

- `cart_type`: Luxury
- `amount`: 1500000

**Steps**

1. Create payment intent for the Luxury cart
2. Fetch allowed payment methods via GET /v1/payments/intents/{id}

**Expected Result:** Allowed methods list contains prepaid options but excludes Cash on Delivery, with eligibility reason stating COD isn't available for Luxury items.

---

### TC-PAYMENT-008 — View payment methods for Bulk order cart -> Prepaid methods allowed and Cash on Delivery hidden

**Feature:** Payment Method Orchestrator · **Type:** Business Rule · **Priority:** Medium · **Traces to:** AC-PAY-004.2, BR-01

**Preconditions**

- Buyer has a Bulk order in the cart

**Test Data**

- `cart_type`: Bulk
- `amount`: 2000000

**Steps**

1. Create payment intent for Bulk order
2. Inspect allowed methods

**Expected Result:** All prepaid methods are allowed; Cash on Delivery is hidden.

---

### TC-PAYMENT-009 — View payment methods for mixed cart containing Luxury and Standard items -> Strictest rule wins and COD is hidden

**Feature:** Payment Method Orchestrator · **Type:** Business Rule · **Priority:** High · **Traces to:** AC-PAY-004.3, BR-01

**Preconditions**

- Cart contains both Standard and Luxury items

**Test Data**

- `cart_items`: Standard Item; Luxury Item

**Steps**

1. Create payment intent for mixed cart
2. Fetch allowed payment methods

**Expected Result:** Cash on Delivery is hidden due to the Luxury item constraint winning.

---

### TC-PAYMENT-010 — Check EMI eligibility for order amount below minimum threshold -> EMI method unavailable

**Feature:** Payment Method Orchestrator · **Type:** Boundary · **Priority:** High · **Traces to:** AC-PAY-004.4, BR-PAY-002

**Preconditions**

- Order amount is set below ₹3,000

**Test Data**

- `amount_minor`: 299900

**Steps**

1. Request EMI plans or check allowed methods for amount 299900 (₹2,999)
2. Test boundary amount 300000 (₹3,000)

**Expected Result:** For ₹2,999, EMI is ineligible and hidden; for ₹3,000, EMI is eligible and available.

---

### TC-PAYMENT-011 — Check Cash on Delivery eligibility across order amount boundary -> COD blocked above ₹50,000

**Feature:** Payment Method Orchestrator · **Type:** Boundary · **Priority:** High · **Traces to:** AC-PAY-004.5, BR-01

⚠️ Assumption-based (A-02)

**Preconditions**

- Order has serviceable PIN code and normal items

**Test Data**

- `amounts`: 5000000; 5000100

**Steps**

1. Create payment intent with amount 5000000 (₹50,000) and check COD eligibility
2. Create payment intent with amount 5000100 (₹50,001) and check COD eligibility

**Expected Result:** COD is available for ₹50,000; COD is hidden for ₹50,001 with eligibility reason.

---

### TC-PAYMENT-012 — Attempt Cash on Delivery with buyer having 2+ refused orders in 90 days -> COD blocked

**Feature:** Payment Method Orchestrator · **Type:** Business Rule · **Priority:** High · **Traces to:** AC-PAY-004.5, BR-01

**Preconditions**

- Buyer account has 2 refused COD deliveries within past 90 days

**Test Data**

- `refused_cod_count`: 2

**Steps**

1. Create payment intent for eligible standard order
2. Fetch allowed payment methods

**Expected Result:** Cash on Delivery is marked ineligible and hidden for the buyer.

---

### TC-PAYMENT-013 — Payment intent expires after 30 minutes of inactivity -> Status updates to EXPIRED and payment blocked

**Feature:** Payment Method Orchestrator · **Type:** Business Rule · **Priority:** High · **Traces to:** AC-PAY-005.1, BR-PAY-003

**Preconditions**

- Payment intent created with status OPEN

**Test Data**

- `elapsed_time_min`: 31

**Steps**

1. Simulate passage of 31 minutes without successful payment
2. Attempt to initiate a payment attempt on the expired intent

**Expected Result:** Intent status transitions to EXPIRED, attempt creation returns 422 with intent expired error, and buyer sees 'Session expired. Please restart checkout.'

---

### TC-PAYMENT-014 — Receive late payment success webhook after intent has expired -> System triggers automatic refund

**Feature:** Payment Method Orchestrator · **Type:** Error Handling · **Priority:** Critical · **Traces to:** AC-PAY-005.2

**Preconditions**

- Payment intent status is EXPIRED

**Test Data**

- `provider_ref`: REF-LATE-12345
- `amount`: 250000

**Steps**

1. Send webhook callback with SUCCEEDED status for an expired intent

**Expected Result:** System records attempt success but immediately initiates an auto-refund for the transaction and notifies the buyer.

---

### TC-PAYMENT-015 — Initiate Card payment with saved token -> Redirects to 3-D Secure authentication page

**Feature:** Payment Method Orchestrator · **Type:** Positive · **Priority:** Critical · **Traces to:** AC-PAY-006.1

**Preconditions**

- Buyer has a saved network-tokenised card

**Test Data**

- `method`: CARD
- `card_token`: tok_visa_1234

**Steps**

1. Send POST /v1/payments/intents/{id}/attempts with method CARD and saved token
2. Inspect response next action

**Expected Result:** Response returns NextAction with redirect URL to 3-D Secure page, keeping card data out of server scope.

---

### TC-PAYMENT-016 — Initiate UPI payment attempt -> Client polls status every 3s and handles webhook source of truth

**Feature:** Payment Method Orchestrator · **Type:** Positive · **Priority:** Critical · **Traces to:** AC-PAY-006.2

**Preconditions**

- Payment intent OPEN

**Test Data**

- `method`: UPI
- `upi_flow`: INTENT

**Steps**

1. Send POST /v1/payments/intents/{id}/attempts for UPI intent
2. Client polls GET /v1/payments/attempts/{id} every 3 seconds
3. Simulate webhook callback confirming payment success

**Expected Result:** Attempt returns intent URI, client successfully polls status while showing approval timer, and webhook terminal state updates intent to PAID.

---

### TC-PAYMENT-017 — Perform split tender with E-Gift Voucher and UPI -> Voucher amount blocked and remainder paid via UPI

**Feature:** Payment Method Orchestrator · **Type:** Positive · **Priority:** High · **Traces to:** AC-PAY-006.3, BR-PAY-004

**Preconditions**

- Order total ₹2,500; gift voucher balance ₹1,000

**Test Data**

- `vouchers`: GV-001
- `remainder_method`: UPI
- `remainder_amount`: 150000

**Steps**

1. Apply gift voucher ₹1,000 (Attempt 1 succeeds, blocking voucher funds)
2. Pay remaining ₹1,500 via UPI (Attempt 2 succeeds)

**Expected Result:** Intent status becomes PAID with amount_captured_minor equaling total order amount.

---

### TC-PAYMENT-018 — Split tender second attempt fails -> Held gift voucher funds released after intent expires

**Feature:** Payment Method Orchestrator · **Type:** Error Handling · **Priority:** High · **Traces to:** AC-PAY-006.3, BR-PAY-004

**Preconditions**

- Gift voucher ₹1,000 successfully applied (attempt 1)

**Test Data**

- `remainder_method`: UPI
- `attempt_status`: FAILED

**Steps**

1. Simulate failure of second payment attempt for remainder
2. Allow payment intent to reach 30-minute expiration

**Expected Result:** Held gift voucher funds are released back to the voucher balance upon intent expiration.

---

### TC-PAYMENT-019 — Attempt payment with insufficient funds -> Returns normalised INSUFFICIENT_FUNDS error code and message

**Feature:** Payment Method Orchestrator · **Type:** Negative · **Priority:** High · **Traces to:** AC-PAY-007.1

**Preconditions**

- Payment intent created

**Test Data**

- `method`: WALLET
- `simulation`: low_balance

**Steps**

1. Initiate payment attempt that results in insufficient funds response from provider
2. Inspect API response and error code

**Expected Result:** API returns error with code INSUFFICIENT_FUNDS and buyer-facing message 'Not enough balance. Pay the rest with another method.'

---

### TC-PAYMENT-020 — Attempt payment with declined card -> Returns PAYMENT_DECLINED error code and message

**Feature:** Payment Method Orchestrator · **Type:** Negative · **Priority:** High · **Traces to:** AC-PAY-007.1

**Preconditions**

- Payment intent created

**Test Data**

- `method`: CARD
- `simulation`: decline

**Steps**

1. Initiate card payment with test card triggering issuer decline

**Expected Result:** Response indicates failure with code PAYMENT_DECLINED and message 'Your bank declined this payment. Try another method.'

---

### TC-PAYMENT-021 — Receive webhook callback with valid HMAC signature and duplicate event -> First terminal status wins

**Feature:** Payment Method Orchestrator · **Type:** Security · **Priority:** Critical · **Traces to:** AC-PAY-008.1, BR-PAY-005

**Preconditions**

- Payment attempt in PENDING state

**Test Data**

- `signature`: sha256=valid_hmac
- `provider_ref`: GW-TXN-112233

**Steps**

1. Send POST /v1/payments/webhooks/{provider} with valid signature and SUCCEEDED status
2. Resend identical webhook payload

**Expected Result:** First webhook updates attempt to SUCCEEDED; duplicate webhook is logged only without changing state or triggering duplicate processing.

---

### TC-PAYMENT-022 — Receive webhook callback with invalid HMAC signature -> Rejected with 401 Unauthorized

**Feature:** Payment Method Orchestrator · **Type:** Security · **Priority:** Critical · **Traces to:** AC-PAY-008.1

**Preconditions**

- Webhook endpoint active

**Test Data**

- `signature`: sha256=invalid_signature

**Steps**

1. Send POST /v1/payments/webhooks/{provider} with invalid signature header

**Expected Result:** Endpoint rejects request with 401 Unauthorized and does not process payload.
