from __future__ import annotations

from dataclasses import dataclass

from .model import CPSState, ControlAction, ReviewDecision


@dataclass(frozen=True)
class SafetyAwareOperator:
    """Deterministic operator model for controlled HITL experiments.

    This is an experimental policy, not a model of real human behavior.
    """

    minimum_projected_margin: float = 0.25
    service_floor: float = 0.55

    def __call__(
        self,
        state: CPSState,
        proposed: ControlAction,
        actions: list[ControlAction],
    ) -> tuple[ReviewDecision, ControlAction]:
        projected_margin = state.safety_margin + proposed.safety_delta
        projected_service = state.service_quality + proposed.service_delta

        if projected_margin >= self.minimum_projected_margin and projected_service >= self.service_floor:
            return ReviewDecision.ACCEPT, proposed

        feasible = [
            action
            for action in actions
            if state.safety_margin + action.safety_delta >= self.minimum_projected_margin
            and state.service_quality + action.service_delta >= self.service_floor
        ]
        if feasible:
            replacement = min(feasible, key=lambda action: action.energy_cost)
            if replacement.name == proposed.name:
                return ReviewDecision.ACCEPT, proposed
            return ReviewDecision.MODIFY, replacement

        safest = max(actions, key=lambda action: action.safety_delta)
        return ReviewDecision.REJECT, safest


@dataclass(frozen=True)
class EnergyAwareOperator:
    """Select the lowest-energy action that respects explicit guardrails."""

    minimum_projected_margin: float = 0.10
    service_floor: float = 0.50

    def __call__(
        self,
        state: CPSState,
        proposed: ControlAction,
        actions: list[ControlAction],
    ) -> tuple[ReviewDecision, ControlAction]:
        feasible = [
            action
            for action in actions
            if state.safety_margin + action.safety_delta >= self.minimum_projected_margin
            and state.service_quality + action.service_delta >= self.service_floor
        ]
        if not feasible:
            return ReviewDecision.REJECT, max(actions, key=lambda action: action.safety_delta)
        selected = min(feasible, key=lambda action: action.energy_cost)
        decision = ReviewDecision.ACCEPT if selected.name == proposed.name else ReviewDecision.MODIFY
        return decision, selected
