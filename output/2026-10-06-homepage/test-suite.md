# Homepage

Generated: 2026-10-06 · Input types: FEATURE_DESCRIPTION · Test cases: 20

## Inputs analysed

| Source | Detected type | Confidence | Evidence |
|---|---|---|---|
| resources/examples/homepage.md | FEATURE_DESCRIPTION | high | Narrative prose describing one page ('The homepage is the landing page...'); No story format, requirement IDs or acceptance-criteria list; Describes layout and behaviour of header, carousel, product grid, search and footer |

## QA Summary

| Metric | Value |
|---|---|
| Requirements identified | 9 (9 covered) |
| Acceptance criteria identified | 8 (8 covered) |
| Business rules identified | 4 (4 covered) |
| Total test cases | 20 |
| Positive | 8 |
| Negative (incl. error handling) | 0 |
| Boundary | 5 |
| Edge cases | 2 |
| Validation | 1 |
| Other types | Business Rule: 1, Compatibility: 1, UI: 2 |
| By priority | Critical: 1, High: 7, Medium: 7, Low: 5 |
| Assumption-based cases | 2 |
| Coverage gaps | 7 |

All 9 requirements, 8 acceptance criteria and 4 business rules are covered, including the 5-banner limit, the 2-character search minimum and the 480px breakpoint. Search rejection behaviour (TC-HOME-015/016) is based on assumption A-1. Remaining risks are banner selection with more than 5 promotions and a partially filled featured grid.

## Clarifications & Assumptions

| ID | Question | Severity | Status | Answer |
|---|---|---|---|---|
| Q-1 | What happens when a 1-character search is submitted: nothing, an inline message, or a disabled search icon? | non_blocking | assumed |  |
| Q-2 | With more than 5 active promotions, which 5 banners are shown? | non_blocking | out_of_scope |  |
| Q-3 | What does the grid show when fewer than 8 products are featured? | non_blocking | out_of_scope |  |

| ID | Assumption | Related |
|---|---|---|
| A-1 | A search with fewer than 2 characters is not submitted: the URL does not change to /search and the user stays on the homepage. | BR-004 |

## Coverage Gaps

| Ref | Gap | Reason |
|---|---|---|
| — | Which 5 banners are shown when more than 5 promotions are active | Selection rule not stated (Q-2) |
| — | Grid behaviour with fewer than 8 featured products | Not stated (Q-3) |
| — | Page performance and accessibility | No targets in the description |
| REQ-001 | No negative case for serving '/' | Display requirement; guest and logged-in states are both covered by TC-HOME-001/002 |
| REQ-002 | No negative case for the logo link | Navigation-only requirement with no failure behaviour described |
| REQ-004 | No separate negative case for the greeting | TC-HOME-001 asserts the greeting is absent for guests; TC-HOME-002 asserts 'Sign in' is absent when logged in |
| REQ-008 | No negative case for footer links | Link targets are not specified; only presence and page title are tested |

## Traceability Matrix

| Kind | ID | Text | Test cases |
|---|---|---|---|
| REQ | REQ-001 | Homepage is served at '/' for guests and logged-in customers | TC-HOME-001 |
| REQ | REQ-002 | Header shows the ShopEase logo, which always returns to the homepage | TC-HOME-003 |
| REQ | REQ-003 | Header cart icon shows the number of items in the cart | TC-HOME-004, TC-HOME-020 |
| REQ | REQ-004 | Header shows 'Sign in' for guests and 'Hi, <first name>' for logged-in customers | TC-HOME-001, TC-HOME-002 |
| REQ | REQ-005 | Hero banner carousel shows promotional banners | TC-HOME-005, TC-HOME-006, TC-HOME-007, TC-HOME-008, TC-HOME-009, TC-HOME-010 |
| REQ | REQ-006 | Featured Products grid shows product cards | TC-HOME-011, TC-HOME-012 |
| REQ | REQ-007 | Search bar opens the results page | TC-HOME-013, TC-HOME-014, TC-HOME-015, TC-HOME-016 |
| REQ | REQ-008 | Footer contains About Us, Contact, Privacy Policy and Terms of Service links | TC-HOME-017 |
| REQ | REQ-009 | Page is usable on mobile (<= 480px wide) | TC-HOME-018, TC-HOME-019 |
| AC | AC-005.1 | Carousel auto-rotates every 6 seconds | TC-HOME-005 |
| AC | AC-005.2 | Left/right arrows move between banners | TC-HOME-006 |
| AC | AC-005.3 | Each banner links to its promotion page | TC-HOME-007 |
| AC | AC-006.1 | Each product card shows image, name, price and an 'Add to cart' button | TC-HOME-011 |
| AC | AC-006.2 | Out-of-stock products show an 'Out of stock' label instead of the 'Add to cart' button | TC-HOME-012 |
| AC | AC-007.1 | Pressing Enter opens /search?q=<term> | TC-HOME-013 |
| AC | AC-007.2 | Clicking the search icon opens /search?q=<term> | TC-HOME-014 |
| AC | AC-009.1 | At <= 480px the featured grid shows 2 products per row; otherwise 4 per row | TC-HOME-018, TC-HOME-019 |
| BR | BR-001 | The carousel shows at most 5 banners | TC-HOME-008, TC-HOME-009 |
| BR | BR-002 | If there are no active promotions the carousel is hidden | TC-HOME-010 |
| BR | BR-003 | The Featured Products grid shows 8 products | TC-HOME-011 |
| BR | BR-004 | Search requires at least 2 characters | TC-HOME-013, TC-HOME-015, TC-HOME-016 |

## Test Case Index

| ID | Feature | Scenario | Type | Priority | Traces to |
|---|---|---|---|---|---|
| TC-HOME-001 | Homepage | Guest opens the homepage and sees the 'Sign in' link | Positive | Critical | REQ-001, REQ-004 |
| TC-HOME-002 | Homepage | Logged-in customer sees 'Hi, <first name>' instead of 'Sign in' | Positive | High | REQ-004 |
| TC-HOME-003 | Homepage | Logo returns to the homepage from another page | Positive | Medium | REQ-002 |
| TC-HOME-004 | Homepage | Cart icon shows the number of items in the cart | Positive | High | REQ-003 |
| TC-HOME-005 | Homepage | Carousel rotates to the next banner every 6 seconds | UI | Medium | AC-005.1 |
| TC-HOME-006 | Homepage | Right and left arrows move between banners | UI | Medium | AC-005.2 |
| TC-HOME-007 | Homepage | Clicking a banner opens its promotion page | Positive | High | AC-005.3 |
| TC-HOME-008 | Homepage | Carousel shows at most 5 banners when 6 promotions are active | Boundary | Medium | BR-001 |
| TC-HOME-009 | Homepage | Carousel shows all 5 banners when exactly 5 promotions are active | Boundary | Low | BR-001 |
| TC-HOME-010 | Homepage | Carousel is hidden when there are no active promotions | Edge Case | Medium | BR-002 |
| TC-HOME-011 | Homepage | Featured Products grid shows 8 complete product cards | Positive | High | AC-006.1, BR-003 |
| TC-HOME-012 | Homepage | Out-of-stock featured product shows 'Out of stock' instead of 'Add to cart' | Business Rule | High | AC-006.2 |
| TC-HOME-013 | Homepage | Search with exactly 2 characters using Enter opens the results page | Boundary | High | AC-007.1, BR-004 |
| TC-HOME-014 | Homepage | Search using the search icon opens the results page | Positive | High | AC-007.2 |
| TC-HOME-015 | Homepage | Search with 1 character is not submitted | Boundary | Medium | BR-004 |
| TC-HOME-016 | Homepage | Empty search is not submitted | Validation | Low | BR-004 |
| TC-HOME-017 | Homepage | Footer links open About Us, Contact, Privacy Policy and Terms of Service | Positive | Low | REQ-008 |
| TC-HOME-018 | Homepage | Featured grid shows 2 products per row at 480px | Compatibility | Medium | AC-009.1 |
| TC-HOME-019 | Homepage | Featured grid shows 4 products per row at 481px | Boundary | Low | AC-009.1 |
| TC-HOME-020 | Homepage | Cart icon with an empty cart shows a count of 0 or no count badge | Edge Case | Low | REQ-003 |

## Test Cases

### TC-HOME-001 — Guest opens the homepage and sees the 'Sign in' link

**Feature:** Homepage · **Type:** Positive · **Priority:** Critical · **Traces to:** REQ-001, REQ-004

**Preconditions**

- User is not logged in (fresh browser session)

**Test Data**

- `url`: /

**Steps**

1. Open the store root URL '/'

**Expected Result:** Homepage loads with header (logo, search bar, cart icon, 'Sign in' link), hero carousel, Featured Products grid and footer; no 'Hi, ' greeting is shown

---

### TC-HOME-002 — Logged-in customer sees 'Hi, <first name>' instead of 'Sign in'

**Feature:** Homepage · **Type:** Positive · **Priority:** High · **Traces to:** REQ-004

**Preconditions**

- Customer account with first name 'Asha' exists
- Customer is logged in

**Test Data**

- `first_name`: Asha

**Steps**

1. Open '/'
2. Look at the right side of the header

**Expected Result:** Header shows 'Hi, Asha' and the 'Sign in' link is not displayed

---

### TC-HOME-003 — Logo returns to the homepage from another page

**Feature:** Homepage · **Type:** Positive · **Priority:** Medium · **Traces to:** REQ-002

**Preconditions**

- User is on a page other than the homepage, e.g. /search?q=shoes

**Test Data**

- `start_url`: /search?q=shoes

**Steps**

1. Click the ShopEase logo in the header

**Expected Result:** Browser navigates to '/' and the homepage content is displayed

---

### TC-HOME-004 — Cart icon shows the number of items in the cart

**Feature:** Homepage · **Type:** Positive · **Priority:** High · **Traces to:** REQ-003

**Preconditions**

- Cart contains 3 items

**Test Data**

- `cart_items`: 3

**Steps**

1. Open '/'
2. Look at the cart icon in the header

**Expected Result:** Cart icon shows the count 3

---

### TC-HOME-005 — Carousel rotates to the next banner every 6 seconds

**Feature:** Homepage · **Type:** UI · **Priority:** Medium · **Traces to:** AC-005.1

**Preconditions**

- 3 active promotions exist (banners B1, B2, B3)

**Test Data**

- `banners`: B1; B2; B3
- `interval_seconds`: 6

**Steps**

1. Open '/' and note the visible banner (B1)
2. Wait 6 seconds without interacting
3. Wait another 6 seconds

**Expected Result:** B2 becomes visible about 6 seconds after load and B3 about 12 seconds after load; no banner changes earlier than 6 seconds

---

### TC-HOME-006 — Right and left arrows move between banners

**Feature:** Homepage · **Type:** UI · **Priority:** Medium · **Traces to:** AC-005.2

**Preconditions**

- 3 active promotions exist (banners B1, B2, B3)

**Test Data**

- `banners`: B1; B2; B3

**Steps**

1. Open '/' while B1 is visible
2. Click the right arrow
3. Click the left arrow

**Expected Result:** After the right arrow B2 is shown; after the left arrow B1 is shown again

---

### TC-HOME-007 — Clicking a banner opens its promotion page

**Feature:** Homepage · **Type:** Positive · **Priority:** High · **Traces to:** AC-005.3

**Preconditions**

- Active promotion 'Diwali Sale' with promotion page /promo/diwali-sale

**Test Data**

- `banner`: Diwali Sale
- `target`: /promo/diwali-sale

**Steps**

1. Open '/'
2. Navigate the carousel to the 'Diwali Sale' banner
3. Click the banner

**Expected Result:** Browser navigates to /promo/diwali-sale, the configured page of that promotion

---

### TC-HOME-008 — Carousel shows at most 5 banners when 6 promotions are active

**Feature:** Homepage · **Type:** Boundary · **Priority:** Medium · **Traces to:** BR-001

**Preconditions**

- 6 active promotions exist

**Test Data**

- `active_promotions`: 6
- `max_banners`: 5

**Steps**

1. Open '/'
2. Click the right arrow repeatedly, counting distinct banners until the first banner reappears or the arrow stops advancing

**Expected Result:** Exactly 5 distinct banners are reachable in the carousel

---

### TC-HOME-009 — Carousel shows all 5 banners when exactly 5 promotions are active

**Feature:** Homepage · **Type:** Boundary · **Priority:** Low · **Traces to:** BR-001

**Preconditions**

- Exactly 5 active promotions exist

**Test Data**

- `active_promotions`: 5

**Steps**

1. Open '/'
2. Click the right arrow, counting distinct banners until the first banner reappears or the arrow stops advancing

**Expected Result:** All 5 promotion banners are reachable, none missing

---

### TC-HOME-010 — Carousel is hidden when there are no active promotions

**Feature:** Homepage · **Type:** Edge Case · **Priority:** Medium · **Traces to:** BR-002

**Preconditions**

- All promotions are inactive or expired

**Test Data**

- `active_promotions`: 0

**Steps**

1. Open '/'

**Expected Result:** No carousel area, arrows or empty placeholder are displayed; the Featured Products grid follows the header directly

---

### TC-HOME-011 — Featured Products grid shows 8 complete product cards

**Feature:** Homepage · **Type:** Positive · **Priority:** High · **Traces to:** AC-006.1, BR-003

**Preconditions**

- At least 8 in-stock products are marked as featured
- Desktop viewport 1280px wide

**Test Data**

- `featured_products`: 8
- `viewport_px`: 1280

**Steps**

1. Open '/'
2. Scroll to the 'Featured Products' section
3. Inspect each product card

**Expected Result:** Exactly 8 cards are shown in rows of 4; each card shows the product image, name, price and an 'Add to cart' button

---

### TC-HOME-012 — Out-of-stock featured product shows 'Out of stock' instead of 'Add to cart'

**Feature:** Homepage · **Type:** Business Rule · **Priority:** High · **Traces to:** AC-006.2

**Preconditions**

- Featured product 'Blue Mug' has stock 0

**Test Data**

- `product`: Blue Mug
- `stock`: 0

**Steps**

1. Open '/'
2. Find the 'Blue Mug' card in the Featured Products grid

**Expected Result:** The card shows an 'Out of stock' label and no 'Add to cart' button; image, name and price are still shown

---

### TC-HOME-013 — Search with exactly 2 characters using Enter opens the results page

**Feature:** Homepage · **Type:** Boundary · **Priority:** High · **Traces to:** AC-007.1, BR-004

**Preconditions**

- User is on '/'

**Test Data**

- `term`: tv

**Steps**

1. Type 'tv' in the search bar
2. Press Enter

**Expected Result:** Browser navigates to /search?q=tv

---

### TC-HOME-014 — Search using the search icon opens the results page

**Feature:** Homepage · **Type:** Positive · **Priority:** High · **Traces to:** AC-007.2

**Preconditions**

- User is on '/'

**Test Data**

- `term`: running shoes

**Steps**

1. Type 'running shoes' in the search bar
2. Click the search icon

**Expected Result:** Browser navigates to /search?q=running%20shoes (or running+shoes) and the term is preserved

---

### TC-HOME-015 — Search with 1 character is not submitted

**Feature:** Homepage · **Type:** Boundary · **Priority:** Medium · **Traces to:** BR-004

⚠️ Assumption-based (A-1)

**Preconditions**

- User is on '/'

**Test Data**

- `term`: t

**Steps**

1. Type 't' in the search bar
2. Press Enter
3. Click the search icon

**Expected Result:** The URL stays '/' and the results page is not opened after either action

---

### TC-HOME-016 — Empty search is not submitted

**Feature:** Homepage · **Type:** Validation · **Priority:** Low · **Traces to:** BR-004

⚠️ Assumption-based (A-1)

**Preconditions**

- User is on '/'

**Test Data**

- `term`: 

**Steps**

1. Leave the search bar empty
2. Click the search icon

**Expected Result:** The URL stays '/' and the results page is not opened

---

### TC-HOME-017 — Footer links open About Us, Contact, Privacy Policy and Terms of Service

**Feature:** Homepage · **Type:** Positive · **Priority:** Low · **Traces to:** REQ-008

**Preconditions**

- User is on '/'

**Test Data**

- `links`: About Us; Contact; Privacy Policy; Terms of Service

**Steps**

1. Scroll to the footer
2. Click each link in test data, returning to '/' after each

**Expected Result:** All 4 links are present and each opens the page whose title matches the link text

---

### TC-HOME-018 — Featured grid shows 2 products per row at 480px

**Feature:** Homepage · **Type:** Compatibility · **Priority:** Medium · **Traces to:** AC-009.1

**Preconditions**

- At least 8 featured products

**Test Data**

- `viewport_px`: 480

**Steps**

1. Set the browser viewport width to 480px
2. Open '/'
3. Scroll to the Featured Products grid

**Expected Result:** Products are laid out 2 per row (4 rows of 2) with no horizontal scrolling

---

### TC-HOME-019 — Featured grid shows 4 products per row at 481px

**Feature:** Homepage · **Type:** Boundary · **Priority:** Low · **Traces to:** AC-009.1

**Preconditions**

- At least 8 featured products

**Test Data**

- `viewport_px`: 481

**Steps**

1. Set the browser viewport width to 481px
2. Open '/'
3. Scroll to the Featured Products grid

**Expected Result:** Products are laid out 4 per row (2 rows of 4)

---

### TC-HOME-020 — Cart icon with an empty cart shows a count of 0 or no count badge

**Feature:** Homepage · **Type:** Edge Case · **Priority:** Low · **Traces to:** REQ-003

**Preconditions**

- Cart is empty

**Test Data**

- `cart_items`: 0

**Steps**

1. Open '/'
2. Look at the cart icon in the header

**Expected Result:** Cart icon does not show a non-zero number (shows 0 or no badge) and no stale count from a previous session is displayed
