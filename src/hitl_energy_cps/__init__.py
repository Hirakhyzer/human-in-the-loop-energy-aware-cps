"""Human-in-the-loop energy-aware CPS research package."""

from .domains import all_cases, ev_charging_case, manufacturing_case, smart_building_case
from .evaluation import HITLComparison, Outcome, compare_outcomes
from .human_models import EnergyAwareOperator, SafetyAwareOperator
from .model import CPSState, ControlAction, DecisionScore, HumanDecision, ReviewDecision
from .pareto import ParetoPoint, action_point, dominates, pareto_front
from .policy import ObjectiveWeights, choose_action, score_action
from .review import ReviewPolicy, ReviewRequest, should_request_human
from .simulation import SimulationConfig, SimulationResult, StepRecord, run_simulation

__all__ = [
    "CPSState",
    "ControlAction",
    "DecisionScore",
    "EnergyAwareOperator",
    "HITLComparison",
    "HumanDecision",
    "ObjectiveWeights",
    "Outcome",
    "ParetoPoint",
    "ReviewDecision",
    "ReviewPolicy",
    "ReviewRequest",
    "SafetyAwareOperator",
    "SimulationConfig",
    "SimulationResult",
    "StepRecord",
    "action_point",
    "all_cases",
    "choose_action",
    "compare_outcomes",
    "dominates",
    "ev_charging_case",
    "manufacturing_case",
    "pareto_front",
    "run_simulation",
    "score_action",
    "should_request_human",
    "smart_building_case",
]
