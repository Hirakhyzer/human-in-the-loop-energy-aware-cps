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
python benchmarks/run_hitl_benchmark.py
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
