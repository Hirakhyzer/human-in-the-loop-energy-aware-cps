from math import isinf

import pytest

from hitl_energy_cps.intervention_timing import InterventionTimingConfig, estimate_intervention_timing
from hitl_energy_cps.model import CPSState, ControlAction
from hitl_energy_cps.operator_state import OperatorState


def test_degrading_action_produces_latest_safe_request_window():
    state = CPSState("test", energy_demand=0.5, safety_margin=0.5, service_quality=0.9)
    action = ControlAction("degrading", energy_cost=0.1, safety_delta=-0.1, service_delta=0.0)
    timing = estimate_intervention_timing(
        state,
        action,
        OperatorState(response_latency_s=2.0),
        config=InterventionTimingConfig(step_duration_s=1.0, preparation_buffer_s=1.0),
    )
    # Exactly reaching zero at step five is still on the configured boundary;
    # the first strict violation occurs at step six.
    assert timing.steps_to_boundary == 6
    assert timing.time_to_boundary_s == 6.0
    assert timing.latest_safe_request_s == 3.0
    assert timing.latest_safe_request_step == 3
    assert timing.status == "scheduled"


def test_slow_or_burdened_operator_reports_no_feasible_request_window():
    state = CPSState("test", energy_demand=0.5, safety_margin=0.2, service_quality=0.9)
    action = ControlAction("degrading", energy_cost=0.1, safety_delta=-0.1, service_delta=0.0)
    timing = estimate_intervention_timing(
        state,
        action,
        OperatorState(workload=1.0, fatigue=1.0, response_latency_s=2.0),
        config=InterventionTimingConfig(step_duration_s=1.0, preparation_buffer_s=1.0),
    )
    assert timing.request_now
    assert timing.status == "no-feasible-request-window"
    assert timing.latest_safe_request_s is None
    assert timing.latest_safe_request_step is None
    assert timing.slack_s < 0.0


def test_non_degrading_action_has_no_intervention_deadline_in_horizon():
    state = CPSState("test", energy_demand=0.5, safety_margin=0.2, service_quality=0.9)
    action = ControlAction("recover", energy_cost=0.2, safety_delta=0.05, service_delta=0.0)
    timing = estimate_intervention_timing(state, action, OperatorState(response_latency_s=2.0))
    assert timing.steps_to_boundary is None
    assert isinf(timing.latest_safe_request_s)
    assert not timing.request_now


def test_existing_safety_violation_has_no_feasible_request_window():
    state = CPSState("test", energy_demand=0.5, safety_margin=-0.1, service_quality=0.9)
    action = ControlAction("hold", energy_cost=0.1, safety_delta=0.0, service_delta=0.0)
    timing = estimate_intervention_timing(state, action, OperatorState(response_latency_s=1.0))
    assert timing.steps_to_boundary == 0
    assert timing.request_now
    assert timing.status == "no-feasible-request-window"
    assert timing.latest_safe_request_s is None
    assert timing.latest_safe_request_step is None


def test_exact_zero_slack_is_a_feasible_immediate_request():
    state = CPSState("test", energy_demand=0.5, safety_margin=0.2, service_quality=0.9)
    action = ControlAction("degrading", energy_cost=0.1, safety_delta=-0.1, service_delta=0.0)
    timing = estimate_intervention_timing(
        state,
        action,
        OperatorState(response_latency_s=2.0),
        config=InterventionTimingConfig(step_duration_s=1.0, preparation_buffer_s=1.0),
    )
    assert timing.steps_to_boundary == 3
    assert timing.slack_s == pytest.approx(0.0)
    assert timing.latest_safe_request_s == pytest.approx(0.0)
    assert timing.latest_safe_request_step == 0
    assert timing.status == "request-now"


def test_timing_config_rejects_fractional_horizon_steps():
    with pytest.raises(ValueError, match="positive integer"):
        InterventionTimingConfig(planning_horizon_steps=2.5)  # type: ignore[arg-type]


def test_timing_config_rejects_nonfinite_values():
    with pytest.raises(ValueError, match="finite"):
        InterventionTimingConfig(step_duration_s=float("nan"))
