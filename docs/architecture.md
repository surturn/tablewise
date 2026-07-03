# Architecture notes

Two things in this codebase aren't obvious from reading a single file in isolation. This doc
exists so the next person (or agent) doesn't have to reconstruct them from `git log`.

## 1. The outlet/branch and guest/customer dual vocabulary

TableWise went through a rename: `Branch` → `Outlet` and `Customer` → `Guest`. The rename is
**structural but not yet complete** — both vocabularies are live at once, on purpose, so nothing
that already depends on the old names breaks.

**Models** (`backend/app/models/`): the real columns are `outlet_id` / `guest_id`. `Order`,
`User`, and `InventoryItem` additionally expose `branch_id` as a Python `@property` that reads
and writes the same `outlet_id` column (see `models/order.py:33-47`, `models/user.py:26-32`).
`Order` does the same for `customer_id` → `guest_id`. These are shims, not separate data — there
is only one column underneath.

**API routes** (`backend/app/main.py:55-60`): every affected router is mounted twice —
`/api/v1/outlets` and `/api/v1/branches` both route to `branches.router`; `/api/v1/guests` and
`/api/v1/customers` both route to `customers.router`. Same handlers, same DB rows, two URLs.

**JWTs** (`backend/app/utils/jwt.py`): `create_access_token` accepts `outlet_id` as the primary
kwarg but falls back to a `branch_id` kwarg via `**legacy` if the caller doesn't pass `outlet_id`.
`decode_access_token` does the mirror image — if a token only has `branch_id` in its payload, it
gets copied into `outlet_id` after decode. This means an old token minted before the rename still
authenticates correctly today.

**Implication for new code**: write new code against `outlet_id`/`guest_id` — those are the real
columns. Only touch the `branch_id`/`customer_id`/`/branches`/`/customers` shims if you're
extending backwards compatibility for something that still calls the old name. If you're
deciding whether to finish the rename (drop the shims) or freeze it here, that's a product call,
not an engineering one — the shims work fine as-is, they're just double the surface area to keep
in your head.

## 2. Payment flow: `PaymentEntityType` abstraction + M-Pesa STK push

**One `Payment` model serves two different domain entities.** A payment is either for an `Order`
(food/drink) or a `Booking` (room stay) — `Payment.entity_type` (`PaymentEntityType.order` /
`.booking`) plus `Payment.entity_id` (a bare UUID, no FK) point at whichever one it is. This
keeps `payment_service.py` entity-agnostic: `create_payment_intent_for_entity`,
`handle_payment_success`, and `handle_payment_failure` all branch on `entity_type` internally
rather than needing separate order-payment and booking-payment code paths. If you add a third
payable thing (e.g. a spa booking), it plugs into this same enum + the two `if/else` branches in
`payment_service.py` — no new payment infrastructure needed.

**The M-Pesa flow** (`backend/app/services/mpesa_service.py`):

1. `initiate_stk_push` calls Safaricom's Daraja API, which returns a `CheckoutRequestID` before
   the customer has actually approved anything on their phone. We store that ID on a `pending`
   `Payment` row immediately — it's our only handle on this payment until Safaricom calls back.
2. The customer approves (or rejects) the STK push prompt on their phone.
3. Safaricom POSTs the result to `/api/v1/payments/mpesa/callback`. Unlike Stripe, **Daraja
   doesn't echo back any metadata we sent** — no order ID, no customer reference — just the
   `CheckoutRequestID` and a result code/amount. So `handle_mpesa_callback` looks the `Payment`
   row up by `CheckoutRequestID` (which we stored in step 1) to figure out which order/booking
   this callback is for.
4. On success (`ResultCode == 0`), the callback's `Amount` is checked against the payment's
   stored amount before anything is marked paid — a mismatch leaves the payment `pending` for
   manual reconciliation rather than trusting the callback blindly (see
   `mpesa_service.handle_mpesa_callback`). On failure, the payment/order/booking is marked
   failed — unless the payment was already `success`, in which case a late/duplicate failure
   callback is ignored (idempotency guard in `payment_service.handle_payment_failure`).

**Trust boundary, currently**: the callback endpoint is unauthenticated — Safaricom doesn't sign
callbacks the way Stripe does. The callback URL's obscurity plus the amount-verification above
are the current safeguards; IP-allowlisting Safaricom's ranges is a documented follow-up, not yet
implemented (see the comment in `backend/app/routers/payments.py`).

**Mock mode**: with `ENVIRONMENT=development` and `MPESA_CONSUMER_KEY=mock_key`, `initiate_stk_push`
skips the real Daraja call and fabricates a `CheckoutRequestID` locally — useful for exercising
the whole flow (including hitting `/mpesa/callback` by hand) without Safaricom sandbox access.
