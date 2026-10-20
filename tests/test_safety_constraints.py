import pytest

from hitl_energy_cps.model import CPSState, ControlAction
from hitl_energy_cps.policy import ObjectiveWeights, SafetyConstraint, choose_action, score_action
from hitl_energy_cps.review import ReviewPolicy, should_request_human
from hitl_energy_cps.simulation import SimulationConfig, run_simulation


def test_negative_objective_weight_is_rejected():
    with pytest.raises(ValueError, match="non-negative"):
        ObjectiveWeights(energy=-0.1, safety=0.8, service=0.3)


def test_hard_constraint_prevents_energy_weight_from_selecting_unsafe_action():
    state = CPSState("test", energy_demand=0.8, safety_margin=0.1, service_quality=0.8)
    cheap_unsafe = ControlAction("cheap-unsafe", 0.01, -0.2, 0.0)
    safe = ControlAction("safe", 1.0, 0.1, 0.0)
    choice = choose_action(
        state,
        [cheap_unsafe, safe],
        weights=ObjectiveWeights(energy=0.99, safety=0.01, service=0.0),
        constraint=SafetyConstraint(minimum_projected_margin=0.0),
    )
    assert choice.action.name == "safe"


def test_review_detects_unsafe_projected_proposal_even_when_current_state_is_safe():
    state = CPSState("test", energy_demand=0.8, safety_margin=0.3, service_quality=0.8)
    unsafe = ControlAction("unsafe", 0.01, -0.5, 0.0)
    alternative = ControlAction("alternative", 3.0, 0.0, 0.0)
    scores = [
        score_action(state, unsafe, weights=ObjectiveWeights(energy=1.0, safety=0.0, service=0.0)),
        score_action(state, alternative, weights=ObjectiveWeights(energy=1.0, safety=0.0, service=0.0)),
    ]
    request = should_request_human(
        state,
        scores,
        policy=ReviewPolicy(safety_margin_threshold=0.1, projected_safety_margin_threshold=0.0),
    )
    assert request.required
    assert "unsafe-projected-margin" in request.reasons


def test_simulation_applies_safe_action_under_energy_dominant_weights():
    state = CPSState("test", energy_demand=0.8, safety_margin=0.1, service_quality=0.8)
    cheap_unsafe = ControlAction("cheap-unsafe", 0.01, -0.2, 0.0)
    safe = ControlAction("safe", 1.0, 0.1, 0.0)
    result = run_simulation(
        state,
        [cheap_unsafe, safe],
        config=SimulationConfig(steps=1, minimum_safety_margin=0.0),
        weights=ObjectiveWeights(energy=0.99, safety=0.01, service=0.0),
    )
    assert result.records[0].proposed_action == "safe"
    assert result.records[0].applied_action == "safe"
    assert result.records[0].safety_filter_intervened
    assert result.safety_filter_interventions == 1
    assert result.constraint_fallbacks == 0
    assert result.unsafe_steps == 0


def test_guardrail_review_reasons_describe_actual_feasible_proposal():
    state = CPSState("test", energy_demand=0.8, safety_margin=0.3, service_quality=0.8)
    cheap_unsafe = ControlAction("cheap-unsafe", 0.01, -0.5, 0.0)
    safe = ControlAction("safe", 1.0, 0.1, 0.0)
    result = run_simulation(
        state,
        [cheap_unsafe, safe],
        config=SimulationConfig(steps=1, minimum_safety_margin=0.0),
        weights=ObjectiveWeights(energy=1.0, safety=0.0, service=0.0),
        review_policy=ReviewPolicy(
            safety_margin_threshold=0.1,
            projected_safety_margin_threshold=0.0,
            score_gap_threshold=0.0,
            urgency_threshold=1.0,
        ),
    )
    record = result.records[0]
    assert record.proposed_action == "safe"
    assert record.safety_filter_intervened
    assert "unsafe-projected-margin" not in record.review_reasons


def test_impossible_constraints_use_auditable_safest_fallback():
    state = CPSState("test", energy_demand=0.8, safety_margin=-0.5, service_quality=0.8)
    less_bad = ControlAction("less-bad", 2.0, 0.1, 0.0)
    worse = ControlAction("worse", 0.1, -0.1, 0.0)
    result = run_simulation(
        state,
        [worse, less_bad],
        config=SimulationConfig(steps=1, minimum_safety_margin=0.0),
    )
    assert result.records[0].applied_action == "less-bad"
    assert result.records[0].constraint_fallback
    assert not result.records[0].safety_filter_intervened
    assert result.constraint_fallbacks == 1
    assert result.safety_filter_interventions == 0
