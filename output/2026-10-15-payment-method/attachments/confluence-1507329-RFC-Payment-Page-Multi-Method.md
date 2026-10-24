<!-- Source: https://pratikv8070.atlassian.net/wiki/spaces/SD/pages/1507329/RFC+Payment+Page+Multi-Method (Confluence page 1507329, version 1) -->
# RFC: Payment Page (Multi-Method)

Status: IN REVIEW (DEMO) · 15 Oct 2026

## 1. Document control

| Field | Value |
| Document ID | RFC-PAY-007 |
| Version | 0.1 (Draft, demo) |
| Status | In review |
| Area | Commerce → Payments |
| Author | [Engineer, Payments Platform] |
| Engineering owner | [EM, Payments Platform] |
| Reviewers | Payments, Checkout, Security, Finance, Mobile, Web, QA |
| Decision deadline | [Date] |
| Related documents | PRD: Add to Cart (Multi-Type) · RFC: Create Listing (Multi-Type) |

Approvals

| Role | Name | Decision | Date |
| Payments engineering | [Name] | PENDING | — |
| Security / InfoSec | [Name] | PENDING | — |
| Finance & Reconciliation | [Name] | PENDING | — |
| Compliance | [Name] | PENDING | — |
| QA | [Name] | PENDING | — |

Revision history

| Version | Date | Author | Change |
| 0.1 | 15 Oct 2026 | [Author] | First draft for review |

## 2. Summary, context and goals

This RFC proposes a single Payment Orchestrator behind the payment page, with one adapter per payment method, so eight methods — Cards, UPI, Net Banking, Wallets & Postpaid, E-Gift Vouchers, Pay Later, EMI and Cash on Delivery — share one payment intent, one state machine and one reconciliation flow.

Context. The validated cart from the Add to Cart PRD is handed to Checkout, which creates an order and needs to collect payment. Today only cards and UPI are supported through one gateway, with method logic spread across the web and app clients.

Goals

-
G1: Support all eight methods on web, Android and iOS from one server-driven method list.

-
G2: Keep method-specific logic in isolated adapters; adding a method should not touch the core flow.

-
G3: Never lose or double-charge a payment: every attempt is idempotent and reconciled.

-
G4: Route around a failing gateway without a release.

Non-goals

-
Refund and cancellation flows (separate RFC).

-
Seller payouts and escrow release (owned by Payments Settlement).

-
International cards and multi-currency.

-
Saved UPI mandates and subscriptions.

## 3. Payment methods

All eight methods share one payment intent; they differ in how the buyer authenticates, how we learn the result and whether money is collected now or later.

| Method | Buyer action | Authentication | Result arrives by | Collected | Eligibility rules (demo values) |
| Credit & Debit Cards | Enter card or pick saved token | 3-D Secure / OTP on issuer page | Redirect + webhook | Now | Network-tokenised saved cards only |
| UPI | Intent (app switch), QR, or collect via VPA | UPI PIN in buyer's UPI app | Webhook (async), client polls | Now | Per-transaction UPI limit |
| Internet Banking | Pick bank, redirect to bank site | Bank login | Redirect + webhook | Now | Top banks shown first; full list searchable |
| Wallets & Postpaid | Pick wallet, link or redirect | Wallet login / OTP | Redirect + webhook | Now (wallet) or provider bills later (postpaid) | Wallet balance or postpaid limit from provider |
| E-Gift Vouchers | Enter voucher code + PIN | Code + PIN | Synchronous API | Now | Can combine with one other method (split tender) |
| Pay Later | Pick provider, OTP | Provider OTP | Synchronous API or redirect | Provider pays us; buyer pays provider | Provider credit check; min/max order value |
| EMI | Pick bank card + tenure | 3-D Secure on card | Redirect + webhook | Now (bank converts to EMI) | Order ≥ ₹3,000; eligible card and tenure |
| Cash on Delivery | Confirm COD | None (optional OTP for high value) | Order confirmed immediately | On delivery | Order ≤ ₹50,000; not for Buyer Protection, Luxury or Bulk; serviceable PIN code |

Listing-type rules (from the Create Listing and Add to Cart docs)

-
Buyer Protection and Luxury orders must be prepaid into escrow: COD is hidden.

-
Bulk orders allow all prepaid methods; COD is hidden.

-
If a cart mixes types, the strictest rule wins.

## 4. Architecture

Checkout creates the payment intent; the payment page starts attempts. Each adapter talks only to its own provider, and Cards, UPI, Net Banking and EMI can fail over from Gateway A to Gateway B.

| Layer | Component | Responsibility |
| Client | Payment page (web, Android, iOS) | Shows server-driven method list; starts attempts |
| Client | Checkout service | Creates the payment intent for an order |
| Core | Payment Orchestrator | Adapters for Cards, UPI, Net Banking, Wallets, Gift Voucher, Pay Later, EMI, COD; routing + gateway health; webhooks + status poller |
| Provider | Gateway A | Cards, UPI, Net Banking, EMI (primary) |
| Provider | Gateway B | Failover for the same methods |
| Provider | Wallet providers | Wallets and postpaid |
| Provider | Pay Later providers | Credit check, OTP |
| Provider | Gift voucher service | Balance, block, redeem |
| Provider | Logistics | COD collection on delivery |
| Storage | PostgreSQL | Intents, attempts, webhooks |
| Finance | Daily reconciliation | Matches attempts against gateway settlement files |

## 5. Data model

One payment intent per order holds the amount to collect; each try with a method is a payment attempt. Split tender (gift voucher + one other method) is two attempts under one intent.

payment_intents

| Column | Type | Notes |
| id | UUID | Primary key |
| order_id | UUID | One intent per order |
| amount_minor | BIGINT | Amount in paise |
| amount_captured_minor | BIGINT | Sum of successful attempts |
| status | ENUM | OPEN, PARTIALLY_PAID, PAID, COD_CONFIRMED, EXPIRED, CANCELLED |
| allowed_methods | JSONB | Computed from cart types, amount, PIN code |
| expires_at | TIMESTAMPTZ | 30 min after creation |

payment_attempts

| Column | Type | Notes |
| id | UUID | Primary key; sent to gateway as merchant reference |
| intent_id | UUID | FK to payment_intents |
| method | ENUM | CARD, UPI, NETBANKING, WALLET, GIFT_VOUCHER, PAY_LATER, EMI, COD |
| provider | VARCHAR | Gateway or provider used (after routing) |
| amount_minor | BIGINT | Amount for this attempt |
| status | ENUM | See state machine (section 6) |
| provider_ref | VARCHAR | Gateway transaction ID |
| method_details | JSONB | Masked: card last 4 + network, UPI VPA handle, bank code, EMI tenure; never full card number |
| idempotency_key | VARCHAR | Unique per client request |
| failure_code | VARCHAR | Normalised error code (section 8) |
| created_at / updated_at | TIMESTAMPTZ | |

Split tender example: order ₹2,500 = gift voucher ₹1,000 (attempt 1, SUCCEEDED) + UPI ₹1,500 (attempt 2). If attempt 2 fails, the voucher amount stays held for 30 minutes and is released if the intent expires.

## 6. Payment attempt state machine

Succeeded, Failed, COD confirmed and Auto-refunded are terminal. A success that arrives after the intent has expired is refunded automatically, so a buyer is never charged for an order that was not placed.

| From | To | Trigger |
| Created | Pending | Attempt initiated with provider |
| Created | COD confirmed | Buyer chooses COD |
| Pending | Succeeded | Provider confirms payment |
| Pending | Failed | Declined, cancelled or auth failed |
| Pending | Timed out | No result before timeout |
| Timed out | Succeeded | Status check: paid |
| Timed out | Failed | Status check: not paid |
| Succeeded | Auto-refunded | Late success after intent expired |

## 7. Method-specific flows and rules

Each adapter implements the same interface; the orchestrator never branches on method.

interface PaymentMethodAdapter {
method: PaymentMethod;
isEligible(intent: PaymentIntent, buyer: Buyer): Eligibility; // drives the method list
initiate(attempt: PaymentAttempt): Promise<NextAction>; // redirect URL, UPI intent, OTP, or done
handleCallback(payload: ProviderPayload): Promise<AttemptStatus>;
checkStatus(attempt: PaymentAttempt): Promise<AttemptStatus>; // used by poller and reconciliation
}

| Method | NextAction returned | Key rules |
| Cards | Redirect to 3-D Secure page | Card data entered in gateway-hosted fields only; saved cards are network tokens; one retry with a different card offered on decline |
| UPI | Intent URI (mobile), QR (desktop) or collect request | Poll status every 3 s for up to 5 min; webhook is the source of truth; show "Approve in your UPI app" timer |
| Internet Banking | Redirect to bank | Banks with high failure rate in the last 15 min are shown with a "slow right now" note |
| Wallets & Postpaid | Redirect, or OTP for linked wallet | Postpaid shows provider limit; insufficient balance falls back to split with another method |
| E-Gift Vouchers | Done (synchronous) | Balance checked and blocked first; remainder paid with one other method; max 3 vouchers per order |
| Pay Later | OTP or redirect | Provider credit check result cached for 10 min; min/max order value from provider config |
| EMI | Redirect to 3-D Secure with tenure | Tenure options and interest shown before pay; no-cost EMI subsidy shown as a discount line |
| Cash on Delivery | Done (order confirmed) | Hidden for Buyer Protection, Luxury, Bulk and above ₹50,000; optional OTP above ₹10,000; blocked for buyers with 2+ refused COD orders in 90 days |

## 8. API contracts, webhooks, idempotency and error codes

| Method | Endpoint | Purpose |
| POST | /v1/payments/intents | Create intent for an order; returns allowed methods with eligibility reasons |
| GET | /v1/payments/intents/{id} | Intent with attempts and amount left to pay |
| POST | /v1/payments/intents/{id}/attempts | Start an attempt: method, amount, method fields; Idempotency-Key required |
| GET | /v1/payments/attempts/{id} | Attempt status (client polling for UPI, redirects) |
| POST | /v1/payments/webhooks/{provider} | Provider callbacks; signature verified |
| GET | /v1/payments/emi-plans?amount= | EMI tenures by bank for the amount |

Sample attempt request:

{
"method": "UPI",
"amount": 150000,
"upi": { "flow": "INTENT" }
}

Webhooks. Every provider callback is verified by signature, stored raw, then processed once using provider_ref as the dedupe key. Webhook and redirect may arrive in any order; the first terminal status wins and later ones are logged only.

Idempotency. The same Idempotency-Key within 24 h returns the original attempt instead of creating a new charge.

Normalised error codes (shown to the buyer as plain messages)

| Code | Meaning | Buyer sees |
| PAYMENT_DECLINED | Issuer or bank declined | "Your bank declined this payment. Try another method." |
| AUTH_FAILED | 3-D Secure / OTP / PIN failed | "Verification failed. Please try again." |
| INSUFFICIENT_FUNDS | Wallet, card or voucher balance too low | "Not enough balance. Pay the rest with another method." |
| METHOD_NOT_ELIGIBLE | Rules in section 3 not met | Reason, e.g. "COD isn't available for Luxury items" |
| PROVIDER_UNAVAILABLE | Gateway or bank down | "This option is slow right now. Try another." |
| PAYMENT_TIMEOUT | No result before timeout | "We're checking your payment. Don't pay again." |
| INTENT_EXPIRED | 30 min passed | "Session expired. Please restart checkout." |

## 9. Security and compliance

Card data never touches our servers; the gateway collects it, and we store only network tokens and masked details.

| Area | Control |
| PCI DSS scope | Card fields are gateway-hosted (iframe / SDK), keeping our systems out of card-data scope |
| Card-on-file tokenisation | Saved cards stored only as network tokens per RBI card-on-file rules; no full card numbers or CVV stored |
| Additional factor authentication | Card and EMI payments go through 3-D Secure / OTP as the issuer requires |
| Data localisation | Payment data stored in India-region infrastructure only |
| Webhook security | HMAC signature check, IP allow-list, replay window of 5 min |
| Secrets | Gateway keys in a secrets manager; rotated every 90 days |
| Logging | No card numbers, CVV, UPI PIN or OTP in logs; VPA and phone masked |
| Fraud | Velocity limits per buyer and device; COD abuse block (section 7); high-risk orders sent to manual review |
| Access | Payment data readable only by Payments and Finance roles; all access audited |

Compliance review must confirm the controls above against current RBI and card-network rules before launch; this RFC is not a legal assessment.

## 10. Reliability, reconciliation and observability

Gateway routing and failover

-
Two gateways (primary and secondary) for Cards, UPI, Net Banking and EMI; routing rules in config, changeable without a release.

-
Health score per gateway × method from the last 5 minutes of success rate and latency; traffic shifts to the secondary when success rate drops 10 points below the 24-hour average.

-
Wallets, Pay Later and Gift Vouchers have one provider each; when unavailable, the method is shown as disabled with a reason.

Pending and stuck payments

-
Attempts in PENDING are checked with checkStatus at 1, 5, 15 and 60 minutes.

-
If money is captured after the intent expired (late success), the payment is auto-refunded and the buyer is notified.

Reconciliation

-
Daily job matches every attempt against gateway settlement files by provider_ref and amount.

-
Mismatches (captured but not recorded, recorded but not settled, amount differs) go to a Finance dashboard with an owner and SLA of 2 working days.

Observability

| Signal | Target / alert |
| Payment success rate per method | Alert if 10 points below 24-h average for 10 min |
| Create attempt API latency | p95 < 500 ms (excluding provider time) |
| Webhook processing lag | p95 < 30 s |
| Pending attempts older than 60 min | Alert if > 0.5% of daily attempts |
| Reconciliation mismatches | Alert if > 0.1% of daily volume |

Availability target for payment APIs: 99.95%.

## 11. Alternatives, testing, rollout and risks

Alternatives considered

| Option | Pros | Cons | Decision |
| Own orchestrator + per-method adapters + 2 gateways (proposed) | Failover, one state machine, no vendor lock-in | More code to own; reconciliation is ours | CHOSEN |
| Single gateway's hosted checkout page | Fastest to ship; gateway handles all methods | No failover; limited control of UX and COD/escrow rules | REJECTED |
| Third-party orchestration SaaS | Routing out of the box | Extra fee per transaction; another vendor holding payment data | REVISIT AT SCALE |

Testing strategy

| Layer | Tool | Focus |
| Unit | Jest | Each adapter's eligibility, initiate, callback handling |
| Contract | Pact + gateway sandbox | Request/response and webhook payloads per provider |
| API | Playwright APIRequestContext | Every endpoint, idempotency, error codes, split tender, expired intent |
| E2E web | Playwright (TypeScript) | Each method in gateway sandbox: success, decline, timeout, back button during redirect |
| E2E mobile | Appium | UPI intent app switch, 3-D Secure webview, app killed during payment |
| Resilience | Fault injection | Webhook before redirect, duplicate webhooks, gateway down → failover |
| Reconciliation | Fixture settlement files | Each mismatch type lands on the Finance dashboard |
| Load | k6 | 300 attempts/s with p95 < 500 ms (excluding provider) |

Rollout

-
Phase 1 — Cards, UPI, Net Banking on the new orchestrator (parity with today), 10% of traffic behind flag payments_v2.

-
Phase 2 — Wallets & Postpaid, E-Gift Vouchers (split tender).

-
Phase 3 — EMI and Pay Later.

-
Phase 4 — Cash on Delivery with listing-type rules.

-
Turn on secondary-gateway failover after 2 weeks of clean reconciliation.

Risks

| Risk | Likelihood | Impact | Mitigation |
| Double charge from retries or late webhooks | Medium | High | Idempotency keys; first terminal status wins; auto-refund late success |
| UPI pending for a long time confuses buyers | High | Medium | Clear "don't pay again" message; status checks; notification on final result |
| COD abuse (refused deliveries) | Medium | Medium | Value cap, OTP above threshold, block after repeated refusals |
| Provider config drift (limits, tenures) | Medium | Medium | Provider config pulled daily; alerts on change |
| Reconciliation backlog at launch | Low | High | Phase rollout; Finance dashboard live before Phase 1 |

Open questions

- Which two gateways are primary and secondary for each method?

- Is the ₹50,000 COD cap and ₹10,000 OTP threshold right for our categories?

- Do we show no-cost EMI in v1 or after Phase 3?

- Should gift vouchers be allowed with COD for the remaining amount?

- Who owns the Finance reconciliation dashboard: Payments or Finance engineering?
