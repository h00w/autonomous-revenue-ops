import pytest

from src.integrations.errors import IntegrationError, IntegrationErrorKind
from src.reliability import (
    CircuitBreaker,
    CircuitOpenError,
    CircuitState,
    RetryPolicy,
    SQLiteDeadLetterQueue,
    execute_with_recovery,
)


def _error(*, retryable: bool, retry_after: float | None = None) -> IntegrationError:
    return IntegrationError(
        provider="synthetic",
        kind=IntegrationErrorKind.TIMEOUT if retryable else IntegrationErrorKind.AUTHENTICATION,
        message="synthetic failure",
        retryable=retryable,
        retry_after_seconds=retry_after,
    )


def test_retry_policy_retries_only_retryable_failures(tmp_path):
    attempts = {"count": 0}
    sleeps = []

    def operation():
        attempts["count"] += 1
        if attempts["count"] < 3:
            raise _error(retryable=True)
        return "ok"

    result = execute_with_recovery(
        operation,
        provider="synthetic",
        operation_key="op_1",
        payload={"safe": True},
        retry_policy=RetryPolicy(max_attempts=3, base_delay_seconds=0.1),
        circuit_breaker=CircuitBreaker(failure_threshold=10),
        dead_letter_queue=SQLiteDeadLetterQueue(str(tmp_path / "dlq.sqlite3")),
        sleep=sleeps.append,
    )
    assert result == "ok"
    assert attempts["count"] == 3
    assert sleeps == [0.1, 0.2]


def test_non_retryable_failure_goes_directly_to_dlq(tmp_path):
    dlq = SQLiteDeadLetterQueue(str(tmp_path / "dlq.sqlite3"))
    with pytest.raises(IntegrationError):
        execute_with_recovery(
            lambda: (_ for _ in ()).throw(_error(retryable=False)),
            provider="synthetic",
            operation_key="op_auth",
            payload={"lead_id": "redacted"},
            retry_policy=RetryPolicy(max_attempts=3),
            circuit_breaker=CircuitBreaker(failure_threshold=10),
            dead_letter_queue=dlq,
            sleep=lambda _: None,
        )
    items = dlq.unresolved()
    assert len(items) == 1
    assert items[0]["operation_key"] == "op_auth"


def test_circuit_breaker_opens_and_recovers_after_timeout():
    now = {"value": 10.0}
    breaker = CircuitBreaker(failure_threshold=2, recovery_timeout_seconds=5.0, clock=lambda: now["value"])
    breaker.record_failure()
    breaker.record_failure()
    assert breaker.state == CircuitState.OPEN
    with pytest.raises(CircuitOpenError):
        breaker.before_call()
    now["value"] = 16.0
    breaker.before_call()
    assert breaker.state == CircuitState.CLOSED
