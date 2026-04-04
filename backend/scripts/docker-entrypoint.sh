#!/bin/sh
set -e

echo "[entrypoint] === Backend startup ==="
echo "[entrypoint] POSTGRES_HOST=${POSTGRES_HOST:-не задан}"
echo "[entrypoint] POSTGRES_PORT=${POSTGRES_PORT:-не задан}"
echo "[entrypoint] POSTGRES_DB=${POSTGRES_DB:-не задан}"
echo "[entrypoint] POSTGRES_USER=${POSTGRES_USER:-не задан}"

echo "[entrypoint] Step 1: ensure database exists..."
python scripts/ensure_postgres_database.py
EXIT=$?
if [ $EXIT -ne 0 ]; then
  echo "[entrypoint] FATAL: ensure_postgres_database failed (exit $EXIT). Остановка." >&2
  exit $EXIT
fi

echo "[entrypoint] Step 2: alembic migrate..."
alembic upgrade head

echo "[entrypoint] Step 3: starting uvicorn..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
