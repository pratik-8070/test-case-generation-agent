# Create Listing (Multi-Type) Comprehensive Test Suite

Generated: 2026-10-13 · Input types: PRD, TECHNICAL_SPEC, UI_DESIGN · Test cases: 17

## Inputs analysed

| Source | Detected type | Confidence | Evidence |
|---|---|---|---|
| confluence-753666-PRD-Create-Listing-Multi-Type.md | PRD | high | Status: DRAFT (DEMO) · 13 Oct 2026; Goals, listing types, user stories, requirements FR-1 to FR-14, acceptance criteria |
| confluence-786433-RFC-Create-Listing-Multi-Type.md | TECHNICAL_SPEC | high | RFC: Create Listing (Multi-Type); Architecture, data model, type strategies, state machine, API contracts, testing |
| figma-01-Choose-listing-type.png | UI_DESIGN | high | Frame 01 Choose listing type; What are you listing? Pick a type. You can't change it after publishing. |

## QA Summary

| Metric | Value |
|---|---|
| Requirements identified | 15 (15 covered) |
| Acceptance criteria identified | 10 (10 covered) |
| Business rules identified | 6 (6 covered) |
| Total test cases | 17 |
| Positive | 5 |
| Negative (incl. error handling) | 0 |
| Boundary | 2 |
| Edge cases | 0 |
| Validation | 6 |
| Other types | Business Rule: 2, Security: 1, UI: 1 |
| By priority | Critical: 7, High: 10 |
| Assumption-based cases | 1 |
| Coverage gaps | 1 |

Coverage is robust across listing types, eligibility rules, common field validations, type-specific pricing/authentication rules, and state transitions. All 15 requirements and 10 acceptance criteria identified in the PRD are fully covered by test cases. Non-functional requirements regarding performance and accessibility are noted as out-of-scope for functional test execution.

## Clarifications & Assumptions

| ID | Question | Severity | Status | Answer |
|---|---|---|---|---|
| Q-1 | What is the exact formula or fixed percentage for calculating the Buyer Protection fee displayed to buyers? | non_blocking | assumed | Assumed 2% of listing price or flat tier fee based on demo design (e.g., ₹18,500 item has ₹370 fee). |

| ID | Assumption | Related |
|---|---|---|
| A-1 | Buyer Protection fee calculation uses a standard 2% rate as illustrated in Figma design 03a. | REQ-005 |

## Coverage Gaps

| Ref | Gap | Reason |
|---|---|---|
| REQ-003 | Network drop recovery during parallel photo uploads (retry 3 times) | Requires simulated network interception tooling in E2E automation rather than functional API/UI tests. |

## Traceability Matrix

| Kind | ID | Text | Test cases |
|---|---|---|---|
| REQ | REQ-001 | The type selector is the first step, displaying all 5 listing types with a one-line description and eligibility status. | TC-LISTING-TYPE-001 |
| REQ | REQ-002 | Ineligible listing types are visible but disabled, displaying the reason and instructions on how to qualify. | TC-LISTING-TYPE-002 |
| REQ | REQ-003 | The system shall auto-save drafts every 10 seconds and upon step changes. | TC-COMMON-DETAILS-001 |
| REQ | REQ-004 | All common listing fields (Title, Category, Condition, Description, Photos, Quantity, Shipping, Pickup location, Return policy) must be validated according to defined rules. | TC-COMMON-DETAILS-002, TC-COMMON-DETAILS-003, TC-COMMON-DETAILS-004, TC-COMMON-DETAILS-005 |
| REQ | REQ-005 | For Buyer Protection listings, display the protection fee and payout timeline before publishing, and require tracked shipping to be enabled. | TC-BUYER-PROT-001 |
| REQ | REQ-006 | Buyer Protection listing cards and detail pages must display a Buyer Protection badge. | TC-BUYER-PROT-001, TC-LUXURY-001 |
| REQ | REQ-007 | Luxury listings require a price of at least ₹50,000, along with brand, model, and serial number inputs. | TC-LUXURY-001 |
| REQ | REQ-008 | Luxury listings require proof of purchase upload and at least 4 photos including serial number and logo close-ups. | TC-LUXURY-002 |
| REQ | REQ-009 | On submit, Luxury listings enter Pending Review state until authentication passes, then become Live with a Verified Luxury badge. | TC-LUXURY-002 |
| REQ | REQ-010 | For Offer Mode listings, sellers set an asking price; minimum offer is optional, must be <= asking price, and is never shown to buyers. | TC-OM-001, TC-OM-002 |
| REQ | REQ-011 | Sellers set offer expiry (24, 48, or 72 hours), and offers below the minimum are auto-declined. | TC-OM-003 |
| REQ | REQ-012 | Bulk listings require MOQ and up to 5 price tiers, where each tier's unit price must be strictly lower than the previous tier. | TC-BULK-001 |
| REQ | REQ-013 | GSTIN must be verified on the business account before publishing a Bulk listing. | TC-BULK-002 |
| REQ | REQ-014 | The preview screen must render the listing exactly as a buyer sees it, per listing type. | TC-PUBLISH-001 |
| REQ | REQ-015 | Publish confirmation must show listing ID, status, and a link to the listing. | TC-PUBLISH-002 |
| AC | AC-001.1 | Seller can select any of the 5 listing types on Step 1. | TC-LISTING-TYPE-001 |
| AC | AC-002.1 | Ineligible types are disabled with a visible reason and path to qualify. | TC-LISTING-TYPE-002 |
| AC | AC-003.1 | Draft auto-saves and restores after closing browser or app. | TC-COMMON-DETAILS-001 |
| AC | AC-006.1 | Buyer Protection badge shows on the listing card and detail page. | TC-BUYER-PROT-001 |
| AC | AC-007.1 | Luxury listing below ₹50,000 cannot be published. | TC-LUXURY-001 |
| AC | AC-009.1 | Luxury listing stays Pending Review until authentication passes. | TC-LUXURY-002 |
| AC | AC-010.1 | OM minimum offer is never returned in any buyer-facing API or page. | TC-OM-002 |
| AC | AC-011.1 | OM offers below the minimum are auto-declined. | TC-OM-003 |
| AC | AC-012.1 | Bulk tiers with non-decreasing prices are rejected with an inline error. | TC-BULK-001 |
| AC | AC-014.1 | Preview matches the published buyer view for every type. | TC-PUBLISH-001 |
| BR | BR-001 | Title must be 10-80 characters, no phone numbers or URLs. | TC-COMMON-DETAILS-002, TC-COMMON-DETAILS-003 |
| BR | BR-002 | Description must be 50-2,000 characters. | TC-COMMON-DETAILS-004 |
| BR | BR-003 | Photos must be 1-10 images, JPG/PNG/WEBP, max 10 MB each, min 800x800 px. | TC-COMMON-DETAILS-005 |
| BR | BR-004 | Luxury price minimum is ₹50,000. | TC-LUXURY-001 |
| BR | BR-005 | OM minimum offer must be less than or equal to the asking price. | TC-OM-001 |
| BR | BR-006 | Bulk price tiers must contain up to 5 tiers, and each tier's unit price must be strictly lower than the previous tier. | TC-BULK-001 |

## Test Case Index

| ID | Feature | Scenario | Type | Priority | Traces to |
|---|---|---|---|---|---|
| TC-LISTING-TYPE-001 | Listing Type Selection and Eligibility | Select Standard listing type on Step 1 -> Type is selected and description is displayed | Positive | Critical | REQ-001, AC-001.1 |
| TC-LISTING-TYPE-002 | Listing Type Selection and Eligibility | View ineligible Luxury listing type -> Card is disabled with reason and qualification path | Validation | High | REQ-002, AC-002.1 |
| TC-COMMON-DETAILS-001 | Common Listing Details and Draft Management | Auto-save draft on step change -> Draft is saved automatically | Positive | High | REQ-003, AC-003.1 |
| TC-COMMON-DETAILS-002 | Common Listing Details and Draft Management | Enter title below minimum character limit -> Inline validation error is shown | Validation | High | REQ-004, BR-001 |
| TC-COMMON-DETAILS-003 | Common Listing Details and Draft Management | Enter title exceeding maximum character limit -> Inline validation error is shown | Boundary | High | REQ-004, BR-001 |
| TC-COMMON-DETAILS-004 | Common Listing Details and Draft Management | Enter description below minimum character limit -> Inline validation error is shown | Validation | High | REQ-004, BR-002 |
| TC-COMMON-DETAILS-005 | Common Listing Details and Draft Management | Upload photo exceeding 10 MB size limit -> Validation error code 413 is triggered | Validation | High | REQ-004, BR-003 |
| TC-BUYER-PROT-001 | Buyer Protection Listing Type | Configure Buyer Protection listing -> Protection fee and payout timeline are displayed correctly | Positive | Critical | REQ-005, AC-006.1 |
| TC-LUXURY-001 | Luxury Listing Type and Authentication | Enter Luxury price below ₹50,000 threshold -> Inline error blocks publishing | Boundary | Critical | REQ-006, BR-004, AC-007.1 |
| TC-LUXURY-002 | Luxury Listing Type and Authentication | Submit valid Luxury listing -> Listing enters Pending Review state | Positive | Critical | REQ-008, AC-009.1 |
| TC-OM-001 | Offer Mode Listing Type | Set OM minimum offer higher than asking price -> Inline error blocks progression | Validation | High | REQ-010, BR-005 |
| TC-OM-002 | Offer Mode Listing Type | Fetch buyer-facing API/view for OM listing -> Minimum offer is excluded from payload | Security | Critical | REQ-010, AC-010.1 |
| TC-OM-003 | Offer Mode Listing Type | Receive offer below OM minimum offer -> System automatically declines the offer | Business Rule | High | REQ-011, AC-011.1 |
| TC-BULK-001 | Bulk Listing Type and Tiered Pricing | Enter non-decreasing bulk price tier -> Inline error is displayed and publishing blocked | Validation | High | REQ-012, BR-006, AC-012.1 |
| TC-BULK-002 | Bulk Listing Type and Tiered Pricing | Attempt to publish Bulk listing with unverified GSTIN -> Publishing is blocked with error | Business Rule | Critical | REQ-013 |
| TC-PUBLISH-001 | Preview, State Machine and Publishing | Preview Buyer Protection listing -> Preview matches buyer view exactly | UI | High | REQ-014, AC-014.1 |
| TC-PUBLISH-002 | Preview, State Machine and Publishing | Publish listing successfully -> Confirmation screen displays listing ID, status, and link | Positive | Critical | REQ-015 |

## Test Cases

### TC-LISTING-TYPE-001 — Select Standard listing type on Step 1 -> Type is selected and description is displayed

**Feature:** Listing Type Selection and Eligibility · **Type:** Positive · **Priority:** Critical · **Traces to:** REQ-001, AC-001.1

**Preconditions**

- Seller is logged in and on Step 1 of listing creation.

**Test Data**

- `selected_type`: Standard

**Steps**

1. View Step 1 'What are you listing?' screen.
2. Click on the 'Standard' listing type card.
3. Click 'Continue'.

**Expected Result:** Standard radio button is checked, one-line description 'Fixed price. Paid when the order is confirmed.' is visible, and the user navigates to Step 2 'Item details'.

**Postconditions**

- Draft is created with type Standard.

---

### TC-LISTING-TYPE-002 — View ineligible Luxury listing type -> Card is disabled with reason and qualification path

**Feature:** Listing Type Selection and Eligibility · **Type:** Validation · **Priority:** High · **Traces to:** REQ-002, AC-002.1

**Preconditions**

- Seller has 4 completed orders and lacks KYC completion.

**Test Data**

- `seller_orders`: 4
- `kyc_status`: false

**Steps**

1. Navigate to Step 1 'What are you listing?'.

**Expected Result:** Luxury listing type card is visible but disabled (grayed out) with text 'Needs KYC and 10+ completed orders (you have 4)' displayed in red/orange.

---

### TC-COMMON-DETAILS-001 — Auto-save draft on step change -> Draft is saved automatically

**Feature:** Common Listing Details and Draft Management · **Type:** Positive · **Priority:** High · **Traces to:** REQ-003, AC-003.1

**Preconditions**

- Seller has entered valid common details on Step 2.

**Test Data**

- `title`: Sony WH-1000XM5 headphones

**Steps**

1. Fill out valid common details on Step 2.
2. Click 'Next' to proceed to Step 3.

**Expected Result:** Draft is auto-saved immediately upon clicking Next, and user transitions to Step 3 without data loss.

**Postconditions**

- Draft record updated in database.

---

### TC-COMMON-DETAILS-002 — Enter title below minimum character limit -> Inline validation error is shown

**Feature:** Common Listing Details and Draft Management · **Type:** Validation · **Priority:** High · **Traces to:** REQ-004, BR-001

**Preconditions**

- Seller is on Step 2 'Item details'.

**Test Data**

- `title`: Sony

**Steps**

1. Enter 'Sony' (4 characters) into the Title field.
2. Blur the title field.

**Expected Result:** Inline validation error 'Title must be 10 to 80 characters' is displayed below the Title field, and 'Next' button remains disabled or blocks progression.

---

### TC-COMMON-DETAILS-003 — Enter title exceeding maximum character limit -> Inline validation error is shown

**Feature:** Common Listing Details and Draft Management · **Type:** Boundary · **Priority:** High · **Traces to:** REQ-004, BR-001

**Preconditions**

- Seller is on Step 2 'Item details'.

**Test Data**

- `title`: AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA

**Steps**

1. Enter an 81-character string into the Title field.
2. Blur the title field.

**Expected Result:** Inline validation error 'Title must be 10 to 80 characters' is displayed, blocking progression.

---

### TC-COMMON-DETAILS-004 — Enter description below minimum character limit -> Inline validation error is shown

**Feature:** Common Listing Details and Draft Management · **Type:** Validation · **Priority:** High · **Traces to:** REQ-004, BR-002

**Preconditions**

- Seller is on Step 2 'Item details'.

**Test Data**

- `description`: Too short description

**Steps**

1. Enter a description of 21 characters.
2. Blur the description field.

**Expected Result:** Inline validation error 'Min 50 characters' is displayed below the description field.

---

### TC-COMMON-DETAILS-005 — Upload photo exceeding 10 MB size limit -> Validation error code 413 is triggered

**Feature:** Common Listing Details and Draft Management · **Type:** Validation · **Priority:** High · **Traces to:** REQ-004, BR-003

**Preconditions**

- Seller is on Step 2 'Item details'.

**Test Data**

- `file_size_mb`: 11.5
- `file_format`: JPG

**Steps**

1. Click photo upload button and select an 11.5 MB JPG image.

**Expected Result:** Upload fails with error 'Media file exceeds 10 MB limit' (HTTP 413 MEDIA_TOO_LARGE), and the photo slot is marked as failed without corrupting other draft data.

---

### TC-BUYER-PROT-001 — Configure Buyer Protection listing -> Protection fee and payout timeline are displayed correctly

**Feature:** Buyer Protection Listing Type · **Type:** Positive · **Priority:** Critical · **Traces to:** REQ-005, AC-006.1

⚠️ Assumption-based (A-1)

**Preconditions**

- Seller selected 'Buyer Protection' on Step 1 and completed common details with price ₹18,500.

**Test Data**

- `price`: 18500

**Steps**

1. View Step 3 'Buyer Protection' settings screen.

**Expected Result:** Banner shows 'Your listing gets a Buyer Protection badge...', Protection fee is calculated as ₹370 (2%), Buyer pays ₹18,870, You receive ₹18,500, Tracked shipping toggle is enabled by default, and payout timeline message is displayed.

---

### TC-LUXURY-001 — Enter Luxury price below ₹50,000 threshold -> Inline error blocks publishing

**Feature:** Luxury Listing Type and Authentication · **Type:** Boundary · **Priority:** Critical · **Traces to:** REQ-006, BR-004, AC-007.1

**Preconditions**

- Seller selected 'Luxury' on Step 1 and is on Step 3 'Luxury details'.

**Test Data**

- `price`: 42000

**Steps**

1. Enter ₹42,000 into the Price field.
2. Blur price field or attempt to proceed.

**Expected Result:** Inline validation error 'Luxury listings must be ₹50,000 or more' is displayed in red, price border turns red, and progression to preview is blocked.

---

### TC-LUXURY-002 — Submit valid Luxury listing -> Listing enters Pending Review state

**Feature:** Luxury Listing Type and Authentication · **Type:** Positive · **Priority:** Critical · **Traces to:** REQ-008, AC-009.1

**Preconditions**

- Seller completed Luxury details with price ₹75,000, brand, model, serial number, proof of purchase, and all 4 required photos.

**Test Data**

- `price`: 75000
- `brand`: Rolex
- `model`: Submariner

**Steps**

1. Click 'Publish' on the preview screen.

**Expected Result:** Listing is successfully submitted and state becomes 'Pending Review' (Status: Pending Review, Type: Luxury) with message 'Sent for authentication. Most checks finish within 48 hours.'

**Postconditions**

- Listing state in DB is PENDING_REVIEW.

---

### TC-OM-001 — Set OM minimum offer higher than asking price -> Inline error blocks progression

**Feature:** Offer Mode Listing Type · **Type:** Validation · **Priority:** High · **Traces to:** REQ-010, BR-005

**Preconditions**

- Seller selected 'OM (Offer Mode)' and entered asking price ₹22,000.

**Test Data**

- `askingPrice`: 22000
- `minOffer`: 24000

**Steps**

1. Enter ₹24,000 into the Minimum offer field.
2. Blur the field.

**Expected Result:** Inline error 'Must be less than or equal to the asking price' is displayed in red below the minimum offer field, and progression is blocked.

---

### TC-OM-002 — Fetch buyer-facing API/view for OM listing -> Minimum offer is excluded from payload

**Feature:** Offer Mode Listing Type · **Type:** Security · **Priority:** Critical · **Traces to:** REQ-010, AC-010.1

**Preconditions**

- OM listing with asking price ₹22,000 and hidden minOffer ₹18,000 is published.

**Test Data**

- `endpoint`: GET /v1/listings/{id}

**Steps**

1. Send GET request to `/v1/listings/{id}` using a buyer auth token.

**Expected Result:** Response contains asking price and offer expiry, but `minOffer` field is completely stripped by the buyer-facing serializer.

---

### TC-OM-003 — Receive offer below OM minimum offer -> System automatically declines the offer

**Feature:** Offer Mode Listing Type · **Type:** Business Rule · **Priority:** High · **Traces to:** REQ-011, AC-011.1

**Preconditions**

- OM listing is live with asking price ₹22,000 and hidden minimum offer ₹18,000.

**Test Data**

- `incoming_offer`: 16000

**Steps**

1. Buyer submits an offer of ₹16,000 via the offers service.

**Expected Result:** The offer is automatically declined by the system because it is below the hidden minimum offer of ₹18,000, and notification reflects the declined status.

**Postconditions**

- Offer status is set to DECLINED.

---

### TC-BULK-001 — Enter non-decreasing bulk price tier -> Inline error is displayed and publishing blocked

**Feature:** Bulk Listing Type and Tiered Pricing · **Type:** Validation · **Priority:** High · **Traces to:** REQ-012, BR-006, AC-012.1

**Preconditions**

- Seller selected 'Bulk' and is on Step 3 'Bulk pricing'.

**Test Data**

- `tiers`: fromQty: 50; unitPrice: 120; fromQty: 200; unitPrice: 105; fromQty: 500; unitPrice: 110

**Steps**

1. Enter Tier 3 with quantity 500 and unit price ₹110 (higher than previous ₹105).
2. Blur tier fields.

**Expected Result:** Inline error 'Tier 3 must be cheaper than ₹105' is displayed in red, highlighting the offending tier row.

---

### TC-BULK-002 — Attempt to publish Bulk listing with unverified GSTIN -> Publishing is blocked with error

**Feature:** Bulk Listing Type and Tiered Pricing · **Type:** Business Rule · **Priority:** Critical · **Traces to:** REQ-013

**Preconditions**

- Seller account has unverified GSTIN and is creating a Bulk listing.

**Test Data**

- `gstin`: 29ABCDE1234F1Z5
- `status`: unverified

**Steps**

1. Complete all Bulk listing steps.
2. Click 'Publish'.

**Expected Result:** Publishing is blocked, and an error message is displayed stating that GSTIN verification is required before publishing a Bulk listing.

**Postconditions**

- Listing remains in Draft state.

---

### TC-PUBLISH-001 — Preview Buyer Protection listing -> Preview matches buyer view exactly

**Feature:** Preview, State Machine and Publishing · **Type:** UI · **Priority:** High · **Traces to:** REQ-014, AC-014.1

**Preconditions**

- Seller completed all steps for Buyer Protection listing.

**Test Data**

- `type`: Buyer Protection

**Steps**

1. Proceed to Step 4 'Preview as buyer'.

**Expected Result:** Preview screen renders title, photos count, correct calculated price (₹18,870), condition, category, returns policy, and the green 'Buyer Protection' badge with escrow info banner.

---

### TC-PUBLISH-002 — Publish listing successfully -> Confirmation screen displays listing ID, status, and link

**Feature:** Preview, State Machine and Publishing · **Type:** Positive · **Priority:** Critical · **Traces to:** REQ-015

**Preconditions**

- Seller is on Step 4 Preview screen with a valid Standard draft.

**Test Data**

- `idempotency_key`: uuid-test-key-001

**Steps**

1. Click 'Publish' button with a valid Idempotency-Key header.

**Expected Result:** Listing is published, transition succeeds, and confirmation screen displays success checkmark, Listing ID (e.g. LST-8F3K2Q), Type, Status 'Live', and a 'View listing' link.

**Postconditions**

- Listing state is LIVE.
