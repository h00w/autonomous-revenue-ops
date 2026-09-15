# ADR-011: Separate runtime measurement from business-impact scenarios

## Status
Accepted for Phase 7.

## Decision
Derive operational metrics only from persisted workflow runs and label them `measured_runtime`. Keep labor/cost/time-savings economics in a separate projection model labeled `scenario_projection` whose assumptions are explicit in the request and response.

## Rationale
Combining synthetic assumptions with observed system events makes portfolio ROI claims look stronger than the evidence supports. The two evidence classes answer different questions: runtime telemetry describes what the software recorded; scenario projections describe what a given operating model would imply.

## Consequences
The project can demonstrate business-impact modeling without presenting synthetic numbers as customer results. Any future measured ROI claim must be backed by audited inputs and a clearly defined measurement period.
