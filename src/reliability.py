import json
import sqlite3
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from threading import RLock
from typing import Any, Callable, TypeVar

from .integrations.errors import IntegrationError

T = TypeVar("T")


@dataclass(frozen=True)
class RetryPolicy:
    max_attempts: int = 3
    base_delay_seconds: float = 0.25
    max_delay_seconds: float = 5.0

    def delay_for(self, attempt: int, retry_after_seconds: float | None = None) -> float:
        if retry_after_seconds is not None:
            return min(max(retry_after_seconds, 0.0), self.max_delay_seconds)
        return min(self.base_delay_seconds * (2 ** max(attempt - 1, 0)), self.max_delay_seconds)


class CircuitState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"


class CircuitOpenError(RuntimeError):
    pass


class CircuitBreaker:
    def __init__(self, failure_threshold: int = 3, recovery_timeout_seconds: float = 30.0, *, clock: Callable[[], float] = time.monotonic) -> None:
        self.failure_threshold = failure_threshold
        self.recovery_timeout_seconds = recovery_timeout_seconds
        self.clock = clock
        self._lock = RLock()
        self._failures = 0
        self._opened_at: float | None = None

    @property
    def state(self) -> CircuitState:
        with self._lock:
            if self._opened_at is None:
                return CircuitState.CLOSED
            if self.clock() - self._opened_at >= self.recovery_timeout_seconds:
                return CircuitState.CLOSED
            return CircuitState.OPEN

    def before_call(self) -> None:
        with self._lock:
            if self._opened_at is None:
                return
            if self.clock() - self._opened_at >= self.recovery_timeout_seconds:
                self._opened_at = None
                self._failures = 0
                return
            raise CircuitOpenError("Circuit is open")

    def record_success(self) -> None:
        with self._lock:
            self._failures = 0
            self._opened_at = None

    def record_failure(self) -> None:
        with self._lock:
            self._failures += 1
            if self._failures >= self.failure_threshold:
                self._opened_at = self.clock()


class SQLiteDeadLetterQueue:
    def __init__(self, path: str) -> None:
        self.path = path
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS dead_letters (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    operation_key TEXT NOT NULL,
                    provider TEXT NOT NULL,
                    error_json TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    resolved_at REAL
                )
                """
            )

    def enqueue(self, operation_key: str, provider: str, error: IntegrationError, payload: dict[str, Any]) -> int:
        with sqlite3.connect(self.path) as conn:
            cursor = conn.execute(
                "INSERT INTO dead_letters(operation_key,provider,error_json,payload_json,created_at) VALUES(?,?,?,?,?)",
                (operation_key, provider, json.dumps(error.as_dict(), default=str), json.dumps(payload, default=str), time.time()),
            )
            return int(cursor.lastrowid)

    def unresolved(self) -> list[dict[str, Any]]:
        with sqlite3.connect(self.path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("SELECT * FROM dead_letters WHERE resolved_at IS NULL ORDER BY id").fetchall()
        return [dict(row) for row in rows]

    def resolve(self, item_id: int) -> None:
        with sqlite3.connect(self.path) as conn:
            conn.execute("UPDATE dead_letters SET resolved_at=? WHERE id=?", (time.time(), item_id))


def execute_with_recovery(
    operation: Callable[[], T],
    *,
    provider: str,
    operation_key: str,
    payload: dict[str, Any],
    retry_policy: RetryPolicy,
    circuit_breaker: CircuitBreaker,
    dead_letter_queue: SQLiteDeadLetterQueue,
    sleep: Callable[[float], None] = time.sleep,
) -> T:
    for attempt in range(1, retry_policy.max_attempts + 1):
        circuit_breaker.before_call()
        try:
            result = operation()
            circuit_breaker.record_success()
            return result
        except IntegrationError as exc:
            circuit_breaker.record_failure()
            if not exc.retryable or attempt >= retry_policy.max_attempts:
                dead_letter_queue.enqueue(operation_key, provider, exc, payload)
                raise
            sleep(retry_policy.delay_for(attempt, exc.retry_after_seconds))
    raise RuntimeError("unreachable")
