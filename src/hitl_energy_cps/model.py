from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class ReviewDecision(str, Enum):
    ACCEPT = "accept"
    MODIFY = "modify"
    REJECT = "reject"


@dataclass(frozen=True)
class CPSState:
    domain: str
    energy_demand: float
    safety_margin: float
    service_quality: float
    urgency: float = 0.0
    metadata: dict[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.energy_demand < 0:
            raise ValueError("energy_demand must be non-negative")
        if not 0.0 <= self.service_quality <= 1.0:
            raise ValueError("service_quality must be between 0 and 1")
        if not 0.0 <= self.urgency <= 1.0:
            raise ValueError("urgency must be between 0 and 1")


@dataclass(frozen=True)
class ControlAction:
    name: str
    energy_cost: float
    safety_delta: float
    service_delta: float

    def __post_init__(self) -> None:
        if self.energy_cost < 0:
            raise ValueError("energy_cost must be non-negative")


@dataclass(frozen=True)
class DecisionScore:
    action: ControlAction
    energy_score: float
    safety_score: float
    service_score: float
    total_score: float


@dataclass(frozen=True)
class HumanDecision:
    decision: ReviewDecision
    selected_action: ControlAction
    rationale: str = ""
    review_cost: float = 0.0
