#!/usr/bin/env bash
# Starts the FastAPI backend, waits for it to be healthy, then runs the
# Flutter frontend in Chrome. Stops the backend when the frontend exits.
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")"

BACKEND_LOG="$(mktemp -t agri_rag_backend_log)"
WEB_PORT="${WEB_PORT:-8765}"

echo "Starting backend (log: $BACKEND_LOG)..."
.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload \
  > "$BACKEND_LOG" 2>&1 &
BACKEND_PID=$!

cleanup() {
  echo "Stopping backend (pid $BACKEND_PID)..."
  kill "$BACKEND_PID" 2>/dev/null || true
}
trap cleanup EXIT

echo "Waiting for backend to become healthy..."
for _ in $(seq 1 60); do
  if curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/health | grep -q 200; then
    echo "Backend is up."
    break
  fi
  if ! kill -0 "$BACKEND_PID" 2>/dev/null; then
    echo "Backend process exited early. Last log lines:"
    tail -n 40 "$BACKEND_LOG"
    exit 1
  fi
  sleep 1
done

echo "Starting frontend on http://localhost:$WEB_PORT ..."
(cd frontend && flutter run -d chrome --web-port="$WEB_PORT")
