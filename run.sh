#!/usr/bin/env bash
# Start the Solana Desk. Works on a machine that has never run it before.
#
#   ./run.sh              -> random key, printed once. Pair your phone, others need the key.
#   ./run.sh mypassword   -> use your own key
#   ./run.sh --open       -> no lock at all (anyone who can reach the port gets in)
#
# Nothing here talks to the internet except pip, once, to install the deps.
set -euo pipefail
cd "$(dirname "$0")"

PORT="${PORT:-8000}"

# ---------- find a python ----------
PY=""
for cand in python3 python; do
  if command -v "$cand" >/dev/null 2>&1; then
    if "$cand" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3,10) else 1)' 2>/dev/null; then
      PY="$cand"; break
    fi
  fi
done
if [ -z "$PY" ]; then
  echo "ERROR: need Python 3.10 or newer."
  echo "  macOS:   brew install python"
  echo "  Debian:  sudo apt install python3 python3-pip"
  echo "  Windows: https://python.org/downloads  (tick 'Add to PATH')"
  exit 1
fi

# ---------- install deps if missing ----------
if ! "$PY" -c 'import fastapi, uvicorn, pydantic, requests' 2>/dev/null; then
  echo "First run: installing dependencies (one time, ~30 seconds)..."
  "$PY" -m pip install --quiet --upgrade pip >/dev/null 2>&1 || true
  if ! "$PY" -m pip install --quiet -r requirements.txt; then
    echo "ERROR: pip install failed. On Debian/Ubuntu try:"
    echo "  sudo apt install python3-venv && python3 -m venv .venv && . .venv/bin/activate"
    echo "  pip install -r requirements.txt"
    exit 1
  fi
  echo "Dependencies installed."
fi

# ---------- optional: live signing ----------
if ! "$PY" -c 'import solders, base58' 2>/dev/null; then
  "$PY" -m pip install --quiet -r requirements-live.txt >/dev/null 2>&1 || true
fi
if "$PY" -c 'import solders, base58' 2>/dev/null; then
  LIVE_SIGN="available"
else
  LIVE_SIGN="unavailable (paper only) - pip install -r requirements-live.txt"
fi

# ---------- lock ----------
if [ "${1:-}" = "--open" ]; then
  echo "=============================================================="
  echo "  WARNING: desk is OPEN. Anyone who can reach port $PORT"
  echo "  can read state and press Start / Reset / Kill."
  echo "=============================================================="
  unset DESK_TOKEN || true
elif [ -n "${1:-}" ]; then
  export DESK_TOKEN="$1"
else
  export DESK_TOKEN="$("$PY" -c 'import secrets; print(secrets.token_urlsafe(18))')"
fi

if [ -n "${DESK_TOKEN:-}" ]; then
  PAIRED="$("$PY" - <<'PY' 2>/dev/null || echo 0
import json, pathlib
p = pathlib.Path("desk_devices.json")
print(len(json.loads(p.read_text())["devices"]) if p.exists() else 0)
PY
)"
  echo "=============================================================="
  echo "  Solana Desk is LOCKED"
  echo ""
  echo "  Open:  http://localhost:$PORT"
  echo "  Key:   $DESK_TOKEN"
  echo "  Paired devices: $PAIRED"
  echo ""
  echo "  On your phone: open the URL, then 'Pair this device'."
  echo "  After that the phone opens with no key. Every other device"
  echo "  still needs the key above."
  echo ""
  echo "  Manage devices: http://localhost:$PORT/devices"
  echo "  Live signing:   $LIVE_SIGN"
  echo "=============================================================="
fi

exec "$PY" -m uvicorn app:app --host 0.0.0.0 --port "$PORT"
