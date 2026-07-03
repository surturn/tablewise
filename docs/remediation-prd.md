# TableWise Audit Remediation — PRD

## Summary

The 2026-07-02 project audit of TableWise (FastAPI backend + React/Vite frontend) found a backend with solid layered architecture and real test coverage, alongside a frontend with zero automated tests and at least one confirmed functional bug in production-critical auth flow. This PRD scopes the remediation work needed to close the bug and coverage/security gaps identified in that audit. It does not cover repo hygiene (committed `node_modules`, stray root `package.json`) or missing documentation (READMEs, architecture notes) — those are tracked as explicit non-goals below and can be picked up in a follow-up pass.

## Problem Statement

Three concrete problems surfaced during the audit:

1. **Live order updates likely never authenticate.** `useOrdersWebSocket.ts` reads the auth token from a localStorage key (`'auth-storage'`) that the Zustand store never writes to (it persists under `'tablewise-auth'`), and the fallback key (`'token'`) is never written anywhere either. In practice this means the WebSocket connection either fails to authenticate or silently runs unauthenticated, depending on server-side enforcement — neither is acceptable for an order-management system used by staff and kitchen/POS terminals in real time.
2. **The frontend has no safety net.** There are no test files, no test runner configured, and no CI signal for regressions in `frontend/src`. Given the backend has 15 real pytest tests covering auth, orders, payments, and inventory, the frontend is the weak link for catching breakage before it reaches staff or guests.
3. **Auth endpoints are open to brute-force, and a backend test currently leaks secrets to stdout.** No rate limiting exists on `/auth/login` or `/auth/customer/login`. Separately, a failing backend test (`test_mock_ai_forecast_task`) prints the full `Settings` object repr — including `POSTGRES_PASSWORD` and `SECRET_KEY` — in plaintext, which is a live credential-leak risk if that output ever reaches CI logs external to the local machine.

## Goals

- Close the WebSocket auth-token bug so real-time order updates reliably authenticate.
- Get the two currently-failing/broken backend tests (stale `branch_id` assertion, orphaned `OPENAI_API_KEY` reference) green or removed, and stop the `Settings` object from leaking secrets to stdout.
- Stand up a minimal but real frontend test suite (runner + first tests) covering at least the fixed WebSocket auth path and one core user flow, so future regressions in that area are caught automatically.
- Add rate limiting to both login endpoints to close the brute-force gap.

## Non-Goals / Out of Scope

- Repo hygiene: purging the committed root `node_modules/` (4,859 files) and fixing the stray root `package.json` are **not** covered by this PRD. Tracked separately.
- Documentation: root/backend/frontend READMEs and the `outlet_id`/`branch_id` architecture note are **not** covered by this PRD. Tracked separately.
- Broad frontend test coverage (every component/page) — this PRD scopes only the initial runner setup plus tests for the flows directly tied to the bug fix, not a full coverage push.
- Any new product features (offline POS sync, mobile money, AI forecasting) from `docs/grand-platform-roadmap.md` — unrelated to this remediation effort.

## User Stories / Use Cases

- As a **kitchen/POS staff member**, I want live order updates to arrive reliably over the WebSocket connection, so that I'm not missing new orders or status changes during a shift.
- As an **engineer** working on the frontend, I want a test suite to exist, so that I can verify a fix (like the WebSocket auth bug) doesn't regress later and get fast feedback on other changes.
- As an **engineer** reviewing CI output, I want the backend test suite to be green and free of secret leakage, so that a red pipeline always means a real problem, and logs are safe to share.
- As an **attacker attempting credential stuffing** (failure/abuse case), I want to be blocked after repeated failed login attempts against `/auth/login` or `/auth/customer/login`, so that brute-forcing account credentials is infeasible.

## Requirements

### Functional Requirements

- **FR-1**: `useOrdersWebSocket.ts` must read the auth token from the same storage key the Zustand auth store actually persists to (`'tablewise-auth'`), or the store must expose a single source of truth (e.g. a selector/getter) that both the store and the hook use, eliminating key-name drift as a class of bug.
- **FR-2**: The WebSocket connection must fail visibly (logged error / connection-state UI, not a silent no-op) if no valid auth token is available at connect time.
- **FR-3**: `backend/tests/utils/test_security.py` must assert against the current JWT claim name (`outlet_id`) rather than the removed `branch_id` claim, or the back-compat shim in `app/utils/jwt.py` must be made bidirectional if `branch_id` still needs support.
- **FR-4**: `backend/tests/tasks/test_celery.py` must reference an existing config value (or the test must be removed/updated) — no test may depend on a settings field that doesn't exist in `app/config.py`.
- **FR-5**: The `Settings` class (or wherever secrets are logged/printed on test failure) must not expose `POSTGRES_PASSWORD`, `SECRET_KEY`, or other sensitive fields in its string representation — use `repr=False` / `SecretStr` or equivalent field-level masking.
- **FR-6**: A frontend test runner (Vitest, consistent with the Vite toolchain already in use) must be added to `frontend/package.json` with a working `test` script.
- **FR-7**: At least one test must cover the corrected WebSocket auth-token lookup (FR-1), verifying the hook reads the token from the correct store key.
- **FR-8**: At least one test must cover a core existing user flow (e.g. cart/order submission) end-to-end at the component level, to establish the pattern for future test additions.
- **FR-9**: Rate limiting must be added to `/auth/login` and `/auth/customer/login` (e.g. via `slowapi` or equivalent FastAPI-compatible middleware), with a sensible default threshold (e.g. 5 failed attempts per IP per 15 minutes) and a clear 429 response.

### Non-Functional Requirements

- **Security**: No remediation step introduces a new secret-storage or auth bypass risk (e.g. rate-limit state must not itself leak credentials or be trivially bypassable via header spoofing without additional validation).
- **Reliability**: The full backend pytest suite must pass cleanly (no failing tests) after FR-3/FR-4 land; skipped tests should be confirmed to skip only for legitimate reasons (e.g. missing local Postgres), not silently masking broken coverage.
- **Performance**: Rate limiting must not introduce meaningful latency to legitimate login requests (limiter should be in-memory or Redis-backed, consistent with the existing Redis usage noted in the platform roadmap).

## Success Metrics

- WebSocket connections authenticate successfully in a manual staff-flow test (place an order as a customer, confirm it appears live on a staff/POS session) — 0 silent auth failures.
- `pytest` in `backend/` exits 0 with no failing tests (skips only where justified).
- `npm test` (or equivalent) runs successfully in `frontend/` with ≥2 passing tests (FR-7, FR-8).
- Repeated failed logins against `/auth/login` return HTTP 429 after the configured threshold, verified with a manual or scripted brute-force simulation.
- No secret values appear in test stdout/stderr across a full backend test run (manual grep of test output for known secret substrings).

## Open Questions / Risks

- **Root cause of the WebSocket key mismatch is unconfirmed** — it's unclear whether this is a recent regression (renamed store key without updating the hook) or has been broken since the hook was written. Worth a quick `git blame` before fixing, since it affects how urgently other WS-dependent code should be audited for the same drift.
- **Whether the 10 skipped backend tests are legitimately environment-gated** (e.g. require live Postgres) or are masking broken coverage was not confirmed during the audit — should be checked as part of FR-3/FR-4 work, since "green suite" is meaningless if half the tests don't actually run in CI.
- **Rate-limiter backend choice** (in-memory vs. Redis) depends on whether the app is expected to run multiple API replicas — the roadmap doc mentions scaling web replicas independently, which would make in-memory rate limiting ineffective across instances. Needs a decision before FR-9 implementation.
- **No timeline was set for this work** — the user did not confirm a deadline; treat as best-effort/prioritized-by-impact unless stated otherwise.
