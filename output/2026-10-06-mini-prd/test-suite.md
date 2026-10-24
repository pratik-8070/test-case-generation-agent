# ShopEase Engagement Release v2.4

Generated: 2026-10-06 · Input types: PRD · Test cases: 31

## Inputs analysed

| Source | Detected type | Confidence | Evidence |
|---|---|---|---|
| resources/examples/mini-prd.md | PRD | high | Title 'PRD: ShopEase Engagement Release (v2.4)' with Overview, Users, Out of scope and Non-functional sections; Three feature sections (§2-§4) with functional requirement IDs FR-2.1..FR-4.4 |

## QA Summary

| Metric | Value |
|---|---|
| Requirements identified | 12 (12 covered) |
| Acceptance criteria identified | 0 (0 covered) |
| Business rules identified | 0 (0 covered) |
| Total test cases | 31 |
| Positive | 8 |
| Negative (incl. error handling) | 2 |
| Boundary | 10 |
| Edge cases | 1 |
| Validation | 1 |
| Other types | Authentication: 1, Authorization: 2, Business Rule: 5, Integration: 1 |
| By priority | Critical: 3, High: 19, Medium: 9 |
| Assumption-based cases | 1 |
| Coverage gaps | 7 |

All 12 functional requirements across Wishlist, Reviews and Coupons are covered, including boundaries at 50/51 wishlist items, 1000/1001 review characters, the coupon minimum subtotal and discounts at or above the subtotal. The non-functional 'load quickly' statement is reported as a gap because it has no target. Open questions Q-2..Q-4 leave expiry-day, move-to-cart and empty-review behaviour untested.

## Clarifications & Assumptions

| ID | Question | Severity | Status | Answer |
|---|---|---|---|---|
| Q-1 | What is shown when a coupon code does not exist? | non_blocking | assumed |  |
| Q-2 | Is a coupon still valid on its expiry date itself? | non_blocking | out_of_scope |  |
| Q-3 | Does moving a wishlist item to the cart remove it from the wishlist, and what happens for out-of-stock items? | non_blocking | out_of_scope |  |
| Q-4 | What does a product with no reviews show? | non_blocking | out_of_scope |  |
| Q-5 | What is the target load time for the wishlist page? | non_blocking | out_of_scope |  |

| ID | Assumption | Related |
|---|---|---|
| A-1 | An unknown coupon code is rejected and no discount is applied (message text unspecified). | FR-4.1 |

## Coverage Gaps

| Ref | Gap | Reason |
|---|---|---|
| — | Wishlist page load performance ('should load quickly') | No measurable target (Q-5); not testable as stated |
| — | Coupon validity on the expiry date itself | Not specified (Q-2); day-before and day-after are tested |
| — | Move-to-cart side effects on the wishlist and for out-of-stock items | Not specified (Q-3) |
| — | Product page with zero reviews | Not specified (Q-4) |
| — | Wishlist sharing and review moderation | Out of scope per PRD §1.2 |
| FR-2.1 | No negative case for heart add/remove | FR-2.1 defines no failure behaviour; the limit and guest paths are covered under FR-2.2/FR-2.3 |
| FR-4.2 | No separate negative case for discount application | Rejection paths for coupons are covered under FR-4.1 (unknown code), FR-4.3 (expiry/minimum) and FR-4.4 |

## Traceability Matrix

| Kind | ID | Text | Test cases |
|---|---|---|---|
| REQ | FR-2.1 | Customer adds a product to the wishlist with the heart icon; clicking the filled heart removes it | TC-WISHLIST-001, TC-WISHLIST-002 |
| REQ | FR-2.2 | Wishlist holds at most 50 products; adding a 51st shows 'Your wishlist is full (50 items)' | TC-WISHLIST-003, TC-WISHLIST-004 |
| REQ | FR-2.3 | Guest clicking the heart is redirected to login and the product is added after logging in | TC-WISHLIST-005, TC-WISHLIST-006 |
| REQ | FR-2.4 | Wishlist page lists products with current price and stock status and lets the customer move an item to the cart | TC-WISHLIST-007, TC-WISHLIST-008, TC-WISHLIST-009 |
| REQ | FR-3.1 | Only customers with a delivered order containing the product can review it | TC-REVIEW-001, TC-REVIEW-002, TC-REVIEW-003, TC-REVIEW-004 |
| REQ | FR-3.2 | A review has a required 1-5 star rating and optional text up to 1000 characters | TC-REVIEW-001, TC-REVIEW-005, TC-REVIEW-006, TC-REVIEW-007, TC-REVIEW-008 |
| REQ | FR-3.3 | One review per customer per product; it can be edited afterwards | TC-REVIEW-009, TC-REVIEW-010 |
| REQ | FR-3.4 | Product page shows the average rating rounded to one decimal and the total number of reviews | TC-REVIEW-010, TC-REVIEW-011 |
| REQ | FR-4.1 | Customer can enter one coupon code at checkout; codes are case-insensitive | TC-COUPON-001, TC-COUPON-003, TC-COUPON-004, TC-COUPON-011 |
| REQ | FR-4.2 | A valid coupon applies its percentage or fixed discount to the subtotal before shipping | TC-COUPON-001, TC-COUPON-002 |
| REQ | FR-4.3 | Coupons have an expiry date and a minimum subtotal with messages 'This coupon has expired' / 'Add ₹<amount> more to use this coupon' | TC-COUPON-005, TC-COUPON-006, TC-COUPON-007, TC-COUPON-008 |
| REQ | FR-4.4 | The discount can never make the order subtotal negative | TC-COUPON-009, TC-COUPON-010 |

## Test Case Index

| ID | Feature | Scenario | Type | Priority | Traces to |
|---|---|---|---|---|---|
| TC-WISHLIST-001 | Wishlist | Add a product to the wishlist with the heart icon | Positive | Critical | FR-2.1 |
| TC-WISHLIST-002 | Wishlist | Remove a product by clicking the filled heart | Positive | High | FR-2.1 |
| TC-WISHLIST-003 | Wishlist | Add the 50th product to a wishlist holding 49 | Boundary | High | FR-2.2 |
| TC-WISHLIST-004 | Wishlist | Adding a 51st product is rejected | Boundary | High | FR-2.2 |
| TC-WISHLIST-005 | Wishlist | Guest clicking the heart is redirected to login | Authentication | High | FR-2.3 |
| TC-WISHLIST-006 | Wishlist | After logging in from the heart redirect, the product is added | Integration | High | FR-2.3 |
| TC-WISHLIST-007 | Wishlist | Wishlist page shows the current price after a price change | Business Rule | High | FR-2.4 |
| TC-WISHLIST-008 | Wishlist | Wishlist page shows stock status for an out-of-stock product | Edge Case | Medium | FR-2.4 |
| TC-WISHLIST-009 | Wishlist | Move a wishlist item to the cart | Positive | High | FR-2.4 |
| TC-REVIEW-001 | Product Reviews | Eligible customer submits a review with rating and text | Positive | Critical | FR-3.1, FR-3.2 |
| TC-REVIEW-002 | Product Reviews | Customer without an order of the product cannot review it | Authorization | High | FR-3.1 |
| TC-REVIEW-003 | Product Reviews | Order not yet delivered does not allow a review | Business Rule | High | FR-3.1 |
| TC-REVIEW-004 | Product Reviews | Guest cannot submit a review | Authorization | Medium | FR-3.1 |
| TC-REVIEW-005 | Product Reviews | Review without a star rating is rejected | Validation | High | FR-3.2 |
| TC-REVIEW-006 | Product Reviews | Rating-only review with 1 star (minimum) is accepted | Boundary | Medium | FR-3.2 |
| TC-REVIEW-007 | Product Reviews | Review text of exactly 1000 characters is accepted | Boundary | High | FR-3.2 |
| TC-REVIEW-008 | Product Reviews | Review text of 1001 characters is not saved in full | Boundary | High | FR-3.2 |
| TC-REVIEW-009 | Product Reviews | Second review for the same product is not allowed | Business Rule | High | FR-3.3 |
| TC-REVIEW-010 | Product Reviews | Editing a review updates it and the average | Positive | Medium | FR-3.3, FR-3.4 |
| TC-REVIEW-011 | Product Reviews | Average rating is rounded to one decimal place with total count | Business Rule | High | FR-3.4 |
| TC-COUPON-001 | Coupon Codes | Percentage coupon is applied to the subtotal before shipping | Positive | Critical | FR-4.1, FR-4.2 |
| TC-COUPON-002 | Coupon Codes | Fixed-amount coupon is applied to the subtotal | Positive | High | FR-4.2 |
| TC-COUPON-003 | Coupon Codes | Coupon code is accepted in lowercase | Positive | Medium | FR-4.1 |
| TC-COUPON-004 | Coupon Codes | Only one coupon can be applied to an order | Business Rule | Medium | FR-4.1 |
| TC-COUPON-005 | Coupon Codes | Expired coupon is rejected | Negative | High | FR-4.3 |
| TC-COUPON-006 | Coupon Codes | Coupon expiring tomorrow is still accepted | Boundary | Medium | FR-4.3 |
| TC-COUPON-007 | Coupon Codes | Subtotal ₹1 below the coupon minimum is rejected | Boundary | High | FR-4.3 |
| TC-COUPON-008 | Coupon Codes | Subtotal exactly at the coupon minimum is accepted | Boundary | High | FR-4.3 |
| TC-COUPON-009 | Coupon Codes | Fixed discount larger than the subtotal does not make it negative | Boundary | High | FR-4.4 |
| TC-COUPON-010 | Coupon Codes | Fixed discount equal to the subtotal brings it to exactly zero | Boundary | Medium | FR-4.4 |
| TC-COUPON-011 | Coupon Codes | Unknown coupon code is not applied | Negative | Medium | FR-4.1 |

## Test Cases

### TC-WISHLIST-001 — Add a product to the wishlist with the heart icon

**Feature:** Wishlist · **Type:** Positive · **Priority:** Critical · **Traces to:** FR-2.1

**Preconditions**

- Customer asha@example.com is logged in
- Wishlist is empty

**Test Data**

- `product`: Blue Mug

**Steps**

1. Open the 'Blue Mug' product page
2. Click the empty heart icon
3. Open the wishlist page

**Expected Result:** The heart icon becomes filled and the wishlist page lists 'Blue Mug'

---

### TC-WISHLIST-002 — Remove a product by clicking the filled heart

**Feature:** Wishlist · **Type:** Positive · **Priority:** High · **Traces to:** FR-2.1

**Preconditions**

- Customer asha@example.com is logged in
- 'Blue Mug' is in the wishlist

**Test Data**

- `product`: Blue Mug

**Steps**

1. Open the 'Blue Mug' product page
2. Click the filled heart icon
3. Open the wishlist page

**Expected Result:** The heart icon becomes empty and 'Blue Mug' is no longer on the wishlist page

---

### TC-WISHLIST-003 — Add the 50th product to a wishlist holding 49

**Feature:** Wishlist · **Type:** Boundary · **Priority:** High · **Traces to:** FR-2.2

**Preconditions**

- Customer asha@example.com is logged in
- Wishlist contains 49 products

**Test Data**

- `existing_items`: 49
- `product`: Product #50

**Steps**

1. Open the product page of 'Product #50'
2. Click the heart icon
3. Open the wishlist page

**Expected Result:** The product is added and the wishlist page lists 50 products; no 'full' message is shown

---

### TC-WISHLIST-004 — Adding a 51st product is rejected

**Feature:** Wishlist · **Type:** Boundary · **Priority:** High · **Traces to:** FR-2.2

**Preconditions**

- Customer asha@example.com is logged in
- Wishlist contains 50 products

**Test Data**

- `existing_items`: 50
- `product`: Product #51

**Steps**

1. Open the product page of 'Product #51'
2. Click the heart icon
3. Open the wishlist page

**Expected Result:** Message 'Your wishlist is full (50 items)' is shown, the heart stays empty and the wishlist still lists exactly 50 products

---

### TC-WISHLIST-005 — Guest clicking the heart is redirected to login

**Feature:** Wishlist · **Type:** Authentication · **Priority:** High · **Traces to:** FR-2.3

**Preconditions**

- User is not logged in

**Test Data**

- `product`: Blue Mug

**Steps**

1. Open the 'Blue Mug' product page as a guest
2. Click the heart icon

**Expected Result:** The browser navigates to the login page and the product is not added to any wishlist yet

---

### TC-WISHLIST-006 — After logging in from the heart redirect, the product is added

**Feature:** Wishlist · **Type:** Integration · **Priority:** High · **Traces to:** FR-2.3

**Preconditions**

- User is a guest who clicked the heart on 'Blue Mug' and is on the login page
- Account asha@example.com has an empty wishlist

**Test Data**

- `email`: asha@example.com
- `password`: Valid#Pass1
- `product`: Blue Mug

**Steps**

1. Log in with the credentials from test data
2. Open the wishlist page

**Expected Result:** The wishlist of asha@example.com contains 'Blue Mug'

---

### TC-WISHLIST-007 — Wishlist page shows the current price after a price change

**Feature:** Wishlist · **Type:** Business Rule · **Priority:** High · **Traces to:** FR-2.4

**Preconditions**

- Customer asha@example.com is logged in
- 'Blue Mug' was added to the wishlist at ₹500
- The price of 'Blue Mug' was then changed to ₹450

**Test Data**

- `product`: Blue Mug
- `old_price`: ₹500
- `current_price`: ₹450

**Steps**

1. Open the wishlist page

**Expected Result:** 'Blue Mug' is listed with price ₹450 (not ₹500) and its stock status

---

### TC-WISHLIST-008 — Wishlist page shows stock status for an out-of-stock product

**Feature:** Wishlist · **Type:** Edge Case · **Priority:** Medium · **Traces to:** FR-2.4

**Preconditions**

- Customer asha@example.com is logged in
- 'Red Lamp' is in the wishlist and its stock is 0

**Test Data**

- `product`: Red Lamp
- `stock`: 0

**Steps**

1. Open the wishlist page

**Expected Result:** 'Red Lamp' is listed with an out-of-stock status and its current price

---

### TC-WISHLIST-009 — Move a wishlist item to the cart

**Feature:** Wishlist · **Type:** Positive · **Priority:** High · **Traces to:** FR-2.4

**Preconditions**

- Customer asha@example.com is logged in
- 'Blue Mug' (in stock) is in the wishlist
- Cart is empty

**Test Data**

- `product`: Blue Mug

**Steps**

1. Open the wishlist page
2. Use the move-to-cart action on 'Blue Mug'
3. Open the cart

**Expected Result:** The cart contains 'Blue Mug'

---

### TC-REVIEW-001 — Eligible customer submits a review with rating and text

**Feature:** Product Reviews · **Type:** Positive · **Priority:** Critical · **Traces to:** FR-3.1, FR-3.2

**Preconditions**

- Customer asha@example.com is logged in and has a DELIVERED order containing 'Blue Mug'
- asha has not reviewed 'Blue Mug'

**Test Data**

- `rating`: 5
- `text`: Great mug, keeps coffee hot.

**Steps**

1. Open the 'Blue Mug' product page
2. Open the review form
3. Select 5 stars and enter `text`
4. Submit the review

**Expected Result:** The review is saved and shown on the product page with 5 stars and the entered text

---

### TC-REVIEW-002 — Customer without an order of the product cannot review it

**Feature:** Product Reviews · **Type:** Authorization · **Priority:** High · **Traces to:** FR-3.1

**Preconditions**

- Customer ravi@example.com is logged in and has never ordered 'Blue Mug'

**Test Data**

- `product`: Blue Mug

**Steps**

1. Open the 'Blue Mug' product page
2. Try to open the review form and submit a 4-star review

**Expected Result:** No review from ravi@example.com is saved: the review form is unavailable or submission is refused, and the review count is unchanged

---

### TC-REVIEW-003 — Order not yet delivered does not allow a review

**Feature:** Product Reviews · **Type:** Business Rule · **Priority:** High · **Traces to:** FR-3.1

**Preconditions**

- Customer meera@example.com is logged in and her only order with 'Blue Mug' has status SHIPPED

**Test Data**

- `order_status`: SHIPPED

**Steps**

1. Open the 'Blue Mug' product page
2. Try to open the review form and submit a 4-star review

**Expected Result:** No review from meera@example.com is saved and the review count is unchanged

---

### TC-REVIEW-004 — Guest cannot submit a review

**Feature:** Product Reviews · **Type:** Authorization · **Priority:** Medium · **Traces to:** FR-3.1

**Preconditions**

- User is not logged in

**Test Data**

- `product`: Blue Mug

**Steps**

1. Open the 'Blue Mug' product page as a guest
2. Try to submit a 4-star review

**Expected Result:** No review is saved and the review count is unchanged

---

### TC-REVIEW-005 — Review without a star rating is rejected

**Feature:** Product Reviews · **Type:** Validation · **Priority:** High · **Traces to:** FR-3.2

**Preconditions**

- Customer asha@example.com is logged in and has a DELIVERED order containing 'Blue Mug'

**Test Data**

- `rating`: 
- `text`: No stars given

**Steps**

1. Open the review form for 'Blue Mug'
2. Enter `text` without selecting a rating
3. Submit the review

**Expected Result:** The review is not saved and the rating is indicated as required; the review count is unchanged

---

### TC-REVIEW-006 — Rating-only review with 1 star (minimum) is accepted

**Feature:** Product Reviews · **Type:** Boundary · **Priority:** Medium · **Traces to:** FR-3.2

**Preconditions**

- Customer asha@example.com is logged in and has a DELIVERED order containing 'Blue Mug'

**Test Data**

- `rating`: 1
- `text`: 

**Steps**

1. Open the review form for 'Blue Mug'
2. Select 1 star and leave the text empty
3. Submit the review

**Expected Result:** The review is saved and shown with 1 star and no text

---

### TC-REVIEW-007 — Review text of exactly 1000 characters is accepted

**Feature:** Product Reviews · **Type:** Boundary · **Priority:** High · **Traces to:** FR-3.2

**Preconditions**

- Customer asha@example.com is logged in and has a DELIVERED order containing 'Blue Mug'

**Test Data**

- `rating`: 4
- `text_length`: 1000

**Steps**

1. Open the review form for 'Blue Mug'
2. Select 4 stars and paste a 1000-character text
3. Submit the review

**Expected Result:** The review is saved and the displayed text contains all 1000 characters

---

### TC-REVIEW-008 — Review text of 1001 characters is not saved in full

**Feature:** Product Reviews · **Type:** Boundary · **Priority:** High · **Traces to:** FR-3.2

**Preconditions**

- Customer asha@example.com is logged in and has a DELIVERED order containing 'Blue Mug'

**Test Data**

- `rating`: 4
- `text_length`: 1001

**Steps**

1. Open the review form for 'Blue Mug'
2. Select 4 stars and paste a 1001-character text
3. Submit the review

**Expected Result:** No review with more than 1000 characters is stored: the field stops at 1000 characters or submission is refused with an error

---

### TC-REVIEW-009 — Second review for the same product is not allowed

**Feature:** Product Reviews · **Type:** Business Rule · **Priority:** High · **Traces to:** FR-3.3

**Preconditions**

- Customer asha@example.com is logged in and has a DELIVERED order containing 'Blue Mug'
- asha already has a 5-star review on 'Blue Mug'

**Test Data**

- `rating`: 3

**Steps**

1. Open the 'Blue Mug' product page
2. Try to submit a new 3-star review

**Expected Result:** No second review is created; asha still has exactly one review on 'Blue Mug' and the total count is unchanged

---

### TC-REVIEW-010 — Editing a review updates it and the average

**Feature:** Product Reviews · **Type:** Positive · **Priority:** Medium · **Traces to:** FR-3.3, FR-3.4

**Preconditions**

- 'Blue Mug' has exactly 3 reviews rated 4, 4 and 5; the 5-star review belongs to logged-in customer asha

**Test Data**

- `old_rating`: 5
- `new_rating`: 2

**Steps**

1. Open asha's review on 'Blue Mug'
2. Edit the rating from 5 to 2 and save
3. Reload the product page

**Expected Result:** asha's review shows 2 stars, the review count is still 3, and the average shows 3.3

---

### TC-REVIEW-011 — Average rating is rounded to one decimal place with total count

**Feature:** Product Reviews · **Type:** Business Rule · **Priority:** High · **Traces to:** FR-3.4

**Preconditions**

- 'Blue Mug' has exactly 3 reviews rated 4, 4 and 5

**Test Data**

- `ratings`: 4; 4; 5
- `expected_average`: 4.3

**Steps**

1. Open the 'Blue Mug' product page

**Expected Result:** The product page shows average rating 4.3 and a total of 3 reviews

---

### TC-COUPON-001 — Percentage coupon is applied to the subtotal before shipping

**Feature:** Coupon Codes · **Type:** Positive · **Priority:** Critical · **Traces to:** FR-4.1, FR-4.2

**Preconditions**

- Customer is logged in and at checkout
- Cart subtotal ₹1000, shipping ₹50
- Coupon SAVE10 (10% off, min subtotal ₹500, not expired) exists

**Test Data**

- `code`: SAVE10
- `subtotal`: 1000
- `shipping`: 50

**Steps**

1. Enter coupon code `code`
2. Apply the coupon

**Expected Result:** Discount ₹100 is applied, subtotal becomes ₹900, shipping stays ₹50 and the order total is ₹950

---

### TC-COUPON-002 — Fixed-amount coupon is applied to the subtotal

**Feature:** Coupon Codes · **Type:** Positive · **Priority:** High · **Traces to:** FR-4.2

**Preconditions**

- Customer is logged in and at checkout
- Cart subtotal ₹1000, shipping ₹50
- Coupon FLAT200 (₹200 off, min subtotal ₹500, not expired) exists

**Test Data**

- `code`: FLAT200
- `subtotal`: 1000
- `shipping`: 50

**Steps**

1. Enter coupon code `code`
2. Apply the coupon

**Expected Result:** Discount ₹200 is applied, subtotal becomes ₹800 and the order total is ₹850

---

### TC-COUPON-003 — Coupon code is accepted in lowercase

**Feature:** Coupon Codes · **Type:** Positive · **Priority:** Medium · **Traces to:** FR-4.1

**Preconditions**

- Customer is logged in and at checkout
- Cart subtotal ₹1000
- Coupon SAVE10 (10% off) exists

**Test Data**

- `code`: save10

**Steps**

1. Enter coupon code `code`
2. Apply the coupon

**Expected Result:** SAVE10 is applied and the subtotal becomes ₹900

---

### TC-COUPON-004 — Only one coupon can be applied to an order

**Feature:** Coupon Codes · **Type:** Business Rule · **Priority:** Medium · **Traces to:** FR-4.1

**Preconditions**

- Customer is logged in and at checkout
- Cart subtotal ₹1000
- Coupons SAVE10 and FLAT200 exist
- SAVE10 is already applied

**Test Data**

- `second_code`: FLAT200

**Steps**

1. Enter `second_code`
2. Apply the coupon
3. Review the order summary

**Expected Result:** The order summary shows exactly one coupon discount (either SAVE10 or FLAT200, never both combined)

---

### TC-COUPON-005 — Expired coupon is rejected

**Feature:** Coupon Codes · **Type:** Negative · **Priority:** High · **Traces to:** FR-4.3

**Preconditions**

- Customer is logged in and at checkout
- Cart subtotal ₹1000
- Coupon OLD10 expired yesterday

**Test Data**

- `code`: OLD10

**Steps**

1. Enter coupon code `code`
2. Apply the coupon

**Expected Result:** Message 'This coupon has expired' is shown and the subtotal stays ₹1000

---

### TC-COUPON-006 — Coupon expiring tomorrow is still accepted

**Feature:** Coupon Codes · **Type:** Boundary · **Priority:** Medium · **Traces to:** FR-4.3

**Preconditions**

- Customer is logged in and at checkout
- Cart subtotal ₹1000
- Coupon SOON10 (10% off) expires tomorrow

**Test Data**

- `code`: SOON10

**Steps**

1. Enter coupon code `code`
2. Apply the coupon

**Expected Result:** SOON10 is applied and the subtotal becomes ₹900

---

### TC-COUPON-007 — Subtotal ₹1 below the coupon minimum is rejected

**Feature:** Coupon Codes · **Type:** Boundary · **Priority:** High · **Traces to:** FR-4.3

**Preconditions**

- Customer is logged in and at checkout
- Cart subtotal ₹499
- Coupon SAVE10 has minimum subtotal ₹500

**Test Data**

- `code`: SAVE10
- `subtotal`: 499
- `minimum`: 500

**Steps**

1. Enter coupon code `code`
2. Apply the coupon

**Expected Result:** Message 'Add ₹1 more to use this coupon' is shown and the subtotal stays ₹499

---

### TC-COUPON-008 — Subtotal exactly at the coupon minimum is accepted

**Feature:** Coupon Codes · **Type:** Boundary · **Priority:** High · **Traces to:** FR-4.3

**Preconditions**

- Customer is logged in and at checkout
- Cart subtotal ₹500
- Coupon SAVE10 has minimum subtotal ₹500

**Test Data**

- `code`: SAVE10
- `subtotal`: 500
- `minimum`: 500

**Steps**

1. Enter coupon code `code`
2. Apply the coupon

**Expected Result:** SAVE10 is applied and the subtotal becomes ₹450

---

### TC-COUPON-009 — Fixed discount larger than the subtotal does not make it negative

**Feature:** Coupon Codes · **Type:** Boundary · **Priority:** High · **Traces to:** FR-4.4

**Preconditions**

- Customer is logged in and at checkout
- Cart subtotal ₹200
- Coupon FLAT300 (₹300 off, no minimum above ₹200, not expired) exists

**Test Data**

- `code`: FLAT300
- `subtotal`: 200

**Steps**

1. Enter coupon code `code`
2. Apply the coupon
3. Review the order summary

**Expected Result:** The subtotal after discount is not negative (≥ ₹0) and the order total is never below the shipping amount

---

### TC-COUPON-010 — Fixed discount equal to the subtotal brings it to exactly zero

**Feature:** Coupon Codes · **Type:** Boundary · **Priority:** Medium · **Traces to:** FR-4.4

**Preconditions**

- Customer is logged in and at checkout
- Cart subtotal ₹200
- Coupon FLAT200 (₹200 off, min subtotal ≤ ₹200) exists

**Test Data**

- `code`: FLAT200
- `subtotal`: 200

**Steps**

1. Enter coupon code `code`
2. Apply the coupon

**Expected Result:** The subtotal after discount is ₹0 and only shipping remains in the total

---

### TC-COUPON-011 — Unknown coupon code is not applied

**Feature:** Coupon Codes · **Type:** Negative · **Priority:** Medium · **Traces to:** FR-4.1

⚠️ Assumption-based (A-1)

**Preconditions**

- Customer is logged in and at checkout
- Cart subtotal ₹1000
- No coupon named NOPE123 exists

**Test Data**

- `code`: NOPE123

**Steps**

1. Enter coupon code `code`
2. Apply the coupon

**Expected Result:** The coupon is rejected with an error message and the subtotal stays ₹1000
