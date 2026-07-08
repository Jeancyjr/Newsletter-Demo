# Ontaskly | Product Requirements Document (PRD) v5.0

**Version:** 5.0 (Reshaped after council review)
**Date:** July 8, 2026
**Status:** DRAFT — pending validation gate (Section 2)
**Supersedes:** v4.1
**Build model:** Solo founder + Claude Code / GitHub (AI-accelerated development)

---

## 0. What changed from v4.1 and why

v4.1 was reviewed by an adversarial five-persona council (contrarian, bull,
first-principles, market research, target-customer). Verdict: **RESHAPE**. The
core insight (SnapSign / change-order capture) survived; the plan around it did
not. Key changes:

| v4.1 | v5.0 | Reason |
|---|---|---|
| Home Depot Pro / Ferguson price-book APIs | **Removed.** User-editable price books | Those APIs are partner-only (negotiated B2B deals); not accessible to an indie builder. The claim was fictional as specced. |
| 0.5% platform fee on all payments | **Fee on card/tap-to-pay only; $0 on everything else** | Target customers actively route around revenue taxes (Zelle/check). A fee on all volume kills payment attach — and payment attach is the business. |
| 3 phases, 6 modules, "locked" scope | **1 wedge product + validation-gated fast-follows** | AI-accelerated builds lower the cost of building, not the cost of building the wrong thing. Scope is earned by traction, not locked upfront. |
| Photo-to-Quote as an authoritative quote engine | **AI Draft Assist — always editable, never final** | One hallucinated price destroys trust permanently. AI drafts; the tradesperson owns the number. |
| Success metrics asserted (+12%, 50%, <4%) | **Metrics become hypotheses to test** | None were evidence-based. They are now the validation gate. |

---

## 1. Product overview & positioning

**Ontaskly** is a mobile app that helps solo tradespeople (plumbers,
electricians, HVAC) **get paid for all the work they actually do** —
especially the unplanned "while-I-was-in-there" work that never makes it onto
an invoice.

**Positioning:** not another field-service management suite. Jobber and
Housecall Pro organize crews; Joist does free invoices. Ontaskly's category is
**revenue capture**: the fastest path from "found extra work in a basement" to
"signed, billed, and paid."

**Target customer:** solo operator, ~$150–300K/yr revenue, invoices at the
kitchen table at night, currently on Joist / texted photos / Zelle.

---

## 2. Validation gate (before dev kickoff)

No production code until this 48-hour test returns signal:

- Post in 3–5 trades Facebook groups (and/or supply-house counter
  conversations) with one mockup screen and one question: *"Last month, how
  much 'while-I-was-in-there' work did you do that never made it onto an
  invoice — and would you pay $29/mo for an app that gets it signed and billed
  on the spot, offline, in 30 seconds?"*
- **Pass criteria:** ≥10 tradespeople name a real dollar figure for their
  change-order leakage, and ≥3 give an email for a beta.
- **Fail:** the +X% invoice-value thesis is invented; stop or re-aim.

The dollar figures collected here replace the invented "+12%" metric with a
measured baseline.

---

## 3. Monetization

- **Pro tier: $29/mo flat.** Unlimited quotes, invoices, SnapSign orders.
- **Card & tap-to-pay processing:** standard Stripe rate + 0.5% platform fee,
  with the exact net deposit shown before every transaction ("You receive
  $482.50").
- **No fee on any non-card settlement.** Recording a check/cash/Zelle payment
  against an invoice is free forever. The app must be the system of record
  even when it isn't the payment rail — that's how it earns the rail later.
- **Long-term thesis (unchanged from v4.1, but earned not assumed):** payments
  attach → payments data → instant payouts / materials financing (Toast
  playbook). None of this is in scope until payment attach >50%.

---

## 4. Scope

### v1 — The Wedge (target: 4–6 weeks, AI-accelerated)

One product, one job: capture and collect on-site.

1. **SnapSign (flagship).** Offline-first change orders:
   photo → AI-polished description (GPT-4o mini, editable) → price entered by
   the tradesperson → customer signs on-device → total auto-appends to the
   active invoice → syncs when signal returns.
   - Offline layer: local SQLite queue with explicit conflict rules
     (append-only change orders; invoice totals recomputed server-side on
     sync; signature blobs stored locally until confirmed uploaded).
   - This is the highest-risk engineering in the product. It is built
     **first**, not last, and gets field testing (real basements, airplane
     mode) before anything else is added.
2. **Dead-simple invoicing.** Create, send (SMS/email link), track status.
   One-tap Joist/CSV customer import.
3. **Get paid.** Stripe payment links + Tap to Pay (Stripe Terminal SDK).
   Manual "mark paid" for cash/check/Zelle at no charge.

**Rule of Three (kept from v4.1):** every core action ≤3 taps from Home.
- Home → Active Job → SnapSign
- Home → Active Job → Collect Payment
- Home → Customer → New Invoice

### v1.5 — The Hook (gated on: v1 shipped + ≥10 active weekly users)

4. **Missed-call text-back.** Auto-SMS to missed callers with a booking link.
   Council finding: this is the strongest *marketing* feature — the thing that
   demonstrably books jobs — and should headline acquisition messaging, but it
   is not required to prove the wedge.

### v2 — Quote acceleration (gated on: SnapSign weekly adoption ≥30%)

5. **AI Draft Assist (formerly Photo-to-Quote).** Photo → draft line items
   priced from the **user's own price book** (seeded manually or from their
   invoice history). Clearly labeled a draft; requires explicit review before
   send. No third-party supplier pricing until a real data partnership exists.

### v3 — Growth flywheel (gated on: 30-day retention ≥70%)

6. Google review request on payment completion; $10/mo referral credit.

### Explicitly out of scope

- Home Depot Pro / Ferguson API integrations (revisit only with a signed
  partnership).
- Lead triage AI, scheduling/dispatch, crew features — that's Jobber's game.
- Any fintech beyond payment processing (financing, payouts, banking).

---

## 5. Technical stack

- **Frontend:** React Native + Expo (native modules required for Stripe
  Terminal Tap to Pay).
- **Offline layer:** SQLite (expo-sqlite) + sync queue. Supabase has no
  first-class offline story, so the local store is the source of truth in the
  field; the server reconciles on sync. This is designed and tested as its own
  subsystem.
- **Backend:** Supabase (Postgres, Auth, Storage).
- **AI:** GPT-4o mini for SnapSign description polish and draft-assist copy.
  AI never produces a price; prices come from the user or their price book.
- **Payments:** Stripe Connect (Express) + Stripe Terminal SDK. Progressive
  onboarding: quotes/invoices immediately; KYC (SSN/bank) deferred to first
  payout.

**AI-accelerated build notes:** CRUD surfaces, screens, and schema are cheap
to generate and iterate. The two areas requiring disproportionate human
verification are (a) offline sync/conflict handling and (b) money movement —
both get dedicated test plans and real-device field testing, not just
generated unit tests.

---

## 6. Risks & mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Nobody switches from free (Joist/Zelle) | Fatal | Validation gate (§2) before code; one-tap Joist import; free non-card payments |
| Users route payments around the fee | High | Fee on card only; app stays useful (and sticky) as system of record for $0 |
| Offline sync data loss / signature disputes | High | Append-only change orders, local-first storage, server-side total recompute, field testing in airplane mode; signed PDF snapshot generated at signature time |
| AI writes something wrong on a legal document | High | AI drafts descriptions only, always editable, never prices; explicit review step before signature |
| Incumbents copy SnapSign | Medium | Accepted. The moat isn't the feature; it's payment attach + speed of iteration. Win the solo segment they structurally under-serve |
| Building v2/v3 before v1 proves out | Medium | Hard gates between phases (adoption/retention thresholds above), enforced in this document |

---

## 7. Success metrics (now hypotheses, with gates)

| Hypothesis | Measure | Gate it unlocks |
|---|---|---|
| Change-order leakage is real and quantifiable | ≥10 tradespeople name a dollar figure (validation test) | Start v1 build |
| SnapSign changes on-the-job behavior | ≥30% of weekly-active users create ≥1 SnapSign order/week | v2 (Draft Assist) |
| The product retains | 30-day retention ≥70% (churn ≤ ~10%/mo for v1; tighten later) | v3 (flywheel) |
| Payments attach without coercion | >50% of invoice volume settled in-app within 60 days of a user's first payout | Fintech exploration |
| Invoice-value lift (the original +12% claim) | Measured against each user's pre-Ontaskly baseline from the validation interviews | Marketing claim, only once measured |
