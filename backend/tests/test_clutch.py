"""
Unit and validation tests for Module E: Clutch Calculations.
"""

import math
import pytest

from clutch import (
    calculate_outer_friction_radius,
    calculate_inner_friction_radius,
    calculate_mean_friction_radius,
    calculate_design_torque,
    calculate_axial_clamping_force,
    calculate_effective_radius_uniform_pressure,
    calculate_torque_capacity_uniform_pressure,
    calculate_average_contact_pressure,
    calculate_uniform_wear_constant,
    calculate_max_pressure_uniform_wear,
    calculate_min_pressure_uniform_wear,
    perform_complete_clutch_analysis,
)
import specifications as spec


def test_clutch_radii():
    # OD = 240 mm => r1 = 0.120 m
    # ID = 155 mm => r2 = 0.0775 m
    r1 = calculate_outer_friction_radius(240.0)
    r2 = calculate_inner_friction_radius(155.0)
    assert r1 == pytest.approx(0.120, rel=1e-5)
    assert r2 == pytest.approx(0.0775, rel=1e-5)

    mean_r = calculate_mean_friction_radius(r1, r2)
    # (0.120 + 0.0775) / 2 = 0.09875 m
    assert mean_r == pytest.approx(0.09875, rel=1e-5)


def test_design_torque_and_clamping_force():
    # Te = 250 Nm, SF = 1.25 => Tc = 312.5 Nm
    t_c = calculate_design_torque(250.0, 1.25)
    assert t_c == pytest.approx(312.5, rel=1e-5)

    r1 = 0.120
    r2 = 0.0775
    mean_r = 0.09875
    # Wc = Tc / (n * mu_c * R)
    # Wc = 312.5 / (2 * 0.35 * 0.09875) = 312.5 / 0.069125 = 4520.7957 N
    w_c = calculate_axial_clamping_force(t_c, mean_r, 0.35, 2)
    assert w_c == pytest.approx(4520.8, rel=1e-3)


def test_effective_radius_and_uniform_pressure():
    r1 = 0.120
    r2 = 0.0775
    # Reff = (2/3) * (r1^3 - r2^3) / (r1^2 - r2^2)
    num = (0.120 ** 3) - (0.0775 ** 3)
    denom = (0.120 ** 2) - (0.0775 ** 2)
    expected_reff = (2.0 / 3.0) * (num / denom)
    r_eff = calculate_effective_radius_uniform_pressure(r1, r2)
    assert r_eff == pytest.approx(expected_reff, rel=1e-5)
    assert r_eff == pytest.approx(0.10027, rel=1e-3)

    # Torque under uniform pressure with same Wc
    t_c = 312.5
    w_c = calculate_axial_clamping_force(t_c, 0.09875, 0.35, 2)
    t_up = calculate_torque_capacity_uniform_pressure(w_c, r_eff, 0.35, 2)
    # T = 2 * 0.35 * 4520.8 * 0.100274 = 317.3 Nm
    assert t_up == pytest.approx(317.3, rel=1e-2)


def test_contact_pressures():
    r1 = 0.120
    r2 = 0.0775
    w_c = 4520.7957

    # p_avg = Wc / (pi * (r1^2 - r2^2))
    area = math.pi * ((r1 ** 2) - (r2 ** 2))
    expected_p_avg = w_c / area
    p_avg = calculate_average_contact_pressure(w_c, r1, r2)
    assert p_avg == pytest.approx(expected_p_avg, rel=1e-5)
    # ~0.170 MPa = 170 kPa
    assert (p_avg / 1e6) == pytest.approx(0.1706, rel=1e-2)

    # C = Wc / (2 * pi * (r1 - r2))
    expected_c = w_c / (2.0 * math.pi * (r1 - r2))
    c_const = calculate_uniform_wear_constant(w_c, r1, r2)
    assert c_const == pytest.approx(expected_c, rel=1e-5)

    p_max = calculate_max_pressure_uniform_wear(c_const, r2)
    p_min = calculate_min_pressure_uniform_wear(c_const, r1)
    assert p_max > p_avg
    assert p_min < p_avg


def test_complete_clutch_analysis():
    res = perform_complete_clutch_analysis()
    assert "average_contact_pressure_MPa" in res
    assert "max_pressure_uniform_wear_MPa" in res
    assert res["average_contact_pressure_MPa"] > 0
