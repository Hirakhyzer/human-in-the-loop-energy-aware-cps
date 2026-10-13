from __future__ import annotations

from dataclasses import dataclass

from .model import CPSState, ControlAction, DecisionScore


@dataclass(frozen=True)
class ObjectiveWeights:
    energy: float = 0.4
    safety: float = 0.4
    service: float = 0.2

    def __post_init__(self) -> None:
        if any(value < 0 for value in (self.energy, self.safety, self.service)):
            raise ValueError("objective weights must be non-negative")
        if self.energy + self.safety + self.service <= 0:
            raise ValueError("objective weights must sum to a positive value")


@dataclass(frozen=True)
class SafetyConstraint:
    minimum_projected_margin: float = 0.0
    minimum_projected_service: float = 0.0


def projected_safety_margin(state: CPSState, action: ControlAction) -> float:
    return state.safety_margin + action.safety_delta


def projected_service_quality(state: CPSState, action: ControlAction) -> float:
    return max(0.0, min(1.0, state.service_quality + action.service_delta))


def action_is_feasible(
    state: CPSState,
    action: ControlAction,
    constraint: SafetyConstraint = SafetyConstraint(),
) -> bool:
    return (
        projected_safety_margin(state, action) >= constraint.minimum_projected_margin
        and projected_service_quality(state, action) >= constraint.minimum_projected_service
    )


def score_action(
    state: CPSState,
    action: ControlAction,
    *,
    weights: ObjectiveWeights = ObjectiveWeights(),
) -> DecisionScore:
    total_weight = weights.energy + weights.safety + weights.service
    energy_score = 1.0 / (1.0 + action.energy_cost)
    projected_margin = projected_safety_margin(state, action)
    safety_score = max(0.0, min(1.0, 0.5 + projected_margin / 2.0))
    service_score = projected_service_quality(state, action)

    total_score = (
        weights.energy * energy_score
        + weights.safety * safety_score
        + weights.service * service_score
    ) / total_weight

    return DecisionScore(
        action=action,
        energy_score=energy_score,
        safety_score=safety_score,
        service_score=service_score,
        total_score=total_score,
    )


def rank_actions(
    state: CPSState,
    actions: list[ControlAction],
    *,
    weights: ObjectiveWeights = ObjectiveWeights(),
    constraint: SafetyConstraint | None = None,
) -> list[DecisionScore]:
    if not actions:
        raise ValueError("at least one action is required")
    candidates = actions
    if constraint is not None:
        candidates = [action for action in actions if action_is_feasible(state, action, constraint)]
        if not candidates:
            raise ValueError("no action satisfies the hard safety/service constraints")
    return sorted(
        (score_action(state, action, weights=weights) for action in candidates),
        key=lambda item: item.total_score,
        reverse=True,
    )


def choose_action(
    state: CPSState,
    actions: list[ControlAction],
    *,
    weights: ObjectiveWeights = ObjectiveWeights(),
    constraint: SafetyConstraint | None = None,
) -> DecisionScore:
    return rank_actions(state, actions, weights=weights, constraint=constraint)[0]
