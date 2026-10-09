"""
Unit and validation tests for Module A: Basic Calculations.
"""

import math
import pytest

from basic_calculations import (
    calculate_free_tyre_radius,
    calculate_dynamic_rolling_radius,
    calculate_vehicle_weight,
    calculate_overall_gear_ratio,
    calculate_all_overall_gear_ratios,
    calculate_torque_at_rated_power,
    calculate_cg_reference_distances,
)
import specifications as spec


def test_free_tyre_radius():
    # 215/55 R17
    # Rim radius = (17 * 25.4) / 2 = 215.9 mm
    # Sidewall = 215 * 0.55 = 118.25 mm
    # Total = 334.15 mm = 0.33415 m
    r_free = calculate_free_tyre_radius(17.0, 215.0, 55.0)
    assert r_free == pytest.approx(0.33415, rel=1e-4)


def test_dynamic_rolling_radius():
    r_free = 0.33415
    r_dyn = calculate_dynamic_rolling_radius(r_free, 0.97)
    # 0.33415 * 0.97 = 0.3241255 m
    assert r_dyn == pytest.approx(0.32413, rel=1e-4)


def test_vehicle_weight():
    w_kerb = calculate_vehicle_weight(spec.KERB_MASS, spec.GRAVITY)
    # 1550 * 9.81 = 15205.5 N
    assert w_kerb == pytest.approx(15205.5, rel=1e-4)

    w_gvw = calculate_vehicle_weight(spec.GROSS_VEHICLE_MASS, spec.GRAVITY)
    # 1805 * 9.81 = 17707.05 N
    assert w_gvw == pytest.approx(17707.05, rel=1e-4)


def test_overall_gear_ratios():
    ratios = calculate_all_overall_gear_ratios(spec.GEAR_RATIOS, 4.0)
    assert ratios[1] == pytest.approx(3.833 * 4.0, rel=1e-4)  # 15.332
    assert ratios[2] == pytest.approx(2.143 * 4.0, rel=1e-4)  # 8.572
    assert ratios[6] == pytest.approx(0.727 * 4.0, rel=1e-4)  # 2.908


def test_torque_at_rated_power():
    # P = 85.3 kW, N = 4000 rpm
    # omega = 2 * pi * 4000 / 60 = 418.879 rad/s
    # T_P = 85300 / 418.879 = 203.6387 Nm ~ 203.64 Nm
    t_p = calculate_torque_at_rated_power(85.3, 4000.0)
    assert t_p == pytest.approx(203.6387, rel=1e-3)


def test_cg_reference_distances():
    # L = 2.610 m, sf = 0.61
    # L2 = 0.61 * 2.610 = 1.5921 m
    # L1 = 2.610 - 1.5921 = 1.0179 m
    l1, l2 = calculate_cg_reference_distances(2.610, 0.61)
    assert l2 == pytest.approx(1.5921, rel=1e-4)
    assert l1 == pytest.approx(1.0179, rel=1e-4)
    assert (l1 + l2) == pytest.approx(2.610, rel=1e-5)


def test_basic_calculations_invalid_inputs():
    with pytest.raises(ValueError):
        calculate_free_tyre_radius(-17, 215, 55)
    with pytest.raises(ValueError):
        calculate_dynamic_rolling_radius(0.33, -0.97)
    with pytest.raises(ValueError):
        calculate_vehicle_weight(-100)
    with pytest.raises(ValueError):
        calculate_torque_at_rated_power(85.3, 0)
    with pytest.raises(ValueError):
        calculate_cg_reference_distances(2.61, 1.5)
