# Grand Platform Refactor Roadmap

Grand Platform is a unified hospitality management system for a hotel property in Juba, South Sudan. It combines a public guest web app and a private operations dashboard on one backend, one PostgreSQL database, and one payment orchestration layer.

## Product scope

- **Hotel room management:** room browsing, real-time availability, online booking, check-in/check-out, housekeeping, room status, walk-in bookings, and occupancy reporting.
- **Restaurant ordering:** menu, cart, Stripe card checkout, cash fallback, mobile money fallback, KDS, order tracking, rider dispatch, table QR ordering, and Africa's Talking SMS updates.
- **Bar management:** QR/tablet ordering, open tabs, bill splitting, par-level stock alerts, and bar sales analytics.
- **AI intelligence:** Celery-run OpenAI tasks for 7-day demand forecasting, Monday reorder lists, menu performance, anomaly detection, and owner morning briefing.

## Refactor responses to identified gaps

| Gap | Refactor response |
| --- | --- |
| Stripe unavailable in Kenya | Switched to M-Pesa (Safaricom Daraja STK Push) as the primary payment rail, keep cash-on-delivery/front-desk settlement, and route future providers (e.g. a global card processor once selected) through the same provider abstraction. |
| Lack of offline functionality | Use persisted cart state in the public UI now; next POS phase adds IndexedDB order queue, offline order IDs, batch sync, and conflict resolution. |
| AI lacks validation | AI outputs must validate against typed schemas, confidence thresholds, bounded horizons, USD currency, and data-quality notes before workflows use them. |
| Limited infrastructure scaling plan | Run FastAPI, Celery workers, Redis, PostgreSQL, and frontend separately; scale web and worker replicas independently behind Cloudflare CDN. |
| No compliance details | Treat PCI scope through Stripe-hosted checkout, keep audit logs for sensitive staff actions, encrypt secrets, and define South Sudan/East Africa SMS/payment consent retention. |
| Weak continuity planning | Maintain cash/offline workflows, Redis/Celery retry policies, PostgreSQL backups, provider fallbacks, incident runbooks, and daily restore checks. |

## Offline-first POS plan

1. Generate client-side `offline_order_id` values with the configured prefix.
2. Store open tables, bar tabs, KDS acknowledgements, and cash orders in IndexedDB.
3. Sync batches to FastAPI when connectivity returns using `OFFLINE_SYNC_BATCH_SIZE`.
4. Resolve conflicts by outlet, device ID, staff user, and monotonic local sequence.
5. Mark synced orders immutable except for status transitions and reconciliation notes.

## Payment plan

- **M-Pesa:** primary payment rail via Safaricom Daraja STK Push (phone-number-initiated, server-confirmed via callback). Amounts still tracked in USD cents internally; STK push converts to KES at request time.
- **Cash:** fallback for delivery, reception, and table-close settlement.
- **Future providers:** a global card processor is still being researched (Stripe doesn't serve Kenya) — the payment service is structured so a new provider is a new service module plus a `PaymentMethod` enum value, not a rewrite.
- **Reconciliation:** every `Payment` stores method, status, provider reference (`mpesa_checkout_request_id`/`mpesa_receipt_number`), phone number, and audit log entries for matching.

## AI data and accuracy framework

- OpenAI tasks run on Celery and never block request/checkout paths.
- Inputs must come from validated bookings, orders, inventory movements, and payments.
- Outputs are schema-validated and must include confidence scores and data-quality notes.
- Recommendations below the confidence threshold require manager review instead of automatic reorder.
- Forecast accuracy should be reviewed weekly using MAPE by outlet/module and item category.

## Infrastructure scaling plan

- **Phase 1:** Docker Compose for local/dev parity.
- **Phase 2:** Railway/Render services for web API, frontend, Redis, Celery worker, and Celery beat.
- **Phase 3:** Managed PostgreSQL read replica for reporting, Cloudflare CDN/WAF, Sentry alerts, Uptime Robot checks, and worker autoscaling by queue depth.
- **Phase 4:** Multi-region backup restore target for continuity, plus object storage for room/menu images.

## Compliance and controls

- Stripe-hosted Checkout reduces PCI exposure; do not store card PAN/CVV.
- RBAC gates owner, manager, chef, rider, receptionist, and guest capabilities at API middleware.
- Store all amounts in USD minor units for new tables and migrations.
- Keep audit logs for price changes, refunds, discounts, voids, staff changes, check-ins, and room status overrides.
- Document SMS opt-in, retention, deletion requests, and access reviews before production launch.

## Disaster recovery and business continuity

- Daily PostgreSQL backups with monthly restore drills.
- Redis is treated as ephemeral; Celery tasks must be idempotent and retry-safe.
- Cash/offline POS allows trading during Stripe/mobile-money/network outages.
- Cloudflare caches static frontend assets; Uptime Robot and Sentry notify owner/technical lead.
- Incident runbook should define RTO of 4 hours for core ordering/check-in and RPO of 24 hours for transactional data until managed PITR is enabled.

## ROI and financial projections to add

Track ROI against the current Jipos/Glovo replacement costs:

- Monthly software/vendor savings.
- Reduced commission leakage from direct ordering.
- Higher room occupancy from direct booking conversion.
- Bar/restaurant margin uplift from AI reorder and waste reduction.
- Labor savings from KDS, QR ordering, and automated reports.
- Payback period, 12-month cash-flow projection, and sensitivity analysis for transaction volume, room occupancy, and average order value.
