from __future__ import annotations

import json
from pathlib import Path

from hitl_energy_cps.domains import all_cases
from hitl_energy_cps.human_models import EnergyAwareOperator, SafetyAwareOperator
from hitl_energy_cps.simulation import SimulationConfig, run_simulation


def summarize(domain, autonomous, hitl, operator_name):
    return {
        "domain": domain,
        "operator": operator_name,
        "autonomous": {
            "energy": autonomous.total_energy,
            "minimum_safety_margin": autonomous.minimum_safety_margin,
            "service_quality": autonomous.final_service_quality,
            "unsafe_steps": autonomous.unsafe_steps,
        },
        "hitl": {
            "energy": hitl.total_energy,
            "minimum_safety_margin": hitl.minimum_safety_margin,
            "service_quality": hitl.final_service_quality,
            "unsafe_steps": hitl.unsafe_steps,
            "reviews": hitl.review_count,
            "modifications": hitl.modification_count,
            "rejections": hitl.rejection_count,
            "intervention_cost": hitl.intervention_cost,
        },
        "delta": {
            "energy_saved": autonomous.total_energy - hitl.total_energy,
            "safety_margin": hitl.minimum_safety_margin - autonomous.minimum_safety_margin,
            "service_quality": hitl.final_service_quality - autonomous.final_service_quality,
            "unsafe_steps_prevented": autonomous.unsafe_steps - hitl.unsafe_steps,
        },
    }


def main() -> None:
    config = SimulationConfig(steps=24, review_cost=0.05)
    operators = {
        "safety-aware": SafetyAwareOperator(),
        "energy-aware": EnergyAwareOperator(),
    }
    rows = []

    for domain, (state, actions) in all_cases().items():
        autonomous = run_simulation(state, actions, config=config)
        for name, operator in operators.items():
            hitl = run_simulation(state, actions, config=config, human_policy=operator)
            rows.append(summarize(domain, autonomous, hitl, name))

    payload = {
        "experiment": "paired-autonomous-vs-hitl-v1",
        "steps": config.steps,
        "note": "Synthetic operator policies; results are simulation evidence only.",
        "comparisons": rows,
    }
    output = Path("artifacts/paired-hitl-benchmark.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
