# Payment Currency Correctness & Booking Failure Symmetry — PRD

## Summary

An architecture audit of the payment flow (`payment_service.py`, `mpesa_service.py`,
`routers/payments.py`) on 2026-07-04 surfaced one live money bug, one live correctness bug, one
inaccurate architecture doc, and two lower-severity code-quality gaps. This PRD scopes the fix for
all of them. Confirmed with the product owner: **KES is the authoritative currency** for all
pricing in TableWise, and a failed M-Pesa payment on a booking should land in a distinct
`BookingPaymentStatus.failed` state rather than being indistinguishable from "never attempted."

## Problem Statement

1. **Every money field in the system is named and stored as if it were USD, but the business
   prices in KES.** `menu_item.price_usd_cents`, `order.total_usd_cents`,
   `order_item.unit_price_usd_cents`/`subtotal_usd_cents`, `rooms.RoomType.base_price_usd_cents`,
   `rooms.Booking.total_usd_cents`, `rooms.BookingExtra.price_usd_cents`,
   `payment.amount_usd_cents`, and `customer.total_spend_usd_cents` all carry the `_usd_cents`
   suffix. Seed data (`seed_grandplatform.py`) sets `base_price_usd_cents=8500` for a "Standard"
   room — a normal-looking $85.00 room price — and the frontend renders every one of these fields
   with a literal `$` sign (`MenuItemCard.tsx`, `RoomTypeCard.tsx`, `CartDrawer.tsx`, `Book.tsx`,
   `Menu.tsx`, `StayFlow.tsx`, `OrdersFeed.tsx`, `OrderTicket.tsx`, `ProductCard.tsx`). Meanwhile
   `mpesa_service.initiate_stk_push` takes that same integer, divides by 100, and sends it to
   Safaricom's Daraja API as a **KES** amount with zero currency conversion. Since KES is in fact
   authoritative, the numbers themselves (8500, 12500, 22000, etc.) are wrong by roughly two
   orders of magnitude for what they need to represent as KES cents — every M-Pesa charge
   processed today undercharges the guest by ~100x versus the intended KES price.
2. **`handle_payment_failure` only updates `Order`, never `Booking`.** A failed M-Pesa STK push on
   a room booking leaves `Booking.status`/`payment_status` silently unchanged (still
   `pending`/`unpaid`) while the `Payment` row correctly says `failed` — the two records disagree
   and reception staff have no way to see a payment was attempted and failed versus never
   attempted at all, because `BookingPaymentStatus` has no `failed` member.
3. **`docs/architecture.md` misdescribes the `PaymentEntityType` extension point.** It states a
   third payable type "plugs into this same enum + the two if/else branches in
   `payment_service.py`" — in reality the order/booking branch is duplicated across five call
   sites (`routers/payments.py::create_payment_intent`, and four functions in
   `payment_service.py`), and they don't all agree with each other (see problem #2). The doc's
   claim of "no new payment infrastructure needed" is currently false and already produced a bug.
4. **The payment-intent ownership check duplicates a DB fetch and lives at the wrong layer.**
   `routers/payments.py::create_payment_intent` fetches `Order`/`Booking` directly and does
   entity-type branching that also happens inside `payment_service.create_payment_intent_for_entity`
   — the router is reaching past the service boundary the codebase's own layering convention
   (`routers → services → models`) is supposed to enforce.
5. **`PaymentStatus` has duplicate enum aliases.** `pending`/`PENDING`, `success`/`SUCCESS`,
   `failed`/`FAILED`, `reversed`/`REVERSED` are defined as separate members with identical string
   values in `app/models/enums.py`; Python silently aliases the second definition to the first,
   which works but is confusing and easy to typo against.

## Goals

- Every money field reflects its true currency (KES) in both name and stored magnitude, backend
  and frontend, with a migration that corrects existing data rather than just renaming columns.
- `handle_payment_failure` is symmetric with `handle_payment_success` for both entity types, with
  a test that locks in all four success/failure × order/booking transitions.
- `BookingPaymentStatus` gains a `failed` member and the failure path uses it.
- `docs/architecture.md` accurately describes the current number and location of `entity_type`
  branches.
- The router/service duplication around payment-intent creation and ownership checks is
  consolidated into the service layer without changing the existing 403-vs-404 behavior.
- The `PaymentStatus` enum aliasing is cleaned up.

## Non-Goals / Out of Scope

- The `PayableEntity` strategy-pattern refactor discussed during the audit is **explicitly
  deferred**. With exactly two payable types, a `Protocol` + registry + two classes is more
  machinery than the current branches justify — it only pays off once a third payable type (e.g.
  the roadmap's spa booking) is actually scheduled. Tracked as a backlog note, not a requirement
  here.
- Multi-currency support (accepting/pricing in more than one currency) is out of scope — this PRD
  fixes TableWise to be correctly and consistently KES-only.
- Live FX-rate integration is out of scope — not needed since KES is authoritative (no conversion
  required, just correct magnitude/naming).
- Any change to the Stripe-era migration history (`alembic/versions/7f2a1c9e4b3d_*`,
  `94471fb24b14_*`) — those are historical record, not touched.

## User Stories / Use Cases

- As a **guest paying via M-Pesa**, I want to be charged the actual KES price shown to me, so
  that TableWise isn't systematically undercharging (or, once fixed, silently overcharging if the
  fix is done wrong) on every transaction.
- As **finance/ops**, I want the stored amounts to be trustworthy in KES so that revenue reports,
  refunds, and reconciliation against M-Pesa statements are correct.
- As **reception/front-desk staff**, I want to see when a guest's booking payment failed (not just
  "unpaid"), so I know to follow up rather than assuming payment was never attempted.
- As an **engineer** extending the payment system later, I want `docs/architecture.md` to
  accurately describe how many places branch on `entity_type`, so I don't get surprised the way
  the failure-handling bug surprised this audit.
- As an **engineer** reviewing `routers/payments.py`, I want the router to not re-implement
  entity-fetch-and-authorize logic that the service already does, so there's one place to get it
  right.

## Requirements

### Functional Requirements

- **FR-1**: Rename every `*_usd_cents` column/field to `*_kes_cents` across
  `menu_item.price_usd_cents`, `order.total_usd_cents`, `order_item.unit_price_usd_cents`,
  `order_item.subtotal_usd_cents`, `rooms.RoomType.base_price_usd_cents`,
  `rooms.Booking.total_usd_cents`, `rooms.BookingExtra.price_usd_cents`,
  `payment.amount_usd_cents`, `customer.total_spend_usd_cents` — models, Pydantic schemas,
  services, routers.
- **FR-2**: Alembic migration renames the above columns **and** multiplies existing stored values
  by 100 (so a room currently priced at 8500 "cents" — meant to read as $85.00 — becomes
  850000 KES-cents, i.e. KES 8,500.00, preserving the face-value number guests/staff already see
  in demos/seed data as the real KES price) so no in-flight data silently changes face value.
- **FR-3**: `seed_grandplatform.py` (and any other seed script) is updated to set prices at their
  corrected KES-cents magnitude.
- **FR-4**: Every frontend price display (`MenuItemCard.tsx`, `RoomTypeCard.tsx`,
  `CartDrawer.tsx`, `Book.tsx`, `Menu.tsx`, `StayFlow.tsx`, `OrdersFeed.tsx`, `OrderTicket.tsx`,
  `ProductCard.tsx`, `DineFlow.tsx`, `DrinkFlow.tsx`, and any others found referencing
  `*_usd_cents` fields) renders the renamed `*_kes_cents` field with a "KSh" prefix (matching
  common Kenyan-market formatting) instead of `$`.
- **FR-5**: `mpesa_service.py`'s STK-push amount calculation is updated to reference the renamed
  field(s); the `/100` conversion logic itself is unchanged (it was always correct — converting
  minor units to whole KES units — only the field's name and stored magnitude were wrong).
- **FR-6**: `BookingPaymentStatus` gains a `failed` member (+ migration for the Postgres enum
  type).
- **FR-7**: `payment_service.handle_payment_failure` is made symmetric with
  `handle_payment_success`: on failure for a `booking` entity, sets
  `Booking.payment_status = BookingPaymentStatus.failed` (booking `status` remains `pending`,
  not `cancelled`, so staff/guest can retry payment without re-creating the booking).
- **FR-8**: A test exists asserting all four transitions — `handle_payment_success`/
  `handle_payment_failure` × `Order`/`Booking` — update the correct entity fields, so this
  asymmetry class of bug can't regress silently.
- **FR-9**: `docs/architecture.md` §2 is corrected to state the actual number and location of
  `entity_type` branches (five, across `routers/payments.py` and four functions in
  `payment_service.py`), and documents that a new payable type must update all of them (or that
  the strategy-pattern refactor should be revisited at that point).
- **FR-10**: `docs/architecture.md` (or a new note) documents that KES is the authoritative
  currency platform-wide, so this doesn't get re-litigated by a future audit.
- **FR-11**: `routers/payments.py::create_payment_intent`'s entity-fetch-and-ownership-check logic
  is moved into `payment_service.create_payment_intent_for_entity` (or a helper it calls), so the
  router no longer imports `Order`/`Booking` directly. The existing 403-for-unauthorized vs.
  404-for-not-found distinction must be preserved exactly — this is a deliberate security property
  (don't leak the existence of rows an unauthorized caller doesn't own's existence any more than
  the current behavior does), not incidental.
- **FR-12**: `PaymentStatus`'s duplicate uppercase aliases (`PENDING`, `SUCCESS`, `FAILED`,
  `REVERSED`) are removed from `app/models/enums.py`, leaving the single lowercase canonical set
  already used everywhere in application code.

### Non-Functional Requirements

- **Data integrity**: FR-2's migration must be reviewed for correctness on a copy of real data (or
  at minimum tested against the seeded dev DB) before being run anywhere with live bookings/orders
  — a magnitude migration on money columns is unforgiving if it's wrong in either direction.
- **No silent behavior change**: FR-11's consolidation must not change the 403/404 response
  behavior (see FR-11) or introduce a new double-fetch — the router and service already share one
  `AsyncSession`, so a single fetch inside the service is sufficient; no need to pass the loaded
  entity back to the router.
- **Backward compatibility**: none required — no external API consumers depend on the
  `*_usd_cents` field names (frontend and backend are both in this repo and updated together).

## Success Metrics

- `grep -rn "usd_cents" backend/app frontend/src` returns zero results after the migration (only
  historical Alembic files may still mention it).
- A manual/scripted M-Pesa mock-mode payment for a seeded room booking charges the KES amount
  matching what's displayed in the UI (no more, no less) — verified against `initiate_stk_push`'s
  outgoing `Amount` field in mock mode logs.
- `pytest` in `backend/` passes with the renamed fields and the new success/failure symmetry test
  (FR-8), 0 failures.
- `npm test` in `frontend/` passes with all price-display components exercised against the
  renamed fields.
- A failed booking payment (`handle_payment_failure`) results in
  `Booking.payment_status == BookingPaymentStatus.failed` and `Booking.status` unchanged, verified
  by the FR-8 test.
- `docs/architecture.md` §2 no longer claims "two if/else branches."

## Open Questions / Risks

- **Production data migration risk**: if any real (non-seed) `Order`/`Booking`/`Payment` rows
  already exist, FR-2's ×100 migration is a one-way, high-consequence change on money columns.
  Confirm whether any environment currently holds real transaction data before running it there;
  if so, back up first and consider a dry-run report of before/after values.
- **"KSh" vs "KES" display label**: FR-4 assumes "KSh" prefix; confirm this matches whatever
  branding/format the product actually wants before implementing broadly (cheap to change, but
  worth confirming once rather than per-component).
- **`PayableEntity` refactor timing**: explicitly deferred (see Non-Goals) — revisit only when a
  third payable type is actually scheduled, and at that point use FR-8's test as the correctness
  backstop rather than relying on static type-checking, since this repo currently has no
  mypy/pyright CI gate.
