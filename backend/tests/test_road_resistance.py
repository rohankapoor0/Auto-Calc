"""
Unit and validation tests for Module C: Road Resistance and Performance.
"""

import math
import pytest

from basic_calculations import (
    calculate_free_tyre_radius,
    calculate_dynamic_rolling_radius,
    calculate_vehicle_weight,
)
from road_resistance import (
    calculate_air_resistance_constant,
    calculate_rolling_resistance,
    calculate_aerodynamic_resistance,
    calculate_grade_resistance,
    calculate_total_road_resistance,
    calculate_drawbar_pull,
    calculate_wheel_power_kw,
    calculate_engine_power_required_kw,
    calculate_engine_speed_from_road_speed,
    evaluate_top_speed_feasibility,
    calculate_power_at_100kmh,
)
import specifications as spec


@pytest.fixture
def vehicle_weights():
    w_kerb = calculate_vehicle_weight(spec.KERB_MASS, spec.GRAVITY)
    w_gvw = calculate_vehicle_weight(spec.GROSS_VEHICLE_MASS, spec.GRAVITY)
    return {"kerb": w_kerb, "gvw": w_gvw}


@pytest.fixture
def dynamic_radius():
    r_free = calculate_free_tyre_radius()
    return calculate_dynamic_rolling_radius(r_free, spec.TYRE_DEFLECTION_FACTOR)


def test_air_resistance_constant():
    # k = 0.5 * 1.225 * 0.35 * 2.4 = 0.5145 kg/m
    k = calculate_air_resistance_constant(1.225, 0.35, 2.4)
    assert k == pytest.approx(0.5145, rel=1e-4)


def test_rolling_resistance(vehicle_weights):
    # R_RR = 0.015 * 15205.5 = 228.0825 N
    r_rr_kerb = calculate_rolling_resistance(vehicle_weights["kerb"], 0.015)
    assert r_rr_kerb == pytest.approx(228.0825, rel=1e-4)

    # R_RR = 0.015 * 17707.05 = 265.60575 N
    r_rr_gvw = calculate_rolling_resistance(vehicle_weights["gvw"], 0.015)
    assert r_rr_gvw == pytest.approx(265.6058, rel=1e-4)


def test_aerodynamic_resistance():
    # V = 100 / 3.6 = 27.7778 m/s
    # V^2 = 771.6049
    # R_AF = 0.5145 * 771.6049 = 396.99 N
    v_mps = 100.0 / 3.6
    r_af = calculate_aerodynamic_resistance(v_mps, 1.225, 0.35, 2.4)
    assert r_af == pytest.approx(396.99, rel=1e-3)


def test_grade_resistance(vehicle_weights):
    # On flat ground theta = 0 => R_GR = 0
    assert calculate_grade_resistance(vehicle_weights["kerb"], 0.0) == 0.0

    # On a slope
    r_gr_slope = calculate_grade_resistance(vehicle_weights["kerb"], math.radians(5))
    assert r_gr_slope == pytest.approx(vehicle_weights["kerb"] * math.sin(math.radians(5)), rel=1e-4)


def test_total_resistance_and_power_at_100kmh(vehicle_weights):
    res = calculate_power_at_100kmh(vehicle_weights["kerb"])
    # R_T = 228.08 + 396.99 = 625.07 N
    assert res["total_resistance_N"] == pytest.approx(625.07, rel=1e-3)
    # P_wheel = 625.07 * 27.7778 / 1000 = 17.36 kW
    assert res["wheel_power_kw"] == pytest.approx(17.36, rel=1e-2)
    # P_engine = 17.36 / 0.90 = 19.29 kW
    assert res["engine_power_kw"] == pytest.approx(19.29, rel=1e-2)


def test_drawbar_pull():
    f_db = calculate_drawbar_pull(1000.0, 600.0)
    assert f_db == 400.0


def test_engine_speed_from_road_speed(dynamic_radius):
    # Test inverse consistency: compute road speed at 2000 rpm in 4th gear, then invert
    gear_4_ratio = spec.GEAR_RATIOS[4]
    io = gear_4_ratio * spec.FINAL_DRIVE_RATIO
    from drivetrain import calculate_vehicle_speed_mps
    v_mps = calculate_vehicle_speed_mps(2000.0, gear_4_ratio, dynamic_radius, spec.FINAL_DRIVE_RATIO)
    n_calc = calculate_engine_speed_from_road_speed(v_mps, dynamic_radius, io)
    assert n_calc == pytest.approx(2000.0, rel=1e-4)


def test_top_speed_feasibility(vehicle_weights, dynamic_radius):
    res_kerb = evaluate_top_speed_feasibility(
        gear_ratio=spec.GEAR_RATIOS[6],
        dynamic_radius=dynamic_radius,
        weight=vehicle_weights["kerb"],
    )
    assert "feasibility_status" in res_kerb
    assert "spare_force_drawbar_pull_N" in res_kerb
    assert res_kerb["rated_speed_kmh"] > 160.0
