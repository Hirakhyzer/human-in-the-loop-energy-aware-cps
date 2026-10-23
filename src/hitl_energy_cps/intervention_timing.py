from __future__ import annotations

from dataclasses import dataclass
from math import floor, inf

from .model import CPSState, ControlAction
from .operator_state import OperatorState, operator_burden


@dataclass(frozen=True)
class InterventionTimingConfig:
    minimum_safety_margin: float = 0.0
    step_duration_s: float = 1.0
    planning_horizon_steps: int = 30
    preparation_buffer_s: float = 1.0

    def __post_init__(self) -> None:
        if self.step_duration_s <= 0:
            raise ValueError("step_duration_s must be positive")
        if self.planning_horizon_steps < 1:
            raise ValueError("planning_horizon_steps must be positive")
        if self.preparation_buffer_s < 0:
            raise ValueError("preparation_buffer_s must be non-negative")


@dataclass(frozen=True)
class InterventionTiming:
    request_now: bool
    steps_to_boundary: int | None
    time_to_boundary_s: float
    effective_human_latency_s: float
    latest_safe_request_s: float
    latest_safe_request_step: int | None
    slack_s: float
    status: str


def estimate_intervention_timing(
    state: CPSState,
    proposed: ControlAction,
    operator: OperatorState,
    *,
    config: InterventionTimingConfig = InterventionTimingConfig(),
) -> InterventionTiming:
    """Estimate when human review must be requested before safety is unrecoverable.

    The model projects repeated execution of the currently proposed action. It
    estimates the first step at which the projected safety margin is strictly
    below the configured boundary, then subtracts burden-adjusted operator
    response latency and an explicit preparation buffer.
    """
    burden = operator_burden(operator)
    available_margin = state.safety_margin - config.minimum_safety_margin

    if available_margin < 0:
        steps_to_boundary = 0
    elif proposed.safety_delta >= 0:
        steps_to_boundary = None
    else:
        loss_per_step = -proposed.safety_delta
        # Add a scale-aware tolerance so exact-boundary cases are not classified
        # as violations merely because of binary floating-point representation.
        tolerance = 1e-12 * max(1.0, abs(available_margin), loss_per_step)
        steps_to_boundary = floor((available_margin + tolerance) / loss_per_step) + 1

    if steps_to_boundary is None or steps_to_boundary > config.planning_horizon_steps:
        return InterventionTiming(
            request_now=False,
            steps_to_boundary=None,
            time_to_boundary_s=inf,
            effective_human_latency_s=burden.effective_latency_s,
            latest_safe_request_s=inf,
            latest_safe_request_step=None,
            slack_s=inf,
            status="outside-horizon",
        )

    time_to_boundary = steps_to_boundary * config.step_duration_s
    response_budget = burden.effective_latency_s + config.preparation_buffer_s
    latest_request = max(0.0, time_to_boundary - response_budget)
    latest_step = max(0, int(latest_request // config.step_duration_s))
    slack = time_to_boundary - response_budget
    request_now = slack <= config.step_duration_s

    if slack <= 0:
        status = "late-or-immediate"
    elif request_now:
        status = "request-now"
    else:
        status = "scheduled"

    return InterventionTiming(
        request_now=request_now,
        steps_to_boundary=steps_to_boundary,
        time_to_boundary_s=time_to_boundary,
        effective_human_latency_s=burden.effective_latency_s,
        latest_safe_request_s=latest_request,
        latest_safe_request_step=latest_step,
        slack_s=slack,
        status=status,
    )
