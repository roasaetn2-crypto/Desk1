#!/usr/bin/env bash
# Start command for hosted platforms (Render, Koyeb, Railway, Fly, VPS).
# The platform supplies $PORT. Never hardcode it.
set -euo pipefail
cd "$(dirname "$0")"

PORT="${PORT:-8000}"

# DESK_TOKEN must come from the platform's environment variables.
# If it is missing the desk would be OPEN to anyone with the link, so we
# refuse to start rather than silently expose your dashboard.
if [ -z "${DESK_TOKEN:-}" ]; then
  echo "FATAL: DESK_TOKEN is not set."
  echo "Add it as an environment variable in your host's dashboard."
  exit 1
fi

echo "Solana Desk starting on port $PORT (locked)"
exec python -m uvicorn app:app --host 0.0.0.0 --port "$PORT" --proxy-headers --forwarded-allow-ips='*'
