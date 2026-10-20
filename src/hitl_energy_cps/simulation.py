from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Callable

from .model import CPSState, ControlAction, ReviewDecision
from .policy import ObjectiveWeights, SafetyConstraint, action_is_feasible, rank_actions
from .review import ReviewPolicy, should_request_human


@dataclass(frozen=True)
class SimulationConfig:
    steps: int = 24
    review_cost: float = 0.05
    minimum_safety_margin: float = 0.0
    minimum_service_quality: float = 0.0
    enforce_hard_constraints: bool = True

    def __post_init__(self) -> None:
        if self.steps < 1:
            raise ValueError("steps must be positive")
        if self.review_cost < 0:
            raise ValueError("review_cost must be non-negative")
        if not 0.0 <= self.minimum_service_quality <= 1.0:
            raise ValueError("minimum_service_quality must be within [0, 1]")


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
    constraint_fallback: bool = False
    safety_filter_intervened: bool = False


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
    constraint_fallbacks: int = 0
    safety_filter_interventions: int = 0


HumanPolicy = Callable[[CPSState, ControlAction, list[ControlAction]], tuple[ReviewDecision, ControlAction]]


def _advance(state: CPSState, action: ControlAction) -> CPSState:
    return replace(
        state,
        energy_demand=max(0.0, state.energy_demand - 0.03),
        safety_margin=state.safety_margin + action.safety_delta,
        service_quality=max(0.0, min(1.0, state.service_quality + action.service_delta)),
        urgency=max(0.0, state.urgency - 0.02),
    )


def _safest_fallback(state: CPSState, actions: list[ControlAction]) -> ControlAction:
    return max(
        actions,
        key=lambda action: (
            state.safety_margin + action.safety_delta,
            state.service_quality + action.service_delta,
            -action.energy_cost,
        ),
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
    reviews = modifications = rejections = unsafe_steps = fallbacks = safety_filters = 0
    constraint = SafetyConstraint(config.minimum_safety_margin, config.minimum_service_quality)

    for step in range(config.steps):
        all_ranked = rank_actions(state, actions, weights=weights)
        unconstrained_proposed = all_ranked[0].action
        constraint_fallback = False
        safety_filter_intervened = False
        if config.enforce_hard_constraints:
            feasible = [score for score in all_ranked if action_is_feasible(state, score.action, constraint)]
            if feasible:
                ranked = feasible
                safety_filter_intervened = ranked[0].action.name != unconstrained_proposed.name
                if safety_filter_intervened:
                    safety_filters += 1
            else:
                ranked = all_ranked
                constraint_fallback = True
                fallbacks += 1
        else:
            ranked = all_ranked

        proposed = ranked[0].action
        # Review the action that is actually proposed after automated guardrails.
        # This keeps human-review reasons aligned with the auditable proposal.
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
                applied = selected

        if config.enforce_hard_constraints and not action_is_feasible(state, applied, constraint):
            feasible_actions = [a for a in actions if action_is_feasible(state, a, constraint)]
            applied = min(feasible_actions, key=lambda a: a.energy_cost) if feasible_actions else _safest_fallback(state, actions)
            if not constraint_fallback:
                constraint_fallback = True
                fallbacks += 1

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
                constraint_fallback=constraint_fallback,
                safety_filter_intervened=safety_filter_intervened,
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
        constraint_fallbacks=fallbacks,
        safety_filter_interventions=safety_filters,
    )
