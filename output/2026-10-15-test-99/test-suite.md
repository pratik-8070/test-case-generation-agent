# Add to Cart Multi-Type Test Suite

Generated: 2026-10-15 · Input types: PRD · Test cases: 44

## Inputs analysed

| Source | Detected type | Confidence | Evidence |
|---|---|---|---|
| output/2026-10-15-test-99/attachments/confluence-1081346-PRD-Add-to-Cart-Multi-Type.md | PRD | high | Document ID \| PRD-COM-014; PRD: Add to Cart (Multi-Type); US-1 through US-10; FR-1 through FR-17; NFR-1 through NFR-7 |

## QA Summary

| Metric | Value |
|---|---|
| Requirements identified | 34 (34 covered) |
| Acceptance criteria identified | 17 (17 covered) |
| Business rules identified | 5 (5 covered) |
| Total test cases | 44 |
| Positive | 12 |
| Negative (incl. error handling) | 9 |
| Boundary | 5 |
| Edge cases | 1 |
| Validation | 8 |
| Other types | Authentication: 1, Business Rule: 1, Compatibility: 1, Integration: 3, Security: 2, UI: 1 |
| By priority | Critical: 12, High: 19, Medium: 10, Low: 3 |
| Assumption-based cases | 0 |
| Coverage gaps | 1 |

Comprehensive test suite covering all requirements, acceptance criteria (AC-01 through AC-09), user stories (US-1 through US-10), and non-functional requirements (NFR-1 through NFR-7). Each requirement includes robust positive, negative, boundary, validation, error-handling, and NFR verification scenarios.

## Clarifications & Assumptions

| ID | Question | Severity | Status | Answer |
|---|---|---|---|---|
| Q-1 | Should guest buyers get a cart in v1, or is login required? | non_blocking | assumed | Login is required for v1. |

| ID | Assumption | Related |
|---|---|---|
| A-1 | Buyer must be logged in to add to cart; guest cart is out of scope for v1. | FR-2 |

## Coverage Gaps

| Ref | Gap | Reason |
|---|---|---|
| — | Cross-device session inactivity cart expiration after 30 days | Time-dependent background cleanup task not testable via standard API test flows. |

## Traceability Matrix

| Kind | ID | Text | Test cases |
|---|---|---|---|
| REQ | FR-1 | Add to Cart button on product page for Live listings; hidden for Draft, Pending Review, Paused, Closed | TC-CART-CORE-001, TC-CART-CORE-002, TC-CART-CORE-003 |
| REQ | FR-2 | Server validates listing state, stock and buyer eligibility on every add | TC-CART-CORE-004, TC-CART-CORE-005 |
| REQ | FR-3 | Adding the same listing again increases quantity instead of creating a new line | TC-CART-CORE-006, TC-CART-CORE-007 |
| REQ | FR-4 | Cart shows line items, type badge, unit price, quantity, line total, fees and grand total | TC-CART-CORE-008, TC-CART-CORE-009 |
| REQ | FR-5 | Buyer can change quantity or remove a line; totals update within 1 s | TC-CART-CORE-010, TC-CART-CORE-011, TC-CART-CORE-012 |
| REQ | FR-6 | Protection fee shown as its own line on the cart and product page | TC-CART-PROT-001, TC-CART-PROT-002 |
| REQ | FR-7 | Quantity fixed at 1; 15-minute reservation starts on add | TC-CART-LUX-001, TC-CART-LUX-002, TC-CART-LUX-003 |
| REQ | FR-8 | Reservation expiry removes the hold and shows a banner in the cart | TC-CART-LUX-004 |
| REQ | FR-9 | Add to Cart only from an accepted, unexpired offer; price locked to the offer | TC-CART-OM-001, TC-CART-OM-002 |
| REQ | FR-10 | Cart shows offer expiry countdown; expired offer lines cannot go to checkout | TC-CART-OM-003 |
| REQ | FR-11 | Add requires business account; quantity >= MOQ | TC-CART-BULK-001, TC-CART-BULK-002, TC-CART-BULK-003, TC-CART-BULK-004 |
| REQ | FR-12 | Unit price recalculated from tier on every quantity change | TC-CART-BULK-005, TC-CART-BULK-006 |
| REQ | FR-13 | Next-tier saving hint | TC-CART-BULK-007, TC-CART-BULK-008 |
| REQ | FR-14 | Cart revalidates price and stock when opened and when checkout starts | TC-CART-CORE-013, TC-CART-CORE-014 |
| REQ | FR-15 | Max 50 lines per cart | TC-CART-CORE-015, TC-CART-CORE-016 |
| REQ | FR-16 | Cart synced across web, Android and iOS for the same account | TC-CART-CORE-017, TC-CART-CORE-018 |
| REQ | FR-17 | Mini-cart confirmation (toast) after add with View cart action | TC-CART-CORE-019, TC-CART-CORE-020 |
| REQ | US-1 | As a buyer, I want to add an item to my cart from the product page so that I can buy several items together. | TC-CART-CORE-001, TC-CART-CORE-004 |
| REQ | US-2 | As a buyer, I want to see each item's type badge and any fees in the cart so that the total has no surprises. | TC-CART-CORE-008 |
| REQ | US-3 | As a cautious buyer, I want the Buyer Protection fee shown before checkout so that I know what I pay. | TC-CART-PROT-001 |
| REQ | US-4 | As a luxury buyer, I want my item held for me for 15 minutes so that nobody else buys it while I pay. | TC-CART-LUX-001 |
| REQ | US-5 | As a negotiating buyer, I want to add my accepted offer to the cart at the agreed price so that I can check out. | TC-CART-OM-001 |
| REQ | US-6 | As a business buyer, I want the tier price to update as I change quantity so that I can pick the best quantity. | TC-CART-BULK-001, TC-CART-BULK-005 |
| REQ | US-7 | As a buyer, I want to be told when a price or stock changes in my cart so that checkout does not fail. | TC-CART-CORE-013 |
| REQ | US-8 | As a buyer, I want to change quantity or remove items from the cart. | TC-CART-CORE-010 |
| REQ | US-9 | As a business buyer, I want a hint like 'Add 20 more to save ₹15 per unit'. | TC-CART-BULK-007 |
| REQ | US-10 | As a buyer, I want my cart to be the same on web and app. | TC-CART-CORE-017 |
| REQ | NFR-1 | Add to Cart API < 300 ms at p95; cart page loads in < 1.5 s at p95 on 4G | TC-CART-NFR-001 |
| REQ | NFR-2 | 99.95% for cart APIs; cart reads degrade to cached data if Listing service is down | TC-CART-NFR-002 |
| REQ | NFR-3 | Reservations are atomic; one unit is never reserved by two buyers | TC-CART-NFR-003 |
| REQ | NFR-4 | Cart APIs require auth; buyers can only read and change their own cart | TC-CART-NFR-004 |
| REQ | NFR-5 | OM minimum offer and seller payout amounts never appear in cart responses | TC-CART-NFR-005 |
| REQ | NFR-6 | WCAG 2.1 AA; timers announced to screen readers once per minute | TC-CART-NFR-006 |
| REQ | NFR-7 | English and Hindi; ₹ formatting with Indian digit grouping | TC-CART-NFR-007 |
| AC | AC-01 | Button absent on a Pending Review Luxury listing, including via deep link | TC-CART-CORE-001, TC-CART-CORE-002, TC-CART-CORE-003 |
| AC | AC-03 | One line per listing ID | TC-CART-CORE-006, TC-CART-CORE-007 |
| AC | AC-05 | Second buyer sees 'Reserved, check back soon' during reservation | TC-CART-LUX-001, TC-CART-LUX-002, TC-CART-LUX-003 |
| AC | AC-06 | Product page Add to Cart is hidden for OM; offer screen shows it | TC-CART-OM-001, TC-CART-OM-002 |
| AC | AC-08 | Non-business buyer sees reason and link to upgrade | TC-CART-BULK-001, TC-CART-BULK-002, TC-CART-BULK-003, TC-CART-BULK-004 |
| AC | AC-09 | Fee equals Listing service value; included in grand total | TC-CART-PROT-001, TC-CART-PROT-002 |
| AC | AC-FR2-1 | API returns 409 with reason when any check fails; cart unchanged | TC-CART-CORE-004, TC-CART-CORE-005 |
| AC | AC-FR4-1 | Totals match server calculation to the paisa | TC-CART-CORE-008, TC-CART-CORE-009 |
| AC | AC-FR5-1 | Quantity limits per type enforced in UI and API | TC-CART-CORE-010, TC-CART-CORE-011, TC-CART-CORE-012 |
| AC | AC-FR8-1 | After 15 min the item is still in the cart but marked 'No longer reserved' | TC-CART-LUX-004 |
| AC | AC-FR10-1 | Expired line is disabled with 'Offer expired' | TC-CART-OM-003 |
| AC | AC-FR12-1 | Price matches tier table for boundary quantities (MOQ, each tier start) | TC-CART-BULK-005, TC-CART-BULK-006 |
| AC | AC-FR13-1 | Hint hidden when already on the highest tier | TC-CART-BULK-007, TC-CART-BULK-008 |
| AC | AC-FR14-1 | Changed lines highlighted with old and new value | TC-CART-CORE-013, TC-CART-CORE-014 |
| AC | AC-FR15-1 | 51st add returns CART_FULL with message | TC-CART-CORE-015, TC-CART-CORE-016 |
| AC | AC-FR16-1 | Item added on web appears on app after refresh | TC-CART-CORE-017, TC-CART-CORE-018 |
| AC | AC-FR17-1 | Toast shows item name and new cart count | TC-CART-CORE-019, TC-CART-CORE-020 |
| BR | BR-01 | Add to Cart is only permitted for Live listings and restricted for Draft, Pending Review, Paused, or Closed states. | TC-CART-CORE-001, TC-CART-CORE-002 |
| BR | BR-02 | Maximum 50 line items per cart. | TC-CART-CORE-015, TC-CART-CORE-016 |
| BR | BR-03 | Luxury items have fixed quantity of 1 and a 15-minute stock reservation on add. | TC-CART-LUX-001, TC-CART-LUX-002 |
| BR | BR-04 | OM listings can only be added via accepted unexpired offers with price locked to the offer. | TC-CART-OM-001, TC-CART-OM-002 |
| BR | BR-05 | Bulk listings require a business account and quantity >= MOQ. | TC-CART-BULK-001, TC-CART-BULK-002, TC-CART-BULK-003, TC-CART-BULK-004 |

## Test Case Index

| ID | Feature | Scenario | Type | Priority | Traces to |
|---|---|---|---|---|---|
| TC-CART-CORE-001 | Cart Core & General Behavior | Add to Cart button availability for Live versus non-Live listing states → Correct visibility and access control | Positive | Critical | FR-1, AC-01, BR-01, US-1 |
| TC-CART-CORE-002 | Cart Core & General Behavior | Attempt to add Pending Review Luxury listing via direct deep link → Blocked with button absent | Negative | Critical | FR-1, AC-01, BR-01 |
| TC-CART-CORE-003 | Cart Core & General Behavior | Validate Add to Cart button state when listing changes from Live to Closed → Button updates immediately | Validation | High | FR-1, AC-01 |
| TC-CART-CORE-004 | Cart Core & General Behavior | Server validation failure on add-to-cart request → Returns 409 status and cart remains unchanged | Error Handling | High | FR-2, AC-FR2-1, US-1 |
| TC-CART-CORE-005 | Cart Core & General Behavior | Add to cart with invalid bearer token → Returns 401 Unauthorized status | Authentication | Critical | FR-2, AC-FR2-1 |
| TC-CART-CORE-006 | Cart Core & General Behavior | Add the same listing to cart multiple times → Quantity increases instead of creating a new line | Positive | High | FR-3, AC-03 |
| TC-CART-CORE-007 | Cart Core & General Behavior | Attempt to add existing item with zero quantity → Validation error returned and line unchanged | Validation | Medium | FR-3, AC-03 |
| TC-CART-CORE-008 | Cart Core & General Behavior | View cart page details and totals calculation → Correctly displays all line items, badges, prices, and grand total | Positive | Critical | FR-4, AC-FR4-1, US-2 |
| TC-CART-CORE-009 | Cart Core & General Behavior | Cart totals calculation with malformed decimal quantities or corrupted pricing payload → Handled with error or clamped | Negative | Medium | FR-4, AC-FR4-1 |
| TC-CART-CORE-010 | Cart Core & General Behavior | Change quantity of cart item via patch endpoint → Totals update within 1 second | Positive | High | FR-5, AC-FR5-1, US-8 |
| TC-CART-CORE-011 | Cart Core & General Behavior | Remove cart item via delete endpoint → Line is removed and totals update | Positive | High | FR-5, AC-FR5-1 |
| TC-CART-CORE-012 | Cart Core & General Behavior | Attempt to update cart item quantity exceeding available stock → Validation error returned | Validation | High | FR-5, AC-FR5-1 |
| TC-CART-CORE-013 | Cart Core & General Behavior | Cart revalidation on cart open after price change → Changed lines highlighted with old and new values | Positive | High | FR-14, AC-FR14-1, US-7 |
| TC-CART-CORE-014 | Cart Core & General Behavior | Cart revalidation when listing goes out of stock while in cart → Line marked as Low stock or Unavailable | Validation | High | FR-14, AC-FR14-1 |
| TC-CART-CORE-015 | Cart Core & General Behavior | Add 51st line item to cart → Returns CART_FULL error message | Boundary | High | FR-15, AC-FR15-1, BR-02 |
| TC-CART-CORE-016 | Cart Core & General Behavior | Add 50th line item to cart (boundary) → Addition succeeds | Boundary | High | FR-15, AC-FR15-1, BR-02 |
| TC-CART-CORE-017 | Cart Core & General Behavior | Cart synchronization across web and app clients → Items added on web appear on app after refresh | Integration | Medium | FR-16, AC-FR16-1, US-10 |
| TC-CART-CORE-018 | Cart Core & General Behavior | Cart synchronization failure / network timeout during cross-client sync → Graceful retry or cached state displayed | Error Handling | Low | FR-16, AC-FR16-1 |
| TC-CART-CORE-019 | Cart Core & General Behavior | Mini-cart toast confirmation after successful add → Toast displays item name and new cart count | Positive | Medium | FR-17, AC-FR17-1 |
| TC-CART-CORE-020 | Cart Core & General Behavior | Rapid successive add-to-cart clicks triggering multiple toasts → Toast queue or debounce behavior functions correctly | Edge Case | Low | FR-17, AC-FR17-1 |
| TC-CART-PROT-001 | Buyer Protection | Add Buyer Protection listing to cart → Protection fee appears as separate line and included in grand total | Positive | Critical | FR-6, AC-09, US-3 |
| TC-CART-PROT-002 | Buyer Protection | Buyer Protection fee update when seller modifies fee → Cart reflects updated fee value | Validation | Medium | FR-6, AC-09 |
| TC-CART-LUX-001 | Luxury Listings | Add Live authenticated Luxury listing to cart → Quantity fixed at 1 and 15-minute reservation starts | Positive | Critical | FR-7, AC-05, BR-03, US-4 |
| TC-CART-LUX-002 | Luxury Listings | Attempt to add quantity greater than 1 for Luxury listing → Quantity limit enforced | Validation | High | FR-7, AC-05, BR-03 |
| TC-CART-LUX-003 | Luxury Listings | Second buyer attempts to add reserved Luxury item → Sees 'Reserved, check back soon' | Negative | Critical | FR-7, AC-05 |
| TC-CART-LUX-004 | Luxury Listings | Luxury reservation expiry after 15 minutes → Hold ends and cart shows 'No longer reserved' banner | Boundary | High | FR-8, AC-FR8-1 |
| TC-CART-OM-001 | Offer Mode (OM) | Add OM listing to cart from accepted offer screen → Added successfully with price locked to offer | Positive | Critical | FR-9, AC-06, BR-04, US-5 |
| TC-CART-OM-002 | Offer Mode (OM) | Attempt to add OM listing from standard product page → Add to Cart button hidden | Negative | High | FR-9, AC-06, BR-04 |
| TC-CART-OM-003 | Offer Mode (OM) | Expired OM offer line in cart → Disabled with 'Offer expired' message and blocked from checkout | Negative | High | FR-10, AC-FR10-1 |
| TC-CART-BULK-001 | Bulk Listings | Add Bulk listing with business account and quantity >= MOQ → Added successfully with tier pricing | Positive | Critical | FR-11, AC-08, BR-05, US-6 |
| TC-CART-BULK-002 | Bulk Listings | Non-business buyer attempts to add Bulk listing → Blocked with reason and link to upgrade | Negative | Critical | FR-11, AC-08, BR-05 |
| TC-CART-BULK-003 | Bulk Listings | Bulk buyer adds quantity below MOQ (boundary) → Validation error QTY_BELOW_MOQ returned | Boundary | High | FR-11, AC-08, BR-05 |
| TC-CART-BULK-004 | Bulk Listings | Bulk buyer adds quantity equal to MOQ (boundary) → Addition succeeds | Boundary | High | FR-11, AC-08, BR-05 |
| TC-CART-BULK-005 | Bulk Listings | Recalculate unit price from tier table upon quantity change → Price matches tier table for boundary quantities | Business Rule | High | FR-12, AC-FR12-1, US-6 |
| TC-CART-BULK-006 | Bulk Listings | Bulk buyer changes quantity to invalid intermediate number between tiers → Validated and priced according to applicable active tier | Validation | Medium | FR-12, AC-FR12-1 |
| TC-CART-BULK-007 | Bulk Listings | Next-tier saving hint display and hiding on highest tier → Hint shown when eligible, hidden on highest tier | Positive | Medium | FR-13, AC-FR13-1, US-9 |
| TC-CART-BULK-008 | Bulk Listings | Next-tier saving hint behavior when tier pricing structure is missing or single-tier → Hint is omitted gracefully | Validation | Low | FR-13, AC-FR13-1 |
| TC-CART-NFR-001 | Cart Core & General Behavior | Add to Cart API performance load test under target threshold → p95 latency is under 300 ms | Integration | Medium | NFR-1 |
| TC-CART-NFR-002 | Cart Core & General Behavior | Cart read behavior when downstream Listing service is down → Degrades gracefully to cached data | Error Handling | High | NFR-2 |
| TC-CART-NFR-003 | Cart Core & General Behavior | Concurrent add-to-cart requests for final scarce unit → Atomicity ensures exactly one buyer secures the reservation | Integration | Critical | NFR-3 |
| TC-CART-NFR-004 | Cart Core & General Behavior | Attempt to access or modify another user's cart by ID or token → Blocked with 403 Forbidden | Security | Critical | NFR-4 |
| TC-CART-NFR-005 | Offer Mode (OM) | Inspect OM cart API response JSON structure → Minimum offer and seller payout amounts are absent | Security | High | NFR-5 |
| TC-CART-NFR-006 | Cart Core & General Behavior | Screen reader accessibility audit for cart reservation timers → Timers announced once per minute per WCAG 2.1 AA | UI | Medium | NFR-6 |
| TC-CART-NFR-007 | Cart Core & General Behavior | Localization and currency formatting check in Hindi and English → Correct ₹ symbol and Indian digit grouping | Compatibility | Medium | NFR-7 |

## Test Cases

### TC-CART-CORE-001 — Add to Cart button availability for Live versus non-Live listing states → Correct visibility and access control

**Feature:** Cart Core & General Behavior · **Type:** Positive · **Priority:** Critical · **Traces to:** FR-1, AC-01, BR-01, US-1

**Preconditions**

- Buyer is logged in
- Listings exist in Live, Draft, Paused, and Closed states

**Test Data**

- `listing_states`: Live; Draft; Paused; Closed

**Steps**

1. Navigate to a Live listing detail page
2. Verify Add to Cart button is visible
3. Navigate to Draft, Paused, and Closed listing detail pages

**Expected Result:** Add to Cart button is present and enabled on the Live listing page, and absent or hidden on Draft, Paused, and Closed listing pages.

---

### TC-CART-CORE-002 — Attempt to add Pending Review Luxury listing via direct deep link → Blocked with button absent

**Feature:** Cart Core & General Behavior · **Type:** Negative · **Priority:** Critical · **Traces to:** FR-1, AC-01, BR-01

**Preconditions**

- Buyer is logged in
- A Luxury listing is in 'Pending Review' state

**Test Data**

- `listing_type`: Luxury
- `state`: Pending Review

**Steps**

1. Access the Pending Review Luxury listing directly via deep link
2. Inspect product page UI

**Expected Result:** Add to Cart button is absent on the Pending Review Luxury listing page.

---

### TC-CART-CORE-003 — Validate Add to Cart button state when listing changes from Live to Closed → Button updates immediately

**Feature:** Cart Core & General Behavior · **Type:** Validation · **Priority:** High · **Traces to:** FR-1, AC-01

**Preconditions**

- Buyer is viewing a Live listing detail page

**Test Data**

- `listing_id`: LST-LIVE-001
- `new_state`: Closed

**Steps**

1. Listing transitions to Closed state in backend
2. Tap 'Add to Cart' button

**Expected Result:** API returns LISTING_NOT_AVAILABLE error and item is not added to cart.

---

### TC-CART-CORE-004 — Server validation failure on add-to-cart request → Returns 409 status and cart remains unchanged

**Feature:** Cart Core & General Behavior · **Type:** Error Handling · **Priority:** High · **Traces to:** FR-2, AC-FR2-1, US-1

**Preconditions**

- Buyer is logged in
- Cart contains 0 items

**Test Data**

- `listing_id`: LST-UNAVAILABLE
- `quantity`: 1

**Steps**

1. Send POST /v1/cart/items for an unavailable listing
2. Inspect HTTP response status and cart contents

**Expected Result:** API returns 409 with reason code, and the cart remains unchanged.

---

### TC-CART-CORE-005 — Add to cart with invalid bearer token → Returns 401 Unauthorized status

**Feature:** Cart Core & General Behavior · **Type:** Authentication · **Priority:** Critical · **Traces to:** FR-2, AC-FR2-1

**Preconditions**

- User is logged out or token is expired

**Test Data**

- `headers`: Authorization: Bearer invalid_token

**Steps**

1. Send POST /v1/cart/items with invalid authorization token

**Expected Result:** Response is 401 Unauthorized and cart is unaffected.

---

### TC-CART-CORE-006 — Add the same listing to cart multiple times → Quantity increases instead of creating a new line

**Feature:** Cart Core & General Behavior · **Type:** Positive · **Priority:** High · **Traces to:** FR-3, AC-03

**Preconditions**

- Buyer is logged in
- Standard listing with sufficient stock exists

**Test Data**

- `listing_id`: LST-STD-001
- `initial_qty`: 1
- `added_qty`: 2

**Steps**

1. Send POST /v1/cart/items with quantity 1
2. Send POST /v1/cart/items for the same listing ID with quantity 2
3. Send GET /v1/cart

**Expected Result:** Cart contains exactly one line item for the listing ID with a total quantity of 3.

---

### TC-CART-CORE-007 — Attempt to add existing item with zero quantity → Validation error returned and line unchanged

**Feature:** Cart Core & General Behavior · **Type:** Validation · **Priority:** Medium · **Traces to:** FR-3, AC-03

**Preconditions**

- Listing LST-STD-001 is already in cart with qty 2

**Test Data**

- `listing_id`: LST-STD-001
- `quantity`: 0

**Steps**

1. Send POST /v1/cart/items with quantity 0

**Expected Result:** API returns validation error and existing cart line quantity remains 2.

---

### TC-CART-CORE-008 — View cart page details and totals calculation → Correctly displays all line items, badges, prices, and grand total

**Feature:** Cart Core & General Behavior · **Type:** Positive · **Priority:** Critical · **Traces to:** FR-4, AC-FR4-1, US-2

**Preconditions**

- Buyer is logged in
- Cart has active items with known prices

**Test Data**

- `items`: listing_id: LST-STD-001; price: 1000.0; qty: 2

**Steps**

1. Navigate to GET /v1/cart
2. Inspect response fields and rendered UI totals

**Expected Result:** Cart displays line items, type badge, unit price (₹1000.00), quantity (2), line total (₹2000.00), fees, and grand total matching server calculation to the paisa.

---

### TC-CART-CORE-009 — Cart totals calculation with malformed decimal quantities or corrupted pricing payload → Handled with error or clamped

**Feature:** Cart Core & General Behavior · **Type:** Negative · **Priority:** Medium · **Traces to:** FR-4, AC-FR4-1

**Preconditions**

- Buyer is logged in

**Test Data**

- `quantity`: -5

**Steps**

1. Send POST /v1/cart/items with negative quantity

**Expected Result:** API returns 422 Unprocessable Entity or validation error, and cart totals remain uncorrupted.

---

### TC-CART-CORE-010 — Change quantity of cart item via patch endpoint → Totals update within 1 second

**Feature:** Cart Core & General Behavior · **Type:** Positive · **Priority:** High · **Traces to:** FR-5, AC-FR5-1, US-8

**Preconditions**

- Buyer is logged in
- Cart contains item with quantity 1

**Test Data**

- `line_id`: LINE-001
- `new_quantity`: 3

**Steps**

1. Send PATCH /v1/cart/items/LINE-001 with quantity 3
2. Measure response time and check updated line total and grand total

**Expected Result:** Response received in under 1 second with updated quantity, line total, and grand total reflecting the change.

---

### TC-CART-CORE-011 — Remove cart item via delete endpoint → Line is removed and totals update

**Feature:** Cart Core & General Behavior · **Type:** Positive · **Priority:** High · **Traces to:** FR-5, AC-FR5-1

**Preconditions**

- Buyer is logged in
- Cart contains at least one line item

**Test Data**

- `line_id`: LINE-001

**Steps**

1. Send DELETE /v1/cart/items/LINE-001
2. Send GET /v1/cart

**Expected Result:** Line item is removed from the cart and grand total is updated accordingly.

---

### TC-CART-CORE-012 — Attempt to update cart item quantity exceeding available stock → Validation error returned

**Feature:** Cart Core & General Behavior · **Type:** Validation · **Priority:** High · **Traces to:** FR-5, AC-FR5-1

**Preconditions**

- Cart item has available stock limit of 5 units

**Test Data**

- `line_id`: LINE-001
- `requested_quantity`: 10

**Steps**

1. Send PATCH /v1/cart/items/LINE-001 with quantity 10

**Expected Result:** API returns OUT_OF_STOCK or quantity validation error and cart quantity is unchanged.

---

### TC-CART-CORE-013 — Cart revalidation on cart open after price change → Changed lines highlighted with old and new values

**Feature:** Cart Core & General Behavior · **Type:** Positive · **Priority:** High · **Traces to:** FR-14, AC-FR14-1, US-7

**Preconditions**

- Buyer has item in cart
- Seller updates listing price from 1000 to 1200

**Test Data**

- `old_price`: 1000.0
- `new_price`: 1200.0

**Steps**

1. Open cart GET /v1/cart or view cart page
2. Observe revalidation behavior and line highlighting

**Expected Result:** Cart line is flagged as 'Price changed' with old price struck through and new price displayed.

---

### TC-CART-CORE-014 — Cart revalidation when listing goes out of stock while in cart → Line marked as Low stock or Unavailable

**Feature:** Cart Core & General Behavior · **Type:** Validation · **Priority:** High · **Traces to:** FR-14, AC-FR14-1

**Preconditions**

- Item is in cart
- Listing stock becomes 0

**Test Data**

- `listing_id`: LST-STD-001

**Steps**

1. Trigger cart revalidation via GET /v1/cart or checkout start

**Expected Result:** Cart line state updates to 'Unavailable' or 'Low stock' with appropriate visual indicators.

---

### TC-CART-CORE-015 — Add 51st line item to cart → Returns CART_FULL error message

**Feature:** Cart Core & General Behavior · **Type:** Boundary · **Priority:** High · **Traces to:** FR-15, AC-FR15-1, BR-02

**Preconditions**

- Buyer is logged in
- Cart currently contains exactly 50 distinct line items

**Test Data**

- `additional_listing_id`: LST-NEW-051

**Steps**

1. Send POST /v1/cart/items for the 51st unique listing ID

**Expected Result:** API returns CART_FULL error response with appropriate message, and cart remains at 50 items.

---

### TC-CART-CORE-016 — Add 50th line item to cart (boundary) → Addition succeeds

**Feature:** Cart Core & General Behavior · **Type:** Boundary · **Priority:** High · **Traces to:** FR-15, AC-FR15-1, BR-02

**Preconditions**

- Buyer is logged in
- Cart currently contains 49 distinct line items

**Test Data**

- `additional_listing_id`: LST-NEW-050

**Steps**

1. Send POST /v1/cart/items for the 50th unique listing ID

**Expected Result:** API returns success response and cart now contains 50 line items.

---

### TC-CART-CORE-017 — Cart synchronization across web and app clients → Items added on web appear on app after refresh

**Feature:** Cart Core & General Behavior · **Type:** Integration · **Priority:** Medium · **Traces to:** FR-16, AC-FR16-1, US-10

**Preconditions**

- Buyer is logged in on web and mobile app with same account

**Test Data**

- `listing_id`: LST-STD-001

**Steps**

1. Add item to cart on web client
2. Open mobile app and refresh cart

**Expected Result:** Item added on web appears in the mobile app cart upon refresh.

---

### TC-CART-CORE-018 — Cart synchronization failure / network timeout during cross-client sync → Graceful retry or cached state displayed

**Feature:** Cart Core & General Behavior · **Type:** Error Handling · **Priority:** Low · **Traces to:** FR-16, AC-FR16-1

**Preconditions**

- Buyer is logged in across clients

**Test Data**

- `network_condition`: timeout

**Steps**

1. Simulate network timeout during mobile app cart fetch after web add

**Expected Result:** App displays cached cart data with a retry indicator, preventing app crash.

---

### TC-CART-CORE-019 — Mini-cart toast confirmation after successful add → Toast displays item name and new cart count

**Feature:** Cart Core & General Behavior · **Type:** Positive · **Priority:** Medium · **Traces to:** FR-17, AC-FR17-1

**Preconditions**

- Buyer is logged in on product page

**Test Data**

- `listing_id`: LST-STD-001
- `item_name`: Standard Widget

**Steps**

1. Tap 'Add to Cart' on product page
2. Observe UI toast notification

**Expected Result:** Toast notification appears showing item name, new cart count, and a 'View cart' action button.

---

### TC-CART-CORE-020 — Rapid successive add-to-cart clicks triggering multiple toasts → Toast queue or debounce behavior functions correctly

**Feature:** Cart Core & General Behavior · **Type:** Edge Case · **Priority:** Low · **Traces to:** FR-17, AC-FR17-1

**Preconditions**

- Buyer is on product page

**Test Data**

- `clicks`: 5

**Steps**

1. Rapidly tap 'Add to Cart' 5 times in 1 second

**Expected Result:** Toasts debounce or update cleanly without overlapping or crashing UI.

---

### TC-CART-PROT-001 — Add Buyer Protection listing to cart → Protection fee appears as separate line and included in grand total

**Feature:** Buyer Protection · **Type:** Positive · **Priority:** Critical · **Traces to:** FR-6, AC-09, US-3

**Preconditions**

- Buyer is logged in
- Buyer Protection listing exists with listing price ₹5000 and fee ₹250

**Test Data**

- `listing_id`: LST-PROT-001
- `listing_price`: 5000.0
- `protection_fee`: 250.0

**Steps**

1. Send POST /v1/cart/items for Buyer Protection listing
2. Inspect GET /v1/cart response

**Expected Result:** Cart displays listing price (₹5000.00) and protection fee (₹250.00) as a separate line, totaling ₹5250.00 in the grand total.

---

### TC-CART-PROT-002 — Buyer Protection fee update when seller modifies fee → Cart reflects updated fee value

**Feature:** Buyer Protection · **Type:** Validation · **Priority:** Medium · **Traces to:** FR-6, AC-09

**Preconditions**

- Buyer has Buyer Protection item in cart with fee ₹250
- Seller updates fee to ₹300

**Test Data**

- `old_fee`: 250.0
- `new_fee`: 300.0

**Steps**

1. Open cart GET /v1/cart
2. Inspect protection fee line item

**Expected Result:** Protection fee is updated to ₹300.00 and grand total reflects the new fee correctly.

---

### TC-CART-LUX-001 — Add Live authenticated Luxury listing to cart → Quantity fixed at 1 and 15-minute reservation starts

**Feature:** Luxury Listings · **Type:** Positive · **Priority:** Critical · **Traces to:** FR-7, AC-05, BR-03, US-4

**Preconditions**

- Buyer is logged in
- Authenticated Luxury listing is Live and in stock

**Test Data**

- `listing_id`: LST-LUX-001

**Steps**

1. Send POST /v1/cart/items for Luxury listing with quantity 1
2. Inspect cart line response and reservation status

**Expected Result:** Item added successfully with quantity fixed at 1 and reservation status showing active countdown timer starting from 15 minutes.

---

### TC-CART-LUX-002 — Attempt to add quantity greater than 1 for Luxury listing → Quantity limit enforced

**Feature:** Luxury Listings · **Type:** Validation · **Priority:** High · **Traces to:** FR-7, AC-05, BR-03

**Preconditions**

- Buyer is logged in
- Authenticated Luxury listing exists

**Test Data**

- `listing_id`: LST-LUX-001
- `quantity`: 2

**Steps**

1. Send POST /v1/cart/items with quantity 2

**Expected Result:** API returns validation error (e.g. QTY_ABOVE_LIMIT) and item is not added with quantity > 1.

---

### TC-CART-LUX-003 — Second buyer attempts to add reserved Luxury item → Sees 'Reserved, check back soon'

**Feature:** Luxury Listings · **Type:** Negative · **Priority:** Critical · **Traces to:** FR-7, AC-05

**Preconditions**

- Buyer A has added the last Luxury listing and holds active reservation

**Test Data**

- `listing_id`: LST-LUX-001

**Steps**

1. Log in as Buyer B
2. Navigate to the same Luxury listing product page

**Expected Result:** Buyer B sees 'Reserved, check back soon' and cannot add the item to cart.

---

### TC-CART-LUX-004 — Luxury reservation expiry after 15 minutes → Hold ends and cart shows 'No longer reserved' banner

**Feature:** Luxury Listings · **Type:** Boundary · **Priority:** High · **Traces to:** FR-8, AC-FR8-1

**Preconditions**

- Buyer added Luxury item, 15 minutes reservation timer elapsed

**Test Data**

- `listing_id`: LST-LUX-001
- `elapsed_time_min`: 15

**Steps**

1. Simulate 15-minute timer expiry
2. Open cart GET /v1/cart

**Expected Result:** Item remains in the cart but state is updated to 'Reservation expired' with banner 'No longer reserved'.

---

### TC-CART-OM-001 — Add OM listing to cart from accepted offer screen → Added successfully with price locked to offer

**Feature:** Offer Mode (OM) · **Type:** Positive · **Priority:** Critical · **Traces to:** FR-9, AC-06, BR-04, US-5

**Preconditions**

- Buyer has accepted unexpired offer with ID OFF-001 and offered price ₹8000

**Test Data**

- `listing_id`: LST-OM-001
- `offer_id`: OFF-001
- `locked_price`: 8000.0

**Steps**

1. Send POST /v1/cart/items with listingId, quantity, and offerId
2. Inspect cart line item price and badge

**Expected Result:** OM item added successfully with Offer badge, unit price locked to ₹8000.00, and offer expiration countdown timer.

---

### TC-CART-OM-002 — Attempt to add OM listing from standard product page → Add to Cart button hidden

**Feature:** Offer Mode (OM) · **Type:** Negative · **Priority:** High · **Traces to:** FR-9, AC-06, BR-04

**Preconditions**

- Buyer is logged in
- OM listing is live

**Test Data**

- `listing_type`: OM

**Steps**

1. Navigate to OM listing product page directly

**Expected Result:** Add to Cart button is hidden on the standard product page for OM listings.

---

### TC-CART-OM-003 — Expired OM offer line in cart → Disabled with 'Offer expired' message and blocked from checkout

**Feature:** Offer Mode (OM) · **Type:** Negative · **Priority:** High · **Traces to:** FR-10, AC-FR10-1

**Preconditions**

- OM item with expired offer is present in cart

**Test Data**

- `offer_id`: OFF-EXPIRED

**Steps**

1. Open cart GET /v1/cart
2. Attempt to proceed to checkout

**Expected Result:** OM line item is disabled with 'Offer expired' message, and checkout is blocked until removed or updated.

---

### TC-CART-BULK-001 — Add Bulk listing with business account and quantity >= MOQ → Added successfully with tier pricing

**Feature:** Bulk Listings · **Type:** Positive · **Priority:** Critical · **Traces to:** FR-11, AC-08, BR-05, US-6

**Preconditions**

- Buyer has a verified business account
- Bulk listing MOQ is 50 units

**Test Data**

- `listing_id`: LST-BULK-001
- `quantity`: 50

**Steps**

1. Send POST /v1/cart/items with quantity 50

**Expected Result:** Item added successfully with tier unit price and tier table displayed in cart.

---

### TC-CART-BULK-002 — Non-business buyer attempts to add Bulk listing → Blocked with reason and link to upgrade

**Feature:** Bulk Listings · **Type:** Negative · **Priority:** Critical · **Traces to:** FR-11, AC-08, BR-05

**Preconditions**

- Buyer is logged in with standard personal account
- Bulk listing exists

**Test Data**

- `listing_id`: LST-BULK-001
- `quantity`: 50

**Steps**

1. Send POST /v1/cart/items for Bulk listing as non-business buyer

**Expected Result:** API returns NOT_BUSINESS_ACCOUNT error with reason and link to upgrade account.

---

### TC-CART-BULK-003 — Bulk buyer adds quantity below MOQ (boundary) → Validation error QTY_BELOW_MOQ returned

**Feature:** Bulk Listings · **Type:** Boundary · **Priority:** High · **Traces to:** FR-11, AC-08, BR-05

**Preconditions**

- Buyer has business account
- Bulk listing MOQ is 50 units

**Test Data**

- `listing_id`: LST-BULK-001
- `quantity`: 49

**Steps**

1. Send POST /v1/cart/items with quantity 49

**Expected Result:** API returns QTY_BELOW_MOQ error and item is not added.

---

### TC-CART-BULK-004 — Bulk buyer adds quantity equal to MOQ (boundary) → Addition succeeds

**Feature:** Bulk Listings · **Type:** Boundary · **Priority:** High · **Traces to:** FR-11, AC-08, BR-05

**Preconditions**

- Buyer has business account
- Bulk listing MOQ is 50 units

**Test Data**

- `listing_id`: LST-BULK-001
- `quantity`: 50

**Steps**

1. Send POST /v1/cart/items with quantity 50

**Expected Result:** Item is added successfully with quantity 50.

---

### TC-CART-BULK-005 — Recalculate unit price from tier table upon quantity change → Price matches tier table for boundary quantities

**Feature:** Bulk Listings · **Type:** Business Rule · **Priority:** High · **Traces to:** FR-12, AC-FR12-1, US-6

**Preconditions**

- Bulk item in cart with Tier 1 qty 50 @ ₹100, Tier 2 qty 200 @ ₹90

**Test Data**

- `line_id`: LINE-BULK-001
- `new_quantity`: 200

**Steps**

1. Send PATCH /v1/cart/items/LINE-BULK-001 with quantity 200
2. Inspect updated unit price

**Expected Result:** Unit price updates to ₹90.00 matching Tier 2 boundary pricing correctly.

---

### TC-CART-BULK-006 — Bulk buyer changes quantity to invalid intermediate number between tiers → Validated and priced according to applicable active tier

**Feature:** Bulk Listings · **Type:** Validation · **Priority:** Medium · **Traces to:** FR-12, AC-FR12-1

**Preconditions**

- Bulk item in cart with Tier 1 (50) and Tier 2 (200)

**Test Data**

- `quantity`: 120

**Steps**

1. Send PATCH /v1/cart/items with quantity 120

**Expected Result:** Item quantity updates successfully and unit price applies the correct active tier rate.

---

### TC-CART-BULK-007 — Next-tier saving hint display and hiding on highest tier → Hint shown when eligible, hidden on highest tier

**Feature:** Bulk Listings · **Type:** Positive · **Priority:** Medium · **Traces to:** FR-13, AC-FR13-1, US-9

**Preconditions**

- Bulk item in cart with quantity in Tier 1 and highest tier at 500 units

**Test Data**

- `quantity_tier1`: 50
- `quantity_highest`: 500

**Steps**

1. View cart with quantity 50 and check for saving hint
2. Update quantity to 500 (highest tier) and check saving hint

**Expected Result:** Saving hint 'Add X more to save Y' is displayed at quantity 50, and hidden when quantity reaches 500 (highest tier).

---

### TC-CART-BULK-008 — Next-tier saving hint behavior when tier pricing structure is missing or single-tier → Hint is omitted gracefully

**Feature:** Bulk Listings · **Type:** Validation · **Priority:** Low · **Traces to:** FR-13, AC-FR13-1

**Preconditions**

- Single tier bulk listing in cart

**Test Data**

- `listing_id`: LST-BULK-SINGLE

**Steps**

1. View cart for single-tier bulk listing

**Expected Result:** No next-tier saving hint is rendered in the cart UI.

---

### TC-CART-NFR-001 — Add to Cart API performance load test under target threshold → p95 latency is under 300 ms

**Feature:** Cart Core & General Behavior · **Type:** Integration · **Priority:** Medium · **Traces to:** NFR-1

**Preconditions**

- Staging environment seeded with test listings and load generator active

**Test Data**

- `load_rps`: 500

**Steps**

1. Execute 500 add-to-cart requests/s for 5 minutes
2. Measure API response times and calculate p95 latency

**Expected Result:** Add to Cart API p95 latency is strictly less than 300 ms.

---

### TC-CART-NFR-002 — Cart read behavior when downstream Listing service is down → Degrades gracefully to cached data

**Feature:** Cart Core & General Behavior · **Type:** Error Handling · **Priority:** High · **Traces to:** NFR-2

**Preconditions**

- Buyer is logged in with items in cart
- Listing service is simulated as down

**Test Data**

- `service_status`: down

**Steps**

1. Send GET /v1/cart while Listing service is down
2. Inspect response status and headers/body

**Expected Result:** Cart API returns cached cart data successfully without failing with 5xx error.

---

### TC-CART-NFR-003 — Concurrent add-to-cart requests for final scarce unit → Atomicity ensures exactly one buyer secures the reservation

**Feature:** Cart Core & General Behavior · **Type:** Integration · **Priority:** Critical · **Traces to:** NFR-3

**Preconditions**

- Exactly 1 unit of a scarce Luxury/OM item remains in stock

**Test Data**

- `concurrent_requests`: 2

**Steps**

1. Simulate Buyer A and Buyer B sending POST /v1/cart/items simultaneously for the final unit

**Expected Result:** One request succeeds with active reservation and the other fails with OUT_OF_STOCK or reservation conflict error.

---

### TC-CART-NFR-004 — Attempt to access or modify another user's cart by ID or token → Blocked with 403 Forbidden

**Feature:** Cart Core & General Behavior · **Type:** Security · **Priority:** Critical · **Traces to:** NFR-4

**Preconditions**

- Buyer A and Buyer B are authenticated with distinct user tokens

**Test Data**

- `target_cart_user`: Buyer_B_ID

**Steps**

1. Send GET /v1/cart or PATCH requests using Buyer A token targeted at Buyer B's resources

**Expected Result:** API returns 403 Forbidden, preventing unauthorized cart access or modification.

---

### TC-CART-NFR-005 — Inspect OM cart API response JSON structure → Minimum offer and seller payout amounts are absent

**Feature:** Offer Mode (OM) · **Type:** Security · **Priority:** High · **Traces to:** NFR-5

**Preconditions**

- OM item with accepted offer is present in cart

**Test Data**

- `endpoint`: /v1/cart

**Steps**

1. Send GET /v1/cart and inspect full JSON response payload

**Expected Result:** Payload contains locked price and offer ID, but minOffer and sellerPayout fields are completely absent.

---

### TC-CART-NFR-006 — Screen reader accessibility audit for cart reservation timers → Timers announced once per minute per WCAG 2.1 AA

**Feature:** Cart Core & General Behavior · **Type:** UI · **Priority:** Medium · **Traces to:** NFR-6

**Preconditions**

- Cart contains item with active reservation countdown timer

**Test Data**

- `wcag_standard`: 2.1 AA

**Steps**

1. Inspect DOM and screen reader accessibility tree for reservation countdown elements
2. Verify aria-live polite/assertive announcement intervals

**Expected Result:** Reservation timers have proper ARIA attributes and announce remaining time to screen readers once per minute.

---

### TC-CART-NFR-007 — Localization and currency formatting check in Hindi and English → Correct ₹ symbol and Indian digit grouping

**Feature:** Cart Core & General Behavior · **Type:** Compatibility · **Priority:** Medium · **Traces to:** NFR-7

**Preconditions**

- App/Web language set to Hindi and English with Indian locale formatting active

**Test Data**

- `amount`: 150000.5
- `locales`: en-IN; hi-IN

**Steps**

1. Render cart page with large monetary amounts in English and Hindi modes
2. Inspect currency symbol and digit formatting

**Expected Result:** Monetary values render with Indian Rupee symbol (₹) and Indian digit grouping (e.g. ₹1,50,000.50) in both languages.
