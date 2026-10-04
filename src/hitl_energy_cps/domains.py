from __future__ import annotations

from .model import CPSState, ControlAction


def ev_charging_case() -> tuple[CPSState, list[ControlAction]]:
    return (
        CPSState(
            domain="ev-charging",
            energy_demand=0.72,
            safety_margin=0.18,
            service_quality=0.70,
            urgency=0.65,
        ),
        [
            ControlAction("slow-charge", energy_cost=0.35, safety_delta=0.20, service_delta=-0.05),
            ControlAction("balanced-charge", energy_cost=0.55, safety_delta=0.08, service_delta=0.08),
            ControlAction("fast-charge", energy_cost=0.90, safety_delta=-0.15, service_delta=0.18),
        ],
    )


def smart_building_case() -> tuple[CPSState, list[ControlAction]]:
    return (
        CPSState(
            domain="smart-building",
            energy_demand=0.60,
            safety_margin=0.45,
            service_quality=0.78,
            urgency=0.30,
        ),
        [
            ControlAction("eco-hvac", energy_cost=0.30, safety_delta=0.05, service_delta=-0.08),
            ControlAction("balanced-hvac", energy_cost=0.50, safety_delta=0.05, service_delta=0.02),
            ControlAction("comfort-first", energy_cost=0.85, safety_delta=0.02, service_delta=0.12),
        ],
    )


def manufacturing_case() -> tuple[CPSState, list[ControlAction]]:
    return (
        CPSState(
            domain="smart-manufacturing",
            energy_demand=0.80,
            safety_margin=0.25,
            service_quality=0.68,
            urgency=0.85,
        ),
        [
            ControlAction("eco-cycle", energy_cost=0.40, safety_delta=0.10, service_delta=-0.10),
            ControlAction("balanced-cycle", energy_cost=0.62, safety_delta=0.06, service_delta=0.05),
            ControlAction("throughput-cycle", energy_cost=0.95, safety_delta=-0.10, service_delta=0.20),
        ],
    )


def all_cases() -> dict[str, tuple[CPSState, list[ControlAction]]]:
    return {
        "ev-charging": ev_charging_case(),
        "smart-building": smart_building_case(),
        "smart-manufacturing": manufacturing_case(),
    }
