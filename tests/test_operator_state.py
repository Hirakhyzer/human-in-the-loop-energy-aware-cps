import pytest

from hitl_energy_cps.adaptive_review import adapt_review_policy
from hitl_energy_cps.operator_state import OperatorState, operator_burden
from hitl_energy_cps.review import ReviewPolicy


def test_operator_state_rejects_invalid_human_factors():
    with pytest.raises(ValueError, match="workload"):
        OperatorState(workload=1.1)
    with pytest.raises(ValueError, match="fatigue"):
        OperatorState(fatigue=-0.1)
    with pytest.raises(ValueError, match="latency"):
        OperatorState(response_latency_s=-1.0)


def test_operator_burden_increases_effective_response_latency():
    state = OperatorState(workload=0.8, fatigue=0.7, response_latency_s=10.0)
    burden = operator_burden(state)
    assert burden.score > 55
    assert burden.effective_latency_s > state.response_latency_s


def test_high_burden_protects_attention_without_weakening_safety_thresholds():
    base = ReviewPolicy(
        safety_margin_threshold=0.25,
        projected_safety_margin_threshold=0.05,
        projected_service_threshold=0.60,
        score_gap_threshold=0.08,
        urgency_threshold=0.70,
    )
    adapted = adapt_review_policy(
        base,
        OperatorState(workload=1.0, fatigue=1.0, response_latency_s=30.0),
    )
    assert adapted.mode == "protected-attention"
    assert adapted.policy.safety_margin_threshold == base.safety_margin_threshold
    assert adapted.policy.projected_safety_margin_threshold == base.projected_safety_margin_threshold
    assert adapted.policy.projected_service_threshold == base.projected_service_threshold
    assert adapted.policy.score_gap_threshold < base.score_gap_threshold
    assert adapted.policy.urgency_threshold > base.urgency_threshold


def test_low_burden_preserves_original_review_policy():
    base = ReviewPolicy()
    adapted = adapt_review_policy(base, OperatorState(workload=0.1, fatigue=0.1, response_latency_s=1.0))
    assert adapted.mode == "normal"
    assert adapted.policy == base
