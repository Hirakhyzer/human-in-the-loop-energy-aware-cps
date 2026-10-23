from __future__ import annotations

from dataclasses import dataclass

from .operator_state import OperatorState, operator_burden
from .review import ReviewPolicy


@dataclass(frozen=True)
class AdaptiveReviewDecision:
    policy: ReviewPolicy
    burden_score: float
    mode: str


def adapt_review_policy(
    base: ReviewPolicy,
    operator: OperatorState,
) -> AdaptiveReviewDecision:
    """Adapt escalation thresholds while preserving hard safety review triggers.

    High operator burden should reduce discretionary review demand rather than
    weaken projected-safety safeguards. The policy therefore tightens only the
    ambiguity/urgency pathways while leaving safety and service thresholds unchanged.
    """
    burden = operator_burden(operator)
    if burden.score >= 75:
        gap = max(0.01, base.score_gap_threshold * 0.50)
        urgency = min(1.0, base.urgency_threshold + 0.20)
        mode = "protected-attention"
    elif burden.score >= 55:
        gap = max(0.01, base.score_gap_threshold * 0.75)
        urgency = min(1.0, base.urgency_threshold + 0.10)
        mode = "reduced-discretionary-review"
    else:
        return AdaptiveReviewDecision(base, burden.score, "normal")

    policy = ReviewPolicy(
        safety_margin_threshold=base.safety_margin_threshold,
        projected_safety_margin_threshold=base.projected_safety_margin_threshold,
        projected_service_threshold=base.projected_service_threshold,
        score_gap_threshold=gap,
        urgency_threshold=urgency,
    )
    return AdaptiveReviewDecision(policy, burden.score, mode)
