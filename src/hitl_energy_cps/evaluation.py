from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Outcome:
    energy_used: float
    safety_margin: float
    service_quality: float
    human_reviews: int = 0
    intervention_cost: float = 0.0


@dataclass(frozen=True)
class HITLComparison:
    autonomous_energy: float
    hitl_energy: float
    energy_saving: float
    safety_margin_delta: float
    service_quality_delta: float
    review_count: int
    intervention_cost: float
    human_intervention_value: float


def compare_outcomes(autonomous: Outcome, hitl: Outcome) -> HITLComparison:
    energy_saving = autonomous.energy_used - hitl.energy_used
    safety_delta = hitl.safety_margin - autonomous.safety_margin
    service_delta = hitl.service_quality - autonomous.service_quality

    human_value = (
        energy_saving
        + max(0.0, safety_delta)
        + max(0.0, service_delta)
        - hitl.intervention_cost
    )

    return HITLComparison(
        autonomous_energy=autonomous.energy_used,
        hitl_energy=hitl.energy_used,
        energy_saving=energy_saving,
        safety_margin_delta=safety_delta,
        service_quality_delta=service_delta,
        review_count=hitl.human_reviews,
        intervention_cost=hitl.intervention_cost,
        human_intervention_value=human_value,
    )
