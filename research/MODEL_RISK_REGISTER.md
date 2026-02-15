# Model Risk Register

## High Risks

1. **Competitive response calibration gap**
   - Risk: response penalties are assumption-led rather than estimated from German post-entry data.
   - Impact: strategy ranking may over/understate downside resilience.
   - Mitigation: calibrate using observed competitor price reactions in pilot cities.

2. **Data refresh parser fragility**
   - Risk: source HTML layouts change and parsers miss values.
   - Impact: stale defaults remain active silently if not monitored.
   - Mitigation: monitor `data/latest_inputs.json` check statuses and parser error counts each run.

3. **Behavioral parameter transferability**
   - Risk: current adoption parameters may not transfer perfectly to specific city micro-markets.
   - Impact: conversion and spend projections biased.
   - Mitigation: Bayesian update from real sign-up and basket panel data.

## Medium Risks

1. **Capex assumptions**
   - Risk: all-in warehouse capex may differ by municipality and permit complexity.
   - Mitigation: city-specific capex book and real-estate scenario envelopes.

2. **Scenario probabilities**
   - Risk: probability weights can materially alter risk-adjusted rankings.
   - Mitigation: run quarterly scenario-weight workshops with finance and macro teams.

## Controls Checklist (Before Board Use)

1. Confirm source refresh status and overrides.
2. Confirm no high-severity compliance findings unresolved.
3. Confirm NPV model assumptions reviewed by finance lead.
4. Confirm sensitivity charts include downside and tail metrics (CVaR/probability of loss).
