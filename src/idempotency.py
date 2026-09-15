import hashlib
import json
import threading
import time
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel


@dataclass
class _Entry:
    value: Any
    expires_at: float


class InMemoryIdempotencyStore:
    """Thread-safe TTL store used for Phase 1 local/runtime proof.

    A durable Redis/Postgres implementation is intentionally deferred to the
    reliability/deployment phases. The service interface is already isolated so
    storage can be replaced without changing policy or API contracts.
    """

    def __init__(self, ttl_seconds: int = 3600) -> None:
        self.ttl_seconds = ttl_seconds
        self._entries: dict[str, _Entry] = {}
        self._lock = threading.Lock()

    def get(self, key: str) -> Any | None:
        now = time.monotonic()
        with self._lock:
            entry = self._entries.get(key)
            if entry is None:
                return None
            if entry.expires_at <= now:
                self._entries.pop(key, None)
                return None
            return entry.value

    def put(self, key: str, value: Any) -> None:
        with self._lock:
            self._entries[key] = _Entry(
                value=value,
                expires_at=time.monotonic() + self.ttl_seconds,
            )

    def prune(self) -> int:
        now = time.monotonic()
        with self._lock:
            expired = [key for key, entry in self._entries.items() if entry.expires_at <= now]
            for key in expired:
                self._entries.pop(key, None)
            return len(expired)

    def __len__(self) -> int:
        self.prune()
        return len(self._entries)


def derive_idempotency_key(value: BaseModel) -> str:
    canonical = json.dumps(value.model_dump(mode="json"), sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return f"idem_{digest[:32]}"
