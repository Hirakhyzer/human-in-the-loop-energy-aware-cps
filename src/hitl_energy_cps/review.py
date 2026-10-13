from __future__ import annotations

from dataclasses import dataclass

from .model import CPSState, DecisionScore
from .policy import projected_safety_margin, projected_service_quality


@dataclass(frozen=True)
class ReviewPolicy:
    safety_margin_threshold: float = 0.2
    projected_safety_margin_threshold: float = 0.0
    projected_service_threshold: float = 0.0
    score_gap_threshold: float = 0.08
    urgency_threshold: float = 0.8


@dataclass(frozen=True)
class ReviewRequest:
    required: bool
    reasons: tuple[str, ...]
    score_gap: float | None


def should_request_human(
    state: CPSState,
    ranked_scores: list[DecisionScore],
    *,
    policy: ReviewPolicy = ReviewPolicy(),
) -> ReviewRequest:
    reasons: list[str] = []

    if state.safety_margin <= policy.safety_margin_threshold:
        reasons.append("low-safety-margin")
    if state.urgency >= policy.urgency_threshold:
        reasons.append("high-urgency")

    ordered = sorted(ranked_scores, key=lambda item: item.total_score, reverse=True)
    if ordered:
        proposed = ordered[0].action
        if projected_safety_margin(state, proposed) < policy.projected_safety_margin_threshold:
            reasons.append("unsafe-projected-margin")
        if projected_service_quality(state, proposed) < policy.projected_service_threshold:
            reasons.append("service-floor-violation")

    score_gap = None
    if len(ordered) >= 2:
        score_gap = ordered[0].total_score - ordered[1].total_score
        if score_gap <= policy.score_gap_threshold:
            reasons.append("decision-ambiguity")

    return ReviewRequest(bool(reasons), tuple(reasons), score_gap)
