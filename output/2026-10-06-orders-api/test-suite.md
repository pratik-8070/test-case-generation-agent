# Orders API v1.2.0

Generated: 2026-10-06 · Input types: API_SPEC · Test cases: 25

## Inputs analysed

| Source | Detected type | Confidence | Evidence |
|---|---|---|---|
| resources/examples/orders-api.yaml | API_SPEC | high | 'openapi: 3.0.3' header with a 'paths:' block for /orders and /orders/{orderId}; Request/response schemas, bearerAuth security scheme and status codes 200/201/400/401/404/409 |

## QA Summary

| Metric | Value |
|---|---|
| Requirements identified | 2 (2 covered) |
| Acceptance criteria identified | 7 (7 covered) |
| Business rules identified | 6 (6 covered) |
| Total test cases | 25 |
| Positive | 3 |
| Negative (incl. error handling) | 2 |
| Boundary | 8 |
| Edge cases | 0 |
| Validation | 7 |
| Other types | Authentication: 3, Authorization: 1, Business Rule: 1 |
| By priority | Critical: 5, High: 10, Medium: 9, Low: 1 |
| Assumption-based cases | 0 |
| Coverage gaps | 4 |

Both endpoints and every documented status code (200, 201, 400, 401, 404, 409) are covered, with boundaries for items (0/20/21), quantity (0/10/11) and coupon length (5/13). Cross-customer access is tested as 404 per the spec. The largest risks are undocumented responses for unknown references and coupon semantics (Q-2, Q-3).

## Clarifications & Assumptions

| ID | Question | Severity | Status | Answer |
|---|---|---|---|---|
| Q-1 | What does GET /orders/{orderId} return for a non-uuid orderId (400 or 404)? | non_blocking | out_of_scope |  |
| Q-2 | What happens with a well-formed couponCode that does not exist or is expired, and how does a coupon change the total? | non_blocking | out_of_scope |  |
| Q-3 | What is returned for a shippingAddressId or productId that does not exist or belongs to another customer? | non_blocking | out_of_scope |  |

## Coverage Gaps

| Ref | Gap | Reason |
|---|---|---|
| — | GET with a non-uuid orderId: response code not documented | Q-1 |
| — | Non-existent/expired coupon and the coupon's effect on total | Q-2; only the pattern is specified |
| — | Unknown or foreign productId / shippingAddressId | Q-3; response not documented |
| — | Order status after creation, total calculation, rate limiting, idempotency of POST | Not specified in the spec |

## Traceability Matrix

| Kind | ID | Text | Test cases |
|---|---|---|---|
| REQ | REQ-001 | POST /orders creates an order from the caller's cart items | TC-ORDERS-API-001, TC-ORDERS-API-002, TC-ORDERS-API-003, TC-ORDERS-API-004, TC-ORDERS-API-005, TC-ORDERS-API-006, TC-ORDERS-API-007, TC-ORDERS-API-008, TC-ORDERS-API-009, TC-ORDERS-API-010, TC-ORDERS-API-011, TC-ORDERS-API-012, TC-ORDERS-API-013, TC-ORDERS-API-014, TC-ORDERS-API-015, TC-ORDERS-API-016, TC-ORDERS-API-017, TC-ORDERS-API-018, TC-ORDERS-API-019, TC-ORDERS-API-020, TC-ORDERS-API-021 |
| REQ | REQ-002 | GET /orders/{orderId} returns an order by id | TC-ORDERS-API-022, TC-ORDERS-API-023, TC-ORDERS-API-024, TC-ORDERS-API-025 |
| AC | AC-001.1 | Valid request returns 201 with an Order body | TC-ORDERS-API-001, TC-ORDERS-API-002 |
| AC | AC-001.2 | Invalid request returns 400 with an Error body (code, message, field) | TC-ORDERS-API-004, TC-ORDERS-API-005 |
| AC | AC-001.3 | Missing or invalid bearer token returns 401 | TC-ORDERS-API-020, TC-ORDERS-API-021 |
| AC | AC-001.4 | Out-of-stock items return 409 with an Error body and no order is created | TC-ORDERS-API-019 |
| AC | AC-002.1 | Existing own order returns 200 with the Order body | TC-ORDERS-API-022 |
| AC | AC-002.2 | Missing or invalid bearer token returns 401 | TC-ORDERS-API-025 |
| AC | AC-002.3 | Unknown order, or an order of another customer, returns 404 | TC-ORDERS-API-023, TC-ORDERS-API-024 |
| BR | BR-001 | items and shippingAddressId are required | TC-ORDERS-API-004, TC-ORDERS-API-005 |
| BR | BR-002 | items has 1 to 20 entries (minItems 1, maxItems 20) | TC-ORDERS-API-006, TC-ORDERS-API-007, TC-ORDERS-API-008 |
| BR | BR-003 | Each item requires productId (uuid) and quantity (integer 1-10) | TC-ORDERS-API-009, TC-ORDERS-API-010, TC-ORDERS-API-011, TC-ORDERS-API-012, TC-ORDERS-API-013, TC-ORDERS-API-014 |
| BR | BR-004 | couponCode, when given, matches ^[A-Z0-9]{6,12}$ | TC-ORDERS-API-002, TC-ORDERS-API-016, TC-ORDERS-API-017, TC-ORDERS-API-018 |
| BR | BR-005 | On 201, stock is reserved for each item | TC-ORDERS-API-003 |
| BR | BR-006 | shippingAddressId is a uuid | TC-ORDERS-API-015 |

## Test Case Index

| ID | Feature | Scenario | Type | Priority | Traces to |
|---|---|---|---|---|---|
| TC-ORDERS-API-001 | Orders API | Create an order with only the required fields | Positive | Critical | AC-001.1 |
| TC-ORDERS-API-002 | Orders API | Create an order with all fields including a valid coupon code | Positive | High | AC-001.1, BR-004 |
| TC-ORDERS-API-003 | Orders API | Successful order reserves stock for each item | Business Rule | Critical | BR-005 |
| TC-ORDERS-API-004 | Orders API | Request without items is rejected | Validation | High | AC-001.2, BR-001 |
| TC-ORDERS-API-005 | Orders API | Request without shippingAddressId is rejected | Validation | High | AC-001.2, BR-001 |
| TC-ORDERS-API-006 | Orders API | Empty items array is rejected (0 items, below minItems 1) | Boundary | High | BR-002 |
| TC-ORDERS-API-007 | Orders API | Order with 20 items (maxItems) is accepted | Boundary | Medium | BR-002 |
| TC-ORDERS-API-008 | Orders API | Order with 21 items (above maxItems 20) is rejected | Boundary | High | BR-002 |
| TC-ORDERS-API-009 | Orders API | Item quantity 0 (below minimum 1) is rejected | Boundary | High | BR-003 |
| TC-ORDERS-API-010 | Orders API | Item quantity 10 (maximum) is accepted | Boundary | Medium | BR-003 |
| TC-ORDERS-API-011 | Orders API | Item quantity 11 (above maximum 10) is rejected | Boundary | High | BR-003 |
| TC-ORDERS-API-012 | Orders API | Non-integer item quantity is rejected | Validation | Medium | BR-003 |
| TC-ORDERS-API-013 | Orders API | Item with a non-uuid productId is rejected | Validation | Medium | BR-003 |
| TC-ORDERS-API-014 | Orders API | Item without quantity is rejected | Validation | Medium | BR-003 |
| TC-ORDERS-API-015 | Orders API | Non-uuid shippingAddressId is rejected | Validation | Medium | BR-006 |
| TC-ORDERS-API-016 | Orders API | Coupon code of 5 characters (below 6) is rejected | Boundary | Medium | BR-004 |
| TC-ORDERS-API-017 | Orders API | Coupon code of 13 characters (above 12) is rejected | Boundary | Medium | BR-004 |
| TC-ORDERS-API-018 | Orders API | Lowercase coupon code violates the pattern and is rejected | Validation | Low | BR-004 |
| TC-ORDERS-API-019 | Orders API | Order with an out-of-stock item is rejected with 409 | Negative | Critical | AC-001.4 |
| TC-ORDERS-API-020 | Orders API | Create order without a bearer token is rejected | Authentication | Critical | AC-001.3 |
| TC-ORDERS-API-021 | Orders API | Create order with an invalid or expired token is rejected | Authentication | High | AC-001.3 |
| TC-ORDERS-API-022 | Orders API | Get own order by id | Positive | High | AC-002.1 |
| TC-ORDERS-API-023 | Orders API | Get an order id that does not exist | Negative | Medium | AC-002.3 |
| TC-ORDERS-API-024 | Orders API | Get another customer's order returns 404 | Authorization | Critical | AC-002.3 |
| TC-ORDERS-API-025 | Orders API | Get order without a bearer token is rejected | Authentication | High | AC-002.2 |

## Test Cases

### TC-ORDERS-API-001 — Create an order with only the required fields

**Feature:** Orders API · **Type:** Positive · **Priority:** Critical · **Traces to:** AC-001.1

**Preconditions**

- Customer C1 has a valid bearer token
- Product P1 (uuid) has stock 50; product P2 (uuid) has stock 50
- C1 has shipping address S1 (uuid)

**Test Data**

- `body`: items: productId: <P1>; quantity: 1; shippingAddressId: <S1>

**Steps**

1. Send `POST /orders` with header `Authorization: Bearer <valid_token of customer C1>` and body `test_data.body`
2. Send `GET /orders/{id}` with the same header using `id` from the response

**Expected Result:** Response is `201`; body matches the Order schema: `id` is a uuid, `items` has 1 entry with productId P1 and quantity 1, `total` is a number, `createdAt` is a date-time; `GET /orders/{id}` returns the same order

---

### TC-ORDERS-API-002 — Create an order with all fields including a valid coupon code

**Feature:** Orders API · **Type:** Positive · **Priority:** High · **Traces to:** AC-001.1, BR-004

**Preconditions**

- Customer C1 has a valid bearer token
- Product P1 (uuid) has stock 50; product P2 (uuid) has stock 50
- C1 has shipping address S1 (uuid)
- Coupon SAVE2026 exists and is active

**Test Data**

- `body`: items: productId: <P1>; quantity: 2; productId: <P2>; quantity: 1; shippingAddressId: <S1>; couponCode: SAVE2026

**Steps**

1. Send `POST /orders` with header `Authorization: Bearer <valid_token of customer C1>` and body `test_data.body`

**Expected Result:** Response is `201`; body has a uuid `id` and 2 `items` matching the request (P1 x2, P2 x1)

---

### TC-ORDERS-API-003 — Successful order reserves stock for each item

**Feature:** Orders API · **Type:** Business Rule · **Priority:** Critical · **Traces to:** BR-005

**Preconditions**

- Customer C1 has a valid bearer token
- Product P1 (uuid) has stock 50; product P2 (uuid) has stock 50
- C1 has shipping address S1 (uuid)

**Test Data**

- `body`: items: productId: <P1>; quantity: 3; shippingAddressId: <S1>

**Steps**

1. Send `POST /orders` with header `Authorization: Bearer <valid_token of customer C1>` and body `test_data.body`
2. Check the available stock of P1 via the inventory admin view or DB

**Expected Result:** Response is `201` and the available stock of P1 drops from 50 to 47 (reserved quantity 3)

---

### TC-ORDERS-API-004 — Request without items is rejected

**Feature:** Orders API · **Type:** Validation · **Priority:** High · **Traces to:** AC-001.2, BR-001

**Preconditions**

- Customer C1 has a valid bearer token
- Product P1 (uuid) has stock 50; product P2 (uuid) has stock 50
- C1 has shipping address S1 (uuid)

**Test Data**

- `body`: shippingAddressId: <S1>

**Steps**

1. Send `POST /orders` with header `Authorization: Bearer <valid_token of customer C1>` and body `test_data.body`

**Expected Result:** Response is `400` with a body containing string `code` and `message` (`field` = "items" if provided); no order is created (C1's order list is unchanged)

---

### TC-ORDERS-API-005 — Request without shippingAddressId is rejected

**Feature:** Orders API · **Type:** Validation · **Priority:** High · **Traces to:** AC-001.2, BR-001

**Preconditions**

- Customer C1 has a valid bearer token
- Product P1 (uuid) has stock 50; product P2 (uuid) has stock 50
- C1 has shipping address S1 (uuid)

**Test Data**

- `body`: items: productId: <P1>; quantity: 1

**Steps**

1. Send `POST /orders` with header `Authorization: Bearer <valid_token of customer C1>` and body `test_data.body`

**Expected Result:** Response is `400` with a body containing string `code` and `message` (`field` = "shippingAddressId" if provided); no order is created (C1's order list is unchanged)

---

### TC-ORDERS-API-006 — Empty items array is rejected (0 items, below minItems 1)

**Feature:** Orders API · **Type:** Boundary · **Priority:** High · **Traces to:** BR-002

**Preconditions**

- Customer C1 has a valid bearer token
- Product P1 (uuid) has stock 50; product P2 (uuid) has stock 50
- C1 has shipping address S1 (uuid)

**Test Data**

- `body`: items: ; shippingAddressId: <S1>

**Steps**

1. Send `POST /orders` with header `Authorization: Bearer <valid_token of customer C1>` and body `test_data.body`

**Expected Result:** Response is `400` with a body containing string `code` and `message`; no order is created (C1's order list is unchanged)

---

### TC-ORDERS-API-007 — Order with 20 items (maxItems) is accepted

**Feature:** Orders API · **Type:** Boundary · **Priority:** Medium · **Traces to:** BR-002

**Preconditions**

- Customer C1 has a valid bearer token
- Product P1 (uuid) has stock 50; product P2 (uuid) has stock 50
- C1 has shipping address S1 (uuid)
- 20 distinct products with stock >= 1 exist

**Test Data**

- `body`: items: 20 entries, each {productId: distinct in-stock product uuid, quantity: 1}; shippingAddressId: <S1>

**Steps**

1. Send `POST /orders` with header `Authorization: Bearer <valid_token of customer C1>` and body `test_data.body`

**Expected Result:** Response is `201` and the Order body contains 20 items

---

### TC-ORDERS-API-008 — Order with 21 items (above maxItems 20) is rejected

**Feature:** Orders API · **Type:** Boundary · **Priority:** High · **Traces to:** BR-002

**Preconditions**

- Customer C1 has a valid bearer token
- Product P1 (uuid) has stock 50; product P2 (uuid) has stock 50
- C1 has shipping address S1 (uuid)
- 21 distinct products with stock >= 1 exist

**Test Data**

- `body`: items: 21 entries, each {productId: distinct in-stock product uuid, quantity: 1}; shippingAddressId: <S1>

**Steps**

1. Send `POST /orders` with header `Authorization: Bearer <valid_token of customer C1>` and body `test_data.body`

**Expected Result:** Response is `400` with a body containing string `code` and `message`; no order is created (C1's order list is unchanged)

---

### TC-ORDERS-API-009 — Item quantity 0 (below minimum 1) is rejected

**Feature:** Orders API · **Type:** Boundary · **Priority:** High · **Traces to:** BR-003

**Preconditions**

- Customer C1 has a valid bearer token
- Product P1 (uuid) has stock 50; product P2 (uuid) has stock 50
- C1 has shipping address S1 (uuid)

**Test Data**

- `body`: items: productId: <P1>; quantity: 0; shippingAddressId: <S1>

**Steps**

1. Send `POST /orders` with header `Authorization: Bearer <valid_token of customer C1>` and body `test_data.body`

**Expected Result:** Response is `400` with a body containing string `code` and `message`; no order is created (C1's order list is unchanged)

---

### TC-ORDERS-API-010 — Item quantity 10 (maximum) is accepted

**Feature:** Orders API · **Type:** Boundary · **Priority:** Medium · **Traces to:** BR-003

**Preconditions**

- Customer C1 has a valid bearer token
- Product P1 (uuid) has stock 50; product P2 (uuid) has stock 50
- C1 has shipping address S1 (uuid)

**Test Data**

- `body`: items: productId: <P1>; quantity: 10; shippingAddressId: <S1>

**Steps**

1. Send `POST /orders` with header `Authorization: Bearer <valid_token of customer C1>` and body `test_data.body`

**Expected Result:** Response is `201` and the order item for P1 has quantity 10

---

### TC-ORDERS-API-011 — Item quantity 11 (above maximum 10) is rejected

**Feature:** Orders API · **Type:** Boundary · **Priority:** High · **Traces to:** BR-003

**Preconditions**

- Customer C1 has a valid bearer token
- Product P1 (uuid) has stock 50; product P2 (uuid) has stock 50
- C1 has shipping address S1 (uuid)

**Test Data**

- `body`: items: productId: <P1>; quantity: 11; shippingAddressId: <S1>

**Steps**

1. Send `POST /orders` with header `Authorization: Bearer <valid_token of customer C1>` and body `test_data.body`

**Expected Result:** Response is `400` with a body containing string `code` and `message`; no order is created (C1's order list is unchanged)

---

### TC-ORDERS-API-012 — Non-integer item quantity is rejected

**Feature:** Orders API · **Type:** Validation · **Priority:** Medium · **Traces to:** BR-003

**Preconditions**

- Customer C1 has a valid bearer token
- Product P1 (uuid) has stock 50; product P2 (uuid) has stock 50
- C1 has shipping address S1 (uuid)

**Test Data**

- `body`: items: productId: <P1>; quantity: 2.5; shippingAddressId: <S1>
- `also_try`: quantity "2" (string)

**Steps**

1. Send `POST /orders` with header `Authorization: Bearer <valid_token of customer C1>` and body `test_data.body`
2. Repeat with the `also_try` value

**Expected Result:** Each request returns `400` with an Error body (`code`, `message`); no order is created

---

### TC-ORDERS-API-013 — Item with a non-uuid productId is rejected

**Feature:** Orders API · **Type:** Validation · **Priority:** Medium · **Traces to:** BR-003

**Preconditions**

- Customer C1 has a valid bearer token
- Product P1 (uuid) has stock 50; product P2 (uuid) has stock 50
- C1 has shipping address S1 (uuid)

**Test Data**

- `body`: items: productId: 12345; quantity: 1; shippingAddressId: <S1>

**Steps**

1. Send `POST /orders` with header `Authorization: Bearer <valid_token of customer C1>` and body `test_data.body`

**Expected Result:** Response is `400` with a body containing string `code` and `message`; no order is created (C1's order list is unchanged)

---

### TC-ORDERS-API-014 — Item without quantity is rejected

**Feature:** Orders API · **Type:** Validation · **Priority:** Medium · **Traces to:** BR-003

**Preconditions**

- Customer C1 has a valid bearer token
- Product P1 (uuid) has stock 50; product P2 (uuid) has stock 50
- C1 has shipping address S1 (uuid)

**Test Data**

- `body`: items: productId: <P1>; shippingAddressId: <S1>

**Steps**

1. Send `POST /orders` with header `Authorization: Bearer <valid_token of customer C1>` and body `test_data.body`

**Expected Result:** Response is `400` with a body containing string `code` and `message`; no order is created (C1's order list is unchanged)

---

### TC-ORDERS-API-015 — Non-uuid shippingAddressId is rejected

**Feature:** Orders API · **Type:** Validation · **Priority:** Medium · **Traces to:** BR-006

**Preconditions**

- Customer C1 has a valid bearer token
- Product P1 (uuid) has stock 50; product P2 (uuid) has stock 50
- C1 has shipping address S1 (uuid)

**Test Data**

- `body`: items: productId: <P1>; quantity: 1; shippingAddressId: home-address

**Steps**

1. Send `POST /orders` with header `Authorization: Bearer <valid_token of customer C1>` and body `test_data.body`

**Expected Result:** Response is `400` with a body containing string `code` and `message`; no order is created (C1's order list is unchanged)

---

### TC-ORDERS-API-016 — Coupon code of 5 characters (below 6) is rejected

**Feature:** Orders API · **Type:** Boundary · **Priority:** Medium · **Traces to:** BR-004

**Preconditions**

- Customer C1 has a valid bearer token
- Product P1 (uuid) has stock 50; product P2 (uuid) has stock 50
- C1 has shipping address S1 (uuid)

**Test Data**

- `body`: items: productId: <P1>; quantity: 1; shippingAddressId: <S1>; couponCode: SAVE1

**Steps**

1. Send `POST /orders` with header `Authorization: Bearer <valid_token of customer C1>` and body `test_data.body`

**Expected Result:** Response is `400` with a body containing string `code` and `message`; no order is created (C1's order list is unchanged)

---

### TC-ORDERS-API-017 — Coupon code of 13 characters (above 12) is rejected

**Feature:** Orders API · **Type:** Boundary · **Priority:** Medium · **Traces to:** BR-004

**Preconditions**

- Customer C1 has a valid bearer token
- Product P1 (uuid) has stock 50; product P2 (uuid) has stock 50
- C1 has shipping address S1 (uuid)

**Test Data**

- `body`: items: productId: <P1>; quantity: 1; shippingAddressId: <S1>; couponCode: SAVE2026EXTRA

**Steps**

1. Send `POST /orders` with header `Authorization: Bearer <valid_token of customer C1>` and body `test_data.body`

**Expected Result:** Response is `400` with a body containing string `code` and `message`; no order is created (C1's order list is unchanged)

---

### TC-ORDERS-API-018 — Lowercase coupon code violates the pattern and is rejected

**Feature:** Orders API · **Type:** Validation · **Priority:** Low · **Traces to:** BR-004

**Preconditions**

- Customer C1 has a valid bearer token
- Product P1 (uuid) has stock 50; product P2 (uuid) has stock 50
- C1 has shipping address S1 (uuid)

**Test Data**

- `body`: items: productId: <P1>; quantity: 1; shippingAddressId: <S1>; couponCode: save2026

**Steps**

1. Send `POST /orders` with header `Authorization: Bearer <valid_token of customer C1>` and body `test_data.body`

**Expected Result:** Response is `400` with a body containing string `code` and `message`; no order is created (C1's order list is unchanged)

---

### TC-ORDERS-API-019 — Order with an out-of-stock item is rejected with 409

**Feature:** Orders API · **Type:** Negative · **Priority:** Critical · **Traces to:** AC-001.4

**Preconditions**

- Customer C1 has a valid bearer token
- Product P1 (uuid) has stock 50; product P2 (uuid) has stock 50
- C1 has shipping address S1 (uuid)
- Product P3 (uuid) has stock 0

**Test Data**

- `body`: items: productId: <P3>; quantity: 1; shippingAddressId: <S1>

**Steps**

1. Send `POST /orders` with header `Authorization: Bearer <valid_token of customer C1>` and body `test_data.body`

**Expected Result:** Response is `409` with an Error body (`code`, `message`); no order is created and P3 stock stays 0

---

### TC-ORDERS-API-020 — Create order without a bearer token is rejected

**Feature:** Orders API · **Type:** Authentication · **Priority:** Critical · **Traces to:** AC-001.3

**Preconditions**

- Customer C1 has a valid bearer token
- Product P1 (uuid) has stock 50; product P2 (uuid) has stock 50
- C1 has shipping address S1 (uuid)

**Test Data**

- `headers`: 
- `body`: items: productId: <P1>; quantity: 1; shippingAddressId: <S1>

**Steps**

1. Send `POST /orders` with headers `test_data.headers` and body `test_data.body`

**Expected Result:** Response is `401` and no order is created

---

### TC-ORDERS-API-021 — Create order with an invalid or expired token is rejected

**Feature:** Orders API · **Type:** Authentication · **Priority:** High · **Traces to:** AC-001.3

**Preconditions**

- Customer C1 has a valid bearer token
- Product P1 (uuid) has stock 50; product P2 (uuid) has stock 50
- C1 has shipping address S1 (uuid)

**Test Data**

- `headers`: Authorization: Bearer expired-or-tampered-token
- `body`: items: productId: <P1>; quantity: 1; shippingAddressId: <S1>

**Steps**

1. Send `POST /orders` with headers `test_data.headers` and body `test_data.body`

**Expected Result:** Response is `401` and no order is created

---

### TC-ORDERS-API-022 — Get own order by id

**Feature:** Orders API · **Type:** Positive · **Priority:** High · **Traces to:** AC-002.1

**Preconditions**

- Customer C1 has a valid bearer token
- C1 owns order O1

**Test Data**

- `orderId`: <O1>

**Steps**

1. Send `GET /orders/{orderId}` with `orderId` from test data and header `Authorization: Bearer <valid_token of customer C1>`

**Expected Result:** Response is `200`; body matches the Order schema with `id` = O1 and the items, total and createdAt stored for O1

---

### TC-ORDERS-API-023 — Get an order id that does not exist

**Feature:** Orders API · **Type:** Negative · **Priority:** Medium · **Traces to:** AC-002.3

**Preconditions**

- Customer C1 has a valid bearer token
- No order with the test orderId exists

**Test Data**

- `orderId`: 00000000-0000-4000-8000-000000000000

**Steps**

1. Send `GET /orders/{orderId}` with `orderId` from test data and header `Authorization: Bearer <valid_token of customer C1>`

**Expected Result:** Response is `404` and no order data is returned

---

### TC-ORDERS-API-024 — Get another customer's order returns 404

**Feature:** Orders API · **Type:** Authorization · **Priority:** Critical · **Traces to:** AC-002.3

**Preconditions**

- Customer C1 has a valid bearer token
- Customer C2 owns order O2

**Test Data**

- `orderId`: <O2 owned by C2>

**Steps**

1. Send `GET /orders/{orderId}` with `orderId` from test data and header `Authorization: Bearer <valid_token of customer C1>`

**Expected Result:** Response is `404` (not `200` or `403`) and no data from C2's order is returned

---

### TC-ORDERS-API-025 — Get order without a bearer token is rejected

**Feature:** Orders API · **Type:** Authentication · **Priority:** High · **Traces to:** AC-002.2

**Preconditions**

- C1 owns order O1

**Test Data**

- `orderId`: <O1>

**Steps**

1. Send `GET /orders/{orderId}` with `orderId` from test data and header `(no Authorization header)`

**Expected Result:** Response is `401` and no order data is returned
