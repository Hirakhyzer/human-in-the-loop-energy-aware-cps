from __future__ import annotations

from dataclasses import dataclass

from .model import CPSState, ControlAction, DecisionScore


@dataclass(frozen=True)
class ObjectiveWeights:
    energy: float = 0.4
    safety: float = 0.4
    service: float = 0.2

    def __post_init__(self) -> None:
        total = self.energy + self.safety + self.service
        if total <= 0:
            raise ValueError("objective weights must sum to a positive value")


def score_action(
    state: CPSState,
    action: ControlAction,
    *,
    weights: ObjectiveWeights = ObjectiveWeights(),
) -> DecisionScore:
    total_weight = weights.energy + weights.safety + weights.service
    energy_score = 1.0 / (1.0 + action.energy_cost)
    projected_margin = state.safety_margin + action.safety_delta
    safety_score = max(0.0, min(1.0, 0.5 + projected_margin / 2.0))
    projected_service = state.service_quality + action.service_delta
    service_score = max(0.0, min(1.0, projected_service))

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


def choose_action(
    state: CPSState,
    actions: list[ControlAction],
    *,
    weights: ObjectiveWeights = ObjectiveWeights(),
) -> DecisionScore:
    if not actions:
        raise ValueError("at least one action is required")
    scored = [score_action(state, action, weights=weights) for action in actions]
    return max(scored, key=lambda item: item.total_score)
