# TableWise

TableWise is a full-stack point-of-sale and guest-facing ordering platform for hotels and
restaurants (branded internally as "GrandPlatform"). It covers:

- **Staff POS** — order entry, kitchen order tickets, inventory deduction, room bookings,
  housekeeping, analytics.
- **Customer-facing ordering** — browse the menu, order dine-in/takeaway/delivery, book rooms,
  pay by M-Pesa STK push or cash.
- **Live updates** — kitchen/POS staff see new orders and status changes over a WebSocket
  connection in real time.

## Stack

| Layer      | Tech |
|------------|------|
| Backend    | FastAPI (async), SQLAlchemy 2.0 (async), PostgreSQL, Alembic migrations |
| Background jobs | Celery + Redis (SMS, email, inventory deduction, forecasting) |
| Payments   | M-Pesa (Safaricom Daraja STK push) |
| Frontend   | React 18 + TypeScript, Vite, Tailwind CSS, TanStack Query, Zustand |
| Auth       | JWT (staff + guest accounts share one token scheme) |
| Deploy     | Backend → Render (Docker); Frontend → Vercel |

## Prerequisites

- Python 3.12, Node 18+
- Docker (for Postgres/Redis locally, or run them natively)

## Backend setup

```bash
cd backend
python -m venv venv
venv/Scripts/activate        # Windows; use `source venv/bin/activate` on macOS/Linux
pip install -r requirements.txt

cp .env.example .env         # fill in real values, see comments in the file
```

Start Postgres + Redis (either via the root `docker-compose.yml`, or point `POSTGRES_HOST`/
`REDIS_URL` in `.env` at instances you already have running):

```bash
docker compose up -d db redis
```

Run migrations and start the API:

```bash
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

API docs are served at `http://localhost:8000/docs` once running.

### Database Seeding

To populate a fresh database with initial dummy data (e.g., users, outlets, rooms, and menus):

1. **Important:** Ensure your Postgres and Redis Docker containers are running before executing the script.
2. Run the database seeding command:

```bash
cd backend
python -m app.seed
```

### Running the backend test suite

Tests need a real Postgres and Redis reachable at whatever `DATABASE_URL`/`REDIS_URL` resolve to
— they're skipped automatically (not failed) if unreachable:

```bash
cd backend
pytest
```

### Celery worker (optional, for background jobs)

```bash
celery -A app.celery_worker worker --loglevel=info
```

## Frontend setup

```bash
cd frontend
npm install
cp .env.example .env          # set VITE_API_BASE_URL to your backend URL
npm run dev
```

### Running the frontend test suite

```bash
cd frontend
npm test
```

### Other frontend scripts

```bash
npm run lint       # ESLint
npm run build      # typecheck (tsc) + production build
```

## Payments (M-Pesa)

Set `MPESA_CONSUMER_KEY=mock_key` with `ENVIRONMENT=development` to run STK push in mock mode
(no real Safaricom calls — a fake `CheckoutRequestID` is generated and payments can be completed
by manually POSTing a callback to `/api/v1/payments/mpesa/callback`). See
`backend/app/services/mpesa_service.py` for the real Daraja integration and
`docs/architecture.md` for how the STK-push → callback flow fits together.

## Deployment

- **Backend**: `render.yaml` defines a Render Blueprint (Docker web service + managed Postgres).
  Note it still references `STRIPE_*` env vars left over from the pre-M-Pesa Stripe integration —
  update it to the `MPESA_*` vars in `backend/.env.example` before deploying from this branch.
- **Frontend**: `frontend/vercel.json` configures the Vite build for Vercel; set
  `VITE_API_BASE_URL` in the Vercel project's environment variables.

## Repository layout

```
backend/    FastAPI app (routers → services → models/schemas), Alembic migrations, pytest suite
frontend/   React app (pages → components, Zustand stores, TanStack Query API layer)
docs/       Planning docs (remediation PRD/todos, roadmap) and architecture notes
```
