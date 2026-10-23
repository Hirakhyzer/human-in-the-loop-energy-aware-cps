from math import isinf

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
    assert timing.steps_to_boundary == 5
    assert timing.time_to_boundary_s == 5.0
    assert timing.latest_safe_request_s == 2.0
    assert timing.latest_safe_request_step == 2
    assert timing.status == "scheduled"


def test_slow_or_burdened_operator_requires_immediate_escalation():
    state = CPSState("test", energy_demand=0.5, safety_margin=0.2, service_quality=0.9)
    action = ControlAction("degrading", energy_cost=0.1, safety_delta=-0.1, service_delta=0.0)
    timing = estimate_intervention_timing(
        state,
        action,
        OperatorState(workload=1.0, fatigue=1.0, response_latency_s=2.0),
        config=InterventionTimingConfig(step_duration_s=1.0, preparation_buffer_s=1.0),
    )
    assert timing.request_now
    assert timing.status in {"request-now", "late-or-immediate"}


def test_non_degrading_action_has_no_intervention_deadline_in_horizon():
    state = CPSState("test", energy_demand=0.5, safety_margin=0.2, service_quality=0.9)
    action = ControlAction("recover", energy_cost=0.2, safety_delta=0.05, service_delta=0.0)
    timing = estimate_intervention_timing(state, action, OperatorState(response_latency_s=2.0))
    assert timing.steps_to_boundary is None
    assert isinf(timing.latest_safe_request_s)
    assert not timing.request_now


def test_existing_safety_violation_is_late_or_immediate():
    state = CPSState("test", energy_demand=0.5, safety_margin=-0.1, service_quality=0.9)
    action = ControlAction("hold", energy_cost=0.1, safety_delta=0.0, service_delta=0.0)
    timing = estimate_intervention_timing(state, action, OperatorState(response_latency_s=1.0))
    assert timing.steps_to_boundary == 0
    assert timing.request_now
    assert timing.status == "late-or-immediate"
