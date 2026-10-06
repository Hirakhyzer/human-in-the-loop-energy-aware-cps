from hitl_energy_cps.domains import ev_charging_case
from hitl_energy_cps.human_models import EnergyAwareOperator, SafetyAwareOperator
from hitl_energy_cps.model import CPSState, ControlAction
from hitl_energy_cps.pareto import action_point, dominates, pareto_front
from hitl_energy_cps.simulation import SimulationConfig, run_simulation


def test_simulation_records_every_control_step():
    state, actions = ev_charging_case()
    result = run_simulation(state, actions, config=SimulationConfig(steps=5))
    assert len(result.records) == 5
    assert result.total_energy == sum(record.energy_used for record in result.records)


def test_safety_operator_is_only_counted_when_review_is_requested():
    state, actions = ev_charging_case()
    result = run_simulation(
        state,
        actions,
        config=SimulationConfig(steps=4),
        human_policy=SafetyAwareOperator(),
    )
    assert result.review_count <= 4
    assert result.modification_count + result.rejection_count <= result.review_count


def test_energy_operator_respects_guardrails_when_feasible():
    state = CPSState("test", 0.5, 0.2, 0.7)
    actions = [
        ControlAction("cheap-unsafe", 0.1, -0.2, 0.0),
        ControlAction("efficient-safe", 0.3, 0.0, 0.0),
        ControlAction("expensive-safe", 0.8, 0.2, 0.1),
    ]
    _, selected = EnergyAwareOperator(minimum_projected_margin=0.1)(state, actions[2], actions)
    assert selected.name == "efficient-safe"


def test_pareto_front_removes_dominated_action():
    state = CPSState("test", 0.5, 0.4, 0.6)
    actions = [
        ControlAction("dominated", 0.8, 0.0, 0.0),
        ControlAction("better", 0.4, 0.1, 0.1),
        ControlAction("low-energy-tradeoff", 0.2, -0.1, -0.1),
    ]
    front = pareto_front(state, actions)
    assert "dominated" not in {point.action for point in front}
    assert {point.action for point in front} == {"better", "low-energy-tradeoff"}


def test_dominance_requires_no_worse_all_objectives():
    state = CPSState("test", 0.5, 0.4, 0.6)
    cheap = action_point(state, ControlAction("cheap", 0.2, -0.1, 0.0))
    safe = action_point(state, ControlAction("safe", 0.5, 0.2, 0.0))
    assert not dominates(cheap, safe)
    assert not dominates(safe, cheap)
