#!/usr/bin/env bash
# ───────────────────────────────────────────────
#  TableWise – Container Entrypoint (Render)
#
#  1. Run Alembic migrations
#  2. If migrations succeed → start Uvicorn
#  3. If migrations fail   → log error, exit 1
# ───────────────────────────────────────────────
set -euo pipefail

echo "=========================================="
echo " TableWise – Starting Deployment"
echo "=========================================="

# ── Step 1: Run Alembic migrations ───────────
echo ""
echo "▶ Running database migrations (alembic upgrade head)..."
echo ""

if alembic upgrade head; then
    echo ""
    echo "✅  Migrations completed successfully."
    echo ""
else
    echo ""
    echo "❌  Migration FAILED. Aborting startup to prevent a broken deployment."
    echo "    Check the logs above for the specific Alembic error."
    echo ""
    exit 1
fi

# ── Step 2: Start the application ────────────
# Render injects $PORT (typically 10000); fall back to 8000 for local Docker.
PORT="${PORT:-8000}"

echo "▶ Starting Uvicorn on 0.0.0.0:${PORT} ..."
echo ""

exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port "${PORT}" \
    --workers 2 \
    --log-level info
