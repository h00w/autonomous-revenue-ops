import hashlib
import hmac
import sqlite3
import time
from pathlib import Path
from typing import Callable


class WebhookSignatureError(ValueError):
    pass


class SQLiteReplayProtector:
    def __init__(self, path: str) -> None:
        self.path = path
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(path) as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS webhook_replays (replay_key TEXT PRIMARY KEY, expires_at REAL NOT NULL)"
            )

    def check_and_record(self, replay_key: str, expires_at: float, *, now: float | None = None) -> bool:
        current = now if now is not None else time.time()
        with sqlite3.connect(self.path) as conn:
            conn.execute("DELETE FROM webhook_replays WHERE expires_at <= ?", (current,))
            try:
                conn.execute(
                    "INSERT INTO webhook_replays(replay_key, expires_at) VALUES(?,?)",
                    (replay_key, expires_at),
                )
                return True
            except sqlite3.IntegrityError:
                return False


class WebhookVerifier:
    def __init__(
        self,
        secret: str,
        replay_protector: SQLiteReplayProtector,
        *,
        max_skew_seconds: int = 300,
        clock: Callable[[], float] = time.time,
    ) -> None:
        if not secret:
            raise ValueError("Webhook signing secret must not be empty")
        self.secret = secret.encode("utf-8")
        self.replay_protector = replay_protector
        self.max_skew_seconds = max_skew_seconds
        self.clock = clock

    def verify(self, body: bytes, timestamp: str, signature: str) -> None:
        try:
            ts = int(timestamp)
        except (TypeError, ValueError) as exc:
            raise WebhookSignatureError("Invalid webhook timestamp") from exc
        now = self.clock()
        if abs(now - ts) > self.max_skew_seconds:
            raise WebhookSignatureError("Webhook timestamp is outside the accepted window")
        supplied = signature.removeprefix("sha256=")
        expected = hmac.new(self.secret, timestamp.encode("utf-8") + b"." + body, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(supplied, expected):
            raise WebhookSignatureError("Webhook signature mismatch")
        replay_key = hashlib.sha256((timestamp + ":" + supplied).encode("utf-8")).hexdigest()
        if not self.replay_protector.check_and_record(
            replay_key,
            now + self.max_skew_seconds,
            now=now,
        ):
            raise WebhookSignatureError("Webhook replay detected")

    def sign(self, body: bytes, timestamp: str) -> str:
        digest = hmac.new(self.secret, timestamp.encode("utf-8") + b"." + body, hashlib.sha256).hexdigest()
        return f"sha256={digest}"
