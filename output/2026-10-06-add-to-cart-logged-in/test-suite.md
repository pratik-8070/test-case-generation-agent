# Add to Cart (logged-in user)

Generated: 2026-10-06 · Input types: REQUIREMENT · Test cases: 10

## Inputs analysed

| Source | Detected type | Confidence | Evidence |
|---|---|---|---|
| pasted text: 'Feature: Add to Cart' | REQUIREMENT | high | Labelled 'Requirement:' with a single 'should be able to' statement for one feature; Numbered 'Acceptance Criteria' list 1-6 attached to that requirement; No story format ('As a...'), no document sections, no API or UI artefacts |

## QA Summary

| Metric | Value |
|---|---|
| Requirements identified | 1 (1 covered) |
| Acceptance criteria identified | 6 (6 covered) |
| Business rules identified | 1 (0 covered) |
| Total test cases | 10 |
| Positive | 2 |
| Negative (incl. error handling) | 1 |
| Boundary | 1 |
| Edge cases | 3 |
| Validation | 2 |
| Other types | UI: 1 |
| By priority | Critical: 2, High: 5, Medium: 3 |
| Assumption-based cases | 4 |
| Coverage gaps | 4 |

All 6 acceptance criteria are covered: the happy path, the cart count from 0 and from a non-empty cart, data checks in the cart, and out-of-stock blocking, including the stock 1/0 boundary and stock running out while the page is open. Four cases depend on assumptions A-1 to A-3. The biggest gaps are guest behaviour (Q-4) and the absence of quantity rules (Q-1), which limit boundary and validation coverage.

## Clarifications & Assumptions

| ID | Question | Severity | Status | Answer |
|---|---|---|---|---|
| Q-1 | Is there a quantity selector on the product details page, or does each 'Add to Cart' click add exactly 1 unit? | non_blocking | assumed |  |
| Q-2 | When a product already in the cart is added again, does its quantity increase, or is a new line created? Does the cart count show total units or distinct products? | non_blocking | assumed |  |
| Q-3 | What is the exact out-of-stock message text? | non_blocking | assumed |  |
| Q-4 | What happens when a user who is not logged in clicks 'Add to Cart' (redirect to login, guest cart, or button hidden)? | non_blocking | out_of_scope |  |

| ID | Assumption | Related |
|---|---|---|
| A-1 | Each 'Add to Cart' click adds a quantity of 1 (no quantity selector is described). | AC-001.3, AC-001.4 |
| A-2 | Adding a product that is already in the cart increases the cart count by 1 and its total quantity in the cart to 2 (line structure is not asserted). | AC-001.3 |
| A-3 | The out-of-stock message states that the product is out of stock or unavailable; exact wording is not asserted. | AC-001.6 |

## Coverage Gaps

| Ref | Gap | Reason |
|---|---|---|
| BR-001 | Behaviour for users who are not logged in | The requirement covers logged-in users only; guest behaviour is undefined (Q-4). All cases use a logged-in precondition. |
| — | Quantity selection, maximum quantity per product and maximum cart size | No quantity selector or numeric limits are specified (Q-1), so no quantity validation or boundary cases can be written without inventing rules |
| — | Exact out-of-stock message text | AC 6 only says 'appropriate message' (Q-3); cases assert that an out-of-stock message appears |
| — | Rapid double-click, session expiry before clicking, sale/discounted prices in the cart | Expected behaviour is not specified |

## Traceability Matrix

| Kind | ID | Text | Test cases |
|---|---|---|---|
| REQ | REQ-001 | A logged-in user can add an available product to the shopping cart from the product details page | TC-CART-001, TC-CART-002, TC-CART-003, TC-CART-004, TC-CART-005, TC-CART-006, TC-CART-007, TC-CART-008, TC-CART-009, TC-CART-010 |
| AC | AC-001.1 | User can click the 'Add to Cart' button | TC-CART-002 |
| AC | AC-001.2 | The selected product is added to the cart | TC-CART-001, TC-CART-007, TC-CART-009 |
| AC | AC-001.3 | Cart count increases by 1 | TC-CART-001, TC-CART-005, TC-CART-009, TC-CART-010 |
| AC | AC-001.4 | Product name, price and quantity are displayed correctly in the cart | TC-CART-003, TC-CART-004, TC-CART-005 |
| AC | AC-001.5 | Out-of-stock products cannot be added to the cart | TC-CART-006, TC-CART-007, TC-CART-008 |
| AC | AC-001.6 | User sees an appropriate message when adding an out-of-stock product | TC-CART-006, TC-CART-008 |
| BR | BR-001 | Adding to cart is specified for logged-in users only | ❌ none |

## Test Case Index

| ID | Feature | Scenario | Type | Priority | Traces to |
|---|---|---|---|---|---|
| TC-CART-001 | Add to Cart | Add an in-stock product to an empty cart | Positive | Critical | AC-001.2, AC-001.3 |
| TC-CART-002 | Add to Cart | 'Add to Cart' button is visible and clickable for an in-stock product | UI | High | AC-001.1 |
| TC-CART-003 | Add to Cart | Cart shows the added product's name, price and quantity matching the product page | Validation | High | AC-001.4 |
| TC-CART-004 | Add to Cart | Price with decimals and thousands separator is shown exactly in the cart | Validation | Medium | AC-001.4 |
| TC-CART-005 | Add to Cart | Add a different product to a cart that already has items | Positive | High | AC-001.3, AC-001.4 |
| TC-CART-006 | Add to Cart | Out-of-stock product cannot be added and a message is shown | Negative | Critical | AC-001.5, AC-001.6 |
| TC-CART-007 | Add to Cart | Product with exactly 1 unit in stock (last unit) can be added | Boundary | High | AC-001.2, AC-001.5 |
| TC-CART-008 | Add to Cart | Product goes out of stock while its details page is open | Edge Case | High | AC-001.5, AC-001.6 |
| TC-CART-009 | Add to Cart | Added product remains in the cart after reloading the page | Edge Case | Medium | AC-001.2, AC-001.3 |
| TC-CART-010 | Add to Cart | Adding the same product a second time | Edge Case | Medium | AC-001.3 |

## Test Cases

### TC-CART-001 — Add an in-stock product to an empty cart

**Feature:** Add to Cart · **Type:** Positive · **Priority:** Critical · **Traces to:** AC-001.2, AC-001.3

**Preconditions**

- User asha@example.com is logged in
- Cart is empty and the cart count shows 0
- Product 'Blue Mug' (₹499.00) has stock 20

**Test Data**

- `product`: Blue Mug
- `price`: ₹499.00
- `stock`: 20

**Steps**

1. Open the 'Blue Mug' product details page
2. Click 'Add to Cart'
3. Open the cart

**Expected Result:** The cart count changes from 0 to 1 and the cart contains exactly one product, 'Blue Mug'

---

### TC-CART-002 — 'Add to Cart' button is visible and clickable for an in-stock product

**Feature:** Add to Cart · **Type:** UI · **Priority:** High · **Traces to:** AC-001.1

**Preconditions**

- User is logged in
- Product 'Blue Mug' has stock 20

**Test Data**

- `product`: Blue Mug
- `stock`: 20

**Steps**

1. Open the 'Blue Mug' product details page
2. Locate the 'Add to Cart' button
3. Hover over and click the button

**Expected Result:** The 'Add to Cart' button is displayed, enabled, and responds to the click by adding the product (cart count increases by 1)

---

### TC-CART-003 — Cart shows the added product's name, price and quantity matching the product page

**Feature:** Add to Cart · **Type:** Validation · **Priority:** High · **Traces to:** AC-001.4

⚠️ Assumption-based (A-1)

**Preconditions**

- User is logged in with an empty cart
- Product 'Blue Mug' (₹499.00) has stock 20

**Test Data**

- `product`: Blue Mug
- `price`: ₹499.00
- `expected_quantity`: 1

**Steps**

1. Open the 'Blue Mug' product details page and note the displayed name and price
2. Click 'Add to Cart'
3. Open the cart

**Expected Result:** The cart line shows name 'Blue Mug', price ₹499.00 (identical to the product page) and quantity 1

---

### TC-CART-004 — Price with decimals and thousands separator is shown exactly in the cart

**Feature:** Add to Cart · **Type:** Validation · **Priority:** Medium · **Traces to:** AC-001.4

**Preconditions**

- User is logged in with an empty cart
- Product 'Desk Lamp Pro' priced ₹1,299.50 has stock 5

**Test Data**

- `product`: Desk Lamp Pro
- `price`: ₹1,299.50

**Steps**

1. Open the 'Desk Lamp Pro' product details page
2. Click 'Add to Cart'
3. Open the cart

**Expected Result:** The cart shows price ₹1,299.50 for 'Desk Lamp Pro' with no rounding, truncation or currency change

---

### TC-CART-005 — Add a different product to a cart that already has items

**Feature:** Add to Cart · **Type:** Positive · **Priority:** High · **Traces to:** AC-001.3, AC-001.4

**Preconditions**

- User is logged in
- Cart contains 'Blue Mug' only and the cart count shows 1
- Product 'Desk Lamp Pro' (₹1,299.50) has stock 5

**Test Data**

- `existing_cart`: Blue Mug
- `product`: Desk Lamp Pro
- `price`: ₹1,299.50

**Steps**

1. Open the 'Desk Lamp Pro' product details page
2. Click 'Add to Cart'
3. Open the cart

**Expected Result:** The cart count changes from 1 to 2; the cart lists 'Blue Mug' and 'Desk Lamp Pro', each with its own name, price and quantity, and 'Blue Mug' is unchanged

---

### TC-CART-006 — Out-of-stock product cannot be added and a message is shown

**Feature:** Add to Cart · **Type:** Negative · **Priority:** Critical · **Traces to:** AC-001.5, AC-001.6

⚠️ Assumption-based (A-3)

**Preconditions**

- User is logged in
- Cart contains 'Blue Mug' only and the cart count shows 1
- Product 'Red Lamp' has stock 0

**Test Data**

- `product`: Red Lamp
- `stock`: 0

**Steps**

1. Open the 'Red Lamp' product details page
2. Click 'Add to Cart'
3. Open the cart

**Expected Result:** A message stating 'Red Lamp' is out of stock is displayed; the cart count stays 1 and the cart still contains only 'Blue Mug'

---

### TC-CART-007 — Product with exactly 1 unit in stock (last unit) can be added

**Feature:** Add to Cart · **Type:** Boundary · **Priority:** High · **Traces to:** AC-001.2, AC-001.5

**Preconditions**

- User is logged in with an empty cart
- Product 'Green Vase' has stock 1

**Test Data**

- `product`: Green Vase
- `stock`: 1

**Steps**

1. Open the 'Green Vase' product details page
2. Click 'Add to Cart'
3. Open the cart

**Expected Result:** No out-of-stock message is shown, the cart count changes from 0 to 1 and the cart contains 'Green Vase'

---

### TC-CART-008 — Product goes out of stock while its details page is open

**Feature:** Add to Cart · **Type:** Edge Case · **Priority:** High · **Traces to:** AC-001.5, AC-001.6

⚠️ Assumption-based (A-3)

**Preconditions**

- User is logged in with an empty cart
- Product 'Green Vase' has stock 1
- A second test account is available to buy the last unit

**Test Data**

- `product`: Green Vase
- `stock_before`: 1
- `stock_after`: 0

**Steps**

1. As the user, open the 'Green Vase' product details page and leave it open
2. Using the second account, purchase the last 'Green Vase' so its stock becomes 0
3. Without reloading, as the user click 'Add to Cart'
4. Open the cart

**Expected Result:** The out-of-stock message is displayed, the cart count stays 0 and 'Green Vase' is not in the cart

---

### TC-CART-009 — Added product remains in the cart after reloading the page

**Feature:** Add to Cart · **Type:** Edge Case · **Priority:** Medium · **Traces to:** AC-001.2, AC-001.3

**Preconditions**

- User is logged in with an empty cart
- Product 'Blue Mug' has stock 20

**Test Data**

- `product`: Blue Mug

**Steps**

1. Open the 'Blue Mug' product details page
2. Click 'Add to Cart'
3. Reload the browser page
4. Open the cart

**Expected Result:** After the reload the cart count still shows 1 and the cart still contains 'Blue Mug'

---

### TC-CART-010 — Adding the same product a second time

**Feature:** Add to Cart · **Type:** Edge Case · **Priority:** Medium · **Traces to:** AC-001.3

⚠️ Assumption-based (A-2)

**Preconditions**

- User is logged in
- Cart contains 'Blue Mug' with quantity 1 and the cart count shows 1
- Product 'Blue Mug' has stock 20

**Test Data**

- `product`: Blue Mug
- `existing_quantity`: 1

**Steps**

1. Open the 'Blue Mug' product details page
2. Click 'Add to Cart'
3. Open the cart

**Expected Result:** The cart count changes from 1 to 2 and the total quantity of 'Blue Mug' in the cart is 2

_Notes: Whether this is one line with quantity 2 or two lines is not specified (Q-2); only the totals are asserted._
