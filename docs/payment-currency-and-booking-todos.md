# Payment Currency Correctness & Booking Failure Symmetry — Todo Checklist

Tracks implementation against `docs/payment-currency-and-booking-prd.md`. Every item is tagged
with the FR it satisfies. Ordered high risk → low risk per the PRD's priority.

## P0 — US: Guest paying via M-Pesa must be charged the correct KES amount (live money bug)

- [ ] Rename backend model columns `*_usd_cents` → `*_kes_cents`: `menu_item.price_usd_cents`,
      `order.total_usd_cents`, `order_item.unit_price_usd_cents`,
      `order_item.subtotal_usd_cents`, `rooms.RoomType.base_price_usd_cents`,
      `rooms.Booking.total_usd_cents`, `rooms.BookingExtra.price_usd_cents`,
      `payment.amount_usd_cents`, `customer.total_spend_usd_cents` (FR-1)
- [ ] Update all Pydantic schemas referencing these fields (`schemas/menu.py`, `schemas/order.py`,
      `schemas/booking.py`, `schemas/payment.py`, `schemas/customer.py`) (FR-1)
- [ ] Update all services/routers referencing these fields (`order_service.py`,
      `booking_service.py`, `payment_service.py`, `mpesa_service.py`, `routers/bookings.py`,
      `routers/rooms.py`) (FR-1, FR-5)
- [ ] Write Alembic migration: rename the 8 columns, and multiply existing values ×100 in the same
      migration (FR-2)
- [ ] Update `seed_grandplatform.py` (and any other seed script) to the corrected KES-cents
      magnitude (FR-3)
- [ ] Update frontend field references and price display in `MenuItemCard.tsx`,
      `RoomTypeCard.tsx`, `CartDrawer.tsx`, `Book.tsx`, `Menu.tsx`, `StayFlow.tsx`,
      `OrdersFeed.tsx`, `OrderTicket.tsx`, `ProductCard.tsx`, `DineFlow.tsx`, `DrinkFlow.tsx` —
      rename fields consumed and switch `$` → `KSh` (FR-4)
- [ ] Sweep remaining frontend files referencing `*_usd_cents` found by the original inventory
      (`api/*.ts`, `store/*.ts`, `pages/Dashboard/*.tsx`) for type/field renames (FR-1, FR-4)
- [ ] Update backend tests referencing old field names (`test_payments.py`, `test_orders.py`,
      `test_menu.py`) and frontend `cartStore.test.ts` (FR-1)
- [ ] `grep -rn "usd_cents" backend/app frontend/src` returns zero results (only historical
      Alembic files may still reference it) (Success Metric 1)
- [ ] Manually verify in M-Pesa mock mode: a seeded room booking's outgoing STK-push `Amount`
      matches the KES price shown in the UI (Success Metric 2)
- [ ] Run `npm test` in `frontend/`, confirm all price-display-related tests still pass with
      renamed fields (Success Metric 4)

## P0 — US: Reception staff must be able to see a booking payment failed, not just "unpaid"

- [ ] Add `BookingPaymentStatus.failed` enum member (FR-6)
- [ ] Alembic migration adding `failed` to the Postgres `bookingpaymentstatus` enum type (FR-6)
- [ ] Make `payment_service.handle_payment_failure` symmetric with `handle_payment_success`: on
      `booking` entity failure, set `payment_status = BookingPaymentStatus.failed`, leave
      `Booking.status` as `pending` (not `cancelled`) (FR-7)
- [ ] Write a test asserting all four transitions: success×order, success×booking, failure×order,
      failure×booking each update the correct fields (FR-8)
- [ ] Run `pytest` in `backend/`, confirm 0 failures with the new test included (Success Metric 3)

## P1 — US: Engineer must be able to trust `docs/architecture.md`'s description of the payment extension point

- [ ] Correct `docs/architecture.md` §2 to state the actual count/location of `entity_type`
      branches (five, not two) (FR-9)
- [ ] Document that KES is the platform-wide authoritative currency (FR-10)
- [ ] Note in `docs/architecture.md` that the `PayableEntity` strategy-pattern refactor is a
      deferred backlog item, not a requirement, until a third payable type is scheduled (ties to
      PRD Non-Goals)

## P2 — Code quality: router/service duplication around payment-intent creation

- [ ] Move `routers/payments.py::create_payment_intent`'s entity-fetch + ownership check into
      `payment_service.create_payment_intent_for_entity` (or a helper it calls) (FR-11)
- [ ] Confirm the 403-vs-404 response behavior is unchanged before/after (write or extend a test
      covering both an unauthorized-owner case and a not-found case) (FR-11, NFR: no silent
      behavior change)
- [ ] Confirm no new duplicate DB fetch is introduced — single fetch inside the service, reusing
      the shared `AsyncSession` (NFR: no silent behavior change)

## P3 — Code quality: enum aliasing cleanup

- [ ] Remove `PaymentStatus`'s duplicate uppercase aliases (`PENDING`, `SUCCESS`, `FAILED`,
      `REVERSED`) from `app/models/enums.py`, leaving only the lowercase canonical members (FR-12)
- [ ] Confirm nothing in the codebase references the uppercase aliases before removing (grep
      first) (FR-12)

## Explicitly Deferred (not part of this checklist)

- `PayableEntity` strategy-pattern refactor — revisit only when a third payable type (e.g. spa
  booking) is actually scheduled; use the FR-8 test as the correctness backstop rather than
  relying on static type-checking (no mypy/pyright CI gate exists in this repo today).
- Multi-currency support / live FX integration — out of scope, KES-only per this PRD.

## Unclear / Needs Clarification

- **"KSh" vs "KES" display label** (FR-4) — proceeding with "KSh" as the common Kenyan-market
  convention; flag for confirmation if the product wants a different format.
- **Production data migration risk** — proceeding on the assumption that current environments hold
  only seed/test data; if any environment has real transaction rows, the ×100 migration (FR-2)
  needs a backup/dry-run step before running there.

## Coverage Check

| ID | Covered? |
|---|---|
| FR-1 | Yes — P0 currency section |
| FR-2 | Yes — P0 currency section |
| FR-3 | Yes — P0 currency section |
| FR-4 | Yes — P0 currency section |
| FR-5 | Yes — P0 currency section |
| FR-6 | Yes — P0 booking-failure section |
| FR-7 | Yes — P0 booking-failure section |
| FR-8 | Yes — P0 booking-failure section |
| FR-9 | Yes — P1 documentation section |
| FR-10 | Yes — P1 documentation section |
| FR-11 | Yes — P2 code-quality section |
| FR-12 | Yes — P3 code-quality section |
| NFR: Data integrity | Yes — Unclear/Needs Clarification (production data risk) |
| NFR: No silent behavior change | Yes — P2 code-quality section |
| NFR: Backward compatibility | N/A — no external consumers, noted in PRD |
| Success Metric 1 (grep clean) | Yes — P0 currency section |
| Success Metric 2 (mock-mode charge matches UI) | Yes — P0 currency section |
| Success Metric 3 (pytest 0 failures) | Yes — P0 booking-failure section |
| Success Metric 4 (npm test passes) | Yes — P0 currency section |
| Success Metric 5 (architecture.md corrected) | Yes — P1 documentation section |
| Open Question 1 (production data risk) | Yes — Unclear/Needs Clarification |
| Open Question 2 (KSh vs KES label) | Yes — Unclear/Needs Clarification |
| Open Question 3 (PayableEntity timing) | Yes — Explicitly Deferred |
