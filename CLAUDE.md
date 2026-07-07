# Project Context: TableWise

## What this is
TableWise (internally "GrandPlatform") is a full-stack POS + guest-facing ordering platform for
hotels and restaurants: staff POS (order entry, KOTs, inventory deduction, room bookings,
housekeeping, analytics), customer-facing ordering (menu browsing, dine-in/takeaway/delivery,
room booking, M-Pesa/cash payment), and real-time order updates over WebSocket. Actively in
development — current branch work is an M-Pesa payment migration (replacing a prior Stripe
integration; see `render.yaml` note below).

## Stack
| Layer | Tech |
|---|---|
| Backend | FastAPI (async), SQLAlchemy 2.0 (async), PostgreSQL, Alembic |
| Background jobs | Celery + Redis |
| Payments | M-Pesa (Safaricom Daraja STK push) — Stripe fully replaced |
| Frontend | React 18 + TypeScript, Vite, Tailwind, TanStack Query, Zustand, React Router 6 |
| Auth | JWT, shared token scheme for staff and guest accounts |
| Realtime | Socket.IO client ↔ FastAPI WebSocket (`websocket_manager.py`) |
| Deploy | Backend → Render (Docker); Frontend → Vercel |
| Python | 3.12 · Node 18+ |

## Architecture
Backend is layered: `routers/` (HTTP boundary, FastAPI) → `services/` (business logic) →
`models/`+`schemas/` (SQLAlchemy ORM + Pydantic). Routers stay thin; services own transactions
and cross-entity logic. Background work (SMS via africastalking, email, inventory deduction,
forecasting) runs through Celery tasks (`app/tasks.py`, `app/celery_worker.py`).

Frontend mirrors this with `pages/` (route-level views, split into `Auth/`, `Dashboard/` (staff),
`Public/`, `customer/`) → `components/` → API layer (`src/api/*.ts`, one file per resource,
axios-based) → TanStack Query for server state, Zustand (`src/store/*`) for client state (cart,
active orders, auth, toasts).

One payment model (`Payment`) serves both `Order` and `Booking` via a `PaymentEntityType`
discriminator + bare-UUID `entity_id` — see `docs/architecture.md` §2 for the full STK-push →
callback flow, mock mode, and the callback trust boundary (unauthenticated endpoint, amount
verification as the safeguard).

## Where things live
```
backend/app/routers/     HTTP endpoints, one file per resource (auth, orders, payments, rooms, ...)
backend/app/services/    business logic called by routers
backend/app/models/      SQLAlchemy models
backend/app/schemas/     Pydantic request/response schemas
backend/app/utils/       jwt.py, etc.
backend/alembic/versions/  migrations
backend/tests/api/       one test_<resource>.py per router
backend/tests/tasks/, tests/utils/
frontend/src/api/        axios calls per resource, mirrors backend routers
frontend/src/pages/      Auth/, Dashboard/ (staff), Public/, customer/ (guest flows)
frontend/src/store/      Zustand stores (cart, posCart, activeOrders, auth, toast)
frontend/src/routes/     AppRouter.tsx — route registration
frontend/src/contexts/   AuthContext.tsx
frontend/src/components/ Cart/, customer/, landing/, Layout/, shared/, ui/
docs/                    architecture.md (read this first), remediation-prd.md, remediation-todos.md, grand-platform-roadmap.md
```

## Conventions
- **Backend**: async everywhere (`async def`, asyncpg, SQLAlchemy 2.0 async session). Routers
  depend on `routers/deps.py` for auth/DB session injection. Rate limiting via `slowapi`
  (`app/rate_limit.py`).
- **Testing (backend)**: pytest + pytest-asyncio, `backend/tests/conftest.py` sets up fixtures.
  Tests need a real Postgres/Redis reachable via `DATABASE_URL`/`REDIS_URL` — they're **skipped**
  (not failed) if unreachable. Run with `pytest` from `backend/`.
- **Testing (frontend)**: Vitest + Testing Library (`npm test` from `frontend/`). `npm run build`
  runs `tsc` typecheck before Vite build — treat build failures as typecheck failures first.
- **Migrations**: Alembic, revision files named `<hash>_<description>.py` under
  `backend/alembic/versions/`.
- **API prefix**: everything under `settings.API_V1_STR` (`/api/v1`).

## Domain concepts
- **Outlet/Branch, Guest/Customer dual vocabulary**: mid-rename, both live on purpose.
  `outlet_id`/`guest_id` are the real DB columns; `branch_id`/`customer_id` are Python
  `@property` shims on `Order`/`User`/`InventoryItem` reading the same columns. Every affected
  router is mounted at both the new and legacy URL prefix (`/outlets`+`/branches`,
  `/guests`+`/customers`) pointing at the same handler. JWTs accept either `outlet_id` or
  `branch_id` at mint time and normalize to `outlet_id` on decode, so old tokens still work.
  **Write new code against `outlet_id`/`guest_id`** — see `docs/architecture.md` §1 for full detail.
- **PaymentEntityType**: `Payment.entity_type` (`order`/`booking`) + `Payment.entity_id` (bare
  UUID, no FK) let one payment model/service serve both domains without duplicate payment code
  paths.
- **M-Pesa STK push flow**: `CheckoutRequestID` from Safaricom is the only handle on a pending
  payment until their async callback arrives (no metadata echoed back, unlike Stripe) — see
  `docs/architecture.md` §2.
- **Mock M-Pesa mode**: `ENVIRONMENT=development` + `MPESA_CONSUMER_KEY=mock_key` fabricates a
  local `CheckoutRequestID` instead of calling Daraja, letting you exercise the full flow
  (including manually POSTing to `/api/v1/payments/mpesa/callback`) without sandbox access.

## Gotchas / non-obvious things
- `render.yaml` still references leftover `STRIPE_*` env vars from the pre-M-Pesa integration —
  update to `MPESA_*` vars before deploying from a branch that assumes the migration is complete.
- The M-Pesa callback endpoint is unauthenticated (Safaricom doesn't sign callbacks like Stripe
  does); URL obscurity + amount verification are the current safeguards. IP-allowlisting
  Safaricom's ranges is a documented but unimplemented follow-up (see comment in
  `backend/app/routers/payments.py`).
- `docs/` also contains planning artifacts (`remediation-prd.md`, `remediation-todos.md`,
  `grand-platform-roadmap.md`) — check these for in-flight work context before assuming a gap is
  unintentional.
