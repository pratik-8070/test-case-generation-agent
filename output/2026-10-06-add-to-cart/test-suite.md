# Add to Cart

Generated: 2026-10-06 · Input types: ACCEPTANCE_CRITERIA · Test cases: 14

## Inputs analysed

| Source | Detected type | Confidence | Evidence |
|---|---|---|---|
| resources/examples/add-to-cart.md | ACCEPTANCE_CRITERIA | high | Title 'Feature: Add to Cart — Acceptance Criteria'; Six Given/When/Then criteria AC-CART-1..6 with no story or narrative |

## QA Summary

| Metric | Value |
|---|---|
| Requirements identified | 1 (1 covered) |
| Acceptance criteria identified | 6 (6 covered) |
| Business rules identified | 1 (1 covered) |
| Total test cases | 14 |
| Positive | 3 |
| Negative (incl. error handling) | 1 |
| Boundary | 6 |
| Edge cases | 0 |
| Validation | 1 |
| Other types | Business Rule: 2, Integration: 1 |
| By priority | Critical: 2, High: 7, Medium: 5 |
| Assumption-based cases | 4 |
| Coverage gaps | 3 |

All six acceptance criteria are covered, with boundaries on the 1-10 quantity range, the 10-unit line cap and available stock. Rejection of invalid quantities (TC-CART-004..006) and the over-cap add (TC-CART-009) rely on assumptions A-2 and A-1. The biggest open risk is the guest-cart merge conflict rule (Q-3).

## Clarifications & Assumptions

| ID | Question | Severity | Status | Answer |
|---|---|---|---|---|
| Q-1 | If a line has quantity 8 and the shopper adds 3 more, is the add rejected, capped at 10, or allowed? | non_blocking | assumed |  |
| Q-2 | How is an invalid quantity (0, 11, 2.5, empty) rejected: the selector prevents it, or an error message is shown? | non_blocking | assumed |  |
| Q-3 | When the guest cart and account cart contain the same product, are quantities summed, and is the 10-unit cap applied? | non_blocking | out_of_scope |  |
| Q-4 | Does the cart icon count total units or distinct lines (e.g. after AC-CART-2)? | non_blocking | out_of_scope |  |

| ID | Assumption | Related |
|---|---|---|
| A-1 | An add that would exceed 10 units on a line is rejected with 'You can buy a maximum of 10 units of this item' and the line quantity is unchanged. | BR-001 |
| A-2 | Quantities outside 1-10 or non-whole numbers cannot be added: the cart is unchanged (message text unspecified). | AC-CART-3 |

## Coverage Gaps

| Ref | Gap | Reason |
|---|---|---|
| — | Merging when guest and account carts contain the same product (sum vs cap at 10) | Not stated (Q-3) |
| — | Whether the cart icon counts units or lines after a quantity increase | Not stated (Q-4) |
| — | Adding a product with stock 0 and stock checks that include quantity already in the cart | AC-CART-1 and AC-CART-5 do not define these cases |

## Traceability Matrix

| Kind | ID | Text | Test cases |
|---|---|---|---|
| REQ | REQ-001 | A shopper can add a product to the cart from the product detail page | TC-CART-001, TC-CART-002, TC-CART-003, TC-CART-004, TC-CART-005, TC-CART-006, TC-CART-007, TC-CART-008, TC-CART-009, TC-CART-010, TC-CART-011, TC-CART-012, TC-CART-013, TC-CART-014 |
| AC | AC-CART-1 | Adding an in-stock product adds it with quantity 1, increments the cart icon count by 1 and shows toast 'Added to cart' | TC-CART-001, TC-CART-014 |
| AC | AC-CART-2 | Adding a product already in the cart increases the existing line's quantity by 1 instead of creating a new line | TC-CART-002, TC-CART-008 |
| AC | AC-CART-3 | Selected quantity must be a whole number between 1 and 10 inclusive | TC-CART-003, TC-CART-004, TC-CART-005, TC-CART-006 |
| AC | AC-CART-4 | Adding to a line with quantity 10 shows 'You can buy a maximum of 10 units of this item' and the quantity stays 10 | TC-CART-007, TC-CART-008 |
| AC | AC-CART-5 | Requesting more than the available stock shows 'Only <n> left in stock' and nothing is added | TC-CART-010, TC-CART-011 |
| AC | AC-CART-6 | A guest's items are stored in a guest cart and merged into the account cart on login | TC-CART-012, TC-CART-013 |
| BR | BR-001 | An add that would take a cart line above 10 units is rejected with the maximum message and the line keeps its quantity | TC-CART-009 |

## Test Case Index

| ID | Feature | Scenario | Type | Priority | Traces to |
|---|---|---|---|---|---|
| TC-CART-001 | Add to Cart | Add an in-stock product to an empty cart | Positive | Critical | AC-CART-1 |
| TC-CART-002 | Add to Cart | Adding a product already in the cart increments the existing line | Business Rule | High | AC-CART-2 |
| TC-CART-003 | Add to Cart | Add the maximum selectable quantity of 10 | Boundary | High | AC-CART-3 |
| TC-CART-004 | Add to Cart | Quantity 0 cannot be added | Boundary | High | AC-CART-3 |
| TC-CART-005 | Add to Cart | Quantity 11 cannot be added | Boundary | High | AC-CART-3 |
| TC-CART-006 | Add to Cart | Non-whole or empty quantity cannot be added | Validation | Medium | AC-CART-3 |
| TC-CART-007 | Add to Cart | Adding to a line already at 10 shows the maximum message | Boundary | High | AC-CART-4 |
| TC-CART-008 | Add to Cart | Adding to a line at 9 reaches the maximum of 10 | Boundary | Medium | AC-CART-4, AC-CART-2 |
| TC-CART-009 | Add to Cart | Add that would push a line from 8 to 11 is rejected | Business Rule | Medium | BR-001 |
| TC-CART-010 | Add to Cart | Requesting more than available stock is rejected | Negative | High | AC-CART-5 |
| TC-CART-011 | Add to Cart | Requesting exactly the available stock is allowed | Boundary | Medium | AC-CART-5 |
| TC-CART-012 | Add to Cart | Guest adds a product to a guest cart | Positive | High | AC-CART-6 |
| TC-CART-013 | Add to Cart | Guest cart is merged into the account cart on login | Integration | Critical | AC-CART-6 |
| TC-CART-014 | Add to Cart | Adding a second different product increments the cart count by 1 | Positive | Medium | AC-CART-1 |

## Test Cases

### TC-CART-001 — Add an in-stock product to an empty cart

**Feature:** Add to Cart · **Type:** Positive · **Priority:** Critical · **Traces to:** AC-CART-1

**Preconditions**

- Shopper is logged in with an empty cart
- Product 'Blue Mug' has stock 20

**Test Data**

- `product`: Blue Mug
- `quantity`: 1

**Steps**

1. Open the 'Blue Mug' product detail page
2. Click 'Add to cart'

**Expected Result:** Toast 'Added to cart' is shown, the cart icon count changes from 0 to 1, and the cart contains one 'Blue Mug' line with quantity 1

---

### TC-CART-002 — Adding a product already in the cart increments the existing line

**Feature:** Add to Cart · **Type:** Business Rule · **Priority:** High · **Traces to:** AC-CART-2

**Preconditions**

- Cart contains one 'Blue Mug' line with quantity 1
- Product 'Blue Mug' has stock 20

**Test Data**

- `product`: Blue Mug
- `existing_quantity`: 1

**Steps**

1. Open the 'Blue Mug' product detail page
2. Click 'Add to cart'
3. Open the cart

**Expected Result:** The cart still has exactly one 'Blue Mug' line, now with quantity 2; no second line is created

---

### TC-CART-003 — Add the maximum selectable quantity of 10

**Feature:** Add to Cart · **Type:** Boundary · **Priority:** High · **Traces to:** AC-CART-3

**Preconditions**

- Cart is empty
- Product 'Blue Mug' has stock 20

**Test Data**

- `product`: Blue Mug
- `quantity`: 10

**Steps**

1. Open the 'Blue Mug' product detail page
2. Select quantity 10
3. Click 'Add to cart'

**Expected Result:** Toast 'Added to cart' is shown and the cart contains 'Blue Mug' with quantity 10

---

### TC-CART-004 — Quantity 0 cannot be added

**Feature:** Add to Cart · **Type:** Boundary · **Priority:** High · **Traces to:** AC-CART-3

⚠️ Assumption-based (A-2)

**Preconditions**

- Cart is empty
- Product 'Blue Mug' has stock 20

**Test Data**

- `product`: Blue Mug
- `quantity`: 0

**Steps**

1. Open the 'Blue Mug' product detail page
2. Try to set quantity to 0
3. Click 'Add to cart' if enabled

**Expected Result:** Quantity 0 cannot be selected or the add is rejected; the cart stays empty and no 'Added to cart' toast appears

---

### TC-CART-005 — Quantity 11 cannot be added

**Feature:** Add to Cart · **Type:** Boundary · **Priority:** High · **Traces to:** AC-CART-3

⚠️ Assumption-based (A-2)

**Preconditions**

- Cart is empty
- Product 'Blue Mug' has stock 20

**Test Data**

- `product`: Blue Mug
- `quantity`: 11

**Steps**

1. Open the 'Blue Mug' product detail page
2. Try to set quantity to 11
3. Click 'Add to cart' if enabled

**Expected Result:** Quantity 11 cannot be selected or the add is rejected; the cart stays empty and no 'Added to cart' toast appears

---

### TC-CART-006 — Non-whole or empty quantity cannot be added

**Feature:** Add to Cart · **Type:** Validation · **Priority:** Medium · **Traces to:** AC-CART-3

⚠️ Assumption-based (A-2)

**Preconditions**

- Cart is empty
- Product 'Blue Mug' has stock 20

**Test Data**

- `product`: Blue Mug
- `quantities`: 2.5; ; abc

**Steps**

1. Open the 'Blue Mug' product detail page
2. For each value in `quantities`, try to enter it in the quantity field and click 'Add to cart'

**Expected Result:** None of the values can be added; the cart stays empty after every attempt

_Notes: If the quantity control is a dropdown/stepper that cannot accept these values, record that as the pass evidence._

---

### TC-CART-007 — Adding to a line already at 10 shows the maximum message

**Feature:** Add to Cart · **Type:** Boundary · **Priority:** High · **Traces to:** AC-CART-4

**Preconditions**

- Cart contains 'Blue Mug' with quantity 10
- Product 'Blue Mug' has stock 20

**Test Data**

- `product`: Blue Mug
- `existing_quantity`: 10

**Steps**

1. Open the 'Blue Mug' product detail page
2. Click 'Add to cart'

**Expected Result:** Message 'You can buy a maximum of 10 units of this item' is shown and the 'Blue Mug' line quantity remains 10

---

### TC-CART-008 — Adding to a line at 9 reaches the maximum of 10

**Feature:** Add to Cart · **Type:** Boundary · **Priority:** Medium · **Traces to:** AC-CART-4, AC-CART-2

**Preconditions**

- Cart contains 'Blue Mug' with quantity 9
- Product 'Blue Mug' has stock 20

**Test Data**

- `product`: Blue Mug
- `existing_quantity`: 9

**Steps**

1. Open the 'Blue Mug' product detail page
2. Click 'Add to cart'

**Expected Result:** Toast 'Added to cart' is shown and the line quantity becomes 10 with no maximum message

---

### TC-CART-009 — Add that would push a line from 8 to 11 is rejected

**Feature:** Add to Cart · **Type:** Business Rule · **Priority:** Medium · **Traces to:** BR-001

⚠️ Assumption-based (A-1)

**Preconditions**

- Cart contains 'Blue Mug' with quantity 8
- Product 'Blue Mug' has stock 20

**Test Data**

- `product`: Blue Mug
- `existing_quantity`: 8
- `quantity`: 3

**Steps**

1. Open the 'Blue Mug' product detail page
2. Select quantity 3
3. Click 'Add to cart'

**Expected Result:** Message 'You can buy a maximum of 10 units of this item' is shown and the line quantity stays 8

---

### TC-CART-010 — Requesting more than available stock is rejected

**Feature:** Add to Cart · **Type:** Negative · **Priority:** High · **Traces to:** AC-CART-5

**Preconditions**

- Cart is empty
- Product 'Red Lamp' has stock 3

**Test Data**

- `product`: Red Lamp
- `stock`: 3
- `quantity`: 4

**Steps**

1. Open the 'Red Lamp' product detail page
2. Select quantity 4
3. Click 'Add to cart'

**Expected Result:** Message 'Only 3 left in stock' is shown, nothing is added, and the cart icon count stays 0

---

### TC-CART-011 — Requesting exactly the available stock is allowed

**Feature:** Add to Cart · **Type:** Boundary · **Priority:** Medium · **Traces to:** AC-CART-5

**Preconditions**

- Cart is empty
- Product 'Red Lamp' has stock 3

**Test Data**

- `product`: Red Lamp
- `stock`: 3
- `quantity`: 3

**Steps**

1. Open the 'Red Lamp' product detail page
2. Select quantity 3
3. Click 'Add to cart'

**Expected Result:** Toast 'Added to cart' is shown, no stock message appears, and the cart has 'Red Lamp' with quantity 3

---

### TC-CART-012 — Guest adds a product to a guest cart

**Feature:** Add to Cart · **Type:** Positive · **Priority:** High · **Traces to:** AC-CART-6

**Preconditions**

- Shopper is not logged in and has an empty cart
- Product 'Blue Mug' has stock 20

**Test Data**

- `product`: Blue Mug
- `quantity`: 1

**Steps**

1. Open the 'Blue Mug' product detail page as a guest
2. Click 'Add to cart'
3. Open the cart

**Expected Result:** Toast 'Added to cart' is shown and the guest cart contains 'Blue Mug' with quantity 1, without being asked to log in

---

### TC-CART-013 — Guest cart is merged into the account cart on login

**Feature:** Add to Cart · **Type:** Integration · **Priority:** Critical · **Traces to:** AC-CART-6

**Preconditions**

- Account asha@example.com has 'Red Lamp' x1 in its cart
- Shopper is a guest with 'Blue Mug' x2 in the guest cart

**Test Data**

- `account`: asha@example.com
- `account_cart`: Red Lamp: 1
- `guest_cart`: Blue Mug: 2

**Steps**

1. As the guest, log in as asha@example.com
2. Open the cart

**Expected Result:** Cart contains 'Red Lamp' x1 and 'Blue Mug' x2; no guest item is lost

---

### TC-CART-014 — Adding a second different product increments the cart count by 1

**Feature:** Add to Cart · **Type:** Positive · **Priority:** Medium · **Traces to:** AC-CART-1

**Preconditions**

- Cart contains 'Blue Mug' x1 and the cart icon shows 1
- Product 'Red Lamp' has stock 3

**Test Data**

- `product`: Red Lamp
- `quantity`: 1

**Steps**

1. Open the 'Red Lamp' product detail page
2. Click 'Add to cart'

**Expected Result:** Toast 'Added to cart' is shown, the cart icon count changes from 1 to 2, and the cart has two separate lines
