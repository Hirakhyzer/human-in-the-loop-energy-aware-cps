from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Callable

from .model import CPSState, ControlAction, ReviewDecision
from .policy import ObjectiveWeights, score_action
from .review import ReviewPolicy, should_request_human


@dataclass(frozen=True)
class SimulationConfig:
    steps: int = 24
    review_cost: float = 0.05
    minimum_safety_margin: float = 0.0

    def __post_init__(self) -> None:
        if self.steps < 1:
            raise ValueError("steps must be positive")
        if self.review_cost < 0:
            raise ValueError("review_cost must be non-negative")


@dataclass(frozen=True)
class StepRecord:
    step: int
    proposed_action: str
    applied_action: str
    review_required: bool
    review_decision: str | None
    review_reasons: tuple[str, ...]
    energy_used: float
    safety_margin: float
    service_quality: float
    unsafe: bool


@dataclass(frozen=True)
class SimulationResult:
    domain: str
    records: tuple[StepRecord, ...]
    total_energy: float
    minimum_safety_margin: float
    final_service_quality: float
    review_count: int
    modification_count: int
    rejection_count: int
    unsafe_steps: int
    intervention_cost: float


HumanPolicy = Callable[[CPSState, ControlAction, list[ControlAction]], tuple[ReviewDecision, ControlAction]]


def _advance(state: CPSState, action: ControlAction) -> CPSState:
    return replace(
        state,
        energy_demand=max(0.0, state.energy_demand - 0.03),
        safety_margin=state.safety_margin + action.safety_delta,
        service_quality=max(0.0, min(1.0, state.service_quality + action.service_delta)),
        urgency=max(0.0, state.urgency - 0.02),
    )


def run_simulation(
    initial_state: CPSState,
    actions: list[ControlAction],
    *,
    config: SimulationConfig = SimulationConfig(),
    weights: ObjectiveWeights = ObjectiveWeights(),
    review_policy: ReviewPolicy = ReviewPolicy(),
    human_policy: HumanPolicy | None = None,
) -> SimulationResult:
    if not actions:
        raise ValueError("at least one action is required")

    state = initial_state
    records: list[StepRecord] = []
    total_energy = 0.0
    reviews = modifications = rejections = unsafe_steps = 0

    for step in range(config.steps):
        ranked = sorted(
            (score_action(state, action, weights=weights) for action in actions),
            key=lambda item: item.total_score,
            reverse=True,
        )
        proposed = ranked[0].action
        review = should_request_human(state, ranked, policy=review_policy)
        applied = proposed
        decision: ReviewDecision | None = None

        if review.required and human_policy is not None:
            reviews += 1
            decision, selected = human_policy(state, proposed, actions)
            if decision == ReviewDecision.MODIFY:
                modifications += 1
                applied = selected
            elif decision == ReviewDecision.REJECT:
                rejections += 1
                # A rejected proposal uses the lowest-energy action among those
                # that do not reduce the current safety margin, when available.
                feasible = [a for a in actions if a.safety_delta >= 0.0]
                applied = min(feasible or actions, key=lambda a: a.energy_cost)

        state = _advance(state, applied)
        total_energy += applied.energy_cost
        unsafe = state.safety_margin < config.minimum_safety_margin
        unsafe_steps += int(unsafe)
        records.append(
            StepRecord(
                step=step,
                proposed_action=proposed.name,
                applied_action=applied.name,
                review_required=review.required,
                review_decision=decision.value if decision else None,
                review_reasons=review.reasons,
                energy_used=applied.energy_cost,
                safety_margin=state.safety_margin,
                service_quality=state.service_quality,
                unsafe=unsafe,
            )
        )

    return SimulationResult(
        domain=initial_state.domain,
        records=tuple(records),
        total_energy=total_energy,
        minimum_safety_margin=min(r.safety_margin for r in records),
        final_service_quality=state.service_quality,
        review_count=reviews,
        modification_count=modifications,
        rejection_count=rejections,
        unsafe_steps=unsafe_steps,
        intervention_cost=reviews * config.review_cost,
    )
