"""Device registry: which physical devices may open the desk without a key.

A "device" is a browser that completed pairing once. It holds a long-lived
random token in an HttpOnly cookie; only the SHA-256 of that token is stored
on disk, so a stolen desk_devices.json cannot be replayed.

    desk_devices.json
    {
      "devices": [
        {"id": "ab12", "name": "Pixel 7", "hash": "…", "created": "…", "last_seen": "…"}
      ]
    }
"""
from __future__ import annotations

import hashlib
import json
import secrets
import threading
from datetime import datetime, timezone
from pathlib import Path

DEVICES = Path(__file__).resolve().parent.parent / "desk_devices.json"
_lock = threading.Lock()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _hash(token: str) -> str:
    return hashlib.sha256(("device::" + token).encode()).hexdigest()


def _load() -> dict:
    if not DEVICES.exists():
        return {"devices": []}
    try:
        return json.loads(DEVICES.read_text())
    except (json.JSONDecodeError, OSError):
        return {"devices": []}


def _save(data: dict) -> None:
    DEVICES.write_text(json.dumps(data, indent=2))


def pair(name: str) -> tuple[str, dict]:
    """Create a device and return (raw_token, record). Raw token is shown once."""
    token = secrets.token_urlsafe(32)
    rec = {
        "id": secrets.token_hex(3),
        "name": (name or "unnamed device").strip()[:40],
        "hash": _hash(token),
        "created": _now(),
        "last_seen": _now(),
    }
    with _lock:
        data = _load()
        data["devices"].append(rec)
        _save(data)
    return token, rec


def verify(token: str) -> dict | None:
    """Return the device record if the token matches one, else None."""
    if not token:
        return None
    want = _hash(token)
    with _lock:
        data = _load()
        for rec in data["devices"]:
            if secrets.compare_digest(rec.get("hash", ""), want):
                rec["last_seen"] = _now()
                _save(data)
                return rec
    return None


def listing() -> list[dict]:
    """Public view: never exposes hashes."""
    return [
        {k: v for k, v in rec.items() if k != "hash"}
        for rec in _load()["devices"]
    ]


def revoke(device_id: str) -> bool:
    with _lock:
        data = _load()
        before = len(data["devices"])
        data["devices"] = [r for r in data["devices"] if r.get("id") != device_id]
        changed = len(data["devices"]) != before
        if changed:
            _save(data)
    return changed


def count() -> int:
    return len(_load()["devices"])
