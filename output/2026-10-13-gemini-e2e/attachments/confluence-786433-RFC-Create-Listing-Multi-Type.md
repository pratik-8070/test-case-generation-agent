<!-- Source: https://pratikv8070.atlassian.net/wiki/spaces/SD/pages/720897/Create+Listing+Multi-Type › RFC: Create Listing (Multi-Type) (Confluence page 786433, version 1) -->
# RFC: Create Listing (Multi-Type)

Status: DRAFT (DEMO) · 13 Oct 2026

## Summary and context

This RFC proposes one Listing service with a pluggable type strategy, so Standard, Buyer Protection, Luxury, OM (Offer Mode) and Bulk listings share one data model, one API and one state machine.

| Item | Value |
| Status | Draft (demo) |
| PRD | PRD: Create Listing (Multi-Type) |
| Figma | Create Listing (Multi-Type) – Demo Design |
| Reviewers | Backend, Mobile, Web, QA, Payments, Security |
| Target release | Phase 1 (Standard + Buyer Protection) |

Goals

-
One listings API for all five types; type-specific rules live in isolated strategy classes.

-
Adding a new type needs a new strategy and a feature flag, not a schema migration.

-
Same validation on client and server, driven by a type schema the server publishes.

Non-goals

-
Auctions, buyer checkout, and the offers negotiation UI (owned by the Offers team).

## Architecture

All clients call one Listing service; each type's strategy calls only the dependencies it needs, and all types share one PostgreSQL table.

| Layer | Component | Responsibility |
| Clients | Web app, Android app, iOS app | Render forms from the type JSON schema |
| Edge | API gateway | Auth, rate limits |
| Core | Listing service (strategies: Standard, Buyer Protection, Luxury, OM, Bulk) | Validation, state machine, publish |
| Dependency | Escrow service | Buyer Protection + Luxury payouts |
| Dependency | Offers service | OM offers |
| Dependency | Authentication partner API | Authenticates Luxury items |
| Dependency | KYC / GSTIN check | Seller eligibility |
| Dependency | Media storage | Photos and documents |
| Storage | PostgreSQL | listings + type_attributes |

## Data model

Common fields live in typed columns; type-specific fields live in one validated JSONB column, so new types need no migration.

listings

| Column | Type | Notes |
| id | UUID | Primary key |
| seller_id | UUID | FK to sellers |
| type | ENUM | STANDARD, BUYER_PROTECTION, LUXURY, OM, BULK |
| state | ENUM | DRAFT, PENDING_REVIEW, LIVE, REJECTED, PAUSED, CLOSED |
| title | VARCHAR(80) | |
| category_id | VARCHAR | Leaf category |
| condition | ENUM | NEW, LIKE_NEW, GOOD, FAIR |
| description | TEXT | 50–2,000 characters |
| quantity | INT | ≥ 1 |
| price_minor | BIGINT | Price in paise; null for OM until an offer is accepted |
| type_attributes | JSONB | Validated against the type's JSON schema |
| schema_version | INT | Version of the type schema used |
| version | INT | Optimistic locking |
| created_at / updated_at / published_at | TIMESTAMPTZ | |

Supporting tables

| Table | Purpose |
| listing_media | Photos and documents (proof of purchase, GST), with kind, storage key, order |
| listing_state_history | Every state change: from, to, actor, reason, timestamp |
| listing_reviews | Luxury authentication requests and results from the partner |

type_attributes examples

{ "OM": { "askingPrice": 22000, "minOffer": 18000, "offerExpiryHours": 48 },
"BULK": { "moq": 50, "tiers": [{ "minQty": 50, "unitPrice": 120 }, { "minQty": 200, "unitPrice": 105 }] },
"LUXURY": { "brand": "Rolex", "model": "Datejust 41", "serialNumber": "XXXX" } }

minOffer is stored encrypted at field level and removed by the buyer-facing serializer.

## Listing type strategy

Each type implements one interface; the Listing service picks the strategy by type and never branches on type elsewhere.

interface ListingTypeStrategy {
type: ListingType;
attributeSchema: JSONSchema; // published to clients via GET /v1/listing-types
checkEligibility(seller: Seller): Eligibility;
validate(listing: ListingDraft): ValidationError[];
onPublish(listing: Listing): Promise<ListingState>; // returns LIVE or PENDING_REVIEW
serializeForBuyer(listing: Listing): BuyerListing; // strips hidden fields
}

| Type | Eligibility | Extra validation | onPublish |
| Standard | Verified seller | None | LIVE |
| Buyer Protection | Verified, no open disputes | Tracked shipping required | Register with escrow service → LIVE |
| Luxury | KYC complete, 10+ orders | Price ≥ ₹50,000; brand, model, serial; proof of purchase; 4+ photos | Create authentication request → PENDING_REVIEW |
| OM | Verified seller | minOffer ≤ askingPrice; expiry in {24, 48, 72} | Register with offers service → LIVE |
| Bulk | Business account, verified GSTIN | MOQ ≥ 1; up to 5 tiers, unit price strictly decreasing | LIVE |

The same JSON schemas drive client-side form validation on web, Android and iOS.

## State machine

Every transition is written to listing_state_history; any transition not listed here returns 409 INVALID_STATE_TRANSITION.

| From | To | Trigger |
| Draft | Live | Publish (all types except Luxury) |
| Draft | Pending Review | Publish (Luxury) |
| Pending Review | Live | Authentication passes |
| Pending Review | Rejected | Authentication fails |
| Rejected | Draft | Seller edits and resubmits |
| Live | Paused | Seller pauses |
| Paused | Live | Seller resumes |
| Live | Sold out / Closed | Quantity reaches 0 or seller closes |

## API contracts, error codes and idempotency

| Method | Endpoint | Request | Response |
| GET | /v1/listing-types | — | Types, eligibility + reason, attribute JSON schema |
| POST | /v1/listings | type + common fields | 201, listing in DRAFT |
| PATCH | /v1/listings/{id} | Partial fields + If-Match: <version> | 200, updated draft |
| POST | /v1/listings/{id}/media | Multipart file, kind | 201, media id |
| POST | /v1/listings/{id}/publish | Idempotency-Key header | 200, new state (LIVE or PENDING_REVIEW) |
| GET | /v1/listings/{id} | — | Seller view (owner) or buyer view (others) |

Error codes

| HTTP | Code | When |
| 400 | VALIDATION_FAILED | Field errors; body lists field, code, message |
| 403 | TYPE_NOT_ELIGIBLE | Seller fails the type's eligibility check |
| 409 | VERSION_CONFLICT | If-Match version is stale (two tabs editing) |
| 409 | INVALID_STATE_TRANSITION | e.g. publish on a LIVE listing |
| 413 | MEDIA_TOO_LARGE | File over 10 MB |
| 422 | DEPENDENCY_REJECTED | Escrow, offers or authentication service refused the listing |
| 503 | DEPENDENCY_UNAVAILABLE | Downstream service down; listing stays DRAFT |

Idempotency. Publish requires an Idempotency-Key; the key and response are stored for 24 h, so a retried publish returns the first result instead of registering twice with escrow or offers.

## Alternatives considered

| Option | Pros | Cons | Decision |
| One service + type strategies + JSONB attributes (proposed) | One API and state machine; new type without migration | JSONB needs schema validation and careful indexing | CHOSEN |
| Separate table per type | Strong typing per column | Migration for every new type; duplicated common logic | REJECTED |
| Separate microservice per type | Teams own types independently | Five APIs for clients; cross-type features duplicated | REJECTED |
| Single wide table with nullable columns | Simple queries | Dozens of nullable columns; unclear which apply to which type | REJECTED |

## Security, observability and testing

Security

-
Proof-of-purchase and GST documents in a private bucket, encrypted at rest; signed URLs valid 5 minutes, visible only to the owner and reviewers.

-
minOffer encrypted at field level; buyer serializer has an allow-list, so new hidden fields are excluded by default.

-
Only the listing owner can PATCH or publish; checked in the service, not only the gateway.

Observability

-
Metrics: publish latency (p95), publish success rate per type, dependency error rate, Luxury time in PENDING_REVIEW.

-
Alerts: publish error rate > 2% for 10 min; authentication queue older than 48 h.

-
Structured logs carry listing_id, type, state and idempotency key.

Testing strategy

| Layer | Tool | Focus |
| Unit | Jest | Each strategy's eligibility, validation and onPublish |
| Contract | Pact | Escrow, offers and authentication partner APIs |
| API | Playwright APIRequestContext | Every endpoint, error code, idempotency and If-Match conflict |
| E2E web | Playwright (TypeScript) | Create and publish each of the five types; draft restore |
| E2E mobile | Appium | Same flows on Android and iOS |
| Security | Automated check in API suite | minOffer never appears in any buyer response |
| Performance | k6 | Publish p95 < 800 ms at expected peak load |

## Rollout, migration and open questions

Rollout

-
Ship the new service behind flag listing_types_v2; existing generic form keeps working.

-
Phase 1: Standard + Buyer Protection to 10% of sellers, then 100% after one week with error rate < 1%.

-
Phase 2: OM and Bulk to all sellers.

-
Phase 3: Luxury after authentication partner UAT passes.

Migration

-
Existing listings are backfilled as type = STANDARD, type_attributes = {}, schema_version = 1.

-
Backfill runs in batches of 5,000 rows; old endpoint stays read-compatible until all clients move to /v1/listings.

Open questions

- Store price_minor for OM as the asking price, or keep it null until an offer is accepted?

- Do we need a search index field per type attribute (e.g. Luxury brand) in v1?

- Who owns the authentication partner integration: Listings team or Trust & Safety?

- Review the demo Figma screens (01–05b) against the state machine and error codes.
