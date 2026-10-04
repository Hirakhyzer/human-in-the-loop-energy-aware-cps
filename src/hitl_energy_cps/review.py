from __future__ import annotations

from dataclasses import dataclass

from .model import CPSState, DecisionScore


@dataclass(frozen=True)
class ReviewPolicy:
    safety_margin_threshold: float = 0.2
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

    score_gap = None
    if len(ranked_scores) >= 2:
        ordered = sorted(ranked_scores, key=lambda item: item.total_score, reverse=True)
        score_gap = ordered[0].total_score - ordered[1].total_score
        if score_gap <= policy.score_gap_threshold:
            reasons.append("decision-ambiguity")

    return ReviewRequest(bool(reasons), tuple(reasons), score_gap)
