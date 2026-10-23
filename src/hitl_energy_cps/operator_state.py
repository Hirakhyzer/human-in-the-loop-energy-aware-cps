from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class OperatorState:
    """Experimental operator-state variables for reproducible HITL studies."""

    workload: float = 0.0
    fatigue: float = 0.0
    response_latency_s: float = 0.0

    def __post_init__(self) -> None:
        if not 0.0 <= self.workload <= 1.0:
            raise ValueError("workload must be within [0, 1]")
        if not 0.0 <= self.fatigue <= 1.0:
            raise ValueError("fatigue must be within [0, 1]")
        if self.response_latency_s < 0.0:
            raise ValueError("response_latency_s must be non-negative")


@dataclass(frozen=True)
class OperatorBurden:
    score: float
    band: str
    effective_latency_s: float


def operator_burden(state: OperatorState) -> OperatorBurden:
    """Combine workload, fatigue and latency into an auditable burden index."""
    latency_component = min(1.0, state.response_latency_s / 30.0)
    score = 100.0 * (
        0.45 * state.workload
        + 0.35 * state.fatigue
        + 0.20 * latency_component
    )
    band = "Critical" if score >= 75 else "High" if score >= 55 else "Watch" if score >= 30 else "Low"
    effective_latency = state.response_latency_s * (1.0 + 0.5 * state.workload + 0.5 * state.fatigue)
    return OperatorBurden(score=score, band=band, effective_latency_s=effective_latency)
