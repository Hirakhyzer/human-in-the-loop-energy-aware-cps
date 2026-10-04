# Human-in-the-Loop Energy-Aware CPS Research Framework

## Motivation

Energy-optimal automation is not always operationally optimal. A controller may minimize energy while ignoring context that a human operator understands: urgency, comfort expectations, production priorities, equipment concerns, or unusual operating conditions.

At the same time, asking a human to review every decision defeats the purpose of automation and creates workload.

This repository studies the middle ground: **selective human involvement in energy-aware CPS control**.

## Research questions

### RQ1 — Energy benefit

Does human-in-the-loop control reduce total energy use compared with autonomy-only or human-only baselines?

### RQ2 — Safety preservation

Can HITL energy optimization preserve or improve safety margin while reducing energy consumption?

### RQ3 — Intervention value

Which human interventions produce enough benefit to justify their interruption and review cost?

### RQ4 — Review selectivity

Can the controller identify when human review is useful rather than requesting review indiscriminately?

### RQ5 — Operator workload

How does review frequency affect energy performance, decision latency, and simulated operator burden?

### RQ6 — Cross-domain generalization

Do review policies behave consistently across EV charging, smart buildings, and manufacturing?

## Experimental conditions

The benchmark program should compare:

1. autonomous baseline;
2. energy-prioritized automation;
3. human-only decision policy;
4. selective human-in-the-loop energy-aware control.

## Outcome categories

### Energy

- total energy use;
- energy saving relative to baseline;
- peak demand where applicable;
- energy per completed service/task.

### Safety

- minimum safety margin;
- number of unsafe proposals;
- number of human interventions preventing low-margin actions.

### Service

- service-quality score;
- task/comfort/charging objective satisfaction;
- degradation caused by excessive energy saving.

### Human factors

- review count;
- review rate;
- modification / rejection count;
- accumulated intervention cost;
- decision latency in future human studies.

## Human Intervention Value

The initial prototype uses an interpretable exploratory quantity:

```text
intervention value =
    energy saving
  + positive safety improvement
  + positive service improvement
  - human intervention cost
```

This is not intended as a universal utility function. The components use simplified scales and must be normalized and sensitivity-tested before quantitative comparisons are treated seriously.

## Threats to validity

- current domains are synthetic;
- current human behavior is not based on real operator data;
- objective scales are simplified;
- human review cost is an experimental abstraction;
- different domains may require non-comparable energy units;
- simulated intervention does not capture fatigue, trust, expertise, or organizational constraints.

## Scientific boundary

The project should report results as controlled simulation findings. It should not claim real-world energy savings, safety improvement, or human trust without external validation and human-subject evidence.
