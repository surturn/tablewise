# ───────────────────────────────────────────────
#  TableWise – Production Dockerfile (Render)
# ───────────────────────────────────────────────
FROM python:3.12-slim

# Prevent Python from writing .pyc files & enable unbuffered stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# ── System deps (pg_isready for optional health checks, curl for debugging) ──
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       libpq-dev gcc curl \
    && rm -rf /var/lib/apt/lists/*

# ── Python deps ──
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# ── App source ──
COPY . .

# ── Entrypoint script ──
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]