# Business Impact Methodology

The project deliberately separates measured runtime evidence from scenario-based business impact.

## Scenario projection

`POST /v1/analytics/impact` accepts explicit assumptions:

- workflows per month;
- manual minutes per workflow;
- automation rate;
- loaded hourly cost;
- automation cost per automated workflow;
- currency label.

It returns `evidence_class=scenario_projection` with baseline manual hours, remaining manual hours, hours avoided, capacity value, automation operating cost, and net capacity value.

## What the projection does not claim

The calculator does **not** infer or claim customer ROI. It does not infer revenue uplift, sales conversion improvement, opportunity cost, implementation cost, tax, discount rate, staffing reductions, or causal impact. Those require real operational/customer evidence.

A portfolio/demo can show how the economics are calculated, but synthetic inputs must remain labeled as scenarios. A future customer deployment may replace assumptions with audited measurements; only then can the resulting business outcome be described as measured.
