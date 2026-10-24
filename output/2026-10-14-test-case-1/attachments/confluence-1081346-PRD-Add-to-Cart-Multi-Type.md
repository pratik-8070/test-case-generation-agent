<!-- Source: https://pratikv8070.atlassian.net/wiki/spaces/SD/pages/1081346/PRD+Add+to+Cart+Multi-Type (Confluence page 1081346, version 1) -->
# PRD: Add to Cart (Multi-Type)

Status: DRAFT (DEMO) · 14 Oct 2026

## 1. Document control

| Field | Value |
| Document ID | PRD-COM-014 |
| Version | 0.1 (Draft, demo) |
| Product area | Commerce → Cart & Checkout |
| Product owner | [Product Manager, Commerce] |
| Engineering lead | [EM, Cart Platform] |
| Design lead | [Product Designer, Buyer Experience] |
| QA lead | [QA Lead, Commerce] |
| Target release | Q1 FY27, phased (see section 11) |
| Related documents | PRD: Create Listing (Multi-Type) · RFC: Create Listing (Multi-Type) |

Approvals

| Role | Name | Decision | Date |
| Product | [Name] | PENDING | — |
| Engineering | [Name] | PENDING | — |
| Design | [Name] | PENDING | — |
| QA | [Name] | PENDING | — |
| Payments / Finance | [Name] | PENDING | — |
| Legal & Compliance | [Name] | PENDING | — |

Revision history

| Version | Date | Author | Change |
| 0.1 | 14 Oct 2026 | [Author] | First draft for review |

## 2. Executive summary

Buyers will be able to add items from all five listing types — Standard, Buyer Protection, Luxury, OM (Offer Mode) and Bulk — to one cart, with each type's rules (offers, MOQ, authentication, escrow fees) enforced at the moment of adding, not at payment.

Background. The Create Listing (Multi-Type) launch lets sellers publish five listing types. The current cart only understands fixed-price, single-unit items, so the new types either cannot be bought through the cart or fail late at checkout.

Problem statement

-
Bulk buyers cannot add a quantity below or above tier boundaries correctly; pricing is recalculated only at payment.

-
OM listings have no price until an offer is accepted, so the cart has nothing to add.

-
Buyer Protection fees appear for the first time on the payment page, which surprises buyers.

-
Luxury items that are still in Pending Review can be reached by deep link and added to the cart.

-
Cart prices and stock go stale; buyers find out only when payment fails.

Proposed solution. A type-aware Add to Cart that validates eligibility, quantity and price per listing type, shows type badges and fees in the cart, reserves scarce stock for a short time, and hands a clean, validated cart to checkout.

## 3. Goals, success metrics and non-goals

Business goals

-
G1: Let buyers purchase every listing type through one cart.

-
G2: Remove late surprises at checkout (fees, price changes, stock).

-
G3: Grow Bulk and Buyer Protection order volume.

Success metrics (measured 60 days after full rollout; baselines to be filled from analytics before sign-off)

| ID | Metric | Baseline | Target |
| M1 | Add-to-cart rate (adds ÷ product page views) | [TBD] | +15% relative |
| M2 | Cart-to-checkout rate | [TBD] | ≥ 55% |
| M3 | Checkout failures caused by price or stock change | [TBD] | −60% relative |
| M4 | Share of orders from non-Standard types | [TBD] | ≥ 20% |
| M5 | Add to Cart API p95 latency | [TBD] | < 300 ms |

Guardrail metrics (must not get worse): payment success rate, refund rate, cart page crash-free sessions.

Non-goals

-
Payment, address and delivery-slot selection (owned by Checkout PRD).

-
Making offers from the product page (owned by Offers team); this PRD only covers adding an accepted offer to the cart.

-
Wishlist, saved-for-later and shared carts.

-
Coupons and promotions engine changes.

## 4. Scope, assumptions and constraints

| In scope (v1) | Out of scope (v1) |
| Add to Cart from product page and accepted-offer screen | Add to Cart from search results and listing cards |
| Cart page: view, change quantity, remove, type badges, fees | Saved for later, wishlist, shared cart |
| Per-type validation (eligibility, quantity, price) | Coupons and promotions |
| Stock reservation for low-stock and single-unit items | Multi-currency carts |
| Price and stock revalidation on cart open and checkout start | Cart merge across devices for logged-out users |
| Handoff of a validated cart to Checkout | Payment, address, delivery slots |
| Web, Android, iOS | Seller-side cart views |

Assumptions

-
A1: Buyer must be logged in to add to cart (guest cart is out of scope for v1).

-
A2: Listings, prices and stock come from the Listing service defined in the Create Listing RFC.

-
A3: The Offers service exposes accepted offers with a price and an expiry.

-
A4: All prices are in INR; GST is shown at checkout, not in the cart.

Constraints

-
C1: Maximum 50 line items per cart (performance and payment-gateway limits).

-
C2: Stock reservations must not exceed 15 minutes, to avoid blocking other buyers.

-
C3: Buyer Protection and Luxury payments must go through escrow (regulatory and partner contracts).

## 5. Cart behaviour by listing type

Every type uses the same cart; each adds its own rule for when an item can be added, what quantity is allowed and which price applies.

| Type | Can be added when | Quantity rule | Price in cart | Shown in cart | Reservation |
| Standard | Listing is Live and in stock | 1 to available stock | Listing price | Price × qty | Only when stock ≤ 3 |
| Buyer Protection | Listing is Live and in stock | 1 to available stock | Listing price + protection fee | Buyer Protection badge, fee as a separate line | Only when stock ≤ 3 |
| Luxury | Listing is Live (authenticated); never in Pending Review | Fixed at 1 | Listing price | Verified Luxury badge, escrow note | Always, 15 min |
| OM (Offer Mode) | Buyer has an accepted, unexpired offer | Quantity in the accepted offer | Accepted offer price (locked) | Offer badge, "Offer expires in" timer | Always, until offer expiry (max 15 min after add) |
| Bulk | Buyer has a business account; qty ≥ MOQ | MOQ to available stock | Unit price from matching tier | Tier table, next-tier saving hint | Never (large stock) |

A single cart can mix types. Items from different sellers stay in one cart; Checkout splits them into orders per seller.

## 6. Personas and user stories

| Persona | Who | Main need |
| Everyday buyer | Buys used or new items occasionally | Quick add, clear total |
| Cautious buyer | First-time or high-value purchase | Protection, no hidden fees |
| Luxury buyer | Buys authenticated watches, bags, jewellery | Certainty the item is verified and held for them |
| Negotiating buyer | Made an offer that the seller accepted | Buy at the agreed price before it expires |
| Business buyer | Procurement for a shop or office | Large quantities, tier pricing, GST invoices |
| ID | User story | Priority |
| US-1 | As a buyer, I want to add an item to my cart from the product page so that I can buy several items together. | Must |
| US-2 | As a buyer, I want to see each item's type badge and any fees in the cart so that the total has no surprises. | Must |
| US-3 | As a cautious buyer, I want the Buyer Protection fee shown before checkout so that I know what I pay. | Must |
| US-4 | As a luxury buyer, I want my item held for me for 15 minutes so that nobody else buys it while I pay. | Must |
| US-5 | As a negotiating buyer, I want to add my accepted offer to the cart at the agreed price so that I can check out. | Must |
| US-6 | As a business buyer, I want the tier price to update as I change quantity so that I can pick the best quantity. | Must |
| US-7 | As a buyer, I want to be told when a price or stock changes in my cart so that checkout does not fail. | Must |
| US-8 | As a buyer, I want to change quantity or remove items from the cart. | Must |
| US-9 | As a business buyer, I want a hint like "Add 20 more to save ₹15 per unit". | Should |
| US-10 | As a buyer, I want my cart to be the same on web and app. | Should |

## 7. User flow

-
Buyer taps Add to Cart (product page, or accepted-offer screen for OM).

-
Server checks the type rules in section 5. If any check fails, the buyer sees the reason and the cart is unchanged.

-
If the item is scarce (Luxury, OM, or stock ≤ 3), the server reserves it.

-
The cart line is added, or its quantity updated if the listing is already in the cart.

-
When the cart is opened, every line is revalidated for price and stock.

-
If any line is flagged (price changed, low stock, unavailable), the buyer fixes it: accepts the new price, reduces quantity or removes the line.

-
When all lines are valid, the buyer goes to checkout with a validated cart.

## 8. Functional requirements

Priority uses MoSCoW: Must, Should, Could. Every Must requirement has an acceptance criterion that QA will test.

| ID | Area | Requirement | Priority | Acceptance criterion |
| FR-1 | All | Add to Cart button on product page for Live listings; hidden for Draft, Pending Review, Paused, Closed | Must | Button absent on a Pending Review Luxury listing, including via deep link |
| FR-2 | All | Server validates listing state, stock and buyer eligibility on every add | Must | API returns 409 with reason when any check fails; cart unchanged |
| FR-3 | All | Adding the same listing again increases quantity instead of creating a new line | Must | One line per listing ID |
| FR-4 | All | Cart shows line items, type badge, unit price, quantity, line total, fees and grand total | Must | Totals match server calculation to the paisa |
| FR-5 | All | Buyer can change quantity or remove a line; totals update within 1 s | Must | Quantity limits per type enforced in UI and API |
| FR-6 | Buyer Protection | Protection fee shown as its own line on the cart and product page | Must | Fee equals Listing service value; included in grand total |
| FR-7 | Luxury | Quantity fixed at 1; 15-minute reservation starts on add | Must | Second buyer sees "Reserved, check back soon" during reservation |
| FR-8 | Luxury | Reservation expiry removes the hold and shows a banner in the cart | Must | After 15 min the item is still in the cart but marked "No longer reserved" |
| FR-9 | OM | Add to Cart only from an accepted, unexpired offer; price locked to the offer | Must | Product page Add to Cart is hidden for OM; offer screen shows it |
| FR-10 | OM | Cart shows offer expiry countdown; expired offer lines cannot go to checkout | Must | Expired line is disabled with "Offer expired" |
| FR-11 | Bulk | Add requires business account; quantity ≥ MOQ | Must | Non-business buyer sees reason and link to upgrade |
| FR-12 | Bulk | Unit price recalculated from tier on every quantity change | Must | Price matches tier table for boundary quantities (MOQ, each tier start) |
| FR-13 | Bulk | Next-tier saving hint | Should | Hint hidden when already on the highest tier |
| FR-14 | All | Cart revalidates price and stock when opened and when checkout starts | Must | Changed lines highlighted with old and new value |
| FR-15 | All | Max 50 lines per cart | Must | 51st add returns CART_FULL with message |
| FR-16 | All | Cart synced across web, Android and iOS for the same account | Should | Item added on web appears on app after refresh |
| FR-17 | All | Mini-cart confirmation (toast) after add with View cart action | Could | Toast shows item name and new cart count |

## 9. Cart rules, line states and edge cases

The server is the source of truth for price, stock and eligibility; the client only displays what the server returns.

Cart line states

| State | Meaning | Can go to checkout? | Buyer sees |
| Active | Valid price and stock | Yes | Normal line |
| Reserved | Stock held for this buyer (Luxury, OM, low stock) | Yes | "Held for you · 12:40 left" |
| Price changed | Seller changed price since add | Yes, after buyer accepts | Old price struck through, new price |
| Low stock | Requested qty > available | Yes, after qty reduced | "Only 2 left" and qty capped |
| Reservation expired | Hold ended, item may still be available | Yes, if still in stock | "No longer reserved" |
| Unavailable | Listing sold out, paused, closed or offer expired | No | Greyed out with Remove action |

Edge cases

-
Seller edits price while the item is in a cart: line moves to Price changed; buyer must confirm before checkout.

-
Two buyers add the last Luxury item: first add wins the reservation; second sees "Reserved, check back soon".

-
OM offer expires while in cart: line becomes Unavailable; buyer is linked back to the offer thread.

-
Bulk buyer reduces quantity below MOQ: inline error, quantity resets to MOQ.

-
Business account downgraded while Bulk line is in cart: line becomes Unavailable with the reason.

-
Buyer Protection disabled by seller after add: line falls back to Standard pricing and fee line disappears; buyer is told.

-
Network error during add: client retries once with the same idempotency key; no duplicate lines.

-
Cart opened after 30 days of inactivity: cart is cleared; buyer sees "Your cart was emptied after 30 days".

## 10. Non-functional requirements, API and analytics

| ID | Area | Requirement |
| NFR-1 | Performance | Add to Cart API < 300 ms at p95; cart page loads in < 1.5 s at p95 on 4G |
| NFR-2 | Availability | 99.95% for cart APIs; cart reads degrade to cached data if Listing service is down |
| NFR-3 | Consistency | Reservations are atomic; one unit is never reserved by two buyers |
| NFR-4 | Security | Cart APIs require auth; buyers can only read and change their own cart |
| NFR-5 | Privacy | OM minimum offer and seller payout amounts never appear in cart responses |
| NFR-6 | Accessibility | WCAG 2.1 AA; timers announced to screen readers once per minute |
| NFR-7 | Localisation | English and Hindi; ₹ formatting with Indian digit grouping |

API sketch

| Method | Endpoint | Purpose |
| GET | /v1/cart | Cart with lines, states, totals |
| POST | /v1/cart/items | Add listingId, quantity, optional offerId; Idempotency-Key header |
| PATCH | /v1/cart/items/{lineId} | Change quantity |
| DELETE | /v1/cart/items/{lineId} | Remove line |
| POST | /v1/cart/validate | Revalidate price and stock before checkout |

Error codes: LISTING_NOT_AVAILABLE, OUT_OF_STOCK, QTY_BELOW_MOQ, QTY_ABOVE_LIMIT, OFFER_EXPIRED, NOT_BUSINESS_ACCOUNT, ITEM_RESERVED, CART_FULL.

Analytics events

| Event | Properties |
| add_to_cart_clicked | listing_id, type, source (pdp / offer) |
| add_to_cart_succeeded | listing_id, type, qty, unit_price, cart_size |
| add_to_cart_failed | listing_id, type, error_code |
| cart_viewed | cart_size, types_present, total |
| cart_line_state_changed | line_id, type, from_state, to_state |
| cart_qty_changed | line_id, type, old_qty, new_qty, tier_changed |
| checkout_started | cart_size, total, types_present |

## 11. Delivery: dependencies, RACI, release plan and risks

Dependencies

| Dependency | Owner team | Needed for | Status |
| Listing service: state, stock, price, type attributes | Listings | All types | AVAILABLE |
| Inventory reservation API | Inventory | Luxury, OM, low stock | NEEDS NEW ENDPOINT |
| Offers service: accepted offer by ID | Offers | OM | NEEDS NEW ENDPOINT |
| Business account flag | Accounts | Bulk | AVAILABLE |
| Escrow fee calculation | Payments | Buyer Protection, Luxury | AVAILABLE |
| Checkout handoff contract | Checkout | All types | IN DESIGN |

RACI (R = Responsible, A = Accountable, C = Consulted, I = Informed)

| Activity | Product | Engineering | Design | QA | Payments |
| Requirements and scope | A/R | C | C | C | C |
| Cart UX and copy | A | C | R | C | I |
| Cart service and APIs | C | A/R | I | C | C |
| Test plan and automation | C | C | I | A/R | I |
| Fee and escrow rules | C | C | I | C | A/R |
| Launch decision | A | R | C | R | C |

Release plan

-
Phase 1 — Standard + Buyer Protection, behind flag cart_multi_type, 10% of buyers for 1 week.

-
Phase 2 — Bulk, all business accounts.

-
Phase 3 — OM, after Offers endpoint is live.

-
Phase 4 — Luxury, after reservation API passes load test.

Each phase moves forward only if M3 improves and guardrail metrics hold for 7 days.

Risks

| Risk | Likelihood | Impact | Mitigation |
| Reservations block stock for real buyers | Medium | High | 15-min cap; reserve only low-stock, Luxury and OM |
| Price-changed lines annoy buyers | Medium | Medium | Clear old vs new price; one-tap accept |
| Offers endpoint slips | Medium | Medium | Ship OM last; phases are independent |
| Tier pricing mismatch between cart and checkout | Low | High | Single pricing function on server; contract tests |

Open questions

- Should guest buyers get a cart in v1, or is login required? (assumed login)

- Should the Buyer Protection fee be optional for the buyer at cart stage?

- Do OM reservations last until offer expiry or a fixed 15 minutes?

- Does Bulk need GST invoice details captured in cart or at checkout?

Sign-off criteria

- All Must requirements have passing automated tests (web, Android, iOS, API).

- Load test: 500 add-to-cart requests/s with p95 < 300 ms.

- No P1 or P2 bugs open.

- Analytics events verified in staging.

- Approvals in section 1 completed.
