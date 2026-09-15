# ADR-010: Separate deterministic CI evaluation from live-model evidence

## Status
Accepted for Phase 6.

## Decision
Use deterministic provider fixtures as a required release gate for software invariants, prompt/version control, policy safety, traces and structured-output contracts. Keep real-provider evaluation as an explicit opt-in harness with separately labeled reports.

## Rationale
A mocked green CI run cannot prove live-model quality, latency, cost, or provider reliability. Conversely, making routine CI depend on paid/nondeterministic provider calls creates flaky gates and secret-management risk. The two evidence classes answer different questions and must remain visibly separate.

## Consequences
The repository can make strong claims about deterministic governance invariants when CI is green. Claims about OpenAI, Anthropic or Gemini quality require retained live-provider evaluation evidence for the exact provider/model/prompt/dataset combination.
