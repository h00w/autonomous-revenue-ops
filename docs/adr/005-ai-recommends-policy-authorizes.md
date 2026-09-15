# ADR-005: AI recommends; deterministic policy authorizes

## Status
Accepted

## Decision
The Research and Qualification agents may synthesize evidence and recommend qualification features. They may not authorize CRM writes, messages, email, or other external effects. Authorization remains in deterministic application policy (`src/policy.py`). The Outreach Drafting Agent is callable only after an authorized `PolicyResult` exists.

## Consequences
Model/provider changes cannot silently change the authorization mechanism. Agent output can be evaluated independently from policy behavior. Some apparently reasonable model actions will be withheld when policy requires review, which is intentional.
