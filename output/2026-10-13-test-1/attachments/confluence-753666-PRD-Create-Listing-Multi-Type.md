<!-- Source: https://pratikv8070.atlassian.net/wiki/spaces/SD/pages/720897/Create+Listing+Multi-Type › PRD: Create Listing (Multi-Type) (Confluence page 753666, version 1) -->
# PRD: Create Listing (Multi-Type)

Status: DRAFT (DEMO) · 13 Oct 2026 · Related: RFC: Create Listing (Multi-Type) · Figma demo design

## Overview

One Create Listing flow will let sellers publish five listing types — Standard, Buyer Protection, Luxury, OM (Offer Mode) and Bulk — from a single entry point, with type-specific steps added only where needed.

Problem. Today sellers create every listing through one generic form. Sellers who need escrow, authentication or offer-based pricing either contact support or abandon the flow. Support handles these as manual tickets, and listing data is inconsistent across types.

Goals

-
Let a seller create any of the five listing types in under 5 minutes, without support.

-
Share one common form and data model across types; add only the fields each type needs.

-
Raise listing completion rate from the current baseline to 70%+.

Non-goals (v1)

-
Auction listings and live bidding.

-
Editing a published listing's type (seller must create a new listing).

-
Seller analytics dashboard for listing performance.

## Listing types

All five types share the same core listing; each adds its own rules for pricing, payment and verification.

| Type | What it is | Pricing | Payment | Extra checks | Seller eligibility |
| Standard | Default fixed-price listing | Fixed price | Paid to seller on order confirmation | None | Any verified seller |
| Buyer Protection | Funds held in escrow until buyer confirms receipt | Fixed price + protection fee (shown to buyer) | Released 3 days after delivery or on buyer confirmation | Tracked shipping required | Verified seller, no open disputes |
| Luxury | High-value items needing authentication | Fixed price, minimum ₹50,000 | Escrow, released after authentication + delivery | Proof of purchase, serial number, 4+ photos, third-party authentication | KYC-complete seller with 10+ completed orders |
| OM (Offer Mode) | Buyers send offers instead of paying a fixed price | Asking price + optional minimum offer (hidden) | Paid when seller accepts an offer and buyer checks out | Offer expiry window 24–72 h | Any verified seller |
| Bulk | Many units or lots for B2B buyers | Tiered price by quantity | Standard or invoice (net 30) | MOQ, stock count, GST invoice details | Business account with GSTIN |

A seller picks the type first; it cannot be changed after publishing (see Non-goals).

## Personas and user stories

| Persona | Who | Main need |
| Casual seller | Individual selling used items occasionally | Fast, simple listing |
| Trusted seller | Repeat seller who wants buyers to feel safe | Buyer Protection badge |
| Luxury reseller | Sells watches, bags, jewellery | Authentication and high-value safety |
| Negotiator | Seller unsure of the right price | Let buyers make offers |
| Business seller | Wholesaler or distributor | Bulk lots, tiered pricing, GST invoices |

User stories

-
As a seller, I want to choose a listing type at the start so that I only see fields relevant to it.

-
As a seller, I want to save a draft so that I can finish a long listing later.

-
As a trusted seller, I want to enable Buyer Protection so that buyers see a protection badge and trust my listing.

-
As a luxury reseller, I want to upload proof of purchase and request authentication so that my item gets a Verified Luxury badge.

-
As a negotiator, I want to set an asking price and a hidden minimum offer so that low offers are auto-declined.

-
As a business seller, I want to set price tiers by quantity so that larger orders get a lower unit price.

-
As a seller, I want to preview the listing as a buyer sees it before publishing.

-
As an admin, I want Luxury listings to stay in Pending Review until authentication passes.

## User flow

-
Seller chooses a listing type.

-
Eligibility check: if not eligible, show the reason and keep the draft.

-
Seller fills in common details.

-
Seller completes the type-specific step (Standard skips this).

-
Seller previews the listing as a buyer sees it.

-
Seller publishes.

-
Luxury listings go to Pending Review until authentication passes; all other types go Live.

Screens for each step are in the Figma demo design.

## Functional requirements

Every listing shares the common fields below; type-specific fields appear in one extra step only for that type.

Common fields (all types)

| Field | Required | Rules |
| Title | Yes | 10–80 characters, no phone numbers or URLs |
| Category | Yes | Leaf category from the category tree |
| Condition | Yes | New, Like new, Good, Fair |
| Description | Yes | 50–2,000 characters |
| Photos | Yes | 1–10 images, JPG/PNG/WEBP, max 10 MB each, min 800×800 px |
| Quantity | Yes | Integer ≥ 1 |
| Shipping | Yes | Self-ship or platform pickup; weight and dimensions |
| Pickup location | Yes | Saved address, PIN code validated |
| Return policy | Yes | No returns, 7 days, 15 days |

Type-specific requirements

| ID | Type | Requirement |
| FR-1 | All | Type selector is the first step; each type shows a one-line description and eligibility status |
| FR-2 | All | Ineligible types are visible but disabled, with the reason and how to qualify |
| FR-3 | All | Auto-save draft every 10 s and on step change |
| FR-4 | Buyer Protection | Show protection fee and payout timeline before publish; require tracked shipping |
| FR-5 | Buyer Protection | Listing card shows a Buyer Protection badge |
| FR-6 | Luxury | Price must be ≥ ₹50,000; brand, model and serial number required |
| FR-7 | Luxury | Upload proof of purchase (PDF/JPG) and at least 4 photos incl. serial and logo close-ups |
| FR-8 | Luxury | On submit, status = Pending Review until authentication passes; then Live with Verified Luxury badge |
| FR-9 | OM | Seller sets asking price; minimum offer is optional, must be ≤ asking price and is never shown to buyers |
| FR-10 | OM | Seller sets offer expiry (24, 48 or 72 h); offers below the minimum are auto-declined |
| FR-11 | Bulk | Seller sets MOQ and up to 5 price tiers; each tier's unit price must be lower than the previous |
| FR-12 | Bulk | GSTIN must be verified on the business account before publish |
| FR-13 | All | Preview screen renders the listing exactly as a buyer sees it, per type |
| FR-14 | All | Publish confirmation shows listing ID, status and a link to the listing |

## Validation, states and edge cases

Validation runs inline on blur and again on submit; the server is the final check.

Listing states

| State | Meaning | Applies to |
| Draft | Saved, not submitted | All |
| Pending Review | Awaiting authentication or moderation | Luxury; any listing flagged by moderation |
| Live | Visible to buyers | All |
| Rejected | Failed review; reason shown to seller, editable and resubmittable | Luxury, flagged listings |
| Paused | Hidden by seller | All |
| Sold out / Closed | Quantity is 0 or seller closed it | All |

Edge cases

-
Seller loses eligibility mid-flow (e.g. a dispute opens on Buyer Protection): block publish, keep the draft, show the reason.

-
Network drops during photo upload: retry each image 3 times, then mark it failed without losing other data.

-
Seller switches type in the draft: keep common fields, discard type-specific fields after a confirm dialog.

-
OM minimum offer above asking price: inline error, publish blocked.

-
Luxury price edited below ₹50,000 after review: listing returns to Pending Review.

-
Bulk tier prices not decreasing: inline error on the offending tier.

-
Duplicate listing (same title, category and photos within 24 h): warn the seller, allow publish.

-
Two tabs editing one draft: last save wins, other tab shows a stale-data banner.

## Non-functional requirements and API sketch

| Area | Requirement |
| Performance | Each step loads in < 1.5 s at p95; publish API responds in < 800 ms at p95 |
| Uploads | Photos compressed client-side; parallel upload of up to 4 images |
| Availability | 99.9% for listing APIs |
| Security | Proof-of-purchase and GST files stored encrypted, visible only to the seller and reviewers |
| Accessibility | WCAG 2.1 AA; type cards and all fields keyboard-navigable |
| Platforms | Web (desktop, mobile web) and Android/iOS apps with the same flow |
| Localisation | English and Hindi at launch; prices in ₹ |

API sketch

| Method | Endpoint | Purpose |
| GET | /v1/listing-types | Types with the seller's eligibility and reason |
| POST | /v1/listings | Create a draft with type and common fields |
| PATCH | /v1/listings/{id} | Update draft fields, incl. typeAttributes |
| POST | /v1/listings/{id}/media | Upload a photo or document |
| POST | /v1/listings/{id}/publish | Validate and publish; returns new state |
| GET | /v1/listings/{id} | Fetch listing with state and badges |

Sample create request:

{
"type": "OM",
"title": "Sony WH-1000XM5 headphones",
"categoryId": "electronics.audio.headphones",
"condition": "LIKE_NEW",
"quantity": 1,
"typeAttributes": {
"askingPrice": 22000,
"minOffer": 18000,
"offerExpiryHours": 48
}
}

## Success metrics, analytics and acceptance criteria

Success metrics (90 days after launch)

| Metric | Target |
| Listing completion rate (start → publish) | ≥ 70% |
| Median time to publish | < 5 min (Standard), < 10 min (Luxury) |
| Share of listings using a non-Standard type | ≥ 25% |
| Support tickets about listing creation | −50% vs. pre-launch |
| Luxury authentication turnaround | < 48 h at p90 |

Analytics events

-
listing_type_selected (type, eligible)

-
listing_step_completed (type, step, duration_ms)

-
listing_draft_saved (type, auto/manual)

-
listing_validation_error (type, field, error_code)

-
listing_published (type, listing_id, time_to_publish_ms)

-
listing_abandoned (type, last_step)

Acceptance criteria

- Seller can create and publish each of the five types end to end on web, Android and iOS.

- Ineligible types are disabled with a visible reason.

- Draft auto-saves and restores after closing the browser or app.

- Luxury listing below ₹50,000 cannot be published.

- Luxury listing stays Pending Review until authentication passes.

- OM minimum offer is never returned in any buyer-facing API or page.

- OM offers below the minimum are auto-declined.

- Bulk tiers with non-decreasing prices are rejected with an inline error.

- Buyer Protection badge shows on the listing card and detail page.

- Preview matches the published buyer view for every type.

- All analytics events fire with the listed properties.

## Release plan, dependencies, risks and open questions

Release phases

-
Phase 1 — Standard and Buyer Protection, behind a feature flag for 10% of sellers.

-
Phase 2 — OM (Offer Mode) and Bulk, rolled out to all sellers.

-
Phase 3 — Luxury, after the authentication partner integration passes UAT.

Dependencies

-
Escrow/payments service for Buyer Protection and Luxury payouts.

-
Third-party authentication partner API for Luxury.

-
KYC and GSTIN verification services for seller eligibility.

-
Offers service (create, accept, decline, expire) for OM.

Risks

| Risk | Impact | Mitigation |
| Authentication partner is slow | Luxury listings stuck in review, sellers churn | SLA of 48 h in contract; status updates to seller |
| Too many types confuse casual sellers | Lower completion rate | Default to Standard; one-line help on each type card |
| Minimum offer leaks to buyers | Seller trust loss | API contract tests; security review |
| Escrow increases payout time | Seller complaints | Show payout timeline clearly before publish |

Open questions

- Should the Buyer Protection fee be paid by the buyer, the seller, or split?

- Is ₹50,000 the right Luxury minimum, or should it vary by category?

- Can OM listings also have a Buy Now price?

- Do Bulk listings support invoice (net 30) payment in v1 or later?
