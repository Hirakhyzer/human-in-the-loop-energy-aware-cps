from __future__ import annotations

from dataclasses import dataclass

from .model import CPSState, ControlAction


@dataclass(frozen=True)
class ParetoPoint:
    action: str
    energy_cost: float
    projected_safety_margin: float
    projected_service_quality: float


def action_point(state: CPSState, action: ControlAction) -> ParetoPoint:
    return ParetoPoint(
        action=action.name,
        energy_cost=action.energy_cost,
        projected_safety_margin=state.safety_margin + action.safety_delta,
        projected_service_quality=max(0.0, min(1.0, state.service_quality + action.service_delta)),
    )


def dominates(left: ParetoPoint, right: ParetoPoint) -> bool:
    """Return True when left is no worse in all objectives and better in one."""
    no_worse = (
        left.energy_cost <= right.energy_cost
        and left.projected_safety_margin >= right.projected_safety_margin
        and left.projected_service_quality >= right.projected_service_quality
    )
    strictly_better = (
        left.energy_cost < right.energy_cost
        or left.projected_safety_margin > right.projected_safety_margin
        or left.projected_service_quality > right.projected_service_quality
    )
    return no_worse and strictly_better


def pareto_front(state: CPSState, actions: list[ControlAction]) -> tuple[ParetoPoint, ...]:
    points = [action_point(state, action) for action in actions]
    front = [point for point in points if not any(dominates(other, point) for other in points if other != point)]
    return tuple(sorted(front, key=lambda point: (point.energy_cost, -point.projected_safety_margin)))
