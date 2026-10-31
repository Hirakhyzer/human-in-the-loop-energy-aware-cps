# Human-in-the-Loop Energy-Aware CPS

**Balancing energy efficiency, autonomy, safety, and human judgment in cyber-physical systems.**

This repository studies how human feedback can improve energy-aware control decisions in cyber-physical systems without sacrificing safety, operational performance, or transparency.

## Core research question

> **Can human feedback improve the energy efficiency of autonomous CPS decisions while preserving safety, performance, and operator trust?**

## Research idea

The framework models a CPS controller that proposes actions using energy, safety, and performance objectives, then selectively involves a human operator when decisions are uncertain, safety-critical, or likely to benefit from domain judgment.

```text
Sensors / CPS
      ↓
Digital Twin
      ↓
State + Energy Estimation
      ↓
Energy-Aware Decision Engine
      ↓
Human Review Policy
  ↙       ↓       ↘
Accept   Modify   Reject
  ↘       ↓       ↙
Applied Control Action
      ↓
Energy + Safety + Human Feedback
      ↓
Evaluation / Adaptation
```

## Initial capabilities

- reusable CPS state and action abstractions;
- energy, safety, and performance objective scoring;
- human-review trigger policies;
- accept / modify / reject operator decisions;
- intervention-cost accounting;
- paired autonomous-vs-HITL evaluation;
- human-intervention-value metrics;
- deterministic benchmark scenarios;
- reproducible experiment artifacts.

## Intervention-timing semantics

The intervention-timing module projects when repeated use of a proposed action would first cross the configured safety boundary and subtracts burden-adjusted human response time plus an explicit preparation buffer.

- `scheduled` means there is a positive request window before the modeled deadline.
- `request-now` means a request at the current instant is still feasible but little or no slack remains.
- `no-feasible-request-window` means the modeled response budget is already longer than the time remaining to the predicted safety boundary. In this case `latest_safe_request_s` and `latest_safe_request_step` are `None`; the framework does **not** report time zero as if an on-time human response were still possible.
- `outside-horizon` means no degrading boundary is predicted inside the configured planning horizon.

These timing results are properties of the reduced-order model and configured human-response abstraction; they are not deployment-level safety guarantees.

## Initial domains

The first benchmark suite focuses on three synthetic reduced-order domains:

- **EV charging** — balance charging energy, urgency, and safety constraints;
- **smart building HVAC** — balance thermal comfort, power demand, and operator preferences;
- **smart manufacturing** — balance machine energy, throughput, and human production priorities.

These are controlled research models, not validated operational plants.

## Research boundary

This repository is a research prototype. It does not claim that simulated human feedback represents all real operators, and it does not claim deployment-level safety or energy savings without external validation.

## Quick start

```bash
python -m pip install -e ".[dev]"
pytest -q
python examples/run_demo.py
python benchmarks/run_paired_experiment.py
```

## Planned research tracks

1. **Human intervention value** — when is asking a person worth the interruption cost?
2. **Energy-safety Pareto analysis** — how much efficiency is gained before safety margin or service quality degrades?
3. **Adaptive review policies** — can review requests become more selective over time?
4. **Human disagreement analysis** — when do operator decisions systematically differ from energy-optimal automation?
5. **Workload-aware HITL control** — can the system avoid overloading operators during high-event periods?
6. **Cross-domain robustness** — do HITL policies generalize across CPS domains?

## License

MIT
