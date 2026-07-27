# Thera Appeal — PRD v2 (Reshaped)

**Supersedes:** PRD v1 (post-pre-mortem)
**Reason for reshape:** Council verdict RESHAPE, high confidence — 0 of 5 reviewers supported v1 as specified. See `thera-appeal-verdict.html`.

---

## 1. What changed and why

| v1 | v2 | Driver |
|---|---|---|
| Appeal letter generator | Denial triage tool; appeal generation is one branch | Appeal-shaped denials are 1–3/mo; triage-shaped events are 6–20/mo |
| $99/mo unlimited | Free triage · $39 per appeal packet · $149/mo practice tier | ROI below 1.0 at $99; $99 = price of a full EHR |
| Upload EOB PDF | De-identified structured input; **no PHI ever enters the system** | No BAA available on the stack; compliance floor ~$600–950/mo |
| Generic letter PDF | Submission packet: payer form + route + deadline + letter with merge fields | A generic PDF is often the wrong artifact |
| Cold outreach to solo therapists | Free triage as acquisition engine; billing services and group practices as revenue | Cold start, no audience, 30–60 day runway |
| Logging as post-launch analytics | Outcome ledger from day one, as the primary asset | The letter is a commodity; the overturn data is not |

---

## 2. Project overview

| Field | Detail |
|---|---|
| **Product name** | Thera Appeal |
| **Tagline** | Know what a denial means before you waste an hour on it. |
| **Primary goal** | Tell a mental-health provider, in under 30 seconds, which of four actions a denial actually requires — then do the paperwork for the one action that's worth paying for. |
| **Target audience** | Primary revenue: mental-health billing services and 5–30 clinician group practices. Primary volume: solo LCSW/LMFT/PsyD who bill their own insurance. |
| **Key differentiator** | Zero-PHI architecture (no BAA required, ships legally today) plus a payer-level outcome ledger nobody else is building. |
| **Pricing** | Triage: free, unlimited, no account. Appeal packet: $39 each / $99 for three. Practice: $149/mo, 5+ seats. Billing services: volume contract. |
| **Trial** | None. Triage is permanently free and needs no card. The first paid moment is a single $39 packet the user chose to buy. |

**Explicit non-goals for v1:** no EOB/PDF upload, no ERA/EHR integration, no PHI storage, no subscription for solo practitioners, no claim submission on the user's behalf.

---

## 3. Validation gate (blocking)

**No engineering begins until this passes.** Offer 20 self-billing therapists a hand-written appeal for $40, taking denials de-identified.

- **Gate A — willingness to pay:** ≥3 of 20 pay $40. If zero pay, there is no floor under any paid tier and the project stops.
- **Gate B — denial mix:** record the four-way sort of everything received. If <30% is genuinely appealable, v2's premise is confirmed and the appeal branch is de-prioritized further in favor of triage depth.

Every denial collected during this gate is seed data for §5.3. Log it in the ledger schema from the first one.

---

## 4. Core user flow

Two loops. The free one runs weekly; the paid one runs monthly at most.

**Triage loop (free, no account, no PHI):**
1. User lands on a triage page — direct, or from a long-tail page for their specific denial code.
2. User enters payer, CARC/RARC code, CPT, denied amount, and optionally pastes denial language. Identifier fields do not exist in the UI.
3. Deterministic engine returns one of four verdicts with a reason, a filing deadline, and a dollar-vs-effort read.
4. If the verdict is anything but APPEAL, the user gets their answer and leaves. This is the product working correctly.

**Appeal loop (paid, $39):**
5. If the verdict is APPEAL, the user is offered a submission packet at $39. Account creation happens here, not before.
6. Packet is generated: payer-correct form, submission route, deadline, attachment checklist, and a letter body containing merge fields — never real patient data.
7. User downloads, fills the merge fields in their own word processor, and submits through the payer's channel.
8. 35 days later, one email: "Did this get paid?" One click. That answer is the asset.

---

## 5. Functional requirements

### 5.1 Zero-PHI input

| Requirement | Detail |
|---|---|
| Structured fields only | Payer (select), CARC/RARC (typeahead), CPT (select), denied amount, date of service **month/year only**, free-text denial language. |
| No identifier fields | No patient name, member ID, claim number, or DOB fields exist anywhere in the product. |
| Paste scrubbing | Free-text input is client-side scrubbed for identifier-shaped strings (long digit runs, name patterns, SSN/member-ID formats) before transmission, with a visible "we removed this, we don't need it" notice. |
| No file upload | Deliberately absent in v1. Revisit only behind a real BAA chain. |
| Stated plainly | A compliance page states: we do not receive PHI, therefore no BAA is required. Linked from every input screen. |

**Rationale:** this removes the single failure mode that killed v1, eliminates a $600–950/mo fixed cost, and lets the product launch this month. The cost is the "upload your PDF" magic — accepted deliberately.

### 5.2 Triage engine (deterministic)

| Requirement | Detail |
|---|---|
| Lookup table, not LLM | ~300 CARC codes × RARC modifiers mapped to verdicts in Postgres. No model call in the free path. Deterministic, testable, instant, free to serve. |
| Four verdicts | RESUBMIT CORRECTED (with the specific field to fix) · BILL THE PATIENT · APPEAL · CALL PAYER. |
| Deadline clock | Appeal/reconsideration window by payer, shown as a date, with the caveat that it runs from the payer's determination date. |
| Worth-it read | Denied amount against typical effort. Explicitly tells the user to write off low-dollar claims when that's the right call. |
| LLM only as fallback | If the code is unmapped, an LLM classifies from pasted language and the result is flagged as unverified and queued for human mapping. |
| Honest gaps | Unknown code returns "we don't know this one yet" rather than a guess. |

**The BILL THE PATIENT verdict is load-bearing.** A deductible-applied EOB drafted as an appeal is active harm and burns trust on first use. Getting this branch right is worth more than letter quality.

### 5.3 Outcome ledger (the asset)

| Requirement | Detail |
|---|---|
| Capture from day one | Every triage and every packet writes: payer, CARC/RARC, CPT, denied amount, verdict, argument used, and — after follow-up — result and dollars recovered. |
| Follow-up | Single email at day 35, one-click paid / denied / no response. |
| Feed it back | Once a payer × code × argument cell has enough observations, surface it: "Appeals to this payer on this code succeed X% of the time." Below threshold, show nothing rather than a misleading number. |
| Aggregate only | No identifiers exist to leak. Published stats are aggregate. |

This is the only asset here that compounds and the only one the free competitors are not structurally motivated to build.

### 5.4 Appeal packet generation

| Requirement | Detail |
|---|---|
| Gated on verdict | Only offered when triage returns APPEAL. Never upsold on a resubmission. |
| Payer-correct artifact | Identify the payer's required reconsideration/dispute form, link it, and state the submission route (portal, address, or fax) and deadline. |
| Merge fields, not data | Letter body ships with `[PATIENT NAME]`, `[MEMBER ID]`, `[CLAIM NUMBER]`, `[DOS]` for the user to fill locally. This is what keeps the system PHI-free. |
| Argument selection | Denial type selects the argument: medical necessity → clinical standard-of-care framing; parity-eligible → mental health parity framing; timely filing → adjudication timeframes **plus an explicit warning that this usually fails without proof of original submission**. |
| Attachment checklist | What to staple to it — progress note, proof of submission, authorization record — by denial type. |
| Editable output | Plain text and .docx, not a locked PDF. The user finishes it in their own tool. |
| Liability language | Retained from v1 §3.4, reframed as a one-time account-level acknowledgment rather than a per-download modal. |

### 5.5 Distribution surface

| Requirement | Detail |
|---|---|
| Long-tail triage pages | One indexable page per common payer × CARC × CPT combination, each with the free triage tool inline. Search intent exists at the moment of the denial. |
| Practice tier | $149/mo, 5+ seats, shared ledger, per-clinician recovery reporting. Sold to group practices where the volume math already closes. |
| Billing service contracts | Volume pricing and white-label. Ten relationships instead of a thousand customers; they already hold BAAs and have the volume. |

---

## 6. Technical requirements

- **Frontend:** React, Tailwind, shadcn/ui.
- **Backend:** Supabase (Postgres + Auth) — standard tier is sufficient **because no PHI is stored**. Auth only on the paid path.
- **Triage:** SQL against the CARC/RARC mapping table. No model in the free path.
- **LLM:** GPT-4o for letter body generation and unmapped-code fallback only. Prompts carry merge-field placeholders, never real data.
- **Payments:** Stripe, one-off charges primary; subscription only on the practice tier.
- **Export:** .docx and plain text.
- **Ledger:** dedicated tables, written on every event, with the day-35 follow-up job.

---

## 7. Open questions

1. Who maintains the CARC → verdict mapping as payer behavior drifts, and how are corrections fed back?
2. Are payer-specific forms and submission routes stable enough to hard-code, and what is the review cadence?
3. Does free triage actually convert to $39 packets, or does it satisfy the need and end the session?
4. Is the paste-scrubber reliable enough to claim "no PHI," and what happens when a user pastes identifiers anyway?
5. Does the day-35 follow-up get answered often enough for the ledger to reach significance in any cell?
