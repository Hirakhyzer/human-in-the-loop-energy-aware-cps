from hitl_energy_cps import (
    CPSState,
    ControlAction,
    ObjectiveWeights,
    Outcome,
    compare_outcomes,
    score_action,
    should_request_human,
)


def test_energy_score_prefers_lower_energy_when_other_effects_match():
    state = CPSState("test", energy_demand=0.5, safety_margin=0.5, service_quality=0.7)
    low = ControlAction("low", 0.2, 0.0, 0.0)
    high = ControlAction("high", 0.8, 0.0, 0.0)

    assert score_action(state, low).total_score > score_action(state, high).total_score


def test_low_safety_margin_requests_human_review():
    state = CPSState("test", energy_demand=0.5, safety_margin=0.1, service_quality=0.8)
    scores = [
        score_action(state, ControlAction("a", 0.3, 0.0, 0.0)),
        score_action(state, ControlAction("b", 0.6, 0.0, 0.0)),
    ]

    review = should_request_human(state, scores)
    assert review.required is True
    assert "low-safety-margin" in review.reasons


def test_human_intervention_value_penalizes_review_cost():
    autonomous = Outcome(energy_used=10.0, safety_margin=0.2, service_quality=0.7)
    hitl = Outcome(
        energy_used=8.0,
        safety_margin=0.3,
        service_quality=0.72,
        human_reviews=2,
        intervention_cost=0.5,
    )

    result = compare_outcomes(autonomous, hitl)
    assert result.energy_saving == 2.0
    assert result.human_intervention_value > 0
