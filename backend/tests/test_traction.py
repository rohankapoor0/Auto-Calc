"""
Unit and validation tests for Module D: Traction and Gradeability Calculations.
"""

import math
import pytest

from basic_calculations import (
    calculate_free_tyre_radius,
    calculate_dynamic_rolling_radius,
    calculate_vehicle_weight,
    calculate_cg_reference_distances,
)
from drivetrain import calculate_tractive_effort, calculate_wheel_torque_demand
from traction import (
    calculate_static_axle_loads,
    calculate_max_tractive_force_fwd,
    check_wheel_spin,
    calculate_traction_factor,
    calculate_gradeability,
    calculate_longitudinal_load_transfer,
    calculate_dynamic_front_axle_load,
    calculate_tyre_slip_torque,
    compare_torque_demand_and_slip_torque,
    perform_complete_traction_analysis,
)
import specifications as spec


@pytest.fixture
def base_params():
    r_free = calculate_free_tyre_radius()
    r_dyn = calculate_dynamic_rolling_radius(r_free)
    w_kerb = calculate_vehicle_weight(spec.KERB_MASS)
    w_gvw = calculate_vehicle_weight(spec.GROSS_VEHICLE_MASS)
    l1, l2 = calculate_cg_reference_distances(spec.WHEELBASE, spec.FRONT_WEIGHT_SHARE)
    f_tw_1st = calculate_tractive_effort(
        spec.MAX_ENGINE_TORQUE, spec.GEAR_RATIOS[1], r_dyn, spec.FINAL_DRIVE_RATIO, spec.TRANSMISSION_EFFICIENCY
    )
    return {
        "r_dyn": r_dyn,
        "w_kerb": w_kerb,
        "w_gvw": w_gvw,
        "l1": l1,
        "l2": l2,
        "f_tw_1st": f_tw_1st,
    }


def test_static_axle_loads(base_params):
    loads = calculate_static_axle_loads(
        base_params["w_kerb"], spec.WHEELBASE, l1=base_params["l1"], l2=base_params["l2"]
    )
    # W_f = 15205.5 * 0.61 = 9275.355 N
    # W_r = 15205.5 * 0.39 = 5930.145 N
    assert loads["W_f"] == pytest.approx(base_params["w_kerb"] * 0.61, rel=1e-4)
    assert loads["W_r"] == pytest.approx(base_params["w_kerb"] * 0.39, rel=1e-4)
    assert (loads["W_f"] + loads["W_r"]) == pytest.approx(base_params["w_kerb"], rel=1e-5)


def test_max_tractive_force_fwd(base_params):
    # F_max = (mu * W * L2) / (L + mu * h)
    # mu = 0.80, L = 2.610, h = 0.605, L2 = 1.5921
    # Denom = 2.610 + (0.80 * 0.605) = 2.610 + 0.484 = 3.094
    # Kerb: F_max = (0.80 * 15205.5 * 1.5921) / 3.094 = 19366.52 / 3.094 = 6259.38 N
    f_max_kerb = calculate_max_tractive_force_fwd(
        base_params["w_kerb"], base_params["l2"], spec.WHEELBASE, spec.CG_HEIGHT, spec.TYRE_ROAD_ADHESION
    )
    assert f_max_kerb == pytest.approx(6259.4, rel=1e-3)


def test_wheel_spin_check(base_params):
    f_max_kerb = calculate_max_tractive_force_fwd(
        base_params["w_kerb"], base_params["l2"]
    )
    # In 1st gear, F_TW is ~10643 N, which exceeds F_max (~6259 N)
    spin = check_wheel_spin(base_params["f_tw_1st"], f_max_kerb)
    assert spin["spins"] is True
    assert spin["excess_force_N"] > 0


def test_gradeability(base_params):
    f_max_kerb = calculate_max_tractive_force_fwd(
        base_params["w_kerb"], base_params["l2"]
    )
    k = calculate_traction_factor(f_max_kerb, base_params["w_kerb"])
    # k = 6259.4 / 15205.5 = ~0.4116
    assert k == pytest.approx(0.4116, rel=1e-3)

    grade = calculate_gradeability(k, spec.ROLLING_RESISTANCE_COEFFICIENT)
    assert grade["gradeability_angle_deg"] > 20.0
    assert grade["gradient_percent"] > 40.0


def test_dynamic_load_transfer_and_slip_torque(base_params):
    f_max_kerb = calculate_max_tractive_force_fwd(base_params["w_kerb"], base_params["l2"])
    delta_w = calculate_longitudinal_load_transfer(f_max_kerb, spec.CG_HEIGHT, spec.WHEELBASE)
    static_wf = base_params["w_kerb"] * spec.FRONT_WEIGHT_SHARE
    wf_dyn = calculate_dynamic_front_axle_load(static_wf, delta_w)
    t_slip = calculate_tyre_slip_torque(wf_dyn, base_params["r_dyn"], spec.TYRE_ROAD_ADHESION, 1.0)

    # Slip torque = 0.8 * wf_dyn * r
    # Also verify demand vs slip
    t_demand_1st = calculate_wheel_torque_demand(base_params["f_tw_1st"], base_params["r_dyn"])
    comp = compare_torque_demand_and_slip_torque(t_demand_1st, t_slip)
    assert comp["exceeds_slip_torque"] is True


def test_complete_traction_analysis(base_params):
    res_kerb = perform_complete_traction_analysis(
        base_params["w_kerb"], base_params["r_dyn"], base_params["f_tw_1st"]
    )
    assert "f_max_N" in res_kerb
    assert "gradeability" in res_kerb
    assert "tyre_slip_torque_Nm" in res_kerb
