"""
Unit and validation tests for Module F: Hypothetical AWD Calculations.
"""

import math
import pytest

from basic_calculations import calculate_free_tyre_radius, calculate_dynamic_rolling_radius
from awd import (
    calculate_rear_axle_center_radius,
    calculate_front_inner_wheel_path_radius,
    calculate_rear_outer_wheel_path_radius,
    calculate_rear_inner_wheel_path_radius,
    calculate_outer_steering_angle,
    calculate_inner_steering_angle,
    calculate_cg_turning_radius,
    calculate_yaw_rate,
    calculate_wheel_rotational_speed,
    calculate_lateral_acceleration,
    calculate_lateral_load_transfer_factor,
    calculate_remaining_longitudinal_friction_coeff,
    calculate_open_differential_capacity,
    calculate_fixed_60_40_center_diff_capacity,
    calculate_locked_center_diff_capacity,
    calculate_ideal_total_torque_capacity,
    calculate_percentage_of_ideal_capacity,
    perform_complete_awd_analysis,
)
import specifications as spec


@pytest.fixture
def dynamic_radius():
    r_free = calculate_free_tyre_radius()
    return calculate_dynamic_rolling_radius(r_free)


def test_awd_turning_radii():
    # Ro = 5.3, L = 2.61, t = 1.55
    # R_r = sqrt(5.3^2 - 2.61^2) - 1.55 / 2
    # 5.3^2 = 28.09, 2.61^2 = 6.8121 => diff = 21.2779 => sqrt = 4.612798
    # R_r = 4.612798 - 0.775 = 3.837798 m ~ 3.838 m
    r_rear = calculate_rear_axle_center_radius(5.3, 2.61, 1.55)
    assert r_rear == pytest.approx(3.8378, rel=1e-3)

    # R_FI = sqrt((R_r - t/2)^2 + L^2)
    # R_r - t/2 = 3.8378 - 0.775 = 3.0628
    # R_FI = sqrt(3.0628^2 + 2.61^2) = sqrt(9.3807 + 6.8121) = sqrt(16.1928) = 4.024 m
    r_fi = calculate_front_inner_wheel_path_radius(r_rear, 2.61, 1.55)
    assert r_fi == pytest.approx(4.024, rel=1e-3)

    # R_RO = sqrt(R_r^2 + L^2)
    # R_RO = sqrt(3.8378^2 + 2.61^2) = sqrt(14.7287 + 6.8121) = 4.641 m
    r_ro = calculate_rear_outer_wheel_path_radius(r_rear, 2.61)
    assert r_ro == pytest.approx(4.641, rel=1e-3)

    # R_RI = R_r - t/2 = 3.0628 m
    r_ri = calculate_rear_inner_wheel_path_radius(r_rear, 1.55)
    assert r_ri == pytest.approx(3.0628, rel=1e-3)


def test_steering_angles():
    r_rear = 3.8378
    delta_o = calculate_outer_steering_angle(r_rear, 2.61)
    # tan(delta_o) = 2.61 / 3.8378 = 0.68007 => ~34.22 deg
    assert delta_o["angle_deg"] == pytest.approx(34.22, rel=1e-2)

    delta_i = calculate_inner_steering_angle(r_rear, 2.61, 1.55)
    # tan(delta_i) = 2.61 / 3.0628 = 0.85216 => ~40.43 deg
    assert delta_i["angle_deg"] == pytest.approx(40.44, rel=1e-2)


def test_lateral_acceleration_and_load_transfer():
    # V = 3.32 m/s, R_CG = sqrt(3.8378^2 + 1.5921^2) = 4.155 m
    r_cg = calculate_cg_turning_radius(3.8378, 1.5921)
    a_y = calculate_lateral_acceleration(3.32, r_cg)
    # a_y = 3.32^2 / 4.155 = 11.0224 / 4.155 = 2.653 m/s^2
    assert a_y == pytest.approx(2.653, rel=1e-2)

    # lambda = (a_y / g) * (h / t)
    # lambda = (2.653 / 9.81) * (0.605 / 1.55) = 0.2704 * 0.3903 = 0.1055
    lam = calculate_lateral_load_transfer_factor(a_y, 0.605, 1.55, 9.81)
    assert lam == pytest.approx(0.1055, rel=1e-2)


def test_remaining_friction():
    # mu = 0.80, a_y = 2.653, g = 9.81 => a_y / g = 0.2704
    # mu_x = sqrt(0.80^2 - 0.2704^2) = sqrt(0.64 - 0.0731) = sqrt(0.5669) = 0.7529
    mu_x = calculate_remaining_longitudinal_friction_coeff(0.80, 2.653, 9.81)
    assert mu_x == pytest.approx(0.7529, rel=1e-2)


def test_differential_torque_hierarchy():
    # Given wheel limits: FO=1500, FI=1000, RO=1200, RI=800
    t_fo, t_fi, t_ro, t_ri = 1500.0, 1000.0, 1200.0, 800.0
    t_ideal = calculate_ideal_total_torque_capacity(t_fo, t_fi, t_ro, t_ri)
    assert t_ideal == 4500.0

    # Open: 4 * min(800) = 3200
    t_open = calculate_open_differential_capacity(t_fo, t_fi, t_ro, t_ri)
    assert t_open == 3200.0

    # Locked: 2*min(1000) + 2*min(800) = 2000 + 1600 = 3600
    t_locked = calculate_locked_center_diff_capacity(t_fo, t_fi, t_ro, t_ri)
    assert t_locked["t_locked_Nm"] == 3600.0

    # Check %
    pct_open = calculate_percentage_of_ideal_capacity(t_open, t_ideal)
    pct_locked = calculate_percentage_of_ideal_capacity(t_locked["t_locked_Nm"], t_ideal)
    assert pct_open < pct_locked < 100.0


def test_complete_awd_analysis(dynamic_radius):
    res = perform_complete_awd_analysis(dynamic_radius)
    assert "kinematics" in res
    assert "dynamics" in res
    assert "differential_comparison" in res
    diffs = res["differential_comparison"]
    assert diffs["open_differential"]["total_torque_Nm"] <= diffs["locked_center_differential"]["total_torque_Nm"]
    assert diffs["locked_center_differential"]["total_torque_Nm"] <= diffs["torque_vectoring_ideal"]["total_torque_Nm"]
