"""
Unit and validation tests for Module B: Drivetrain Calculations.
"""

import math
import pytest

from basic_calculations import (
    calculate_free_tyre_radius,
    calculate_dynamic_rolling_radius,
    calculate_torque_at_rated_power,
)
from drivetrain import (
    calculate_tractive_effort,
    calculate_vehicle_speed_mps,
    convert_mps_to_kmh,
    calculate_vehicle_speed_kmh,
    calculate_wheel_torque_demand,
    calculate_drivetrain_gear_table,
)
import specifications as spec


@pytest.fixture
def dynamic_radius():
    r_free = calculate_free_tyre_radius()
    return calculate_dynamic_rolling_radius(r_free, spec.TYRE_DEFLECTION_FACTOR)


def test_tractive_effort_1st_gear(dynamic_radius):
    # 1st gear: ig = 3.833, if = 4.0, io = 15.332
    # Te = 250 Nm, eta_T = 0.90
    # r = 0.3241255 m
    # F_TW = (250 * 15.332 * 0.90) / 0.3241255 = 10643.099 N
    f_tw = calculate_tractive_effort(
        engine_torque=250.0,
        gear_ratio=3.833,
        dynamic_radius=dynamic_radius,
        final_drive_ratio=4.0,
        transmission_efficiency=0.90,
    )
    assert f_tw == pytest.approx(10643.1, rel=1e-3)


def test_vehicle_speeds(dynamic_radius):
    # 1st gear: io = 15.332
    # At 1500 rpm:
    # omega = 2 * pi * 1500 / 60 = 157.0796 rad/s
    # V = 157.0796 * 0.3241255 / 15.332 = 3.3208 m/s
    # V_kmh = 3.3208 * 3.6 = 11.955 km/h
    v_mps = calculate_vehicle_speed_mps(1500.0, 3.833, dynamic_radius, 4.0)
    v_kmh = convert_mps_to_kmh(v_mps)
    assert v_mps == pytest.approx(3.3208, rel=1e-3)
    assert v_kmh == pytest.approx(11.955, rel=1e-3)

    # At 4000 rpm:
    # V_kmh = 11.955 * (4000 / 1500) = 31.88 km/h
    v_kmh_4000 = calculate_vehicle_speed_kmh(4000.0, 3.833, dynamic_radius, 4.0)
    assert v_kmh_4000 == pytest.approx(31.88, rel=1e-3)


def test_tractive_effort_at_4000rpm(dynamic_radius):
    # At 4000 rpm, torque should be T_P = ~203.64 Nm (not 250 Nm)
    t_p = calculate_torque_at_rated_power(spec.MAX_POWER_KW, spec.RATED_POWER_RPM)
    f_tw_4000 = calculate_tractive_effort(
        t_p, 3.833, dynamic_radius, 4.0, 0.90
    )
    # Ratio should be t_p / 250.0
    f_tw_250 = calculate_tractive_effort(
        250.0, 3.833, dynamic_radius, 4.0, 0.90
    )
    assert f_tw_4000 == pytest.approx(f_tw_250 * (t_p / 250.0), rel=1e-4)


def test_wheel_torque_demand(dynamic_radius):
    f_tw = 10000.0
    t_demand = calculate_wheel_torque_demand(f_tw, dynamic_radius)
    assert t_demand == pytest.approx(10000.0 * dynamic_radius, rel=1e-5)


def test_drivetrain_gear_table(dynamic_radius):
    table = calculate_drivetrain_gear_table(dynamic_radius)
    assert len(table["gears"]) == 6
    assert 1 in table["gears"]
    assert 6 in table["gears"]
    # 6th gear speed at 4000 rpm
    v6_4000 = table["gears"][6]["speeds_by_rpm"][4000]["speed_kmh"]
    assert v6_4000 > 150.0  # Around 168 km/h
