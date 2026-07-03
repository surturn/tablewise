# TableWise Remediation — Todo Checklist

Tracks implementation against `docs/remediation-prd.md`. Every item is tagged with the FR/US it satisfies.

## US-1: Kitchen/POS staff — live order updates must reliably authenticate

- [x] `git blame` on `useOrdersWebSocket.ts` and `authStore.ts` to confirm whether the key mismatch is a recent regression or long-standing (Open Question 1) — **resolved: not a regression.** `authStore.ts` has used `'tablewise-auth'` since 2026-04-21 (commit f029357); `useOrdersWebSocket.ts` was introduced later (2026-05-29, commit 5a2b93b) already reading the wrong `'auth-storage'` key. Bug existed from the hook's inception.
- [x] Fix `useOrdersWebSocket.ts` to read the auth token from the same key the Zustand store persists to (`'tablewise-auth'`), or add a single shared getter/selector used by both (FR-1) — used `useAuthStore.getState().token` directly instead of re-parsing localStorage, eliminating the key-drift bug class entirely.
- [x] Remove the dead `'token'` fallback key or replace it with the real selector (FR-1) — removed; no longer needed.
- [x] Add visible failure handling (logged error / connection-state UI) when no valid token is available at connect time — no silent no-op (FR-2) — already present (`console.error("WebSocket blocked: Auth token missing")`), preserved.
- [ ] Manually verify: place a customer order, confirm it appears live on a staff/POS session (Success Metric 1) — pending full-stack run (deferred until backend fixes land, will verify end-to-end together)

## US-2: Engineer — frontend needs a test suite to catch regressions

- [ ] Add Vitest (+ React Testing Library as needed) to `frontend/package.json` with a working `test` script (FR-6)
- [ ] Write a test covering the corrected WebSocket auth-token lookup from US-1 (FR-7)
- [ ] Write a test covering one core existing user flow end-to-end at the component level, e.g. cart/order submission (FR-8)
- [ ] Confirm `npm test` (or equivalent) runs cleanly with ≥2 passing tests (Success Metric 3)

## US-3: Engineer — backend suite must be green and free of secret leakage

- [ ] Check whether the `branch_id` → `outlet_id` key mismatch in `test_security.py` is a recent rename or long-standing (Open Question 1, applies here too)
- [ ] Fix `backend/tests/utils/test_security.py` to assert `outlet_id`, or make the `app/utils/jwt.py` back-compat shim bidirectional if `branch_id` support is still required (FR-3)
- [ ] Fix or remove `backend/tests/tasks/test_celery.py`'s reference to the nonexistent `settings.OPENAI_API_KEY` (FR-4)
- [ ] Mask sensitive fields (`POSTGRES_PASSWORD`, `SECRET_KEY`, etc.) on the `Settings` class repr — `SecretStr` or `repr=False` (FR-5)
- [ ] Investigate the 10 currently-skipped backend tests: confirm they're legitimately environment-gated (e.g. missing local Postgres) and not masking broken coverage (Open Question 2)
- [ ] Run full `pytest` in `backend/` and confirm exit 0 with no failing tests (Success Metric 2)
- [ ] Grep a full backend test run's stdout/stderr for known secret substrings to confirm no leakage (Success Metric 5)

## US-4: Abuse case — brute-force login attempts must be blocked

- [ ] Decide rate-limiter backend (in-memory vs. Redis) based on whether the app runs multiple API replicas (Open Question 3 — **blocks FR-9, resolve first**)
- [ ] Add rate limiting to `/auth/login` (FR-9)
- [ ] Add rate limiting to `/auth/customer/login` (FR-9)
- [ ] Set default threshold (e.g. 5 failed attempts / IP / 15 min) and confirm clear HTTP 429 response (FR-9)
- [ ] Verify rate-limit state can't itself leak credentials or be trivially bypassed via header spoofing (NFR: Security)
- [ ] Confirm rate limiting doesn't add meaningful latency to legitimate logins (NFR: Performance)
- [ ] Manually or scriptedly simulate repeated failed logins and confirm HTTP 429 after threshold (Success Metric 4)

## Unclear / Needs Clarification

- Rate-limiter backend choice (in-memory vs. Redis) is explicitly unresolved in the PRD's Open Questions — must be decided before FR-9 work starts, not assumed.
- No timeline/deadline was confirmed by the user; treating all items as best-effort/priority-ordered per Open Question 4.

## Coverage Check

| ID | Covered? |
|---|---|
| FR-1 | Yes — US-1 |
| FR-2 | Yes — US-1 |
| FR-3 | Yes — US-3 |
| FR-4 | Yes — US-3 |
| FR-5 | Yes — US-3 |
| FR-6 | Yes — US-2 |
| FR-7 | Yes — US-2 |
| FR-8 | Yes — US-2 |
| FR-9 | Yes — US-4 |
| NFR: Security | Yes — US-4 |
| NFR: Reliability | Yes — US-3 |
| NFR: Performance | Yes — US-4 |
| US-1 (staff live updates) | Yes |
| US-2 (frontend test suite) | Yes |
| US-3 (backend suite green/secrets) | Yes |
| US-4 (brute-force protection) | Yes |
| Success Metric 1 (WS auth manual test) | Yes — US-1 |
| Success Metric 2 (pytest exit 0) | Yes — US-3 |
| Success Metric 3 (npm test ≥2 passing) | Yes — US-2 |
| Success Metric 4 (429 on brute-force) | Yes — US-4 |
| Success Metric 5 (no secrets in stdout) | Yes — US-3 |
| Open Question 1 (WS key mismatch origin) | Yes — US-1/US-3 (investigation step) |
| Open Question 2 (skipped tests legit?) | Yes — US-3 (investigation step) |
| Open Question 3 (rate-limiter backend) | Yes — US-4 (blocking decision step) |
