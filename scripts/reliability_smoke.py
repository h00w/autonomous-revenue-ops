"""Local Phase 5 smoke test. It performs no network or SaaS calls."""

import json
import tempfile

from src.integrations.errors import IntegrationError, IntegrationErrorKind
from src.reliability import CircuitBreaker, RetryPolicy, SQLiteDeadLetterQueue, execute_with_recovery
from src.security.webhooks import SQLiteReplayProtector, WebhookVerifier


def main() -> None:
    with tempfile.TemporaryDirectory() as directory:
        attempts = {"count": 0}

        def operation():
            attempts["count"] += 1
            if attempts["count"] == 1:
                raise IntegrationError(
                    provider="synthetic",
                    kind=IntegrationErrorKind.TIMEOUT,
                    message="injected timeout",
                    retryable=True,
                )
            return "recovered"

        result = execute_with_recovery(
            operation,
            provider="synthetic",
            operation_key="smoke",
            payload={},
            retry_policy=RetryPolicy(max_attempts=2, base_delay_seconds=0),
            circuit_breaker=CircuitBreaker(failure_threshold=10),
            dead_letter_queue=SQLiteDeadLetterQueue(f"{directory}/dlq.sqlite3"),
            sleep=lambda _: None,
        )
        verifier = WebhookVerifier(
            "local-smoke-secret",
            SQLiteReplayProtector(f"{directory}/security.sqlite3"),
            max_skew_seconds=60,
            clock=lambda: 1000.0,
        )
        body = b"{}"
        verifier.verify(body, "1000", verifier.sign(body, "1000"))
        print(json.dumps({"status": "ok", "network_calls": 0, "attempts": attempts["count"], "result": result}))


if __name__ == "__main__":
    main()
